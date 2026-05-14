"""Benchmarks run via pytest-codspeed."""

from __future__ import annotations

import datetime as dt

import pytest

import humanize

TYPE_CHECKING = False
if TYPE_CHECKING:
    from pytest_codspeed import BenchmarkFixture


@pytest.fixture(scope="session", autouse=True)
def _warmup_i18n() -> None:
    # Touch i18n-backed functions once so lazy gettext catalog loading
    # is not attributed to the first benchmarked call.
    humanize.naturaltime(dt.datetime.now() - dt.timedelta(seconds=1))
    humanize.naturalday(dt.date.today())


def test_apnumber(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.apnumber, 7)


def test_clamp(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.clamp, 0.5, "{:.0%}", 0.1, 0.9)


def test_fractional(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.fractional, 1.5)


def test_intcomma(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.intcomma, 1_234_567_890)


def test_intword(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.intword, 1_234_567_890)


def test_metric(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.metric, 1500, "W")


def test_natural_list(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.natural_list, ["one", "two", "three", "four"])


def test_naturaldate(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.naturaldate, dt.date.today() - dt.timedelta(days=30))


def test_naturalday(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.naturalday, dt.date.today() - dt.timedelta(days=1))


def test_naturaldelta(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.naturaldelta, dt.timedelta(hours=3, minutes=27))


def test_naturalsize(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.naturalsize, 1_234_567_890)


def test_naturaltime(benchmark: BenchmarkFixture) -> None:
    when = dt.datetime.now() - dt.timedelta(hours=3, minutes=27)
    benchmark(humanize.naturaltime, when)


def test_ordinal(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.ordinal, 123)


def test_precisedelta(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.precisedelta, dt.timedelta(days=2, hours=3, seconds=4))


def test_scientific(benchmark: BenchmarkFixture) -> None:
    benchmark(humanize.scientific, -1.234e-50)
