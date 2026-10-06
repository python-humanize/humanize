"""Internationalisation tests."""

from __future__ import annotations

import datetime as dt
import gettext
import importlib
import shutil
import subprocess
from pathlib import Path

import pytest
from freezegun import freeze_time

import humanize

LOCALE_DIR = Path(humanize.i18n.__file__).parent / "locale"

with freeze_time("2020-02-02"):
    NOW = dt.datetime.now(tz=dt.UTC)


GERMAN_DELTA_CASES = [
    (dt.timedelta(seconds=1), "seconds", True, "einer Sekunde"),
    (dt.timedelta(seconds=2), "seconds", True, "2 Sekunden"),
    (dt.timedelta(minutes=1), "seconds", True, "einer Minute"),
    (dt.timedelta(minutes=2), "seconds", True, "2 Minuten"),
    (dt.timedelta(minutes=59, seconds=30), "seconds", True, "einer Stunde"),
    (dt.timedelta(hours=1), "seconds", True, "einer Stunde"),
    (dt.timedelta(hours=2), "seconds", True, "2 Stunden"),
    (dt.timedelta(hours=23, minutes=59), "seconds", True, "einem Tag"),
    (dt.timedelta(days=1), "seconds", True, "einem Tag"),
    (dt.timedelta(days=2), "seconds", True, "2 Tagen"),
    (dt.timedelta(days=65), "seconds", False, "65 Tagen"),
    (dt.timedelta(days=31), "seconds", True, "einem Monat"),
    (dt.timedelta(days=61), "seconds", True, "2 Monaten"),
    (dt.timedelta(days=364), "seconds", True, "einem Jahr"),
    (dt.timedelta(days=365), "seconds", True, "einem Jahr"),
    (dt.timedelta(days=366), "seconds", True, "einem Jahr und 1 Tag"),
    (dt.timedelta(days=369), "seconds", True, "einem Jahr und 4 Tagen"),
    (dt.timedelta(days=400), "seconds", True, "einem Jahr und einem Monat"),
    (dt.timedelta(days=426), "seconds", True, "einem Jahr und 2 Monaten"),
    (dt.timedelta(days=400), "seconds", False, "einem Jahr und 35 Tagen"),
    (dt.timedelta(days=729), "seconds", True, "2 Jahren"),
    (dt.timedelta(days=730), "seconds", True, "2 Jahren"),
    (dt.timedelta(days=365 * 1234), "seconds", True, "1.234 Jahren"),
    (dt.timedelta(microseconds=1), "microseconds", True, "1 Mikrosekunde"),
    (dt.timedelta(microseconds=4), "microseconds", True, "4 Mikrosekunden"),
    (dt.timedelta(microseconds=4), "milliseconds", True, "0 Millisekunden"),
    (dt.timedelta(milliseconds=1), "milliseconds", True, "1 Millisekunde"),
    (dt.timedelta(milliseconds=4), "microseconds", True, "4 Millisekunden"),
]


@pytest.mark.parametrize("locale, one", [("de_DE", "eins"), ("fr_FR", "un")])
def test_update_translations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, locale: str, one: str
) -> None:
    for command in ("bash", "xgettext", "msgmerge", "msgfmt"):
        if shutil.which(command) is None:
            pytest.skip(f"Translation updates require {command}")

    root = Path(__file__).resolve().parents[1]
    source = root / "src" / "humanize"
    destination = tmp_path / "src" / "humanize"
    messages = destination / "locale" / locale / "LC_MESSAGES"
    messages.mkdir(parents=True)
    for path in source.glob("*.py"):
        shutil.copy2(path, destination)
    catalog = messages / "humanize.po"
    shutil.copy2(source / "locale" / locale / "LC_MESSAGES" / "humanize.po", catalog)
    binary = catalog.with_suffix(".mo")
    subprocess.run(["msgfmt", "--check", "-o", str(binary), str(catalog)], check=True)

    results = []
    try:
        for updated in (False, True):
            if updated:
                subprocess.run(
                    ["bash", str(root / "scripts" / "update-translations.sh")],
                    cwd=tmp_path,
                    check=True,
                )
            with binary.open("rb") as stream:
                translation = gettext.GNUTranslations(stream)
            # Replace the cached catalog so the second pass uses the updated one.
            monkeypatch.setitem(humanize.i18n._TRANSLATIONS, locale, translation)
            humanize.activate(locale)
            results.append(
                [humanize.apnumber(value) for value in range(10)]
                + [
                    humanize.ordinal(value, gender=gender)
                    for gender in ("male", "female")
                    for value in range(10)
                ]
                + [
                    result
                    for value, minimum_unit, months, _ in GERMAN_DELTA_CASES
                    for result in (
                        humanize.naturaldelta(value, months, minimum_unit),
                        humanize.naturaltime(
                            value, months=months, minimum_unit=minimum_unit, when=NOW
                        ),
                        humanize.naturaltime(
                            -value, months=months, minimum_unit=minimum_unit, when=NOW
                        ),
                    )
                ]
                + [humanize.naturaldelta(0), humanize.naturaltime(0)]
            )
    finally:
        humanize.deactivate()

    assert results[0][1] == one
    assert results[1] == results[0]


