"""Tests for the humanize command-line interface."""

from __future__ import annotations

import io
import os
import subprocess
import sys
from pathlib import Path

import pytest

from humanize.cli import main

ROOT = Path(__file__).parents[1]


def run_cli(
    args: list[str],
    input_text: str = "",
    *,
    interactive: bool = False,
) -> tuple[int, str, str]:
    stdin = io.StringIO(input_text)
    stdin.isatty = lambda: interactive  # type: ignore[method-assign]
    stdout = io.StringIO()
    stderr = io.StringIO()

    old_stdin, old_stdout, old_stderr = sys.stdin, sys.stdout, sys.stderr
    try:
        sys.stdin, sys.stdout, sys.stderr = stdin, stdout, stderr
        try:
            status = main(args)
        except SystemExit as error:
            status = error.code if isinstance(error.code, int) else 1
    finally:
        sys.stdin, sys.stdout, sys.stderr = old_stdin, old_stdout, old_stderr
    return status, stdout.getvalue(), stderr.getvalue()


def test_naturalsize_defaults_to_decimal() -> None:
    assert run_cli(["naturalsize", "8589934592"]) == (0, "8.6 GB\n", "")


@pytest.mark.parametrize(
    "option, expected",
    [
        ("--binary", "8.0 GiB\n"),
        ("--gnu", "8.0G\n"),
    ],
)
def test_naturalsize_supports_unit_options(option: str, expected: str) -> None:
    assert run_cli(["naturalsize", option, "8589934592"]) == (0, expected, "")


def test_naturalsize_supports_custom_format() -> None:
    assert run_cli(["naturalsize", "--format", "%.2f", "3000"]) == (
        0,
        "3.00 kB\n",
        "",
    )


def test_naturalsize_reads_one_value_per_piped_line() -> None:
    assert run_cli(["naturalsize"], "1000\n2048\n") == (
        0,
        "1.0 kB\n2.0 kB\n",
        "",
    )


def test_naturalsize_reports_invalid_piped_line() -> None:
    assert run_cli(["naturalsize"], "1000\nnot-a-number\n3000\n") == (
        2,
        "1.0 kB\n",
        (
            "humanize: error: invalid value on line 2 'not-a-number': "
            "could not convert string to float: 'not-a-number'\n"
        ),
    )


def test_naturalsize_reports_invalid_value() -> None:
    status, stdout, stderr = run_cli(["naturalsize", "invalid"])

    assert status == 2
    assert stdout == ""
    assert "invalid value 'invalid'" in stderr
    assert "could not convert string to float" in stderr


def test_naturalsize_reports_malformed_format() -> None:
    status, stdout, stderr = run_cli(["naturalsize", "--format", "%q", "3000"])

    assert status == 2
    assert stdout == ""
    assert "invalid format '%q'" in stderr
    assert "unsupported format character" in stderr


def test_naturalsize_requires_value_for_interactive_stdin() -> None:
    assert run_cli(["naturalsize"], interactive=True) == (
        2,
        "",
        "humanize: error: a value is required when stdin is interactive\n",
    )


def test_help() -> None:
    status, stdout, stderr = run_cli(["naturalsize", "--help"])

    assert status == 0
    assert "format byte counts as human-readable file sizes" in stdout
    assert "--binary" in stdout
    assert "--gnu" in stdout
    assert "--format" in stdout
    assert stderr == ""


def test_python_module_invocation() -> None:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT / "src")
    result = subprocess.run(
        [sys.executable, "-m", "humanize", "naturalsize", "8589934592"],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert result.stdout == "8.6 GB\n"
    assert result.stderr == ""
