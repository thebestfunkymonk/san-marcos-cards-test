"""Render the inkkit demo sheets (one per module) and the showpiece card.

    .venv/bin/python -m inkkit.demo            # from the project root
    .venv/bin/python inkkit/demo.py [names...]

Outputs SVG + PNG (1500 px wide) into inkkit/demo/, plus index.png (contact
sheet of everything), the showpiece's print plates (knockouts applied), its
preflight overlay and a Bézier-fitted copy.
"""
from __future__ import annotations

import math
import os
import sys
import time
import warnings

import numpy as np

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inkkit import card, geom as G, hatch as H, svg, tokens as T  # noqa: E402
from inkkit import heraldry as HR, preflight as PF, suits as SU  # noqa: E402
from inkkit import ornament as O  # noqa: E402
from inkkit.stroke import PROFILES, STYLES, stroke, styled  # noqa: E402
from inkkit.typeset import text_on_arc, text_on_path, text_to_path  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "demo")
INK, RED, FOIL, PAPER, JADE = T.INK, T.RED, T.FOIL, T.PAPER, T.JADE
GREY = "#7A776E"
LABEL_FONT = ("Cinzel", {"wght": 600})
FOIL_MIN = T.PRINT_PROFILES["foil"]["min_line"]


# =============================================================================
# helpers
# =============================================================================
def label(text, x, y, size=10.5, anchor="middle", color=GREY, font=LABEL_FONT, tracking=90):
    d, _, _ = text_to_path(font[0], text.upper(), size, x, y, anchor=anchor, variations=font[1],
                           tracking=tracking)
    return svg.path(d, fill=color)


def sheet(title, h=1050):
    doc = svg.Doc(750, h, layers=("paper", "ink", "red", "foil", "labels"), title=f"inkkit — {title}")
    doc.add(svg.rect(0, 0, 750, h, fill=PAPER), layer="paper")
    d, _, _ = text_to_path("Cinzel", f"INKKIT · {title.upper()}", 17, 375, 34, anchor="middle",
                           variations={"wght": 700}, tracking=220)
    doc.add(svg.path(d, fill=INK), layer="labels")
    doc.add(svg.path(G.outline("M40 46H710", 1.05, cap="flat"), fill=INK), layer="labels")
    doc.add_def(svg.foil_gradient("foil", FOIL))
    doc.layer_style("foil", fill="url(#foil)")
    return doc


def fillp(d, color=INK, **kw):
    return svg.path(d, fill=color, **kw)


def strokep(d, color=INK, w=1.05, **kw):
    return svg.path(d, fill="none", stroke=color, stroke_width=w, stroke_linecap="round",
                    stroke_linejoin="round", **kw)


# =============================================================================
# showpiece
# =============================================================================
def showpiece():
    """A 750x1050 test card combining a nested frame, filigree corners, a
    guilloché rosette medallion, a tonal-engraved sphere, tapered scrolls, a
    laurel wreath and outlined type. Two-headed (180° symmetric) like a back.
    Every line meets the offset/foil print minimum (see showpiece-preflight)."""
    doc = card.new_card(PAPER, layers=("paper", "red", "foil", "ink"), title="inkkit showpiece")
    doc.add_def(svg.foil_gradient("foil", FOIL))
    doc.layer_style("foil", fill="url(#foil)")
    W, Hh, cx, cy = card.W, card.H, card.CX, card.CY

    # --- frame system -----------------------------------------------------------
    doc.add(fillp(O.rules(22, 22, W - 44, Hh - 44, [(0, 3.4), (6.2, 1.2)], r=20)), layer="ink")
    gb = O.guilloche_frame(36, 36, W - 72, Hh - 72, 14, width=13, wavelength=17, lines=6,
                           auto_lines=True, line_width=1.05)
    doc.add(strokep(gb, INK, 1.05), layer="ink")
    doc.add(fillp(O.rules(52, 52, W - 104, Hh - 104, [(0, 1.2)], r=6)), layer="ink")
    doc.add(fillp(O.beaded(O.frame_path(52, 52, W - 104, Hh - 104, 6, "round", 7), 1.6, 3.2)), layer="ink")

    # --- filigree corners (foil: 1.6 px minimum line) ---------------------------------
    foil = T.PRINT_PROFILES["foil"]
    doc.add(fillp(O.filigree_corners((66, 66, W - 132, Hh - 132), 170, 3, min_width=foil["min_line"],
                                     gap=foil["min_gap"], width=5.6), None), layer="foil")

    # --- central medallion -------------------------------------------------------------------
    R_ros_in, R_ros_out = 120, 156
    doc.add(fillp(O.wreath(cx, cy, 186, gap_deg=74, count=10, leaf_len=36, leaf_w=13, stem_width=2.2,
                           berries=4, berry_r=2.6, jitter=0.5, seed=4, gap=foil["min_gap"] + 0.2,
                           leaf_kw={"vein_w": foil["min_reversed"]}), None), layer="foil")
    ros = O.rosette(cx, cy, R_ros_in, R_ros_out, lobes=24, lines=8, phase_span=1.0, shape=0.85,
                    auto_lines=True, line_width=1.05)
    doc.add(strokep(ros, INK, 1.05), layer="ink")
    doc.add(fillp(O.rules(cx - 163, cy - 163, 326, 326, [(0, 2.4), (4.8, 1.1)], r=163)), layer="ink")
    doc.add(fillp(O.rules(cx - 116, cy - 116, 232, 232, [(0, 1.3)], r=116)), layer="ink")
    doc.add(fillp(O.beaded(G.circle_d(cx, cy, 107.5), 2.2, 2.8), RED), layer="red")
    # engraved sphere: breaks dissolve (staggered), tapers end at the print minimum
    rs = 98
    tone = H.sphere_tone(cx, cy, rs, light=(-0.55, -0.62, 0.56), ambient=0.0, gamma=1.1)
    lat = H.latitudes(cx, cy, rs, 3.8, tilt_deg=-18, rot_deg=-24)
    glint = O.starburst(cx - 36, cy - 40, 12, 2.4, 4, facets=False)
    eng = H.engrave(lat, tone, wmin=0.7, wmax=2.6, clip=G.circle_d(cx, cy, rs - 0.5), fade=3, edge_gap=1.6)
    cross_t = lambda x, y: np.clip((tone(x, y) - 0.66) / 0.34, 0, 1)
    eng += H.tonal(G.circle_d(cx, cy, rs - 1), cross_t, angle=30, spacing=4.2, wmax=1.7, fade=4, edge_gap=1.6)
    # the red star glint knocks a paper gap out of the engraving geometrically
    doc.add(fillp(G.knockout(eng, glint, 2.4)), layer="ink")
    doc.add(fillp(G.outline(G.circle_d(cx, cy, rs), 1.4)), layer="ink")
    doc.add(fillp(glint, RED), layer="red")

    # --- title block (drawn once, then rotated for the two-headed back) -----------------
    top = []
    tx, ty = cx, 258
    d, bb, _ = text_to_path("Cinzel", "SAN MARCOS", 46, tx, ty, anchor="middle",
                            variations={"wght": 700}, tracking=170)
    top.append(fillp(d, INK))
    d2, _, _ = text_to_path("Cinzel", "TEXAS", 13, tx, ty - 52, anchor="middle",
                            variations={"wght": 700}, tracking=900)
    for sg in (-1, 1):
        pts = np.array([[tx + sg * 50, ty - 57], [tx + sg * 90, ty - 60], [tx + sg * 128, ty - 70]])
        fl = O.flourish(pts, end_turns=1.15, end_size=16, end_cw=(sg < 0), tighten=2.2)
        top.append(fillp(styled(fl, 2.6, "scroll", end_ratio=0.35, taper=0.12, min_width=1.05,
                                terminal="ball", terminal_r=1.9), INK))
    top.append(fillp(O.filigree_band(372, 30, x=tx, y=ty + 32, width=2.4), INK))
    block = "\n".join(top)
    doc.add(block, card.rot180(block), layer="ink")
    tex = fillp(d2, RED)
    doc.add(tex, card.rot180(tex), layer="red")

    # --- side stars ---------------------------------------------------------------------------
    for sx in (104, W - 104):
        doc.add(fillp(O.starburst(sx, cy, 20, 5, 4, lw=FOIL_MIN), None), layer="foil")
        for sy in (-34, 34):
            doc.add(fillp(G.circle_d(sx, cy + sy, 2.4), None), layer="foil")
    return doc


