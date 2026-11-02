"""Translation-defined intword scales and catalog compatibility."""

from __future__ import annotations

import gettext
import json
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

import humanize


@pytest.fixture(autouse=True)
def isolated_translations(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(
        humanize.i18n, "_TRANSLATIONS", {None: gettext.NullTranslations()}
    )
    humanize.deactivate()
    yield
    humanize.deactivate()


def compile_catalog(path: Path) -> None:
    subprocess.run(
        ["msgfmt", "--check", "-o", str(path.with_suffix(".mo")), str(path)],
        check=True,
    )


def write_catalog(
    root: Path,
    locale: str,
    scales: object,
    patterns: object | None,
    plural_patterns: object | None = None,
) -> None:
    path = root / locale / "LC_MESSAGES" / "humanize.po"
    path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        "Project-Id-Version: humanize test\n"
        "PO-Revision-Date: 2026-10-02 00:00+0000\n"
        "Last-Translator: Test\n"
        "Language-Team: Test\n"
        "MIME-Version: 1.0\n"
        "Content-Transfer-Encoding: 8bit\n"
        "Content-Type: text/plain; charset=UTF-8\n"
        "Plural-Forms: nplurals=2; plural=(n != 1);\n"
        f"Language: {locale}\n"
    )
    text = f'msgid ""\nmsgstr {json.dumps(header)}\n\n'
    text += 'msgid "intword:scales:v1"\n'
    text += f"msgstr {json.dumps(json.dumps(scales))}\n\n"
    if patterns is not None:
        plural_patterns = patterns if plural_patterns is None else plural_patterns
        text += 'msgid "intword:patterns:v1"\nmsgid_plural "intword:patterns:v1"\n'
        text += f"msgstr[0] {json.dumps(json.dumps(patterns))}\n"
        text += f"msgstr[1] {json.dumps(json.dumps(plural_patterns))}\n"
    path.write_text(text, encoding="utf-8")
    compile_catalog(path)


@pytest.mark.parametrize(
    "value,expected",
    [(234909023, "2.3億"), (2349090, "234.9万"), (-2349090, "-234.9万")],
)
def test_japanese_intword(tmp_path: Path, value: int, expected: str) -> None:
    source = (
        Path(humanize.i18n.__file__).parent / "locale/ja_JP/LC_MESSAGES/humanize.po"
    )
    destination = tmp_path / "ja_JP/LC_MESSAGES/humanize.po"
    destination.parent.mkdir(parents=True)
    shutil.copyfile(source, destination)
    compile_catalog(destination)
    humanize.activate("ja_JP", path=tmp_path)
    assert humanize.intword(value) == expected


def test_translated_scale_plural_and_rollover(tmp_path: Path) -> None:
    write_catalog(
        tmp_path,
        "zz",
        [4, 8],
        {"exponents": [4, 8], "patterns": ["unit {number}", "large {number}"]},
        {"exponents": [4, 8], "patterns": ["units {number}", "large units {number}"]},
    )
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(9999) == "9999"
    assert humanize.intword(10000) == "unit 1.0"
    assert humanize.intword(20000) == "units 2.0"
    assert humanize.intword(99999999) == "large 1.0"
    assert humanize.intword(200000000) == "large units 2.0"
    assert humanize.intword(-10000) == "unit -1.0"
    assert humanize.intword(-99999999) == "large -1.0"
    assert humanize.intword(-9999) == "-9999"


def test_regional_scale_mismatch_uses_legacy(tmp_path: Path) -> None:
    write_catalog(
        tmp_path,
        "zz",
        [4, 8],
        {"exponents": [4, 8], "patterns": ["{number}万", "{number}億"]},
    )
    write_catalog(tmp_path, "zz_ZZ", [3, 6], None)
    translation = humanize.activate("zz_ZZ", path=tmp_path)
    assert translation is not None
    assert json.loads(translation.gettext("intword:scales:v1")) == [3, 6]
    inherited = translation.ngettext("intword:patterns:v1", "intword:patterns:v1", 1)
    assert json.loads(inherited)["exponents"] == [4, 8]
    assert humanize.intword(1000) == "1.0 thousand"
    assert humanize.intword(1000000) == "1.0 million"


