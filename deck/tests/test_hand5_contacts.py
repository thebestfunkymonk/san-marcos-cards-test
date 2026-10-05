"""Regressions for defects visible only after the hand outline is stroked."""
import shapely
from shapely.geometry import LineString, Polygon, box

from deck import courtkit as K
from deck import tokens as T
from tools import hand_specimen as specimen


def _painted_scene(scene):
    """Opaque non-ground coverage, including the actual clipped round strokes."""
    regions = []
    for mark in scene.compose().marks:
        if mark.kind == "stroke":
            regions.extend(line.buffer(mark.w / 2, quad_segs=16)
                           for line in K._stroke_lines(mark.d))
        elif mark.kind == "fill" and mark.color != K.JADE:
            regions.append(K.R(mark.d))
    return shapely.union_all(regions)


def test_wrap_thumb_web_remains_open_after_medium_and_contour_stroking():
    for size in (70.0, 85.0, 100.0):
        for hand in ("L", "R"):
            for view in ("back", "palm"):
                for spread, curl in ((0, 0), (12, 4), (18, 45)):
                    result = K.hand5((0, 0), -90, "wrap", size=size, hand=hand,
                                     view=view, grip_w=18, spread=spread, curl=curl)
                    # A closed web becomes a hole in the filled silhouette
                    # plus its round-joined SVG outline, even without a staff.
                    for stroke in (T.MEDIUM, T.CONTOUR):
                        mark = K.outline(result.shape, w=stroke).marks[0]
                        # Buffer the emitted SVG path (rounded coordinates),
                        # not the higher-precision source polygon.
                        painted = shapely.union_all(
                            [K.R(mark.d)] + [line.buffer(stroke / 2, quad_segs=16)
                                            for line in K._stroke_lines(mark.d)])
                        assert not painted.interiors, (size, hand, view, spread, curl, stroke)


def test_wrap_covers_staff_instead_of_leaving_rectangular_windows():
    for size in (70.0, 85.0, 100.0):
        for hand in ("L", "R"):
            for view in ("back", "palm"):
                for grip_w in (12.0, 18.0, 28.0):
                    result = K.hand5((0, 0), -90, "wrap", size=size, hand=hand,
                                     view=view, grip_w=grip_w)
                    tips = result.hand.meta["digit_tips"][:4]
                    low, high = sorted(point[1] for point in tips)[0::3]
                    shaft = box(-grip_w / 2 + 1.55, low, grip_w / 2 - 1.55, high)
                    assert shaft.difference(result.shape).area < 0.12 * shaft.area
                    radii = result.hand.meta["digit_tip_radii"][:4]
                    assert radii[1] > radii[3] * 1.4
                    assert max(point[0] for point in tips) - min(point[0] for point in tips) > 0.07 * size


def test_hold_flat_object_and_stroked_notches_have_no_sub_1_point_6_fill_fragments():
    for size in (70.0, 85.0, 100.0):
        for hand in ("L", "R"):
            for view in ("back", "palm"):
                for spread, curl in ((0, 0), (12, 4), (18, 45)):
                    call = specimen._hand5(size, hand, "hold_flat", view=view,
                                           spread=spread, curl=curl, grip_w=28.0)
                    scene, _ = specimen._scene(call)
                    painted = _painted_scene(scene)
                    # Enclosed ground holes within the actual hand/object
                    # interaction, not merely an unstroked polygon assertion.
                    for region in K._polys_of(painted):
                        for ring in region.interiors:
                            fragment = Polygon(ring)
                            width = fragment.minimum_rotated_rectangle
                            sides = [LineString([a, b]).length
                                     for a, b in zip(width.exterior.coords,
                                                     list(width.exterior.coords)[1:])]
                            assert min(sides) >= T.HAIRLINE, (
                                size, hand, view, spread, curl, fragment.bounds)
