"""Lists related humanization."""

from __future__ import annotations

from typing import Any

__all__ = ["naturallist"]


def naturallist(items: list[Any]) -> str:
    """Natural list.

    Convert a list of items into a human-readable string with commas and 'and'.

    Examples:
        >>> naturallist(["one", "two", "three"])
        'one, two and three'
        >>> naturallist(["one", "two"])
        'one and two'
        >>> naturallist(["one"])
        'one'

    Args:
        items (list): An iterable of items.

    Returns:
        str: A string with commas and 'and' in the right places.
    """
    if len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return f"{str(items[0])} and {str(items[1])}"
    else:
        return ", ".join(str(item) for item in items[:-1]) + f" and {str(items[-1])}"
