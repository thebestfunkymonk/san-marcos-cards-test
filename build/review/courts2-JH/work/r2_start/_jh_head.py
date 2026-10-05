"""art/_jh_head.py — the J♥ Spring Minstrel's headgear and hair (v3).

    soft_beret   the jade beret as a soft full disc (explicit spline points),
                 tilted back on a band that hugs the skull; the overhang's
                 underside half-hatched, ripple rings round a gold button on
                 the crown (the spring seen from above), gold bead piping on
                 the band
    plume        one long curling ostrich plume of gold current lines:
                 a smooth tapered crescent whose tip rolls into a volute,
                 current lines combed along its outer edge
    bob          the page-boy bob behind the ear, rolled under at the nape
"""
from __future__ import annotations

from dataclasses import replace

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Point, Polygon

from deck import courtkit as K
from deck.motifs import core as C
from deck.motifs import forms as FM
from art import _jh_parts as JP

P = K.P
MED, FINE, RULE, CON = K.MEDIUM, K.FINE, K.RULE, K.CONTOUR
INK, RED, JADE, GOLD = K.INK, K.RED, K.JADE, K.GOLD


def _strip(f0, f1, h, ext=40.0):
    """The strip ``h`` px above the line f0 → f1 (screen-up of travel for a
    left-to-right line), extended ``ext`` past both ends."""
    f0, f1 = P(f0), P(f1)
    u = (f1 - f0) / np.hypot(*(f1 - f0))
    nn = np.array([u[1], -u[0]])
    return Polygon([f0 - u * ext, f1 + u * ext, f1 + u * ext + nn * h, f0 - u * ext + nn * h]), u, nn


def _hatch_upto(f, x1):
    """Keep only the hatch strokes (subpaths 'M x y L x y') lying wholly left of x = x1."""
    out = []
    for m in f.marks:
        segs = [q for q in m.d.split("M") if q.strip()]
        keep = []
        for q in segs:
            nums = [float(v) for v in q.replace("L", " ").replace(",", " ").split()]
            if max(nums[0::2]) <= x1:
                keep.append("M" + q)
        if keep:
            out.append(replace(m, d="".join(keep)))
    return C.Frag(out, f.meta)


def soft_beret(disc_pts, band_lo, band_h, skull, *, button=None, button_d=8.4, rings=(), ring_tilt=0.0,
               under_hatch=0.0, hatch_angle=-50.0, beads=False, bead_d=6.3, bead_gap=4.6, headings=None,
               ripple=(14.0, 2.4), under_x1=None):
    """The jade beret.

    disc_pts  closed spline points of the soft disc (clockwise from the
              front lip).
    band_lo   (front, back) bottom edge of the band; the band is ``band_h``
              tall and clipped to the ``skull`` region grown 2.5 px.
    rings     [(rx, ry), ...] flattened ripple rings round the ``button``
              (FINE Aquifer on jade), kept whole or dropped.
    The part of the disc below its own rim line where it overhangs the band
    at the back (its underside) is half-hatched; the band carries gold bead
    piping on its mid-line (solid gold, Aquifer contour)."""
    d_disc, disc = JP.spline_region(disc_pts, headings)
    strip, u, nn = _strip(band_lo[0], band_lo[1], band_h)
    band = strip.intersection(skull.buffer(2.5, quad_segs=24))
    shape = JP.biggest(K.U(disc, band).buffer(3.0, quad_segs=12).buffer(-3.0, quad_segs=12))
    band_vis = JP.biggest(band.difference(disc))
    fills = K.fill(shape, JADE)
    lines = K.outline(shape)
    lines += K.clip_in(K.outline(disc), band.buffer(-0.4))      # the disc's rim over the band
    extra = C.Frag()
    if beads and not band_vis.is_empty:
        f0, f1 = P(band_lo[0]), P(band_lo[1])
        mid0, mid1 = f0 + nn * band_h / 2 - u * 30, f1 + nn * band_h / 2 + u * 30
        mp = np.array([mid0 + (mid1 - mid0) * t for t in np.linspace(0, 1, 200)])
        keep = band_vis.buffer(-(MED / 2 + K.GAP_MARK + 0.05))
        extra += JP.bead_chain(mp, d=bead_d, gap=bead_gap, keep=keep)
    if under_hatch:
        # the droop's underside, half-hatched (§B.2 tone): the crescent between the disc's lower rim
        # and the same rim lifted ``under_hatch`` px, behind the band
        lift = shapely.affinity.translate(disc, 0.0, -under_hatch)
        cres = disc.difference(lift).difference(band.buffer(0.5))
        f0, f1 = P(band_lo[0]), P(band_lo[1])
        x1 = 800.0 if under_x1 is None else float(under_x1)
        cres = cres.intersection(K.box(float(f1[0]) - 10.0, 0.0, 800.0, 800.0))
        cres = JP.biggest(cres)
        if not cres.is_empty:
            hz = cres.buffer(-0.2)
            # whole hatch strokes only, none in the crescent's tail past ``under_x1`` (where the
            # fold converges on the contour a hatch runs nearly parallel to it: a jade wedge)
            extra += _hatch_upto(K.hatch_in(hz, angle=hatch_angle), x1)
            extra += K.clip_in(K.line(K.D(LineString(np.asarray(lift.exterior.coords))), MED, role="fold"),
                               disc.buffer(-(CON / 2 + 0.1)).intersection(K.box(float(f1[0]) - 10.0, 0, x1 + 6.0, 800)))
    if ripple and not band_vis.is_empty:
        # the band's trim: a FINE ripple line (§F.1's ♥ ripple, small) along its mid-line
        lam, amp = ripple
        f0, f1 = P(band_lo[0]), P(band_lo[1])
        L = float(np.hypot(*(f1 - f0))) + 80.0
        ss = np.linspace(-40.0, L - 40.0, int(L * 2))
        base = f0 + nn * band_h / 2
        pts = np.array([base + u * t + nn * amp * math.sin(2 * math.pi * t / lam) for t in ss])
        zone = band_vis.buffer(-(MED / 2 + K.GAP_MARK + FINE / 2 + 0.1))
        extra += K.clip_in(C.stroke(C.polyline_d(pts), FINE, role="ripple"), zone)
    if rings and button is not None:
        bx, by = button
        zone = disc.buffer(-(CON / 2 + K.GAP_MARK + FINE / 2 + 0.2))
        for rx_, ry_ in rings:
            e = C.stroke(C.ellipse_arc_d(bx, by, rx_, ry_, 0, 360), FINE, role="ripple")
            e = e.rotate(ring_tilt, bx, by) if ring_tilt else e
            if zone.contains(K.R(K.G.from_skia(e.marks[0].skia()))):
                extra += e
    if button is not None and button_d:
        g = Point(*button).buffer(button_d / 2, quad_segs=16)
        extra += K.fill(g, GOLD, role="button") + K.outline(g, FINE, role="button")
    return K.Part(shape, fills, lines + extra, {"disc": disc, "band": band, "band_vis": band_vis})


