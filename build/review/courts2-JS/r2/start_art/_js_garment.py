"""art/_js_garment.py — J♠'s doublet, sleeves, belt and livery collar (§H.3):

* the DOUBLET, Spring Jade, with fault-line stepped chevrons knocked out to
  paper: heraldic chevron rows (apex up) broken by a plain placket at the
  centre front, the right half dropped one course across it — the fault,
  exactly as the ♠ divider and the K♠ strata step across the Balcones fault;
* plain jade puffed upper SLEEVES;
* the BELT, gold, set with karst-void rings (§G.12) in Aquifer FINE, and its
  buckle;
* the LIVERY collar the Lion Mark badge hangs from: graduated gold pearls
  (§G.29), solid with Aquifer contours (legal on the red cape, §C.4).
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import geometric as MG

MEDIUM, FINE, CONTOUR = K.MEDIUM, K.FINE, K.CONTOUR


def chevrons(region, xc, *, y_top=300.0, y_bot=560.0, pitch=24.0, slope_deg=24.0, faults=(-62.0, 0.0, 62.0, 124.0),
             step=7.0, w=MEDIUM, up=False):
    """Chevron rows (V's opening upward, straight arms) clipped to ``region``,
    cut by vertical FAULTS at x = xc + each of ``faults``: across every fault
    the pattern on the right drops one course (``step``), joined by a riser on
    the fault — the Balcones fault zone stepping down to the coast, as the ♠
    divider and the K♠ strata step. → Frag of MEDIUM strokes (miter joins,
    butt caps: §B.2 fault-steps)."""
    reg = K.R(region)
    f = C.Frag()
    t = math.tan(math.radians(slope_deg))
    fx = sorted(xc + d for d in faults)
    x0, x1 = xc - 360.0, xc + 360.0

    def drop(x):
        return step * sum(1 for q in fx if x > q + 1e-6)

    y = y_top
    while y < y_bot:
        pts = []
        xs = [x0] + fx + [x1]
        for a, b in zip(xs[:-1], xs[1:]):
            for xx in (a, b):
                yy = y + abs(xx - xc) * (t if up else -t) + drop((a + b) / 2)
                pts.append((xx, yy))
        ln = LineString(pts).intersection(reg)
        for g in K._lines_of(shapely.line_merge(ln) if ln.geom_type == "MultiLineString" else ln):
            if g.length > 6.0:
                f += C.stroke(np.asarray(g.coords), w, style="rule", role="chevron")
        y += pitch
    return f


def doublet(shape, xc, *, border=9.0, color=K.JADE, placket=0.0, front=None, pocket=80.0, **kw):
    """The doublet: ``shape`` filled jade with the chevrons knocked out inside
    a plain border (and outside a plain ``placket`` strip ± px about the
    centre front, where the chevrons step across the fault). ``front``: the
    parts stacked over the doublet — the small pockets of it they leave
    visible (< ``pocket`` px², e.g. between the rope coil, the belt and the
    doublet's edge) stay plain jade, never a stray fleck of a chevron. → Part."""
    inner = shape.buffer(-border, quad_segs=12)
    if front is not None:
        vis = shape.difference(front)
        small = [g for g in K._polys_of(vis) if g.area < pocket]
        if small:
            inner = inner.difference(shapely.union_all(small).buffer(1.5, quad_segs=8))
    if placket:
        inner = inner.difference(K.box(xc - placket, 0, xc + placket, 2000))
    chev = chevrons(inner, xc, **kw)
    fill_d = C.knockout(K.D(shape), chev) if chev else K.D(shape)
    return K.Part(shape, K.fill(fill_d, color), K.outline(shape), {"inner": inner, "chev": chev})


def belt(torso_shape, y0, y1, *, color=K.GOLD, voids=(16.0, 6.0, 10.0, 6.0), gap=5.0, xc=None):
    """A gold belt band y0–y1 across the torso, set with a running row of
    karst-void rings (Aquifer FINE) on its centre line. → Part."""
    band = torso_shape.intersection(K.box(0, y0, 2000, y1)).buffer(0)
    band = max(K._polys_of(band), key=lambda p: p.area)
    lines = K.outline(band)
    x0, _, x1, _ = band.bounds
    ym = (y0 + y1) / 2
    room = band.buffer(-(MEDIUM / 2 + K.GAP_MARK + FINE / 2))
    xs = []
    x = (x0 + x1) / 2 if xc is None else xc
    # lay voids outward from the centre both ways (the row reads symmetric at the buckle)
    seq = list(voids)
    out = C.Frag()
    placed = []
    for sgn in (+1, -1):
        k = 0
        xx = x if sgn > 0 else x - (MG.KARST_ASPECT * seq[0] / 2 + gap + MG.KARST_ASPECT * seq[-1] / 2)
        kk = 0 if sgn > 0 else len(seq) - 1
        while x0 < xx < x1:
            d = seq[kk % len(seq)]
            rx = MG.KARST_ASPECT * d / 2
            ell = shapely.affinity.scale(Point(xx, ym).buffer(1.0, quad_segs=32), rx + FINE / 2, d / 2 + FINE / 2)
            if room.contains(ell):
                out += K.atomic(MG.karst_void(xx, ym, d), f"belt{sgn}{k}")
            nd = seq[(kk + sgn) % len(seq)]
            xx += sgn * (rx + gap + FINE + MG.KARST_ASPECT * nd / 2)
            kk += sgn
            k += 1
    return K.Part(band, K.fill(band, color), lines + out, {"band": band})


def buckle(c, w=34.0, h=46.0, *, color=K.GOLD):
    """The belt's buckle, a gold clasp (§C.1): a rounded frame with its
    opening (an Aquifer MEDIUM inner frame) and the tongue bar across it."""
    c = K.P(c)
    outer = K.R(K.rrect(c[0] - w / 2, c[1] - h / 2, c[0] + w / 2, c[1] + h / 2, 7.0))
    iw, ih = w - 16.0, h - 18.0
    inner_d = K.rrect(c[0] - iw / 2, c[1] - ih / 2, c[0] + iw / 2, c[1] + ih / 2, 3.5)
    lines = K.outline(outer) + K.outline(inner_d, MEDIUM, role="buckle")
    lines += K.seg((c[0], c[1] - ih / 2), (c[0], c[1] + ih / 2), MEDIUM, role="tongue")
    return K.Part(outer, K.fill(outer, color), lines, {})


def sleeve_part(region, *, color=K.JADE, folds=()):
    """A plain puffed upper sleeve: the region filled ``color`` with optional
    MEDIUM fold lines (d-strings / point lists) clipped inside it. → Part."""
    reg = K.R(region)
    lines = K.outline(reg)
    for fd in folds:
        d = fd if isinstance(fd, str) else C.polyline_d(np.asarray(fd, float))
        lines += K.clip_in(K.line(d, MEDIUM, role="fold"), reg.buffer(-0.5))
    return K.Part(reg, K.fill(reg, color), lines, {})


def livery(points, *, d=(7.0, 10.5), gap=3.4, keep=None, skip=None, color=K.GOLD, links=(13.0, 7.0), small=0.0):
    """A gold livery collar along the open spline through ``points``: round
    beads (§G.29 pearl beading, graduated, largest at the pendant) between
    lozenge links (``links`` = length, width, laid along the chain) — each a
    SOLID gold shape with a FINE Aquifer contour (legal on red, §C.4), 3.4 px
    of ground between neighbours. Pieces not wholly inside ``keep`` or
    touching ``skip`` are dropped whole. → Part."""
    from art import _js_util as U
    _, pts = U.open_spline(points)
    cv = K.G.Curve(pts)
    L = cv.length
    ys = pts[:, 1]
    s_low = float(np.argmax(ys)) / (len(ys) - 1) * L
    d0, d1 = d
    ll, lw = links if links else (0.0, 0.0)
    pieces = []
    s = 0.0
    k = 0
    while s < L:
        t = 1.0 - min(1.0, abs(s - s_low) / max(s_low, L - s_low))
        if links and k % 2 == 1:
            size = ll
            pieces.append(("lz", s + size / 2, size))
        elif small and k % 2 == 1:
            size = small
            pieces.append(("bd", s + size / 2, size))
        else:
            size = d0 + (d1 - d0) * t ** 1.5
            pieces.append(("bd", s + size / 2, size))
        s += size + gap + K.FINE
        k += 1
    f = C.Frag()
    shp = []
    for i, (kind, sb, size) in enumerate(pieces):
        if sb + size / 2 > L:
            break
        p = cv.at_s(sb)
        if kind == "bd":
            g = Point(*p).buffer(size / 2, quad_segs=24)
        else:
            p0, p1 = cv.at_s(sb - size / 2), cv.at_s(sb + size / 2)
            rot = math.degrees(math.atan2(p1[1] - p0[1], p1[0] - p0[0]))
            g = K.R(C.lozenge_d(p[0], p[1], size, lw, rot))
        if keep is not None and not keep.contains(g.buffer(K.FINE / 2 + 3.0)):
            continue
        if skip is not None and g.buffer(K.FINE / 2 + 3.0).intersects(skip):
            continue
        f += K.atomic(K.fill(g, color, role="bead") + K.outline(g, K.FINE, role="bead"), f"bead{i}")
        shp.append(g.buffer(K.FINE / 2))
    shape = shapely.union_all(shp) if shp else Polygon()
    return K.Part(shape, C.Frag(), f, {})
