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
    "test_args, expected",
    [
        (
            [["one", "two", "three", "four", "five", "six", "seven", "eight"], 6],
            "one, two, three, four, five, six, etc.",
        ),
        ([["1", "2", "3"], 4], "1, 2 and 3"),
        ([["one", "two", "three"], 4], "one, two and three"),
        ([["one", "two"], 3], "one and two"),
        ([["one"], 3], "one"),
        ([[""], 3], ""),
        ([[1, 2, 3], 4], "1, 2 and 3"),
        ([[1, "two"], 4], "1 and two"),
    ],
)
def test_natural_list_etc(
    test_args: list[str] | list[int] | list[str | int], expected: str
) -> None:
    assert humanize.natural_list_etc(*test_args) == expected
