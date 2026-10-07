"""Regression checks for the continuous Ferryman King composition."""
from types import SimpleNamespace

import numpy as np
import pytest
from shapely.geometry import LineString, Point

from art import KH
from deck import courtkit as K


@pytest.fixture(scope="module")
def composition():
    """Observe real construction without replacing the generated artwork."""
    observed = SimpleNamespace(hands=[], sleeves=[], cuffs=[], held=[],
                               chalices=[], bubbles=[], decorations=[])

    def record(owner, name, destination):
        original = getattr(owner, name)

        def wrapped(*args, **kwargs):
            result = original(*args, **kwargs)
            destination.append((args, kwargs, result))
            return result

        patch.setattr(owner, name, wrapped)

    def forbidden(*args, **kwargs):
        pytest.fail("Continuous KH must not use a legacy fist or routed sleeve")

    with pytest.MonkeyPatch.context() as patch:
        for name in ("fist", "fist_geom", "fist_wrist", "sleeve", "_arm_dir"):
            patch.setattr(K, name, forbidden)
        record(K, "hand5", observed.hands)
        record(KH, "sleeve_end", observed.sleeves)
        record(KH, "sleeved_hand", observed.cuffs)
        record(KH, "held_attribute", observed.held)
        record(KH.KP, "chalice", observed.chalices)
        record(KH.KP, "bubble_column", observed.bubbles)
        record(KH.KC.KW, "window", observed.decorations)
        record(K, "lion_clasp", observed.decorations)
        observed.scene = KH.figure()
    return observed


def test_approved_continuous_scene_has_ten_integrated_items(composition):
    assert KH.DOUBLE_HEAD == "continuous"
    assert KH.SEAM == -20
    scene = composition.scene
    assert scene.rank is None
    assert len(scene.items) == 10  # The original separate-plate scene had 26.
    assert [item.name for item in scene.items] == [
        "collar", "robes", "pole+handR+cuff", "chalice+handL+cuff",
        "bubbles", "hair-1", "hair1", "head", "beard", "crown",
    ]
    assert all(item.halo == 0 for item in scene.items)


def test_two_face_scaled_wrapping_hands_without_legacy_arms(composition):
    # The pole hand approaches from the tunic side, 14 px down the unchanged shaft.
    assert KH.FIST == (527.4, 467.9)
    assert KH.POLE_HAND_DEG == pytest.approx(KH.POLE_DEG + 180.0)
    assert KH.CHAL_GRIP == (233.5, 394.0)
    assert KH.HAND_SCALE == 0.82
    assert len(composition.hands) == 2
    face = K.face(KH.HEAD, "frontal", **KH.FACE_KW)
    expected = [
        # Compensated for the wrap chirality fix: opposite letter (chalice: angle + 180), legacy lines.
        (KH.FIST, KH.POLE_HAND_DEG, "L", "back", KH.POLE_WIDTH),
        (KH.CHAL_GRIP, 90.0, "R", "back", 10.4),
    ]
    for (args, kwargs, _), (at, angle, hand, view, grip) in zip(
            composition.hands, expected):
        assert args == (at, angle, "wrap")
        assert kwargs["size"] == pytest.approx(K.hand_size(face) * 0.82)
        assert kwargs["hand"] == hand
        assert kwargs["view"] == view
        assert kwargs["grip_w"] == grip
        assert kwargs["cues"] is False


def test_sleeves_are_jade_lapel_lobes_not_separate_cuff_stubs(composition):
    robes = next(item for item in composition.scene.items if item.name == "robes")
    jade = robes.frag.select(lambda m: m.kind == "fill" and m.layer == "jade").shape()
    assert len(composition.sleeves) == len(composition.cuffs) == 2
    for sleeve_call, cuff_call, hand_call, held_call, name, run, reach in zip(
            composition.sleeves, composition.cuffs, composition.hands, composition.held,
            ("pole+handR+cuff", "chalice+handL+cuff"), (KH.POLE_RUN, KH.CHAL_RUN), (KH.POLE_REACH, KH.CHAL_REACH)):
        (hand,), sleeve_kw, sleeve = sleeve_call
        assert sleeve_kw["run"] == run and sleeve_kw["reach"] == reach
        (_, cuff_sleeve), _, cuff = cuff_call
        assert cuff_sleeve is sleeve
        (attribute, hand_cuff), _, held = held_call
        assert hand_cuff is cuff
        # The sleeve is the lapel's own region: jade fill covers it and no
        # closed outline separates it from the tunic.
        assert sleeve.difference(jade).area < 0.1
        # A bold turn-back band parallels the cuff mouth inside the jade sleeve.
        assert any(mark.role == "cuffline" for mark in robes.frag.marks)
        assert sleeve.area > 0.0
        mouth = K.P(hand.wrist) - hand.wrist_dir * reach
        body = mouth + hand.wrist_dir * run
        assert np.hypot(*(body - mouth)) <= 90.0
        # The hand ends at the cuff mouth: its region is the hand minus the
        # sleeve, with no separate cuff fill or cuff outline of its own.
        assert not cuff.fills.marks
        assert cuff.shape.intersection(sleeve).area < 0.01
        assert cuff.shape.symmetric_difference(hand.shape.difference(sleeve)).area < 1.0
        assert not any(mark.role == "cuffline" for mark in cuff.lines.marks)
        filleted = K.U(attribute.shape, cuff.shape).buffer(1.6).buffer(-1.6).simplify(0.2)
        assert held.shape.symmetric_difference(filleted).area < 0.01
        assert any(mark.role == "grip-edge" for mark in held.lines.marks)
        outline = held.lines.select(lambda mark: mark.role == "contour")
        assert outline.layers() == K.outline(held.shape, role="contour").layers()
        item = next(item for item in composition.scene.items if item.name == name)
        assert item.sil and item.halo == 0
        assert item.occ.symmetric_difference(held.shape).area < 0.01


