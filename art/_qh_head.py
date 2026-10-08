"""art/_qh_head.py — the Q♥ head-dress and hair (brief §H.5).

The 1950s PETAL SWIM-CAP DIADEM: "overlapping half-hatched petals in jade
forming a close cap, with a gold rim and a gold pearl at its crown. Gold
current-line hair shows beneath, threaded with 3 small bubbles."

Construction (compass-built, card px):

* The cap SILHOUETTE is an arc spline over the skull of the 3/4 head: it
  runs from the far temple over the crown and down the back of the head to
  the nape (a 3/4-right head shows the back of its skull on the viewer's
  left). The RIM (gold, ``h`` px) is the band above the rim arc — one
  circle through the nape, the forehead and the far temple, so it crosses
  the forehead high and sweeps down behind the temple, over the ear.
* LATITUDES: circles through three points interpolated between the rim arc
  (v = 0) and the crown point (v = 1). Row j of petals hangs its pointed
  tips on latitude ``v_j`` (the lowest row over the rim); rows nearer the
  crown are IN FRONT (petals sewn on like shingles, tips down), so each row
  shows only its tips. Along each latitude the petals are spaced evenly in
  angle about the head's vertical axis and projected (sin), so they crowd
  and narrow toward both sides — the cap turns with the head.
* Each PETAL is an ogive tip (two arcs) with straight sides running up to
  the next row; a FINE midrib from the tip and ONE hatched half (§B.2:
  perpendicular to the midrib, 7.0 pitch).
* The PEARL: a gold disc on the crown with an Aquifer contour and a Ø4.2
  paper highlight knocked out.
* HAIR: gold current lines (§G.24) — on the near side a full mid-century
  FLIP falling from under the rim behind the jaw to the shoulder and
  curling out, threaded with three bubbles (FINE rings, the gold knocked out
  inside them); on the far side a short flipped lock below the rim.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C

P = K.P
FINE, MEDIUM, RULE, CONTOUR = K.FINE, K.MEDIUM, K.RULE, K.CONTOUR
JADE, GOLD, RED, INK = K.JADE, K.GOLD, K.RED, K.INK


def _spline(points, **kw):
    d, pts, _ = K.FM.arc_spline([P(q) for q in points], **kw)
    return d, np.asarray(pts)


class PetalCap:
    """Compass layout of the petal cap for a 3/4 head.

    * RIM: the gold band between two concentric circles about ``c0`` (far
      below the head): its lower edge (radius ``R0``) crosses the forehead
      and meets the temples; it is ``h`` px tall.
    * DOME: the cap's silhouette, a circle (``dc``, ``dR``) over the skull,
      bulging toward the back of the head (the viewer's left for a
      3/4-right head); with ``scallop`` its edge is a ring of shallow
      scallops (the petals' rounded backs).
    * ROWS: petals hang in rows on circles about ``c0`` (radius ``r_tip`` for
      the tips); each petal is an ogive tip with sides running out radially
      (away from ``c0``) to the dome; rows further from ``c0`` (higher) lie
      IN FRONT — sewn on like shingles, each row shows its pointed tips over
      the row below, the lowest row over the rim."""

    def __init__(self, *, c0, R0, h=10.0, dc, dR, scallop=None, clip_lo=None):
        self.c0, self.R0, self.h = P(c0), float(R0), float(h)
        self.dc, self.dR = P(dc), float(dR)
        dome = K.R(K.circle(self.dc, self.dR))
        if scallop:
            n, depth, phase = scallop
            d_, _, _ = K.FM.scallop_ring(self.dc[0], self.dc[1], self.dR - depth, self.dR, n, phase=phase)
            dome = K.R(d_).buffer(0)
        self.dome = dome
        below = K.R(K.circle(self.c0, self.R0))
        shape = dome.difference(below)
        if clip_lo is not None:
            shape = shape.difference(clip_lo)
        self.shape = max(K._polys_of(shape), key=lambda g: g.area)

    def rim(self):
        band = K.R(K.circle(self.c0, self.R0 + self.h)).difference(K.R(K.circle(self.c0, self.R0)))
        band = band.intersection(self.shape)
        band = max(K._polys_of(band), key=lambda g: g.area)
        return K.Part(band, K.fill(band, GOLD), K.outline(band), {})

    def body(self):
        """The cap's base (jade) above the rim: it shows in the V notches
        between the lowest petals."""
        body = self.shape.difference(K.R(K.circle(self.c0, self.R0 + self.h)).buffer(-0.01))
        body = max(K._polys_of(body), key=lambda g: g.area)
        return K.Part(body, K.fill(body, JADE), K.outline(body), {})

    def span(self, r, inset=0.0):
        """The angular range (a0, a1) of the circle of radius r about c0 that
        lies inside the dome (shrunk by ``inset`` px)."""
        th = np.linspace(150.0, 390.0, 2401)
        dome = self.dome.buffer(-inset) if inset else self.dome
        ins = [a for a in th if dome.contains(Point(*K.polar(self.c0, r, a)))]
        return (min(ins), max(ins)) if ins else (270.0, 270.0)

    def even(self, r, n, *, phase=0.0, inset=0.0, squeeze=0.0):
        """n petal angles spread over the visible span at radius r; ``phase``
        0.5 offsets them half a step (brick bond with the row below)."""
        a0, a1 = self.span(r, inset)
        w = np.linspace(1.0, 1.0 - squeeze, n + 1)
        cum = np.concatenate([[0.0], np.cumsum(w)])
        cum = cum / cum[-1]
        return [a0 + (a1 - a0) * (cum[k] + (cum[k + 1] - cum[k]) * (0.5 + phase - 0.5 * 0)) for k in range(n)] \
            if phase == 0.0 else [a0 + (a1 - a0) * cum[k + 1] for k in range(n)]

    @staticmethod
    def angles(a0, a1, n, squeeze=0.0):
        """n petal angles from a0 to a1, the steps shrinking by ``squeeze``
        toward a1 (the far side of a 3/4 head)."""
        w = np.linspace(1.0, 1.0 - squeeze, n)
        cum = np.concatenate([[0.0], np.cumsum((w[:-1] + w[1:]) / 2)]) if n > 1 else np.zeros(1)
        return list(a0 + (a1 - a0) * (cum / cum[-1] if n > 1 else 0.5))

    def row(self, r_tip, a0, a1, n, *, length=26.0, shoulder=0.5, bulge=0.14, hatch_side=+1, rib=True,
            hatch=True, squeeze=0.0, angs=None):
        """Petals with tips on radius ``r_tip`` about c0 at ``n`` angles from
        a0 to a1 (screen degrees: 270 = straight up); ``squeeze`` > 0 narrows
        the petals toward a1 (the far side of a 3/4 head). → Part."""
        c0 = self.c0
        if angs is None:
            angs = self.angles(a0, a1, n, squeeze)
        n = len(angs)
        petals, regs = [], []
        for k, a in enumerate(angs):
            if n > 1:
                da_l = (angs[k] - angs[k - 1]) if k > 0 else (angs[1] - angs[0])
                da_r = (angs[k + 1] - angs[k]) if k < n - 1 else (angs[-1] - angs[-2])
            else:
                da_l = da_r = 20.0
            tip = K.polar(c0, r_tip, a)
            r_sh = r_tip + length * shoulder
            sl = K.polar(c0, r_sh, a - da_l / 2)
            sr = K.polar(c0, r_sh, a + da_r / 2)
            d = ""
            for p_, q_, first in ((sl, tip, True), (tip, sr, False)):
                L = float(np.hypot(*(q_ - p_)))
                d += K.arc_sag(p_, q_, -bulge * L, move=first)
            pts = C.sample_d(d, 0.3)[0][0]
            far_l = K.polar(c0, r_tip + 400.0, a - da_l / 2)
            far_r = K.polar(c0, r_tip + 400.0, a + da_r / 2)
            poly = Polygon(np.vstack([[far_l], pts, [far_r]])).buffer(0)
            petals.append(dict(tip=tip, a=a, poly=poly, sl=sl, sr=sr))
            regs.append(poly)
        reg = shapely.union_all(regs).buffer(0.05).buffer(-0.05).intersection(self.shape)
        reg = reg.difference(K.R(K.circle(c0, self.R0 + self.h)).buffer(-0.01)) if r_tip >= self.R0 + self.h else reg
        fills = K.fill(reg, JADE)
        lines = K.outline(reg)
        for q in petals:
            poly = q["poly"].intersection(reg)
            if poly.is_empty or poly.area < 30:
                continue
            u = K.unit(q["a"])
            if rib:
                lines += K.clip_in(K.seg(q["tip"] + u * 5.5, q["tip"] + u * 300.0, FINE, role="midrib"),
                                   poly.buffer(-0.2))
            if hatch:
                half = poly.intersection(K.halfplane(q["tip"], q["tip"] + u * 10.0, side=hatch_side))
                lines += K.hatch_in(half, angle=q["a"] + 90.0, origin=tuple(q["tip"]))
        return K.Part(reg, fills, lines, {"petals": petals})


def pearl(c, d=18.0, hl=4.2):
    """The crown pearl: gold disc, Aquifer contour, a paper highlight knocked
    out of the gold, upper left (≥ 3 px from the rim)."""
    c = P(c)
    r = d / 2
    disc = K.R(K.circle(c, r))
    hole = K.R(K.circle(c + P(-r * 0.36, -r * 0.36), hl / 2))
    return K.Part(disc, K.fill(disc.difference(hole), GOLD), K.outline(disc), {"c": c})


def lock(guide, width, *, n=4, side=+1, end="round", bubbles=None, bubble_at=0.5, bubble_lane=None,
         color=GOLD, first=None, stagger=8.0, curl_r=4.2, curl_deg=75.0, taper=0.0, taper_from=0.4):
    """A lock of hair: a band ``width`` px wide whose OUTER edge is the arc
    spline through ``guide`` (root → free end), its free end rolled (a
    semicircle); ``side`` = which side of travel the body lies (+1 = screen
    left). ``n`` current lines follow the outer edge (8.4 inside it, 7 px
    pitch), rolling into Ø6.3 terminals. ``bubbles`` (diameters, smallest
    first): FINE rings threaded along lane ``bubble_lane`` (an offset from
    the outer edge, between two current lines), rising toward the root,
    their inside knocked out of the gold. → Part."""
    d, pts, _ = K.FM.arc_spline([P(q) for q in guide])
    pts = np.asarray(pts)
    cv = K.G.Curve(pts)
    if taper:
        # the lock narrows toward its free end: width × (1 − taper) at the end,
        # full width up to ``taper_from`` of the length (a smooth cosine run)
        pts = np.asarray(cv.resample(0.5))
        cv = K.G.Curve(pts)
        tg = np.gradient(pts, axis=0)
        tg = tg / np.hypot(tg[:, 0], tg[:, 1])[:, None]
        nl = np.column_stack([tg[:, 1], -tg[:, 0]])          # screen-left of travel
        u = np.linspace(0.0, 1.0, len(pts))
        v = np.clip((u - taper_from) / (1 - taper_from), 0.0, 1.0)
        wv = width * (1 - taper * (1 - np.cos(np.pi * v)) / 2)
        inner = pts + nl * (side * wv)[:, None]
        end_w = float(wv[-1])
    else:
        inner = np.asarray(cv.offset(side * width, spacing=0.5))
        end_w = width
    e0, e1 = pts[-1], inner[-1]
    cc = (e0 + e1) / 2
    t_ = pts[-1] - pts[-4]
    t_ = t_ / np.hypot(*t_)
    r = end_w / 2
    a0 = math.degrees(math.atan2(e0[1] - cc[1], e0[0] - cc[0]))
    a_mid = math.degrees(math.atan2(t_[1], t_[0]))
    cw = ((a_mid - a0) % 360) < 180
    a1 = K.unwrap(a0, a0 + (180 if cw else -180), cw)
    th = np.radians(np.linspace(a0, a1, 40))
    cap_pts = np.column_stack([cc[0] + r * np.cos(th), cc[1] + r * np.sin(th)])
    ring = np.vstack([pts, cap_pts[1:-1], inner[::-1]])
    reg = Polygon(ring).buffer(0)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.outline(reg)
    first = (CONTOUR / 2 + K.GAP + FINE / 2 + 0.05) if first is None else first
    offs = [first + K.PITCH * k for k in range(n)]
    holes, rings = [], C.Frag()
    if bubbles:
        k_ = bubble_lane                        # the lane runs between current lines k_-1 and k_
        dmax = max(bubbles)
        spread = 2 * (dmax / 2 + FINE / 2 + K.GAP_MARK + FINE / 2 + 0.3)
        shift = max(spread - K.PITCH, 0.0)
        offs = [o if k < k_ else o + shift for k, o in enumerate(offs)]
        lane = (offs[k_ - 1] + offs[k_]) / 2 if k_ > 0 else offs[0] - spread / 2
        mid = K.G.Curve(np.asarray(cv.offset(side * lane, spacing=0.5)))
        s_ = mid.length * bubble_at
        for dd in bubbles:
            c = mid.at_s(s_)
            holes.append(Point(*c).buffer(dd / 2, quad_segs=24))
            rings += C.stroke(K.circle(c, dd / 2), FINE, color=INK, role="bubble")
            s_ -= dd / 2 + 5.6 + dd * 0.6     # keeps ≥ 3 px clear between neighbouring rings
    ext = np.vstack([pts[:1] - (pts[1] - pts[0]) * 30, pts])
    placed = shapely.union_all(holes).buffer(FINE / 2) if holes else Polygon()
    for k, o in enumerate(offs):
        cl = K.current_lines(ext, 1, reg, side=side, first=o, edge=MEDIUM, stagger=0.0, placed=placed,
                             curl_r=curl_r, curl_deg=curl_deg)
        if cl.marks:
            placed = placed.union(cl.shape())
        lines += cl
    lines += rings
    gold = reg.difference(shapely.union_all(holes)) if holes else reg
    return K.Part(reg, K.fill(gold, color), lines, {"pts": pts, "inner": inner})


def fan_petals(cap, crown, r_tip, angs, *, widths=None, waist=0.62, root_w=8.0, bulge=0.16, front=None,
               hatch_side=None, rib=True, over=0.0):
    """Petals RADIATING from the crown point to tips on the circle r_tip about
    cap.c0 at the angles ``angs`` — a close cap of long overlapping petals
    (the petal swim cap seen from the front). Each petal: narrow at the
    crown (``root_w``), widest (``widths[k]``) at ``waist`` of its length,
    an ogive tip. Painter's order: from both ends toward the ``front`` index
    (drawn last, on top), so each petal overlaps its neighbour on the side
    away from the front. The half of each petal that is overlapped (toward
    the front petal's side) is hatched perpendicular to its axis.
    → list of (name, Part), back to front."""
    Cr = P(crown)
    n = len(angs)
    front = n // 2 if front is None else front
    order = list(range(0, front)) + list(range(n - 1, front, -1)) + [front]
    out = []
    for k in order:
        a = angs[k]
        tip = K.polar(cap.c0, r_tip, a)
        ax = tip - Cr
        L = float(np.hypot(*ax))
        u = ax / L
        nrm = np.array([u[1], -u[0]])            # screen-left of crown → tip
        w = widths[k] if widths is not None else 30.0
        # a vesica (the deck's leaf, two equal arcs) from behind the crown to the tip
        root = Cr - u * root_w
        reg = K.R(K.vesica(root, tip, w)).buffer(0)
        reg = reg.intersection(cap.dome.buffer(over))
        lines = K.outline(reg)
        if rib:
            lines += K.clip_in(K.seg(Cr + u * 14.0, tip - u * 6.0, FINE, role="midrib"), reg.buffer(-0.2))
        hs = hatch_side if hatch_side is not None else (+1 if k < front else -1)
        if k == front and hatch_side is None:
            hs = +1
        half = reg.intersection(K.halfplane(Cr, tip, side=hs)).difference(K.R(K.circle(Cr, 14.0)))
        lines += K.hatch_in(half, angle=math.degrees(math.atan2(u[1], u[0])) + 90.0, origin=tuple(tip))
        out.append((f"petal{k}", K.Part(reg, K.fill(reg, JADE), lines, {"tip": tip})))
    return out
