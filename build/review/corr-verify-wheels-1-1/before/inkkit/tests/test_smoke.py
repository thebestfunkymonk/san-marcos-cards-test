"""inkkit smoke + regression tests — plain asserts, runnable as a script:

    .venv/bin/python inkkit/tests/test_smoke.py        # from the project root
    .venv/bin/python inkkit/tests/test_smoke.py geom   # only tests whose name contains 'geom'

(also collectable by pytest if it is ever installed). Every public function is
exercised; composed SVGs are validated with xml.etree + svgelements and
rendered with rsvg-convert (and resvg when available). Each review issue has
a regression test (see the ``# review:`` comments).
"""
from __future__ import annotations

import math
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import time
import traceback
import warnings
import xml.etree.ElementTree as ET

import numpy as np
import shapely

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, ROOT)

from inkkit import card, geom as G, hatch as H, svg, tokens  # noqa: E402
from inkkit import heraldry as HR, preflight as PF, suits as SU  # noqa: E402
from inkkit import ornament as O  # noqa: E402
from inkkit import stroke as ST  # noqa: E402
from inkkit import typeset as TY  # noqa: E402
from inkkit import type as TYPE_ALIAS  # noqa: E402

TMP = tempfile.mkdtemp(prefix="inkkit-test-")
NS = "{http://www.w3.org/2000/svg}"
warnings.simplefilter("ignore")


def ok_d(d, closed_expected=None):
    """d parses, is non-empty and flattens to finite points."""
    assert isinstance(d, str) and d.strip(), "empty d"
    cmds = G.parse_d(d)
    assert cmds and cmds[0][0] == "M"
    polys = G.flatten(cmds, 0.1)
    assert polys, "no geometry"
    for p, _ in polys:
        assert np.isfinite(p).all()
    return d


def area(d, rule="nonzero"):
    return G.to_shape(d, rule).area


def near(a, b, rel=0.02, abs_=1e-6):
    return abs(a - b) <= max(abs_, rel * max(abs(a), abs(b)))


def raises(fn, exc=ValueError):
    try:
        fn()
    except exc:
        return True
    except Exception as e:  # wrong exception type
        raise AssertionError(f"expected {exc.__name__}, got {type(e).__name__}: {e}")
    raise AssertionError(f"expected {exc.__name__}, nothing raised")


def concat_safe(d, pad=5.0):
    """review: FILL outputs must compose by concatenation — a clockwise box
    covering the art concatenated with it must stay fully solid."""
    x0, y0, x1, y1 = G.bbox(d)
    box = G.rect_d(x0 - pad, y0 - pad, x1 - x0 + 2 * pad, y1 - y0 + 2 * pad)
    return near(area(box + d), area(box), 1e-3)


# raster oracle -------------------------------------------------------------------
_M = 200
_X, _Y = np.meshgrid((np.arange(_M) + 0.5) * 100 / _M, (np.arange(_M) + 0.5) * 100 / _M)
_P = np.column_stack([_X.ravel(), _Y.ravel()])


def _winding(poly):
    w = np.zeros(len(_P))
    Q = np.vstack([poly, poly[:1]])
    for (x1, y1), (x2, y2) in zip(Q[:-1], Q[1:]):
        up = (y1 <= _P[:, 1]) & (y2 > _P[:, 1])
        dn = (y1 > _P[:, 1]) & (y2 <= _P[:, 1])
        cr = (x2 - x1) * (_P[:, 1] - y1) - (_P[:, 0] - x1) * (y2 - y1)
        w += np.where(up & (cr > 0), 1, 0) - np.where(dn & (cr < 0), 1, 0)
    return w


def _mask(d):
    w = np.zeros(len(_P))
    for pts, _ in G.flatten(d, 0.02):
        w += _winding(pts)
    return w != 0


# =============================================================================
# svg
# =============================================================================
def test_svg_builder():
    assert svg.fmt(1.0) == "1" and svg.fmt(-0.004) == "0" and svg.fmt(1.256) == "1.26" and svg.fmt(3) == "3"
    a = svg.attrs(stroke_width=1.5, class_="x", fill=None, clip_path="url(#c)")
    assert 'stroke-width="1.5"' in a and 'class="x"' in a and "fill" not in a and 'clip-path="url(#c)"' in a
    # review: duplicate attributes are de-duplicated (last wins), text is escaped,
    # Doc-only keywords are rejected
    a2 = svg.attrs(stroke_width=2, class_="a", sw=1)
    assert a2.count("stroke-width") == 1 and 'stroke-width="1"' in a2
    ET.fromstring(f"<g{a2}/>")
    ET.fromstring(svg.el("desc", "a < b & c"))
    raises(lambda: svg.path("M0 0L1 1", layer="foil"), TypeError)
    parts = [svg.path("M0 0L1 1", fill="#000"), svg.g(svg.circle(1, 2, 3), transform=svg.translate(1, 2)),
             svg.ellipse(0, 0, 2, 1), svg.rect(0, 0, 5, 5, rx=1), svg.line(0, 0, 1, 1, stroke="#000"),
             svg.polyline([(0, 0), (1, 2)]), svg.polygon([(0, 0), (1, 2), (2, 0)]), svg.use("sym", 1, 2),
             svg.clip_path("c", svg.rect(0, 0, 1, 1)), svg.mask("m", svg.rect(0, 0, 1, 1, fill="#fff")),
             svg.linear_gradient("lg", [(0, "#000"), (1, "#fff", 0.5)]),
             svg.radial_gradient("rg", [(0, "#000"), (1, "#fff")]), svg.defs(svg.rect(0, 0, 1, 1)),
             svg.symbol("sym", svg.circle(0, 0, 1), viewBox=(-1, -1, 2, 2)), svg.foil_gradient("fg"),
             svg.el("desc")]
    for p in parts:
        ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">{p}</svg>')
    t = svg.tf(svg.translate(1, 2), svg.rotate(30, 5, 5), svg.scale(2), svg.matrix(1, 0, 0, 1, 3, 4))
    assert "translate(1 2)" in t and "rotate(30 5 5)" in t and "matrix(" in t
    assert svg.path("") == "" and svg.g() == ""
    # review: colour parsing for foil_gradient
    assert svg.parse_color("#b95") == (0xbb, 0x99, 0x55) and svg.parse_color("Gold") == (255, 215, 0)
    assert svg.parse_color("rgb(20, 40, 60)") == (20, 40, 60) and svg.parse_color("none") is None
    svg.foil_gradient("f1", "#b95"); svg.foil_gradient("f2", "gold")
    assert svg.to_hex("white") == "#FFFFFF"


def test_svg_doc_layers():
    doc = svg.Doc(100, 140, layers=("paper", "ink", "foil"))
    assert doc.uid("a") == "a1" and doc.uid("a") == "a2"
    doc.add_def(svg.foil_gradient("f", tokens.FOIL))
    doc.layer_style("foil", fill="url(#f)")
    doc.add(svg.rect(0, 0, 100, 140, fill=tokens.PAPER), layer="paper")
    doc.add([svg.circle(50, 50, 10, fill=tokens.INK), svg.path("M0 0L10 10", stroke=tokens.RED)], layer="ink")
    doc.add(svg.path(G.circle_d(50, 90, 8)), layer="foil")
    doc.add(svg.circle(1, 1, 1, fill="#123456"), layer="extra")
    assert doc.layers == ["paper", "ink", "foil", "extra"]
    s = doc.to_string()
    root = ET.fromstring(s)
    ids = [g.get("id") for g in root.iter(NS + "g") if (g.get("id") or "").startswith("layer-")]
    assert ids == ["layer-paper", "layer-ink", "layer-foil", "layer-extra"]
    fn = doc.save(os.path.join(TMP, "doc.svg"))
    assert os.path.getsize(fn) > 100
    seps = doc.save_layers(os.path.join(TMP, "sep"), exclude=())
    assert len(seps) == 4
    assert len(doc.save_layers(os.path.join(TMP, "sep2"))) == 3  # paper skipped by default
    ink = open(seps[1]).read()
    assert tokens.INK not in ink and "#000000" in ink
    for f in seps:
        ET.parse(f)
    png = doc.render(os.path.join(TMP, "doc.png"), 100)
    assert os.path.getsize(png) > 0
    assert len(doc.save_layers(os.path.join(TMP, "sep3"), mono=None)) == 3


def _plate_mask(svg_text, w=100):
    return PF._raster(svg_text, w)


