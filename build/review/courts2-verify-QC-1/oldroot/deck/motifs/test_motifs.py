"""Rule checks for deck.motifs (plain asserts; run as a script from the root):

    .venv/bin/python -m deck.motifs.test_motifs
"""
from __future__ import annotations

import math
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import shapely  # noqa: E402
from shapely.geometry import LineString, Point, box  # noqa: E402

from inkkit import geom as G  # noqa: E402

from deck import tokens as T  # noqa: E402
from deck.motifs import core as C  # noqa: E402
from deck.motifs import geometric as M  # noqa: E402

BANNED_SVG = re.compile(r"transform=|<text|<filter|Gradient|mix-blend|vector-effect|<image")


def _sym_diff(a: C.Frag, b: C.Frag) -> float:
    return float(a.shape().symmetric_difference(b.shape()).area)


def _dev(a: C.Frag, b: C.Frag) -> float:
    """Max deviation (px) between two fragments' outlines."""
    return float(a.shape().hausdorff_distance(b.shape()))


def test_legal_widths():
    for w in T.LEGAL_STROKES:
        C.stroke("M0 0L10 0", w)
    for bad in (1.0, 2.0, 3.0, 5.0):
        try:
            C.stroke("M0 0L10 0", bad)
        except ValueError:
            continue
        raise AssertionError(f"width {bad} accepted")


def test_rigid_only():
    f = C.stroke("M0 0L10 0")
    # scale, shear, det-1 non-uniform stretch: all rejected (review #29)
    for M_ in ((2, 0, 0, 2, 0, 0), (1, 0, 0.7, 1, 0, 0), (0.6, 0.8, 0, 1 / 0.6, 0, 0)):
        try:
            f.transformed(M_)
        except ValueError:
            continue
        raise AssertionError(f"non-rigid transform {M_} accepted")
    # rigid ones pass
    a = math.radians(33)
    f.transformed((math.cos(a), math.sin(a), -math.sin(a), math.cos(a), 5, 7))
    f.transformed((-1, 0, 0, 1, 750, 0))


def test_meta_warnings_merge():
    """Composition keeps every part's QA warnings (review #28)."""
    a = C.Frag(meta={"warnings": ["a"]})
    b = C.Frag(meta={"warnings": ["b"]})
    assert (a + b).meta["warnings"] == ["a", "b"]
    assert C.frag(a, b).meta["warnings"] == ["a", "b"]
    c = C.Frag(meta={"warnings": ["c"]})
    c += a
    assert c.meta["warnings"] == ["c", "a"] and a.meta["warnings"] == ["a"], "aliased"


def test_specimens_clean():
    from deck.motifs.sheet import specimens
    for sp in specimens():
        f = sp["frag"]
        assert not C.check(f), (sp["title"], C.check(f))
        svg = f.svg()
        assert not BANNED_SVG.search(svg), sp["title"]
        for wv in re.findall(r'stroke-width="([0-9.]+)"', svg):
            assert float(wv) in T.LEGAL_STROKES, (sp["title"], wv)


def test_rosette_symmetry():
    cn = M.source_rosette(375, 525, 130)
    assert _dev(cn, cn.rot180()) < 0.05, ("C_N rosette not C2", _dev(cn, cn.rot180()))
    assert _sym_diff(cn, cn.mirror_x()) > 500.0, "C_N rosette should be chiral"
    d2 = M.source_rosette(375, 525, 130, twist=False)
    assert _dev(d2, d2.mirror_x()) < 0.05, ("straight rosette not mirror-symmetric (x)", _dev(d2, d2.mirror_x()))
    assert _dev(d2, d2.mirror_y()) < 0.05, ("straight rosette not mirror-symmetric (y)", _dev(d2, d2.mirror_y()))


def test_rosette_radii():
    sp = M.rosette_spec(130)
    assert sp["detail"] == "full"
    assert sp["crater"] == 20 and sp["rings"] == (30.0, 39.0, 50.0)
    assert sp["bubbles"] == (62.0, 24, 7.0) and sp["band"] == (72.0, 104.0, 24) and sp["rule"] == 130.0
    f = M.source_rosette(0, 0, 130)
    # every mark stays inside the outer rule's outer edge
    x0, y0, x1, y1 = f.bbox()
    assert max(abs(x0), abs(y0), x1, y1) <= 130 + T.FINE / 2 + 0.05


def test_knockout_exact():
    solid = G.rect_d(0, 0, 300, 300)
    f = M.source_rosette(150, 150, 90)
    ko = C.knockout(solid, f)
    a_solid = G.area(solid)
    a_marks = float(f.shape().intersection(box(0, 0, 300, 300)).area)
    assert abs(G.area(ko) - (a_solid - a_marks)) < 0.002 * a_solid, (G.area(ko), a_solid - a_marks)