def test_whole_card_robe_geometry_and_textile_contours_are_c2(composition):
    robes = next(item for item in composition.scene.items if item.name == "robes")
    assert robes.occ.symmetric_difference(K.rot180(robes.occ)).area < 0.1
    assert robes.occ.bounds[1] < 525 < robes.occ.bounds[3]
    assert robes.occ.contains(LineString([(KH.AX, 500), (KH.AX, 550)]))

    # The window and clasp are upper-portrait details, not doubled by the
    # garment builder. Outside both orientations of those apertures, the
    # chest hatch and garment contours must remain continuous C2 courses.
    decoration_shapes = [
        result.shape
        for _, _, result in composition.decorations
    ]
    mask = K.c2(K.U(*decoration_shapes)).buffer(10.0)
    for role in ("hatch", "outline", "contour", "scale"):
        strokes = robes.frag.select(
            lambda mark: mark.kind == "stroke" and mark.role == role)
        ink = strokes.shape().difference(mask)
        assert not ink.is_empty
        rotated = K.rot180(ink)
        # polyline_d writes 0.001 px; rotated paths serialize at 0.01 px.
        # Measure positional agreement, not accumulated sub-pixel strips.
        assert ink.hausdorff_distance(rotated) <= 0.05
        assert ink.difference(rotated.buffer(0.05)).area < 1e-6
        assert rotated.difference(ink.buffer(0.05)).area < 1e-6
    assert any(mark.role == "scale" for mark in robes.frag.marks)
    assert any(mark.role.startswith("pearl@") for mark in robes.frag.marks)


def test_original_chalice_and_graduated_bubbles_stay_clear_of_seam(composition):
    assert len(composition.chalices) == len(composition.bubbles) == 1
    args, kwargs, chalice = composition.chalices[0]
    assert args == (233.5, 292.0)
    assert kwargs == dict(rim_hw=29.0, bowl_h=44.0, stem_len=90.0,
                          foot_hw=(7.0, 21.5), tip_r=2.2, engrave_gap=4.3)
    assert {"lip", "joint", "rib"} <= {mark.role for mark in chalice.lines.marks}
    args, kwargs, bubbles = composition.bubbles[0]
    assert args == (
        [(231.5, 280.0), (227.5, 265.0), (222.5, 247.0),
         (216.5, 226.0), (209.5, 201.0)],
        [6.3, 8.4, 10.5, 12.6, 15.2],
    )
    assert kwargs == {}
    assert all(mark.role == "bubble" for mark in bubbles.lines.marks)
    assert len(bubbles.lines.marks) == 5
    # Neither original nor rotated held objects end on the central join.
    seam_band = K.box(0, 505, 750, 545)
    for _, _, held in composition.held:
        assert not K.c2(held.shape).intersects(seam_band)
    assert not K.c2(bubbles.shape).intersects(seam_band)


def test_chalice_lapel_fills_enclosed_pocket_but_not_open_finger_notch(composition):
    robes = next(item for item in composition.scene.items if item.name == "robes")
    jade = robes.frag.select(lambda mark: mark.kind == "fill" and mark.layer == "jade").shape()
    red = robes.frag.select(lambda mark: mark.kind == "fill" and mark.layer == "red").shape()
    for point in (Point(249.7, 424.7), Point(500.3, 625.3)):
        assert jade.contains(point)
        assert not red.contains(point)
    for point in (Point(221.8, 404.4), Point(528.2, 645.6)):
        assert red.contains(point)
        assert not jade.contains(point)
    trim_ink = robes.frag.select(lambda mark: mark.role == "outline").shape()
    for point in (Point(253.5, 419.7), Point(496.5, 630.3)):
        assert not trim_ink.intersects(point.buffer(2.0))


def test_art_is_deterministic():
    assert KH.build() == KH.build()