def test_separations_knockouts():
    """review (critical): paper/white = knockout, masks untouched, style= and
    rgb()/named colours handled, opacity flattened, upper layers knock out."""
    doc = svg.Doc(100, 100, layers=("paper", "red", "ink", "foil"))
    doc.add(svg.rect(0, 0, 100, 100, fill=tokens.PAPER), layer="paper")
    doc.add_def(svg.mask("m1", svg.rect(0, 0, 100, 50, fill="#fff")))
    doc.add(svg.rect(0, 0, 100, 100, fill=tokens.RED, mask="url(#m1)"), layer="red")
    doc.add(svg.path(G.rect_d(10, 10, 80, 80), fill=tokens.INK), layer="ink")
    doc.add(svg.path(G.circle_d(30, 30, 8), fill=tokens.PAPER), layer="ink")             # paper knockout
    doc.add(svg.path(G.circle_d(70, 30, 8), style="fill:white"), layer="ink")            # style= knockout
    doc.add(svg.circle(30, 70, 6, fill="rgb(20,40,60)", opacity=0.4), layer="ink")      # rgb + opacity
    doc.add(svg.path(G.circle_d(70, 70, 8)), layer="ink", knockout=True)               # explicit knockout
    doc.add(svg.path(G.rect_d(45, 45, 10, 10)), layer="foil")
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        plates = doc.separations()
        msgs = " ".join(str(x.message) for x in w)
    assert "opacity" in msgs
    ink = _plate_mask(plates["ink"])
    px = lambda m, x, y: bool(m[int(y), int(x)])
    assert px(ink, 20, 50) and not px(ink, 30, 30) and not px(ink, 70, 30) and not px(ink, 70, 70)
    assert px(ink, 30, 70)                     # rgb() ink prints black (not left in colour)
    assert not px(ink, 50, 50)                 # foil above knocks out of the ink plate
    red = _plate_mask(plates["red"])
    assert px(red, 5, 5) and not px(red, 5, 80)   # mask kept: only the top half prints
    assert not px(red, 50, 30)                    # ink rect above knocks red out
    assert 'mask id="m1"' in plates["ink"] and 'fill="#fff"' in plates["ink"]   # mask content untouched
    foil = _plate_mask(plates["foil"])
    assert px(foil, 50, 50) and not px(foil, 20, 20)
    # overprint keeps the lower plate intact; trap chokes the knockout
    red_op = _plate_mask(doc.separations(overprint=("ink", "foil"))["red"])
    assert px(red_op, 50, 30)
    trapped = doc.separations(trap=2.0)["red"]
    assert "d=" in trapped
    # ribbon workflow from its docstring: paper-filled ribbon over hatching
    d2 = card.new_card()
    d2.add(svg.path(H.parallel(card.card_outline_d(), 45, 6, width=2)), layer="ink")
    rb = O.ribbon(200, 550, 300, 40)
    d2.add(svg.path(rb["silhouette"], fill=tokens.PAPER), svg.path(rb["lines"]), layer="ink")
    m = _plate_mask(d2.separations()["ink"], 750)
    x0, y0, x1, y1 = G.bbox(rb["front"])
    assert not m[int((y0 + y1) / 2), int((x0 + x1) / 2)]    # ribbon interior is paper, not ink


# =============================================================================
# geom
# =============================================================================
def _alarm(seconds):
    def handler(signum, frame):
        raise TimeoutError("hang")
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(seconds)


def test_geom_parse_roundtrip():
    d = ("M10 10 C 20 0 40 0 50 10 S 80 20 90 10 A 20 10 30 0 1 120 40 L 100 100 H 50 V 80 "
         "q 10 -10 20 0 t 20 0 Z m 5 5 l 3 3 a1 1 0 011 1z")
    cmds = G.parse_d(d)
    assert {c[0] for c in cmds} <= {"M", "L", "C", "Q", "Z"}
    d2 = G.cmds_to_d(cmds)
    b1, b2 = G.bbox(d), G.bbox(d2)
    assert all(abs(x - y) < 0.02 for x, y in zip(b1, b2))
    assert G.parse_d(d2)[0] == ("M", 10.0, 10.0)
    assert G.parse_d("m1 1 2 2")[1] == ("L", 3.0, 3.0)
    # review: coordinates after Z used to hang the parser
    _alarm(3)
    try:
        raises(lambda: G.parse_d("M0 0L10 0Z 5 5"))
        raises(lambda: G.parse_d("M0 0 X 5 5"))
    finally:
        signal.alarm(0)
    # review: NaN/inf never reach the file
    raises(lambda: G.poly_d([[0, 0], [np.nan, 1]]))
    raises(lambda: G.cmds_to_d([("M", 0, 0), ("L", math.inf, 1)]))
    polys = G.flatten(d, 0.05)
    assert len(polys) == 2 and polys[0][1] is True
    assert len(G.as_polys(np.array([[0, 0], [1, 1]]))) == 1
    assert len(G.as_polys([[0, 0], [1, 1]])) == 1
    assert len(G.as_polys([np.array([[0, 0], [1, 1]]), np.array([[2, 2], [3, 3]])])) == 2
    assert len(G.as_polys((np.array([[0, 0], [1, 0], [1, 1]]), True))) == 1
    assert G.as_polys(G.to_shape(G.circle_d(0, 0, 5)))[0][1] is True
    assert G.poly_d([[0, 0], [1.005, 2]], True).endswith("z")
    assert G.polys_d([([[0, 0], [1, 1]], False)]).startswith("M0 0")
    assert G.join_d("M0 0L1 1", [[0, 0], [2, 2]], None).count("M") == 2


def test_geom_winding_convention():
    """review (critical): every FILL generator winds clockwise so concatenated
    pieces never punch holes into each other."""
    a = ST.stroke("M100 300 C 250 150 450 450 650 300", 14, "taper-both")
    b = G.outline("M375 120 L375 480", 8)
    assert near(area(a + b), area(G.union(a, b)), 1e-3)
    assert near(area(G.rect_d(0, 0, 100, 100) + G.circle_d(50, 50, 20)), 10000, 1e-4)
    assert G.signed_area(G.flatten(G.circle_d(0, 0, 10))[0][0]) > 0
    assert G.signed_area(G.flatten(G.ellipse_d(0, 0, 10, 5))[0][0]) > 0
    samples = {
        "circle": G.circle_d(0, 0, 20), "ellipse": G.ellipse_d(0, 0, 20, 10, 30), "rect": G.rect_d(0, 0, 50, 50, 5),
        "star": G.star_d(0, 0, 20, 8, 5), "polygon": G.polygon_d(0, 0, 20, 6), "offset": G.offset(G.circle_d(0, 0, 20), 2),
        "outline": G.outline("M0 0L50 0", 4), "from_shape": G.from_shape(shapely.Point(0, 0).buffer(9)),
        "mirror": G.mirror_x(G.star_d(0, 0, 20, 8, 5), 30), "stroke": ST.stroke("M0 0C20 -20 40 20 60 0", 4, "swell"),
        "dot_screen": H.dot_screen(G.rect_d(0, 0, 50, 50), 10, 2),
        "stipple": H.stipple(G.circle_d(0, 0, 20), lambda x, y: np.full_like(x, 0.5)),
        "beaded": O.beaded(G.rect_d(0, 0, 100, 100), 2, 2), "frame_shape": O.frame_shape(0, 0, 100, 100, 10),
        "scroll": O.scroll((0, 0), 0, 100, 1.2, width=5), "leaf": O.leaf((0, 0), (40, -60), 22, style="solid"),
        "cartouche oval": O.cartouche(0, 0, 100, 50, "oval"), "cartouche ogee": O.cartouche(0, 0, 100, 50, "ogee"),
        "shield": HR.shield(0, 0, 80, 100), "text": TY.text_to_path("Cinzel", "OAB", 60, 0, 0)[0],
        "flower": O.flower(0, 0, 30), "ermine": O.ermine_spot(0, 0, 10), "pip": SU.pip("club", 0, 0, 60),
        "fleuron": O.fleuron(0, 0, 40), "sunburst": O.sunburst(0, 0, 10, 40, 12, style="wedge"),
        "filigree": O.filigree_corner(120, 3), "wreath": O.wreath(0, 0, 60, count=6),
        "place_corner tr": O.place_corner(G.star_d(10, 10, 8, 3, 5), 100, 0, "tr"),
    }
    for name, d in samples.items():
        assert concat_safe(d), f"{name} is not concat-safe"
    assert G.orient(G.reverse(G.rect_d(0, 0, 5, 5)), "cw") and G.signed_area(
        G.flatten(G.orient(G.reverse(G.rect_d(0, 0, 5, 5)), "cw"))[0][0]) > 0


