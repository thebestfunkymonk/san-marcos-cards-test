"""Regression checks for QH's approved seam and two short cuff openings."""
from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString

from art import QH
from deck import courtkit as K
from deck import frames as F


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[], sleeves=[], cuffs=[], garments=[])

    def record(owner, name, destination):
        original = getattr(owner, name)

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            destination.append((args, kwargs, result))
            return result

        patch.setattr(owner, name, wrapped)

    def forbidden(*args, **kwargs):
        pytest.fail("QH must use hand5 and local cuffs, not routed arms")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        record(K, "hand5", observed.hands)
        record(K.Hand, "with_sleeve", observed.sleeves)
        record(QH, "fold_cuff", observed.cuffs)
        record(QH.QC, "garments", observed.garments)
        observed.scene = QH.figure()
    return observed


def test_approved_seam_and_four_integrated_items(composition):
    assert QH.DOUBLE_HEAD == "continuous"
    assert QH.SEAM == -42
    assert composition.scene.rank is None
    assert [item.name for item in composition.scene.items] == [
        "bubbles", "robes", "sagittaria+hand+cuff", "portrait",
    ]
    assert all(item.halo == 0 for item in composition.scene.items)


def test_two_face_scaled_hands_restore_bodice_gesture(composition):
    face = QH.QF.queen_face(QH.HEAD, wing_mode="hook",
                           wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
    assert len(composition.hands) == 2
    args, kwargs, _ = composition.hands[0]
    assert args == ((546, 434), 90, "wrap")
    assert kwargs == dict(size=K.hand_size(face), hand="L",
                         view="palm", grip_w=19)
    args, kwargs, _ = composition.hands[1]
    assert args == ((322, 424), -24, "rest")
    assert kwargs == dict(size=K.hand_size(face) * 0.82, hand="R",
                         view="back", curl=6, spread=3)
    seam = LineString(F.seam_points(QH.SEAM))
    for _, _, hand in composition.hands:
        assert hand.hand.shape.distance(seam) >= 12


def test_local_patterned_cuffs_hide_forearms(composition):
    assert len(composition.cuffs) == len(composition.sleeves) == 2
    for (_, _, cuff), ((hand, sleeve), kwargs, joined) in zip(
            composition.cuffs, composition.sleeves):
        assert kwargs == {"cuff_line": True}
        assert cuff.shape.equals(joined.shape)
        assert cuff.meta["cuff_depth"] == 24
        assert cuff.meta["cuff_width"] == pytest.approx(hand.wrist_w + 10)
        wrist = K.P(hand.wrist)
        local = np.asarray(sleeve.shape.exterior.coords) - wrist
        depth = local @ hand.wrist_dir
        assert depth.min() == pytest.approx(-2, abs=0.01)
        assert depth.max() == pytest.approx(24, abs=0.01)
        assert any(mark.role.startswith("pearl") for mark in sleeve.lines.marks)
        assert any(mark.role == "cuffline" for mark in cuff.lines.marks)


def test_whole_gown_and_dense_textiles_are_c2(composition):
    _, _, gown = composition.garments[0]
    assert gown.shape.symmetric_difference(K.rot180(gown.shape)).area < 0.1
    assert gown.shape.contains(LineString([(375, 500), (375, 550)]))
    for role in ("wave", "hatch"):
        assert any(mark.role == role for mark in gown.lines.marks)
    red = gown.fills.select(lambda mark: mark.layer == "red").shape()
    assert red.area < gown.meta["bodice"].area * 0.85  # Scales are knockouts.
    for layer in ("jade", "red"):
        plate = gown.fills.select(lambda mark: mark.layer == layer).shape()
        assert plate.hausdorff_distance(K.rot180(plate)) < 0.1


def test_art_is_deterministic():
    assert QH.build() == QH.build()
