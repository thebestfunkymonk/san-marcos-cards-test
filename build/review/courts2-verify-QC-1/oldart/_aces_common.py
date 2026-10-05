"""Shared construction for the three sibling aces A♥ / A♣ / A♦ (brief §F.3, §H.14–16).

Everything the family has in common lives here so the three read as one
hand:

* the u-280 pip at (375, 470) (``deck.frames.ace_pip_d``);
* the gold FINE keyline 10 px outside it, sharp miters (limit 10);
* the MEDIUM geometric knockout of the emblem (paper lines are holes in the
  pip, never paint), with 4.2 px clear between neighbouring paper marks;
* the gold device outside, always FINE line, always *behind* the pip: it
  stops 4.2 px short of the keyline (``behind``), so pip + keyline read as
  the nearest plane;
* the gold two-line caption on baselines 760 / 790 (§J.2 copy, verbatim,
  via ``deck.frames.ACE_CAPTION_TEXT``) with FINE em-rules beside line 1.
"""
from __future__ import annotations

import math

import numpy as np
import shapely

from deck import frames as F
from deck import tokens as T
from deck import motifs as M
from inkkit import geom as G

CX, CY = F.ACE_PIP_CX, F.ACE_PIP_CY
KO = T.MEDIUM                    # §B.2 knockout lines inside solid pips
EDGE = 14.0                      # §H.14: knockout paper keeps >= 14 px from the silhouette edge
COUNTER_MIN = 2.65               # micro-type counters >= 2.5 px (+ AA margin)
COUNTER_CLOSE = 2.0              # ...narrower ones (the cap-12 A) are closed instead
CLEAR = T.INTERLACE_GAP          # 4.2: §I.12 parallel clear / §B.2 interlace gap


def pip_d(suit: str) -> str:
    return F.ace_pip_d(suit)


def keyline(suit: str) -> M.Frag:
    """§F.3 gold FINE keyline, 10 px outside the silhouette, sharp miters."""
    return M.stroke(F.ace_keyline_d(suit), T.FINE, style="point", color=T.FOIL, role="keyline")


def keyline_zone(suit: str) -> str:
    """FILL d of everything the keyline encloses, out to its outer edge:
    gold art 'behind' the pip is cut against this (plus a gap)."""
    return G.offset(pip_d(suit), F.ACE_KEYLINE_OFFSET + T.FINE / 2, join="miter", miter_limit=10)


def behind(f: M.Frag, suit: str) -> M.Frag:
    """``f`` passing behind the pip: broken 4.2 px clear of the keyline."""
    return M.cut(f, keyline_zone(suit), CLEAR)


def knocked_pip(suit: str, *frags: M.Frag, color: str = T.RED) -> M.Frag:
    """The solid pip with every mark of ``frags`` cut out as geometry (paper
    holes); enclosed ink slivers under 3 px are knocked out too (:func:`knock`)."""
    return M.fill(knock(pip_d(suit), *frags), color=color, role="ace-pip")


def inset_d(suit: str, t: float, join: str = "round") -> str:
    """The silhouette offset ``t`` px inward (FILL d)."""
    return G.offset(pip_d(suit), -t, join=join, miter_limit=10)


def caption(suit: str, rules: str = "line1") -> M.Frag:
    """§F.3 / §H.14 caption in gold Barlow Condensed SemiBold: line 1 cap 16
    +220 on y 760, line 2 cap 12 +200 on y 790; text from §J.2 via
    frames.ACE_CAPTION_TEXT. ``rules`` puts the §D FINE em-rules (24 px,
    10 px gap) beside 'line1', 'line2', 'both' or 'none'."""
    t1, t2 = F.ACE_CAPTION_TEXT[suit]
    c1, c2 = F.ACE_CAPTION["line1"], F.ACE_CAPTION["line2"]
    f = M.Frag()
    for i, (txt, c) in enumerate(((t1, c1), (t2, c2)), start=1):
        d, bb = F.type_line(txt, c["cap"], c["baseline"], c["tracking"])
        f += M.fill(open_counters(d), color=T.FOIL, role="caption")
        if rules in (f"line{i}", "both"):
            f += M.stroke(F.em_rules_d(bb, c["cap"]), T.FINE, style="rule", color=T.FOIL, role="em-rule")
    return f


