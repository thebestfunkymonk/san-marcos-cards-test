"""art/_qd_hair.py — Q♦'s hair and bare skin: the swept gold hair (cap and
long tresses, §G.24 current lines), the neck with the spring of the
shoulders, and the pearl choker. Built on deck.courtkit; art/QD.py stacks
them."""
from __future__ import annotations


import numpy as np
from shapely.geometry import Point, Polygon

from deck import courtkit as K
from inkkit import geom as G
from deck.motifs import core as C

P, R, U, D = K.P, K.R, K.U, K.D
FINE, MEDIUM, CONTOUR = K.FINE, K.MEDIUM, K.CONTOUR
GOLD, INK = K.GOLD, K.INK


def sp(points, h_start=None, h_end=None, step=0.5):
    """Dense points of the kit's G1 arc spline."""
    return C.sample_d(K.spline(list(points), h_start, h_end), step)[0][0]


def smooth(p, step=1.0, win=9):
    """Resample a polyline evenly and smooth it (moving average): a clean
    guide for current lines — G.Curve.offset leaves micro-loops on some
    arc-spline guides at offsets > 20 px, which fragment the lines."""
    q = G.Curve(np.asarray(p, float)).resample(step)
    k = np.ones(win) / win
    x = np.convolve(np.pad(q[:, 0], win // 2, mode="edge"), k, mode="valid")
    y = np.convolve(np.pad(q[:, 1], win // 2, mode="edge"), k, mode="valid")
    return np.column_stack([x, y])


def neck_chest(axis=380.0, *, top=236.0, hw=14.5, base_y=286.0, shoulder=(346.0, 420.0), spring_y=300.0,
               bottom=380.0, lean=0.0) -> K.Part:
    """Bare skin: the neck column (a slender taper under the jaw) springing
    at its base into the shoulders — each side a tangent arc out to the
    cape's inner edge — and the chest down under the gown's neckline. Paper
    is never painted: the Part only hides what is behind it and draws the
    neck's two MEDIUM side lines."""
    xl, xr = axis - hw, axis + hw
    sl, sr = shoulder
    left = K.Path((xl + 1.0 + lean, top)).line((xl, base_y)).arc3((xl - 5.0, base_y + 9.5), (sl, spring_y))
    right = K.Path((xr - 1.0 + lean, top)).line((xr, base_y)).arc3((xr + 5.0, base_y + 9.5), (sr, spring_y))
    lp = C.sample_d(left.d, 0.5)[0][0]
    rp = C.sample_d(right.d, 0.5)[0][0]
    reg = Polygon(np.vstack([lp, [[sl - 4.0, spring_y + 2.0], [sl - 4.0, bottom], [sr + 4.0, bottom],
                                  [sr + 4.0, spring_y + 2.0]], rp[::-1]])).buffer(0)
    lines = K.line(left.d, MEDIUM, role="neck") + K.line(right.d, MEDIUM, role="neck")
    return K.Part(reg, C.Frag(), lines, {"left": lp, "right": rp})


# =============================================================================
# hair dressed up: the ear, the swept mass with its knot, the earring
# =============================================================================


def earring(top, *, bead=6.3, drop=(12.0, 8.4), gap=0.0, color=GOLD) -> K.Part:
    """A gold earring: a bead at the lobe and a ♦ lozenge drop hanging from
    it (the house mark), both solid gold with Aquifer contours."""
    top = P(top)
    b = Point(*top).buffer(bead / 2, quad_segs=16)
    L, W = drop
    dc = top + P(0.0, bead / 2 + L / 2 - 1.0 + gap)
    lz = R(C.lozenge_d(dc[0], dc[1], L, W, 90.0))
    shape = U(b, lz)
    lines = K.outline(b) + C.stroke(D(lz), MEDIUM, style="point", role="drop")
    lines = K.clip_out(K.outline(lz, MEDIUM), b, eps=-0.5, trap=0.0) if False else lines
    return K.Part(shape, K.fill(shape, color), K.outline(shape), {})


def mane(*, outer, inner, n=4, stagger=0.0, color=GOLD, band=None, first=None, curl_deg=80.0) -> K.Part:
    """Long hair falling BEHIND the head, the neck and the cape (the kit's
    convention: the face egg is in front of its hair): the region between
    the visible ``outer`` contour (root under the diadem → round the back
    of the skull → down the back, into the cape) and a hidden ``inner``
    edge (behind the face and neck). Current lines (§G.24) run parallel to
    the outer contour and pass under the cape (the long hair continues)."""
    po = sp(outer)
    pi = sp(inner)
    reg = Polygon(np.vstack([po, pi[::-1]])).buffer(0)
    if reg.geom_type != "Polygon":
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    if band is not None:
        reg = reg.difference(band)
        reg = max(K._polys_of(reg), key=lambda g: g.area)
    fl = K.current_lines(smooth(po), n, reg, side=+1, edge=CONTOUR, stagger=stagger, curl_deg=curl_deg,
                         first=first)
    return K.Part(reg, K.fill(reg, color), fl + K.outline(reg), {"outer": po})


def ear2(top, mid, bot, *, face, inner=None) -> K.Part:
    """The near ear of a 3/4 head, §H.0 'a C': the lune between the face
    contour and one C arc from ``top`` (on the temple) out through ``mid``
    (the back of the helix) to ``bot`` (the lobe, on the jaw). Paper; the C
    is its outline. ``inner``: three points of a short MEDIUM inner fold."""
    arc = C.sample_d(K.arc3(P(top), P(mid), P(bot)), 0.4)[0][0]
    reg = Polygon(np.vstack([arc, [P(bot) + P(12.0, 0.0), P(top) + P(12.0, 0.0)]])).buffer(0)
    reg = reg.difference(face)
    reg = max(K._polys_of(reg), key=lambda g: g.area)
    lines = K.outline(reg)
    if inner is not None:
        lines += K.line(K.arc3(*[P(q) for q in inner]), MEDIUM, role="ear")
    return K.Part(reg, C.Frag(), lines, {"lobe": P(bot)})
