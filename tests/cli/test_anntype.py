"""Tests ArgType."""

from __future__ import annotations

from argparse import ArgumentTypeError
from typing import Any

import pytest

from humanize.cli.anntype import AnnotationType


@pytest.mark.parametrize(
    "annotation, string, expect",
    [
        ("int", "0", 0),
        ("float | str", "1", 1.0),
        ("float | str", "spam", "spam"),
        ("NumberOrString", "1", "1"),
        ("NumberOrString", "spam", "spam"),
        ("float | None", "2", 2.0),
        ("NumberOrString | None", "2", "2"),
        ("NumberOrString | None", "", ""),
        ("NumberOrString | None", "None", "None"),
    ],
)
def test_argtype(
    annotation: str,
    string: str,
    expect: Any,
) -> None:
    assert AnnotationType.of(annotation)(string) == expect


@pytest.mark.parametrize(
    "annotation, string, exc",
    [
        ("int", "spam", ArgumentTypeError),
        ("Spam", "spam", ValueError),
        ("Ellipsis", "...", ValueError),
    ],
)
def test_argtype_error(
    annotation: str,
    string: str,
    exc: type[BaseException],
) -> None:
    with pytest.raises(exc):
        AnnotationType.of(annotation)(string)
