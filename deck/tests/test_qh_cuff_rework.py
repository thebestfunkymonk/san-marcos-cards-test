"""Regression checks for QH's approved seam and two bell sleeves that are lobes of the mantle."""
from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString

from art import QH
from deck import courtkit as K
from deck import frames as F


@pytest.fixture(scope="module")
def composition():
    observed = SimpleNamespace(hands=[], with_sleeve=[], sleeves=[], cuffs=[], trims=[], garments=[])

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
        record(K.Hand, "with_sleeve", observed.with_sleeve)
        record(QH, "sleeve_end", observed.sleeves)
        record(QH, "sleeved_hand", observed.cuffs)
        record(QH, "cuff_trim", observed.trims)
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
    # Compensated for the wrap chirality fix: opposite letter, same angle, legacy lines.
    assert args == ((546, 434), 90, "wrap")
    assert kwargs == dict(size=K.hand_size(face), hand="R",
                         view="palm", grip_w=19, cues=False)
    args, kwargs, _ = composition.hands[1]
    # Moved 12 px right (from (322,424)) so the sleeve has room between the
    # mantle edge and the hand; still 50+ px clear of the seam.
    assert args == (QH.REST_AT, -24, "rest")
    assert QH.REST_AT == (334, 424)
    assert kwargs == dict(size=K.hand_size(face) * 0.82, hand="R",
                         view="back", curl=6, spread=3, cues=False)
    seam = LineString(F.seam_points(QH.SEAM))
    for _, _, hand in composition.hands:
        assert hand.hand.shape.distance(seam) >= 12


def test_cuffs_are_short_mantle_sleeves_not_stubs(composition):
    assert not composition.with_sleeve, "a closed with_sleeve cuff is the rejected stub"
    assert len(composition.sleeves) == len(composition.cuffs) == len(composition.trims) == 2
    _, _, gown = composition.garments[0]
    jade = gown.fills.select(lambda mark: mark.layer == "jade").shape()
    for i, ((_, kwargs, sleeve), ((hand, region_sleeve), _, cuff), (_, _, trim)) in enumerate(zip(
            composition.sleeves, composition.cuffs, composition.trims)):
        assert region_sleeve is sleeve
        assert kwargs["run"] <= 54.0 <= 90.0
        # Convex mouth toward the hand: a concave one reads as a hand pushed in.
        assert kwargs["curl"] < 0
        # The sleeve is the mantle's own region: jade fill covers it, and the
        # hand region begins exactly where the sleeve's mouth ends.
        if i == 0:
            # The stem hand's sleeve lies on the mantle and enters through its
            # edge: only its tip beyond that edge is not jade.
            assert sleeve.intersection(jade).area > 0.6 * sleeve.area
        else:
            assert sleeve.difference(jade).area < 1.0
        assert cuff.shape.intersection(sleeve).area < 1.0
        assert cuff.fills.marks == []
        assert any(mark.role == "cuffline" for mark in trim.lines.marks)
        assert trim.fills.shape().area > 0
    assert any(mark.role == "cuffline" for mark in gown.lines.marks)


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
