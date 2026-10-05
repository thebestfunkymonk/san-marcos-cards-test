"""TUCK-FLAT: every panel placed on a STANDARD poker reverse-tuck-end dieline.

    >>> THE PRINTER'S DIELINE MUST REPLACE THIS ONE. <<<
    This is a generic 2.5625 x 3.5625 x 0.75 in reverse-tuck-end layout for
    proofing (panel sizes from brief §B.1); flap depths, glue-flap taper,
    thumb-notch radius and lock details vary by printer (MPC, USPCC, ...).
    Re-place the panels on the printer's own dieline before final layout.

Layout (outside face up, px @ 300 ppi, origin = top-left of the dieline's
box, bleed 37.5 px beyond it):

    columns   SIDE B | FRONT | SIDE A | BACK | glue flap
    x         0-225  | 225-994 | 994-1219 | 1219-1988 | 1988-2138
    rows      tuck flap 0-180 and TOP END 180-405 above the FRONT (the lid,
              hinged on the front's top edge, so the front stays whole)
              body 405-1474
              BOTTOM END 1474-1699 and its tuck flap 1699-1879 below the BACK
              dust flaps (150 deep) above and below both sides

Panel placement is rigid only (translate; the BOTTOM END, hinged on the back,
is rotated 180° so it reads with the front up once folded).  The lid's flap
tucks in behind the BACK, whose top edge carries the thumb notch (and where
the seal crosses the closure).  Plates: board (Deep Hole, + 37.5 bleed), emboss (tooling,
non-printing), foil (the one gold foil), dieline (non-printing registration
magenta: cut = solid, fold = dashed; plus the Side-B HOLD note).
"""
from __future__ import annotations

import shapely
from shapely.geometry import Polygon, box

from deck import tokens as T
from deck.motifs import core as C
from inkkit import geom as G
from inkkit.svg import fmt

from tuck import _tuck_common as K

PW, PH, D = K.PW, K.PH, K.DEPTH
TUCK_FLAP = 180.0
DUST = 150.0
GLUE = 150.0
NOTCH_R = K.NOTCH_R

X_SB, X_FR, X_SA, X_BK, X_GL = 0.0, D, D + PW, 2 * D + PW, 2 * D + 2 * PW
X_END = X_GL + GLUE
Y_TF, Y_TOP, Y_BODY = 0.0, TUCK_FLAP, TUCK_FLAP + D
Y_BOT = Y_BODY + PH
Y_BTF = Y_BOT + D
Y_END = Y_BTF + TUCK_FLAP
W_FLAT, H_FLAT = X_END, Y_END

# panel origins (top-left, in flat coords) and rotation about the panel centre
PLACES = dict(front=(X_FR, Y_BODY, 0), side_a=(X_SA, Y_BODY, 0), back=(X_BK, Y_BODY, 0), side_b=(X_SB, Y_BODY, 0),
              top=(X_FR, Y_TOP, 0), bottom=(X_BK, Y_BOT, 180))
SIZES = dict(front=(PW, PH), back=(PW, PH), side_a=(D, PH), side_b=(D, PH), top=(PW, D), bottom=(PW, D))


def place(f: C.Frag, name: str) -> C.Frag:
    x, y, rot = PLACES[name]
    w, h = SIZES[name]
    if rot:
        f = f.rotate(rot, w / 2, h / 2)
    return f.translate(x, y)


def place_d(d: str, name: str) -> str:
    x, y, rot = PLACES[name]
    w, h = SIZES[name]
    if rot:
        d = G.rotate(d, rot, w / 2, h / 2)
    return G.translate(d, x, y)


def _tuck_flap(x0, x1, y_hinge, depth, up=True):
    """A lid's tuck flap: slight 12 px shoulders, rounded far corners."""
    s = -1 if up else 1
    yf = y_hinge + s * depth
    sh = 12.0
    p = Polygon([(x0, y_hinge), (x0 + sh, y_hinge + s * 22), (x0 + sh, yf), (x1 - sh, yf),
                 (x1 - sh, y_hinge + s * 22), (x1, y_hinge)])
    r = 45.0
    return p.buffer(-r, join_style="round").buffer(r, join_style="round").union(
        box(x0, min(y_hinge, y_hinge + s * 30), x1, max(y_hinge, y_hinge + s * 30)))


def outline():
    """The cut outline (shapely Polygon) of the whole blank."""
    parts = [box(X_SB, Y_BODY, X_GL, Y_BOT)]
    # glue flap, tapered
    parts.append(Polygon([(X_GL, Y_BODY), (X_END, Y_BODY + 40), (X_END, Y_BOT - 40), (X_GL, Y_BOT)]))
    # lid on the FRONT: top end + tuck flap
    parts.append(box(X_FR, Y_TOP, X_FR + PW, Y_BODY))
    parts.append(_tuck_flap(X_FR, X_FR + PW, Y_TOP, TUCK_FLAP, up=True))
    # bottom end + tuck flap on the BACK
    parts.append(box(X_BK, Y_BOT, X_BK + PW, Y_BTF))
    parts.append(_tuck_flap(X_BK, X_BK + PW, Y_BTF, TUCK_FLAP, up=False))
    # dust flaps on both sides, top and bottom (tapered toward the lid's hinge side)
    for xs in (X_SB, X_SA):
        parts.append(Polygon([(xs, Y_BODY), (xs + 8, Y_BODY - DUST), (xs + D - 60, Y_BODY - DUST), (xs + D, Y_BODY - 40),
                              (xs + D, Y_BODY)]))
        parts.append(Polygon([(xs, Y_BOT), (xs + 8, Y_BOT + DUST), (xs + D - 60, Y_BOT + DUST), (xs + D, Y_BOT + 40),
                              (xs + D, Y_BOT)]))
    blank = shapely.union_all(parts)
    notch = shapely.Point(X_BK + PW / 2, Y_BODY).buffer(NOTCH_R, quad_segs=64)
    return blank.difference(notch)


