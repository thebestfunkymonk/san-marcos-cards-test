"""Shared constants and helpers for the tuck box (brief §B.1, §D, §H.20).

Units are print px at 300 ppi (1 px = 1/300 in), y down, as everywhere in the
deck.  Every panel is authored in its OWN local frame (0,0 = the panel's
top-left fold/cut corner); ``_tuck_flat`` places the panels on the dieline
with rigid translations / 180° rotations only (nothing is ever scaled).

Print plates (one SVG group each, bottom to top):

* ``board``   the Deep Hole stock (#0F2B29) as a flat rectangle — the substrate
              (uncoated / soft-touch board), extended by the 37.5 px bleed on flats;
* ``emboss``  blind-emboss tooling areas as filled shapes (non-printing plate,
              drawn in a tooling colour so it can never be mistaken for ink);
* ``foil``    the ONE gold foil (flat #B08D57 in print files);
* ``dieline`` (flat only) cut = solid, fold = dashed, in registration magenta,
              non-printing.
"""
from __future__ import annotations

import hashlib
import math
import os
import subprocess
from pathlib import Path

import numpy as np

from deck import tokens as T
from deck import frames as F
from deck.motifs import core as C
from inkkit import geom as G
from inkkit.svg import fmt

ROOT = Path(__file__).resolve().parent.parent
TUCK = ROOT / "tuck"
OUT = ROOT / "build" / "tuck"
DEV = OUT / "dev"
CACHE = OUT / ".cache"

# ---- §B.1 box geometry -------------------------------------------------------
PW, PH = 769.0, 1069.0          # front / back panel (2.5625 × 3.5625 in)
DEPTH = 225.0                   # 0.75 in: side panels and end panels
PCX, PCY = PW / 2, PH / 2       # 384.5, 534.5
BLEED = 37.5
NOTCH_R = 70.0                  # thumb notch on the BACK panel's top edge (0.47 in wide; printer's dieline rules)
NOTCH_CLEAR = 9.0               # foil keeps this far from the notch cut (die tolerance)

FOIL, BOARD = T.FOIL, T.BOARD

# panel frame (front and back share it): the card back's frame vocabulary at 1:1
FRAME_OUTER = 34.0              # outer RULE centreline, inset from the fold
FRAME_COMPANION = 42.0          # FINE companion, 8 px inside
FRAME_BAND_Y = 76.0             # inner rule of the top/bottom bands (34 px bands, as the back)
FRAME_BAND_X = 64.0             # inner rule of the side bands (22 px bands, as the back)
FINE, HAIR, MED, RULE = T.FINE, T.HAIRLINE, T.MEDIUM, T.RULE
GAP = C.MIN_CLEAR               # 4.2: clear gap between parallel foil strokes (foil fills in)

EMBOSS_TOOL = "#7FA7C9"         # tooling colour for the blind-emboss plate (non-printing)
EMBOSS_TOOL_2 = "#4E7FA8"       # second emboss level (sculpted), same plate
DIE_REG = "#EC008C"             # registration magenta for the dieline (non-printing)

FONT_MICRO = str(T.FONT_INDEX)          # Barlow Condensed SemiBold
FONT_SIDE = str(T.FONT_MICRO_MEDIUM)    # Barlow Condensed Medium (tuck sides, cap >= 18)
FONT_SLAB = str(T.FONT_SLAB)            # Roboto Slab @ wght 700


# ---- type (all outlined; §D) ---------------------------------------------------
def type_fill(text: str, cap: float, baseline: float, tracking: float, x: float = PCX, *,
              font: str = FONT_MICRO, variations=None, anchor: str = "middle"):
    """Outlined type as a foil FILL Frag, optically centred (the trailing
    tracking is excluded from the centring).  Returns (Frag, ink bbox)."""
    size = F.cap_to_size(font, cap, variations)
    from inkkit.typeset import text_to_path
    d, bb, adv = text_to_path(font, text, size, 0.0, baseline, anchor="start", variations=variations,
                              tracking=tracking)
    ink_w = bb[2] - bb[0]
    if anchor == "middle":
        dx = x - (bb[0] + ink_w / 2)
    elif anchor == "start":
        dx = x - bb[0]
    else:
        dx = x - bb[2]
    d = G.translate(d, dx, 0.0)
    bb = (bb[0] + dx, bb[1], bb[2] + dx, bb[3])
    return C.fill(d, color=FOIL, role="type"), bb