def plume(guide_pts, *, h_start=None, hw_root=4.0, hw_max=17.0, belly=0.34, hw_tip=7.5, tip_curl=(12.0, 250.0), tip_round=None,
          n=3, stagger=16.0, curl_r=4.4, curl_deg=100.0, side=+1, first=None):
    """One long curling plume: a smooth tapered crescent along the open arc
    spline ``guide_pts`` (quill → tip) whose tip rolls on into a curl
    (``tip_curl`` = radius, degrees, turning toward ``side``) — the plume's
    end drooping into a volute. ``n`` current lines run along the OUTER edge
    (the ``-side`` edge) and end staggered in rolled Ø6.3 terminals."""
    _, gp = JP.open_spline(guide_pts, h_start=h_start)
    if tip_curl:
        gp = K._curl(gp, side, tip_curl[0], tip_curl[1])
    cv = K.G.Curve(gp)
    L = cv.length

    def hw(t):
        if t < belly:
            return hw_root + (hw_max - hw_root) * math.sin(math.pi / 2 * t / belly)
        return hw_tip + (hw_max - hw_tip) * math.cos(math.pi / 2 * (t - belly) / (1 - belly)) ** 1.2
    reg, left, right, pts = JP.ribbon(gp, hw, tip_round=hw_tip if tip_round is None else tip_round, root_round=hw_root)
    outer = right if side > 0 else left          # side +1 curls screen-left: the outer edge is screen-right
    lines = K.current_lines(outer[: int(len(outer) * 0.97)], n, reg, side=side, edge=CON, stagger=stagger,
                            curl_r=curl_r, curl_deg=curl_deg, first=first)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + lines, {"guide": pts, "L": L})


def bob(outline_pts, guide_pts, *, n=4, side=-1, stagger=7.0, curl_r=4.4, curl_deg=110.0, headings=None,
        h_start=None, h_end=None, filler=None, around=()):
    """The gold page-boy bob: region through ``outline_pts`` (∪ ``filler``,
    e.g. the skull under the beret); current lines are offsets of
    ``guide_pts`` (drawn from the crown down to the roll), rolling into
    terminals at the roll."""
    _, reg = JP.spline_region(outline_pts, headings)
    if filler is not None:
        reg = JP.biggest(K.U(reg, filler).buffer(2.0).buffer(-2.0))
    if around:
        # close any paper pocket the bob leaves against the head / collar (a hole in the figure
        # silhouette would be stroked solid at CONTOUR)
        u_ = K.U(reg, *around)
        pockets = [Polygon(r) for p_ in K._polys_of(u_) for r in p_.interiors]
        pockets = [q for q in pockets if q.area < 400 and q.distance(reg) < 0.5]
        if pockets:
            reg = JP.biggest(K.U(reg, *[q.buffer(0.8) for q in pockets]))
    _, gp = JP.open_spline(guide_pts, h_start=h_start, h_end=h_end)
    lines = K.current_lines(gp, n, reg, side=side, edge=CON, stagger=stagger, curl_r=curl_r, curl_deg=curl_deg)
    return K.Part(reg, K.fill(reg, GOLD), K.outline(reg) + lines, {"n_lines": len(lines.meta.get("lines", []))})