# =============================================================================
# module sheets
# =============================================================================
def sheet_svg():
    doc = sheet("svg · layers · separations", 700)
    doc.add(svg.rect(60, 90, 180, 120, rx=12, fill="none", stroke=INK, stroke_width=2), layer="ink")
    doc.add(svg.circle(150, 150, 40, fill=RED), layer="red")
    doc.add(svg.path(G.star_d(150, 150, 30, 12, 5)), layer="foil")
    doc.add(label("rect / circle / path on ink, red, foil layers", 150, 232, 9), layer="labels")
    doc.add(svg.g(svg.path(G.star_d(0, 0, 40, 16, 6), fill=INK), transform=svg.tf(svg.translate(375, 150), svg.rotate(15))),
            layer="ink")
    doc.add(label("g + translate/rotate", 375, 232, 9), layer="labels")
    doc.add(svg.clip_path("cp1", svg.circle(600, 150, 55)), layer="ink")
    doc.add(svg.g(fillp(H.parallel(G.rect_d(530, 80, 140, 140), 30, 5, width=2.2)), clip_path="url(#cp1)"), layer="ink")
    doc.add(label("clipPath", 600, 232, 9), layer="labels")
    doc.add(svg.rect(60, 262, 630, 44, fill="url(#foil)"), layer="foil")
    doc.add(label("foil_gradient preview (print uses the foil plate)", 375, 326, 9), layer="labels")
    # --- separation demo: a tiny doc, its composite and its three plates -------
    mini = svg.Doc(160, 130, layers=("paper", "red", "ink", "foil"))
    mini.add(svg.rect(0, 0, 160, 130, fill=PAPER), layer="paper")
    mini.add(svg.path(G.circle_d(62, 65, 44), fill=RED), layer="red")
    mini.add(svg.path(G.rect_d(70, 22, 70, 86, 8), fill=INK), layer="ink")
    mini.add(svg.path(G.circle_d(105, 65, 17), fill=PAPER), layer="ink")          # paper = knockout
    mini.layer_style("foil", fill=FOIL)
    mini.add(svg.path(G.star_d(62, 65, 22, 9, 5)), layer="foil")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plates = mini.separations(trap=0.0)
    y0 = 380
    x = 40
    comp = mini.to_string()
    frames = [("composite", comp)] + [(f"{n} plate", s) for n, s in plates.items()]
    for nm, s in frames:
        inner = s.split(">", 1)[1].rsplit("</svg>", 1)[0]
        doc.add(svg.rect(x - 2, y0 - 2, 164, 134, fill="#FFFFFF", stroke=GREY, stroke_width=0.8), layer="labels")
        doc.add(svg.g(inner, transform=svg.translate(x, y0)), layer="labels")
        doc.add(label(nm, x + 80, y0 + 152, 8.5), layer="labels")
        x += 172
    doc.add(label("separations(): ink = black, paper/white & knockout=True = white,", 375, 580, 9), layer="labels")
    doc.add(label("every upper layer knocks out of the plates below it (trap= chokes it)", 375, 598, 9),
            layer="labels")
    return doc


def sheet_geom():
    doc = sheet("geom")
    a = G.circle_d(0, 0, 38)
    b = G.rect_d(-10, -30, 60, 60, 10)
    ops = [("union", G.union), ("difference", G.difference), ("intersection", G.intersection), ("xor", G.xor)]
    for i, (nm, fn) in enumerate(ops):
        x = 105 + i * 180
        doc.add(strokep(G.translate(a, x, 130), GREY, 0.8), strokep(G.translate(b, x, 130), GREY, 0.8),
                layer="labels")
        doc.add(fillp(G.translate(fn(a, b), x, 130), INK), layer="ink")
        doc.add(label(nm, x + 10, 200, 9), layer="labels")
    s = G.translate(G.star_d(0, 0, 50, 22, 5), 105, 290)
    doc.add(fillp(G.offset(s, 8), RED, opacity=0.25), fillp(s, INK), strokep(G.offset(s, -6), PAPER, 1.2),
            strokep(G.offset(s, 14, join="miter"), INK, 1.05), layer="ink")
    doc.add(label("offset round / miter / inset", 105, 375, 9), layer="labels")
    th = np.linspace(0, 2 * math.pi, 400)
    wob = np.column_stack([285 + (40 + 6 * np.sin(9 * th)) * np.cos(th), 290 + (40 + 6 * np.sin(9 * th)) * np.sin(th)])
    doc.add(strokep(G.poly_d(wob, True), GREY, 0.8), layer="labels")
    doc.add(strokep(G.simplify(G.poly_d(wob, True), 3.0), INK, 1.2), layer="ink")
    doc.add(label("simplify(tol=3)", 285, 375, 9), layer="labels")
    half = G.smooth_d([(465, 250), (430, 270), (445, 320), (465, 335)])
    doc.add(fillp(stroke(half, 5, "swell", min_width=1.05)),
            fillp(stroke(G.mirror_x(half, 470), 5, "swell", min_width=1.05), RED), layer="ink")
    doc.add(strokep("M470 240V345", GREY, 0.8, stroke_dasharray="3 3"), layer="labels")
    doc.add(label("mirror_x about axis", 470, 375, 9), layer="labels")
    petal = stroke(np.array([[645, 290], [645, 245]]), 12, "swell", min_width=1.05)
    doc.add(fillp(G.repeat_rotational(petal, 12, 645, 290)), layer="ink")
    doc.add(label("repeat_rotational(12)", 645, 375, 9), layer="labels")
    mini = G.rect_d(60, 420, 150, 210, 10)
    doc.add(strokep(mini, GREY, 0.8), layer="labels")
    glyph = G.translate(G.star_d(0, 0, 18, 7, 5), 100, 470)
    doc.add(fillp(glyph), fillp(G.rotate180(glyph, 135, 525), RED), layer="ink")
    doc.add(label("rotate180 (two-headed)", 135, 655, 9), layer="labels")
    path = "M260 600 C 300 420 440 640 480 450"
    cv = G.Curve(path)
    doc.add(strokep(path, INK, 1.2), layer="ink")
    for t in np.linspace(0, 1, 11):
        p, tg, nm = cv.at(t), cv.tangent(t), cv.normal(t)
        doc.add(strokep(G.poly_d([p, p + tg * 18]), RED, 1.05), strokep(G.poly_d([p, p + nm * 18]), FOIL, 1.05),
                layer="red")
    for p in G.resample(path, 12):
        doc.add(svg.circle(p[0], p[1], 1.6, fill=INK), layer="ink")
    doc.add(label("resample / tangent (red) / normal (gold)", 370, 655, 9), layer="labels")
    zig = G.poly_d([(560, 440), (700, 440), (700, 520), (640, 480), (560, 620)], True)
    doc.add(strokep(zig, GREY, 0.8), strokep(G.fillet(zig, 12), INK, 1.4), layer="ink")
    doc.add(strokep(G.round_corners("M565 600 L610 470 L660 560", 14), RED, 1.4), layer="red")
    doc.add(label("fillet(12) / round_corners (open)", 630, 655, 9), layer="labels")
    pts = np.array([(80, 760), (160, 700), (240, 800), (320, 720), (400, 780)])
    for p in pts:
        doc.add(svg.circle(p[0], p[1], 2.5, fill=RED), layer="red")
    doc.add(strokep(G.smooth_d(pts), INK, 1.4), layer="ink")
    doc.add(label("smooth_d (catmull-rom -> cubic béziers)", 240, 840, 9), layer="labels")
    ring = G.circle_d(560, 760, 60) + G.circle_d(560, 760, 30)
    doc.add(fillp(G.from_shape(G.to_shape(ring, "evenodd"))), layer="ink")
    doc.add(fillp(G.from_shape(G.to_shape(G.translate(ring, 120, 0), "nonzero")), RED), layer="red")
    doc.add(label("to_shape evenodd / nonzero", 620, 840, 9), layer="labels")
    txt, bb, _ = text_to_path("PlayfairDisplay", "bbox()", 44, 375, 950, anchor="middle", variations={"wght": 700})
    doc.add(fillp(txt), layer="ink")
    x0, y0, x1, y1 = G.bbox(txt)
    doc.add(svg.rect(x0, y0, x1 - x0, y1 - y0, fill="none", stroke=RED, stroke_width=1.05), layer="red")
    return doc


