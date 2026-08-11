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
        ([[]], ""),
        ([[""]], ""),
        ([[1, 2, 3]], "1, 2 and 3"),
        ([[1, "two"]], "1 and two"),
        ([("a", "b", "c")], "a, b and c"),
    ],
)
def test_natural_list(
    test_args: list[str] | list[int] | list[str | int], expected: str
) -> None:
    assert humanize.natural_list(*test_args) == expected


def test_natural_list_generator_and_oxford_comma() -> None:
    gen = (x for x in ["alpha", "beta", "gamma"])
    assert humanize.natural_list(gen) == "alpha, beta and gamma"
    assert (
        humanize.natural_list(["one", "two", "three"], oxford_comma=True)
        == "one, two, and three"
    )
    assert humanize.natural_list(["one", "two"], oxford_comma=True) == "one and two"
