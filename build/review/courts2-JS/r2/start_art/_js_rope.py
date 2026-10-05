"""art/_js_rope.py — J♠'s rope coil (§H.3 'grips a rope coil over the
shoulder, drawn as a helix of diagonal FINE ticks'; colour map: Aquifer line
on paper).

The coil is a loop of rope — three turns bundled — slung on the viewer's
left shoulder: an elliptical annulus lying over the cape, the page's left
fist closed round its front. Each turn is a paper band between MEDIUM
edges carrying the helix: FINE ticks across the turn at a steady lay
angle, butting onto both edges (no free ends), staggered half a pitch
between neighbouring turns and laid greedily so they never crowd on the
inside of the coil's tight ends.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from dataclasses import replace
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from inkkit import geom as G

MEDIUM, FINE = K.MEDIUM, K.FINE


def _ellipse_pts(c, rx, ry, rot, a0=0.0, a1=360.0, n=720):
    t = np.radians(np.linspace(a0, a1, n))
    x, y = rx * np.cos(t), ry * np.sin(t)
    cr, sr = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return np.column_stack([c[0] + x * cr - y * sr, c[1] + x * sr + y * cr])


class CoilSpec:
    def __init__(self, c=(252.0, 404.0), rx=58.0, ry=76.0, rot=-8.0, strand=13.0, strands=2, lay=58.0, pitch=8.6):
        self.c = K.P(c)
        self.rx, self.ry, self.rot = rx, ry, rot     # the coil's centreline ellipse (mid of the bundle)
        self.strand = strand                          # one strand's width (edge centre to edge centre)
        self.strands = strands
        self.lay = lay                                # helix tick angle to the strand axis (deg)
        self.pitch = pitch


def coil(s: CoilSpec, visible=None):
    """→ Part: the bundle region (paper; its outer ring is the silhouette), the
    divisions between the coil's turns (MEDIUM) and the helix ticks (FINE).
    ``visible``: a region the coil is clipped to.

    Each tick crosses its turn at the lay angle and runs 1 px into both edge
    lines (butting, no free ends). The ticks of neighbouring turns are
    staggered by half a pitch so their ends never meet on a division line
    (§I.13: no line crosses another), and they are laid greedily: a tick
    that would come within 4.2 px of paper of a tick in its own turn, or
    3 px of one in the next (the inside of the coil's tight ends), is
    skipped, so the lay opens and closes with the curve instead of
    crowding."""
    W = s.strand * s.strands
    rings = []
    for k in range(s.strands + 1):
        off = -W / 2 + k * s.strand
        rings.append(_ellipse_pts(s.c, s.rx + off, s.ry + off, s.rot))
    outer = Polygon(rings[-1]).buffer(0)
    inner = Polygon(rings[0]).buffer(0)
    band = outer.difference(inner)
    if visible is not None:
        band = band.intersection(visible).buffer(0)
    lines = C.Frag()
    for k in range(1, s.strands):
        ln = LineString(np.vstack([rings[k], rings[k][:1]])).intersection(band.buffer(-0.5))
        for g in K._lines_of(ln):
            if g.length > 5:
                lines += K.line(np.asarray(g.coords), MEDIUM, role="strand")
    same_d = 4.2 + FINE
    near_d = 3.0 + FINE
    accepted = []                        # (strand, LineString)
    for k in range(s.strands):
        mid = _ellipse_pts(s.c, s.rx - W / 2 + (k + 0.5) * s.strand, s.ry - W / 2 + (k + 0.5) * s.strand, s.rot,
                           n=2880)
        cv = G.Curve(mid, True)
        L = cv.length
        lo = Polygon(rings[k]).buffer(-1.0)
        hi = Polygon(rings[k + 1]).buffer(1.0)
        strand_reg = hi.difference(lo).intersection(band.buffer(1.0))
        mine = []
        last_s = None
        for sv in np.arange((k % 2) * s.pitch / 2, L, 0.5):
            if last_s is not None and sv - last_s < s.pitch:
                continue
            p = cv.at_s(sv)
            p2 = cv.at_s(min(sv + 0.5, L - 1e-3))
            tng = (p2 - p) / max(np.hypot(*(p2 - p)), 1e-9)
            h = math.degrees(math.atan2(tng[1], tng[0]))
            u = K.unit(h + s.lay)
            seg = LineString([tuple(p - u * 25.0), tuple(p + u * 25.0)]).intersection(strand_reg)
            pieces = [g for g in K._lines_of(seg) if g.length > 3.0]
            if not pieces:
                continue
            g = min(pieces, key=lambda q: q.distance(Point(*p)))
            if mine and (g.distance(mine[-1]) < same_d or (sv > L - 4 * s.pitch and g.distance(mine[0]) < same_d)):
                continue
            if any(g.distance(o) < near_d for kk, o in accepted if abs(kk - k) == 1):
                continue
            mine.append(g)
            last_s = sv
        accepted += [(k, g) for g in mine]
    for _, g in accepted:
        lines += K.line(np.asarray(g.coords), FINE, style="hatch", role="lay")
    return K.Part(band, C.Frag(), lines + K.outline(band), {"rings": rings})


def drop_free_ticks(res: C.Frag, *, role="lay", zone=None, reach=None, min_len=4.2):
    """After the scene is composed and healed: keep a helix tick only where it
    still butts on ink at both ends. Heal cuts a tick back where its end nears
    a fill trapped under the coil's edge (or a finger's outline), which leaves
    a half tick hanging from one line in the middle of a strand, and crumbs of
    ticks between fingertip lobes; a tick is drawn whole or not at all, like
    the kit's ``atomic`` motifs. ``zone``: region the check is limited to
    (default: everywhere). → Frag."""
    reach = FINE / 2 + 0.9 if reach is None else reach
    others = []
    for m in res.marks:
        if m.kind != "stroke" or m.role == role or m.layer != "ink":
            continue
        for sub in C.sample_d(m.d, 0.6):
            p = np.asarray(sub[0], float)
            if len(p) < 2:
                continue
            ln = LineString(p)
            if zone is not None and not ln.intersects(zone):
                continue
            others.append(ln.buffer(m.w / 2, quad_segs=6))
    ink = shapely.union_all(others) if others else None
    out = C.Frag()
    for m in res.marks:
        if m.role != role or m.kind != "stroke":
            out += C.Frag([m])
            continue
        subs = [np.asarray(sub[0], float) for sub in C.sample_d(m.d, 0.5)]
        subs = [p for p in subs if len(p) >= 2]
        keep = []
        for p in subs:
            L = float(np.sum(np.hypot(*np.diff(p, axis=0).T)))
            if zone is not None and not LineString(p).intersects(zone):
                keep.append(p)
            elif L >= min_len and ink is not None and all(ink.distance(Point(*q)) <= reach for q in (p[0], p[-1])):
                keep.append(p)
        if len(keep) == len(subs):
            out += C.Frag([m])
        elif keep:
            # ticks are straight: each kept piece is its own end points
            d = "".join(f"M{p[0][0]:.3f} {p[0][1]:.3f}L{p[-1][0]:.3f} {p[-1][1]:.3f}" for p in keep)
            out += C.Frag([replace(m, d=d)])
    return out