def sheet_print():
    doc = sheet("geom · knockout · interlace · fit")
    # interlace: knot of two strands + a ribbon crossing
    th = np.linspace(0, 2 * math.pi, 600, endpoint=False)
    trefoil = np.column_stack([190 + 70 * (np.sin(th) + 2 * np.sin(2 * th)) / 3 * 1.25,
                               220 + 70 * (np.cos(th) - 2 * np.cos(2 * th)) / 3 * 1.25])
    doc.add(fillp(G.interlace([trefoil], T.FINE, T.INTERLACE_GAP, closed=True)), layer="ink")
    doc.add(label("interlace(trefoil) — every crossing alternates", 190, 330, 9), layer="labels")
    xs = np.linspace(420, 710, 400)
    braid = [np.column_stack([xs, 215 + 42 * np.sin((xs - 420) / 290 * 2 * math.pi * 2 + 2 * math.pi * k / 3)])
             for k in range(3)]
    doc.add(fillp(G.interlace(braid, 3.1, 4.2)), layer="ink")
    doc.add(label("interlace(3-strand braid, 3.1 px, gap 4.2)", 565, 330, 9), layer="labels")
    # knockout: fill art and stroke art
    art = H.parallel(G.rect_d(60, 380, 260, 190, 12), 45, 7, width=2.1, cap="butt")
    occ = G.circle_d(190, 475, 58)
    doc.add(fillp(G.knockout(art, occ, 4.2)), fillp(G.outline(occ, 2.1)), layer="ink")
    doc.add(fillp(SU.pip("club", 190, 475, 62), RED), layer="red")
    doc.add(label("knockout(fill art, occluder, gap=4.2)", 190, 600, 9), layer="labels")
    lines = H.parallel(G.rect_d(430, 380, 260, 190, 12), -30, 7)
    occ2 = SU.pip_shape("spade", 90)
    occ2 = G.translate(occ2, 560, 475)
    ko = G.knockout(lines, occ2, 4.2, lines=True, lw=2.1)
    doc.add(fillp(H.emit(H.lines_of(ko), 2.1, taper=5, min_width=1.05)), fillp(G.outline(occ2, 2.1)), layer="ink")
    doc.add(label("knockout(lines=True) + tapered emit", 560, 600, 9), layer="labels")
    # fit_curves: dense polyline vs fitted beziers
    dense = O.filigree_corner(150, 3, x=60, y=660)
    fitted = G.fit_curves(dense, 0.05)
    doc.add(fillp(dense), layer="ink")
    doc.add(fillp(G.translate(fitted, 190, 0), RED), layer="red")
    doc.add(label(f"polyline {len(dense) // 1024} KB  ->  fit_curves {len(fitted) // 1024} KB", 230, 860, 9),
            layer="labels")
    # fillet_junction
    y_ = G.union(stroke("M520 820 L600 700", 7), stroke("M600 700 L680 820", 7), stroke("M600 700 L600 660", 7))
    doc.add(fillp(y_), layer="ink")
    doc.add(fillp(G.translate(G.fillet_junction(y_, (600, 700), 12, 40), 0, 150)), layer="ink")
    doc.add(label("fillet_junction (crotch fillet)", 600, 1000, 9), layer="labels")
    return doc


def sheet_stroke():
    doc = sheet("stroke")
    y = 80
    for i, prof in enumerate(PROFILES):
        yy = y + i * 34
        kw = dict(nib_angle=35, nib_min=0.18) if prof == "nib" else {}
        path = f"M150 {yy} C 250 {yy - 22} 350 {yy + 22} 450 {yy}" if prof == "nib" else f"M150 {yy}L450 {yy}"
        doc.add(fillp(stroke(path, 10, prof, min_width=1.05, **kw)), layer="ink")
        doc.add(label(prof, 140, yy + 4, 9, anchor="end"), layer="labels")
    doc.add(fillp(stroke("M520 90 L700 90", 9, cap="flat")), layer="ink")
    doc.add(label("cap=flat", 610, 115, 9), layer="labels")
    doc.add(fillp(stroke("M520 145 L700 145", 9, cap="pointed", min_width=1.05)), layer="ink")
    doc.add(label("cap=pointed + min_width", 610, 170, 9), layer="labels")
    doc.add(fillp(stroke("M520 200 C 580 170 640 230 690 200", 5, "hairline-end", terminal="ball", terminal_r=4,
                         min_width=1.05)), layer="ink")
    doc.add(label("terminal=ball", 610, 230, 9), layer="labels")
    doc.add(fillp(stroke("M520 270 L700 270", lambda t: 2 + 8 * np.sin(6 * np.pi * t) ** 2)), layer="ink")
    doc.add(label("width=callable(t)", 610, 295, 9), layer="labels")
    for i, st in enumerate(STYLES):
        yy = 330 + i * 26
        doc.add(fillp(styled(f"M520 {yy} C 580 {yy - 16} 640 {yy + 16} 700 {yy}", 11, "swell", style=st,
                             lw=2.1 if st == "monoline" else None, min_width=1.05)), layer="ink")
        doc.add(label(st, 512, yy + 4, 8.5, anchor="end"), layer="labels")
    th = np.linspace(0, 6 * np.pi, 1500)
    r = 90 * np.exp(-0.14 * th)
    spiral = np.column_stack([150 + r * np.cos(th), 510 + r * np.sin(th)])
    doc.add(fillp(stroke(spiral, 11, "scroll", end_ratio=0.15, terminal="ball", terminal_r=3, min_width=1.05)),
            layer="ink")
    doc.add(label("log spiral, 11px scroll profile", 150, 640, 9), layer="labels")
    hp = "M280 470 C 450 470 450 590 280 590"
    doc.add(fillp(stroke(hp, 26)), strokep(hp, RED, 1.05), layer="ink")
    doc.add(label("26px hairpin (fold-safe)", 360, 640, 9), layer="labels")
    tips = [("teardrop", 16), ("teardrop-rev", 16), ("taper-both", 16)]
    for i, (p, w) in enumerate(tips):
        doc.add(fillp(stroke(np.array([[540 + i * 55, 600], [540 + i * 55, 480]]), w, p, power=0.3 if i == 2 else 1)),
                layer="ink")
    doc.add(label("tips: no fishtails (power 0.3)", 595, 640, 9), layer="labels")
    cal = "M80 760 C 120 680 200 680 200 760 S 290 840 320 760 C 340 700 400 700 420 760"
    doc.add(fillp(stroke(cal, 12, "nib", nib_angle=40, nib_min=0.12, cap="pointed", min_width=1.05)), layer="ink")
    doc.add(label("broad nib 40°", 250, 850, 9), layer="labels")
    lp = "M500 830 C 760 600 420 600 680 830"
    doc.add(fillp(stroke(lp, 14, "taper-both", taper=0.4, min_width=1.05)), layer="ink")
    doc.add(label("self-crossing loop", 590, 850, 9), layer="labels")
    doc.add(fillp(stroke(G.ellipse_d(375, 950, 120, 45), 8, "nib", nib_angle=0, nib_min=0.15)), layer="red")
    doc.add(label("closed path + nib", 375, 1025, 9), layer="labels")
    return doc


