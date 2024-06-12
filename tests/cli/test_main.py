"""Tests for CLI main."""

from __future__ import annotations

from io import StringIO

import pytest

from humanize.cli.main import main


@pytest.mark.parametrize(
    "cmd, stdin_lines, stdout_lines",
    [
        ("humanize naturalsize 300 40000", None, "300 Bytes\n40.0 kB"),
        ("humanize naturalsize", "300\n40000\n", "300 Bytes\n40.0 kB"),
        ("humanize naturalsize 4096 --binary --format %.2f", None, "4.00 KiB"),
        ("humanize naturalsize -4096 --gnu", None, "-4.0K"),
        ("humanize apnumber 5", None, "five"),
        ("humanize apnumber", "9", "nine"),
        ("humanize clamp", "123.456", "123.456"),
        ("humanize clamp --floor 5 --ceil 95 3 98", None, "<5.0\n>95.0"),
        ("humanize clamp --floor 5 --ceil 95", "5\n95", "5.0\n95.0"),
        ("humanize fractional .5 .9 1/3", None, "1/2\n9/10\n1/3"),
        ("humanize fractional", ".5\n.9\n1/3", "1/2\n9/10\n1/3"),
        ("humanize intcomma 10000", None, "10,000"),
        ("humanize intcomma", "10000", "10,000"),
        ("humanize intword 1000 4000", None, "1.0 thousand\n4.0 thousand"),
        ("humanize intword", "1000\n4000", "1.0 thousand\n4.0 thousand"),
        ("humanize metric --unit V 1500 1e-14", None, "1.50 kV\n10.0 fV"),
        ("humanize metric --unit V", "1500\n1e-14", "1.50 kV\n10.0 fV"),
        ("humanize ordinal 0 1 2", None, "0th\n1st\n2nd"),
        ("humanize ordinal", "0\n1\n2", "0th\n1st\n2nd"),
        ("humanize scientific 0.1 100", None, "1.00 x 10⁻¹\n1.00 x 10²"),
        ("humanize scientific", "0.1\n100", "1.00 x 10⁻¹\n1.00 x 10²"),
    ],
)
def test_main(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    cmd: str,
    stdin_lines: str | None,
    stdout_lines: str,
) -> None:
    with monkeypatch.context() as m:
        m.setattr("sys.argv", cmd.split())
        m.setattr("sys.stdin", StringIO(stdin_lines or ""))
        try:
            main()
        except SystemExit as e:
            pytest.fail(f"Unexpected {e} was raised.")

    captured = capsys.readouterr()
    assert captured.out.splitlines() == stdout_lines.splitlines()
    assert captured.err == ""


@pytest.mark.parametrize(
    "cmd, stdin_lines, stdout_lines",
    [
        ("humanize naturalsize --locale ja_JP", "5", "5 Bytes"),
        ("humanize apnumber --locale ja_JP", "5", "五"),
        ("humanize intcomma --locale de_DE 1000,12", None, "1.000,12"),
        ("humanize intcomma --locale de_DE", "1000,12", "1.000,12"),
        ("humanize ordinal --locale fr_FR --gender male 1", None, "1er"),
        ("humanize ordinal --locale fr_FR --gender female", "1", "1ère"),
    ],
)
def test_main_locale(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    cmd: str,
    stdin_lines: str | None,
    stdout_lines: str,
) -> None:
    with monkeypatch.context() as m:
        m.setattr("sys.argv", cmd.split())
        m.setattr("sys.stdin", StringIO(stdin_lines or ""))
        try:
            main()
        except SystemExit as e:
            pytest.fail(f"Unexpected {e} was raised.")

    captured = capsys.readouterr()
    if "FileNotFoundError" in captured.err:
        pytest.skip(".mo locale file was not found")
    assert captured.out.splitlines() == stdout_lines.splitlines()
    assert captured.err == ""


@pytest.mark.parametrize(
    "cmd, stdin_lines, stdout_lines, stderr_keyword, exitcode",
    [
        ("humanize naturalsize 300 400A", None, "300 Bytes", "400A", 2),
        ("humanize naturalsize", "300\n400A", "300 Bytes", "400A", 2),
        ("humanize clamp 3 4A", None, "", "4A", 2),  # exit before execution
        ("humanize clamp", "3\n4A", "3.0", "4A", 2),  # exit on exception
    ],
)
def test_main_error(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    cmd: str,
    stdin_lines: str | None,
    stdout_lines: str,
    stderr_keyword: str,
    exitcode: int,
) -> None:
    with monkeypatch.context() as m:
        m.setattr("sys.argv", cmd.split())
        m.setattr("sys.stdin", StringIO(stdin_lines or ""))
        try:
            main()
        except SystemExit as e:
            assert e.code == exitcode
        else:
            pytest.fail("No SystemExit was caught")

    captured = capsys.readouterr()
    assert captured.out.splitlines() == stdout_lines.splitlines()
    assert stderr_keyword in captured.err