@freeze_time("2020-02-02")
def test_i18n() -> None:
    three_seconds = NOW - dt.timedelta(seconds=3)
    one_min_three_seconds = dt.timedelta(milliseconds=67_000)

    assert humanize.naturaltime(three_seconds) == "3 seconds ago"
    assert humanize.ordinal(5) == "5th"
    assert humanize.precisedelta(one_min_three_seconds) == "1 minute and 7 seconds"

    try:
        humanize.i18n.activate("lv")
        assert humanize.naturaltime(three_seconds) == "pirms 3 sekundēm"
        assert humanize.ordinal(5) == "5."

        humanize.i18n.activate("ru_RU")
        assert humanize.naturaltime(three_seconds) == "3 секунды назад"
        assert humanize.ordinal(5) == "5ый"
        assert humanize.precisedelta(one_min_three_seconds) == "1 минута и 7 секунд"

        humanize.i18n.activate("si_LK")
        assert humanize.naturaltime(three_seconds) == "තත්පර 3කට පෙර"
        assert humanize.precisedelta(one_min_three_seconds) == "විනාඩි 1යි තත්පර 7ක්"

    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")

    finally:
        humanize.i18n.deactivate()
        assert humanize.naturaltime(three_seconds) == "3 seconds ago"
        assert humanize.ordinal(5) == "5th"
        assert humanize.precisedelta(one_min_three_seconds) == "1 minute and 7 seconds"


def test_intcomma() -> None:
    number = 10_000_000

    assert humanize.intcomma(number) == "10,000,000"

    try:
        humanize.i18n.activate("de_DE")
        assert humanize.intcomma(number) == "10.000.000"
        assert humanize.intcomma(1_234_567.8901) == "1.234.567,8901"
        assert humanize.intcomma(1_234_567.89) == "1.234.567,89"
        assert humanize.intcomma("1234567,89") == "1.234.567,89"
        assert humanize.intcomma("1.234.567,89") == "1.234.567,89"
        assert humanize.intcomma("1.234.567,8") == "1.234.567,8"

        humanize.i18n.activate("fr_FR")
        assert humanize.intcomma(number) == "10 000 000"
        assert humanize.intcomma(1_234_567.89) == "1 234 567,89"
        assert humanize.intcomma("1 234 567,89") == "1 234 567,89"

        humanize.i18n.activate("pt_BR")
        assert humanize.intcomma(number) == "10.000.000"

    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")

    finally:
        humanize.i18n.deactivate()
        assert humanize.intcomma(number) == "10,000,000"


def test_naturaldelta() -> None:
    seconds = 1234 * 365 * 24 * 60 * 60

    assert humanize.naturaldelta(seconds) == "1,234 years"

    try:
        humanize.i18n.activate("fr_FR")
        assert humanize.naturaldelta(seconds) == "1 234 ans"
        humanize.i18n.activate("es_ES")
        assert humanize.naturaldelta(seconds) == "1,234 años"

    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")

    finally:
        humanize.i18n.deactivate()
        assert humanize.naturaldelta(seconds) == "1,234 years"


