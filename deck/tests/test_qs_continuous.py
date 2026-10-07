"""Regression checks for the continuous Queen of Spades composition."""
from types import SimpleNamespace

import pytest

from art import QS
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous QS must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = QS.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert QS.DOUBLE_HEAD == "continuous"
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 11  # The original separate-plate scene had 36.
    assert [item.name for item in scene.items][:2] == ["ruff", "robes"]
    assert [item.name for item in scene.items][-2:] == ["mirror+hand+sleeve", "posy+hand+sleeve"]
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_wrap_hands(composition):
    assert len(composition.hands) == 2
    expected = [(QS.MIRROR_GRIP, -90.0, "L"), (QS.POSY_GRIP, -90.0, "R")]
    for (args, kwargs, _), (at, angle, letter) in zip(composition.hands, expected):
        assert args == (at, angle, "wrap")
        assert kwargs["hand"] == letter and kwargs["view"] == "back"


def test_sleeves_are_short(composition):
    assert QS.MIRROR_RUN <= 90.0 and QS.POSY_RUN <= 90.0
    assert composition.scene.items[1].name == "robes"
