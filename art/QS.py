"""art/QS.py — Q♠ · The Blind Oracle (creative brief §H.2): continuous double-head, two cloak-sleeve hands.

Whole-card textiles (art/_qs_garments.py): the jade barrel mantle with its hatched border and karst
voids, the red lining lens with its water-drop columns, the paper gown and the two sleeves are C2
about the card centre, so the seam (SEAM, a gentle diagonal through the robes) is only a place where
the 180° copy takes over — no band, medallion or divider.

Hands (both ``K.hand5``, back view, posed by parameters):
  * the oracle's LEFT hand (viewer's right) wraps the scrying mirror's handle, thumb up the shaft;
  * the oracle's RIGHT hand (viewer's left) wraps the mountain-laurel posy-holder, thumb up.
Each wrist continues a short jade sleeve that opens from the mantle's outer edge; its cuff is a red
turn-back band with the §H.2 drip fringe hanging from it.
"""
from __future__ import annotations

import math
from dataclasses import replace

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon
from shapely.prepared import prep

from inkkit import geom as G

from deck import courtkit as K
from deck import frames as F
from deck import tokens as T
from deck.motifs import core as C
from art import _qs_parts as Q
from art import _qs_face as QF
from art import _qs_body as B
from art import _qs_garments as QG
from art import _qs_sal as QSAL

DOUBLE_HEAD = "continuous"
SEAM = -10.0
P = K.P
HAND_SCALE = 0.82

HEAD = (388.0, 200.0)
TILT, PIVOT = -6.0, (388.0, 292.0)

# ---- head group (drawn upright, then inclined TILT about PIVOT) --------------------
VEIL = [(300, 350), (306, 300), (314, 250), (322, 206), (336, 168), (358, 142), (392, 128), (428, 134),
        (456, 152), (474, 184), (486, 226), (496, 282), (508, 350), (404, 372)]
VEIL_HEM = [(270, 222), (330, 210), (350, 206), (388, 196), (426, 194), (452, 198), (474, 206), (520, 222)]
# sparse contour lines (§H.2): offsets of the veil's edge, far temple -> over the crown -> near foot
VEIL_GUIDE = [(326, 196), (336, 168), (358, 142), (392, 128), (428, 134), (456, 152), (474, 184), (486, 226),
              (496, 282), (504, 330)]
CIRCLET = ((324.0, 152.0), (378.0, 156.0), (484.0, 142.0))
VEIL_IN = 10.0      # the veil's inner contour: the crown guide offset this far inward (the circlet ends on it)
# nine graduated points hung from the circlet between the far contour and its
# round end on the veil's inner contour; packed so the kites' outlines join at
# the shoulders (a closed zigzag, no hairline paper slits)
KITES = dict(xs=(347.0, 356.7, 367.1, 378.7, 390.9, 402.5, 413.4, 423.8, 433.5),
             lengths=(13.0, 16.0, 21.0, 31.0, 24.0, 20.0, 17.0, 14.5, 12.0),
             widths=(6.6, 7.2, 7.9, 9.7, 9.2, 8.4, 7.9, 7.2, 6.6), top_k=0.25, axis_min=99.0)
# hair: two locks filling the veil's face opening (outer edge = the veil's front
# edge), falling out of it in front of the shoulders to rolled ends
HAIR_F_OUT = [(342, 176), (328, 222), (324, 266), (325, 312), (319, 362), (309, 400)]
HAIR_F_IN = [(364, 176), (358, 222), (366, 266), (369, 304), (365, 350), (356, 396)]
HAIR_N_OUT = [(448, 170), (466, 214), (476, 262), (481, 316), (492, 366), (502, 406)]
HAIR_N_IN = [(420, 170), (412, 222), (400, 266), (404, 304), (426, 352), (446, 396)]

# ---- ruff: six gill plumes, root -> tip, sag, feathered side, width (back to front) --
PLUMES = [
    ((352, 262), (262, 186), 12.0, -1, 46.0), ((426, 262), (538, 178), -12.0, +1, 48.0),
    ((348, 280), (222, 242), 12.0, -1, 48.0), ((430, 280), (574, 236), -12.0, +1, 50.0),
    ((346, 298), (204, 302), 10.0, -1, 46.0), ((432, 298), (590, 296), -10.0, +1, 48.0),
]

