"""Regression checks for the continuous King of Clubs composition."""
from types import SimpleNamespace

import pytest

from art import KC
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous KC must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = KC.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert KC.DOUBLE_HEAD == "continuous"
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 12  # The separate-plate scene had 20.
    assert [item.name for item in scene.items][:5] == [
        "robes", "collar", "staff+hand+sleeve", "finial", "orb+hand+sleeve"]
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_wrap_hands(composition):
    assert len(composition.hands) == 2
    face = K.face(KC.HEAD, "frontal", age="elder", **KC.FACE)
    expected = [(KC.GRIP, -90.0, "L"), (KC.ORB_GRIP, -90.0, "R")]
    for (args, kwargs, _), (at, angle, letter) in zip(composition.hands, expected):
        assert args == (at, angle, "wrap")
        assert kwargs["hand"] == letter and kwargs["view"] == "back"
        assert kwargs["size"] == pytest.approx(K.hand_size(face) * KC.HAND_SCALE)


def test_sleeves_are_short(composition):
    assert KC.STAFF_RUN <= 90.0 and KC.ORB_RUN <= 90.0
