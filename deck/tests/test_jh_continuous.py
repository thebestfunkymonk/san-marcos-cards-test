"""Regression checks for the continuous Spring Minstrel composition."""
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
            calls, [JH.FIST_R, JH.FIST_L], [90, -90], ["palm", "back"]):
        assert args == (at, angle, "wrap")
        assert kwargs["size"] == K.hand_size(JH.JF.minstrel_profile(JH.HEAD)) * 0.82
        assert kwargs["view"] == view
        assert kwargs["hand"] == "R"


def test_short_patterned_cuffs_share_the_hand_outline():
    for at, angle, view in [(JH.FIST_R, 90, "palm"), (JH.FIST_L, -90, "back")]:
        hand = K.hand5(at, angle, "wrap", size=68, view=view)
        cuff = JH.fold_cuff(hand)
        assert cuff.meta["cuff_depth"] == 24
        assert cuff.meta["cuff_width"] >= hand.wrist_w + 8
        assert hand.hand.shape.difference(cuff.shape.buffer(0.05)).area < 0.1
        assert any(m.role == "hatch" for m in cuff.lines.marks)
        assert not any(m.color == K.PAPER for m in cuff.fills.marks)


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
