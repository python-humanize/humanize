"""Bitrate related humanization."""

from __future__ import annotations

from math import log


def natural_bitrate(value: float | str, format: str = "%.1f") -> str:
    """Format a number of bits per second like a human-readable bitrate (e.g. 1 kbps).

    Uses SI standard (1000-based) prefixes.

    Examples:
        ```pycon
        >>> natural_bitrate(1000)
        '1.0 kbps'
        >>> natural_bitrate(5200)
        '5.2 kbps'
        >>> natural_bitrate(1000000)
        '1.0 Mbps'
        >>> natural_bitrate(1500000000)
        '1.5 Gbps'
        >>> natural_bitrate(1000000000000)
        '1.0 Tbps'
        >>> natural_bitrate(500)
        '500 bps'
        >>> natural_bitrate(0)
        '0 bps'
        >>> natural_bitrate(-1000)
        '-1.0 kbps'

        ```

    Args:
        value (int, float, str): Integer to convert.
        format (str): Custom formatter.

    Returns:
        str: Human readable representation of a bitrate.
    """
    suffixes = (" kbps", " Mbps", " Gbps", " Tbps")
    base = 1000
    bps = float(value)
    abs_bps = abs(bps)

    if abs_bps < base:
        return f"{int(bps)} bps"

    exp = int(min(log(abs_bps, base), len(suffixes)))
    ret: str = format % (bps / (base**exp)) + suffixes[exp - 1]
    return ret