def em_rules(bb, cap: float, *, length: float = 24.0, gap: float = 10.0, w: float = FINE,
             terminals: bool = False) -> C.Frag:
    """§D micro-type em-rules: FINE, 24 px long, 10 px from the ink, on the cap middle."""
    x0, y0, x1, y1 = bb
    ym = y1 - cap / 2
    f = C.stroke(C.polyline_d([(x0 - gap - length, ym), (x0 - gap, ym)])
                 + C.polyline_d([(x1 + gap, ym), (x1 + gap + length, ym)]), w, style="rule", color=FOIL,
                 role="emrule")
    if terminals:
        f += C.terminal(x0 - gap - length, ym, color=FOIL) + C.terminal(x1 + gap + length, ym, color=FOIL)
    return f


# ---- geometry helpers ------------------------------------------------------------
def rect_lines(x0, y0, x1, y1) -> str:
    """Four separate straight runs (butt caps) of a rectangle."""
    return (C.polyline_d([(x0, y0), (x1, y0)]) + C.polyline_d([(x0, y1), (x1, y1)])
            + C.polyline_d([(x0, y0), (x0, y1)]) + C.polyline_d([(x1, y0), (x1, y1)]))


def drop_short(f: C.Frag, min_len: float, roles=None) -> C.Frag:
    """Remove open stroke pieces shorter than ``min_len`` (stubs left by cuts)."""
    from dataclasses import replace
    out = []
    for m in f.marks:
        if m.kind != "stroke" or (roles is not None and m.role not in roles):
            out.append(m)
            continue
        keep = [(p, cl) for p, cl in G.flatten(m.d, 0.05)
                if cl or (len(p) > 1 and G.Curve(p).length >= min_len)]
        if keep:
            out.append(replace(m, d="".join(C.polyline_d(p, closed=cl) for p, cl in keep)))
    return C.Frag(out, f.meta)


def gold(f: C.Frag) -> C.Frag:
    return f.recolor(FOIL)


# ---- SVG assembly ----------------------------------------------------------------
def foil_svg(f: C.Frag) -> str:
    """The foil plate's elements (strokes keep their legal widths; type and
    dots are fills), all in flat Lion Gold."""
    return f.svg("gold")


def svg_doc(w: float, h: float, *, board: str | None = None, emboss: list | None = None, foil: str = "",
            dieline: str = "", view=None, title: str = "", notes: list[str] | None = None,
            extra_defs: str = "", hidden: tuple = ()) -> str:
    """Assemble a print SVG with the plate groups.  ``emboss`` is a list of
    (d, level) filled tooling shapes; ``board`` a FILL d (default: the whole
    view box)."""
    vx, vy, vw, vh = view if view else (0.0, 0.0, w, h)
    parts = [f'<?xml version="1.0" encoding="UTF-8"?>',
             f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(vw)}" height="{fmt(vh)}" '
             f'viewBox="{fmt(vx)} {fmt(vy)} {fmt(vw)} {fmt(vh)}">']
    if title:
        parts.append(f"<title>{title}</title>")
    if notes:
        parts.append("<desc>" + "\n".join(n.replace("&", "&amp;").replace("<", "&lt;") for n in notes) + "</desc>")
    if extra_defs:
        parts.append(f"<defs>{extra_defs}</defs>")
    bd = board if board is not None else G.rect_d(vx, vy, vw, vh)
    parts.append(f'<g id="board" data-plate="substrate: Deep Hole board {BOARD}">'
                 f'<path d="{bd}" fill="{BOARD}"/></g>')
    vis = ' style="display:none"' if "emboss" in hidden else ""
    em = []
    for d, level in (emboss or []):
        col = EMBOSS_TOOL if level == 1 else EMBOSS_TOOL_2
        em.append(f'<path d="{d}" fill="{col}" data-emboss-level="{level}"/>')
    parts.append(f'<g id="emboss" data-plate="blind emboss tooling (non-printing); level 1 = plateau, '
                 f'level 2 = sculpted"{vis}>' + "".join(em) + "</g>")
    parts.append(f'<g id="foil" data-plate="gold foil {FOIL} (one foil only)">{foil}</g>')
    if dieline:
        parts.append(f'<g id="dieline" data-plate="dieline (non-printing): cut = solid, fold = dashed">'
                     f"{dieline}</g>")
    parts.append("</svg>")
    return "\n".join(parts)


