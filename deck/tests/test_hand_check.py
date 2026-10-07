"""tools/hand_check.py: one anatomy line per hand5 call, pinned to the Hearts courts."""
import os
import sys

import numpy as np
import pytest

from deck import courtkit as K

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "tools"))
import hand_check as HC  # noqa: E402

# (court, [(pose, anatomical hand, view, viewer side)]) in call order.
EXPECTED = {
    "KH": [("wrap", "L", "back", "R"), ("wrap", "R", "back", "L")],       # pole, chalice
    "QH": [("wrap", "L", "back", "R"), ("rest", "R", "back", "L")],       # stem, rest
    "JH": [("wrap", "L", "back", "R"), ("wrap", "R", "back", "L")],       # fiddle, bow
}
_cache = {}


def _run(court):
    """(rows, printed lines) for a court, built once per test session."""
    if court not in _cache:
        printed = []
        _cache[court] = (HC.check_module(court, out=printed.append), printed)
    return _cache[court]


def _rows(court):
    return _run(court)[0]


@pytest.mark.parametrize("court", sorted(EXPECTED))
def test_court_hands_match_their_current_calls(court):
    rows = _rows(court)
    got = [(m["pose"], m["hand"], m["view"], m["viewer_side"]) for m in rows]
    assert got == EXPECTED[court]


@pytest.mark.parametrize("court", sorted(EXPECTED))
def test_hearts_hands_pass_every_rule_and_report_measurements(court):
    for m in _rows(court):
        assert m["flags"] == [], m["flags"]
        assert m["seam_dist"] is not None and m["seam_dist"] > 0 and m["seam_side"] == "art side"
        lo, hi = m["range"]
        assert HC._in_range(m["shown"], lo, hi)


@pytest.mark.parametrize("court", sorted(EXPECTED))
def test_one_line_per_hand_with_all_fields(court):
    out = _run(court)[1]
    assert len(out) == len(EXPECTED[court])
    for ln, (pose, hand, view, side) in zip(out, EXPECTED[court]):
        for part in (f" {pose} {hand}/{view} ", f"viewer {side}", "thumb (", "index (", "fingers ",
                     "forearm ", "seam ", "A2 ", "| OK"):
            assert part in ln, (part, ln)


def test_kh_wrist_and_digit_numbers():
    pole, chalice = _rows("KH")
    assert pole["forearm"] == pytest.approx(2.2, abs=0.05) and pole["finger"] == pytest.approx(158.0, abs=0.5)
    assert chalice["forearm"] == pytest.approx(155.8, abs=0.05) and chalice["finger"] == pytest.approx(0.0, abs=0.5)


# --- the rules themselves, on synthetic calls (fast) -------------------------
def _measure(at, angle, pose, *, akimbo=False, seam=None, **kw):
    with HC.collect_hand5() as recs:
        K.hand5(at, angle, pose, size=80.0, grip_w=kw.pop("grip_w", 18.0), **kw)
    return HC.measure(recs[0], seam, akimbo=akimbo)


def test_forearm_rows_follow_the_a2_table():
    assert HC.forearm_row("L", (450, 420)) == ("normal", -10.0, 90.0)
    assert HC.forearm_row("R", (300, 420)) == ("normal", 90.0, 190.0)
    assert HC.forearm_row("R", (200, 420)) == ("outboard", 70.0, 190.0)
    assert HC.forearm_row("L", (560, 420)) == ("outboard", -10.0, 110.0)
    assert HC.forearm_row("L", (500, 250)) == ("raised", 10.0, 90.0)
    assert HC.forearm_row("R", (300, 250)) == ("raised", 90.0, 170.0)
    assert HC.forearm_row("R", (300, 420), akimbo=True) == ("akimbo", 180.0, 240.0)


def test_range_check_wraps_around_180():
    assert HC._in_range(-170.0, 90.0, 190.0)       # -170 == 190
    assert not HC._in_range(-24.0, 90.0, 190.0)
    assert HC._in_range(-30.0, -60.0, 0.0)


def test_out_of_range_forearm_is_flagged():
    # The pre-fix KH chalice: R hand at the viewer's left with the forearm at -24 (up toward the axis).
    bad = _measure((233.5, 392.0), 90.2, "wrap", hand="R", view="back")
    assert bad["forearm"] == pytest.approx(-24.0, abs=0.1)
    assert any(f.startswith("A2") for f in bad["flags"])
    good = _measure((233.5, 392.0), -90.0, "wrap", hand="R", view="back")
    assert not any(f.startswith("A2") for f in good["flags"])


def test_wrong_side_palm_view_and_outward_fingers_are_flagged():
    wrong_side = _measure((233.5, 392.0), -90.0, "wrap", hand="L", view="back")
    assert any(f.startswith("A1") for f in wrong_side["flags"])
    palm = _measure((520.0, 420.0), -90.0, "wrap", hand="L", view="palm")
    assert any(f.startswith("A4") for f in palm["flags"])
    # L hand at the viewer's right with fingers pointing right, out to the card edge.
    out = _measure((520.0, 420.0), 90.0, "wrap", hand="L", view="back")
    assert any(f.startswith("A3") for f in out["flags"])


def test_a7_flags_mismatched_sizes():
    a = _measure((520.0, 420.0), -90.0, "wrap", hand="L", view="back")
    with HC.collect_hand5() as recs:
        K.hand5((233.5, 392.0), -90.0, "wrap", size=60.0, grip_w=18.0, hand="R", view="back")
    b = HC.measure(recs[0], None)
    HC.a7_flags([a, b])
    assert any(f.startswith("A7") for f in a["flags"]) and any(f.startswith("A7") for f in b["flags"])


def test_hook_leaves_hand5_untouched_and_restores_it():
    original = K.hand5
    plain = original((300.0, 400.0), -90.0, "wrap", size=80.0, grip_w=18.0, hand="R", view="back")
    with HC.collect_hand5() as recs:
        assert K.hand5 is not original
        hooked = K.hand5((300.0, 400.0), -90.0, "wrap", size=80.0, grip_w=18.0, hand="R", view="back")
    assert K.hand5 is original
    assert len(recs) == 1 and recs[0].site.startswith("deck/tests/test_hand_check.py:")
    assert hooked.shape.equals(plain.shape)
    assert np.allclose(hooked.wrist_dir, plain.wrist_dir)
    assert [t for t in hooked.hand.meta["digit_tips"]] == [t for t in plain.hand.meta["digit_tips"]]
