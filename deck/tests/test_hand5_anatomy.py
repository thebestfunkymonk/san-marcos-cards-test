"""Anatomy of ``hand5``: the named hand seen from the named side, every pose.

The checks use the hand's own frame (wrist -> fingertips) and the signed side
the thumb and index fall on. A mirrored hand fails every one of them.
"""
import math

import numpy as np
import pytest
from shapely import affinity
from shapely.ops import unary_union

from deck import courtkit as K
from deck import tokens as T

POSES = ("wrap", "cup", "rest", "hold_flat", "open")
AT = (312.0, 427.0)
ANGLES = (-180.0, -135.0, -90.0, -45.0, 0.0, 45.0, 90.0, 135.0)

# Thumb on the viewer's left of an upright hand = right hand seen from the back
# or left hand seen from the palm. Sign of cross(finger_dir, thumb offset) in
# screen coordinates (y down): left of an upward finger direction is negative.
THUMB_SIGN = {("R", "back"): -1.0, ("L", "back"): +1.0, ("R", "palm"): +1.0, ("L", "palm"): -1.0}


def _hand(pose, hand, view, angle=-90.0, size=85.0, **kw):
    kw.setdefault("grip_w", 0.72 * size if pose == "cup" else 22.0)
    return K.hand5(AT, angle, pose, size=size, hand=hand, view=view, **kw)


def _frame(result):
    """(finger direction, wrist -> fingertips) from the tips, not from meta."""
    meta = result.hand.meta
    tips = np.asarray(meta["digit_tips"], float)
    centre = tips[:4].mean(axis=0)
    wrist = np.asarray(result.wrist, float)
    f = centre - wrist
    return f / np.hypot(*f), centre, tips


def _lateral(f, p, centre):
    d = np.asarray(p, float) - centre
    return float(f[0] * d[1] - f[1] * d[0])


def test_thumb_and_index_sit_on_the_anatomical_side_for_every_pose_hand_view_and_angle():
    for pose in POSES:
        for hand in ("L", "R"):
            for view in ("back", "palm"):
                for angle in ANGLES:
                    res = _hand(pose, hand, view, angle)
                    f, centre, tips = _frame(res)
                    sign = THUMB_SIGN[(hand, view)]
                    ctx = (pose, hand, view, angle)
                    assert sign * _lateral(f, tips[4], centre) > 2.0, ctx      # thumb
                    assert sign * _lateral(f, tips[0], centre) > 2.0, ctx      # index beside the thumb
                    assert sign * _lateral(f, tips[3], centre) < -2.0, ctx     # little finger opposite


def test_mirror_images_swap_hand_and_view_together():
    # L/back is the mirror of R/back; L/palm the mirror of R/palm; a left hand seen from the
    # palm has the same silhouette handedness as a right hand seen from the back.
    for pose in POSES:
        for angle in (-90.0, 0.0, 50.0):
            a = _hand(pose, "R", "back", angle)
            b = _hand(pose, "L", "palm", angle)
            fa, ca, ta = _frame(a)
            fb, cb, tb = _frame(b)
            assert _lateral(fa, ta[4], ca) * _lateral(fb, tb[4], cb) > 0, (pose, angle)
            c = _hand(pose, "L", "back", angle)
            fc, cc, tc = _frame(c)
            assert _lateral(fa, ta[4], ca) * _lateral(fc, tc[4], cc) < 0, (pose, angle)


def test_wrap_vertical_shaft_matches_the_documented_geometry():
    at = np.asarray(AT)
    r = _hand("wrap", "R", "back", -90.0)
    assert r.wrist[0] < at[0]
    assert r.hand.meta["digit_tips"][4][1] < at[1]      # thumb at the top
    assert r.hand.meta["digit_tips"][0][0] > at[0]      # fingers point right
    l = _hand("wrap", "L", "back", -90.0)
    assert l.wrist[0] > at[0]
    assert l.hand.meta["digit_tips"][4][1] < at[1]
    assert l.hand.meta["digit_tips"][0][0] < at[0]      # fingers point left


def _dir_deg(v):
    return math.degrees(math.atan2(v[1], v[0]))


def _ang_diff(a, b):
    return abs((a - b + 180.0) % 360.0 - 180.0)


def test_angle_means_what_the_docs_say_for_each_pose():
    for angle in (-90.0, -30.0, 40.0, 160.0):
        for view in ("back", "palm"):
            for hand in ("L", "R"):
                for pose in ("cup", "rest", "hold_flat", "open"):
                    res = _hand(pose, hand, view, angle)
                    f, _, _ = _frame(res)
                    assert _ang_diff(_dir_deg(f), angle) < 25.0, (pose, hand, view, angle)
                    # forearm runs straight back from the fingers
                    assert _ang_diff(_dir_deg(res.wrist_dir), angle + 180.0) < 1.0
                res = _hand("wrap", hand, view, angle)
                f, _, _ = _frame(res)
                left = (hand == "L") == (view == "back")
                want = angle - 90.0 if left else angle + 90.0
                assert _ang_diff(_dir_deg(f), want) < 20.0, (hand, view, angle)
                # forearm leaves the shaft-perpendicular, tilted toward the little finger
                off = 114.2 if left else -114.2
                assert _ang_diff(_dir_deg(res.wrist_dir), angle + off) < 3.0, (hand, view, angle)