def test_untranslated_scale_uses_legacy() -> None:
    assert humanize.intword(234909023) == "234.9 million"
    assert humanize.intword(10**36) == "1000.0 decillion"
    assert humanize.intword(2 * 10**100) == "2.0 googol"


@pytest.mark.parametrize(
    "scales,patterns",
    [
        ([], {"exponents": [], "patterns": []}),
        ([0], {"exponents": [0], "patterns": ["{number} unit"]}),
        ([309], {"exponents": [309], "patterns": ["{number} unit"]}),
        ([4, 4], {"exponents": [4, 4], "patterns": ["{number}", "{number}"]}),
        ([8, 4], {"exponents": [8, 4], "patterns": ["{number}", "{number}"]}),
        ([True], {"exponents": [True], "patterns": ["{number} unit"]}),
        ([4.0], {"exponents": [4.0], "patterns": ["{number} unit"]}),
        ([4], {"exponents": [4.0], "patterns": ["{number} unit"]}),
        ([1], {"exponents": [True], "patterns": ["{number} unit"]}),
        ([4], {"exponents": [4], "patterns": []}),
        ([4], {"exponents": [4], "patterns": ["missing placeholder"]}),
        ([4], {"exponents": [4], "patterns": ["{number}{number}"]}),
        ([4], {"exponents": [4], "patterns": ["{number}{other}"]}),
        ([4], {"exponents": [4], "patterns": [1]}),
        ([4], ["{number} unit"]),
        ("invalid", {"exponents": [4], "patterns": ["{number} unit"]}),
    ],
)
def test_invalid_catalog_uses_legacy(
    tmp_path: Path, scales: object, patterns: object
) -> None:
    write_catalog(tmp_path, "zz", scales, patterns)
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(20000) == "20.0 thousand"


def test_plural_scale_mismatch_uses_legacy(tmp_path: Path) -> None:
    write_catalog(
        tmp_path,
        "zz",
        [4],
        {"exponents": [4], "patterns": ["unit {number}"]},
        {"exponents": [3], "patterns": ["units {number}"]},
    )
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(10000) == "unit 1.0"
    assert humanize.intword(20000) == "20.0 thousand"


def test_scales_above_googol(tmp_path: Path) -> None:
    write_catalog(
        tmp_path,
        "zz",
        [104, 308],
        {"exponents": [104, 308], "patterns": ["{number} high", "{number} highest"]},
    )
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(10**104) == "1.0 high"
    assert humanize.intword(2 * 10**104) == "2.0 high"
    assert humanize.intword(10**308) == "1.0 highest"


def test_catalog_does_not_hide_caller_errors(tmp_path: Path) -> None:
    write_catalog(
        tmp_path, "zz", [4], {"exponents": [4], "patterns": ["{number} unit"]}
    )
    humanize.activate("zz", path=tmp_path)
    with pytest.raises(ValueError, match="unsupported format character"):
        humanize.intword(20000, "%q")
    with pytest.raises(TypeError):
        humanize.intword(20000, None)
    assert humanize.intword("not a number") == "not a number"
    assert humanize.intword(float("inf")) == "+Inf"
    assert humanize.intword(float("nan")) == "NaN"
    assert humanize.intword(20000, "%.2f") == "2.00 unit"


