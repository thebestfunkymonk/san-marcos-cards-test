"""Regression checks for the continuous Spring Minstrel composition."""
import numpy as np

from art import JH
from deck import courtkit as K


def test_two_face_scaled_hands_and_four_integrated_items(monkeypatch):
    calls = []
    original = K.hand5

    def record(*args, **kwargs):
        calls.append((args, kwargs))
        return original(*args, **kwargs)

    monkeypatch.setattr(K, "hand5", record)
    scene = JH.figure()
    assert scene.rank is None
    assert len(scene.items) == 4
    assert [item.name for item in scene.items] == [
        "robes", "bow+hand+cuff", "fiddle+hand+cuff", "portrait"]
    assert all(item.halo == 0 for item in scene.items)
    assert len(calls) == 2
    for (args, kwargs), at, angle, view in zip(
            calls, [JH.FIST_R, JH.FIST_L], [-90, -90], ["palm", "back"]):
        assert args == (at, angle, "wrap")
        assert kwargs["size"] == K.hand_size(JH.JF.minstrel_profile(JH.HEAD)) * 0.82
        assert kwargs["view"] == view
        # Compensated for the wrap chirality fix: opposite letter (fiddle hand: angle + 180), legacy lines.
        assert kwargs["hand"] == "L"
        assert kwargs["cues"] is False


def test_cuffs_are_sleeve_ends_of_the_neighbouring_garments(monkeypatch):
    calls = {"sleeve": [], "cuff": []}
    for name, key in (("sleeve_end", "sleeve"), ("sleeved_hand", "cuff")):
        original = getattr(JH, name)
        monkeypatch.setattr(
            JH, name, lambda *a, _o=original, _k=key, **kw: calls[_k].append((a, kw, _o(*a, **kw)))
            or calls[_k][-1][2])
    scene = JH.figure()
    robes = next(item for item in scene.items if item.name == "robes")
    assert len(calls["sleeve"]) == len(calls["cuff"]) == 2
    fills = {K.JADE: robes.frag.select(lambda m: m.kind == "fill" and m.color == K.JADE).shape(),
             K.RED: robes.frag.select(lambda m: m.kind == "fill" and m.color == K.RED).shape()}
    # fiddle hand: jade mantle fold; bow hand: red tunic crossing the baldric
    for (args, kw, sleeve), (cargs, _, cuff), run, colour in zip(
            calls["sleeve"], calls["cuff"], (JH.FID_RUN, JH.BOW_RUN), (K.JADE, K.RED)):
        hand = args[0]
        assert kw["run"] == run <= 90.0
        assert cargs[1] is sleeve
        assert sleeve.difference(fills[colour].buffer(0.5)).area < 0.05 * sleeve.area
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
