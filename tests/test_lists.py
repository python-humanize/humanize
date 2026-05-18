from __future__ import annotations

import pytest

import humanize


@pytest.mark.parametrize(
    "test_args, expected",
    [
        ([["1", "2", "3"]], "1, 2 and 3"),
        ([["one", "two", "three"]], "one, two and three"),
        ([["one", "two"]], "one and two"),
        ([["one"]], "one"),
        ([[""]], ""),
        ([[1, 2, 3]], "1, 2 and 3"),
        ([[1, "two"]], "1 and two"),
    ],
)
def test_natural_list(
    test_args: list[str] | list[int] | list[str | int], expected: str
) -> None:
    assert humanize.natural_list(*test_args) == expected


@pytest.mark.parametrize(
    "items, conjunction, expected",
    [
        (["one", "two", "three"], "or", "one, two or three"),
        (["one", "two"], "or", "one or two"),
        (["one"], "or", "one"),
        (["one", "two", "three"], "and also", "one, two and also three"),
        (["one", "two", "three"], "and", "one, two and three"),
    ],
)
def test_natural_list_conjunction(
    items: list[str], conjunction: str, expected: str
) -> None:
    assert humanize.natural_list(items, conjunction=conjunction) == expected