def sheet_hatch():
    doc = sheet("hatch")
    shield = "M40 70H210V170C210 215 170 245 125 265C80 245 40 215 40 170Z"
    s = G.translate(shield, 10, 0)
    doc.add(strokep(H.parallel(s, 30, 4.2), INK, 1.05), strokep(s, INK, 2.2), layer="ink")
    doc.add(label("parallel -> stroke", 135, 290, 9), layer="labels")
    s = G.translate(shield, 250, 0)
    doc.add(fillp(H.cross(s, (45, -45), 5, width=1.1, taper=9, min_width=1.05)), strokep(s, INK, 2.2), layer="ink")
    doc.add(label("cross, width + taper", 375, 290, 9), layer="labels")
    s = G.translate(shield, 490, 0)
    doc.add(fillp(H.half(s, [(615, 60), (615, 280)], side=1, angle=45, spacing=7, width=2.1, cap="butt")),
            fillp(G.outline(s, 2.1)), fillp(G.outline("M615 70V265", 2.1, cap="flat")), layer="ink")
    doc.add(label("half() — monarchs half-hatch", 615, 290, 9), layer="labels")
    c = G.circle_d(135, 400, 88)
    doc.add(fillp(H.flow(c, lambda x, y: math.atan2(y - 400, x - 135) + math.pi / 2 + 0.45, 5, width=1.1,
                         singular=[(135, 400)], min_width=1.05)), strokep(c, INK, 1.6), layer="ink")
    doc.add(label("flow field (tapered ends)", 135, 510, 9), layer="labels")
    c = G.circle_d(375, 400, 88)
    doc.add(fillp(H.along(c, "M280 440 C 340 320 420 480 470 360", 5, width=1.1, taper=10, min_width=1.05)),
            strokep(c, INK, 1.6), layer="ink")
    doc.add(label("along guide (wave)", 375, 510, 9), layer="labels")
    c = G.circle_d(615, 400, 88)
    tone = H.sphere_tone(615, 400, 88)
    doc.add(fillp(H.engrave(H.latitudes(615, 400, 88, 3.8, tilt_deg=-15, rot_deg=-25), tone, wmax=2.8,
                            clip=c, edge_gap=1.5)), strokep(c, INK, 1.2), layer="ink")
    doc.add(label("engrave(latitudes, sphere_tone)", 615, 510, 9), layer="labels")
    c = G.circle_d(135, 620, 88)
    doc.add(fillp(H.tonal(c, H.sphere_tone(135, 620, 88), angle=-30, spacing=4.2, wmax=2.6, cross_at=0.6,
                          fade=5, edge_gap=1.5)), layer="ink")
    doc.add(label("tonal + cross_at + stagger", 135, 730, 9), layer="labels")
    c = G.circle_d(375, 620, 88)
    doc.add(fillp(H.stipple(c, H.sphere_tone(375, 620, 88), dmin=2.8, dmax=11, r=0.9)), layer="ink")
    doc.add(label("stipple (poisson disk)", 375, 730, 9), layer="labels")
    c = G.rect_d(530, 535, 170, 170, 16)
    doc.add(fillp(H.dot_screen(c, 7, 1.7, tone=H.linear_tone((530, 535), (700, 705)), r_min=0.6, fade=8)),
            layer="ink")
    doc.add(label("dot_screen + tone + fade", 615, 730, 9), layer="labels")
    sh2 = HR.shield(135, 850, 150, 175, "heater")
    doc.add(fillp(H.tonal(sh2, H.bevel_tone(sh2, -135, 26, base=0.38), angle=90, spacing=4.2, wmin=0.4,
                          wmax=2.8, edge_gap=1.6)),
            fillp(G.outline(sh2, 2.1)), layer="ink")
    doc.add(label("bevel_tone (embossed edge)", 135, 960, 9), layer="labels")
    cyl = G.rect_d(310, 770, 130, 160, 6)
    doc.add(fillp(H.tonal(cyl, H.cylinder_tone((375, 770), (375, 930), 65), angle=90, spacing=4.2, wmin=0.6,
                          wmax=2.8, edge_gap=1.4)), fillp(G.outline(cyl, 2.1)), layer="ink")
    doc.add(label("cylinder_tone", 375, 960, 9), layer="labels")
    doc.add(fillp(H.between("M530 770 C 580 750 650 790 700 770", "M530 930 C 590 960 640 900 700 930", 16,
                            width=1.1, taper=14, min_width=1.05)), layer="ink")
    doc.add(label("between two guides", 615, 960, 9), layer="labels")
    return doc