# ---- the mirror (viewer's right) and the posy-holder (viewer's left) -------------------
MIRROR_C = (510.0, 350.0)
MIRROR_GRIP = (510.0, 448.0)
MIRROR_RUN, MIRROR_REACH = 78.0, 4.0
HANDLE_W = 14.0

POSY_GRIP = (232.0, 440.0)
POSY_W = 10.0
POSY_MOUTH = (232.0, 392.0)
POSY_FOOT = 484.0
POSY_RUN, POSY_REACH = 78.0, 4.0
LEAVES = ((-30.0, 46.0, 4.0), (-68.0, 54.0, 3.0), (-108.0, 50.0, -4.0))
RACEME = (150.0, 40.0, 5.0, 4, 5.8)


def sleeve_end(hand, *, run, reach=0.0, cuff=3.0, flare=12.0, curl=-5.0, elbow_r=9.0):
    """The cloak's own sleeve: a bell that opens from the cuff mouth toward the elbow, running
    to the cloak's outer edge so the garment outline is the sleeve's far end."""
    u = hand.wrist_dir
    w = K.P(hand.wrist) - u * reach
    n = np.array([u[1], -u[0]])
    half = hand.wrist_w / 2
    base = w + u * run
    shape = K.R(K.Path(w + n * (half + cuff)).sag(w - n * (half + cuff), curl)
                .sag(base - n * (half + cuff + flare), 1.5).line(base + n * (half + cuff + flare))
                .sag(w + n * (half + cuff), 1.5).close().d)
    shape = shape.buffer(-1.6).buffer(1.6)
    elbow = shape.buffer(-elbow_r).buffer(elbow_r)
    mouth = shape.intersection(Polygon([w - n * 60 - u * 4, w + n * 60 - u * 4,
                                        w + n * 60 + u * 16, w - n * 60 + u * 16]))
    # clipped to the mantle exactly: any grow leaves a bump in the silhouette at the sleeve's far end
    return K.U(elbow, mouth).intersection(QG.mantle())


def _arc(hand, reach, offset, half, curl):
    u = hand.wrist_dir
    n = np.array([u[1], -u[0]])
    m = K.P(hand.wrist) - u * reach + u * offset
    path = K.Path(m + n * half).sag(m - n * half, curl)
    return np.asarray(K.C.sample_d(path.d, 0.3)[0][0])


