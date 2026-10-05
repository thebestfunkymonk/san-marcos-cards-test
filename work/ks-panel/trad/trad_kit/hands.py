"""§H.0 hands: mitten shapes, 3 finger lines and a separate thumb, closed
round cylindrical attributes. Open hands are avoided.

    fist(cx, cy, staff_w=18, side=+1)   fist round a vertical staff at x = cx
    cup(cx, cy, r, side=-1)             hand grasping a sphere from below

Each returns a dict of shapely shapes {"hand", "thumb"} plus "lines" (the
MEDIUM finger lines) so the caller stacks them in a Scene (hand, then the
thumb in front). ``side`` = +1: the wrist/back of the hand is on the
viewer's right (the fingertips curl round the staff's left edge); −1 mirrors.
Everything is built at +1 and mirrored about cx, so one drawing serves both
hands of every court.
"""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import Point, Polygon

from deck import tokens as T
from deck.motifs import core as MC
from deck.motifs.core import Frag

from . import shapes as SH


def _mir(g, cx, side):
    return g if side > 0 else SH.mirror_geom(g, cx)


def _mirf(f: Frag, cx, side):
    return f if side > 0 else f.mirror_x(cx)


def fist(cx: float, cy: float, *, staff_w: float = 18.0, fh: float = 10.0, side: int = 1,
         wrist=(14.0, 16.0), wrist_dir: float = 58.0):
    """Four stacked fingers wrap the FRONT of a vertical staff (x = cx); the
    fingertips curl round its far edge as four rounded knuckle-ends; the
    back of the hand swells toward ``side`` and runs into the wrist, which
    leaves at ``wrist_dir`` screen degrees (down-right for side +1).
    The thumb lies over the index finger, pointing across the staff."""
    n = 4
    h = n * fh
    y0 = cy - h / 2
    xl = cx - staff_w / 2 - 5.0            # fingertip column (bump centres)
    xr = cx + staff_w / 2 + 9.0            # knuckle ridge on the back side
    parts = []
    for k in range(n):
        yk = y0 + fh * (k + 0.5)
        inset = 0.0 if k < 3 else 2.5      # little finger a touch shorter
        seg_ = shapely.box(xl + inset, yk - fh / 2, xr, yk + fh / 2)
        tip = Point(xl + inset, yk).buffer(fh / 2 + 0.4, quad_segs=16)
        parts += [seg_, tip]
    fingers = shapely.union_all(parts)
    # back of the hand: from the knuckle ridge to the wrist
    a = np.radians(wrist_dir)
    u = np.array([np.cos(a), np.sin(a)])
    wc = np.array([xr + 6.0, cy + h / 2 + 4.0]) + u * 10.0      # wrist centre
    nrm = np.array([-u[1], u[0]])
    ww = wrist[0]
    back = Polygon([(xr - 8, y0 + 1), (xr + 7, y0 + 5), (xr + 13, cy),
                    tuple(wc + nrm * ww / 2 * -1 + u * 0), tuple(wc + nrm * ww / 2),
                    (xr - 8, y0 + h - 1)])
    back = back.buffer(3.5, quad_segs=12).buffer(-3.5, quad_segs=12)
    wristp = SH.ribbon(np.vstack([wc - u * 8, wc + u * wrist[1]]), ww, ww + 1, cap1="flat")
    hand = shapely.union_all([fingers, back, wristp])
    hand = hand.buffer(1.2, quad_segs=12).buffer(-1.2, quad_segs=12)
    # thumb: a lobe from the back of the hand across the index finger
    g = SH.spline([(xr + 7, y0 + 11), (xr - 4, y0 + 5.5), (cx + 1, y0 + 3.2), (cx - 5, y0 + 4.2)])
    thumb = SH.ribbon(g, 11.5, 8.8, cap1="round", cap0="round")
    # finger lines: between the fingers, from the fingertip notch to the knuckles
    lines = Frag()
    for k in range(1, n):
        y = y0 + fh * k
        lines += MC.stroke(SH.seg((xl + 1.5, y), (xr - 1.0, y)), T.MEDIUM)
    return {"hand": _mir(hand, cx, side), "thumb": _mir(thumb, cx, side),
            "lines": _mirf(lines, cx, side), "wrist": (tuple(wc + u * wrist[1]) if side > 0 else
                                                     (2 * cx - (wc + u * wrist[1])[0], (wc + u * wrist[1])[1]))}