def write(path: Path, text: str) -> Path:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def render(svg_path, png_path, width: int | None = None, *, zoom: float | None = None) -> Path:
    png_path = Path(png_path)
    png_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["rsvg-convert", "-o", str(png_path)]
    if width:
        cmd += ["-w", str(int(width))]
    elif zoom:
        cmd += ["-z", str(zoom)]
    subprocess.run(cmd + [str(svg_path)], check=True)
    return png_path


def src_hash(*paths) -> str:
    h = hashlib.sha1()
    for p in paths:
        for f in sorted(Path(p).glob("*.py")) if Path(p).is_dir() else [Path(p)]:
            h.update(f.read_bytes())
    return h.hexdigest()[:16]


# ---- near-touch healing (§I.12: lines either JOIN or keep >= 3 px apart) -------------------------
def heal(f: C.Frag, gap: float = 3.0, *, head_on: float = 70.0, max_extend: float = 3.2, passes: int = 2,
         skip_roles=()) -> C.Frag:
    """Close hair-gaps at stroke ENDS: an open end whose cap comes within
    (0.08, ``gap``) px of another mark (or of its own line further back) is
    EXTENDED along its tangent until it overlaps that mark by 0.45 px when it
    points at it (a T-junction that stopped short: hatch against a contour,
    a line against the part in front), otherwise TRIMMED back until it keeps
    ``gap`` px clear.  Only the touched marks are rewritten (as polylines);
    everything else keeps its exact arcs."""
    import shapely
    import shapely.ops
    from shapely.geometry import LineString, Point
    from dataclasses import replace

    for _ in range(passes):
        subs = []
        for i, m in enumerate(f.marks):
            if m.kind == "stroke" and m.role not in skip_roles:
                for pts, cl in G.flatten(m.d, 0.05):
                    subs.append([i, np.asarray(pts, float), bool(cl)])
            else:
                subs.append([i, None, None])
        geoms = []
        for i, pts, cl in subs:
            m = f.marks[i]
            if pts is None:
                geoms.append(C.region(m.d) if m.kind == "fill" else shapely.union_all(
                    [LineString(p).buffer(m.w / 2) for p, _ in G.flatten(m.d, 0.1) if len(p) > 1]))
            elif len(pts) < 2:
                geoms.append(Point(pts[0]).buffer(m.w / 2))
            else:
                geoms.append(LineString(pts).buffer(m.w / 2, cap_style="round" if m.cap == "round" else "flat"))
        tree = shapely.STRtree(geoms)
        changed = set()
        for k, (i, pts, cl) in enumerate(subs):
            if pts is None or cl or len(pts) < 2:
                continue
            m = f.marks[i]
            seg = np.hypot(*np.diff(pts, axis=0).T)
            Ltot = float(seg.sum())
            for end in (1, 0):
                P = subs[k][1] if end == 1 else subs[k][1][::-1]
                if len(P) < 2:
                    continue
                p = P[-1]
                # tangent from a point ~1.5 px back
                cum = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P[::-1], axis=0).T))])
                j = int(np.searchsorted(cum, 1.5))
                j = min(max(j, 1), len(P) - 1)
                t = P[-1] - P[::-1][j]
                nt = float(np.hypot(*t))
                if nt < 1e-9:
                    continue
                t = t / nt
                cap = Point(p).buffer(m.w / 2, quad_segs=8)
                best, bg = 1e9, None
                for c in tree.query(cap.buffer(gap + 1.0)):
                    if c == k:
                        if Ltot < 12.0:
                            continue
                        # own line more than 8 px back from this end
                        cum_f = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
                        keep = P[cum_f <= Ltot - 8.0]
                        if len(keep) < 2:
                            continue
                        g = LineString(keep).buffer(m.w / 2)
                    else:
                        g = geoms[c]
                    dd = cap.distance(g)
                    if dd < best:
                        best, bg = dd, g
                if bg is None or not (0.08 < best < gap):
                    continue
                q = np.asarray(shapely.ops.nearest_points(Point(p), bg)[1].coords[0])
                v = q - p
                ang = math.degrees(math.acos(max(-1.0, min(1.0, float(np.dot(v, t) / (np.hypot(*v) + 1e-9))))))
                if ang < head_on and best <= max_extend:
                    P2 = np.vstack([P, p + t * (best + 0.45)])
                else:
                    cut_len = gap - best + 0.25
                    cum_f = np.concatenate([[0.0], np.cumsum(np.hypot(*np.diff(P, axis=0).T))])
                    L = cum_f[-1]
                    if L - cut_len < 1.0:
                        P2 = P[:1]
                    else:
                        keep = P[cum_f < L - cut_len]
                        tail_pt = G.Curve(P).at_s(L - cut_len)
                        P2 = np.vstack([keep, tail_pt])
                subs[k][1] = P2 if end == 1 else P2[::-1]
                changed.add(i)
        if not changed:
            break
        out = []
        for i, m in enumerate(f.marks):
            if i not in changed:
                out.append(m)
                continue
            parts = [(pts, cl) for (ii, pts, cl) in subs if ii == i and pts is not None and len(pts) >= 2]
            if parts:
                out.append(replace(m, d="".join(C.polyline_d(p, closed=cl) for p, cl in parts)))
        f = C.Frag(out, f.meta)
    return f