def cuff_band(hand, sleeve, *, reach, width=11.0, curl=-5.0, cuff=3.0):
    """The red turn-back band at the sleeve's mouth: (region, MEDIUM back line, drip knockouts)."""
    half = hand.wrist_w / 2 + cuff + 8.0
    front = _arc(hand, reach, -5.0, half, curl)
    back = _arc(hand, reach, width, half, curl)
    band = Polygon(np.vstack([front, back[::-1]])).buffer(0).intersection(sleeve)
    band = band.buffer(-0.8).buffer(0.8)
    edge = LineString(back).intersection(sleeve.buffer(-0.3))
    line = C.Frag()
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 8.0:
            line += K.line(C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return band, line, edge


def drip_fringe(hand, sleeve, edge, *, width, reach, n=3, pitch=8.4, l_min=3.0, l_max=14.0):
    """§G.14 drip fringe: paper strokes with Ø6.3 terminals hanging from the band's back line down
    the sleeve (KNOCKED out of the jade). A drip that would not keep paper clear of the outline
    is dropped whole. Returns their shapes.

    Each drip starts under the back line, so it is a notch open to the band, not a hole: heal
    fills a knockout hole within 3 px of its fill's edge."""
    u = hand.wrist_dir
    nn = np.array([u[1], -u[0]])
    inner = sleeve.buffer(-(K.MEDIUM / 2 + K.GAP_MARK), quad_segs=12)
    mid = K.P(hand.wrist) - u * reach + u * width
    cross = LineString([tuple(mid + nn * 80), tuple(mid - nn * 80)]).intersection(sleeve)
    if cross.is_empty:
        return Polygon()
    cross = max(K._lines_of(cross), key=lambda g: g.length)
    c0 = np.asarray(cross.interpolate(0.5, normalized=True).coords[0])
    out = []
    for i in range(n):
        off = (i - (n - 1) / 2) * pitch
        t = (i + 0.5) / n
        Lk = l_min + (l_max - l_min) * math.sin(math.pi * t)
        q = c0 + nn * off
        hit = LineString([tuple(q - u * 20.0), tuple(q + u * 20.0)]).intersection(edge)
        pts = [g for g in getattr(hit, "geoms", [hit]) if g.geom_type == "Point" and not g.is_empty]
        if not pts:
            continue
        pe = min(pts, key=lambda g: g.distance(Point(*q)))
        p_edge = np.array([pe.x, pe.y])
        p0 = p_edge - u * 1.0
        p1 = p_edge + u * (Lk + 2.0)
        body = LineString([tuple(p0), tuple(p1)]).buffer(K.MEDIUM / 2).union(
            Point(*p1).buffer(K.TD / 2, quad_segs=12))
        if inner.contains(body):
            out.append(body)
    return K.U(*out) if len(out) == n else Polygon()


def sleeve_edges(sleeve, keep):
    """The sleeve's long folds: its edges inside the cloak (the cloak outline carries the rest)."""
    out = K.C.Frag()
    edge = K.R(sleeve).boundary.intersection(keep)
    for g in K._lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
        if g.length > 6.0:
            out += K.line(K.C.polyline_d(np.asarray(g.coords)), K.MEDIUM, role="cuffline")
    return out


def sleeve_grain(hand, sleeve, avoid, *, inset=6.5):
    """Hatch along the forearm axis, so the sleeve grain differs from the mantle's."""
    u = hand.wrist_dir
    ang = float(np.degrees(np.arctan2(u[1], u[0])))
    zone = sleeve.buffer(-inset).difference(avoid)
    return QG.drop_short(K.hatch_in(zone, angle=ang, origin=tuple(hand.wrist)), 10.0)


def sleeved_hand(hand, sleeve):
    """The hand beyond its cuff mouth; the sleeve's edge is the hand's contour."""
    region = K._biggest(hand.shape.difference(sleeve))
    inner = hand.hand.meta.get("inner", K.C.Frag())
    return K.Part(region, K.C.Frag(), K.outline(region) + K.clip_in(inner, region.buffer(-5.0)),
                  {**hand.hand.meta, "hand_region": region})


def held_attribute(attribute, hand_cuff, *, keep=lambda m: m.role != "outline"):
    """One outline at the hand and the held object, without a halo."""
    joined = K.U(attribute.shape, hand_cuff.shape)
    fillet = joined.buffer(1.6).buffer(-1.6).intersection(hand_cuff.shape.buffer(8.0))
    shape = K.U(joined, fillet).simplify(0.02)
    fills = K.clip_in(attribute.fills, attribute.shape.difference(
        hand_cuff.shape.buffer(-K.MEDIUM / 2))) + hand_cuff.fills
    return K.Part(
        shape, fills,
        K.clip_out(attribute.lines.select(keep), hand_cuff.shape, eps=0.2, trap=0.0)
        + hand_cuff.lines.select(lambda m: m.role != "outline")
        + K.clip_in(K.outline(hand_cuff.shape, role="grip-edge"), attribute.shape.buffer(2.0))
        + K.outline(shape, role="contour"), hand_cuff.meta)


def merged(parts):
    """Painter-ordered sub-composition of Parts (back to front) into one Part, with no silhouette."""
    sub = K.Scene()
    for name, p in parts:
        sub.part(name, p)
    return K.Part(sub.silhouette(), K.C.Frag(), sub.compose(contour=None, heal_gaps=False), {})


def mirror_part():
    mir = Q.mirror(MIRROR_C, 41.0, 55.0, handle_to=486.0, knop_y=482.0, handle_w=HANDLE_W,
                   sal_build=QSAL.salamander)
    lines = mir.lines.select(lambda m: m.role != "outline") + K.outline(K.circle(MIRROR_C, 41.0))
    return K.Part(mir.shape, mir.fills, lines, mir.meta)


def posy_part():
    po = Q.laurel_posy(POSY_MOUTH, -90.0, holder_len=POSY_FOOT - POSY_MOUTH[1], holder_w=(POSY_W, POSY_W),
                       leaves=LEAVES, raceme=RACEME, layered=True)
    return merged([("raceme", po["raceme"]), ("laurel", po["leaves"]), ("holder", po["holder"])])


def seated_clasp(clasp, seat):
    """The Lion Mark set into the gown opening: its wing tips run under the gown's edge lines (the
    gold traps under them and its contour ends inside their ink) instead of their points landing
    on those lines, which made heal break both outlines."""
    sil = clasp.meta["silhouette"].intersection(seat)
    # a wing notch cut through by the seat edge would leave an ink bump on that edge and a gold
    # strip under 3 px beside it: close the notches next to the edge
    near = seat.boundary.buffer(4.0, quad_segs=8)
    sil = K.U(sil, sil.buffer(3.0, quad_segs=8).buffer(-3.0, quad_segs=8).intersection(near)).intersection(seat)
    contour = [m for m in clasp.lines.marks if m.role == "clasp-contour"]
    partings = K.clip_in(C.Frag(contour), sil.buffer(-1.2))
    # a parting whose notch went under the seat edge would only leave a stub beside that line
    edge = seat.boundary.buffer(3.5)
    part_d = "".join(C.polyline_d(np.asarray(pts)) for m in partings.marks if m.d
                     for pts, _ in G.flatten(m.d, 0.02)
                     if len(pts) > 1 and LineString(pts).length >= 5.0 and not LineString(pts).intersects(edge))
    # one contour mark round the seated silhouette: its run along the seat edge lies inside the
    # gown line's ink, so heal sees one piece touching that line rather than stubs beside it
    lines = K.line(K.D(sil) + part_d, K.FINE, role="clasp-contour")
    lines += clasp.lines.select(lambda m: m.role != "clasp-contour")
    fills = K.fill(sil.difference(clasp.meta["face"]), K.GOLD, role="clasp")
    return K.Part(clasp.shape.intersection(seat), fills, lines, {**clasp.meta, "silhouette": sil})


def region(pts):
    return K.R(B.cspline(pts)).buffer(0)


def head_group():
    fc = QF.oracle_face(HEAD, crease=True, dot_dx=0.0, eye_dy=13.0, mouth_dy=33.0, lip_dy=40.0, lip_sag=-1.4,
                        lip_hw=4.6, brow_in=8.0)
    veil = region(VEIL)
    inner = LineString(G.Curve(np.asarray(B.open_spline(VEIL_GUIDE))).offset(-VEIL_IN, spacing=0.5))
    diad = Q.stalactite_circlet(*CIRCLET, h=10.0, clip=veil, stop=inner, **KITES)
    # the veil's dome: above the circlet's centre line, in front of the head
    arc = np.asarray(diad.meta["arc"])
    above = Polygon(np.vstack([arc, [[arc[-1][0] + 80, arc[-1][1]], [arc[-1][0] + 80, 0], [arc[0][0] - 80, 0],
                                     [arc[0][0] - 80, arc[0][1]]]])).buffer(0)
    # the veil's front: above the hem curve at the temples (it hides the
    # hair roots) and above the circlet line over the head, never over the face
    hem = np.array(VEIL_HEM, float)
    below = Polygon(np.vstack([hem, [[hem[-1][0], 700], [hem[0][0], 700]]])).buffer(0)
    dome = veil.difference(below).difference(fc.skin.difference(above))
    neck = K.neck(fc, bottom=318.0, width=32.0)
    hide = K.U(fc.skin, neck.shape, dome)
    lf = B.lock_part(HAIR_F_OUT, HAIR_F_IN, n=2, side=+1, stagger=10.0, hide=hide)
    ln = B.lock_part(HAIR_N_OUT, HAIR_N_IN, n=3, side=-1, stagger=10.0, hide=hide)
    head = K.Part(fc.skin, C.Frag(), fc.lines + K.outline(fc.head), {})
    face_low = fc.skin.difference(above)
    hair_low = K.U(lf.shape, ln.shape).intersection(below)
    return dict(fc=fc, veil=veil, dome=dome, diad=diad, lf=lf, ln=ln, head=head, neck=neck, face_low=face_low,
                hair_low=hair_low)


class Scene(K.Scene):
    """The kit Scene, but slits between items smaller than SLIT_AREA are closed in the silhouette:
    stroked at CONTOUR, a slit's tiny ring prints as an ink blob."""

    def silhouette(self):
        sil = super().silhouette()
        return K.U(*[Polygon(g.exterior.coords, [r.coords for r in g.interiors if Polygon(r).area >= SLIT_AREA])
                     for g in K._polys_of(sil)])


SLIT_AREA = 60.0


def figure():
    sc = Scene()
    hg = head_group()
    fc = hg["fc"]
    size = K.hand_size(fc) * HAND_SCALE
    R_ = lambda p: Q.rot_part(p, TILT, PIVOT)                       # noqa: E731
    rg = lambda g: Q.rot_geom(g, TILT, PIVOT)                       # noqa: E731
    veil, face_low, hair_low = rg(hg["veil"]), rg(hg["face_low"]), rg(hg["hair_low"])
    diad, lf, ln, head, neck = [R_(hg[k]) for k in ("diad", "lf", "ln", "head", "neck")]

    # oracle's LEFT (viewer's right): wrap on the mirror handle, thumb up, forearm out and down
    h_m = K.hand5(MIRROR_GRIP, -90.0, "wrap", size=size, hand="L", view="back", grip_w=HANDLE_W)
    sl_m = sleeve_end(h_m, run=MIRROR_RUN, reach=MIRROR_REACH)
    # oracle's RIGHT (viewer's left): wrap on the posy-holder, thumb up, forearm out and down
    h_p = K.hand5(POSY_GRIP, -90.0, "wrap", size=size, hand="R", view="back", grip_w=POSY_W)
    sl_p = sleeve_end(h_p, run=POSY_RUN, reach=POSY_REACH)

    bands, band_lines, drips, grains = [], C.Frag(), [], C.Frag()
    for h, sl, reach in ((h_m, sl_m, MIRROR_REACH), (h_p, sl_p, POSY_REACH)):
        b, bl, edge = cuff_band(h, sl, reach=reach)
        dz = drip_fringe(h, sl, edge, width=11.0, reach=reach)
        bands.append(b)
        band_lines += bl
        drips.append(dz)
        grains += sleeve_grain(h, sl, K.U(b.buffer(5.5), dz.buffer(5.5)))
    sleeves = K.U(sl_m, sl_p)
    keep = QG.mantle().buffer(-0.4)

    cuff_m, cuff_p = sleeved_hand(h_m, sl_m), sleeved_hand(h_p, sl_p)
    held_m = held_attribute(mirror_part(), cuff_m)
    held_p = held_attribute(posy_part(), cuff_p, keep=lambda m: True)

    seam = LineString(F.seam_spec(SEAM)["points"])
    neckline = K.U(lf.shape, ln.shape, head.shape, neck.shape, veil)
    # on the far side the seat reaches over the hairline strip between the gown's edge and the lock,
    # so the wing tips end on the lock line rather than leaving that strip beside it (on the near
    # side the gap to the lock widens under the wing, and closing it would step the edge)
    locks = K.U(lf.shape, ln.shape)
    gown_ = QG.gown()
    seat = K.U(gown_, K.U(gown_, lf.shape).buffer(2.5, quad_segs=8).buffer(-2.5, quad_segs=8))
    seat = K.U(*K._polys_of(seat.difference(locks)))
    brooch = seated_clasp(K.lion_clasp((388.0, 322.0), 40.0), seat)
    robes = QG.garments(K.U(held_m.shape, held_p.shape, neckline, brooch.shape),
                        sleeves=sleeves, bands=K.U(*bands), band_lines=band_lines, drips=K.U(*drips),
                        sleeve_grain=grains, sleeve_edges=sleeve_edges(sl_m, keep) + sleeve_edges(sl_p, keep),
                        seam=seam)

    # ---- back to front -----------------------------------------------------------
    ruff = K.Scene()
    for i, (r0, t1, sg, sd, wd) in enumerate(PLUMES):
        ruff.part(f"plume{i}", Q.plume(r0, t1, sag=sg, width=wd, n=5, side=sd, hatch=10.5, depth=3.0))
    rf = ruff.compose(contour=None)
    sc.part("ruff", K.Part(ruff.silhouette(), C.Frag(), rf, {}))
    sc.part("robes", robes)
    # the veil: everything of it that is not behind the face, the hair below
    # its hem, the neck or the garments (it hides the ruff's roots and the hair's)
    vf = veil.difference(K.U(face_low, hair_low, neck.shape, robes.shape))
    vf = K.U(*[g for g in K._polys_of(vf) if g.area > 40.0])
    guide = np.asarray([Q.rot_pt(p_, TILT, PIVOT) for p_ in B.open_spline(VEIL_GUIDE)])
    v_lines = C.Frag()
    # the veil's inner contour: ONE line VEIL_IN inside the crown, from the far
    # circlet end over the dome and down the near side; the circlet's round
    # end sits on it (the line stops at the band and runs on below it)
    off = LineString(G.Curve(guide).offset(-VEIL_IN, spacing=0.5))
    segs = [g for g in K._lines_of(off.intersection(vf.difference(diad.shape).buffer(0.5))) if g.length > 20]
    if segs:
        dome = min(segs, key=lambda g: g.bounds[1])
        keep_ = [dome]
        if "end" in diad.meta:
            e_ = Point(*diad.meta["end"])
            keep_ += [g for g in segs if g is not dome and g.distance(e_) < 8.0]
        for g in keep_:
            v_lines += K.line(C.polyline_d(np.asarray(g.coords)), K.FINE, role="veil-fold")
    sc.part("neck", neck)
    sc.part("lockF", lf)
    sc.part("lockN", ln)
    sc.part("head", head)
    sc.part("veil", K.Part(vf, C.Frag(), K.outline(vf) + v_lines, {}))
    sc.part("diadem", diad)
    sc.part("brooch", brooch)
    sc.part("mirror+hand+sleeve", held_m)
    sc.part("posy+hand+sleeve", held_p)
    sc.tidy_zone = diad.shape.buffer(3.0)
    return sc


TIDY_ROLES = ("outline", "contour", "clasp-contour")


def tidy(f: C.Frag, zone) -> C.Frag:
    """Outline crumbs the compose leaves: pieces shorter than 2.5 px anywhere (they print as ink
    beads on the line they sit on), and the face contour's bits that show between the circlet's
    points (``zone``) below 8 px."""
    zp = prep(zone)
    out = []
    for m in f.marks:
        if m.kind == "fill" or not m.d or m.role.split("@")[0] not in TIDY_ROLES:
            out.append(m)
            continue
        keep, dropped = [], False
        for pts, cl in G.flatten(m.d, 0.02):
            pts = np.asarray(pts)
            ln_ = LineString(pts) if len(pts) > 1 else None
            short = ln_ is None or ln_.length < 2.5 or (not cl and ln_.length < 8.0 and zp.contains(ln_))
            if short:
                dropped = True
                continue
            keep.append(C.polyline_d(pts, closed=cl))
        if not dropped:
            out.append(m)
        elif keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def build():
    sc = figure()
    f = tidy(sc.compose(), sc.tidy_zone)
    # red tucked under a thick ink junction (two plume contours meeting the silhouette) is
    # invisible; QA 4c reads it as art hidden under a plate, so cut it
    r_ = T.CONTOUR / 2 + 0.3
    solid = f.shape("ink").buffer(-r_ - 1.0).buffer(r_ + 1.0).buffer(-1.0)
    red = K.clip_out(C.Frag([m for m in f.marks if m.layer == "red" and m.kind == "fill"]), solid, eps=0.0, trap=0.0)
    f = C.Frag([m for m in f.marks if not (m.layer == "red" and m.kind == "fill")] + list(red.marks), f.meta)
    return K.layers(f)
