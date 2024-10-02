"""Main package for humanize."""

from __future__ import annotations

from humanize.filesize import naturalsize
from humanize.i18n import activate, deactivate, decimal_separator, thousands_separator
from humanize.lists import naturallist
from humanize.number import (
    apnumber,
    clamp,
    fractional,
    intcomma,
    intword,
    metric,
    ordinal,
    scientific,
)
from humanize.time import (
    naturaldate,
    naturalday,
    naturaldelta,
    naturaltime,
    precisedelta,
)

from ._version import __version__

__all__ = [
    "__version__",
    "activate",
    "apnumber",
    "clamp",
    "deactivate",
    "decimal_separator",
    "fractional",
    "intcomma",
    "intword",
    "metric",
    "naturaldate",
    "naturalday",
    "naturaldelta",
    "naturalsize",
    "naturaltime",
    "ordinal",
    "precisedelta",
    "scientific",
    "thousands_separator",
    "naturallist",
]