@pytest.mark.parametrize(
    "future, expected",
    [(False, "vor einer Stunde"), (True, "in einer Stunde")],
)
def test_naturaltime_german_grammatical_case(future: bool, expected: str) -> None:
    try:
        humanize.i18n.activate("de_DE")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.naturaldelta(3600) == "eine Stunde"
        assert humanize.naturaltime(3600, future=future, when=NOW) == expected
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize("value, minimum_unit, months, expected", GERMAN_DELTA_CASES)
@pytest.mark.parametrize("future", [False, True])
@pytest.mark.parametrize("input_kind", ["timedelta", "datetime"])
def test_naturaltime_german_units(
    value: dt.timedelta,
    minimum_unit: str,
    months: bool,
    expected: str,
    future: bool,
    input_kind: str,
) -> None:
    delta = -value if future else value
    test_input = NOW - delta if input_kind == "datetime" else delta
    prefix = "in" if future else "vor"
    try:
        humanize.i18n.activate("de_DE")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert (
            humanize.naturaltime(
                test_input,
                future=not future,
                months=months,
                minimum_unit=minimum_unit,
                when=NOW,
            )
            == f"{prefix} {expected}"
        )
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize("future", [False, True])
@pytest.mark.parametrize("value", [0, dt.timedelta(microseconds=1), NOW])
def test_naturaltime_german_now(
    future: bool, value: int | dt.timedelta | dt.datetime
) -> None:
    try:
        humanize.i18n.activate("de_DE")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.naturaltime(value, future=future, when=NOW) == "jetzt"
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize(
    "value, expected",
    [(float("nan"), "nan"), (float("inf"), "inf"), (float("-inf"), "-inf")],
)
def test_naturaltime_german_non_finite(value: float, expected: str) -> None:
    try:
        humanize.i18n.activate("de_DE")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.naturaldelta(value) == expected
        if expected == "nan":
            assert humanize.naturaltime(value, when=NOW) == expected
        else:
            with pytest.raises(OverflowError):
                humanize.naturaltime(value, when=NOW)
        with pytest.raises(OverflowError):
            humanize.naturaldelta(1e30)
        with pytest.raises(ValueError, match="Minimum unit 'years' not supported"):
            humanize.naturaltime(1, minimum_unit="years", when=NOW)
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize("contextual", [False, True])
def test_naturaltime_context_fallback(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, contextual: bool
) -> None:
    if shutil.which("msgfmt") is None:
        pytest.skip("Catalog compilation requires msgfmt")
    catalog = tmp_path / "humanize.po"
    contents = (LOCALE_DIR / "ru_RU" / "LC_MESSAGES" / "humanize.po").read_text()
    if contextual:
        # Explicit contextual translations may equal the English source messages.
        contents += """
msgctxt "naturaltime"
msgid "an hour"
msgstr "an hour"

#, python-format
msgctxt "naturaltime"
msgid "%d hour"
msgid_plural "%d hours"
msgstr[0] "%d hour"
msgstr[1] "%d hours"
msgstr[2] "%d hours"
"""
    catalog.write_text(contents)
    binary = catalog.with_suffix(".mo")
    subprocess.run(["msgfmt", "--check", "-o", str(binary), str(catalog)], check=True)
    with binary.open("rb") as stream:
        translation = gettext.GNUTranslations(stream)
    monkeypatch.setitem(humanize.i18n._TRANSLATIONS, "ru_RU", translation)
    try:
        humanize.activate("ru_RU")
        for hours, ordinary, contextual_text in (
            (1, "час", "an hour"),
            (2, "2 часа", "2 hours"),
            (21, "21 час", "21 hour"),
        ):
            value = dt.timedelta(hours=hours)
            relative = contextual_text if contextual else ordinary
            assert humanize.naturaldelta(value) == ordinary
            assert humanize.naturaltime(value, when=NOW) == f"{relative} назад"
            assert humanize.naturaltime(-value, when=NOW) == f"через {relative}"
        assert humanize.naturaltime(0, when=NOW) == "сейчас"
        humanize.activate("de_DE")
        assert humanize.naturaltime(3600, when=NOW) == "vor einer Stunde"
        humanize.deactivate()
        assert humanize.naturaltime(3600, when=NOW) == "an hour ago"
    finally:
        humanize.deactivate()


@pytest.mark.parametrize(
    "value, expected",
    [
        (dt.timedelta(seconds=1), "bir saniye önce"),
        (dt.timedelta(seconds=-1), "şu andan itibaren bir saniye"),
        (0, "şimdi"),
        (dt.timedelta(milliseconds=4), "şimdi"),
        (dt.timedelta(milliseconds=-4), "şimdi"),
    ],
)
def test_naturaltime_moment_translation_collision(
    value: int | dt.timedelta, expected: str
) -> None:
    try:
        humanize.activate("tr_TR")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.naturaldelta(value) == "bir saniye"
        assert humanize.naturaltime(value, when=NOW) == expected
    finally:
        humanize.deactivate()


