"""HELD-OUT — non-finite. DISJOINT from the oracle. DO NOT show to the repair loop.

Run once after the oracle passes, to measure generalization. The same uncaught-OverflowError class
exists in the SIBLING call site: naturaltime -> _date_and_delta (round(inf) raises OverflowError; the
except catches only ValueError/TypeError, time.py ~line 89-93). Same documented pass-through contract.
A fix hardcoded to naturaldelta's call site FAILS here (scores 3/5); a fix addressing the CLASS passes.
"""
from __future__ import annotations

import datetime as dt
import math

import humanize


def test_heldout_naturaltime_positive_infinity_passes_through():
    assert humanize.naturaltime(math.inf) == "inf"


def test_heldout_naturaltime_negative_infinity_passes_through():
    assert humanize.naturaltime(-math.inf) == "-inf"


def test_heldout_naturaltime_nan_passthrough_unchanged():
    assert humanize.naturaltime(math.nan) == "nan"


def test_heldout_naturaltime_normal_seconds_still_humanized():
    assert humanize.naturaltime(30) == "30 seconds ago"


def test_heldout_naturaldelta_normal_hours_still_humanized():
    assert humanize.naturaldelta(dt.timedelta(hours=3)) == "3 hours"