def sheet_scroll():
    doc = sheet("ornament · scroll")
    doc.add(fillp(O.scroll((40, 115), 0, 190, 1.4, width=7)), layer="ink")
    doc.add(label("scroll() ionic volute", 120, 200, 9), layer="labels")
    doc.add(fillp(O.scroll((270, 115), 0, 190, 1.4, width=7, terminal="eye")), layer="ink")
    doc.add(label("terminal='eye'", 350, 200, 9), layer="labels")
    doc.add(fillp(O.scroll((500, 105), 0, 210, 1.3, width=7, leaves=3, leaf_size=40)), layer="ink")
    doc.add(label("leaves=3 (acanthus)", 600, 200, 9), layer="labels")
    doc.add(fillp(O.s_scroll((70, 330), (300, 250), width=6.5)), layer="ink")
    doc.add(label("s_scroll(a, b)", 185, 370, 9), layer="labels")
    doc.add(fillp(O.c_scroll((420, 320), (690, 320), width=6.5, style="inline")), layer="ink")
    doc.add(label("c_scroll(a, b, style='inline')", 555, 370, 9), layer="labels")
    pts = np.array([[60, 470], [150, 420], [260, 470], [330, 430]])
    fl = O.flourish(pts, end_turns=1.3, end_size=46, start_turns=1.0, start_size=30, start_cw=True)
    doc.add(fillp(styled(fl, 6, lambda t: 0.25 + 0.75 * np.sin(np.pi * np.clip(t, 0, 1)) ** 1.1,
                         terminal="ball-both", terminal_r=3.4, min_width=1.05)), layer="ink")
    for p in pts:
        doc.add(svg.circle(p[0], p[1], 2.2, fill=RED), layer="red")
    doc.add(label("flourish(points) -> G2 volutes", 200, 540, 9), layer="labels")
    for i in range(4):
        doc.add(fillp(O.acanthus_leaf((420 + i * 80, 510), -70 + i * 8, 80, 26, lobes=2 + i % 2,
                                      style="outline" if i == 3 else "solid", lw=1.6)), layer="ink")
    doc.add(label("acanthus_leaf (solid / outline)", 560, 540, 9), layer="labels")
    for i, x in enumerate((30, 275, 520)):
        doc.add(fillp(O.filigree_corner(190, i + 1, x=x, y=575), None if i == 2 else INK),
                layer="foil" if i == 2 else "ink")
        doc.add(label(f"filigree_corner complexity={i + 1}", x + 100, 800, 9), layer="labels")
    doc.add(fillp(O.filigree_band(680, 56, x=375, y=865)), layer="ink")
    doc.add(fillp(O.filigree_band(460, 34, x=375, y=955, center="pearl", style="monoline", lw=1.6)), layer="red")
    doc.add(label("filigree_band: taper / monoline", 375, 1010, 9), layer="labels")
    return doc


