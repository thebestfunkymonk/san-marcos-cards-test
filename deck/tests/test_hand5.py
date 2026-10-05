import math

import numpy as np
from scipy.signal import find_peaks
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import orient
from shapely.ops import substring

from deck import courtkit as K
from deck import tokens as T


POSES = ("wrap", "cup", "rest", "hold_flat", "open")
HANDS = ("L", "R")
VIEWS = ("back", "palm")
SIZES = (70.0, 85.0, 100.0)


def _hand(pose, *, hand="R", view="back", angle=-90.0, size=85.0, **kw):
    kw.setdefault("grip_w", 0.72 * size if pose == "cup" else 22.0)
    return K.hand5((312.0, 427.0), angle, pose, size=size, hand=hand, view=view, **kw)


def test_hand5_is_one_solid_five_digit_silhouette_for_every_pose_and_view():
    for pose in POSES:
        for hand in HANDS:
            for view in VIEWS:
                for size in SIZES:
                    result = _hand(pose, hand=hand, view=view, size=size)
                    assert isinstance(result, K.Hand)
                    assert isinstance(result.shape, Polygon), (pose, hand, view, result.shape.geom_type)
                    assert result.shape.is_valid
                    assert not result.shape.interiors
                    meta = result.hand.meta
                    assert len(meta["digit_centerlines"]) == 5
                    assert len(meta["digit_tips"]) == 5
                    assert len(meta["notch_points"]) == 3
                    thumb = meta["thumb_distal"]
                    fingers = meta["finger_band"]
                    assert thumb.intersection(fingers).area <= 0.02 * thumb.area
                    for tip, radius in zip(meta["digit_tips"][:4], meta["digit_tip_radii"][:4]):
                        assert result.shape.boundary.distance(Point(tip)) <= radius * 1.1
                    thumb_tip = meta["digit_tips"][4]
                    assert result.shape.boundary.distance(Point(thumb_tip)) <= 0.15 * size
                    assert min(Point(a).distance(Point(b)) for i, a in enumerate(meta["digit_tips"])
                               for b in meta["digit_tips"][i + 1:]) >= 4.2


def test_wrap_thumb_leaves_palm_side_and_stays_out_of_finger_band_at_any_angle():
    for angle in (-180.0, -90.0, -35.0, 0.0, 75.0, 180.0):
        for hand in HANDS:
            for view in VIEWS:
                for size in SIZES:
                    result = _hand("wrap", angle=angle, hand=hand, view=view, size=size, grip_w=16.0)
                    meta = result.hand.meta
                    thumb_distal = meta["thumb_distal"]
                    finger_band = meta["finger_band"]
                    assert thumb_distal.intersection(finger_band).area <= 0.02 * thumb_distal.area
                    assert thumb_distal.distance(Point(meta["digit_tips"][0])) >= 4.2
                    thumb_tip, index_tip = meta["digit_tips"][4], meta["digit_tips"][0]
                    assert 4.2 <= Point(thumb_tip).distance(Point(index_tip)) <= 0.48 * size


def test_interior_lines_are_short_clear_of_notches_and_at_most_three():
    for pose in POSES:
        for hand in HANDS:
            for view in VIEWS:
                meta = _hand(pose, hand=hand, view=view).hand.meta
                lines = meta["inner_lines"]
                assert len(lines) <= 3
                assert all(5.0 <= line.length <= 0.30 * meta["size"] for line in lines)
                assert all(line.distance(notch) >= 7.3 for line in lines for notch in meta["notch_points"])
                assert all(mark.w == T.MEDIUM for mark in meta["inner"].marks)


