"""ArgumentParser utilities."""

from __future__ import annotations

import sys
from abc import ABC
from argparse import ArgumentParser
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Any, Literal, NamedTuple, Union

if sys.version_info >= (3, 9):
    from collections.abc import Callable
    from typing import Tuple  # UP006 is suppressed in this file
else:
    # generics syntax is not supported in standard collections before PEP 585
    from typing import Callable, Tuple

from humanize.cli.anntype import AnnotationType

FilesizeFlag = Literal[
    "--binary",
    "--format",
    "--gnu",
]
NumberFlag = Literal[
    "--ceil",
    "--ceil-token",
    "--floor",
    "--floor-token",
    "--format",
    "--gender",
    "--ndigits",
    "--precision",
    "--unit",
]

ArgFlag = Union[FilesizeFlag, NumberFlag]
ArgParam = Union[
    Tuple[Literal["action"], Literal["store_true", "store_false"]],
    Tuple[Literal["default"], Any],
    Tuple[Literal["type"], AnnotationType],
]

ArgFlagParams = Tuple[ArgFlag, Tuple[ArgParam, ...]]
ArgError = Callable[[str], None]
ArgHelp = str

LOCALE_HELP = "Language name, e.g. `en_GB`."
VALUES_HELP = "Values to humanize. If not found, humanizes inputs from stdin."
HELP_SUFFIX = " (default: `%(default)s`)"


class ArgContext(NamedTuple):
    """Execution context to be set in ArgumentParser."""

    func: Callable[..., Any]
    type_: AnnotationType
    error: ArgError


class PositionalArgumentFoundError(ValueError):
    """Raised when an unexpected positional argument is found."""

    def __init__(self, name: str):
        """Init with an error message that includes the argument name."""
        super().__init__(f"Positional argument '{name}' was found.")


def _extract_flags(parameters: Iterable[Parameter]) -> Iterator[ArgFlagParams]:
    """Yield flag and its params from function's parameters."""
    for parameter in parameters:
        if parameter.default is Parameter.empty:
            # expect only optional keyword arguments for flags
            raise PositionalArgumentFoundError(parameter.name)

        kebabed_name = parameter.name.replace("_", "-")
        flag: ArgFlag = f"--{kebabed_name}"  # type: ignore[assignment]
        params: Tuple[ArgParam, ...] = (("default", parameter.default),)

        if parameter.default is False:
            params += (("action", "store_true"),)
        elif parameter.default is True:
            params += (("action", "store_false"),)
            # flip the flag with `--no-` prefix
            flag = f"--no-{kebabed_name}"  # type: ignore[assignment]
        else:
            params += (("type", AnnotationType.of(parameter.annotation)),)

        yield (flag, params)


@dataclass(frozen=True)
class AddArguments(ABC):
    """Base class to organize functions in sub-classes."""

    func: Callable[..., Any]
    helps: Tuple[Tuple[ArgFlag, ArgHelp], ...] = ()

    def __call__(self, parser: ArgumentParser) -> None:
        """Populate parser with function."""
        parameters = dict(signature(self.func).parameters)

        type_ = AnnotationType.of(parameters.pop("value").annotation)
        # add value*s* argument using value's argument type
        parser.add_argument("values", nargs="*", help=VALUES_HELP, type=type_)

        # add flags
        parser.add_argument("--locale", help=LOCALE_HELP)
        for flag, params in _extract_flags(parameters.values()):
            help_ = dict(self.helps)[flag] + HELP_SUFFIX
            parser.add_argument(flag, help=help_, **dict(params))

        # set execution context
        context = ArgContext(func=self.func, type_=type_, error=parser.error)
        parser.set_defaults(context=context)
