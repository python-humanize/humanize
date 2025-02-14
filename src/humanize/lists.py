"""Lists related humanization."""

from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

__all__ = ["natural_list", "natural_list_etc"]


def natural_list(items: list[Any]) -> str:
    """Natural list.

    Convert a list of items into a human-readable string with commas and 'and'.

    Examples:
        >>> natural_list(["one", "two", "three"])
        'one, two and three'
        >>> natural_list(["one", "two"])
        'one and two'
        >>> natural_list(["one"])
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


def natural_list_etc(items: list[Any], limit: int) -> str:
    """Natural list.

    Convert a list of items into a human-readable string with commas and 'etc.'

    Examples:
        >>> natural_list_etc(["one", "two", "three", "four", "five"], 4)
        'one, two, three, four, etc.'
        >>> natural_list_etc(["one", "two", "three"], 4)
        'one, two and three'
        >>> natural_list_etc(["one", "two"], 3)
        'one and two'
        >>> natural_list_etc(["one"], 2)
        'one'

    Args:
        items (list): An iterable of items.
        limit (int): limitation of items when "etc" is appeared in the end.

    Returns:
        str: A string with commas and 'and' in the right places.
    """
    leng_of_items = len(items)
    if leng_of_items == limit or leng_of_items < limit:
        return natural_list(items)
    else:
        return (
            ", ".join(str(item) for item in items[: limit - leng_of_items]) + ", etc."
        )