def _visible_digit_lobes(result):
    """Detect convex tip caps on the actual outline, not the metadata count.

    Distal digit neighbourhoods exclude wrist/palm corners. Each convex
    maximum can belong to only one digit. A recess of at least half a
    MEDIUM stroke must separate adjacent caps; tiny scallops in a merged
    finger mass are not five visible digits.
    """
    boundary = orient(result.shape, sign=1).exterior
    count = math.ceil(boundary.length / 0.25)
    points = np.array([boundary.interpolate(i * boundary.length / count).coords[0]
                       for i in range(count)])
    step = round(2.0 / (boundary.length / count))
    incoming = points - np.roll(points, step, axis=0)
    outgoing = np.roll(points, -step, axis=0) - points
    turns = np.arctan2(incoming[:, 0] * outgoing[:, 1] - incoming[:, 1] * outgoing[:, 0],
                      np.sum(incoming * outgoing, axis=1))
    peaks, _ = find_peaks(np.tile(turns, 3), height=0.4, prominence=0.25,
                         distance=round(5.0 / (boundary.length / count)))
    distal = [substring(line, 0.5, 1.0, normalized=True)
              for line in result.hand.meta["digit_centerlines"]]
    radii = np.array(result.hand.meta["digit_tip_radii"])
    detected = {}
    for peak in peaks:
        if count <= peak < 2 * count:
            cap = Point(points[peak % count])
            distances = np.array([line.distance(cap) for line in distal])
            digit = int(np.argmin(distances / radii))
            if distances[digit] <= 2.0 * radii[digit]:
                if digit not in detected or distances[digit] < detected[digit][1]:
                    detected[digit] = (peak % count, distances[digit])
    visible = len(detected)
    for first, second in ((4, 0), (0, 1), (1, 2), (2, 3)):
        if first not in detected or second not in detected:
            continue
        start, end = detected[first][0], detected[second][0]
        if (end - start) % count > count / 2:
            start, end = end, start
        arc = points[np.arange(start, start + (end - start) % count + 1) % count]
        chord = points[end] - points[start]
        offsets = arc - points[start]
        recess = np.max((chord[0] * offsets[:, 1] - chord[1] * offsets[:, 0])
                        / np.linalg.norm(chord))
        if recess < T.MEDIUM / 2:
            visible -= 1
    return visible


def test_five_visible_silhouette_digits_with_spread_and_curl_in_every_pose():
    for pose in POSES:
        for hand in HANDS:
            for view in VIEWS:
                for size in SIZES:
                    for spread, curl in ((0.0, 0.0), (12.0, 4.0), (7.0, 25.0), (18.0, 45.0)):
                        result = _hand(pose, hand=hand, view=view, size=size,
                                       spread=spread, curl=curl,
                                       grip_w=0.72 * size if pose == "cup" else 28.0)
                        assert _visible_digit_lobes(result) == 5, (
                            pose, hand, view, size, spread, curl)


def test_inner_lines_keep_four_point_two_pixels_of_paper_at_specimen_sizes():
    for pose in POSES:
        for hand in HANDS:
            for view in VIEWS:
                for size in SIZES:
                    for spread, curl in ((0.0, 0.0), (12.0, 4.0), (7.0, 25.0), (18.0, 45.0)):
                        result = _hand(pose, hand=hand, view=view, size=size,
                                       spread=spread, curl=curl)
                        lines = result.hand.meta["inner_lines"]
                        assert len(lines) == len(result.hand.meta["inner"].marks) <= 3
                        for i, first in enumerate(lines):
                            for second in lines[i + 1:]:
                                assert first.distance(second) >= T.MEDIUM + 4.2 - 1e-8, (
                                    pose, hand, view, size, spread, curl,
                                    first.distance(second))
                        drawn = [line for mark in result.hand.meta["inner"].marks
                                 for line in K._stroke_lines(mark.d)]
                        assert all(first.distance(second) >= T.MEDIUM + 4.2 - 1e-8
                                   for i, first in enumerate(drawn) for second in drawn[i + 1:])


def test_sleeve_is_merged_into_one_outline_with_a_cuff_colour_edge():
    sleeve_shape = K.box(235.0, 415.0, 312.0, 439.0)
    sleeve_body = K.box(235.0, 415.0, 303.0, 439.0)
    cuff = K.box(303.0, 415.0, 312.0, 439.0)
    sleeve = K.Part(sleeve_shape, K.fill(sleeve_body, K.RED) + K.fill(cuff, K.JADE),
                    K.outline(sleeve_shape))
    result = K.hand5((312.0, 427.0), -90.0, "rest", size=85.0, hand="R", view="back",
                     sleeve=sleeve)

    assert isinstance(result, K.Hand)
    assert result.shape.geom_type == "Polygon"
    assert not result.shape.interiors
    outlines = [mark for mark in result.hand.lines.marks if mark.role == "outline"]
    cuff_edges = [mark for mark in result.hand.lines.marks if mark.role == "cuffline"]
    assert len(outlines) == 1
    assert not cuff_edges
    assert any(mark.kind == "fill" and mark.color == K.RED for mark in result.hand.fills.marks)
    assert any(mark.kind == "fill" and mark.color == K.JADE for mark in result.hand.fills.marks)
    assert result.hand.meta["kind"] == "hand5+sleeve"

    # Hand.tucked calls this rebuild when the sleeve/cuff implies a different
    # forearm direction; rebuilding must retain the merged sleeve and edge.
    rebuilt = result.hand.meta["rebuild"](np.array([0.0, 1.0]))
    assert rebuilt.shape.geom_type == "Polygon"
    assert rebuilt.meta["kind"] == "hand5+sleeve"
    assert len([mark for mark in rebuilt.lines.marks if mark.role == "outline"]) == 1
    assert not [mark for mark in rebuilt.lines.marks if mark.role == "cuffline"]
    assert any(mark.kind == "fill" and mark.color == K.RED for mark in rebuilt.fills.marks)
    assert any(mark.kind == "fill" and mark.color == K.JADE for mark in rebuilt.fills.marks)


