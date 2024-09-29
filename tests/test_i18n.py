"""Internationalisation tests."""

from __future__ import annotations

import datetime as dt
import importlib

import pytest
from freezegun import freeze_time

import humanize

with freeze_time("2020-02-02"):
    NOW = dt.datetime.now()


@freeze_time("2020-02-02")
def test_i18n() -> None:
    three_seconds = NOW - dt.timedelta(seconds=3)
    one_min_three_seconds = dt.timedelta(milliseconds=67_000)

    assert humanize.naturaltime(three_seconds) == "3 seconds ago"
    assert humanize.ordinal(5) == "5th"
    assert humanize.precisedelta(one_min_three_seconds) == "1 minute and 7 seconds"

    try:
        humanize.i18n.activate("ru_RU")
        assert humanize.naturaltime(three_seconds) == "3 секунды назад"
        assert humanize.ordinal(5) == "5ый"
        assert humanize.precisedelta(one_min_three_seconds) == "1 минута и 7 секунд"

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
    ("locale", "number", "expected_result"),
    (
        ("es_ES", 1000000, "1.0 millón"),
        ("es_ES", 3500000, "3.5 millones"),
        ("es_ES", 1000000000, "1.0 billón"),
        ("es_ES", 1200000000, "1.2 billones"),
        ("es_ES", 1000000000000, "1.0 trillón"),
        ("es_ES", 6700000000000, "6.7 trillones"),
    ),
)
def test_intword_plurals(locale: str, number: int, expected_result: str) -> None:
    try:
        humanize.i18n.activate(locale)
    except FileNotFoundError:
        pytest.skip("Generate .mo with scripts/generate-translation-binaries.sh")
    else:
        assert humanize.intword(number) == expected_result
    finally:
        humanize.i18n.deactivate()


@pytest.mark.parametrize(
    ("locale", "expected_result"),
    (
        ("ar", "5خامس"),
        ("ar_SA", "5خامس"),
        ("fr", "5e"),
        ("fr_FR", "5e"),
        ("pt", "5º"),
        ("pt_BR", "5º"),
        ("pt_PT", "5º"),
    ),
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
    ("locale", "number", "gender", "expected_result"),
    (
        ("fr_FR", 1, "male", "1er"),
        ("fr_FR", 1, "female", "1ère"),
        ("fr_FR", 2, "male", "2e"),
        ("es_ES", 1, "male", "1º"),
        ("es_ES", 5, "female", "5ª"),
        ("it_IT", 3, "male", "3º"),
        ("it_IT", 8, "female", "8ª"),
    ),
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


def test_default_locale_path_defined__file__() -> None:
    i18n = importlib.import_module("humanize.i18n")
    assert i18n._get_default_locale_path() is not None


def test_default_locale_path_null__file__() -> None:
    i18n = importlib.import_module("humanize.i18n")
    i18n.__file__ = None
    assert i18n._get_default_locale_path() is None


def test_default_locale_path_undefined__file__() -> None:
    i18n = importlib.import_module("humanize.i18n")
    del i18n.__file__
    assert i18n._get_default_locale_path() is None


class TestActivate:
    expected_msg = (
        "Humanize cannot determinate the default location of the"
        " 'locale' folder. You need to pass the path explicitly."
    )

    def test_default_locale_path_null__file__(self) -> None:
        i18n = importlib.import_module("humanize.i18n")
        i18n.__file__ = None

        with pytest.raises(Exception) as excinfo:
            i18n.activate("ru_RU")
        assert str(excinfo.value) == self.expected_msg

    def test_default_locale_path_undefined__file__(self) -> None:
        i18n = importlib.import_module("humanize.i18n")
        del i18n.__file__

        with pytest.raises(Exception) as excinfo:
            i18n.activate("ru_RU")
        assert str(excinfo.value) == self.expected_msg
