"""ORACLE — non-finite: naturaldelta must not crash on non-finite floats.

AUTHORITATIVE RULE (the library's own documented contract, src/humanize/time.py naturaldelta
docstring): the value is "returned unchanged" when it "cannot be converted to int (cannot be float
due to 'inf' or 'nan')". Observed pass-through returns str(value) (the nan path already does this).
OverflowError is documented ONLY for finite values too large to convert to datetime.timedelta.

Bug: `int(value)` raises OverflowError for inf/-inf, which the pass-through `except (ValueError,
TypeError)` does not catch (time.py ~line 151-155).

Oracle discipline: >=2 distinct inputs per rule; one test per comparison boundary; expected values
from the documented contract, not current output. HELD-OUT (sibling call site) is disjoint — not shown.
"""
from __future__ import annotations

import datetime as dt
import math

import pytest

import humanize


# RULE 1: non-finite float -> returned unchanged (as str), no crash (>=2 distinct inputs)
def test_rule1_input1_positive_infinity_passes_through():
    assert humanize.naturaldelta(math.inf) == "inf"


def test_rule1_input2_negative_infinity_passes_through():
    assert humanize.naturaldelta(-math.inf) == "-inf"


# RULE 2: normal values still humanize (no regression) (>=2 distinct inputs)
def test_rule2_input1_seconds_still_humanized():
    assert humanize.naturaldelta(61.0) == "a minute"


def test_rule2_input2_timedelta_still_humanized():
    assert humanize.naturaldelta(dt.timedelta(days=7)) == "7 days"


# BOUNDARY 1: nan — the already-working non-finite case must not regress
def test_boundary_nan_passthrough_unchanged():
    assert humanize.naturaldelta(math.nan) == "nan"


# BOUNDARY 2: huge FINITE value — OverflowError is DOCUMENTED behavior; must not be blanket-swallowed
def test_boundary_huge_finite_still_raises_documented_overflow():
    with pytest.raises(OverflowError):
        humanize.naturaldelta(1e300)