TYPE_ROLES = ("type", "wordmark")


def type_hull(f: C.Frag):
    """The type of ``f`` with its counters filled (each glyph piece's exterior):
    a board hole inside it is a letter's counter."""
    import shapely
    typ = C.Frag([m for m in f.marks if m.role in TYPE_ROLES])
    if not len(typ):
        return None
    sh = typ.shape()
    return shapely.union_all([shapely.Polygon(g.exterior) for g in getattr(sh, "geoms", [sh])]).buffer(-0.3)


def plug(f: C.Frag, ko: float = 2.5, max_area: float = 25.0) -> C.Frag:
    """Fill board 'traps' the foil would close anyway: enclosed holes in the
    stamped foil (the exact union) narrower than ``ko`` (the §I.12 knockout
    minimum) and smaller than ``max_area`` px² become solid foil (a FILL
    patch 0.3 px over the hole) — prepress trap-filling where three lines
    converge (hatch in a corner, a pedicel meeting its stalk).  Counters of
    TYPE are never touched."""
    import shapely
    sh = f.shape()
    tsh = type_hull(f)
    patches = []
    for g in getattr(sh, "geoms", [sh]):
        for ring in g.interiors:
            hole = shapely.Polygon(ring)
            if hole.area > max_area:
                continue
            if tsh is not None and tsh.contains(hole) and hole.area >= 1.5:
                continue                                  # a letter's counter
            w = 2 * shapely.maximum_inscribed_circle(hole, 0.02).length if hole.area > 0.01 else 0.0
            if w < ko:
                patches.append(hole.buffer(0.3, join_style="mitre"))
    if not patches:
        return f
    return f + C.fill(G.from_shape(shapely.union_all(patches)), color=FOIL, role="trap")


