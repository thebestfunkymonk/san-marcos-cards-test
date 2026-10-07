"""Regression checks for the continuous Jack of Diamonds composition."""
from types import SimpleNamespace

import pytest

from art import JD
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous JD must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = JD.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert JD.DOUBLE_HEAD == "continuous"
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 19  # The original stacked scene had 29.
    names = [item.name for item in scene.items]
    assert "trumpet+hand+sleeve" in names and "map+hand+sleeve" in names
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_wrap_hands(composition):
    assert len(composition.hands) == 2
    expected = [(JD.GRIP_A, JD.AXIS, "wrap", "L"), (JD.GRIP_B, -90.0, "wrap", "R")]
    for (args, kwargs, _), (at, angle, grip, letter) in zip(composition.hands, expected):
        assert args == (at, angle, grip)
        assert kwargs["hand"] == letter and kwargs["view"] == "back"


def test_sleeves_are_short():
    assert JD.A_RUN <= 90.0 and JD.B_RUN <= 90.0


def test_garment_regions_are_their_own_half_turn_copy():
    from art import _jd_garments as KG
    for region in (KG.barrel(), KG.tabard_shape()):
        assert region.symmetric_difference(KG.rot(region)).area < 5.0
