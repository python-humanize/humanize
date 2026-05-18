"""Lists related humanization."""

from __future__ import annotations

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any

__all__ = ["natural_list"]


def natural_list(items: list[Any], *, conjunction: str = "and") -> str:
    """Natural list.

    Convert a list of items into a human-readable string with commas and a
    conjunction.

    Examples:
        >>> natural_list(["one", "two", "three"])
        'one, two and three'
        >>> natural_list(["one", "two"])
        'one and two'
        >>> natural_list(["one"])
        'one'
        >>> natural_list(["one", "two", "three"], conjunction="or")
        'one, two or three'

    Args:
        items (list): An iterable of items.
        conjunction (str): The word used to join the last item, defaults to 'and'.

    Returns:
        str: A string with commas and the conjunction in the right places.
    """
    if len(items) == 1:
        return str(items[0])
    elif len(items) == 2:
        return f"{str(items[0])} {conjunction} {str(items[1])}"
    else:
        return (
            ", ".join([str(item) for item in items[:-1]])
            + f" {conjunction} {str(items[-1])}"
        )