def test_knockout_matches_line_mode():
    """REGRESSION (review 2026-09, critical): knockout mode must cut exactly
    the ink line mode paints — for every specimen, at several rotations and
    mirrored, rendered by the real renderer (core.knockout_vs_line)."""
    from deck.motifs.sheet import specimens
    worst = []
    for sp in specimens():
        r = C.knockout_vs_line(sp["frag"], rotations=(0.0, 137.0, 180.0), mirror=True)
        # anti-aliasing never flips a pixel by > half the range; allow a few at needle tips
        if r["bad_px"] > max(8, 1e-4 * r["ink_px"]):
            worst.append((sp["title"], r["bad_px"], [t for t in r["tiles"] if t[1]]))
    assert not worst, worst


def test_outline_is_the_union():
    """Frag.outline() (pathops, curves kept) equals the GEOS union of the
    marks' own outlines at every 30° and mirrored (review fix (c))."""
    cases = [M.source_rosette(0, 0, 40, twist=False, w=T.MEDIUM), M.rowel_star(0, 0, 40),
             M.comb_spray("M0 60 C 40 30 100 10 170 15", cone=11), M.vent_roundel(0, 0, 56),
             M.stalactite(0, 0, 64, 20), M.reed_node_medallion(0, 0, 26)]
    for f in cases:
        for g in [f.rotate(a, 0, 0) for a in range(0, 360, 30)] + [f.mirror_x(0), f.rot180(0, 0)]:
            a = C.region(g.outline())
            b = g.shape()
            dis = C._disagree(a, b)
            assert dis < 0.5, ("outline != union", dis)


def test_interlace_gap():
    under = C.stroke("M-60 40 C -20 40 20 -40 60 -40")
    over = C.stroke("M-60 -40 C -20 -40 20 40 60 40")
    res = C.cut(under, over, 4.2)
    clear = res.shape().distance(over.shape())
    assert clear >= 4.2 - 0.05, clear
    assert len(G.flatten(res.marks[0].d)) == 2, "under-stroke not broken in two"


def test_hatch_pitch_and_butt():
    leaf = C.vesica_d((0, 60), (0, -60), 44)
    h = C.half_hatch(leaf, "left", "perp")
    lines = [p for p, _ in G.flatten(h.marks[0].d)]
    ys = sorted(float(p[0][1]) for p in lines)
    d = np.diff(ys)
    assert np.allclose(d, T.HATCH_PITCH, atol=0.02), d
    boundary = C.region(leaf).boundary.union(LineString([(0, -70), (0, 70)]))
    for p in lines:
        for q in (p[0], p[-1]):
            assert boundary.distance(Point(q)) < 0.03, q
    assert h.marks[0].cap == "butt" and h.marks[0].w == T.FINE


def test_wave_clearances():
    hook = M.wave_hook(20.0)
    a, b = hook.meta["wave_a"], hook.meta["wave_b"]
    eye = np.array(hook.meta["wave_eye"])
    # eye sits at the crest centre, clear of the crest and the rule
    assert np.allclose(eye, (a + b, -a), atol=0.02)
    assert b - T.TERMINAL_D / 2 - T.FINE / 2 >= 4.2 - 1e-6
    assert a - T.TERMINAL_D / 2 - T.FINE / 2 >= 4.2 - 1e-6
    band = M.running_wave(0, 300, 0, rule=False)
    pieces = [C.Frag([m]) for m in band.marks if m.role == "wave"]
    for p, q in zip(pieces[:-1], pieces[1:]):
        assert p.shape().distance(q.shape()) >= 4.2, "neighbouring hooks too close"


def test_bubbles_gap():
    f = C.bubble_row((0, 100), (0, 0), C.bubble_sizes(3, 7))
    assert f.meta["bubble_gap"] >= 3.0
    geoms = [C.Frag([m]).shape() for m in f.marks]
    for g1, g2 in zip(geoms[:-1], geoms[1:]):
        assert g1.distance(g2) >= 3.0 - 1e-6


def test_lens_geometry():
    geo = M.lens_geometry(375, 104, 946, 540)
    assert abs(geo["R"] - 463.2) < 0.05
    assert abs(geo["c_left"][0] - 181.8) < 0.05 and abs(geo["c_right"][0] - 568.2) < 0.05


def test_layers_output():
    f = C.stroke("M0 0L10 0") + C.dot(5, 5, 4.2, color=T.FOIL) + C.stroke("M0 5L10 5", color=T.RED)
    lay = f.layers()
    assert list(lay) == ["red", "gold", "ink"], list(lay)
    assert f.recolor(T.JADE).layers().keys() == {"jade"}


def main():
    tests = [(k, v) for k, v in globals().items() if k.startswith("test_") and callable(v)]
    t0 = time.time()
    for name, fn in tests:
        t = time.time()
        fn()
        print(f"ok  {name}  ({time.time() - t:.1f}s)")
    print(f"{len(tests)} tests passed in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