def test_geom_booleans_and_shapes():
    c = G.circle_d(0, 0, 10)
    sq = G.rect_d(0, -10, 20, 20)
    ac, asq = math.pi * 100, 400
    inter = math.pi * 100 / 2
    assert near(area(G.union(c, sq)), ac + asq - inter, 0.01)
    assert near(area(G.difference(c, sq)), ac - inter, 0.01)
    assert near(area(G.intersection(c, sq)), inter, 0.01)
    assert near(area(G.xor(c, sq)), ac + asq - 2 * inter, 0.01)
    ring = G.circle_d(0, 0, 10) + G.circle_d(0, 0, 5)
    assert near(area(ring, "evenodd"), math.pi * 75, 0.01)
    assert near(area(ring, "nonzero"), math.pi * 100, 0.01)
    assert near(area(G.resolve(ring, "evenodd"), "nonzero"), math.pi * 75, 0.01)
    assert near(G.area(sq), 400, 1e-3)
    assert G.from_skia(G.to_skia(c))
    assert near(area(G.offset(sq, 2, join="miter")), 24 * 24, 0.01)
    assert near(area(G.offset(sq, -2)), 16 * 16, 0.01)
    assert near(area(G.outline([[0, 0], [100, 0]], 4, cap="flat")), 400, 0.01)
    assert G.outline([[0, 0], [10, 0]], 2, as_shape=True).area > 0
    clipped = G.clip([[-50, 0], [50, 0]], G.rect_d(-10, -10, 20, 20))
    b = G.bbox(clipped)
    assert near(b[0], -10, 0.01) and near(b[2], 10, 0.01)
    out = G.clip_out([[-50, 0], [50, 0]], G.rect_d(-10, -10, 20, 20))
    assert out.count("M") == 2
    f = G.fillet(G.rect_d(0, 0, 100, 60), 10)
    assert 5900 < area(f) < 6000
    assert near(area(G.round_corners(G.rect_d(0, 0, 100, 50), 10)), 5000 - (4 - math.pi) * 100, 0.01)
    wob = np.column_stack([np.cos(np.linspace(0, 6.28, 500)) * 50, np.sin(np.linspace(0, 6.28, 500)) * 50])
    assert len(G.simplify(G.poly_d(wob, True), 0.5)) < len(G.poly_d(wob, True))
    assert near(G.to_shape(G.from_shape(G.to_shape(c))).area, math.pi * 100, 0.01)
    many = "".join(G.poly_d(G.arc_pts(i * 3.0, 0, 2, 0, 360, n=60)[:-1], True) for i in range(250))
    assert len(many) > G.FAST_SEGMENTS * 8
    assert near(G.to_shape(many).area, G.to_shape(G.resolve(many)).area, 0.02)
    # review: empty inputs / ndarray operands
    assert G.union() == "" and G.union("", None) == "" and G.difference("", c) == ""
    assert G.difference(sq, np.array([[0, 0], [1, 0], [1, 1]])) is not None
    raises(lambda: G.bbox([]))
    raises(lambda: G.bbox(""))


def test_geom_union_oracle():
    """review: union() of self-intersecting / vertex-touching inputs and
    to_shape() ring assembly agree with a nonzero-winding raster."""
    a = G.resolve("M49 68L6 56L27 88L6 68L87 23Z")
    b = "M90 87L2 71L0 50Z"
    assert near(G.area(G.union(a, b)), 1739, 0.01)
    d = "M99 54l-87 -12 9 29 33 -42 -28 58 51 -43 -36 30 56 -66 -81 28z"
    assert near(G.area(d), 1960, 0.01)
    rng = np.random.default_rng(5)
    cell = (100 / _M) ** 2
    for it in range(30):
        A = rng.uniform(2, 98, (int(rng.integers(4, 9)), 2)).round(int(rng.integers(0, 3)))
        B = rng.uniform(2, 98, (int(rng.integers(3, 7)), 2)).round(int(rng.integers(0, 3)))
        if it % 4 == 0:
            B[:2] = A[:2]
        da, db = G.poly_d(A, True), G.poly_d(B, True)
        ma, mb = _mask(da), _mask(db)
        for got, ref in ((G.union(da, db), ma | mb), (G.difference(da, db), ma & ~mb),
                         (G.from_shape(G.to_shape(da)), ma)):
            gm = _mask(got) if got else np.zeros(len(_P), bool)
            assert (gm ^ ref).sum() * cell <= 0.015 * max(ref.sum() * cell, 50) + 3, it
        assert abs(G.area(da) - ma.sum() * cell) <= 0.02 * ma.sum() * cell + 4, it
    # many-piece clusters take the GEOS cascaded route: same answer
    ds = [G.poly_d(rng.uniform(2, 98, (int(rng.integers(3, 8)), 2)), True) for _ in range(30)]
    ref = np.zeros(len(_P), bool)
    for d in ds:
        ref |= _mask(d)
    assert (_mask(G.union(*ds)) ^ ref).sum() * cell < 0.01 * ref.sum() * cell + 3


def test_geom_transforms_and_curves():
    d = G.star_d(100, 100, 30, 12, 5)
    bb = G.bbox(d)
    assert near(G.bbox(G.translate(d, 10, 0))[0], bb[0] + 10, 1e-3)
    assert near(G.bbox(G.scale(d, 2, cx=100, cy=100))[2] - 100, 2 * (bb[2] - 100), 1e-3)
    m = G.mirror_x(d, 50)
    assert near(G.bbox(m)[0], 100 - bb[2] + 0, 0.02)
    assert near(G.bbox(G.mirror_y(d, 0))[1], -bb[3], 0.01)
    r = G.rotate180(d, 375, 525)
    assert near(G.bbox(r)[2], 750 - bb[0], 0.01)
    p = G.mirror_line(np.array([[10.0, 0.0]]), (0, 0), 45)
    assert np.allclose(p, [[0, 10]], atol=1e-9)
    assert np.allclose(G.rotate(np.array([[1.0, 0.0]]), 90), [[0, 1]], atol=1e-9)
    # review: a plain list of points stays a point array (chainable)
    rl = G.rotate([(0, 0), (10, 0), (20, 5)], 90)
    assert isinstance(rl, np.ndarray) and rl.shape == (3, 2)
    assert G.smooth_d(rl)
    assert G.repeat_rotational(d, 6, 0, 0).count("M") == 6
    assert near(area(G.bilateral(G.rect_d(10, 0, 20, 20), 0)), 800, 0.01)
    rv = G.reverse("M0 0L10 0C20 0 20 10 10 10Z")
    assert near(area(rv), area("M0 0L10 0C20 0 20 10 10 10Z"), 0.01)
    cv = G.Curve("M0 0L100 0")
    assert near(cv.length, 100) and np.allclose(cv.at(0.5), [50, 0])
    assert np.allclose(cv.tangent(0.5), [1, 0]) and np.allclose(cv.normal(0.5), [0, -1])
    assert len(cv.resample(10)) == 11
    assert near(cv.sub(0.25, 0.75).length, 50, 1e-6)
    raises(lambda: cv.sub(0.9, 0.1))
    assert np.allclose(cv.map(np.array([[50.0, 5.0]])), [[50, -5]])
    assert np.allclose(cv.offset(3)[0], [0, -3])
    assert np.allclose(cv.reversed().at(0), [100, 0])
    assert cv.d().startswith("M0 0") and float(cv.angle(0.5)) == 0.0
    circ = G.Curve(G.circle_d(0, 0, 10))
    assert circ.closed and near(circ.length, 2 * math.pi * 10, 0.01)
    # review: sub() wraps across the seam of closed curves
    assert near(circ.sub(0.9, 0.1).length, 0.2 * circ.length, 0.01)
    assert len(G.resample("M0 0L10 0L10 10", 1, keep_corners=30)) >= 21
    assert np.allclose(G.point_at("M0 0L10 0", 0.5), [5, 0])
    assert np.allclose(G.tangent_at("M0 0L10 0", 0.5), [1, 0])
    assert np.allclose(G.normal_at("M0 0L10 0", 0.5), [0, -1])
    sm = G.smooth_d([(0, 0), (10, 10), (20, 0)])
    assert "c" in sm and len(G.spline([(0, 0), (10, 10), (20, 0)])) > 10
    assert near(area(G.circle_d(0, 0, 10)), math.pi * 100, 0.005)
    assert near(area(G.ellipse_d(0, 0, 10, 5, 30)), math.pi * 50, 0.01)
    assert near(area(G.rect_d(0, 0, 10, 10, 2)), 100 - (4 - math.pi) * 4, 0.01)
    assert len(G.arc_pts(0, 0, 10, 0, 90)) > 5
    assert G.polygon_d(0, 0, 10, 6).count("l") == 1


def test_geom_knockout_interlace_fit():
    art = H.parallel(G.rect_d(0, 0, 200, 100), 45, 7, width=2.1)
    occ = G.circle_d(100, 50, 30)
    ko = G.knockout(art, occ, 4.2)
    assert G.to_shape(ko).intersection(G.to_shape(occ).buffer(4.1)).area < 1.0
    lines = H.parallel(G.rect_d(0, 0, 200, 100), 45, 7)
    kl = G.knockout(lines, occ, 4.2, lines=True, lw=2.1)
    L = shapely.MultiLineString([p for p, _ in G.flatten(kl)])
    assert L.distance(G.to_shape(occ)) >= 4.2 + 1.05 - 0.05
    # interlace: every crossing is gapped, the trefoil keeps 3 alternating crossings
    th = np.linspace(0, 2 * math.pi, 600, endpoint=False)
    tre = np.column_stack([100 + 40 * (np.sin(th) + 2 * np.sin(2 * th)), 100 + 40 * (np.cos(th) - 2 * np.cos(2 * th))])
    il = G.interlace([tre], 2.1, 4.2, closed=True, as_lines=True)
    assert il.count("M") == 3                       # 3 under-passes split the ring into 3 strands
    ok_d(G.interlace(["M0 0L100 100", "M0 100L100 0"], 2, 3))
    ok_d(G.interlace(["M0 50L100 50", "M50 0L50 100"], 2, 3, over="order"))
    # fillet_junction adds material only near the point
    y_ = G.union(ST.stroke("M0 100 L50 0", 6), ST.stroke("M50 0 L100 100", 6))
    fj = G.fillet_junction(y_, (50, 20), 8, 30)
    assert area(fj) > area(y_)
    # fit_curves: fewer bytes, within tolerance both ways
    x = np.linspace(0, 300, 1500)
    dd = G.poly_d(np.column_stack([x, 6 * np.sin(2 * np.pi * x / 17)]))
    ff = G.fit_curves(dd, 0.05)
    assert len(ff) < len(dd) / 2
    A = np.vstack([p for p, _ in G.flatten(dd, 0.005)])
    B = np.vstack([p for p, _ in G.flatten(ff, 0.005)])
    assert shapely.distance(shapely.LineString(A), shapely.points(B[:, 0], B[:, 1])).max() < 0.07
    fc = O.filigree_corner(120, 2)
    assert near(area(G.fit_curves(fc, 0.05)), area(fc), 0.01)
    assert svg.fit_paths('<path d="' + dd + '"/>').count("c") >= 1