def test_catalog_scales_are_thread_local(tmp_path: Path) -> None:
    write_catalog(
        tmp_path, "zz", [4], {"exponents": [4], "patterns": ["{number} unit"]}
    )
    write_catalog(
        tmp_path, "yy", [3], {"exponents": [3], "patterns": ["other {number}"]}
    )
    original_powers = humanize.number.powers.copy()
    barrier = Barrier(2)

    def render(locale: str) -> str:
        humanize.activate(locale, path=tmp_path)
        try:
            barrier.wait(timeout=5)
            return humanize.intword(20000)
        finally:
            humanize.deactivate()

    with ThreadPoolExecutor(max_workers=2) as executor:
        assert list(executor.map(render, ["zz", "yy", "zz", "yy"])) == [
            "2.0 unit",
            "other 20.0",
            "2.0 unit",
            "other 20.0",
        ]
    assert humanize.intword(20000) == "20.0 thousand"
    assert humanize.number.powers == original_powers


def test_japanese_profile_survives_translation_update(tmp_path: Path) -> None:
    root = Path(__file__).resolve().parents[1]
    source = root / "src/humanize"
    destination = tmp_path / "src/humanize"
    messages = destination / "locale/ja_JP/LC_MESSAGES"
    messages.mkdir(parents=True)
    for path in source.glob("*.py"):
        shutil.copyfile(path, destination / path.name)
    catalog = messages / "humanize.po"
    shutil.copyfile(source / "locale/ja_JP/LC_MESSAGES/humanize.po", catalog)
    subprocess.run(
        ["bash", str(root / "scripts/update-translations.sh")], cwd=tmp_path, check=True
    )
    humanize.activate("ja_JP", path=destination / "locale")
    units = [
        "万",
        "億",
        "兆",
        "京",
        "垓",
        "秭",
        "穣",
        "溝",
        "澗",
        "正",
        "載",
        "極",
        "恒河沙",
        "阿僧祇",
        "那由他",
        "不可思議",
        "無量大数",
    ]
    for exponent, unit in zip(range(4, 69, 4), units):
        assert humanize.intword(10**exponent) == f"1.0{unit}"
    assert humanize.intword(10**72) == "10000.0無量大数"
    assert humanize.intword(10**104, "%.0e") == "1e+36無量大数"
    assert humanize.intword(99999999) == "1.0億"
    assert humanize.intword(9999) == "9999"


def test_fuzzy_profile_uses_legacy(tmp_path: Path) -> None:
    write_catalog(
        tmp_path, "zz", [4], {"exponents": [4], "patterns": ["{number} unit"]}
    )
    catalog = tmp_path / "zz/LC_MESSAGES/humanize.po"
    catalog.write_text(
        catalog.read_text().replace(
            'msgid "intword:patterns:v1"', '#, fuzzy\nmsgid "intword:patterns:v1"'
        )
    )
    compile_catalog(catalog)
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(20000) == "20.0 thousand"


def test_profile_uses_locale_decimal_separator(tmp_path: Path) -> None:
    write_catalog(
        tmp_path, "fr_FR", [4], {"exponents": [4], "patterns": ["{number} unités"]}
    )
    humanize.activate("fr_FR", path=tmp_path)
    assert humanize.intword(-2349090, "%.2f") == "-234,91 unités"


def test_malformed_scale_json_uses_legacy(tmp_path: Path) -> None:
    write_catalog(
        tmp_path, "zz", [4], {"exponents": [4], "patterns": ["{number} unit"]}
    )
    catalog = tmp_path / "zz/LC_MESSAGES/humanize.po"
    catalog.write_text(catalog.read_text().replace('msgstr "[4]"', 'msgstr "not JSON"'))
    compile_catalog(catalog)
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(20000) == "20.0 thousand"


@pytest.mark.parametrize("exponents", [[4, 28], [104, 308]])
def test_wide_scale_rounding_rollover(tmp_path: Path, exponents: list[int]) -> None:
    write_catalog(
        tmp_path,
        "zz",
        exponents,
        {"exponents": exponents, "patterns": ["{number} lower", "{number} upper"]},
    )
    humanize.activate("zz", path=tmp_path)
    assert humanize.intword(10 ** exponents[1] - 1) == "1.0 upper"
    assert humanize.intword(-(10 ** exponents[1] - 1)) == "-1.0 upper"