def open_counters(d: str, min_w: float = COUNTER_MIN, close_below: float = COUNTER_CLOSE) -> str:
    """Micro-type print correction for the cap-12 caption line.

    At cap 12 Barlow Condensed SemiBold's D / O / R counters are 2.40–2.51 px
    and its A counter 1.73 px; §I.12 (QA 12) wants >= 2.5 px of paper inside
    a solid, and in metallic ink such counters plug. Counters between
    ``close_below`` and ``min_w`` are opened outward (mitred) to ``min_w`` —
    a 0.1 px change per side, invisible. The A's counter cannot be opened to
    2.5 px without thinning its legs below HAIRLINE, so counters narrower
    than ``close_below`` are closed, as the press would close them."""
    s = G.to_shape(d, tol=0.01)
    polys = list(getattr(s, "geoms", [s]))
    out = []
    for pg in polys:
        holes = []
        for ring in pg.interiors:
            hole = shapely.Polygon(ring)
            w = 2 * shapely.maximum_inscribed_circle(hole, 0.01).length
            if w < close_below:
                continue                                  # closed
            if w < min_w:
                hole = hole.buffer((min_w - w) / 2 + 0.02, join_style="mitre", mitre_limit=4)
            holes.append(hole)
        pg = shapely.Polygon(pg.exterior)
        for h in holes:
            pg = pg.difference(h)
        out.append(pg)
    return G.from_shape(shapely.union_all(out))


# -----------------------------------------------------------------------------
# small geometry helpers
# -----------------------------------------------------------------------------
def unit(deg: float) -> np.ndarray:
    a = math.radians(deg)
    return np.array([math.cos(a), math.sin(a)])


def cross2(a, b) -> float:
    return float(a[0] * b[1] - a[1] * b[0])


def line_x(p1, p2, q1, q2) -> np.ndarray:
    """Intersection of the infinite lines p1–p2 and q1–q2."""
    p1, p2, q1, q2 = (np.asarray(v, float) for v in (p1, p2, q1, q2))
    d1, d2 = p2 - p1, q2 - q1
    return p1 + d1 * (cross2(q1 - p1, d2) / cross2(d1, d2))


def miter_reach(tip, a, b, w: float = KO) -> float:
    """How far a mitred stroke of width ``w`` reaches past the vertex ``tip``
    between neighbours ``a`` and ``b``."""
    tip, a, b = (np.asarray(v, float) for v in (tip, a, b))
    p, q = a - tip, b - tip
    half = math.acos(float(p @ q) / np.linalg.norm(p) / np.linalg.norm(q)) / 2
    return (w / 2) / math.sin(half)


def drop_short(f: M.Frag, min_len: float = 30.0) -> M.Frag:
    """``f`` without the open sub-paths shorter than ``min_len`` (the stubs a
    cut can leave behind)."""
    out = []
    for m in f.marks:
        keep = [p for p, c in G.flatten(m.d, 0.05) if G.Curve(p).length >= min_len]
        if keep:
            out.append(M.Mark("".join(M.polyline_d(p) for p in keep), m.kind, m.w, m.cap, m.join,
                              m.miter, m.color, m.layer, m.role))
    return M.Frag(out, f.meta)


def dash_run(y0: float, y1: float, x: float, on: float = 6.0, off: float = 6.0) -> list[np.ndarray]:
    """Whole dashes (``on`` long, ``off`` apart) on the vertical x from y0
    toward y1, starting with a full dash AT y0; the last dash is whole too
    (partial ones are dropped)."""
    sgn = 1.0 if y1 > y0 else -1.0
    out, s = [], 0.0
    L = abs(y1 - y0)
    while s + on <= L + 1e-6:
        a, b = y0 + sgn * s, y0 + sgn * (s + on)
        out.append(np.array([[x, a], [x, b]]))
        s += on + off
    return out