# =============================================================================
# stroke
# =============================================================================
def test_stroke_profiles_and_options():
    for prof in ST.PROFILES:
        ok_d(ST.stroke("M0 0C30 -20 60 20 100 0", 6, prof, nib_angle=30 if prof == "nib" else None))
    f = ST.profile_fn("taper-both", taper=0.25)
    assert f(np.array([0.0]))[0] == 0 and near(f(np.array([0.5]))[0], 1.0)
    assert ST.ease(1.0) == 1.0 and ST.ease(0.0) == 0.0
    assert near(area(ST.stroke("M0 0L100 0", 10)), 1000 + math.pi * 25, 0.01)
    assert near(area(ST.stroke("M0 0L100 0", 10, cap="flat")), 1000, 0.01)
    assert area(ST.stroke("M0 0L100 0", 10, cap="pointed")) < 1000
    ok_d(ST.stroke("M0 0L100 0", lambda t: 2 + 4 * t))
    ok_d(ST.stroke("M0 0L100 0", lambda t: 5.0))          # review: scalar-returning callable
    ok_d(ST.stroke("M0 0L100 0", 4, terminal="ball-both", terminal_r=4))
    ok_d(ST.stroke(G.circle_d(0, 0, 30), 5, "nib", nib_angle=0))
    ok_d(ST.stroke_many(["M0 0L10 0", "M0 5L10 5"], width=2))
    ok_d(ST.stroke(["M0 0L10 10", "M0 10L10 0"], 2, merge=True))
    ok_d(ST.variable_stroke(np.column_stack([np.linspace(0, 50, 60), np.zeros(60)]), np.full(60, 2.0)))
    # review: validation and taper clamp
    raises(lambda: ST.stroke("M0 0L10 0", 2, terminal="balls"))
    raises(lambda: ST.stroke("M0 0L10 0", 2, cap="square"))
    raises(lambda: ST.stroke("M0 0L10 0", 2, "bogus"))
    assert area(ST.stroke("M0 0L100 0", 20, "taper-both", taper=5)) > 900
    # min_width floor: tapers end in a round cap, never a needle
    thin = G.to_shape(ST.stroke("M0 0L100 0", 8, "taper-both", min_width=1.2))
    assert thin.buffer(-0.55).area > 0 and near(G.bbox(G.from_shape(thin))[0], -0.6, abs_=0.1)
    # line styles
    for st in ST.STYLES:
        ok_d(ST.styled("M0 0C30 -20 60 20 100 0", 10, "swell", style=st))
    raises(lambda: ST.styled("M0 0L1 1", 2, style="sketch"))


def _disc_union(P, W):
    return shapely.union_all([shapely.Point(p).buffer(w / 2, quad_segs=32) for p, w in zip(P, W) if w > 1e-3])


def test_stroke_fold_safety_and_tips():
    """Hairpins / tight spirals equal the exact disc sweep; review: steep
    tapers (power<1, teardrop/beta profiles) have no fishtails or notches."""
    hp = "M0 0 C 170 0 170 120 0 120"
    for w in (10, 26, 60):
        got = G.to_shape(ST.stroke(hp, w))
        ref = shapely.LineString(G.flatten(hp, 0.02)[0][0]).buffer(w / 2, quad_segs=32)
        assert got.is_valid and got.symmetric_difference(ref).area < 0.01 * ref.area, w
    zz = np.array([[0, 0], [40, -120], [70, 20], [110, -120]])
    got = G.to_shape(ST.stroke(zz, 12))
    ref = shapely.LineString(zz).buffer(6, quad_segs=32)
    assert got.symmetric_difference(ref).area < 0.01 * ref.area
    th = np.linspace(0, 6 * np.pi, 1500)
    r = 90 * np.exp(-0.14 * th)
    sp = np.column_stack([r * np.cos(th), r * np.sin(th)])
    got = G.to_shape(ST.stroke(sp, 14, "swell"))
    assert got.is_valid
    t = np.linspace(0, 1, 400)
    P = np.column_stack([np.linspace(0, 200, 400), np.zeros(400)])
    for prof, kw in (("teardrop", {}), ("teardrop-rev", {}), ("taper-both", {"taper": 0.2, "power": 0.1}),
                     ("taper-both", {"taper": 0.2, "power": 0.3})):
        W = 16 * ST.profile_fn(prof, **kw)(t)
        ref = _disc_union(P, W)
        got = G.to_shape(ST.stroke(P, 16, prof, **kw))
        assert got.symmetric_difference(ref).area < 0.008 * ref.area, (prof, kw)
        assert len(getattr(got, "interiors", [])) == 0


def test_stroke_performance():
    """review: wide strokes used to hit a superlinear cliff (400 px: 85 s)."""
    t0 = time.time()
    for w in (80, 160, 400):
        ST.stroke("M0 0 C 200 -200 400 200 600 0", w)
    ST.stroke("M0 0 C 200 -200 400 200 600 0", 160, "swell")
    assert time.time() - t0 < 5, time.time() - t0


# =============================================================================
# hatch
# =============================================================================
def test_hatch_all():
    shield = "M40 40H210V140C210 185 170 215 125 235C80 215 40 185 40 140Z"
    reg = G.to_shape(shield).buffer(0.05)
    for d in (H.parallel(shield, 30, 4), H.cross(shield, (45, -45), 5), H.contour(shield, 5),
              H.concentric(shield, (120, 120), 5), H.radial(shield, (120, 120), 36),
              H.along(shield, "M0 150C100 50 200 250 300 150", 5),
              H.along(shield, "M0 150C100 50 200 250 300 150", 5, mode="offset"),
              H.between("M40 60L210 60", "M40 200L210 220", 8, clip=shield),
              H.half(shield, [(125, 30), (125, 250)], side=1, spacing=6),
              H.flow(shield, lambda x, y: 0.3, 6)):
        ok_d(d)
        pts = np.vstack([p for p, _ in G.flatten(d, 0.1)])
        assert shapely.contains_xy(reg.buffer(0.3), pts[:, 0], pts[:, 1]).all()
    # half(): exactly one side
    hh = H.half(shield, [(125, 30), (125, 250)], side=1, spacing=6)
    xs = np.vstack([p for p, _ in G.flatten(hh)])[:, 0]
    assert xs.min() >= 124.9
    assert H.flow(shield, lambda x, y: (1.0, 0.2), 6)
    t0 = time.time()
    vort = H.flow(shield, lambda x, y: np.arctan2(y - 140, x - 125) + np.pi / 2, 5)
    assert time.time() - t0 < 6, "flow() did not terminate on closed streamlines"
    assert any(np.allclose(p[0], p[-1]) for p, _ in G.flatten(vort, 0.1))
    ok_d(H.parallel(shield, 30, 4, width=1.2, taper=6, min_width=1.05))
    ok_d(H.contour(shield, 6, count=3, width=1))
    ok_d(H.emit(H.lines_of("M0 0L50 0"), 2, taper=5, cap="butt"))
    tone = H.sphere_tone(125, 140, 80)
    v = tone(np.array([125.0, 60, 200]), np.array([140.0, 80, 200]))
    assert (v >= 0).all() and (v <= 1).all()
    assert H.linear_tone((0, 0), (10, 0))(np.array([5.0]), np.array([0.0]))[0] == 0.5
    raises(lambda: H.linear_tone((0, 0), (0, 0)))
    assert H.radial_tone((0, 0), 10)(np.array([0.0]), np.array([0.0]))[0] == 1.0
    assert H.clamp_tone(lambda x, y: x * 2)(np.array([3.0]), np.array([0.0]))[0] == 1.0
    ct = H.cylinder_tone((0, 0), (0, 100), 20)
    assert ct(np.array([15.0]), np.array([50.0]))[0] > ct(np.array([-15.0]), np.array([50.0]))[0]
    bt = H.bevel_tone(shield, -135, 10)
    assert bt(np.array([205.0]), np.array([100.0]))[0] > bt(np.array([45.0]), np.array([100.0]))[0]
    sd = H.shape_distance_tone(shield, 10)
    assert sd(np.array([42.0]), np.array([100.0]))[0] > sd(np.array([125.0]), np.array([120.0]))[0]
    lat = H.latitudes(125, 140, 80, 5)
    assert len(lat) > 10 and H.latitudes(0, 0, 0, 5) == []
    ok_d(H.engrave(lat, tone, wmax=2.5, clip=G.circle_d(125, 140, 80), fade=4, edge_gap=1.5))
    ok_d(H.engrave(H.lines_of("M0 0L100 0"), 0.8))             # review: scalar tone
    ok_d(H.tonal(shield, tone, angle=-30, spacing=4, cross_at=0.6, fade=4))
    st = H.stipple(G.circle_d(0, 0, 40), lambda x, y: np.full_like(x, 0.7), seed=3)
    st2 = H.stipple(G.circle_d(0, 0, 40), lambda x, y: np.full_like(x, 0.7), seed=3)
    assert st == st2 and st.count("M") > 30
    ok_d(H.dot_screen(shield, 7, 1.5, tone=tone, r_min=0.3, fade=6))


