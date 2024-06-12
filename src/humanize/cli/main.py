"""Main for CLI."""

from __future__ import annotations

import importlib.metadata
import sys
from argparse import ArgumentParser, ArgumentTypeError

from humanize import filesize, i18n, number
from humanize.cli.argutils import ArgContext
from humanize.cli.filesize import AddNaturalsizeArguments
from humanize.cli.number import (
    AddApnumberArguments,
    AddClampArguments,
    AddFractionalArguments,
    AddIntcommaArguments,
    AddIntwordArguments,
    AddMetricArguments,
    AddOrdinalArguments,
    AddScientificArguments,
)


def create_parser() -> ArgumentParser:
    """Create ArgumentParser."""
    name = __name__.split(".")[0]
    version = importlib.metadata.version(name)
    summary = importlib.metadata.metadata(name).get("Summary")

    parser = ArgumentParser(prog=name, description=summary)
    parser.add_argument(
        "-v", "--version", action="version", version=f"%(prog)s {version}"
    )

    subparsers = parser.add_subparsers(metavar="FUNCTION", required=True)
    funcs = (
        filesize.naturalsize,
        number.apnumber,
        number.clamp,
        number.fractional,
        number.intcomma,
        number.intword,
        number.metric,
        number.ordinal,
        number.scientific,
    )

    for func in sorted(funcs, key=lambda func: func.__name__):
        func_doc = getattr(func, "__doc__", "").splitlines()[0]
        subparser = subparsers.add_parser(func.__name__, help=func_doc)

        cameled_name = "".join(map(str.capitalize, func.__name__.split("_")))
        add_arguments = {
            cls.__name__: cls
            for cls in (
                AddApnumberArguments,
                AddClampArguments,
                AddFractionalArguments,
                AddIntcommaArguments,
                AddIntwordArguments,
                AddMetricArguments,
                AddNaturalsizeArguments,
                AddOrdinalArguments,
                AddScientificArguments,
            )
        }[f"Add{cameled_name}Arguments"](func)
        add_arguments(subparser)

    return parser


def main() -> None:
    """Run humanize command."""
    kwargs = vars(create_parser().parse_args())
    context: ArgContext = kwargs.pop("context")

    locale = kwargs.pop("locale")
    if locale:
        try:
            i18n.activate(locale)
        except FileNotFoundError as e:
            context.error(f"{e} locale: {locale}")

    values = kwargs.pop("values")
    if not values:
        # replacing with iterator wrapping stdin
        values = map(context.type_, map(str.strip, sys.stdin))

    try:
        for value in values:
            try:
                print(context.func(value, **kwargs))
            except ValueError as e:
                context.error(str(e))
    except ArgumentTypeError as e:
        context.error(str(e))
    finally:
        i18n.deactivate()