def prune_hatch(lines, region, *, w: float = KO, boundary=None, min_island: float = 3.2) -> list:
    """Drop hatch lines, shortest first, until every solid island they leave
    inside ``region`` (between them and the ``boundary`` Frag's paper) is at
    least ``min_island`` px wide — so no ink sliver is left at a point."""
    reg = M.region(region)
    lines = sorted(lines, key=lambda c: -float(np.hypot(*(np.asarray(c)[-1] - np.asarray(c)[0]))))
    ink = reg
    if boundary is not None:
        ink = reg.difference(boundary.shape())
    while lines:
        hs = M.stroke(lines, w, style="hatch").shape()
        isl = ink.difference(hs)
        polys = [p for p in getattr(isl, "geoms", [isl]) if p.area > 0.05]
        bad = [p for p in polys if 2 * shapely.maximum_inscribed_circle(p, 0.05).length < min_island]
        if not bad:
            break
        b = shapely.union_all(bad).buffer(w / 2 + 0.3)
        cand = [i for i, c in enumerate(lines) if b.intersects(shapely.LineString(c))]
        if not cand:
            break
        lines.pop(max(cand))            # sorted longest first -> max index = shortest
    return lines


def ko_hatch(region, angle: float, *, pitch: float = T.HATCH_PITCH, w: float = KO,
             boundary=None, min_island: float = 3.2, origin=None, min_len: float = 2.0) -> M.Frag:
    """Half-hatching for a KNOCKOUT (§B.2 hatch, drawn MEDIUM because a paper
    line inside a solid must be >= 2.5 px, §I.12): straight lines at
    ``angle`` and ``pitch`` clipped to ``region`` (butt ends on the contour
    centreline), pruned by :func:`prune_hatch`. Lines shorter than
    ``min_len`` are dropped (a lone stub reads as a flaw, not as tone)."""
    reg = M.region(region)
    lines = M.hatch_lines(reg, angle, pitch, origin=origin, min_len=min_len)
    if origin is not None:
        # the line through the origin lies on the split line itself: drop it
        n = np.array([-math.sin(math.radians(angle)), math.cos(math.radians(angle))])
        o = float(np.asarray(origin, float) @ n)
        lines = [c for c in lines if abs(float(np.mean(c, axis=0) @ n) - o) > 1.0]
    lines = prune_hatch(lines, reg, w=w, boundary=boundary, min_island=min_island)
    return M.stroke(lines, w, style="hatch", role="hatch") if lines else M.Frag()


def knock(solid_d: str, *frags: M.Frag, min_ink: float = 3.0, sliver: float = 1.5,
          sliver_area: float = 1.5) -> str:
    """``solid_d`` minus the paper of ``frags`` (M.knockout), then two press
    corrections, both only ever turning ink into paper:

    * any small ink ISLAND left enclosed between paper lines narrower than
      ``min_ink`` (a sliver the press would fill in anyway) is knocked out;
    * ink WEDGES narrower than 2 × ``sliver`` px where paper lines converge
      (inside a leaf or compass point toward its tip, at a pedicel's
      junction) become paper, so every converging tip ends as one clean paper
      point instead of a hairline of ink. Pieces smaller than ``sliver_area``
      px² (the rounding of ordinary corners) and anything on the silhouette's
      own edge are left alone, so corners and the pip outline are untouched.
    The main body is never removed."""
    d = M.knockout(solid_d, *frags)
    sh = G.to_shape(d, tol=0.01)
    polys = sorted(getattr(sh, "geoms", [sh]), key=lambda p: -p.area)
    if len(polys) > 1:
        keep = [polys[0]] + [p for p in polys[1:]
                             if 2 * shapely.maximum_inscribed_circle(p, 0.02).length >= min_ink]
        sh = shapely.union_all(keep)
    if sliver > 0:
        opened = sh.buffer(-sliver, quad_segs=16).buffer(sliver, quad_segs=16)
        rest = sh.difference(opened)
        edge = G.to_shape(solid_d, tol=0.01).boundary.buffer(0.35)
        bits = [p for p in getattr(rest, "geoms", [rest])
                if p.geom_type == "Polygon" and p.area >= sliver_area and not p.intersects(edge)]
        if bits:
            sh = sh.difference(shapely.union_all(bits).buffer(0.05))
    return G.from_shape(sh)
