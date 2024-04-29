"""AddArguments for number module."""

from __future__ import annotations

from dataclasses import dataclass

from humanize.cli.argutils import AddArguments, NumberFlag


@dataclass(frozen=True)
class AddApnumberArguments(AddArguments):
    """naturalsize function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = ()


@dataclass(frozen=True)
class AddClampArguments(AddArguments):
    """clamp function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = (
        ("--format", "A formatting string."),
        ("--floor", "Smallest value before clamping."),
        ("--ceil", "Largest value before clamping."),
        (
            "--floor-token",
            """
             If value is smaller than floor, token will be prepended to output.
             """,
        ),
        (
            "--ceil-token",
            """
             If value is larger than ceil, token will be prepended to output.
             """,
        ),
    )


@dataclass(frozen=True)
class AddFractionalArguments(AddArguments):
    """fractional function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = ()


@dataclass(frozen=True)
class AddIntcommaArguments(AddArguments):
    """intcomma function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = (
        (
            "--ndigits",
            """
             Digits of precision for rounding after the decimal point.
             """,
        ),
    )


@dataclass(frozen=True)
class AddIntwordArguments(AddArguments):
    """intword function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = (
        (
            "--format",
            """
             To change the number of decimal or general format of the number
             portion.
             """,
        ),
    )


@dataclass(frozen=True)
class AddMetricArguments(AddArguments):
    """metric function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = (
        ("--unit", "Optional base unit."),
        ("--precision", "The number of digits the output should contain."),
    )


@dataclass(frozen=True)
class AddOrdinalArguments(AddArguments):
    """ordinal function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = (
        (
            "--gender",
            """
             Gender for translations. Accepts either "male" or "female".
             """,
        ),
    )


@dataclass(frozen=True)
class AddScientificArguments(AddArguments):
    """scientific function from number module."""

    helps: tuple[tuple[NumberFlag, str], ...] = (
        ("--precision", "Number of decimal for first part of the number."),
    )
