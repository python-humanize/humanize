"""Lists related humanization."""

from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

__all__ = ["natural_list"]


def natural_list(items: Iterable[Any], oxford_comma: bool = False) -> str:
    """Natural list.

    Convert a list or iterable of items into a human-readable string with
    commas and 'and'.

    Examples:
        >>> natural_list(["one", "two", "three"])
        'one, two and three'
        >>> natural_list(["one", "two", "three"], oxford_comma=True)
        'one, two, and three'
        >>> natural_list(["one", "two"])
        'one and two'
        >>> natural_list(["one"])
        'one'

    Args:
        items (iterable): An iterable of items.
        oxford_comma (bool): If True, includes an Oxford comma before 'and'
            for 3+ items.

    Returns:
        str: A string with commas and 'and' in the right places.
    """
    item_list = [str(item) for item in items]
    if not item_list:
        return ""
    if len(item_list) == 1:
        return item_list[0]
    elif len(item_list) == 2:
        return f"{item_list[0]} and {item_list[1]}"
    else:
        sep = ", and " if oxford_comma else " and "
        return ", ".join(item_list[:-1]) + f"{sep}{item_list[-1]}"