def test_hatch_empty_and_validation():
    """review: empty / consumed regions return '' instead of crashing."""
    shield = "M40 40H210V140C210 185 170 215 125 235C80 215 40 185 40 140Z"
    tone = lambda x, y: np.full_like(np.asarray(x, float), 0.5)
    for fn in (lambda s: H.parallel(s, 45, 4), lambda s: H.cross(s), lambda s: H.contour(s),
               lambda s: H.concentric(s, (0, 0)), lambda s: H.radial(s, (0, 0)),
               lambda s: H.along(s, "M0 0L10 0"), lambda s: H.flow(s, lambda x, y: 0.2),
               lambda s: H.tonal(s, tone), lambda s: H.stipple(s, tone), lambda s: H.dot_screen(s),
               lambda s: H.half(s, [(0, 0), (0, 10)]), lambda s: O.diaper(s), lambda s: O.scales(s),
               lambda s: O.quatrefoil(s), lambda s: O.stripes(s), lambda s: O.ermine(s),
               lambda s: O.chevrons(s), lambda s: O.checks(s), lambda s: O.polka(s),
               lambda s: O.tile(s, G.circle_d(0, 0, 2), 10), lambda s: O.wave_lattice(s)):
        assert fn("") == ""
    assert H.parallel(shield, 45, 4, inset=500) == ""
    raises(lambda: H.parallel(shield, 45, 0))
    raises(lambda: H.dot_screen(shield, 0))
    raises(lambda: H.dot_screen(shield, 6, grid="hexagon"))
    raises(lambda: H.along(shield, "M0 0L1 1", mode="bogus"))


def test_hatch_flow_coverage():
    """review: flow() used to stop after one streamline (float-exact seeds)
    and never reached other polygons or round holes."""
    sp = 4.0
    for shp, fld, exp in ((G.rect_d(250, 250, 100, 100), lambda x, y: 0.3, 100 * 100 / sp),
                          (G.circle_d(300, 300, 50), lambda x, y: 0.3, math.pi * 2500 / sp),
                          (G.circle_d(100, 100, 40) + G.circle_d(300, 100, 40), lambda x, y: 0.3,
                           2 * math.pi * 1600 / sp),
                          (G.difference(G.circle_d(200, 200, 60), G.circle_d(200, 200, 20)),
                           lambda x, y: math.atan2(y - 200, x - 200), math.pi * (3600 - 400) / sp)):
        d = H.flow(shp, fld, sp)
        L = sum(G.Curve(p).length for p, _ in G.flatten(d))
        assert 0.75 * exp < L < 1.15 * exp, (L, exp)
    ok_d(H.flow(G.circle_d(0, 0, 60), lambda x, y: math.atan2(y, x) + math.pi / 2, 5, width=1.2,
                singular=[(0, 0)]))


# =============================================================================
# ornament
# =============================================================================
def test_ornament_scroll():
    c = O.curl((0, 0), 0, 100, 1.2)
    assert c.shape[1] == 2 and len(c) > 100
    v = O.volute((0, 0), 0, 120, 1.5)
    turn = np.unwrap(np.arctan2(*np.diff(v, axis=0).T[::-1]))
    assert near(abs(turn[-1] - turn[0]), 2 * math.pi * 1.5, 0.03)
    o, rho = O.volute_eye(v)
    assert rho > 0
    ls = O.log_spiral((0, 0), 50, 3, 2)
    assert np.hypot(*ls[-1]) < 3.5
    sc = O.s_curve(200, (1, 1), "S")
    assert len(sc) > 100 and len(O.s_curve(200, kind="C")) > 100
    ft = O.fit(sc, (0, 0), (100, 0))
    assert np.allclose(ft[0], [0, 0]) and np.allclose(ft[-1], [100, 0])
    fl = O.flourish(np.array([[0, 0], [50, -20], [100, 0]]), end_turns=1, start_turns=1)
    assert len(fl) > 50
    br = O.branch(fl, 0.4, side=1, length=40)
    assert np.allclose(br[0], G.Curve(fl).at(0.4))
    for d in (O.scroll((0, 0), 0, 150, 1.2, leaves=2), O.scroll((0, 0), 0, 100, 1.5, terminal="eye"),
              O.scroll((0, 0), 0, 100, 1.5, law="power"), O.s_scroll((0, 0), (100, -40)),
              O.c_scroll((0, 0), (120, 0)), O.acanthus_leaf((0, 0), -60, 40, 12),
              O.acanthus_leaf((0, 0), -60, 40, 12, style="outline"),
              O.filigree_corner(150, 1), O.filigree_corner(150, 2, x=700, y=40, corner="tr"),
              O.filigree_corner(150, 3, x=40, y=1000, corner="bl", merge=False),
              O.filigree_corners((40, 40, 670, 970), 140, 2), O.filigree_band(300, 30),
              O.filigree_band(300, 30, center="pearl", angle=90, x=100, y=100),
              O.place_corner(G.rect_d(0, 0, 5, 5), 100, 100, "br")):
        ok_d(d)
    for st in ("monoline", "outline", "inline"):
        ok_d(O.filigree_corner(150, 3, style=st))
        ok_d(O.scroll((0, 0), 0, 100, 1.3, style=st))
        ok_d(O.filigree_band(200, 24, style=st))
    d, pts = O.scroll(centerline=True)
    assert len(pts) > 10
    tl = O.filigree_corner(150, 2, x=0, y=0, corner="tl")
    tr = O.filigree_corner(150, 2, x=750, y=0, corner="tr")
    assert near(area(tl), area(tr), 0.005)
    # review: validation
    for bad in (lambda: O.filigree_corner(150, 0), lambda: O.filigree_corner(150, 4),
                lambda: O.filigree_band(300, 30, center="bulb"), lambda: O.filigree_band(300, 30, repeats=0),
                lambda: O.curl(length=0), lambda: O.s_scroll((0, 0), (0, 0)), lambda: O.log_spiral(r1=0),
                lambda: O.flourish([[0, 0], [0, 0], [10, 0]]), lambda: O.scroll(style="sketch")):
        raises(bad)


def test_scroll_clearance():
    """review: volute turns and ball terminals never fuse (successive turns
    keep the print gap between their stroke edges)."""
    for (L, w, tu) in [(60, 2.0, 1.25), (60, 3.0, 1.5), (80, 4.0, 1.75), (100, 5.0, 2.0), (120, 3.0, 2.25)]:
        d, pts = O.scroll((0, 0), 0, L, tu, width=w, centerline=True)
        W = O.scrollwork._widths(pts, w, "scroll", tokens.MIN_LINE, end_ratio=0.3, taper=0.1)
        assert O.scrollwork._clearance_ok(pts, W, tokens.MIN_GAP * 0.95), (L, w, tu)
        rep = PF.preflight_svg(svg.Doc(200, 200, viewBox=(-100, -100, 200, 200)).add(
            svg.path(d)).to_string(), scale=6, width=200)
        assert rep["plug_frac"] < 0.02, (L, w, tu, rep["plug_frac"])


