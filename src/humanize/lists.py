from typing import AnyStr, List

__all__ = ["naturallist"]


def naturallist(items: List[AnyStr]) -> str:
    """Convert a list of items into a human-readable string with commas and 'and'

    Args:
        items (list): A list of strings
    Returns:
        str: A string with commas and 'and' in the right places
    Examples:
        >>> naturallist(["one", "two", "three"])
        'one, two and three'
        >>> naturallist(["one", "two"])
        'one and two'
        >>> naturallist(["one"])
        'one'
    """

    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return ", ".join(items[:-1]) + f" and {items[-1]}"