def test_hand5_is_deterministic_and_only_uses_legal_strokes():
    for pose in POSES:
        first = _hand(pose, hand="L", view="palm", angle=-63.0)
        second = _hand(pose, hand="L", view="palm", angle=-63.0)

        assert first.shape.wkb == second.shape.wkb
        assert [mark.d for mark in first.hand.frag.marks] == [mark.d for mark in second.hand.frag.marks]
        assert all(mark.w in T.LEGAL_STROKES for mark in first.hand.frag.marks if mark.kind == "stroke")


def test_pose_controls_change_geometry_and_held_object_anchors():
    narrow = _hand("wrap", grip_w=12.0)
    wide = _hand("wrap", grip_w=28.0)
    curled = _hand("wrap", curl=45.0)
    spread = _hand("wrap", spread=16.0)
    assert narrow.shape.symmetric_difference(wide.shape).area > 1.0
    assert narrow.shape.symmetric_difference(curled.shape).area > 1.0
    assert narrow.shape.symmetric_difference(spread.shape).area > 1.0

    flat_narrow = _hand("hold_flat", grip_w=18.0)
    flat_wide = _hand("hold_flat", grip_w=44.0)
    assert flat_narrow.hand.meta["object_width"] != flat_wide.hand.meta["object_width"]
    assert flat_narrow.shape.symmetric_difference(flat_wide.shape).area > 1.0

    cup = _hand("cup", size=85.0, grip_w=20.0)
    assert cup.hand.meta["object_radius"] >= 0.36 * 85.0
    assert cup.shape.symmetric_difference(_hand("cup", size=85.0, grip_w=64.0).shape).area > 1.0
    assert cup.shape.symmetric_difference(_hand("cup", size=85.0, grip_w=20.0, curl=35.0).shape).area > 1.0
    assert cup.shape.symmetric_difference(_hand("cup", size=85.0, grip_w=20.0, spread=14.0).shape).area > 1.0


def test_add_to_default_halo_is_new_hand5_only_and_none_keeps_legacy_semantics():
    hand5 = _hand("wrap")
    no_halo_scene = K.Scene()
    hand5.add_to(no_halo_scene, "hand5")
    assert no_halo_scene.items[-1].halo == K.LINE_TUCK

    explicit_none_scene = K.Scene()
    K.fist((0.0, 0.0)).add_to(explicit_none_scene, "legacy", halo=None)
    assert explicit_none_scene.items[-1].halo == K.LINE_TUCK

    default_legacy_scene = K.Scene()
    K.fist((0.0, 0.0)).add_to(default_legacy_scene, "legacy")
    assert default_legacy_scene.items[-1].halo == K.HALO

    # A cuff at a different angle from the constructed wrist triggers
    # Hand.tucked's rebuild callback and must still yield one hand outline.
    angled = K.hand5((312.0, 427.0), -75.0, "rest", size=85.0, hand="R", view="back")
    wrist = np.asarray(angled.wrist)
    arm = np.array([0.0, 1.0])
    normal = np.array([arm[1], -arm[0]])
    sleeve_region = Polygon([
        tuple(wrist - 20.0 * normal), tuple(wrist + 20.0 * normal),
        tuple(wrist + 100.0 * arm + 20.0 * normal),
        tuple(wrist + 100.0 * arm - 20.0 * normal),
    ])
    sleeve_scene = K.Scene().part(
        "sleeve", K.Part(sleeve_region, K.fill(sleeve_region, K.RED), K.outline(sleeve_region))
    )
    angled.add_to(sleeve_scene, "hand5", halo=0.0)
    hand_item = sleeve_scene.items[-1]
    assert hand_item.occ.geom_type == "Polygon"
    assert len([mark for mark in hand_item.frag.marks if mark.role == "outline"]) == 1


def test_size_and_pose_metadata_are_explicit():
    result = _hand("hold_flat", size=91.0, curl=12.0, spread=4.0, grip_w=24.0)

    assert result.hand.meta["kind"] == "hand5"
    assert result.hand.meta["pose"] == "hold_flat"
    assert math.isclose(result.hand.meta["size"], 91.0)
    assert math.isclose(result.wrist_w, 0.42 * 91.0, rel_tol=0.1)
