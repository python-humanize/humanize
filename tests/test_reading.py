"""Tests for the custom reading_time() extension."""

from __future__ import annotations

import pytest

import humanize


@pytest.mark.parametrize(
    "text, wpm, expected",
    [
        ("", 200, "a moment"),
        ("Hello world", 200, "a second"),
        ("word " * 200, 200, "a minute"),
        ("word " * 400, 200, "2 minutes"),
        ("word " * 300, 100, "3 minutes"),
        ("Merhaba dünya, nasılsın?", 200, "a second"),
    ],
)
def test_reading_time(text: str, wpm: int, expected: str) -> None:
    assert humanize.reading_time(text, wpm=wpm) == expected


def test_reading_time_invalid_wpm() -> None:
    with pytest.raises(ValueError):
        humanize.reading_time("text", wpm=0)


def test_reading_time_invalid_type() -> None:
    with pytest.raises(TypeError):
        humanize.reading_time(123)  # type: ignore[arg-type]
