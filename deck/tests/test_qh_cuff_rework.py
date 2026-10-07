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


def test_two_anatomical_hands_one_size_restore_bodice_gesture(composition):
    # Checkpoint 3: the queen's left hand (viewer's right) grips the stem back-view, thumb up at
    # the shaft's working end, forearm running down and out into the outer mantle; her right hand
    # (viewer's left) rests on the bodice, back view, thumb on the upper edge. One size for both.
    face = QH.QF.queen_face(QH.HEAD, wing_mode="hook",
                           wing=(4.5, 62.0, 0.8), lid_sag=2.6, low_sag=6.4)
    assert QH.HAND_S == 0.82
    assert len(composition.hands) == 2
    args, kwargs, stem = composition.hands[0]
    assert args == ((546, 434), -90, "wrap")
    assert kwargs == dict(size=K.hand_size(face) * QH.HAND_S, hand="L", view="back", grip_w=19)
    args, kwargs, rest = composition.hands[1]
    assert args == (QH.REST_AT, -24, "rest")
    assert QH.REST_AT == (334, 424)
    assert kwargs == dict(size=K.hand_size(face) * QH.HAND_S, hand="R",
                         view="back", curl=6, spread=3)
    assert "cues" not in kwargs
    seam = LineString(F.seam_points(QH.SEAM))
    for _, _, hand in composition.hands:
        assert hand.hand.shape.distance(seam) >= 12
    for hand, (lo, hi) in ((stem, (-10.0, 90.0)), (rest, (90.0, 190.0))):
        forearm = float(np.degrees(np.arctan2(hand.wrist_dir[1], hand.wrist_dir[0])))
        assert lo <= forearm <= hi
    # stem hand: wrist on the outer (right) side of the shaft, fingers toward the axis,
    # thumb above the index fingertip at the shaft's upper end
    tips = stem.hand.meta["digit_tips"]
    thumb = np.asarray(stem.hand.meta["thumb_centerline"].coords[-1])
    assert stem.wrist[0] > 546 + 20.0
    assert np.asarray(tips[1])[0] < 546
    assert thumb[1] < np.asarray(tips[0])[1] - 10.0
    # resting hand: fingers up and across toward the axis,
    # thumb on the upper edge nearer the wrist than the fingertips
    tips = rest.hand.meta["digit_tips"]
    thumb = np.asarray(rest.hand.meta["thumb_centerline"].coords[-1])
    assert rest.wrist[0] == pytest.approx(QH.REST_AT[0]) and np.asarray(tips[1])[0] > QH.REST_AT[0] + 40.0
    assert thumb[0] < np.asarray(tips[0])[0] - 20.0


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
        # the stem sleeve is cut short by the robe edge: two bands instead of pearls
        assert (trim.fills.shape().area > 0) == (i == 1)
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
