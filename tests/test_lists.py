from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pytest

import humanize


@pytest.mark.parametrize(
    "test_args, expected",
    [
        ([["1", "2", "3"]], "1, 2 and 3"),
        ([["one", "two", "three"]], "one, two and three"),
        ([["one", "two"]], "one and two"),
        ([["one"]], "one"),
        ([[]], ""),
        ([[""]], ""),
        ([[1, 2, 3]], "1, 2 and 3"),
        ([[1, "two"]], "1 and two"),
        ([("one", "two", "three")], "one, two and three"),
        ([("one", "two")], "one and two"),
        ([("one",)], "one"),
        ([{"one": 1, "two": 2}.keys()], "one and two"),
        ([(x for x in ["one", "two", "three"])], "one, two and three"),
        ([range(1, 4)], "1, 2 and 3"),
    ],
)
def test_natural_list(test_args: Iterable[Any], expected: str) -> None:
    assert humanize.natural_list(*test_args) == expected


@pytest.mark.parametrize("oxford_comma", [False, True])
@pytest.mark.parametrize(
    "items, without_comma, with_comma",
    [
        ([], "", ""),
        (["one"], "one", "one"),
        (["one", "two"], "one and two", "one and two"),
        (["one", "two", "three"], "one, two and three", "one, two, and three"),
        ([1, 2, 3, 4], "1, 2, 3 and 4", "1, 2, 3, and 4"),
    ],
)
def test_natural_list_oxford_comma(
    items: list[Any], without_comma: str, with_comma: str, oxford_comma: bool
) -> None:
    expected = with_comma if oxford_comma else without_comma
    assert humanize.natural_list(items, oxford_comma=oxford_comma) == expected


def test_natural_list_oxford_comma_generator() -> None:
    items = (item for item in ["one", "two", "three"])
    assert humanize.natural_list(items, oxford_comma=True) == "one, two, and three"
