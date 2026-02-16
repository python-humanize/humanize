"""Bits and bytes related humanization."""

from __future__ import annotations

from math import log
from humanize import i18n

suffixes = {
    "decimal": ("kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB", "RB", "QB"),
    "binary": ("KiB", "MiB", "GiB", "TiB", "PiB", "EiB", "ZiB", "YiB", "RiB", "QiB"),
    "gnu": "KMGTPEZYRQ",
}


def _translation():
    """Return active gettext translation (or None)."""
    try:
        return i18n.get_translation()
    except Exception:
        return None


def naturalsize(
    value: float | str,
    binary: bool = False,
    gnu: bool = False,
    format: str = "%.1f",
) -> str:
    t = _translation()
    _ = (t.gettext if t is not None else (lambda s: s))

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
        return f"{int(bytes_)} {_('Byte')}"

    if abs_bytes < base:
        if gnu:
            return f"{int(bytes_)}B"
        return f"{int(bytes_)} {_('Bytes')}"

    exp = int(min(log(abs_bytes, base), len(suffix)))
    number = format % (bytes_ / (base**exp))

    # French decimal separator: use comma instead of dot
    if t is not None:
        lang = (t.info().get("language", "") or "").lower()
        if lang.startswith("fr"):
            number = number.replace(".", ",")

    if gnu:
        return number + suffix[exp - 1]

    unit = _(suffix[exp - 1])
    return f"{number} {unit}"