def test_wrap_thumb_is_toward_angle_for_every_hand_and_view():
    for angle in ANGLES:
        for hand in ("L", "R"):
            for view in ("back", "palm"):
                res = _hand("wrap", hand, view, angle)
                at = np.asarray(AT)
                thumb = np.asarray(res.hand.meta["digit_tips"][4]) - at
                axis = np.array([math.cos(math.radians(angle)), math.sin(math.radians(angle))])
                assert float(thumb @ axis) > 10.0, (hand, view, angle)


def test_rebuild_keeps_the_chirality_when_the_sleeve_direction_changes():
    for hand, view in (("R", "back"), ("L", "back"), ("R", "palm"), ("L", "palm")):
        res = _hand("wrap", hand, view, -90.0)
        again = res.hand.meta["rebuild"](np.array([0.0, 1.0]))
        tips = np.asarray(again.meta["digit_tips"], float)
        centre = tips[:4].mean(axis=0)
        f = centre - np.asarray(res.wrist, float)
        f /= np.hypot(*f)
        assert THUMB_SIGN[(hand, view)] * _lateral(f, tips[4], centre) > 2.0
        assert np.allclose(np.asarray(again.meta["wrist_dir"]), [0.0, 1.0], atol=1e-6)


# ---------------------------------------------------------------------------
# back vs palm must read differently at card scale
# ---------------------------------------------------------------------------
def _line_axis_angles(res):
    meta = res.hand.meta
    f, _, _ = _frame(res)
    out = []
    for ln in meta["inner_lines"]:
        a, b = np.asarray(ln.coords[0]), np.asarray(ln.coords[-1])
        v = (b - a) / np.hypot(*(b - a))
        out.append(math.degrees(math.acos(min(1.0, abs(float(v @ f))))))
    return out


@pytest.mark.parametrize("pose", POSES)
def test_back_and_palm_use_different_interior_cues(pose):
    for hand in ("L", "R"):
        for angle in (-90.0, -30.0, 20.0):
            back = _hand(pose, hand, "back", angle)
            palm = _hand(pose, hand, "palm", angle)
            for res in (back, palm):
                lines = res.hand.meta["inner_lines"]
                assert 1 <= len(lines) <= 3, (pose, hand, angle)
                assert all(m.w == T.MEDIUM for m in res.hand.meta["inner"].marks)
            ba, pa = _line_axis_angles(back), _line_axis_angles(palm)
            # back: knuckle/tendon lines run with the fingers
            assert max(ba) <= 40.0, (pose, hand, angle, ba)
            # palm: a crease runs across the palm
            assert max(pa) >= 45.0, (pose, hand, angle, pa)


@pytest.mark.parametrize("pose", POSES)
def test_view_cue_fingerprint_is_unmistakable_in_the_ink(pose):
    """The back's ink must not be a subset of the palm's, mapped into one frame."""
    for hand in ("L", "R"):
        back = _hand(pose, hand, "back", -90.0)
        palm = _hand(pose, hand, "palm", -90.0)
        mb = unary_union(back.hand.meta["inner_lines"])
        mp = unary_union(palm.hand.meta["inner_lines"])
        # compare in the *named hand's* frame: mirror the palm's silhouette side so both
        # views of one hand describe the same wrist/finger axes
        fb, cb, _ = _frame(back)
        fp, cp, _ = _frame(palm)
        # build an orthonormal frame per view (origin = fingertip centre, x = finger_dir)
        def to_local(g, f, c):
            return affinity.affine_transform(
                affinity.translate(g, -c[0], -c[1]), [f[0], f[1], -f[1], f[0], 0, 0])
        gb = to_local(mb, fb, cb).buffer(T.MEDIUM / 2)
        gp = to_local(mp, fp, cp).buffer(T.MEDIUM / 2)
        sym = gb.symmetric_difference(gp).area
        assert sym >= 0.45 * max(gb.union(gp).area, 1e-9), (pose, hand)


def test_cues_false_keeps_the_legacy_line_set():
    # The pre-anatomy courts pass cues=False and must keep their approved art.
    for hand, view in (("R", "back"), ("L", "palm")):
        res = _hand("wrap", hand, view, -90.0, cues=False)
        assert res.hand.meta["cues"] is False
        assert len(res.hand.meta["inner_lines"]) == 3


def test_specimen_matrix_covers_every_pose_hand_and_view_with_labels():
    import importlib.util
    import pathlib
    path = pathlib.Path(__file__).resolve().parents[2] / "tools" / "hand_specimen.py"
    spec = importlib.util.spec_from_file_location("hand_specimen_matrix", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    cells = {(c["args"][2], c["kw"]["hand"], c["kw"]["view"]): c["label"]
             for _, calls in mod.matrix_rows() for c in calls}
    assert set(cells) == {(p, h, v) for p in POSES for h in ("L", "R") for v in ("back", "palm")}
    assert all(h in lab and v in lab and p in lab for (p, h, v), lab in cells.items())
