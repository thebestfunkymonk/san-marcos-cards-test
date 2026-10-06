"""Regression checks for the continuous Spring Minstrel composition."""
from art import JH
from deck import courtkit as K


def test_one_face_scaled_hand_and_four_integrated_items(monkeypatch):
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
        "robes", "tucked-bow", "fiddle+hand+sleeve", "portrait"]
    assert all(item.halo == 0 for item in scene.items)
    assert len(calls) == 1
    args, kwargs = calls[0]
    assert args == ((530.0, 254.0), 90, "wrap")
    assert kwargs["size"] == K.hand_size(JH.JF.minstrel_profile(JH.HEAD))
    assert kwargs["view"] == "palm"


def test_continuous_robes_and_separate_parallel_attributes():
    assert JH.DOUBLE_HEAD == "continuous"
    assert JH.SEAM == -24
    scene = JH.figure()
    robes, bow, fiddle, _ = scene.items
    assert robes.occ.symmetric_difference(K.rot180(robes.occ)).area < 0.1
    assert not bow.occ.intersects(fiddle.occ)
    assert bow.occ.bounds[3] < 450
    assert bow.occ.bounds[2] < JH.FX - 100


def test_art_is_deterministic():
    assert JH.build() == JH.build()