@pytest.mark.parametrize(
    "locale, number, expected_result",
    [
        # Italian uses comma as decimal separator
        ("it_IT", 1_000_000, "1,0 milione"),
        ("it_IT", 1_200_000, "1,2 milioni"),
        ("it_IT", 1_000_000_000, "1,0 miliardo"),
        ("it_IT", 3_500_000_000, "3,5 miliardi"),
        # Sinhala uses borrowed scale words with a dot decimal separator
        ("si_LK", 1_000_000, "1.0 මිලියන"),
        ("si_LK", 1_200_000, "1.2 මිලියන"),
        ("si_LK", 3_500_000_000, "3.5 බිලියන"),
        # Spanish uses dot as decimal separator
        ("es_ES", 1_000_000, "1.0 millón"),
        ("es_ES", 3_500_000, "3.5 millones"),
        ("es_ES", 1_000_000_000, "1.0 mil millones"),
        ("es_ES", 1_200_000_000, "1.2 miles de millones"),
        ("es_ES", 1_000_000_000_000, "1.0 billón"),
        ("es_ES", 6_700_000_000_000, "6.7 billones"),
        # Latvian uses comma as decimal separator
        ("lv", 1_000, "1,0 tūkstotis"),
        ("lv", 1_200, "1,2 tūkstoši"),
        ("lv", 2_000, "2,0 tūkstoši"),
        ("lv", 11_000, "11,0 tūkstoši"),
        ("lv", 21_000, "21,0 tūkstotis"),
        ("lv", 1_000_000, "1,0 miljons"),
        ("lv", 2_000_000, "2,0 miljoni"),
        ("lv", 11_000_000, "11,0 miljoni"),
        ("lv", 21_000_000, "21,0 miljons"),
        ("fr_FR", "1_000", "1,0 mille"),
        ("fr_FR", "12_400", "12,4 milles"),
        ("fr_FR", "12_490", "12,5 milles"),
        ("fr_FR", "1_000_000", "1,0 million"),
        ("fr_FR", "-1_000_000", "-1,0 million"),
        ("fr_FR", "1_200_000", "1,2 millions"),
        ("fr_FR", "1_290_000", "1,3 millions"),
        ("fr_FR", "999_999_999", "1,0 milliard"),
        ("fr_FR", "1_000_000_000", "1,0 milliard"),
        ("fr_FR", "-1_000_000_000", "-1,0 milliard"),
        ("fr_FR", "2_000_000_000", "2,0 milliards"),
        ("fr_FR", "999_999_999_999", "1,0 billion"),
        ("fr_FR", "1_000_000_000_000", "1,0 billion"),
        ("fr_FR", "6_000_000_000_000", "6,0 billions"),
        ("fr_FR", "-6_000_000_000_000", "-6,0 billions"),
        ("fr_FR", "999_999_999_999_999", "1,0 billiard"),
        ("fr_FR", "1_000_000_000_000_000", "1,0 billiard"),
        ("fr_FR", "1_300_000_000_000_000", "1,3 billiards"),
        ("fr_FR", "-1_300_000_000_000_000", "-1,3 billiards"),
        ("fr_FR", "3_500_000_000_000_000_000_000", "3,5 trilliards"),
        ("fr_FR", "8_100_000_000_000_000_000_000_000_000_000_000", "8,1 quintilliards"),
        (
            "fr_FR",
            "-8_100_000_000_000_000_000_000_000_000_000_000",
            "-8,1 quintilliards",
        ),
        (
            "fr_FR",
            1_000_000_000_000_000_000_000_000_000_000_000_000,
            "1000,0 quintilliards",
        ),
        (
            "fr_FR",
            1_100_000_000_000_000_000_000_000_000_000_000_000,
            "1100,0 quintilliards",
        ),
        (
            "fr_FR",
            2_100_000_000_000_000_000_000_000_000_000_000_000,
            "2100,0 quintilliards",
        ),
    ],
)
def test_intword_i18n(locale: str, number: int, expected_result: str) -> None:
    try:
        humanize.i18n.activate(locale)
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.intword(number) == expected_result
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize(
    "locale, value, expected_result",
    [
        ("fr_FR", 1, "1 octet"),
        ("fr_FR", 42, "42 octets"),
        ("si_LK", 1, "බයිට් 1"),
        ("si_LK", 42, "බයිට් 42"),
        ("fr_FR", 42_000, "42.0 Ko"),
        ("fr_FR", 42_000_000, "42.0 Mo"),
        ("fr_FR", 42_000_000_000, "42.0 Go"),
        ("fr_FR", -42_000, "-42.0 Ko"),
    ],
)
def test_naturalsize_i18n(locale: str, value: float, expected_result: str) -> None:
    try:
        humanize.i18n.activate(locale)
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.naturalsize(value) == expected_result
    finally:
        humanize.i18n.deactivate()


