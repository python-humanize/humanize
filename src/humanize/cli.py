"""Command-line interface for humanize."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Iterable, Sequence
from typing import TextIO

from humanize.filesize import naturalsize


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="humanize")
    commands = parser.add_subparsers(dest="command", required=True)

    filesize = commands.add_parser(
        "naturalsize",
        help="format byte counts as human-readable file sizes",
        description="format byte counts as human-readable file sizes",
    )
    filesize.add_argument(
        "value",
        nargs="?",
        help="number of bytes; read one value per line from stdin when omitted",
    )
    filesize.add_argument(
        "--binary",
        action="store_true",
        help="use binary units such as KiB and MiB",
    )
    filesize.add_argument(
        "--gnu",
        action="store_true",
        help="use GNU-style binary units such as K and M",
    )
    filesize.add_argument(
        "--format",
        default="%.1f",
        help="format string for the numeric portion (default: %%.1f)",
    )
    return parser


def _format_value(value: str, args: argparse.Namespace) -> str:
    return naturalsize(value, binary=args.binary, gnu=args.gnu, format=args.format)


def _run_naturalsize(
    args: argparse.Namespace,
    stdin: TextIO,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        _format_value("1024", args)
    except (TypeError, ValueError, OverflowError) as error:
        stderr.write(f"humanize: error: invalid format {args.format!r}: {error}\n")
        return 2

    if args.value is not None:
        values: Iterable[tuple[int, str]] = ((1, args.value),)
    elif stdin.isatty():
        stderr.write("humanize: error: a value is required when stdin is interactive\n")
        return 2
    else:
        values = enumerate(stdin, start=1)

    for line_number, value in values:
        value = value.strip()
        try:
            result = _format_value(value, args)
        except (TypeError, ValueError, OverflowError) as error:
            if args.value is not None:
                stderr.write(f"humanize: error: invalid value {value!r}: {error}\n")
            else:
                stderr.write(
                    f"humanize: error: invalid value on line {line_number} "
                    f"{value!r}: {error}\n"
                )
            return 2
        stdout.write(result + "\n")

    return 0


def main(argv: Sequence[str] | None = None) -> int:
    """Run the humanize command-line interface."""
    args = _parser().parse_args(argv)
    if args.command == "naturalsize":
        return _run_naturalsize(args, sys.stdin, sys.stdout, sys.stderr)
    command = f"unknown command: {args.command}"
    raise AssertionError(command)
