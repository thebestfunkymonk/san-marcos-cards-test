"""Regression checks for the continuous Spring Minstrel composition."""
import numpy as np
from shapely.geometry import LineString

from art import JH
from deck import courtkit as K
from deck import frames as F


def test_two_anatomical_hands_one_size_and_four_integrated_items(monkeypatch):
    # Checkpoint 3: the minstrel's left hand (viewer's right) holds the fiddle neck back-view, thumb
    # up the neck, fingers toward the tunic, forearm down and out; his right hand (viewer's left)
    # holds the bow back-view, thumb up, fingers toward the tunic, forearm down and out.
    calls = []
    original = K.hand5

    def record(*args, **kwargs):
        res = original(*args, **kwargs)
        calls.append((args, kwargs, res))
        return res

    monkeypatch.setattr(K, "hand5", record)
    scene = JH.figure()
    assert scene.rank is None
    assert len(scene.items) == 4
    assert [item.name for item in scene.items] == [
        "robes", "bow+hand+cuff", "fiddle+hand+cuff", "portrait"]
    assert all(item.halo == 0 for item in scene.items)
    assert len(calls) == 2
    size = K.hand_size(JH.JF.minstrel_profile(JH.HEAD)) * JH.HAND_S
    assert JH.HAND_S == 0.82
    (fa, fk, fid), (ba, bk, bow) = calls
    assert fa == (JH.FIST_R, -90, "wrap") and ba == (JH.FIST_L, -90, "wrap")
    assert JH.FID_HAND == ("L", "back") and JH.BOW_HAND == ("R", "back")
    assert fk["hand"] == "L" and fk["view"] == "back" and bk["hand"] == "R" and bk["view"] == "back"
    assert fk["size"] == bk["size"] == size
    assert "cues" not in fk and "cues" not in bk
    seam = LineString(F.seam_points(JH.SEAM))
    for hand in (fid, bow):
        assert hand.hand.shape.distance(seam) >= 12
    angle = lambda h: float(np.degrees(np.arctan2(h.wrist_dir[1], h.wrist_dir[0])))
    # forearms leave outward and down (A2): fiddle hand -10..90, bow hand 90..190
    assert -10.0 <= angle(fid) <= 90.0 and 90.0 <= angle(bow) <= 190.0
    for hand, axis_x, outer in ((fid, JH.FIST_R[0], 1), (bow, JH.FIST_L[0], -1)):
        tips = hand.hand.meta["digit_tips"]
        thumb = np.asarray(hand.hand.meta["thumb_centerline"].coords[-1])
        # wrist on the outer side of the shaft, fingertips across it toward the axis,
        # thumb above the index fingertip at the shaft's upper end
        assert outer * (hand.wrist[0] - axis_x) > 20.0
        assert outer * (np.asarray(tips[1])[0] - axis_x) < 0
        assert thumb[1] < np.asarray(tips[0])[1] - 5.0


def test_cuffs_are_sleeve_ends_of_the_cloak(monkeypatch):
    calls = {"sleeve": [], "cuff": []}
    for name, key in (("sleeve_end", "sleeve"), ("sleeved_hand", "cuff")):
        original = getattr(JH, name)
        monkeypatch.setattr(
            JH, name, lambda *a, _o=original, _k=key, **kw: calls[_k].append((a, kw, _o(*a, **kw)))
            or calls[_k][-1][2])
    scene = JH.figure()
    robes = next(item for item in scene.items if item.name == "robes")
    assert len(calls["sleeve"]) == len(calls["cuff"]) == 2
    jade = robes.frag.select(lambda m: m.kind == "fill" and m.color == K.JADE).shape()
    # both sleeves belong to the jade cloak and run out to its outer edge
    for (args, kw, sleeve), (cargs, _, cuff), run in zip(
            calls["sleeve"], calls["cuff"], (JH.FID_RUN, JH.BOW_RUN)):
        hand = args[0]
        assert kw["run"] == run <= 90.0
        assert cargs[1] is sleeve
        assert sleeve.difference(jade.buffer(0.5)).area < 0.05 * sleeve.area
        assert not cuff.fills.marks
        assert cuff.shape.intersection(sleeve).area < 0.01
        assert cuff.shape.symmetric_difference(hand.shape.difference(sleeve)).area < 30
        # the mouth is convex toward the hand
        w, u = K.P(hand.wrist), hand.wrist_dir
        n = K.P(u[1], -u[0])
        coords = np.asarray(sleeve.exterior.coords) - w
        mouth = coords[abs(coords @ u) < 6]
        edge = mouth[abs(mouth @ n) > hand.wrist_w / 2]
        centre = mouth[abs(mouth @ n) < 3]
        assert (centre @ u).min() < (edge @ u).min() - 1.0
    assert any(m.role == "cuffline" for m in robes.frag.marks)


def test_continuous_robes_and_separate_parallel_attributes():
    assert JH.DOUBLE_HEAD == "continuous"
    assert JH.SEAM == -24
    scene = JH.figure()
    robes, bow, fiddle, _ = scene.items
    assert robes.occ.symmetric_difference(K.rot180(robes.occ)).area < 0.1
    assert not bow.occ.intersects(fiddle.occ)
    assert bow.occ.bounds[3] <= 450.001
    assert bow.occ.bounds[2] < JH.FX - 100
    assert robes.occ.intersects(bow.occ)
    assert robes.occ.intersects(fiddle.occ)


def test_one_eyed_profile_retains_face_stroke_budget():
    face = JH.JF.minstrel_profile(JH.HEAD, pupil_tuck=0.4)
    assert face.anchors["facing"] == -1
    assert face.strokes <= 14
    assert sum(m.role == "pupil" for m in face.lines.marks) == 1


def test_art_is_deterministic():
    assert JH.build() == JH.build()