def test_ornament_guilloche():
    for d in (O.spirograph(0, 0, 80, 30, 40), O.spirograph(0, 0, 45, 18, 20, kind="epi"),
              O.spiro_rosette(0, 0, 75, 30, 30, copies=3), O.rosette(0, 0, 40, 80, lobes=12, lines=6),
              O.rosette(0, 0, 40, 80, lobes=12, lines=6, mod_lobes=4, mod_amp=0.2, twist=0.3, shape=0.8),
              O.rosette_ring(0, 0, 20, 90, bands=2, lines=4), O.guilloche_band(G.circle_d(0, 0, 60), 10, lines=4),
              O.guilloche_frame(0, 0, 300, 200, 20, width=12, lines=4), O.guilloche_strip((0, 0), (200, 50), 10),
              O.guilloche_band(G.rect_d(40, 40, 200, 200), 14), O.wave_lattice(G.rect_d(0, 0, 100, 60), 6, 2, 20)):
        ok_d(d)
    assert O.wave(np.array([math.pi / 2]), 0.5)[0] == 1.0
    ok_d(O.rosette(0, 0, 40, 80, lobes=6, lines=2, width=0.8))
    assert G.flatten(O.spirograph(0, 0, 80, 30, 40), 0.1)[0][1] is True
    b = G.bbox(O.guilloche_band(G.circle_d(0, 0, 60), 10, lines=4))
    assert near(b[2], 65, 0.01)
    # review: spiro_rosette symmetry order is numerator(R/r) for hypo and epi
    for R, r in ((75, 30), (80, 30), (90, 35)):
        P = G.flatten(O.spirograph(0, 0, R, r, 30))[0][0]
        p = O.guilloche._ratio(R, r).numerator
        assert shapely.LinearRing(P).hausdorff_distance(shapely.LinearRing(G.rotate(P, 360 / p))) < 0.1
    # spirograph_fit fills the annulus exactly
    R, r, d = O.spirograph_fit(40, 95, 12, 5)
    rr = np.hypot(*G.flatten(O.spirograph(0, 0, R, r, d))[0][0].T)
    assert near(rr.min(), 40, 0.01) and near(rr.max(), 95, 0.01)
    # review: auto_lines keeps parallel runs apart
    ros = O.rosette(0, 0, 118, 158, lobes=30, lines=16, phase_span=0.5, shape=0.85)
    auto = O.rosette(0, 0, 118, 158, lobes=30, lines=16, phase_span=0.5, shape=0.85, auto_lines=True)
    assert O.min_line_gap(ros) < 1.0 and O.min_line_gap(auto) >= tokens.MIN_LINE + tokens.MIN_GAP
    # review: guilloche_band on a sharp-cornered path does not fold
    gb = O.guilloche_band(G.rect_d(40, 40, 200, 200), 14, lines=4)
    xs = np.vstack([p for p, _ in G.flatten(gb)])
    assert xs[:, 0].min() > 40 - 7.5 and xs[:, 0].max() < 240 + 7.5
    for bad in (lambda: O.spirograph(0, 0, 80, 0, 10), lambda: O.spirograph(0, 0, 80, 30, 10, kind="hyper"),
                lambda: O.rosette_ring(0, 0, 10, 50, bands=0), lambda: O.guilloche_band("M0 0L100 0", 10, amps=())):
        raises(bad)


def test_ornament_borders():
    box = (20, 20, 300, 200)
    for corner in ("round", "square", "notch", "chamfer", "step", "step2"):
        ok_d(O.frame_shape(*box, 24, corner))
        ok_d(O.frame_shape(*box, 24, corner, inset=6))
        ok_d(O.frame_path(*box, 24, corner, 8))
        ok_d(O.rules(*box, [(0, 2), (5, 1)], 24, corner))
    for style in ("classic", "triple", "deco", "fine"):
        ok_d(O.frame(*box, style=style))
    fp = O.frame_path(*box, 24, "round", 10)
    cv = G.Curve(fp)
    ts = np.linspace(0, 1, 400, endpoint=False)
    P = cv.at(ts)
    top = ts[np.argmin(P[:, 1] + 1e-3 * np.abs(P[:, 0] - 170))]
    assert cv.normal(top)[1] < -0.9
    for d in (O.beaded(fp, 2, 2), O.beaded(fp, 2, 2, alternate=1), O.beaded("M0 0L100 0", 2, 2),
              O.rope(fp, 8, 6), O.rope(fp, 8, 6, style="line"), O.rope("M0 0L100 0", 8, 6), O.dentil(fp, 5, 4, 3),
              O.greek_key((0, 0), (200, 0), 14), O.greek_key((0, 0), (200, 0), 14, lw=None),
              O.greek_key_frame(0, 0, 300, 200, 14), O.egg_and_dart("M0 0L200 0", 18),
              O.corner_rosette(0, 0, 20), O.corner_rosette(0, 0, 20, style="daisy"),
              O.corner_rosette(0, 0, 20, style="star"), O.corner_block(0, 0, 10),
              O.frame_strip(0, 0, 300, 200, "band", 12, fill="triangles"),
              O.frame_strip(0, 0, 300, 200, "rope", 12, corner="rosette"),
              O.frame_strip(0, 0, 300, 200, "egg_and_dart", 18), O.frame_strip(0, 0, 300, 200, "dentil", 10),
              O.frame_strip(0, 0, 300, 200, "beaded", 8, corner="pearl"),
              O.frame_strip(0, 0, 300, 200, "greek_key", 14, corner=None),
              O.frame_strip(0, 0, 300, 200, lambda pts, w: G.outline(pts, 2), 10,
                            corner=lambda x, y, s: G.circle_d(x, y, s / 3))):
        ok_d(d)
    for fill in ("zigzag", "triangles", "ladder", "diamond", "chevron", "dots", "none"):
        ok_d(O.band(fp, 10, fill))
        p = O.band("M0 0C50 -20 100 20 150 0", 10, fill, lw=None, parts=True)
        assert set(p) == {"stroke", "fill"} and p["stroke"]
    ok_d(O.band("M0 0C50 -20 100 20 150 0", 10, "zigzag", lw=None))
    # review: lw=None with solid parts needs parts=True
    raises(lambda: O.band("M0 0L150 0", 10, "triangles", lw=None))
    raises(lambda: O.egg_and_dart("M0 0L200 0", 18, lw=None))
    raises(lambda: O.corner_rosette(0, 0, 20, lw=None))
    ok_d(O.corner_rosette(0, 0, 20, style="daisy", lw=None))
    # review: band triangles on step/notch frames never smear into blobs
    tri = O.band(O.frame_path(520, 40, 200, 200, 40, "step2", inset=10), 12, "triangles")
    assert G.to_shape(tri).is_valid
    for st in ("tab", "oval", "ogee", "bracket", "scroll", "shield"):
        ok_d(O.cartouche(100, 100, 120, 60, st))
    # review: ogee never self-intersects when w < 2e
    assert shapely.Polygon(G.flatten(O.cartouche(160, 960, 40, 60, "ogee"))[0][0]).is_valid
    for ends in ("fold", "roll"):
        rb = O.ribbon(0, 200, 50, 20, sag=5, ends=ends)
        assert set(rb) == {"front", "tails", "back", "silhouette", "lines", "path"}
        # review: tails / back never overlap the front
        assert G.to_shape(rb["tails"]).intersection(G.to_shape(rb["front"])).area < 0.5
    rb = O.ribbon(0, 200, 50, 20, sag=12)
    assert rb["back"]
    n, p = O.fit_repeats(100, 7)
    assert near(n * p, 100, 1e-9)
    for bad in (lambda: O.fit_repeats(100, 0), lambda: O.beaded(fp, 0, 0), lambda: O.band(fp, 10, "bogus"),
                lambda: O.ribbon(10, 10, 0), lambda: O.cartouche(0, 0, 10, 10, "blob"),
                lambda: O.frame(*box, style="bogus"), lambda: O.frame_strip(0, 0, 50, 50, "rope", 30)):
        raises(bad)


def test_ornament_botanical():
    out, mid, lh, rh = O.leaf_shape((0, 0), (0, -50), 20)
    assert len(out) > 10 and len(mid) > 10
    for st, h in (("solid", None), ("outline", "half"), ("outline", "full"), ("outline", "veins"),
                  ("engraved", None), ("outline", None)):
        ok_d(O.leaf((0, 0), (40, -60), 20, style=st, hatch=h))
    assert O.leaf((0, 0), (40, -60), 20, style="outline", lw=None).count("M") >= 2
    for shp in O.LEAF_SHAPES:
        ok_d(O.leaf((0, 0), (40, -60), 20, shape=shp, style="solid"))
    for d in (O.sprig("M0 0C40 -20 80 -60 100 -100", count=5),
              O.sprig("M0 0L0 -100", arrangement="opposite", style="outline", hatch="half", jitter=0.5),
              O.laurel("M0 0C40 -20 80 -60 100 -100", berries=3), O.wreath(0, 0, 80),
              O.wreath(0, 0, 80, open_at="bottom", style="outline", lw=1.2), O.grass((0, 0)),
              O.rice("M0 0C0 -60 20 -100 60 -110"), O.rice("M0 0C0 -60 20 -100 60 -110", leaves=3, current=30),
              O.flower(0, 0, 30), O.flower(0, 0, 30, shape="pointed"), O.flower(0, 0, 30, shape="heart"),
              O.flower(0, 0, 30, style="outline"), O.bluebonnet((0, 0), 120),
              O.bluebonnet((0, 0), 120, style="outline"), O.bluebonnet((0, 0), 120, style="engraved"),
              O.bluebonnet((0, 0), 60, whorls=1), O.palmate_leaf((0, 0)), O.palmate_leaf((0, 0), style="outline"),
              O.ripples(0, 0), O.ripples(0, 0, breaks=0)):
        ok_d(d)
    bb = O.bluebonnet((0, 0), 120, parts=True)
    assert set(bb) == {"stem", "flowers", "tip"} and all(bb.values())
    assert O.grass((0, 0), seed=1) == O.grass((0, 0), seed=1)
    assert O.sprig("M0 0L0 -100", jitter=0.7, seed=3) == O.sprig("M0 0L0 -100", jitter=0.7, seed=3)
    # review: occlusion — the stem does not show inside leaves, leaves do not cross
    sp = O.sprig("M0 0L0 -120", count=4, arrangement="opposite", style="outline", lw=None, hatch=None,
                 bend=0.3, parts=True)
    lines = shapely.MultiLineString([p for p, _ in G.flatten(sp["stroke"])])
    assert lines.is_valid
    # review: lw=None contract
    raises(lambda: O.sprig("M0 0L0 -100", style="solid", lw=None))
    raises(lambda: O.sprig("M0 0L0 -100", style="outline", lw=None, berries=2))
    assert O.sprig("M0 0L0 -100", style="outline", lw=None, berries=2, parts=True)["fill"]
    for bad in (lambda: O.leaf((0, 0), (0, 0), 10), lambda: O.leaf((0, 0), (10, 0), 0),
                lambda: O.leaf((0, 0), (10, 0), 5, style="sketch"), lambda: O.wreath(0, 0, 50, open_at="left"),
                lambda: O.rice("M0 0L0 -50", start=1.0), lambda: O.ripples(0, 0, breaks=-1),
                lambda: O.flower(0, 0, 10, shape="star"), lambda: O.sprig("M0 0L0 -50", arrangement="spiral")):
        raises(bad)