def test_naturalsize_i18n_binary() -> None:
    try:
        humanize.i18n.activate("fr_FR")
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.naturalsize(3000, binary=True) == "2.9 Kio"
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize(
    "locale, expected_result",
    [
        ("ar", "5 خامس"),
        ("ar_SA", "5 خامس"),
        ("fr", "5e"),
        ("fr_FR", "5e"),
        ("pt", "5º"),
        ("pt_BR", "5º"),
        ("pt_PT", "5º"),
    ],
)
def test_langauge_codes(locale: str, expected_result: str) -> None:
    try:
        humanize.i18n.activate(locale)
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.ordinal(5) == expected_result
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize(
    "locale, number, gender, expected_result",
    [
        ("fr_FR", 1, "male", "1er"),
        ("fr_FR", 1, "female", "1ère"),
        ("fr_FR", 2, "male", "2e"),
        ("es_ES", 1, "male", "1º"),
        ("es_ES", 5, "female", "5ª"),
        ("it_IT", 3, "male", "3º"),
        ("it_IT", 8, "female", "8ª"),
    ],
)
def test_ordinal_genders(
    locale: str, number: int, gender: str, expected_result: str
) -> None:
    try:
        humanize.i18n.activate(locale)
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.ordinal(number, gender=gender) == expected_result
    finally:
        humanize.i18n.deactivate()


def test_default_locale_path_defined__spec__() -> None:
    i18n = importlib.import_module("humanize.i18n")
    assert i18n._get_default_locale_path() is not None


def test_default_locale_path_none__spec__(monkeypatch: pytest.MonkeyPatch) -> None:
    i18n = importlib.import_module("humanize.i18n")
    monkeypatch.setattr(i18n, "__spec__", None)
    assert i18n._get_default_locale_path() is None


def test_default_locale_path_undefined__file__(monkeypatch: pytest.MonkeyPatch) -> None:
    i18n = importlib.import_module("humanize.i18n")
    monkeypatch.delattr(i18n, "__spec__")
    assert i18n._get_default_locale_path() is None


class TestActivate:
    expected_msg = (
        "Humanize cannot determinate the default location of the"
        " 'locale' folder. You need to pass the path explicitly."
    )

    def test_default_locale_path_null__spec__(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        i18n = importlib.import_module("humanize.i18n")
        monkeypatch.setattr(i18n, "__spec__", None)

        with pytest.raises(FileNotFoundError, match=self.expected_msg):
            i18n.activate("ru_RU")

    def test_default_locale_path_undefined__spec__(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        i18n = importlib.import_module("humanize.i18n")
        monkeypatch.delattr(i18n, "__spec__")

        with pytest.raises(FileNotFoundError, match=self.expected_msg):
            i18n.activate("ru_RU")

    @freeze_time("2020-02-02")
    def test_en_locale(self) -> None:
        three_seconds = NOW - dt.timedelta(seconds=3)
        test_str = humanize.naturaltime(three_seconds)

        humanize.i18n.activate("en_US")
        assert test_str == humanize.naturaltime(three_seconds)

        humanize.i18n.activate("en_GB")
        assert test_str == humanize.naturaltime(three_seconds)

        humanize.i18n.deactivate()

    @freeze_time("2020-02-02")
    def test_none_locale(self) -> None:
        three_seconds = NOW - dt.timedelta(seconds=3)

        try:
            humanize.i18n.activate("fr")
            assert humanize.naturaltime(three_seconds) == "il y a 3 secondes"

            humanize.i18n.activate(None)
            test_str = humanize.naturaltime(three_seconds)
            assert test_str == "3 seconds ago"
        except FileNotFoundError:
            pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")

        finally:
            humanize.i18n.deactivate()

        assert test_str == humanize.naturaltime(three_seconds)


@pytest.mark.parametrize(
    "locale", sorted(p.name for p in LOCALE_DIR.iterdir() if p.is_dir())
)
def test_intword_unit_has_no_format_placeholder(locale: str) -> None:
    try:
        humanize.i18n.activate(locale)
        for value in (1_000, 1_000_000, 1_000_000_000, 10**12, 10**15, 10**100):
            assert "%" not in humanize.intword(value)
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    finally:
        humanize.i18n.deactivate()
