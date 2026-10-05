"""Rule checks for the figurative motifs (Track B2; plain asserts):

    .venv/bin/python -m deck.motifs.test_figurative
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
from shapely.geometry import LineString, Point, Polygon, box  # noqa: E402

from inkkit import geom as G  # noqa: E402

from deck import tokens as T  # noqa: E402
from deck.motifs import core as C  # noqa: E402
from deck.motifs import fauna as FA  # noqa: E402
from deck.motifs import forms as FM  # noqa: E402
from deck.motifs import geometric as M  # noqa: E402
from deck.motifs import hair as HR  # noqa: E402
from deck.motifs import lion as LI  # noqa: E402
from deck.motifs import rice as RI  # noqa: E402

BANNED_SVG = re.compile(r"transform=|<text|<filter|Gradient|mix-blend|vector-effect|<image")


def _clean(f: C.Frag, name: str):
    assert not C.check(f), (name, C.check(f)[:3])
    svg = f.svg()
    assert not BANNED_SVG.search(svg), name
    for wv in re.findall(r'stroke-width="([0-9.]+)"', svg):
        assert float(wv) in T.LEGAL_STROKES, (name, wv)


def test_specimens_clean():
    from deck.motifs.sheet_figurative import specimens
    for sp in specimens():
        _clean(sp["frag"], sp["title"])


def test_moleca_fits_and_is_bilateral():
    from deck.motifs.sheet_figurative import spade_h13, spade_live
    for sil_d in filter(None, (spade_live(), spade_h13())):
        f = LI.lion_moleca(375, 262, silhouette=sil_d)
        sil = C.region(sil_d)
        # §H.13: gold >= 12 px from the silhouette edge (the stroke's outer edge)
        # (tolerance: 0.4 px, the round caps of clipped hatch ends)
        inner = sil.buffer(-12.0 + 0.4)
        outside = f.shape().difference(inner)
        assert outside.area < 0.05, ("lion crosses the 12 px clearance", outside.area)
        # frontal and bilateral: the mirror about x = 375 matches
        dev = f.shape().symmetric_difference(f.mirror_x(375).shape()).area
        assert dev < 0.02 * f.shape().area, ("moleca not bilateral", dev)
        # the wing tips never meet at the axis
        tips = f.select(lambda m: m.role == "tip")
        assert tips, "no wing-tip curls"
        g = tips.shape()
        left = g.intersection(box(0, 0, 375, 1050))
        right = g.intersection(box(375, 0, 750, 1050))
        assert left.distance(right) >= 4.2, left.distance(right)
        # no halo / book / inscription: nothing drawn above the wing curls except the spade apex region
        assert not any(m.role in ("halo", "book", "text") for m in f.marks)


def test_lion_mark_budget():
    for s in (60, 56, 48, 40, 32, 24):
        for style in ("line", "solid"):
            m = LI.lion_mark(0, 0, s, style=style)
            assert m.meta["strokes"] <= 24, (s, style, m.meta["strokes"])
            x0, y0, x1, y1 = m.bbox()
            assert x1 - x0 <= s + 0.6, (s, style, x1 - x0)
            _clean(m, f"mark {s} {style}")
    solid = LI.lion_mark(0, 0, 40, style="solid")
    assert any(m.kind == "fill" and m.layer == "gold" for m in solid.marks)
    # §C rule 4: the solid clasp's contour and details are Aquifer, never thin gold
    assert all(m.layer == "ink" for m in solid.marks if m.kind == "stroke")


def test_andante_in_lens():
    f = LI.lion_andante(0, 0)
    geo = M.lens_geometry(0, -220, 220, 330)
    lens = C.region(geo["d"])
    assert f.shape().difference(lens.buffer(-4.0)).area < 0.5
    # walks to the viewer's left: the head (eye) is left of the body's centre
    eye = f.select(lambda m: m.role == "pupil").bbox()
    x0, _, x1, _ = f.bbox()
    assert eye[0] < (x0 + x1) / 2 - 60
    roles = {m.role for m in f.marks}
    for r in ("ledge", "course", "hatch", "ripple", "arm", "covert", "tail", "terminal"):
        assert r in roles, r
    # 5 primaries (outlined feathers) on the near wing
    ripples = [m for m in f.marks if m.role == "ripple"]
    assert len(ripples) >= 3


def test_ribbon_leaf():
    f = RI.ribbon_leaf(0, 0, 0, 160)
    L, Wd = 160, f.meta["width"]
    assert 10 <= L / Wd <= 14, L / Wd
    hatch = [p for m in f.marks if m.role == "hatch" for p, _ in G.flatten(m.d)]
    assert len(hatch) >= 10
    mid = f.meta["mid"]
    cv = G.Curve(mid)
    # every hatch line is perpendicular to the midrib (within 2°) and 7 px apart
    for p in hatch:
        a, b = p[0], p[-1]
        s = np.argmin(np.hypot(*(mid - a).T))
        t = cv.tangent_s(G.Curve(mid[:s + 1]).length if s > 0 else 0)
        v = (b - a) / np.hypot(*(b - a))
        assert abs(float(v @ t)) < math.sin(math.radians(2.5)), float(v @ t)
    # narrow leaves fall back to plain vesicas (§I.12) and say so
    g = RI.ribbon_leaf(0, 0, 0, 80)
    assert not any(m.role == "hatch" for m in g.marks) and g.meta.get("warnings")


def test_rice_stalk_botany():
    f = RI.rice_stalk(0, 200, -90, 190)
    fem, mal = f.meta["female"], f.meta["male"]
    assert len(fem) >= 5 and len(mal) >= 3
    # erect female spikelets above (smaller y), drooping males below
    assert max(p[1] for p in fem) < min(p[1] for p in mal)
    awns = [m for m in f.marks if m.role == "awn"]
    assert awns and all(m.w == T.HAIRLINE for m in awns)
    assert all(m.w != T.HAIRLINE for m in f.marks if m.role in ("spikelet", "stalk"))


def test_wreath_pairs_shrink():
    f = RI.rice_wreath_arc(0, 0, 150, leaf_len=64, ratio=10.0)
    assert f.meta["n_pairs"] >= 3
    assert any(m.role == "knot" for m in f.marks)
    # bilateral about x = 0
    dev = f.shape().symmetric_difference(f.mirror_x(0).shape()).area
    assert dev < 0.02 * f.shape().area


def test_gill_plume():
    f = FA.gill_plume("M0 110 C 6 70 24 40 40 20", n=7)
    barbs = [m for m in f.marks if m.role == "barb"]
    assert len(barbs) == 7
    tip = [m for m in f.marks if m.role == "tip"]
    assert len(tip) == 1 and abs(G.bbox(tip[0].d)[2] - G.bbox(tip[0].d)[0] - 4.2) < 0.05
    lens = [G.Curve(G.flatten(m.d)[0][0]).length for m in barbs]
    assert all(a >= b - 1e-6 for a, b in zip(lens, lens[1:])), "barbs must shorten toward the tip"
    assert all(m.color == T.RED for m in f.marks)


def test_current_lines():
    f = HR.current_lines("M0 0 C 20 40 20 80 60 110", 4)
    lines = f.meta["lines"]
    assert len(lines) == 4
    # 7 px pitch between neighbours (mid-length sample)
    for a, b in zip(lines, lines[1:]):
        d = LineString(b).distance(Point(*G.Curve(a).at(0.4)))
        assert abs(d - 7.0) < 0.3, d
    terms = [G.bbox(m.d) for m in f.marks if m.role == "terminal"]
    assert len(terms) == 4
    cs = [((x0 + x1) / 2, (y0 + y1) / 2) for x0, y0, x1, y1 in terms]
    for p, q in zip(cs, cs[1:]):
        assert math.dist(p, q) >= T.TERMINAL_D + 4.2 - 0.05, math.dist(p, q)
    g = HR.current_lines("M0 0 C 20 40 20 80 60 110", 5, gold="alternate")
    assert any(m.layer == "gold" and m.kind == "fill" for m in g.marks)


def test_darter():
    f = FA.fountain_darter(0, 0, 100)
    ol = f.select(lambda m: m.role == "outline")
    x0, y0, x1, y1 = ol.bbox()
    # body depth (centrelines) measured over the trunk, i.e. without the caudal fin
    trunk = ol.shape().intersection(box(x0 + 0.25 * (x1 - x0), -100, x1, 100))
    body_depth = trunk.bounds[3] - trunk.bounds[1] - T.FINE
    assert 5.6 <= (x1 - x0 - T.FINE) / body_depth <= 6.4, (x1 - x0) / body_depth
    spines = [p for m in f.marks if m.role == "spine" for p, _ in G.flatten(m.d)]
    assert len(spines) == 9
    stitch = [p for m in f.marks if m.role == "stitch" for p, _ in G.flatten(m.d)]
    lens = [G.Curve(p).length for p in stitch]
    assert all(abs(L - 7.0) < 0.1 for L in lens[:-1]), lens
    xs = sorted(p[0][0] for p in stitch)
    starts = sorted(min(p[0][0], p[-1][0]) for p in stitch)
    ends = sorted(max(p[0][0], p[-1][0]) for p in stitch)
    gaps = [b - a for a, b in zip(ends[:-1], starts[1:])]
    assert all(abs(g - 4.0) < 0.1 for g in gaps), gaps
    assert all(m.cap == "butt" for m in f.marks if m.role == "stitch")
    assert any(m.role == "pupil" for m in f.marks) and any(m.role == "eye" for m in f.marks)
    # facing left is the exact mirror
    g = FA.fountain_darter(0, 0, 100, facing=-1)
    assert f.mirror_x(0).shape().symmetric_difference(g.shape()).area < 1.0


def test_salamander_anatomy():
    f = FA.blind_salamander(0, 0)
    eyes = [m for m in f.marks if m.role == "eye"]
    assert len(eyes) == 2
    plumes = [m for m in f.marks if m.role == "tip"]
    assert len(plumes) == 6                                     # three gills a side
    toes = [m for m in f.marks if m.role == "toe"]
    assert len(toes) == 2 * 4 + 2 * 5                           # 4 front, 5 hind
    grooves = [m for m in f.marks if m.role == "groove"]
    assert len(grooves) == 22
    x0, y0, x1, y1 = f.bbox()
    assert max(x1 - x0, y1 - y0) <= 230, "must fit the seal's inner field"


def test_knockout_modes():
    for f in (LI.lion_mark(40, 40, 60), FA.fountain_darter(60, 30, 100), RI.ribbon_leaf(0, 20, 0, 160)):
        x0, y0, x1, y1 = f.bbox()
        solid = G.rect_d(x0 - 5, y0 - 5, x1 - x0 + 10, y1 - y0 + 10)
        ko = C.knockout(solid, f)
        a_solid = G.area(solid)
        a_marks = float(f.shape().area)
        assert abs(G.area(ko) - (a_solid - a_marks)) < 0.003 * a_solid


def test_track_a_hook():
    from deck import frames as F
    res = F.lion_mark_fragments(375, 525, 24)
    assert res is not None and dict(res.items()).get("gold")
    med = F.medallion_fragments("K", "S", mark=lambda cx, cy: F.lion_mark_fragments(cx, cy, 24))
    assert med["gold"]


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