def cup(cx: float, cy: float, r: float, *, side: int = -1, fw: float = 11.0, grip: float = 0.55,
        wrist_dir: float = 120.0, wrist=(15.0, 18.0)):
    """A hand grasping a sphere (centre cx, cy; radius r) from below, the
    back of the hand to the viewer: four fingertips curl up over the
    sphere's lower front (bumps on an arc at ``grip``·r below the centre),
    the knuckles and back of the hand below, the wrist leaving toward the
    ``side`` at ``wrist_dir`` screen degrees. The thumb rises along the
    sphere's inner edge (−side). Built for side −1 (wrist on the left)."""
    s = -side                                  # build as side -1, then mirror
    n = 4
    ytip = cy + grip * r                       # fingertip arc
    xs = cx + (np.arange(n) - (n - 1) / 2) * fw
    parts = []
    y_kn = cy + r + 8.0                        # knuckle line (below the sphere)
    for k, x in enumerate(xs):
        dy = abs(x - cx) * 0.18                # the tips follow the sphere's curve
        tip = Point(x, ytip + dy).buffer(fw / 2 + 0.3, quad_segs=16)
        body = shapely.box(x - fw / 2, ytip + dy, x + fw / 2, y_kn + 6)
        parts += [tip, body]
    fingers = shapely.union_all(parts)
    a = np.radians(wrist_dir)
    u = np.array([np.cos(a), np.sin(a)])
    left, right = xs[0] - fw / 2, xs[-1] + fw / 2
    wc = np.array([cx - 6, y_kn + 14]) + u * 6
    back = Polygon([(left, y_kn - 6), (right, y_kn - 6), (right + 1, y_kn + 6),
                    (cx + 6, y_kn + 16), tuple(wc + np.array([u[1], -u[0]]) * wrist[0] / 2),
                    tuple(wc - np.array([u[1], -u[0]]) * wrist[0] / 2), (left - 1, y_kn + 2)])
    back = back.buffer(4, quad_segs=12).buffer(-4, quad_segs=12)
    wristp = SH.ribbon(np.vstack([wc - u * 6, wc + u * wrist[1]]), wrist[0], wrist[0] + 1, cap1="flat")
    hand = shapely.union_all([fingers, back, wristp]).buffer(1.2, quad_segs=12).buffer(-1.2, quad_segs=12)
    # thumb up the sphere's inner (right, for side -1) edge
    g = SH.spline([(right - 2, y_kn - 4), (cx + r * 0.80, cy + r * 0.56), (cx + r * 0.93, cy + r * 0.22),
                   (cx + r * 0.90, cy - r * 0.06)])
    thumb = SH.ribbon(g, 11.0, 8.8, cap0="round", cap1="round")
    lines = Frag()
    for k in range(1, n):
        x = (xs[k - 1] + xs[k]) / 2
        dy = abs(x - cx) * 0.18
        lines += MC.stroke(SH.seg((x, ytip + dy + 1.0), (x, y_kn - 3.0)), T.MEDIUM)
    out = {"hand": hand, "thumb": thumb, "lines": lines, "wrist": tuple(wc + u * wrist[1])}
    if s < 0:   # requested side +1: mirror
        out = {"hand": SH.mirror_geom(hand, cx), "thumb": SH.mirror_geom(thumb, cx),
               "lines": lines.mirror_x(cx), "wrist": (2 * cx - out["wrist"][0], out["wrist"][1])}
    return out
