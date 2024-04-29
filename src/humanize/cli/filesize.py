"""AddArguments for filesize module."""

from __future__ import annotations

from dataclasses import dataclass

from humanize.cli.argutils import AddArguments, FilesizeFlag


@dataclass(frozen=True)
class AddNaturalsizeArguments(AddArguments):
    """naturalsize function from filesize module."""

    helps: tuple[tuple[FilesizeFlag, str], ...] = (
        (
            "--binary",
            """
             If `True`, uses binary suffixes (KiB, MiB) with base 2**10 instead
             of 10**3.
             """,
        ),
        (
            "--gnu",
            """
             If `True`, the binary argument is ignored and GNU-style (`ls -sh`
             style) prefixes are used (K, M) with the 2**10 definition.
             """,
        ),
        ("--format", "Custom formatter."),
    )