def test_ornament_radiance_patterns():
    for d in (O.sunburst(0, 0, 10, 50, 24), O.sunburst(0, 0, 10, 50, 24, style="line"),
              O.sunburst(0, 0, 0, 50, 12, style="wedge"), O.sunburst(0, 0, 10, 50, 9, arc=(180, 270)),
              O.fan(0, 0, 60), O.fan(0, 0, 60, lw=None), O.starburst(0, 0, 40, 12, 8, layers=2),
              O.starburst(0, 0, 40, facets=False)):
        ok_d(d)
    fp = O.fan(0, 0, 60, lw=None, hub=5, parts=True)
    assert fp["stroke"] and fp["fill"]
    raises(lambda: O.fan(0, 0, 60, lw=None, hub=5))
    for st in ("lily", "palmette", "heart", "scroll"):
        ok_d(O.fleuron(0, 0, 40, style=st))
        ok_d(O.fleuron(0, 0, 40, style=st, line_style="monoline", rot=90))
        ok_d(O.fleuron(0, 0, 40, style=st, line_style="outline"))
    # review: faceted starburst has no nicks — the solid covers each facet fully
    sb = G.to_shape(O.starburst(0, 0, 26, 10.5, 5, lw=1.1))
    assert len(sb.interiors if sb.geom_type == "Polygon" else []) <= 5
    for bad in (lambda: O.sunburst(0, 0, 10, 50, 0), lambda: O.sunburst(0, 0, 10, 50, 10, style="line", lw=None),
                lambda: O.starburst(0, 0, 20, lw=None), lambda: O.fleuron(0, 0, 20, style="rose")):
        raises(bad)
    shield = "M0 0H200V110C200 170 150 200 100 215C50 200 0 170 0 110Z"
    reg = G.to_shape(shield)
    for fn in (lambda s: O.diaper(s, 18), lambda s: O.diaper(s, 18, dots="nodes"), lambda s: O.scales(s, 10, dots=True),
               lambda s: O.quatrefoil(s, 28), lambda s: O.quatrefoil(s, 28, filled=True),
               lambda s: O.stripes(s, 5, 5, pinstripe=0.8), lambda s: O.ermine(s, 28),
               lambda s: O.chevrons(s, 11, 7), lambda s: O.checks(s, 14, angle=45), lambda s: O.polka(s, 12, 2),
               lambda s: O.tile(s, O.fleuron(0, 0, 20), 30, 34)):
        t0 = time.time()
        d = ok_d(fn(shield))
        assert time.time() - t0 < 10, "pattern too slow"
        assert G.to_shape(d).difference(reg.buffer(0.3)).area < 1.0
    ok_d(O.ermine_spot(0, 0, 10))
    # review: patterns are FILL-only, lw=None is a clear error
    for fn in (O.diaper, O.scales, O.quatrefoil, O.chevrons):
        raises(lambda: fn(shield, lw=None))


