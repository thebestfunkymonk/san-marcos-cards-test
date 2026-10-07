"""Regression checks for the continuous King of Diamonds composition."""
from types import SimpleNamespace

import pytest

from art import KD
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous KD must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = KD.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert KD.DOUBLE_HEAD == "continuous"
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 11  # The original stacked scene had 20.
    assert [item.name for item in scene.items][:4] == ["robes", "sash", "key+hand+sleeve", "hand"]
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_hands_with_the_right_grips(composition):
    assert len(composition.hands) == 2
    expected = [(KD.GRIP, -90.0, "wrap", "L"), (KD.REST_AT, KD.REST_ANGLE, "rest", "R")]
    for (args, kwargs, _), (at, angle, grip, letter) in zip(composition.hands, expected):
        assert args == (at, angle, grip)
        assert kwargs["hand"] == letter and kwargs["view"] == "back"


def test_sleeves_are_short(composition):
    assert KD.KEY_RUN <= 90.0 and KD.REST_RUN <= 90.0


def test_garment_regions_are_their_own_half_turn_copy():
    from art import _kd_garments as KG
    for region in (KG.barrel(), KG.sash_shape(), KG.lens()):
        assert region.symmetric_difference(KG.rot(region)).area < 5.0