def folds():
    """Fold segments [(p, q), ...]."""
    s = []
    for x in (X_FR, X_SA, X_BK, X_GL):
        s.append(((x, Y_BODY), (x, Y_BOT)))
    s.append(((X_FR, Y_BODY), (X_FR + PW, Y_BODY)))           # lid hinge (front)
    s.append(((X_FR, Y_TOP), (X_FR + PW, Y_TOP)))             # tuck flap hinge (lid)
    s.append(((X_BK, Y_BOT), (X_BK + PW, Y_BOT)))             # bottom end hinge (back)
    s.append(((X_BK, Y_BTF), (X_BK + PW, Y_BTF)))             # bottom tuck flap hinge
    for xs in (X_SB, X_SA):
        s.append(((xs, Y_BODY), (xs + D, Y_BODY)))
        s.append(((xs, Y_BOT), (xs + D, Y_BOT)))
    return s


def dieline_svg(note_d: str = "", note_box=None) -> str:
    ol = outline()
    cut = G.from_shape(ol)
    parts = [f'<path d="{cut}" fill="none" stroke="{K.DIE_REG}" stroke-width="{T.HAIRLINE}" '
             f'stroke-linejoin="miter" data-line="cut"/>']
    fd = "".join(f"M{fmt(p[0])} {fmt(p[1])}L{fmt(q[0])} {fmt(q[1])}" for p, q in folds())
    parts.append(f'<path d="{fd}" fill="none" stroke="{K.DIE_REG}" stroke-width="{T.HAIRLINE}" '
                 f'stroke-dasharray="12 8" data-line="fold"/>')
    if note_box is not None:
        x0, y0, x1, y1 = note_box
        parts.append(f'<path d="{G.rect_d(x0, y0, x1 - x0, y1 - y0)}" fill="none" stroke="{K.DIE_REG}" '
                     f'stroke-width="{T.HAIRLINE}" stroke-dasharray="6 5" data-note="hold"/>')
    if note_d:
        parts.append(f'<path d="{note_d}" fill="{K.DIE_REG}" data-note="hold (non-printing)"/>')
    return "".join(parts)


def board_d() -> str:
    return G.from_shape(outline().buffer(K.BLEED, join_style="mitre", mitre_limit=4.0))


def build(front, back, panels):
    """front/back: their build() dicts; panels: _tuck_panels.build().
    -> dict(foil=Frag, emboss=[(d, level)], note=(d, box))."""
    from tuck import _tuck_panels as TP
    foil = place(front["foil"], "front") + place(back["foil"], "back")
    for k in ("side_a", "side_b", "top", "bottom"):
        foil += place(panels[k], k)
    emboss = [(place_d(d, "front"), lv) for d, lv in front["emboss"]]
    emboss += [(place_d(d, "back"), lv) for d, lv in back["emboss"]]
    # the HOLD note beside the acknowledgment on side B (non-printing)
    ax0, ay0, ax1, ay1 = panels["ack_bb"]
    bx = (ax0 - 6 + X_SB, ay0 - 8 + Y_BODY, ax1 + 6 + X_SB, ay1 + 8 + Y_BODY)
    note_d = TP.hold_note_d(X_SB + 17.0, Y_BODY + PH / 2)            # side B's outer margin (non-printing)
    return dict(foil=foil, emboss=emboss, note=(note_d, bx))


def svg(res) -> str:
    notes = ["HEADWATERS tuck FLAT on a STANDARD poker reverse-tuck-end dieline (2.5625 x 3.5625 x 0.75 in),",
             "px @300 ppi. THE PRINTER'S DIELINE MUST REPLACE THIS ONE before final layout.",
             "Plates: board = Deep Hole stock + 37.5 px bleed (not printed); emboss = blind-emboss tooling",
             "(non-printing); foil = ONE gold foil (flat Lion Gold #B08D57); dieline = cut (solid) / fold (dashed),",
             "registration magenta, non-printing.",
             "HOLD: the side-B acknowledgment line is pending Indigenous Cultures Institute review - do not print",
             "it until approved (see the magenta note on side B)."]
    B = K.BLEED
    return K.svg_doc(W_FLAT, H_FLAT, board=board_d(), emboss=res["emboss"], foil=K.foil_svg(res["foil"]),
                     dieline=dieline_svg(*res["note"]), view=(-B, -B, W_FLAT + 2 * B, H_FLAT + 2 * B),
                     title="HEADWATERS tuck flat (standard dieline - replace with the printer's)", notes=notes)
