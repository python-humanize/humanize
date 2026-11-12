"""Numeric separators for short locale codes and their bundled catalogs."""

from __future__ import annotations

import datetime as dt
import gettext
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest

import humanize

CATALOGS = Path(humanize.__file__).parent / "locale"
ALIASES = [
    ("de", "de_DE", ".", "1.234.567,89", "1,2 Millionen"),
    ("fr", "fr_FR", " ", "1 234 567,89", "1,2 millions"),
    ("it", "it_IT", ".", "1.234.567,89", "1,2 milioni"),
    ("hu", "hu_HU", " ", "1 234 567,89", "1,2 millió"),
    ("tr", "tr_TR", ".", "1.234.567,89", "1,2 milyon"),
]


@pytest.fixture(autouse=True)
def _reset_locale() -> Iterator[None]:
    humanize.deactivate()
    try:
        yield
    finally:
        humanize.deactivate()


@pytest.mark.parametrize("alias, regional, thousands, formatted, word", ALIASES)
def test_explicit_catalog_path(
    alias: str, regional: str, thousands: str, formatted: str, word: str
) -> None:
    catalog = gettext.find("humanize", localedir=CATALOGS, languages=[alias])
    assert catalog == str(CATALOGS / regional / "LC_MESSAGES" / "humanize.mo")
    humanize.activate(alias, path=CATALOGS)
    assert humanize.intcomma(1_234_567.89) == formatted
    assert humanize.intword(1_200_000) == word


@pytest.mark.parametrize("alias, regional, thousands, formatted, word", ALIASES)
def test_alias_separators(
    alias: str, regional: str, thousands: str, formatted: str, word: str
) -> None:
    humanize.activate(alias)
    assert humanize.i18n.thousands_separator() == thousands
    assert humanize.i18n.decimal_separator() == ","
    assert humanize.intcomma(1_234_567.89) == formatted
    humanize.activate(regional)
    assert humanize.intcomma(1_234_567.89) == formatted


@pytest.mark.parametrize(
    "locale, thousands, formatted",
    [
        ("de_DE", ".", "1.234.567,89"),
        ("fr_FR", " ", "1 234 567,89"),
        ("it_IT", ".", "1.234.567,89"),
        ("hu_HU", " ", "1 234 567,89"),
        ("tr_TR", ".", "1.234.567,89"),
        ("pt_BR", ".", "1.234.567,89"),
        ("lv", " ", "1 234 567,89"),
    ],
)
def test_existing_separator_entries(
    locale: str, thousands: str, formatted: str
) -> None:
    humanize.activate(locale)
    assert humanize.i18n.thousands_separator() == thousands
    assert humanize.i18n.decimal_separator() == ","
    assert humanize.intcomma(1_234_567.89) == formatted
    assert humanize.intcomma(formatted) == formatted
    assert humanize.intcomma(1234.5, ndigits=2) == f"1{thousands}234,50"


@pytest.mark.parametrize("alias, regional, thousands, formatted, word", ALIASES)
@pytest.mark.parametrize("sign", ["", "-"])
def test_alias_numeric_strings(
    alias: str, regional: str, thousands: str, formatted: str, word: str, sign: str
) -> None:
    humanize.activate(alias)
    assert humanize.intcomma(f"{sign}1234,5") == f"{sign}1{thousands}234,5"
    assert humanize.intcomma(f"{sign}{formatted}") == f"{sign}{formatted}"


@pytest.mark.parametrize("alias, regional, thousands, formatted, word", ALIASES)
def test_alias_precision(
    alias: str, regional: str, thousands: str, formatted: str, word: str
) -> None:
    humanize.activate(alias)
    assert humanize.intcomma(1234.5, ndigits=2) == f"1{thousands}234,50"
    assert humanize.intcomma(1234.567, ndigits=2) == f"1{thousands}234,57"


@pytest.mark.parametrize("alias, regional, thousands, formatted, word", ALIASES)
def test_alias_intword(
    alias: str, regional: str, thousands: str, formatted: str, word: str
) -> None:
    humanize.activate(alias)
    assert humanize.intword(1_200_000) == word


@pytest.mark.parametrize("locale", ["pt", "pt_PT"])
def test_portuguese_catalog_selection(locale: str) -> None:
    catalog = gettext.find("humanize", localedir=CATALOGS, languages=[locale])
    assert catalog == str(CATALOGS / "pt_PT" / "LC_MESSAGES" / "humanize.mo")
    translation = humanize.activate(locale)
    assert translation.info()["language"] == "pt_PT"
    assert humanize.intword(1_200_000) == "1.2 milhão"
    assert humanize.intcomma(1_234_567.89) == "1,234,567.89"


