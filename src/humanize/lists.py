"""Lists related humanization."""

from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Iterable
    from typing import Any

__all__ = ["natural_list"]


def natural_list(items: Iterable[Any], conjunction: str = "and") -> str:
    """Natural list.

    Convert an iterable of items into a human-readable string with commas and
    a conjunction.

    Examples:
        >>> natural_list(["one", "two", "three"])
        'one, two and three'
        >>> natural_list(["one", "two"])
        'one and two'
        >>> natural_list(["one", "two", "three"], conjunction="or")
        'one, two or three'
        >>> natural_list(["one"])
        'one'

    Args:
        items (Iterable): An iterable of items.
        conjunction (str): The word or phrase joining the final two items.

    Returns:
        str: A string with commas and the conjunction in the right places.
    """
    item_list = [str(item) for item in items]
    if not item_list:
        return ""
    if len(item_list) == 1:
        return item_list[0]
    elif len(item_list) == 2:
        return f"{item_list[0]} {conjunction} {item_list[1]}"
    else:
        return ", ".join(item_list[:-1]) + f" {conjunction} {item_list[-1]}"