def prune_parallel(f: C.Frag, obstacle, gap: float = 4.2, min_run: float = 6.0, step: float = 0.4) -> C.Frag:
    """Remove the runs of ``f``'s stroke centrelines that travel ALONGSIDE
    ``obstacle`` (shapely: the outline of the strokes in front) closer than
    ``gap`` px edge to edge for at least ``min_run`` px — where a line
    emerging from behind another would otherwise hug it (§I.12 parallel
    strokes >= 4.2).  Head-on T-junctions (short close runs) are kept."""
    import shapely
    from dataclasses import replace
    if obstacle is None or obstacle.is_empty:
        return f
    out = []
    for m in f.marks:
        if m.kind != "stroke":
            out.append(m)
            continue
        keep_parts = []
        touched = False
        for pts, cl in G.flatten(m.d, 0.05):
            pts = np.asarray(pts, float)
            if len(pts) < 2:
                continue
            if cl:
                pts = np.vstack([pts, pts[:1]])
            cv = G.Curve(pts)
            n = max(2, int(cv.length / step) + 1)
            ss = np.linspace(0, cv.length, n)
            P = cv.at_s(ss)
            d = shapely.distance(shapely.points(P), obstacle) - m.w / 2
            close = d < gap - 0.05
            if not close.any():
                keep_parts.append((pts, cl))
                continue
            # runs of close samples
            kill = np.zeros(n, bool)
            i = 0
            while i < n:
                if close[i]:
                    j = i
                    while j + 1 < n and close[j + 1]:
                        j += 1
                    if ss[j] - ss[i] >= min_run:
                        kill[i:j + 1] = True
                    i = j + 1
                else:
                    i += 1
            if not kill.any():
                keep_parts.append((pts, cl))
                continue
            touched = True
            i = 0
            while i < n:
                if not kill[i]:
                    j = i
                    while j + 1 < n and not kill[j + 1]:
                        j += 1
                    if ss[j] - ss[i] > 1.0:
                        keep_parts.append((P[i:j + 1], False))
                    i = j + 1
                else:
                    i += 1
        if not keep_parts:
            continue
        if touched:
            out.append(replace(m, d="".join(C.polyline_d(p, closed=cl) for p, cl in keep_parts)))
        else:
            out.append(m)
    return C.Frag(out, f.meta)


def separate_gaps(f: C.Frag, sep: float = 3.0):
    """[(point, gap)] where two separate pieces of the stamped foil come
    closer than ``sep`` (the vector rule of build_tuck.foil_gaps)."""
    import shapely
    import shapely.ops
    sh = f.shape()
    geoms = [g for g in getattr(sh, "geoms", [sh]) if g.area > 0.05]
    arr = np.array(geoms, dtype=object)
    tree = shapely.STRtree(arr)
    out = []
    for i, j in zip(*tree.query(arr, predicate="dwithin", distance=sep)):
        if i >= j:
            continue
        d = float(shapely.distance(geoms[i], geoms[j]))
        if 0.08 <= d < sep - 0.08:
            p1, p2 = shapely.ops.nearest_points(geoms[i], geoms[j])
            out.append((np.array([(p1.x + p2.x) / 2, (p1.y + p2.y) / 2]), d))
    return out


def enforce_gaps(f: C.Frag, sep: float = 3.0, passes: int = 4) -> C.Frag:
    """Last resort after :func:`heal`: wherever two separate foil pieces are
    still closer than ``sep``, trim the stroke END nearest the spot back until
    it keeps ``sep`` + 0.2 clear (dots and fills are never moved)."""
    from dataclasses import replace
    for _ in range(passes):
        bad = separate_gaps(f, sep)
        if not bad:
            break
        marks = list(f.marks)
        for pt, d in bad:
            best = None
            for i, m in enumerate(marks):
                if m.kind != "stroke":
                    continue
                for k, (pts, cl) in enumerate(G.flatten(m.d, 0.05)):
                    if cl or len(pts) < 2:
                        continue
                    for end in (0, -1):
                        dist = float(np.hypot(*(pts[end] - pt)))
                        if dist < 5.0 and (best is None or dist < best[0]):
                            best = (dist, i, k, end)
            if best is None:
                continue
            _, i, k, end = best
            m = marks[i]
            subs = G.flatten(m.d, 0.05)
            new = []
            for kk, (pts, cl) in enumerate(subs):
                if kk == k:
                    P = pts if end == -1 else pts[::-1]
                    cv = G.Curve(P)
                    cutlen = sep - d + 0.35
                    if cv.length - cutlen > 1.5:
                        P = cv.sub(0.0, (cv.length - cutlen) / cv.length).pts
                        new.append((P if end == -1 else P[::-1], False))
                else:
                    new.append((pts, cl))
            if new:
                marks[i] = replace(m, d="".join(C.polyline_d(p, closed=cl) for p, cl in new))
            else:
                marks[i] = None
        f = C.Frag([m for m in marks if m is not None], f.meta)
    return f