def test_locale_lifecycle_and_cached_reactivation() -> None:
    assert humanize.intcomma(1234.5) == "1,234.5"
    translation = humanize.activate("de")
    assert humanize.intcomma(1234.5) == "1.234,5"
    humanize.activate("de_DE")
    assert humanize.intcomma(1234.5) == "1.234,5"
    humanize.activate("fr")
    assert humanize.intcomma(1234.5) == "1 234,5"
    humanize.deactivate()
    assert humanize.intcomma(1234.5) == "1,234.5"
    assert humanize.activate("de") is translation
    assert humanize.intcomma(1234.5) == "1.234,5"


@pytest.mark.parametrize("locale", [None, "en", "en_US", "en_GB"])
def test_default_and_english_activation(locale: str | None) -> None:
    humanize.activate("fr_FR")
    assert humanize.intcomma(1234.5) == "1 234,5"
    humanize.activate(locale)
    assert humanize.i18n.thousands_separator() == ","
    assert humanize.i18n.decimal_separator() == "."
    assert humanize.intcomma(1234.5) == "1,234.5"
    assert humanize.intword(1_200_000) == "1.2 million"


def test_failed_activation_preserves_locale() -> None:
    translation = humanize.activate("fr_FR")
    with pytest.raises(FileNotFoundError):
        humanize.activate("zz_UNKNOWN", path=CATALOGS)
    assert humanize.intcomma(1234.5) == "1 234,5"
    assert humanize.ordinal(5) == "5e"
    assert humanize.activate("fr_FR") is translation


def _thread_number(locale: str, barrier: Barrier) -> tuple[str, str]:
    try:
        humanize.activate(locale)
        barrier.wait(timeout=10)
        first = humanize.intcomma(1234.5)
        barrier.wait(timeout=10)
        return first, humanize.intcomma(1234.5)
    finally:
        humanize.deactivate()


def test_locales_are_thread_local() -> None:
    humanize.activate("de_DE")
    barrier = Barrier(2)
    with ThreadPoolExecutor(max_workers=2) as pool:
        french = pool.submit(_thread_number, "fr", barrier)
        english = pool.submit(_thread_number, "en", barrier)
        assert french.result(timeout=20) == ("1 234,5", "1 234,5")
        assert english.result(timeout=20) == ("1,234.5", "1,234.5")
    assert humanize.intcomma(1234.5) == "1.234,5"


@pytest.mark.parametrize(
    "locale, ordinal, one, size, seconds, days",
    [
        ("de", "5.", "eins", "42.0 kB", "3 Sekunden", "1234 Tage"),
        ("fr", "5e", "un", "42.0 Ko", "3 secondes", "1234 jours"),
        ("it", "5º", "uno", "42.0 kB", "3 secondi", "1234 giorni"),
        ("hu", "5.", "egy", "42.0 kB", "3 másodperc", "1234 nap"),
        ("tr", "5.", "bir", "42.0 kB", "3 saniye", "1234 gün"),
    ],
)
def test_other_consumers(
    locale: str, ordinal: str, one: str, size: str, seconds: str, days: str
) -> None:
    humanize.activate(locale)
    assert humanize.ordinal(5) == ordinal
    assert humanize.apnumber(1) == one
    assert humanize.naturalsize(42_000) == size
    assert humanize.fractional(1.5) == "1 1/2"
    assert humanize.scientific(500) == "5.00 x 10²"
    assert humanize.naturaldelta(dt.timedelta(seconds=3)) == seconds
    assert (
        humanize.precisedelta(
            dt.timedelta(days=1234), minimum_unit="days", suppress=["years", "months"]
        )
        == days
    )


@pytest.mark.parametrize(
    "locale, expected",
    [
        ("de", "1.234 Jahre"),
        ("fr", "1 234 ans"),
        ("it", "1.234 anni"),
        ("hu", "1 234 év"),
        ("tr", "1.234 yıl"),
    ],
)
def test_naturaldelta_large_years(locale: str, expected: str) -> None:
    humanize.activate(locale)
    assert humanize.naturaldelta(dt.timedelta(days=365 * 1234)) == expected
