"""Regression checks for the continuous King of Spades composition."""
from types import SimpleNamespace

import pytest

from art import KS
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous KS must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = KS.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert KS.DOUBLE_HEAD == "continuous"
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 12  # The original separate-plate scene had 16.
    assert [item.name for item in scene.items][:5] == [
        "collar", "robes", "sceptre+hand+sleeve", "orb+hand+sleeve", "bubble"]
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_wrap_hands(composition):
    assert len(composition.hands) == 2
    face = K.face(KS.HEAD, "frontal", age="elder", lids="heavy")
    expected = [(KS.GRIP, -90.0, "L"), (KS.ORB_GRIP, -90.0, "R")]
    for (args, kwargs, _), (at, angle, letter) in zip(composition.hands, expected):
        assert args == (at, angle, "wrap")
        assert kwargs["hand"] == letter and kwargs["view"] == "back"
        assert kwargs["size"] == pytest.approx(K.hand_size(face) * KS.HAND_SCALE)


def test_sleeves_are_short_and_end_at_the_mantle_edge(composition):
    assert KS.SC_RUN <= 90.0 and KS.ORB_RUN <= 90.0
    robes = composition.scene.items[1]
    assert robes.name == "robes"
