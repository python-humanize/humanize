"""Bits and bytes related humanization."""

from __future__ import annotations

__lazy_modules__ = {"humanize.i18n", "math"}

import re
from math import log

from humanize.i18n import _gettext as _

suffixes = {
    "decimal": (
        "kB",
        "MB",
        "GB",
        "TB",
        "PB",
        "EB",
        "ZB",
        "YB",
        "RB",
        "QB",
    ),
    "binary": (
        "KiB",
        "MiB",
        "GiB",
        "TiB",
        "PiB",
        "EiB",
        "ZiB",
        "YiB",
        "RiB",
        "QiB",
    ),
    "gnu": "KMGTPEZYRQ",
}

# Matches the numeric part of a rendered mantissa, ignoring any surrounding
# text a custom `format` may add (e.g. "%.1f~" renders "976.6~").
# Matches a single printf-style conversion in a custom format string, or a
# literal "%%" escape. Used to locate the numeric conversion whose rendering
# drives the rounding carry-over check in naturalsize().
_FORMAT_CONVERSION_RE = re.compile(r"%%|%[-+ #0]*\d*(?:\.\d*)?[hlL]?[diueEfFgGrsa]")


def naturalsize(
    value: float | str,
    binary: bool = False,
    gnu: bool = False,
    format: str = "%.1f",
) -> str:
    """Format a number of bytes like a human-readable filesize (e.g. 10 kB).

    By default, decimal suffixes (kB, MB) are used.

    Non-GNU modes are compatible with jinja2's `filesizeformat` filter.

    Examples:
        ```pycon
        >>> naturalsize(3000000)
        '3.0 MB'
        >>> naturalsize(300, False, True)
        '300B'
        >>> naturalsize(3000, False, True)
        '2.9K'
        >>> naturalsize(3000, False, True, "%.3f")
        '2.930K'
        >>> naturalsize(3000, True)
        '2.9 KiB'
        >>> naturalsize(10**28)
        '10.0 RB'
        >>> naturalsize(10**34 * 3)
        '30000.0 QB'
        >>> naturalsize(-4096, True)
        '-4.0 KiB'

        ```

    Args:
        value (int, float, str): Integer to convert.
        binary (bool): If `True`, uses binary suffixes (KiB, MiB) with base
            2<sup>10</sup> instead of 10<sup>3</sup>.
        gnu (bool): If `True`, the binary argument is ignored and GNU-style
            (`ls -sh` style) prefixes are used (K, M) with the 2**10 definition.
        format (str): Custom formatter.

    Returns:
        str: Human readable representation of a filesize.
    """
    if gnu:
        suffix = suffixes["gnu"]
    elif binary:
        suffix = suffixes["binary"]
    else:
        suffix = suffixes["decimal"]

    base = 1024 if (gnu or binary) else 1000
    bytes_ = float(value)
    abs_bytes = abs(bytes_)

    if abs_bytes == 1 and not gnu:
        return _("%d Byte") % int(bytes_)

    if abs_bytes < base:
        return f"{int(bytes_)}B" if gnu else _("%d Bytes") % int(bytes_)

    exp = int(min(log(abs_bytes, base), len(suffix)))
    # The suffix is chosen from the unrounded byte count, but `format` rounds the
    # mantissa afterward; rounding can push it up to `base` (e.g. 999999 is
    # 999.999 kB, which formats to "1000.0 kB"). When that happens and a larger
    # suffix is available, step up one suffix so the result reads "1.0 MB".
    # `format` may contain literal text around the conversion, even digits
    # (e.g. "v2000: %.1f"), so the conversion itself is located first and
    # rendered alone for the numeric check: number-hunting in the rendered
    # string would trip over the literal text instead of the mantissa.
    # Parsing the whole rendered string raises ValueError, and comparing
    # rendered strings misjudges formats that do not round-trip through
    # str -> float (e.g. "%.0e" % 1024 is "1e+03").
    conversion = next(
        (
            match.group()
            for match in _FORMAT_CONVERSION_RE.finditer(format)
            if match.group() != "%%"
        ),
        None,
    )
    if exp < len(suffix) and conversion is not None:
        try:
            rendered = abs(float(conversion % (abs_bytes / (base**exp))))
        except (TypeError, ValueError):
            # Exotic conversions (e.g. "%a") do not render a plain number;
            # leave the suffix choice alone rather than guessing.
            rendered = 0.0
        if rendered >= base:
            exp += 1
    space = "" if gnu else " "
    ret: str = format % (bytes_ / (base**exp)) + space + _(suffix[exp - 1])
    return ret
