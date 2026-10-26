"""Booked vs. pending friendlies for the 'no to everyone' hint."""

from fun_with_flags.flags import _has_booked


def _c(agreed, weekend):
    # same tuple layout as helperf.get_my_challenges()
    return ({"is_agreed": agreed}, None, 0, 0, weekend, True, True)


def test_agreed_midweek_counts_only_for_midweek():
    gmc = [_c("True", False)]
    assert _has_booked(gmc, "0")
    assert not _has_booked(gmc, "1")


def test_pending_challenges_dont_count():
    assert not _has_booked([_c("False", False)], "0")


def test_no_challenges():
    assert not _has_booked([], "0")