def sheet_styles():
    doc = sheet("line styles · monoline americana", 740)
    for i, st in enumerate(STYLES):
        x = 30 + (i % 2) * 360
        y = 64 + (i // 2) * 330
        kw = dict(style=st, lw=2.1 if st == "monoline" else (1.05 if st == "outline" else None))
        doc.add(fillp(O.filigree_corner(200, 3, x=x + 10, y=y + 10, width=7, **kw)), layer="ink")
        doc.add(fillp(O.scroll((x + 230, y + 60), 0, 150, 1.35, width=7, **kw)), layer="ink")
        doc.add(fillp(O.fleuron(x + 280, y + 220, 70, style="lily", line_style=st,
                                lw=kw["lw"])), layer="ink")
        doc.add(label(f"style='{st}'", x + 160, y + 300, 10), layer="labels")
    return doc


def sheet_guilloche():
    doc = sheet("ornament · guilloche")
    st = lambda d, c=INK, w=1.05: strokep(d, c, w)
    doc.add(st(O.spirograph(125, 170, 80, 30, 42)), layer="ink")
    doc.add(label("spirograph hypo 80/30/42", 125, 285, 9), layer="labels")
    doc.add(st(O.spiro_rosette(375, 170, 75, 30, 30, copies=5)), layer="ink")
    doc.add(label("spiro_rosette x5 (5-fold)", 375, 285, 9), layer="labels")
    R, r, d = O.spirograph_fit(40, 95, 12, 5)
    doc.add(st(O.spirograph(625, 170, R, r, d), RED), layer="red")
    doc.add(strokep(G.circle_d(625, 170, 40), GREY, 0.8), strokep(G.circle_d(625, 170, 95), GREY, 0.8),
            layer="labels")
    doc.add(label("spirograph_fit(40, 95, 12, 5)", 625, 285, 9), layer="labels")
    doc.add(st(O.rosette(125, 405, 50, 98, lobes=14, lines=10)), layer="ink")
    doc.add(label("rosette lobes=14 lines=10", 125, 520, 9), layer="labels")
    doc.add(st(O.rosette(375, 405, 40, 98, lobes=12, lines=12, phase_span=0.5, mod_lobes=6, mod_amp=0.2,
                         twist=0.25)), layer="ink")
    doc.add(label("modulated + twist", 375, 520, 9), layer="labels")
    doc.add(st(O.rosette_ring(625, 405, 22, 98, bands=3, lobes=(10, 18, 26), lines=8, shape=0.8,
                              auto_lines=True, line_width=FOIL_MIN, min_gap=2.4), "url(#foil)", FOIL_MIN),
            layer="foil")
    doc.add(label("rosette_ring auto_lines (foil 1.6 px)", 625, 520, 9), layer="labels")
    doc.add(st(O.guilloche_frame(40, 550, 670, 260, 26, width=18, wavelength=20, lines=6, auto_lines=True)),
            layer="ink")
    doc.add(st(O.guilloche_band(G.circle_d(240, 680, 70), 16, wavelength=16, lines=6, amps=(1, 0.5)), RED),
            layer="red")
    doc.add(st(O.guilloche_band(G.poly_d([(390, 620), (520, 700), (670, 620)]), 16, wavelength=20, lines=5,
                                shape=0.7)), layer="ink")
    doc.add(label("frame / band on circle / band round a sharp corner", 375, 835, 9), layer="labels")
    doc.add(st(O.wave_lattice(G.rect_d(50, 860, 300, 150, 14), 8, 3, 28)), layer="ink")
    doc.add(st(O.wave_lattice(G.ellipse_d(540, 935, 160, 75), 7, 3.5, 30, angle=25, shape_power=0.7),
               "url(#foil)", FOIL_MIN), layer="foil")
    doc.add(label("wave_lattice", 375, 1030, 9), layer="labels")
    return doc


def sheet_borders():
    doc = sheet("ornament · borders")
    for i, (corner, style) in enumerate([("round", "classic"), ("notch", "triple"), ("step", "deco"),
                                         ("step2", "deco"), ("chamfer", "fine")]):
        x = 18 + i * 145
        doc.add(fillp(O.frame(x, 64, 134, 150, r=22, corner=corner, style=style)), layer="ink")
        doc.add(label(f"{corner} / {style}", x + 67, 232, 8.5), layer="labels")
    doc.add(fillp(O.frame_strip(30, 256, 330, 230, "band", 14, fill="triangles", lw=1.2)), layer="ink")
    doc.add(fillp(O.frame_strip(58, 284, 274, 174, "rope", 12, lw=1.05, corner="rosette")), layer="ink")
    doc.add(fillp(O.frame_strip(84, 310, 222, 122, "beaded", 9, corner="pearl")), layer="ink")
    doc.add(label("frame_strip: band / rope / beaded", 195, 505, 9), layer="labels")
    doc.add(fillp(O.frame_strip(390, 256, 330, 230, "egg_and_dart", 20)), layer="ink")
    doc.add(fillp(O.frame_strip(424, 290, 262, 162, "dentil", 10, corner="diamond")), layer="ink")
    doc.add(fillp(O.greek_key_frame(452, 318, 206, 106, 12, lw=1.4)), layer="ink")
    doc.add(label("egg_and_dart / dentil / greek key", 555, 505, 9), layer="labels")
    doc.add(fillp(O.band(O.frame_path(30, 530, 330, 200, 30, "notch", 10), 12, "triangles", lw=1.05)), layer="ink")
    doc.add(fillp(O.rope(O.frame_path(30, 530, 330, 200, 30, "notch", 32), 9, 6, style="line", lw=1.05)),
            layer="ink")
    doc.add(label("band / rope on a notched path", 195, 750, 9), layer="labels")
    y = 560
    for fill_, col in (("zigzag", INK), ("diamond", RED), ("chevron", INK), ("dots", INK), ("ladder", INK)):
        doc.add(fillp(O.band(f"M400 {y} C 480 {y - 14} 620 {y + 14} 720 {y}", 11, fill_, lw=1.05), col),
                layer="ink")
        y += 34
    doc.add(label("bands", 560, 750, 9), layer="labels")
    for i, st in enumerate(["flower", "daisy", "star"]):
        doc.add(fillp(O.corner_rosette(70 + i * 95, 810, 34, style=st)), layer="ink")
    doc.add(label("corner_rosette", 165, 865, 9), layer="labels")
    rb = O.ribbon(390, 700, 810, 28, sag=-10)
    doc.add(fillp(H.parallel(rb["back"], 45, 3, width=1.05)), fillp(rb["lines"]), layer="ink")
    txt = text_on_path("Cinzel", "CERCA TROVA", 13, rb["path"], variations={"wght": 700}, tracking=260)
    doc.add(fillp(txt, RED), layer="red")
    doc.add(label("ribbon (folds hatched) + text_on_path", 545, 865, 9), layer="labels")
    for i, st in enumerate(["tab", "oval", "ogee", "bracket", "shield"]):
        doc.add(fillp(G.outline(O.cartouche(85 + i * 145, 950, 120, 56 if st != "shield" else 76, st), 1.4)),
                layer="ink")
        doc.add(label(st, 85 + i * 145, 1010, 8.5), layer="labels")
    return doc


def sheet_botanical():
    doc = sheet("ornament · botanical")
    for i, (st, h) in enumerate([("solid", None), ("outline", "half"), ("outline", "full"), ("outline", "veins"),
                                 ("engraved", None), ("outline", None)]):
        doc.add(fillp(O.leaf((45 + i * 118, 205), (115 + i * 118, 70), 42, style=st, hatch=h, lw=1.4)),
                layer="ink")
        doc.add(label(f"{st}{'/' + h if h else ''}", 80 + i * 118, 232, 8.5), layer="labels")
    doc.add(fillp(O.sprig("M40 470 C 120 430 200 340 250 270", count=7, leaf_len=38, leaf_w=15, style="outline",
                          hatch="half", lw=1.4, jitter=0.6, seed=3)), layer="ink")
    doc.add(label("sprig: outline, half hatch, occluded", 150, 500, 9), layer="labels")
    doc.add(fillp(O.laurel("M300 470 C 360 430 420 360 450 280", count=8, berries=4, jitter=0.5)), layer="ink")
    doc.add(label("laurel + berries + jitter", 380, 500, 9), layer="labels")
    doc.add(fillp(O.wreath(615, 375, 95, count=9, jitter=0.4), None), layer="foil")
    doc.add(label("wreath", 615, 500, 9), layer="labels")
    doc.add(fillp(O.grass((90, 730), count=11, height=170, spread=70)), layer="ink")
    doc.add(label("grass", 90, 760, 9), layer="labels")
    doc.add(fillp(O.rice("M250 730 C 250 640 270 580 330 550 C 360 535 382 552 392 585", grains=14,
                         leaves=5, current=40, leaf_len=250, lw=1.2), JADE), layer="ink")
    doc.add(label("rice (texas wild rice) + leaves", 300, 760, 9), layer="labels")
    bb = O.bluebonnet((520, 730), 190, parts=True, whorls=9, width=34)
    doc.add(fillp(bb["stem"], JADE), fillp(O.palmate_leaf((520, 730), -150, 50), JADE), layer="ink")
    doc.add(fillp(bb["flowers"], "#2F4F8F"), fillp(bb["tip"], "#FFFFFF", stroke="#2F4F8F", stroke_width=0.8),
            layer="ink")
    bo = O.bluebonnet((660, 730), 190, whorls=9, width=34, style="outline", lw=1.2)
    doc.add(fillp(bo, INK), fillp(O.palmate_leaf((660, 730), -30, 46, style="outline", lw=1.2)), layer="ink")
    doc.add(label("bluebonnet solid / outline", 590, 760, 9), layer="labels")
    for i, (sh, st) in enumerate([("round", "solid"), ("pointed", "solid"), ("heart", "solid"), ("pointed", "outline")]):
        doc.add(fillp(O.flower(70 + i * 110, 850, 42, shape=sh, style=st, petals=5 if i < 3 else 8),
                      RED if i % 2 == 0 else INK), layer="ink")
    doc.add(label("flower: round / pointed / heart / outline", 235, 915, 9), layer="labels")
    doc.add(fillp(O.ripples(600, 890, 12, count=6, spacing=10)), layer="ink")
    doc.add(label("ripples", 600, 960, 9), layer="labels")
    return doc


def sheet_radiance():
    doc = sheet("ornament · radiance", 620)
    doc.add(fillp(O.sunburst(110, 160, 20, 85, 32, lengths=(1, 0.68))), layer="ink")
    doc.add(label("sunburst spike", 110, 270, 9), layer="labels")
    doc.add(fillp(O.sunburst(300, 160, 12, 85, 56, style="line", lw=1.1, lengths=(1, 0.8, 0.92, 0.7))), layer="ink")
    doc.add(label("sunburst line", 300, 270, 9), layer="labels")
    doc.add(fillp(O.sunburst(475, 160, 0, 80, 24, style="wedge"), RED), layer="red")
    doc.add(label("wedge", 475, 270, 9), layer="labels")
    doc.add(fillp(O.fan(560, 245, 150, 270, 360, 10, rims=(1.0, 0.82), hub=14)), layer="ink")
    doc.add(label("fan", 650, 270, 9), layer="labels")
    doc.add(fillp(O.starburst(110, 400, 70, 22, 8, layers=2)), layer="ink")
    doc.add(label("starburst layers=2", 110, 500, 9), layer="labels")
    doc.add(fillp(O.starburst(270, 400, 60, 16, 4, lw=1.4)), layer="ink")
    doc.add(label("4-point", 270, 500, 9), layer="labels")
    for i, st in enumerate(["lily", "palmette", "heart", "scroll"]):
        doc.add(fillp(O.fleuron(390 + i * 100, 400, 80, style=st), RED if st == "heart" else INK), layer="ink")
        doc.add(label(f"fleuron {st}", 390 + i * 100, 500, 8.5), layer="labels")
    for i, st in enumerate(["lily", "palmette", "heart", "scroll"]):
        doc.add(fillp(O.fleuron(90 + i * 60, 565, 34, style=st, line_style="monoline", lw=1.6)), layer="ink")
    doc.add(label("small fleurons (monoline)", 180, 606, 8.5), layer="labels")
    return doc


def sheet_patterns():
    doc = sheet("ornament · patterns")
    sh = lambda x, y: G.translate("M0 0H200V120C200 180 150 215 100 230C50 215 0 180 0 120Z", x, y)
    fns = [("diaper", lambda s: O.diaper(s, 18)), ("scales", lambda s: O.scales(s, 10)),
           ("quatrefoil", lambda s: O.quatrefoil(s, 28)), ("stripes + pinstripe", lambda s: O.stripes(s, 5, 5, pinstripe=1.05)),
           ("ermine", lambda s: O.ermine(s, 28)), ("chevrons", lambda s: O.chevrons(s, 11, 7)),
           ("checks 45°", lambda s: O.checks(s, 14, angle=45)), ("polka", lambda s: O.polka(s, 12, 2.4)),
           ("tile(fleuron)", lambda s: O.tile(s, O.fleuron(0, 0, 22, style="lily"), 32, 36))]
    for k, (nm, f) in enumerate(fns):
        x = 30 + (k % 3) * 245
        y = 70 + (k // 3) * 325
        s = sh(x, y)
        doc.add(fillp(f(s), [INK, RED, INK][k % 3]), fillp(G.outline(s, 2.1)), layer="ink")
        doc.add(label(nm, x + 100, y + 262, 9), layer="labels")
    return doc


def sheet_suits():
    doc = sheet("suits · pips · indices · layouts")
    cols = {"spade": INK, "heart": RED, "diamond": RED, "club": INK}
    for i, s in enumerate(SU.SUITS):
        x = 95 + i * 185
        doc.add(fillp(SU.pip(s, x, 140, 116), cols[s]), layer="ink")
        w_, h_ = SU.pip_size(s, 116)
        doc.add(label(f"{s} {w_:.0f}×{h_:.0f}", x, 222, 8.5), layer="labels")
        for j, st in enumerate(["outline", "half", "inline", "engraved"]):
            doc.add(fillp(SU.pip(s, x - 66 + j * 44, 272, 38, style=st, lw=1.6), cols[s]), layer="ink")
        doc.add(fillp(SU.pip(s, x, 360, 90, geometry="classic"), cols[s]), layer="ink")
    doc.add(label("headwaters geometry (brief §E.1) · outline / half / inline / engraved · classic", 375, 428, 8.5),
            layer="labels")
    # mini number cards with index + layout
    sc = 0.22
    for k, (rank, suit) in enumerate([("7", "heart"), ("10", "spade"), ("Q", "club")]):
        ox, oy = 40 + k * 180, 450
        parts = [fillp(card.card_outline_d(), "#FFFFFF"), fillp(G.outline(card.card_outline_d(), 3), GREY)]
        idx = SU.index(rank, suit)
        parts.append(fillp(idx["d"], cols[suit]))
        if rank.isdigit():
            for x, y, rot in SU.pip_layout(rank):
                parts.append(fillp(SU.pip(suit, x, y, 116, rot=180 if rot else 0), cols[suit]))
        else:
            cf = SU.court_frame()
            parts += [fillp(cf["outer"]), fillp(cf["inner"], None), fillp(cf["band"])]
            parts.append(fillp(SU.pip(suit, 190, 110.5, 88), cols[suit]))
            parts.append(fillp(G.rotate180(SU.pip(suit, 190, 110.5, 88)), cols[suit]))
        doc.add(svg.g(*parts, transform=svg.tf(svg.translate(ox, oy), svg.scale(sc))), layer="ink")
        doc.add(label(f"{rank} of {suit}s", ox + 375 * sc, oy + 1050 * sc + 16, 8.5), layer="labels")
    doc.add_def(svg.foil_gradient("foil2", FOIL))
    ace = [fillp(card.card_outline_d(), "#FFFFFF"), fillp(G.outline(card.card_outline_d(), 3), GREY),
           fillp(SU.pip("heart", 375, 470, 280, style="inline"), RED),
           fillp(SU.ace_keyline("heart", 375, 470, 280), "url(#foil2)"),
           fillp(SU.index("A", "heart")["d"], RED)]
    doc.add(svg.g(*ace, transform=svg.tf(svg.translate(580, 450), svg.scale(sc))), layer="ink")
    doc.add(label("ace + keyline", 580 + 375 * sc, 450 + 1050 * sc + 16, 8.5), layer="labels")
    # big index detail
    idx = SU.index("10", "diamond", both=False)
    doc.add(svg.g(fillp(idx["d"], RED), transform=svg.tf(svg.translate(60, 760), svg.scale(1.0))), layer="ink")
    idx = SU.index("K", "spade", both=False)
    doc.add(svg.g(fillp(idx["d"]), transform=svg.translate(220, 760)), layer="ink")
    doc.add(label("index(rank, suit): barlow condensed, brief §D.1 metrics", 250, 1010, 8.5), layer="labels")
    for i, n in enumerate(("2", "5", "9")):
        ox = 470 + i * 90
        doc.add(fillp(G.outline(G.rect_d(ox, 790, 75, 105, 4), 1.05), GREY), layer="labels")
        for x, y, rot in SU.pip_layout(n):
            doc.add(fillp(G.translate(G.scale(SU.pip("club", x, y, 116, rot=180 if rot else 0), 0.1, 0.1), ox, 790)),
                    layer="ink")
    doc.add(label("pip_layout(2 / 5 / 9)", 605, 925, 8.5), layer="labels")
    return doc


def sheet_heraldry():
    doc = sheet("heraldry · tinctures · shields · crowns", 760)
    names = ["or", "argent", "gules", "azure", "vert", "purpure", "sable", "tenne", "sanguine"]
    styles = ["heater", "french", "spanish", "swiss", "heater", "heater", "french", "spanish", "swiss"]
    for i, (tn, st) in enumerate(zip(names, styles)):
        x = 60 + (i % 5) * 140
        y = 80 + (i // 5) * 190
        sh = HR.shield(x + 45, y + 60, 90, 110, st)
        doc.add(fillp(HR.tincture(sh, tn)), fillp(G.outline(sh, 2.1, join="miter")), layer="ink")
        doc.add(label(f"{tn} · {st}", x + 45, y + 140, 8.5), layer="labels")
    for i, st in enumerate(["lozenge", "roundel", "oval"]):
        sh = HR.shield(560 + i * 60, 470, 44, 60, st)
        doc.add(fillp(HR.tincture(sh, ["gules", "azure", "vert"][i], spacing=4.2)),
                fillp(G.outline(sh, 1.6)), layer="ink")
    doc.add(label("lozenge / roundel / oval", 620, 520, 8.5), layer="labels")
    for i, st in enumerate(["royal", "ducal", "mural", "eastern"]):
        doc.add(fillp(HR.crown(110 + i * 175, 640, 140, style=st), FOIL if i % 2 else INK), layer="ink")
        doc.add(label(f"crown '{st}'", 110 + i * 175, 675, 8.5), layer="labels")
    doc.add(fillp(HR.crown(665, 360, 96, style="royal", line_style="outline")), layer="ink")
    doc.add(label("outline crown", 665, 385, 8.5), layer="labels")
    return doc


def sheet_type():
    doc = sheet("typeset")
    fonts = [("Cinzel", {"wght": 700}), ("CinzelDecorative-Bold", None), ("PlayfairDisplaySC-Bold", None),
             ("PlayfairDisplay", {"wght": 900}), ("CormorantGaramond", {"wght": 600}), ("EBGaramond", {"wght": 500}),
             ("IMFeENsc28P", None), ("BodoniModa", {"wght": 800, "opsz": 60}), ("BarlowCondensed-SemiBold", None),
             ("RobotoSlab", {"wght": 700})]
    for i, (f, v) in enumerate(fonts):
        y = 100 + i * 44
        d, _, _ = text_to_path(f, "San Marcos River", 30, 60, y, variations=v)
        doc.add(fillp(d), layer="ink")
        doc.add(label(f + (" " + ",".join(f"{k}={int(x)}" for k, x in v.items()) if v else ""), 690, y - 6, 8,
                      anchor="end"), layer="labels")
    y = 570
    for i, a in enumerate(("start", "middle", "end")):
        yy = y + i * 34
        d, bb, _ = text_to_path("Cinzel", f"ANCHOR {a.upper()}", 20, 375, yy, anchor=a, variations={"wght": 600})
        doc.add(fillp(d), layer="ink")
    doc.add(strokep("M375 545V650", RED, 1.05), layer="red")
    y = 700
    doc.add(strokep(f"M40 {y}H710", RED, 1.05), layer="red")
    for i, b in enumerate(("alphabetic", "middle", "top", "bottom")):
        d, _, _ = text_to_path("PlayfairDisplaySC-Bold", b, 22, 60 + i * 170, y, baseline=b)
        doc.add(fillp(d), layer="ink")
    for i, tr in enumerate((0, 150, 400)):
        d, _, _ = text_to_path("Cinzel", "TRACKING", 18, 130 + i * 245, 780, anchor="middle",
                               variations={"wght": 700}, tracking=tr)
        doc.add(fillp(d), layer="ink")
        doc.add(label(f"tracking={tr}", 130 + i * 245, 800, 8), layer="labels")
    d1, _, a1 = text_to_path("PlayfairDisplay", "AVATAR Wo", 30, 60, 860, variations={"wght": 700}, kerning=False)
    d2, _, a2 = text_to_path("PlayfairDisplay", "AVATAR Wo", 30, 400, 860, variations={"wght": 700}, kerning=True)
    doc.add(fillp(d1, GREY), fillp(d2), layer="ink")
    doc.add(label("kerning off", 140, 880, 8), label("kerning on (GPOS)", 480, 880, 8), layer="labels")
    doc.add(fillp(text_on_arc("Cinzel", "· SAN MARCOS · TEXAS ·", 17, 200, 975, 60, variations={"wght": 700},
                              tracking=120), RED), layer="red")
    doc.add(fillp(text_on_arc("Cinzel", "EST 1851", 14, 200, 975, 60, bottom=True, variations={"wght": 700},
                              tracking=200), INK), layer="ink")
    doc.add(strokep(G.circle_d(200, 975, 60), GREY, 0.8), layer="labels")
    wave = "M380 990 C 450 930 520 1030 600 970 S 690 950 720 980"
    doc.add(strokep(wave, GREY, 0.8), layer="labels")
    doc.add(fillp(text_on_path("EBGaramond", "the river runs clear & cold", 17, wave, variations={"wght": 500},
                               offset=4, baseline="alphabetic")), layer="ink")
    return doc


def sheet_card():
    doc = sheet("card", 800)
    s = 0.28

    def mini(x, y, content):
        return svg.g(content, transform=svg.tf(svg.translate(x, y), svg.scale(s)))

    y0 = 72
    under = y0 + 1050 * s + 20
    c1 = [fillp(card.card_outline_d(), "#FFFFFF"), strokep(card.card_outline_d(), INK, 2), card.safe_zone(True)]
    doc.add(mini(45, y0, c1), layer="ink")
    doc.add(label("card_outline_d + safe_zone", 45 + 375 * s, under, 8.5), layer="labels")
    box = (70, 90, 610, 870)
    half = [fillp(G.translate(G.star_d(0, 0, 90, 34, 5), 375, 330), RED),
            fillp(O.filigree_corner(160, 2, x=70, y=90)), fillp(O.filigree_corner(160, 2, x=680, y=90, corner="tr")),
            fillp(text_to_path("Cinzel", "HALF", 60, 375, 200, anchor="middle", variations={"wght": 700})[0])]
    for k, (div, x) in enumerate((("h", 270), ("diag", 495))):
        court = [fillp(card.card_outline_d(), "#FFFFFF"), card.two_headed("\n".join(half), divider=div, box=box),
                 strokep(G.rect_d(*box), INK, 3)]
        doc.add(mini(x, y0, court), layer="ink")
        doc.add(label(f"two_headed(divider='{div}')", x + 375 * s, under, 8.5), layer="labels")
    glyph = fillp(text_to_path("PlayfairDisplaySC-Bold", "K", 80, 0, 0)[0])
    yk = 520
    g1 = svg.g(glyph, transform=svg.translate(95, yk))
    doc.add(g1, layer="ink")
    doc.add(card.rot180(g1, 165, yk + 8), layer="red")
    doc.add(label("rot180(content, cx, cy)", 150, yk + 105, 8.5), layer="labels")
    g2 = svg.g(glyph, transform=svg.translate(300, yk))
    doc.add(g2, layer="ink")
    doc.add(card.mirror(svg.g(glyph, transform=svg.translate(300, yk)), 390), layer="red")
    doc.add(strokep(f"M390 {yk - 70}V{yk + 10}", GREY, 0.8, stroke_dasharray="3 3"), layer="labels")
    doc.add(label("mirror(content, axis)", 390, yk + 105, 8.5), layer="labels")
    clip = card.clip_group(fillp(H.parallel(G.rect_d(0, 0, 750, 1050), 45, 14, width=5), RED),
                           card.card_outline_d(40), doc=doc)
    doc.add(mini(520, 400, [fillp(card.card_outline_d(), "#FFFFFF"), clip]), layer="ink")
    doc.add(label("clip_group(..., doc=doc) unique ids", 520 + 375 * s, 400 + 1050 * s + 20, 8.5),
            layer="labels")
    doc.add(label("render() = rsvg-convert  ·  contact_sheet() = PIL (see index.png)", 375, 760, 9),
            layer="labels")
    return doc


SHEETS = {
    "showpiece": showpiece,
    "svg": sheet_svg,
    "geom": sheet_geom,
    "print": sheet_print,
    "stroke": sheet_stroke,
    "styles": sheet_styles,
    "hatch": sheet_hatch,
    "scroll": sheet_scroll,
    "guilloche": sheet_guilloche,
    "borders": sheet_borders,
    "botanical": sheet_botanical,
    "radiance": sheet_radiance,
    "patterns": sheet_patterns,
    "suits": sheet_suits,
    "heraldry": sheet_heraldry,
    "type": sheet_type,
    "card": sheet_card,
}


def main(names=None):
    os.makedirs(OUT, exist_ok=True)
    names = names or list(SHEETS)
    pngs = []
    for n in names:
        t0 = time.time()
        doc = SHEETS[n]()
        svg_path = os.path.join(OUT, f"{n}.svg")
        png_path = os.path.join(OUT, f"{n}.png")
        doc.save(svg_path)
        card.render(svg_path, png_path, 1500)
        if n == "showpiece":
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                seps = doc.save_layers(os.path.join(OUT, "showpiece-sep"), trap=0.0)
            for f in seps:
                card.render(f, f[:-4] + ".png", 750, background="#FFFFFF")
            card.contact_sheet([png_path] + [f[:-4] + ".png" for f in seps],
                               os.path.join(OUT, "showpiece-plates.png"), cols=4, gap=20, bg="#2B2B2B",
                               cell_width=500)
            rep = PF.preflight(doc, profiles={"foil": "foil"}, overlay=os.path.join(OUT, "showpiece-preflight"))
            print(PF.summary(rep))
            fit_path = os.path.join(OUT, "showpiece-fitted.svg")
            doc.save(fit_path, fit=0.05)
            print(f"  fitted: {os.path.getsize(svg_path) // 1024} KB -> {os.path.getsize(fit_path) // 1024} KB")
        pngs.append(png_path)
        print(f"{n:10s} {time.time() - t0:5.1f}s  {os.path.getsize(svg_path) / 1024:7.0f} KB  -> {png_path}")
    if set(names) == set(SHEETS):
        card.contact_sheet([os.path.join(OUT, f"{n}.png") for n in SHEETS], os.path.join(OUT, "index.png"),
                           cols=6, gap=30, bg="#2B2B2B", cell_width=500)
        print("index      ->", os.path.join(OUT, "index.png"))
    return pngs


if __name__ == "__main__":
    main(sys.argv[1:] or None)
