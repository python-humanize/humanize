"""Bits and bytes related humanization."""

from __future__ import annotations

from math import log

from humanize.i18n import gettext as _


_SUFFIXES = {
    "decimal": (
        _(" kB"),
        _(" MB"),
        _(" GB"),
        _(" TB"),
        _(" PB"),
        _(" EB"),
        _(" ZB"),
        _(" YB"),
        _(" RB"),
        _(" QB"),
    ),
    "binary": (
        _(" KiB"),
        _(" MiB"),
        _(" GiB"),
        _(" TiB"),
        _(" PiB"),
        _(" EiB"),
        _(" ZiB"),
        _(" YiB"),
        _(" RiB"),
        _(" QiB"),
    ),
}


def naturalsize(
    value: float | str,
    binary: bool = False,
    format: str = "%.1f",
) -> str:
    """
    Format a number of bytes like a human-readable file size.

    Examples:
        >>> naturalsize(42)
        '42 Bytes'
        >>> naturalsize(42000)
        '42.0 kB'
        >>> naturalsize(42000000)
        '42.0 MB'

    When a locale is activated via ``humanize.i18n.activate()``,
    the unit suffixes will be translated accordingly.

    :param value: The number of bytes.
    :param binary: Use binary (powers of 1024) units instead of decimal.
    :param format: Numeric format string.
    :return: Human-readable file size.
    """

    try:
        bytes_value = float(value)
    except (TypeError, ValueError):
        return str(value)

    if bytes_value == 1:
        return _("1 Byte")
    if bytes_value < 1024:
        return _("%d Bytes") % bytes_value

    base = 1024 if binary else 1000
    exp = int(log(bytes_value, base))
    exp = min(exp, len(_SUFFIXES["binary"]) if binary else len(_SUFFIXES["decimal"]))

    value = bytes_value / base**exp

    suffix = (
        _SUFFIXES["binary"][exp - 1]
        if binary
        else _SUFFIXES["decimal"][exp - 1]
    )

    return (format % value) + suffix