def test_suits_and_heraldry():
    exp = {"spade": (62, 68.2), "heart": (64.5, 59.3), "diamond": (49.6, 69.4), "club": (64.5, 64.5)}
    for s in SU.SUITS:
        w, h = SU.pip_size(s, 62)
        assert near(w, exp[s][0], 0.01) and near(h, exp[s][1], 0.01), (s, w, h)
        for st in ("solid", "outline", "half", "inline", "engraved"):
            ok_d(SU.pip(s, 100, 100, 80, style=st))
        ok_d(SU.pip(s, 0, 0, 80, geometry="classic"))
        d = SU.pip(s, 300, 400, 116)
        x0, y0, x1, y1 = G.bbox(d)
        assert near((x0 + x1) / 2, 300, abs_=0.05) and near((y0 + y1) / 2, 400, abs_=0.05)
    assert SU.suit_name("♠") == "spade" and SU.suit_name("H") == "heart"
    raises(lambda: SU.suit_name("cups"))
    assert [len(SU.pip_layout(n)) for n in ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10")] == \
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    lay = SU.pip_layout(10)
    assert (375.0, 307.0, False) in lay and (375.0, 743.0, True) in lay
    raises(lambda: SU.pip_layout("J"))
    idx = SU.index("10", "spade")
    x0, y0, x1, y1 = G.bbox(idx["rank"])
    assert near(x0, 39.0, abs_=0.3) and near(x1, 129.0, abs_=0.3)       # brief §D.1: "10" spans 39–129
    x0, y0, x1, y1 = G.bbox(SU.index("A", "heart")["rank"])
    assert near((x0 + x1) / 2, 84, abs_=0.5) and near(y0, 46, abs_=0.3) and near(y1, 142, abs_=0.3)
    assert G.bbox(idx["d"])[2] > 600          # rotated copy in the opposite corner
    cf = SU.court_frame()
    assert all(cf[k] for k in ("outer", "inner", "band")) and cf["window"][3] == 511.0
    ok_d(SU.ace_keyline("heart", 375, 470, 280))
    sh = HR.shield(100, 100, 80, 100)
    for t in HR.TINCTURES:
        d = HR.tincture(sh, t)
        assert (d == "") == (t == "argent")
    raises(lambda: HR.tincture(sh, "blue"))
    for st in ("heater", "french", "spanish", "swiss", "lozenge", "roundel", "oval"):
        assert shapely.Polygon(G.flatten(HR.shield(0, 0, 80, 100, st))[0][0]).is_valid
    for st in ("royal", "ducal", "mural", "eastern"):
        ok_d(HR.crown(0, 0, 120, style=st))
        ok_d(HR.crown(0, 0, 120, style=st, line_style="outline"))


# =============================================================================
# typeset
# =============================================================================
def test_typeset():
    assert os.path.isfile(TY.resolve_font("Cinzel")) and "CinzelDecorative" not in TY.resolve_font("Cinzel")
    # review: literal '[wght]', case-insensitive, prefer the variable/regular file
    assert TY.resolve_font("EBGaramond[wght]").endswith("EBGaramond[wght].ttf")
    assert TY.resolve_font("cinzel").endswith("Cinzel[wght].ttf")
    assert TY.resolve_font("Playfair").endswith("PlayfairDisplay[wght].ttf")
    f = TY.load_font("Cinzel", {"wght": 700})
    assert "glyf" in f and "fvar" not in f
    m = TY.font_metrics("Cinzel")
    assert m["upm"] > 0 and m["capHeight"] > 0
    d, bb, adv = TY.text_to_path("Cinzel", "SAN MARCOS", 40, 100, 100, variations={"wght": 700}, tracking=100)
    ok_d(d)
    assert near(TY.measure("Cinzel", "SAN MARCOS", 40, {"wght": 700}, 100), adv, 1e-6)
    assert bb[3] <= 101.5 and bb[1] < 80
    d2, bb2, _ = TY.text_to_path("Cinzel", "SAN MARCOS", 40, 100, 100, anchor="middle", variations={"wght": 700},
                                 tracking=100)
    assert near(bb2[0], bb[0] - adv / 2, 0.01)
    _, bb3, _ = TY.text_to_path("Cinzel", "SAN", 40, 100, 100, anchor="end")
    assert bb3[2] <= 100.5
    _, bbm, _ = TY.text_to_path("Cinzel", "H", 40, 0, 0, baseline="middle")
    assert near((bbm[1] + bbm[3]) / 2, 0, abs_=1.0)
    for b in ("top", "x-middle", "bottom"):
        TY.text_to_path("EBGaramond", "Hx", 20, 0, 0, baseline=b)
    _, _, a_k = TY.text_to_path("PlayfairDisplay", "AVAV", 40, 0, 0)
    _, _, a_n = TY.text_to_path("PlayfairDisplay", "AVAV", 40, 0, 0, kerning=False)
    assert a_k < a_n
    for fn in ("Cinzel", "CinzelDecorative-Bold", "CinzelDecorative-Black", "PlayfairDisplay",
               "PlayfairDisplaySC-Bold", "PlayfairDisplaySC-Black", "CormorantGaramond", "IMFeENsc28P",
               "EBGaramond", "Rye-Regular", "AbrilFatface", "BodoniModa", "BarlowCondensed-SemiBold", "RobotoSlab"):
        ok_d(TY.text_to_path(fn, "Éa9&", 20, 0, 0)[0])
    # review: missing glyphs and control characters warn (or raise on request)
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        TY.text_to_path("Cinzel", "A→B\nC", 40)
        assert any("no glyph" in str(x.message) for x in w) and any("control" in str(x.message) for x in w)
    raises(lambda: TY.text_to_path("Cinzel", "A→B", 40, missing="raise"))
    raises(lambda: TY.text_to_path("Cinzel", "AB", 40, anchor="left"))
    ok_d(TY.text_on_path("Cinzel", "RIVER", 14, "M0 0C50 -40 100 40 150 0", offset=2))
    ok_d(TY.text_on_arc("Cinzel", "TOP", 14, 0, 0, 50))
    ok_d(TY.text_on_arc("Cinzel", "BOTTOM", 14, 0, 0, 50, bottom=True))
    assert TYPE_ALIAS.text_to_path is TY.text_to_path


# =============================================================================
# card, preflight + full-document validation
# =============================================================================
def test_card_helpers():
    assert (card.W, card.H, card.R) == (750.0, 1050.0, 37.5)
    bb = G.bbox(card.card_outline_d())
    assert near(bb[2], 750) and near(bb[3], 1050) and abs(bb[0]) < 1e-6
    assert near(G.bbox(card.inset_outline_d(20))[0], 20)
    cg = card.clip_group(svg.circle(0, 0, 5))
    assert "<clipPath" in cg and "clip-path" in cg
    # review: ids never collide with Doc.uid, and two_headed defines its clip once
    doc = svg.Doc()
    ids = {card.clip_group(svg.circle(0, 0, 5)).split('id="')[1].split('"')[0], doc.uid("clip"),
           card.clip_group(svg.circle(0, 0, 6)).split('id="')[1].split('"')[0],
           card.clip_group(svg.circle(0, 0, 7), doc=doc).split('id="')[1].split('"')[0]}
    assert len(ids) == 4
    assert "rotate(180 375 525)" in card.rot180("<g/>")
    assert "matrix(-1" in card.mirror("<g/>")
    for div in (None, "h", "diag", svg.path("M0 525H750", stroke="#000")):
        th = card.two_headed(svg.circle(375, 200, 40), divider=div)
        root = ET.fromstring(f'<svg xmlns="http://www.w3.org/2000/svg">{th}</svg>')
        idl = [e.get("id") for e in root.iter() if e.get("id")]
        assert len(idl) == len(set(idl)) == 1
    raises(lambda: card.two_headed("<g/>", divider=3))
    doc = card.new_card()
    doc.add(card.safe_zone(True), layer="ink")
    fn = doc.save(os.path.join(TMP, "card.svg"))
    png = card.render(fn, os.path.join(TMP, "card.png"), 200)
    raises(lambda: card.render(os.path.join(TMP, "missing.svg"), os.path.join(TMP, "x.png")), RuntimeError)
    cs = card.contact_sheet([png, png, png], os.path.join(TMP, "sheet.png"), cols=2, round_corners=True)
    from PIL import Image
    assert Image.open(cs).size[0] > 400


def test_preflight():
    """review: preflight reports thin lines and plugging gaps per plate."""
    doc = card.new_card()
    doc.add(svg.path(G.outline("M100 100 L600 100", 0.5)), layer="ink")                  # too thin
    doc.add(svg.path(G.outline("M100 200 L600 200", 2.1)), layer="ink")                  # fine
    doc.add(svg.path(G.outline("M100 300 L600 300", 2.1) + G.outline("M100 302.9 L600 302.9", 2.1)),
            layer="red")                                                                    # 0.8 px gap
    rep = PF.preflight(doc, overlay=os.path.join(TMP, "pf"))
    assert rep["ink"]["thin_area"] > 150 and rep["ink"]["thin_frac"] > 0.1
    assert rep["red"]["plug_area"] > 150 and rep["red"]["thin_frac"] < 0.02
    assert os.path.isfile(rep["ink"]["overlay"]) and "ink" in PF.summary(rep)
    assert PF.node_count('<path d="M0 0L10 10 20 0"/>') == 3


def test_full_document_valid_and_renders():
    """Compose one card using every module; validate, render, time and preflight it."""
    t0 = time.time()
    doc = card.new_card(title="smoke")
    doc.add_def(svg.foil_gradient("foil"))
    doc.layer_style("foil", fill="url(#foil)")
    doc.add(svg.path(O.frame(22, 22, 706, 1006)), layer="ink")
    doc.add(svg.path(O.filigree_corners((50, 50, 650, 950), 140, 2, min_width=1.6, gap=2.4)), layer="foil")
    doc.add(svg.path(O.rosette(375, 525, 90, 130, lobes=18, lines=8, auto_lines=True), fill="none",
                     stroke=tokens.INK, stroke_width=1.05), layer="ink")
    doc.add(svg.path(H.engrave(H.latitudes(375, 525, 80, 4), H.sphere_tone(375, 525, 80), wmin=0.6,
                               clip=G.circle_d(375, 525, 80), edge_gap=1.5), fill=tokens.INK), layer="ink")
    doc.add(svg.path(O.wreath(375, 525, 160, gap=2.6, leaf_kw={"vein_w": 2.4})), layer="foil")
    doc.add(svg.path(ST.stroke(O.curl((200, 200), 0, 150, 1.2), 5, "scroll", terminal="ball", min_width=1.05),
                     fill=tokens.RED), layer="red")
    doc.add(svg.path(TY.text_to_path("Cinzel", "SMOKE", 40, 375, 180, anchor="middle")[0], fill=tokens.INK),
            layer="ink")
    doc.add(svg.path(SU.index("K", "heart")["d"], fill=tokens.RED), layer="red")
    build = time.time() - t0
    assert build < 10, f"card build took {build:.1f}s"
    fn = doc.save(os.path.join(TMP, "full.svg"))
    s = open(fn).read()
    root = ET.fromstring(s)
    assert not list(root.iter(NS + "text")), "no <text> allowed"
    assert "href=\"http" not in s and "xlink:href=\"http" not in s and "<image" not in s
    import svgelements
    parsed = svgelements.SVG.parse(fn)
    assert sum(1 for e in parsed.elements() if isinstance(e, svgelements.Path)) > 5
    png = card.render(fn, os.path.join(TMP, "full.png"), 750)
    from PIL import Image
    im = Image.open(png).convert("L")
    assert im.size == (750, 1050)
    ext = im.getextrema()
    assert ext[0] < 80 and ext[1] > 200, "render looks blank"
    if shutil.which("resvg"):
        r = subprocess.run(["resvg", fn, os.path.join(TMP, "full-resvg.png")], capture_output=True, text=True)
        assert r.returncode == 0, r.stderr
    for f in doc.save_layers(os.path.join(TMP, "full-sep")):
        ET.parse(f)
        card.render(f, f[:-4] + ".png", 150)
    fitted = doc.save(os.path.join(TMP, "full-fit.svg"), fit=0.05)
    assert os.path.getsize(fitted) < os.path.getsize(fn)
    rep = PF.preflight(doc, profiles={"foil": "foil"}, scale=3)
    assert rep["ink"]["thin_frac"] < 0.02 and rep["foil"]["thin_frac"] < 0.03, PF.summary(rep)


def test_performance_card_scale():
    """review: primitives that used to blow the 10 s/card budget."""
    card_d = card.card_outline_d()
    fc = O.filigree_corner(120, 2, merge=False)
    pieces = [G.translate(fc, (k % 13) * 50, (k // 13) * 200) for k in range(52)]
    for name, fn, limit in (("quatrefoil", lambda: O.quatrefoil(card_d, 24), 8.0),
                            ("scales", lambda: O.scales(card_d, 8), 8.0),
                            ("union of 52 overlapping corners", lambda: G.union(*pieces), 8.0),
                            ("full-card flow", lambda: H.flow(card_d, lambda x, y: 0.3 + 0.002 * x, 5), 10.0)):
        t0 = time.time()
        fn()
        dt = time.time() - t0
        assert dt < limit, f"{name}: {dt:.1f}s"


# =============================================================================
TESTS = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]


def main(filt=None):
    failed = 0
    t_all = time.time()
    tests = [t for t in TESTS if not filt or any(f in t.__name__ for f in filt)]
    for t in tests:
        t0 = time.time()
        try:
            t()
            print(f"  ok    {t.__name__:40s} {time.time() - t0:5.2f}s")
        except Exception:
            failed += 1
            print(f"  FAIL  {t.__name__}")
            traceback.print_exc()
    print(f"\n{len(tests) - failed}/{len(tests)} passed in {time.time() - t_all:.1f}s  (artifacts: {TMP})")
    return failed


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
