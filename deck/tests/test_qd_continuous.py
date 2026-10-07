"""Regression checks for the continuous Queen of Diamonds composition."""
from types import SimpleNamespace

import pytest

from art import QD
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous QD must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = QD.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert QD.DOUBLE_HEAD == "continuous"
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 17  # The original stacked scene had 32.
    names = [item.name for item in scene.items]
    assert "staff+hand+sleeve" in names and "paintbrush+hand+sleeve" in names
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_wrap_hands(composition):
    assert len(composition.hands) == 2
    expected = [(QD.GRIP_S, -90.0, "wrap", "L"), (QD.GRIP_B, QD.PB_AXIS, "wrap", "R")]
    for (args, kwargs, _), (at, angle, grip, letter) in zip(composition.hands, expected):
        assert args == (at, angle, grip)
        assert kwargs["hand"] == letter and kwargs["view"] == "back"


def test_sleeves_are_short(composition):
    assert QD.SLEEVE_S["run"] <= 90.0 and QD.SLEEVE_B["run"] <= 90.0


def test_garment_regions_are_their_own_half_turn_copy():
    from art import _qd_garments as QG
    for region in (QG.cape_shape(), QG.opening(), QG.gown_shape()):
        assert region.symmetric_difference(QG.rot(region)).area < 5.0
