"""art/QS.py — Q♠ · The Blind Oracle (creative brief §H.2). Pass 4 (layout)."""
from __future__ import annotations

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from art import _qs_parts as Q
from art import _qs_face as QF
from art import _qs_body as B
from art import _qs_garb as GB
import os

P = K.P
HEAD = (388.0, 200.0)
TILT, PIVOT = -6.0, (388.0, 292.0)

# ---- head group (drawn upright, then inclined TILT about PIVOT) --------------------
VEIL = [(300, 350), (306, 300), (314, 250), (322, 206), (336, 168), (358, 142), (392, 128), (428, 134),
        (456, 152), (474, 184), (486, 226), (496, 282), (508, 350), (404, 372)]
VEIL_HEM = [(270, 222), (330, 210), (350, 206), (388, 196), (426, 194), (452, 198), (474, 206), (520, 222)]
# sparse contour lines (§H.2): offsets of the veil's edge, far temple -> over the crown -> near foot
VEIL_GUIDE = [(326, 196), (336, 168), (358, 142), (392, 128), (428, 134), (456, 152), (474, 184), (486, 226),
              (496, 282), (504, 330)]
CIRCLET = ((324.0, 152.0), (378.0, 156.0), (484.0, 134.0))
KITES = dict(xs=(338.5, 350.5, 363.0, 378.0, 396.0, 413.0, 429.5, 445.5, 461.0),
             lengths=(13.0, 16.0, 21.0, 31.0, 24.0, 20.0, 17.0, 14.5, 12.0),
             widths=(7.4, 8.0, 8.8, 10.8, 10.2, 9.4, 8.8, 8.0, 7.4), top_k=0.25)
# hair: two locks filling the veil's face opening (outer edge = the veil's front
# edge), falling out of it in front of the shoulders to rolled ends
HAIR_F_OUT = [(342, 176), (328, 222), (324, 266), (328, 312), (326, 362), (318, 398)]
HAIR_F_IN = [(364, 176), (358, 222), (366, 266), (366, 304), (360, 350), (350, 392)]
HAIR_N_OUT = [(448, 170), (466, 214), (476, 262), (478, 316), (484, 366), (492, 404)]
HAIR_N_IN = [(420, 170), (412, 222), (400, 266), (404, 304), (426, 352), (446, 396)]

# ---- ruff: six gill plumes, root -> tip, sag, feathered side, width (back to front) --
PLUMES = [
    ((352, 262), (260, 183), 12.0, -1, 42.0), ((426, 262), (538, 178), -12.0, +1, 44.0),
    ((348, 280), (222, 242), 12.0, -1, 44.0), ((430, 280), (574, 236), -12.0, +1, 46.0),
    ((346, 298), (204, 302), 10.0, -1, 42.0), ((432, 298), (590, 296), -10.0, +1, 44.0),
]
# ---- body (card frame) ----------------------------------------------------------
MANTLE = [(388, 300), (340, 306), (286, 312), (236, 322), (200, 340), (178, 372), (164, 420), (154, 480),
          (150, 545), (626, 545), (620, 480), (610, 420), (596, 372), (574, 340), (538, 322), (488, 312),
          (436, 306)]
LINING_L = [(372, 300), (330, 306), (306, 360), (290, 440), (280, 545), (366, 545), (366, 440), (370, 360),
            (374, 312)]
LINING_R = [(404, 300), (446, 306), (470, 360), (486, 440), (496, 545), (410, 545), (410, 440), (406, 360),
            (402, 312)]
LINING_L_MID = [(340, 404), (332, 450), (326, 500), (324, 540)]
LINING_R_MID = [(446, 408), (452, 450), (455, 500), (456, 540)]
GOWN = [(374, 300), (368, 380), (362, 460), (360, 545), (416, 545), (414, 460), (408, 380), (402, 300),
        (388, 296)]

GOWN_FOLD = [(386, 352), (384, 420), (383, 480), (383, 545)]
GOWN_SEAM = [(402.5 + 0.02 * (y - 360), y) for y in range(362, 512, 10)]

MIRROR_C = (512.0, 350.0)
SAL = [(-30, -26), (-21, -18), (-8, -6), (3, 7), (9, 16), (11, 26), (5, 34), (-4, 37)]
SAL_K, SAL_D = 0.95, (6.0, -2.0)

