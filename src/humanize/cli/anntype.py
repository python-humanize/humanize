"""Argument type to be used in ArgumentParser."""

from __future__ import annotations

import builtins
import sys
from argparse import ArgumentTypeError
from collections import UserList
from typing import Any

if sys.version_info >= (3, 9):
    from collections.abc import Callable

    TypeList = UserList[Callable[[str], Any]]
else:
    # generics syntax is not supported in standard collections before PEP 585
    TypeList = UserList


class AnnotationType(TypeList):
    """Argument type based on function's annotation."""

    def __init__(self, initlist: TypeList) -> None:
        """Use the `of` class method to get an instance from annotation."""
        super().__init__(initlist)
        self.annotation = ""

    def __hash__(self) -> int:
        """ArgumentParser requires each type to be hashable."""
        return hash(self.annotation)

    def __call__(self, string: str) -> Any:
        """Attempt conversion."""
        if self:
            try:
                return self[0](string)
            except (TypeError, ValueError):
                return AnnotationType.__call__(self[1:], string)
        else:
            raise ArgumentTypeError("Can't convert '%s'" % string)

    @classmethod
    def of(cls, annotation: str) -> AnnotationType:
        """Construction using type hints in annotation."""
        argtype = cls(TypeList())
        argtype.annotation = annotation

        for hint in map(str.strip, annotation.split("|")):
            try:
                obj = getattr(builtins, hint)
            except AttributeError:
                if hint == "NumberOrString":
                    argtype.append(str)
                else:
                    raise ValueError("Unknown hint '%s' was found" % hint)
            else:
                if callable(obj):
                    argtype.append(obj)  # such as int, str, etc.
                elif obj is None:
                    # ignoring the 'None' hint here because ArgumentParser
                    # doesn't convert None arguments
                    pass
                else:
                    raise ValueError("Unsupported hint '%s' was found" % hint)

        return argtype
