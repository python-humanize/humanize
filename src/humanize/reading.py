"""Reading-time humanization (custom extension, Arda-06 fork)."""

from __future__ import annotations

import datetime as dt
import math
import re

from .time import naturaldelta

__all__ = ["reading_time"]

_WORD_RE = re.compile(r"\b\w+\b", re.UNICODE)


def reading_time(text: str, wpm: int = 200, *, minimum_seconds: int = 1) -> str:
    """Return a human-readable estimate of how long *text* takes to read.

    Examples:
        ```pycon
        >>> reading_time("word " * 400)
        '2 minutes'
        >>> reading_time("Hello world")
        'a second'
        >>> reading_time("")
        'a moment'

        ```

    Args:
        text: The text to estimate. Words are counted with a Unicode-aware regex.
        wpm: Reading speed in words per minute. Must be a positive integer.
        minimum_seconds: Non-empty text never reports less than this.

    Returns:
        A string like ``"3 minutes"`` produced by ``humanize.naturaldelta``.

    Raises:
        TypeError: If *text* is not a string.
        ValueError: If *wpm* is not positive.
    """
    if not isinstance(text, str):
        msg = f"text must be str, not {type(text).__name__}"
        raise TypeError(msg)
    if wpm <= 0:
        msg = "wpm must be a positive integer"
        raise ValueError(msg)

    words = len(_WORD_RE.findall(text))
    if words == 0:
        return naturaldelta(dt.timedelta(0))

    seconds = max(minimum_seconds, math.ceil(words * 60 / wpm))
    return naturaldelta(dt.timedelta(seconds=seconds))