WRIST_L, WRIST_R = (316.0, 458.0), (532.0, 488.0)
POSY = dict(mouth=(322.0, 394.0), axis_deg=-104.0)
FIST_L = (326.0, 424.0)
FIST_R = (512.0, 452.0)


def region(pts):
    return K.R(B.cspline(pts)).buffer(0)


def head_group():
    fc = QF.oracle_face(HEAD, crease=True, dot_dx=0.0, eye_dy=13.0, mouth_dy=33.0, lip_dy=40.0, lip_sag=-1.4,
                        lip_hw=4.6, brow_in=8.0)
    veil = region(VEIL)
    diad = Q.stalactite_circlet(*CIRCLET, h=8.0, clip=veil, **KITES)
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


def figure():
    sc = K.Scene(rank="Q")
    hg = head_group()
    R_ = lambda p: Q.rot_part(p, TILT, PIVOT)                       # noqa: E731
    rg = lambda g: Q.rot_geom(g, TILT, PIVOT)                       # noqa: E731
    veil, face_low, hair_low = rg(hg["veil"]), rg(hg["face_low"]), rg(hg["hair_low"])
    diad, lf, ln, head, neck = [R_(hg[k]) for k in ("diad", "lf", "ln", "head", "neck")]

    # ---- back to front -----------------------------------------------------------
    for i, (r0, t1, sg, sd, wd) in enumerate(PLUMES):
        sc.part(f"plume{i}", Q.plume(r0, t1, sag=sg, width=wd, n=5, side=sd, hatch=9.5, depth=3.0))
    mreg = region(MANTLE)
    m_in, m_seam = GB.bordered(mreg, 30.0)
    pk = os.environ.get("QS_PAT", "karst")
    if pk == "drops":
        m_pat = GB.drops(m_in, pitch=(30.0, 30.0), origin=(388.0, 330.0))
    elif pk == "ripples":
        m_pat = GB.ripple_drops(m_in, pitch=(46.0, 40.0), origin=(388.0, 330.0))
    elif pk == "karst":
        m_pat = K.pattern(m_in, "karst", origin=(388.0, 330.0), pitch=(26.0, 20.0))
    elif pk == "strata":
        m_pat = K.pattern(m_in, "strata", heights=(12.0, 19.0), hatched="thin", y0=330.0)
    else:
        m_pat = C.Frag()
    sc.part("mantle", K.Part(mreg, K.fill(mreg, K.JADE), K.outline(mreg) + m_seam + m_pat, {}))
    for nm, pts, mid in (("liningL", LINING_L, LINING_L_MID), ("liningR", LINING_R, LINING_R_MID)):
        r_ = region(pts)
        holes = GB.drop_column(r_, B.open_spline(mid), r=(3.2, 4.4), gap=4.0)
        sc.part(nm, K.Part(r_, K.fill(r_.difference(holes), K.RED), K.outline(r_), {}))
    gr = region(GOWN)
    g_lines = K.outline(gr)
    fold = B.open_spline(GOWN_FOLD)
    g_lines += C.stroke(C.polyline_d(fold), K.FINE, role="gown-fold") + K.dot(fold[0], K.TD, role="gown-fold-t")
    for (x, y) in GOWN_SEAM:
        g_lines += K.dot((x, y), 4.2, role="seam-dot")
    sc.part("gown", K.Part(gr, C.Frag(), g_lines, {}))
    # the veil: everything of it that is not behind the face, the hair below
    # its hem, the neck or the mantle (it hides the ruff's roots and the hair's)
    vf = veil.difference(K.U(face_low, hair_low, neck.shape, mreg, region(LINING_L), region(LINING_R), gr))
    vf = K.U(*[g for g in K._polys_of(vf) if g.area > 40.0])
    guide = np.asarray([Q.rot_pt(p_, TILT, PIVOT) for p_ in B.open_spline(VEIL_GUIDE)])
    v_lines = C.Frag()
    pcs = [g for g in K._polys_of(vf.difference(diad.shape)) if g.area > 400]
    dome_pc = min(pcs, key=lambda g: g.centroid.y)
    near_pc = max(pcs, key=lambda g: g.centroid.x)
    # the dome: one contour line 10 px inside the crown, butting the circlet at both ends
    off = LineString(K.current_lines.__globals__["G"].Curve(guide).offset(-10.0, spacing=0.5))
    seg_ = [g for g in K._lines_of(off.intersection(dome_pc.buffer(0.5))) if g.length > 20]
    if seg_:
        v_lines += K.line(C.polyline_d(np.asarray(max(seg_, key=lambda g: g.length).coords)), K.FINE, role="veil-fold")
    # the near side: a fold falling from the circlet, rolling into a terminal
    v_lines += K.current_lines(guide, 1, near_pc, side=-1, edge=K.CONTOUR, first=9.8, end="edge")
    sc.part("neck", neck)
    sc.part("lockF", lf)
    sc.part("lockN", ln)
    sc.part("head", head)
    sc.part("veil", K.Part(vf, C.Frag(), K.outline(vf) + v_lines, {}))
    sc.part("diadem", diad)
    sc.part("brooch", K.lion_clasp((388.0, 322.0), 40.0))

    # ---- arms, attributes, hands ---------------------------------------------------
    slL, cfL = K.sleeve(K.SleeveSpec(base=(252.0, 552.0), wrist=WRIST_L, sag=6.0, width=50.0, wrist_w=32.0,
                                     cuff=14.0, color=K.JADE, cuff_color=K.RED))
    slR, cfR = K.sleeve(K.SleeveSpec(base=(558.0, 552.0), wrist=WRIST_R, sag=-6.0, width=52.0, wrist_w=34.0,
                                     cuff=14.0, color=K.JADE, cuff_color=K.RED))
    sc.part("sleeveL", Q.drip_fringe_ko(slL, cfL), halo=K.HALO, halo_only=("mantle",))
    sc.part("sleeveR", Q.drip_fringe_ko(slR, cfR), halo=K.HALO, halo_only=("mantle",))
    sal_pts = [(MIRROR_C[0] + x * SAL_K + SAL_D[0], MIRROR_C[1] + y * SAL_K + SAL_D[1]) for x, y in SAL]
    mir = Q.mirror(MIRROR_C, 41.0, 55.0, handle_to=490.0, sal_pts=sal_pts)
    sc.part("mirror", mir, halo=K.HALO, halo_only=("mantle", "liningR", "plume5", "plume3", "lockN", "sleeveR"))
    posy = Q.laurel_posy(POSY["mouth"], POSY["axis_deg"], holder_len=44.0,
                         leaves=((-70.0, 58.0, 5.0), (-118.0, 62.0, -6.0), (-160.0, 56.0, 6.0)),
                         raceme=(150.0, 62.0, -6.0, 7, 6.4))
    sc.part("laurel", posy["leaves"], halo=K.HALO, halo_only=("mantle", "liningL", "plume4", "lockF"))
    sc.part("raceme", posy["raceme"], halo=K.HALO, halo_only=("mantle", "sleeveL", "liningL"))
    sc.part("holder", posy["holder"])
    sc.part("cuffL", cfL)
    sc.part("cuffR", cfR)
    K.fist(FIST_L, POSY["axis_deg"], shaft_w=9.0, back=-1, wrist=WRIST_L, wrist_w=24.0, h=30.0).add_to(
        sc, "handL", halo=0.0)
    K.fist(FIST_R, -90.0, shaft_w=12.0, back=+1, wrist=WRIST_R, wrist_w=26.0, h=34.0).add_to(sc, "handR", halo=0.0)
    K.band_guard(sc, "Q")
    fill_pinholes(sc)
    return sc


def fill_pinholes(sc, max_area=40.0):
    """The veil, head and circlet leave sub-pixel slits in the silhouette
    union; stroked at CONTOUR each becomes an ink dot (and a QA 12 near-miss).
    An empty item at the very BACK (it hides nothing) closes them."""
    sil = sc.silhouette()
    holes = [Polygon(r) for pg in K._polys_of(sil) for r in pg.interiors if Polygon(r).area < max_area]
    if holes:
        sc.items.insert(0, K.Item("pinholes", C.Frag(), K.U(*holes).buffer(0.6), True))


def build():
    return figure().layers()
