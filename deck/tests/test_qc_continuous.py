"""Regression checks for the continuous Queen of Clubs composition."""
from types import SimpleNamespace

import pytest

from art import QC
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[])

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous QC must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        original = K.hand5

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            observed.hands.append((args, kwargs, result))
            return result

        patch.setattr(K, "hand5", wrapped)
        observed.scene = QC.figure()
    return observed


def test_continuous_scene_is_integrated(composition):
    assert QC.DOUBLE_HEAD == "continuous"
    scene, _ = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 25  # The band-mode scene stacked 31.
    names = [item.name for item in scene.items]
    assert names[0] == "cloak" and names[-2:] == ["sceptre", "hand-sceptre"]
    assert all(item.halo == 0 for item in scene.items)


def test_two_back_view_wrap_hands(composition):
    assert len(composition.hands) == 2
    _, face = composition.scene
    expected = [(QC.GRIP_S, -90.0, "L"), (QC.GRIP_F, QC.FAN_AXIS, "R")]
    for (args, kwargs, _), (at, angle, letter) in zip(composition.hands, expected):
        assert args == (at, angle, "wrap")
        assert kwargs["hand"] == letter and kwargs["view"] == "back"
        assert kwargs["size"] == pytest.approx(K.hand_size(face) * QC.HAND_SCALE)


def test_sleeves_are_short(composition):
    scene, _ = composition.scene
    sleeves = {item.name: item.occ for item in scene.items if item.name.startswith("sleeve")}
    assert set(sleeves) == {"sleeve-sceptre", "sleeve-fan"}
    for (_, _, hand), name in zip(composition.hands, ("sleeve-sceptre", "sleeve-fan")):
        u = hand.wrist_dir
        wrist = K.P(hand.wrist)
        pts = sleeves[name].exterior.coords if sleeves[name].geom_type == "Polygon" else [
            c for g in sleeves[name].geoms for c in g.exterior.coords]
        reach = max((K.P(*c) - wrist) @ u for c in pts)
        assert reach <= 95.0
