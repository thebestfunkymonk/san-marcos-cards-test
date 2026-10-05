"""Machine-checkable parts of the creative brief's §I review checklist.

    .venv/bin/python -m deck.qa                  # all pieces
    .venv/bin/python -m deck.qa KS QS courts     # a subset (IDs, file stems or groups)

Every run first rebuilds the requested pieces (Limestone into cards/, white
into build/white/, ≈ 1 s), so the checks always see the current art modules.
Prints one row per piece and writes ``build/qa/report.json`` (details,
numbers and flagged regions) plus overlays of flagged regions in
``build/qa/flags/<stem>.png`` and ``build/white/contact.png``.

Checks (column: brief item) — ✗ fails, ! warns (look at the flag overlay)
  1   strk   every stroke width in {1.6, 2.1, 3.1, 4.2, 6.25}; transforms (attribute
             or CSS style) are translate / rotate / ±1 mirrors only; no vector-effect
  4   pal    every fill/stroke is a §C token and sits on its own layer; no
             paper-coloured paint outside the paper layer (knockouts are geometric)
  4b  budg   inks used ⊆ the §C budget for the piece (courts with art: all four)
  4c  hide   ! art hidden under a higher plate: a lower layer's marks inside a solid
             area (wider than a CONTOUR line) of a layer that prints above it
  5   gold   courts: gold ≤ 15 % of the art window (the two drawable halves,
             band excluded); colour balance vs §C.2 (report)
  5r  g/r    ! thin gold linework on red (§C.4): gold features ≤ 4 px wide whose
             3 px neighbourhood is ≥ 50 % red
  6   idx    rank / pip / JOKER geometry equals the canonical index (±1 px) and the
             br copy is its exact 180° rotation; deck-wide raster overlay of the index
  8   safe   no ink of any layer outside the 37.5 px safe inset (BACK flood edge ±1 px)
  9   pips   2-10: every §E.2 pip present, exact (shape XOR < 0.5 %), rotated iff
             y > 525, nothing else drawn
  10a c2     courts and BACK: the render equals its 180° rotation — no difference
             cluster ≥ 4 px² after a 1 px AA erosion
  10c clr    courts: art ≥ 12 px from the corner pips (vector, §F.1); jokers: no
             figure at x < 130 above y 310 (and its 180° copy) and ≥ 12 px from the
             JOKER index (§F.4); aces: ! art ≥ 12 px from the index
  11  back   frame D2 (mirror both axes) and emblem C2 (clusters ≥ 4 px² after a
             1 px erosion, at 3x), emblem NOT mirror-symmetric, knockout 18-22 %
  12  gaps   VECTOR (✗): every drawn element is outlined (true caps/joins, clips and
             transforms applied), split into connected pieces, and the paper
             between any two pieces — across all layers — is measured:
               stroke-stroke ≥ 4.2 where they run parallel (≥ 8 px), else ≥ 3.0;
               pieces of different layers ≥ 3.0; same-layer fill pieces ≥ 2.5
               (a knockout line; on the BACK, whose lines are all reversed out
               at §B.2 widths, ≥ 1.6); solid bridges between knockouts in solids
               ≥ 300 px² ≥ 3.0 (and such solids no thinner than 3.0 anywhere
               they are a separate piece); knockout holes at least the knockout-
               line minimum wide; no fill piece thinner than HAIRLINE.  Exempt: frame RULE ↔ gold rule (§F.1 3.85 px,
               RESOLUTIONS["frame_gap"]) and clipped art ↔ frame rules.
             RASTER (!): per layer at 3x, features thinner than 1.5 px (below
             HAIRLINE) and paper gaps narrower than 2.5 px inside one layer.
  17  svg    no <text>, <use>/<symbol>, nested <svg>, <marker>, <switch>, <image>,
             filters, gradients, masks, patterns, <style>, blend modes; layer
             groups paper, jade, red, gold, ink present and in order
  25  rndr   rsvg-convert vs resvg composite diff below threshold
  24  wht    the white-stock build shows no Limestone anywhere (no paper covers)
Deck-wide: the index overlay, and the §E.2 clearances actually built (report).
"""
from __future__ import annotations

import argparse
import io
import json
import math
import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from concurrent.futures import ProcessPoolExecutor

import numpy as np
import shapely
import shapely.ops
from shapely import affinity

from inkkit import geom as G
from deck import tokens as T
from deck import build as B
from deck import cardsvg as C
from deck import frames as F
from deck import index as IX
from deck import layout as LY
from deck import pips as P

ROOT = str(T.ROOT)
QA_DIR = os.path.join(ROOT, "build", "qa")
NS = "{http://www.w3.org/2000/svg}"
SCALE = 3                                  # raster scale for layer masks (px per card px)
EPS = 0.08                                 # vector tolerance (flattening, AA)
GAP_PARALLEL = F.GAP_PARALLEL              # §I.12 parallel strokes: 4.2
GAP_MARK = F.GAP_MARK                      # separate marks / knockout gaps (solid bridges): 3.0
KO_LINE_MIN = 2.5                          # §I.12 knockout (paper) line inside solid shapes
KO_LINE_MIN_BACK = T.HAIRLINE              # BACK: its lines ARE the reversed-out art (§B.2/§H.19 FINE,
                                           # HAIRLINE spandrels), so the §B.2 minimum applies there
PARALLEL_RUN = 12.0                        # a near-contact longer than this counts as parallel
SOLID_MIN_AREA = 300.0                     # "solid shapes" for the knockout-bridge test (px²)
RASTER_LINE_MIN = 1.5                      # raster: features thinner than this (< HAIRLINE 1.6)
RASTER_GAP_MIN = 2.5                       # raster: paper narrower than this inside one layer
LINE_CLUSTER = 3.0                         # min flagged area (card px²) for a thin region
GAP_CLUSTER = 8.0                          # min flagged area (card px²) for a narrow-gap region
                                           # (sharp V crotches of the pips stay below it)
HIDE_OPEN = T.CONTOUR / 2 + 0.3            # upper-layer solids = what survives an opening of this radius
HIDE_CLUSTER = 12.0
HIDE_INSET = 2.0                           # hidden = at least this far inside the upper solid
SYM_CLUSTER = 4.0                          # 10a / 11: asymmetry clusters (card px²)
RENDER_DIFF_MAX = 0.002                    # rsvg vs resvg: max fraction of pixels differing > 40
ACE_INDEX_CLEAR = 12.0

LAYER_COLOR = {"paper": {T.PAPER.lower(), T.WHITE.lower()}, "jade": {T.JADE.lower()},
               "red": {T.RED.lower()}, "gold": {T.FOIL.lower()}, "ink": {T.INK.lower()}}
LEGAL = {c.lower() for c in T.LEGAL_COLORS}
INK_OF = {T.INK.lower(): "ink", T.RED.lower(): "red", T.JADE.lower(): "jade", T.FOIL.lower(): "gold"}
BUDGET = {
    "number_black": {"ink"}, "number_red": {"red"},
    "court": {"ink", "red", "jade", "gold"},
    "AS": {"ink", "gold"}, "AC": {"ink", "gold"}, "AH": {"red", "gold"}, "AD": {"red", "gold"},
    "JOKER_RED": {"red", "gold", "ink"}, "JOKER_BLACK": {"ink", "jade", "gold"},
    "BACK": {"jade"},
}
BALANCE = {"paper": (45, 50), "jade": (15, 20), "red": (12, 16), "gold": (10, 15), "ink": (8, 16)}
NAMED = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "none": "none"}
# The build bakes every path, so nothing needs indirection: <use>/<symbol>
# would hide strokes and transforms from these checks (a nested <svg> can
# scale by its viewBox).
BANNED_TAGS = {"text", "tspan", "textPath", "image", "filter", "linearGradient", "radialGradient",
               "mask", "pattern", "foreignObject", "feBlend", "style", "symbol", "use", "marker",
               "switch", "script", "animate", "animateTransform", "animateMotion", "set", "a"}
SYSTEM_CLASSES = {"frame", "frame-inner", "band-rule", "partition", "medallion", "house-mark",
                  "corner-pip", "index-rank", "index-pip", "index-joker", "pip", "stock"}
FRAME_CLASSES = {"frame", "frame-inner"}
INDEX_CLASSES = {"index-rank", "index-pip", "index-joker"}


# =============================================================================
# helpers
# =============================================================================
def _norm_color(v):
    if v is None:
        return None
    v = v.strip().lower()
    if v in NAMED:
        return NAMED[v]
    if re.fullmatch(r"#[0-9a-f]{3}", v):
        return "#" + "".join(ch * 2 for ch in v[1:])
    return v


def _style(el) -> dict:
    out = {}
    for part in (el.get("style") or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def _attr(el, name):
    st = _style(el)
    return st.get(name, el.get(name))


_TF_RE = re.compile(r"([A-Za-z0-9]+)\s*\(([^)]*)\)")
_UNIT = {"": 1.0, "px": 1.0, "deg": 1.0, "rad": 180 / math.pi, "turn": 360.0, "grad": 0.9}


def _num(tok: str) -> float:
    m = re.fullmatch(r"([-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?)([a-z%]*)", tok.strip())
    if not m or m.group(2) not in _UNIT:
        raise ValueError(tok)
    return float(m.group(1)) * _UNIT[m.group(2)]


def _parse_transform(tf: str):
    """SVG attribute or CSS transform -> (3x3 matrix, [problems]). Legal:
    translate*, rotate, scale / matrix that are rigid motions or ±1 mirrors."""
    M = np.eye(3)
    bad = []
    if not tf or tf.strip() in ("none", ""):
        return M, bad
    rest = _TF_RE.sub("", tf).replace(",", "").strip()
    if rest:
        bad.append(f"unparsed transform {tf[:40]!r}")
    for name, args in _TF_RE.findall(tf):
        try:
            a = [_num(x) for x in re.split(r"[\s,]+", args.strip()) if x]
        except ValueError:
            bad.append(f"{name}({args})")
            continue
        n = name.lower()
        m = np.eye(3)
        if n == "translate":
            m[0, 2], m[1, 2] = a[0], (a[1] if len(a) > 1 else 0.0)
        elif n == "translatex":
            m[0, 2] = a[0]
        elif n == "translatey":
            m[1, 2] = a[0]
        elif n in ("rotate", "rotatez"):
            t = math.radians(a[0])
            cx, cy = (a[1], a[2]) if len(a) >= 3 else (0.0, 0.0)
            r = np.array([[math.cos(t), -math.sin(t), 0], [math.sin(t), math.cos(t), 0], [0, 0, 1]])
            tr = np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]])
            m = tr @ r @ np.linalg.inv(tr)
        elif n in ("scale", "scalex", "scaley"):
            sx = a[0] if n != "scaley" else 1.0
            sy = (a[1] if len(a) > 1 else a[0]) if n == "scale" else (a[0] if n == "scaley" else 1.0)
            m[0, 0], m[1, 1] = sx, sy
            if abs(abs(sx) - 1) > 1e-6 or abs(abs(sy) - 1) > 1e-6:
                bad.append(f"{name}({args})")
        elif n == "matrix" and len(a) == 6:
            m = np.array([[a[0], a[2], a[4]], [a[1], a[3], a[5]], [0, 0, 1]])
            if (abs(a[0] ** 2 + a[1] ** 2 - 1) > 1e-4 or abs(a[2] ** 2 + a[3] ** 2 - 1) > 1e-4
                    or abs(a[0] * a[2] + a[1] * a[3]) > 1e-4):
                bad.append(f"matrix({args})")
        else:                                     # skew*, 3D functions, perspective …
            bad.append(f"{name}({args})")
            continue
        M = M @ m
    return M, bad


def _el_transform(el):
    """(matrix, problems) from the transform attribute and a CSS transform."""
    M, bad = _parse_transform(el.get("transform") or "")
    css = _style(el).get("transform")
    if css:
        M2, bad2 = _parse_transform(css)
        M, bad = M2, bad + bad2                   # CSS wins over the attribute
    return M, bad


def _rsvg(svg_text: str, width: int) -> np.ndarray:
    r = subprocess.run(["rsvg-convert", "-w", str(width)], input=svg_text.encode(), capture_output=True)
    if r.returncode:
        raise RuntimeError(r.stderr.decode()[:300])
    from PIL import Image
    return np.asarray(Image.open(io.BytesIO(r.stdout)).convert("RGBA"))


def _resvg(svg_path: str, width: int) -> np.ndarray:
    from PIL import Image
    out = os.path.join(QA_DIR, "tmp", os.path.basename(svg_path) + f".{os.getpid()}.resvg.png")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    r = subprocess.run(["resvg", "-w", str(width), svg_path, out], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[:300])
    a = np.asarray(Image.open(out).convert("RGBA"))
    os.remove(out)
    return a


def _isolate(svg_text: str, keep: str | None = None) -> str:
    """SVG text with only the layer ``keep`` (others emptied)."""
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    root = ET.fromstring(svg_text)
    for g in list(root):
        if g.tag != NS + "g":
            continue
        if keep is not None and g.get("id") != keep:
            for ch in list(g):
                g.remove(ch)
    return ET.tostring(root, encoding="unicode")


def _poly_mask(d, shape, scale: float) -> np.ndarray:
    """Rasterise a closed path (card coords) or shapely polygon into a mask."""
    from PIL import Image, ImageDraw
    im = Image.new("L", (shape[1], shape[0]), 0)
    dr = ImageDraw.Draw(im)
    if isinstance(d, shapely.Geometry):
        polys = [d] if d.geom_type == "Polygon" else list(getattr(d, "geoms", []))
        for pg in polys:
            dr.polygon([(x * scale, y * scale) for x, y in pg.exterior.coords], fill=255)
            for ring in pg.interiors:
                dr.polygon([(x * scale, y * scale) for x, y in ring.coords], fill=0)
        return np.asarray(im) > 127
    for pts, closed in G.as_polys(d, 0.2):
        if len(pts) >= 3:
            dr.polygon([(float(x) * scale, float(y) * scale) for x, y in pts], fill=255)
    return np.asarray(im) > 127


def _clusters(mask: np.ndarray, min_px: float, scale: float, limit: int = 12):
    from scipy import ndimage as ndi
    lab, n = ndi.label(mask)
    if not n:
        return []
    sizes = ndi.sum(mask, lab, index=np.arange(1, n + 1))
    objs = ndi.find_objects(lab)
    out = []
    for sz, sl in zip(sizes, objs):
        if sz >= min_px:
            y0, y1 = sl[0].start / scale, sl[0].stop / scale
            x0, x1 = sl[1].start / scale, sl[1].stop / scale
            out.append({"bbox": [round(x0, 1), round(y0, 1), round(x1, 1), round(y1, 1)],
                        "area": round(float(sz) / scale / scale, 1)})
    out.sort(key=lambda c: -c["area"])
    return out[:limit]


def _open(mask: np.ndarray, r: float) -> np.ndarray:
    """Morphological opening with a disc of radius r (pixels)."""
    from scipy.ndimage import distance_transform_edt as edt
    if not mask.any():
        return mask
    return edt(~(edt(mask) > r)) <= r


def _crop(mask: np.ndarray, pad: int):
    ys, xs = np.nonzero(mask)
    if not len(ys):
        return None
    return (max(ys.min() - pad, 0), min(ys.max() + pad + 1, mask.shape[0]),
            max(xs.min() - pad, 0), min(xs.max() + pad + 1, mask.shape[1]))


def _morph(mask: np.ndarray, gap_min: float = RASTER_GAP_MIN):
    """(thin-feature pixels, narrow-gap pixels) of a boolean mask at SCALE."""
    from scipy.ndimage import distance_transform_edt as edt
    T_ = np.zeros_like(mask)
    Gp = np.zeros_like(mask)
    box = _crop(mask, int(gap_min * SCALE) + 6)
    if box is None:
        return T_, Gp
    y0, y1, x0, x1 = box
    m = mask[y0:y1, x0:x1]
    rl = RASTER_LINE_MIN * SCALE / 2
    thin = m & ~_open(m, rl)
    rg = gap_min * SCALE / 2
    dil = edt(~m) <= rg
    closed = edt(dil) > rg
    T_[y0:y1, x0:x1] = thin
    Gp[y0:y1, x0:x1] = closed & ~m
    return T_, Gp


def _sym_clusters(a: np.ndarray, b: np.ndarray, region=None, scale: float = 1.0):
    """Clusters (≥ SYM_CLUSTER card px²) of a XOR b after a 1 px erosion."""
    from scipy.ndimage import binary_erosion
    x = a ^ b
    if region is not None:
        x &= region
    it = max(1, int(round(scale)))
    x = binary_erosion(x, iterations=it)
    return _clusters(x, SYM_CLUSTER * scale * scale, scale)


# =============================================================================
# vector geometry of a card (for 12 and 10c)
# =============================================================================
_CAP = {"butt": "flat", "round": "round", "square": "square"}
_JOIN = {"miter": "mitre", "miter-clip": "mitre", "arcs": "mitre", "round": "round", "bevel": "bevel"}


def _shape_el_d(el, tag):
    g = lambda k, dflt=0.0: float(str(el.get(k, dflt)).replace("px", ""))  # noqa: E731
    if tag == "path":
        return el.get("d") or ""
    if tag == "circle":
        return G.circle_d(g("cx"), g("cy"), g("r"))
    if tag == "ellipse":
        return G.ellipse_d(g("cx"), g("cy"), g("rx"), g("ry"))
    if tag == "rect":
        return G.rect_d(g("x"), g("y"), g("width"), g("height"), g("rx", el.get("ry", 0.0)))
    if tag == "line":
        return G.poly_d([(g("x1"), g("y1")), (g("x2"), g("y2"))])
    if tag in ("polyline", "polygon"):
        v = [float(t) for t in re.split(r"[\s,]+", (el.get("points") or "").strip()) if t]
        return G.poly_d(np.array(v).reshape(-1, 2), closed=(tag == "polygon")) if len(v) >= 4 else ""
    return ""


def _stroke_geom(d: str, w: float, cap: str, join: str, ml: float):
    parts = []
    for pts, closed in G.as_polys(d, 0.05):
        if len(pts) < 2:
            continue
        pts = np.asarray(pts, float)
        if closed and len(pts) >= 3:
            ln = shapely.LinearRing(pts)
        else:
            ln = shapely.LineString(pts)
        parts.append(ln)
    if not parts:
        return None
    buf = shapely.buffer(np.array(parts, dtype=object), w / 2, quad_segs=8,
                         cap_style=_CAP.get(cap, "flat"), join_style=_JOIN.get(join, "mitre"),
                         mitre_limit=max(ml, 1.0))
    return shapely.union_all(buf)


def card_geometry(svg_text: str) -> list[dict]:
    """Every drawn element outside the paper layer as card-space shapely
    geometry (fill ∪ stroke outline, transforms and clip-paths applied; the
    card-outline clip is ignored), exploded into connected pieces.
    Each piece: {geom, layer, kind ('stroke'|'fill'), el, cls, art}."""
    root = ET.fromstring(svg_text)
    clips = {}
    for cp in root.iter(NS + "clipPath"):
        ds = [ch.get("d") for ch in cp.iter(NS + "path") if ch.get("d")]
        if cp.get("id") and ds:
            clips[cp.get("id")] = "".join(ds)
    pieces = []
    counter = [0]

    def walk(el, layer, M, clip, inh, cls_stack):
        tag = el.tag.replace(NS, "")
        if tag in ("defs", "clipPath", "title", "desc", "metadata"):
            return
        if (_attr(el, "display") or "") == "none" or (_attr(el, "visibility") or "") == "hidden":
            return
        m, _ = _el_transform(el)
        M = M @ m
        cur = dict(inh)
        for k in ("fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin",
                  "stroke-miterlimit", "fill-rule"):
            v = _attr(el, k)
            if v is not None:
                cur[k] = v
        cls = (el.get("class") or "").split()
        cls_stack = cls_stack + cls
        cp = _attr(el, "clip-path")
        if cp and cp.startswith("url(#"):
            cid = cp[5:-1]
            if cid != "card" and cid in clips:
                cg = G.to_shape(clips[cid])
                cg = affinity.affine_transform(cg, [M[0, 0], M[0, 1], M[1, 0], M[1, 1], M[0, 2], M[1, 2]])
                clip = cg if clip is None else clip.intersection(cg)
        if tag in ("path", "circle", "ellipse", "rect", "line", "polyline", "polygon"):
            d = _shape_el_d(el, tag)
            if d:
                fill = _norm_color(cur.get("fill", "#000000"))
                stroke = _norm_color(cur.get("stroke", "none"))
                if tag in ("line", "polyline"):
                    fill = "none" if tag == "line" else fill
                geoms, kinds = [], []
                if fill not in (None, "none"):
                    fg = G.to_shape(d, cur.get("fill-rule", "nonzero"))
                    if not fg.is_empty:
                        geoms.append(fg)
                        kinds.append("fill")
                if stroke not in (None, "none"):
                    try:
                        w = float(str(cur.get("stroke-width", "1")).replace("px", ""))
                    except ValueError:
                        w = 1.0
                    sg = _stroke_geom(d, w, cur.get("stroke-linecap", "butt"),
                                      cur.get("stroke-linejoin", "miter"),
                                      float(cur.get("stroke-miterlimit", 4)))
                    if sg is not None and not sg.is_empty:
                        geoms.append(sg)
                        kinds.append("stroke")
                if geoms:
                    gm = shapely.union_all(geoms) if len(geoms) > 1 else geoms[0]
                    gm = affinity.affine_transform(gm, [M[0, 0], M[0, 1], M[1, 0], M[1, 1], M[0, 2], M[1, 2]])
                    if clip is not None:
                        gm = gm.intersection(clip)
                    kind = "fill" if kinds == ["fill"] else "stroke" if kinds == ["stroke"] else "mixed"
                    art = not (set(cls_stack) & SYSTEM_CLASSES) or bool({"court-top", "court-rot"} &
                                                                         set(cls_stack))
                    idx = counter[0]
                    counter[0] += 1
                    for pg in getattr(gm, "geoms", [gm]):
                        if pg.geom_type == "Polygon" and pg.area > 0.05:
                            pieces.append({"geom": pg, "layer": layer, "kind": kind, "el": idx,
                                           "cls": set(cls_stack), "art": art})
        for ch in el:
            walk(ch, layer, M, clip, cur, cls_stack)

    for g in root:
        if g.tag == NS + "g" and g.get("id") != "paper":
            walk(g, g.get("id"), np.eye(3), None, {}, [])
    return pieces


def _exempt(a: dict, b: dict) -> bool:
    fa, fb = bool(a["cls"] & FRAME_CLASSES), bool(b["cls"] & FRAME_CLASSES)
    if fa and fb and a["el"] != b["el"]:
        return True                                   # §F.1 RULE <-> gold rule (RESOLUTIONS["frame_gap"])
    if (fa and b["art"]) or (fb and a["art"]):
        return True                                   # art clipped to the window beside the frame
    return False


def vector_gaps(pieces: list[dict], ko_min: float = KO_LINE_MIN) -> list[dict]:
    """12 (vector): paper between distinct pieces, and knockout bridges."""
    out = []
    if not pieces:
        return out
    geoms = np.array([p["geom"] for p in pieces], dtype=object)
    tree = shapely.STRtree(geoms)
    pairs = tree.query(geoms, predicate="dwithin", distance=GAP_PARALLEL)
    seen = set()
    for i, j in zip(*pairs):
        if i >= j or (i, j) in seen:
            continue
        seen.add((i, j))
        a, b = pieces[i], pieces[j]
        if _exempt(a, b):
            continue
        d = float(shapely.distance(a["geom"], b["geom"]))
        if d < EPS:
            continue                                   # touching / overlapping: joined on purpose
        same = a["layer"] == b["layer"]
        rule, need = None, None
        if a["kind"] == "stroke" and b["kind"] == "stroke":
            if d < GAP_MARK - EPS:
                rule, need = "strokes", GAP_MARK
            elif d < GAP_PARALLEL - EPS:
                near = a["geom"].intersection(b["geom"].buffer(GAP_PARALLEL + 0.1, quad_segs=4))
                run = 0.0
                if not near.is_empty:
                    rr = near.minimum_rotated_rectangle
                    xy = np.asarray(rr.exterior.coords) if rr.geom_type == "Polygon" else None
                    if xy is not None and len(xy) >= 4:
                        run = max(np.linalg.norm(xy[1] - xy[0]), np.linalg.norm(xy[2] - xy[1]))
                if run >= PARALLEL_RUN:
                    rule, need = f"parallel strokes (run {run:.0f} px)", GAP_PARALLEL
        elif same and a["kind"] != "stroke" and b["kind"] != "stroke":
            if d < ko_min - EPS:
                rule, need = "knockout line / gap in a solid", ko_min
        elif d < GAP_MARK - EPS:
            rule, need = "separate marks" if not same else "fill beside a line", GAP_MARK
        if rule:
            p1, p2 = shapely.ops.nearest_points(a["geom"], b["geom"])
            out.append({"at": [round((p1.x + p2.x) / 2, 1), round((p1.y + p2.y) / 2, 1)],
                        "gap": round(d, 2), "need": need, "rule": rule,
                        "layers": [a["layer"], b["layer"]],
                        "what": [" ".join(sorted(a["cls"] - {"court-top", "court-rot"})) or "art",
                                 " ".join(sorted(b["cls"] - {"court-top", "court-rot"})) or "art"]})
    # widths: fill pieces thinner than HAIRLINE, slivers of large solids, knockout holes
    for p in pieces:
        pg = p["geom"]
        if p["kind"] == "stroke":
            continue
        what = [" ".join(sorted(p["cls"] - {"court-top", "court-rot"})) or "art"]
        mic = shapely.maximum_inscribed_circle(pg, 0.02)
        wmax = 2 * mic.length
        c = mic.coords[0]
        if wmax < T.HAIRLINE - EPS:
            out.append({"at": [round(c[0], 1), round(c[1], 1)], "gap": round(wmax, 2), "need": T.HAIRLINE,
                        "rule": "fill thinner than HAIRLINE", "layers": [p["layer"]], "what": what})
        elif pg.area >= SOLID_MIN_AREA and wmax < GAP_MARK - EPS:
            out.append({"at": [round(c[0], 1), round(c[1], 1)], "gap": round(wmax, 2), "need": GAP_MARK,
                        "rule": "solid sliver between knockouts", "layers": [p["layer"]], "what": what})
        for ring in pg.interiors:
            hole = shapely.Polygon(ring)
            if hole.area < 0.5:
                continue
            hm = shapely.maximum_inscribed_circle(hole, 0.02)
            hw = 2 * hm.length
            if hw < ko_min - EPS:
                c = hm.coords[0]
                out.append({"at": [round(c[0], 1), round(c[1], 1)], "gap": round(hw, 2), "need": ko_min,
                            "rule": "knockout line (hole) too thin", "layers": [p["layer"]], "what": what})
    # knockout bridges inside large solids (hole <-> hole, hole <-> edge)
    for p in pieces:
        pg = p["geom"]
        if p["kind"] == "stroke" or not len(pg.interiors) or pg.area < SOLID_MIN_AREA:
            continue
        rings = [shapely.LinearRing(pg.exterior.coords)] + [shapely.LinearRing(r.coords) for r in pg.interiors]
        rt = shapely.STRtree(rings)
        rp = rt.query(np.array(rings, dtype=object), predicate="dwithin", distance=GAP_MARK)
        for i, j in zip(*rp):
            if i >= j:
                continue
            d = float(shapely.distance(rings[i], rings[j]))
            if EPS < d < GAP_MARK - EPS:
                p1, p2 = shapely.ops.nearest_points(rings[i], rings[j])
                mid = shapely.Point((p1.x + p2.x) / 2, (p1.y + p2.y) / 2)
                if pg.contains(mid):
                    out.append({"at": [round(mid.x, 1), round(mid.y, 1)], "gap": round(d, 2),
                                "need": GAP_MARK, "rule": "solid bridge between knockouts",
                                "layers": [p["layer"]], "what": [" ".join(sorted(p["cls"])) or "art"]})
    out.sort(key=lambda r: r["gap"])
    return out


def _min_dist(a_pieces, b_pieces):
    if not a_pieces or not b_pieces:
        return None
    ua = shapely.union_all([p["geom"] for p in a_pieces])
    ub = shapely.union_all([p["geom"] for p in b_pieces])
    return float(shapely.distance(ua, ub))


def clearance_check(pieces: list[dict], info: dict) -> dict:
    """10c: art clear of the corner pips (courts), the joker index zone
    (jokers) or the index (aces)."""
    kind = info["kind"]
    art = [p for p in pieces if p["art"]]
    if kind == "court":
        if info.get("status") != "art":
            return {"ok": None, "detail": ["n/a (placeholder)"]}
        pip = [p for p in pieces if "corner-pip" in p["cls"]]
        d = _min_dist(art, pip)
        ok = d is None or d >= F.CORNER_PIP_CLEAR - 0.02
        return {"ok": ok, "min_clear": None if d is None else round(d, 2),
                "detail": [] if ok else [f"art {d:.2f} px from the corner pip (need {F.CORNER_PIP_CLEAR})"]}
    if kind == "joker":
        if info.get("status") != "art":
            return {"ok": None, "detail": ["n/a (placeholder)"]}
        idx = [p for p in pieces if p["cls"] & INDEX_CLASSES]
        det = []
        zone = shapely.box(0, 0, F.JOKER_INDEX_CLEAR_X, F.JOKER_INDEX_CLEAR_Y)
        zone = zone.union(shapely.box(T.W - F.JOKER_INDEX_CLEAR_X, T.H - F.JOKER_INDEX_CLEAR_Y, T.W, T.H))
        hit = [p for p in art if p["geom"].intersects(zone) and p["geom"].intersection(zone).area > 0.5]
        if hit:
            bb = shapely.union_all([p["geom"].intersection(zone) for p in hit]).bounds
            det.append(f"figure inside the index zone x < {F.JOKER_INDEX_CLEAR_X}, y < "
                       f"{F.JOKER_INDEX_CLEAR_Y} (or its 180° copy) at {[round(v) for v in bb]}")
        d = _min_dist(art, idx)
        if d is not None and d < F.CORNER_PIP_CLEAR - 0.02:
            det.append(f"art {d:.2f} px from the JOKER index (need 12)")
        return {"ok": not det, "min_clear": None if d is None else round(d, 2), "detail": det}
    if kind == "ace":
        if info.get("status") != "art":
            return {"ok": None, "detail": ["n/a (placeholder)"]}
        idx = [p for p in pieces if p["cls"] & INDEX_CLASSES]
        d = _min_dist(art, idx)
        ok = d is None or d >= ACE_INDEX_CLEAR - 0.02
        return {"ok": True if ok else "warn", "min_clear": None if d is None else round(d, 2),
                "detail": [] if ok else [f"art {d:.2f} px from the index (keep ≥ {ACE_INDEX_CLEAR:g})"]}
    return {"ok": None, "detail": ["n/a"]}


# =============================================================================
# per-piece checks
# =============================================================================
def xml_checks(svg_text: str, info: dict) -> dict:
    res = {}
    root = ET.fromstring(svg_text)
    # ---- 17 structure --------------------------------------------------------
    problems = []
    tags = {el.tag.replace(NS, "") for el in root.iter()}
    bad = sorted(tags & BANNED_TAGS)
    if bad:
        problems.append("banned elements: " + ", ".join(bad))
    if sum(1 for el in root.iter(NS + "svg")) > 1:
        problems.append("nested <svg>")
    for el in root.iter():
        for k in ("mix-blend-mode", "filter", "mask", "vector-effect", "isolation"):
            v = _attr(el, k)
            if v and v not in ("none", "auto"):
                problems.append(f"{k} on <{el.tag.replace(NS, '')}>")
                break
        href = el.get("href") or el.get("{http://www.w3.org/1999/xlink}href")
        if href:
            problems.append(f"reference href={href[:40]}")
    groups = [g.get("id") for g in root if g.tag == NS + "g"]
    allowed = [list(T.LAYERS)] + ([list(C.ACE_ORDER)] if info["kind"] == "ace" else [])
    if groups not in allowed:
        problems.append(f"layer groups {groups} (expected {allowed[0]})")
    res["17"] = {"ok": not problems, "detail": sorted(set(problems))[:8]}

    # ---- 1 strokes / transforms, 4 palette / layers ---------------------------
    stroke_bad, tf_bad, color_bad, layer_bad, paper_cover = [], [], [], [], []
    used = set()

    def walk(el, layer, inh):
        tag = el.tag.replace(NS, "")
        if tag in ("title", "desc", "metadata"):
            return
        _, why = _el_transform(el)
        tf_bad.extend(why)
        if tag in ("defs", "clipPath"):
            for ch in el.iter():                 # clip geometry: transforms only (no paint)
                if ch is not el:
                    tf_bad.extend(_el_transform(ch)[1])
            return
        cur = dict(inh)
        for k in ("fill", "stroke", "stroke-width", "opacity", "fill-opacity", "stroke-opacity"):
            v = _attr(el, k)
            if v is not None:
                cur[k] = v
        if tag in ("path", "circle", "ellipse", "rect", "line", "polyline", "polygon"):
            fill = _norm_color(cur.get("fill", "#000000"))
            stroke = _norm_color(cur.get("stroke", "none"))
            if tag == "line":
                fill = "none"
            for role, c in (("fill", fill), ("stroke", stroke)):
                if c in (None, "none"):
                    continue
                if c.startswith("url(") or c not in LEGAL:
                    color_bad.append(f"{role} {c}")
                    continue
                if layer not in LAYER_COLOR or c not in LAYER_COLOR[layer]:
                    if c in LAYER_COLOR["paper"] and layer != "paper":
                        paper_cover.append(f"{role} {c} on layer {layer}")
                    else:
                        layer_bad.append(f"{role} {c} on layer {layer}")
                if c in INK_OF:
                    used.add(INK_OF[c])
            if stroke not in (None, "none"):
                w = cur.get("stroke-width")
                try:
                    wv = float(str(w).replace("px", "")) if w is not None else 1.0
                except ValueError:
                    wv = -1
                if not any(abs(wv - L) < 1e-6 for L in T.LEGAL_STROKES):
                    stroke_bad.append(f"stroke-width {w}")
            for k in ("opacity", "fill-opacity", "stroke-opacity"):
                if k in cur and float(cur[k]) < 1:
                    color_bad.append(f"{k}={cur[k]}")
        for ch in el:
            walk(ch, layer, cur)

    for g in root:
        if g.tag == NS + "g":
            walk(g, g.get("id"), {})
    res["1"] = {"ok": not stroke_bad and not tf_bad,
                "detail": sorted(set(stroke_bad))[:8] + sorted(set(tf_bad))[:8]}
    res["4"] = {"ok": not color_bad and not layer_bad and not paper_cover,
                "detail": sorted(set(color_bad))[:6] + sorted(set(layer_bad))[:6] +
                          sorted(set(paper_cover))[:6]}
    # ---- 4b budget ------------------------------------------------------------
    pid, kind = info["id"], info["kind"]
    if kind == "number":
        key = "number_black" if info["suit"] in "SC" else "number_red"
    elif kind == "court":
        key = "court"
    else:
        key = pid
    budget = BUDGET[key]
    extra = used - budget
    missing = (budget - used) if (kind == "court" and info.get("status") == "art") else set()
    res["4b"] = {"ok": not extra and not missing, "used": sorted(used), "budget": sorted(budget),
                 "detail": ([f"outside budget: {sorted(extra)}"] if extra else []) +
                           ([f"court must use all four inks; missing {sorted(missing)}"] if missing else [])}
    return res


def _paths(root, cls: str, corner: str | None = None):
    out = []
    for el in root.iter(NS + "path"):
        c = (el.get("class") or "").split()
        if cls in c and (corner is None or el.get("data-corner") == corner):
            out.append(el)
    return out


def _bb_close(a, b, tol=1.0):
    return all(abs(x - y) <= tol for x, y in zip(a, b))


def index_check(svg_text: str, info: dict) -> dict:
    """6: rank/pip/JOKER geometry equals the canonical index; br = rot180(tl)."""
    root = ET.fromstring(svg_text)
    kind, rank, suit = info["kind"], info["rank"], info["suit"]
    if kind == "back":
        return {"ok": None, "detail": ["n/a"]}
    detail, meas = [], {}
    if kind == "joker":
        want = {"index-joker": IX._joker_letters_d()}
    else:
        want = {"index-rank": IX.rank_d(rank), "index-pip": IX.index_pip_d(suit)}
    for cls, d_ref in want.items():
        for corner in ("tl", "br"):
            els = _paths(root, cls, corner)
            if len(els) != 1:
                detail.append(f"{cls}/{corner}: found {len(els)}")
                continue
            ref = d_ref if corner == "tl" else G.rotate180(d_ref, T.CX, T.CY)
            bb, rb = G.bbox(els[0].get("d")), G.bbox(ref)
            meas[f"{cls}/{corner}"] = [round(v, 2) for v in bb]
            if not _bb_close(bb, rb, 1.0):
                detail.append(f"{cls}/{corner} bbox {[round(v, 1) for v in bb]} != {[round(v, 1) for v in rb]}")
    return {"ok": not detail, "detail": detail, "bbox": meas}


def pips_check(svg_text: str, info: dict) -> dict:
    """9: exact §E.2 layout for 2-10, nothing else drawn."""
    if info["kind"] != "number":
        return {"ok": None, "detail": ["n/a"]}
    root = ET.fromstring(svg_text)
    rank, suit = int(info["rank"]), info["suit"]
    found = _paths(root, "pip")
    exp = LY.positions(rank)
    detail = []
    if len(found) != len(exp):
        detail.append(f"{len(found)} pips drawn, {len(exp)} expected")
    shapes = [(G.to_shape(el.get("d")), el) for el in found]
    used = set()
    for x, y, rot in exp:
        ref = G.to_shape(P.pip_d(suit, T.PIP_U_FIELD, x, y, rotate=rot))
        hit = None
        for k, (s, el) in enumerate(shapes):
            if k in used:
                continue
            if abs(s.centroid.x - ref.centroid.x) < 3 and abs(s.centroid.y - ref.centroid.y) < 3:
                if s.symmetric_difference(ref).area / ref.area < 0.005:
                    hit = k
                    break
        if hit is None:
            detail.append(f"missing/mismatched pip at ({x:g},{y:g}) rot={rot}")
        else:
            used.add(hit)
    other = []
    for g in root:
        if g.tag != NS + "g" or g.get("id") == "paper":
            continue
        for el in g:
            cls = (el.get("class") or "").split()
            if not ({"pip", "index-rank", "index-pip"} & set(cls)):
                other.append(el.tag.replace(NS, ""))
    if other:
        detail.append(f"extra elements on a pip card: {other[:5]}")
    return {"ok": not detail, "detail": detail}


def raster_checks(info: dict, svg_text: str) -> dict:
    from scipy.ndimage import binary_erosion, uniform_filter
    res = {}
    kind = info["kind"]
    comp = _rsvg(svg_text, T.W)                         # 750 x 1050 composite
    # ---- 25 renderer agreement --------------------------------------------------
    try:
        rv = _resvg(info["svg"], T.W)
        dd = (np.abs(comp[..., :3].astype(np.int16) - rv[..., :3].astype(np.int16)).max(-1) > 40
              if rv.shape == comp.shape else np.ones(comp.shape[:2], bool))
        frac = float(dd.mean())
        res["25"] = {"ok": frac <= RENDER_DIFF_MAX, "diff": round(frac, 5),
                     "detail": [] if frac <= RENDER_DIFF_MAX else [f"rsvg vs resvg differ on {frac:.3%}"]}
    except Exception as e:  # pragma: no cover
        res["25"] = {"ok": False, "detail": [f"resvg failed: {e}"]}
    # ---- 10a C2 -----------------------------------------------------------------
    if kind in ("court", "back"):
        diff = np.abs(comp[..., :3].astype(np.int16) - comp[::-1, ::-1, :3].astype(np.int16)).max(-1) > 40
        cl = _sym_clusters(diff, np.zeros_like(diff), None, 1.0)
        res["10a"] = {"ok": not cl, "diff": round(float(diff.mean()), 5), "clusters": cl[:6],
                      "detail": [f"differs from its 180° rotation at {c['bbox']} ({c['area']} px²)"
                                 for c in cl[:4]]}
    else:
        res["10a"] = {"ok": None, "detail": ["n/a"]}

    # ---- per-layer masks at SCALE ------------------------------------------------
    W3, H3 = T.W * SCALE, T.H * SCALE
    alpha = {}
    for L in T.LAYERS:
        if f'<g id="{L}" clip-path="url(#card)"></g>' in svg_text:
            alpha[L] = np.zeros((H3, W3), np.uint8)
            continue
        alpha[L] = _rsvg(_isolate(svg_text, L), W3)[..., 3]
    order = info.get("order") or list(T.LAYERS)
    vis = {}
    cover = np.zeros((H3, W3), np.float32)
    for L in reversed(order):
        if L == "paper":
            continue
        a = alpha[L].astype(np.float32) / 255.0
        vis[L] = a * (1.0 - cover)
        cover = cover + vis[L]

    # ---- 8 safe zone ------------------------------------------------------------------
    tol = 1.0 if kind == "back" else 0.0
    s0 = int(math.floor((T.SAFE - tol) * SCALE))
    s1x, s1y = int(math.ceil((T.W - T.SAFE + tol) * SCALE)), int(math.ceil((T.H - T.SAFE + tol) * SCALE))
    ink_any = np.zeros((H3, W3), bool)
    for L in T.LAYERS:
        if L != "paper":
            ink_any |= alpha[L] > 64
    outside = ink_any.copy()
    outside[s0:s1y, s0:s1x] = False
    cl = _clusters(outside, 1, SCALE)
    res["8"] = {"ok": not cl, "detail": [f"ink outside safe zone at {c['bbox']}" for c in cl[:4]]}

    # ---- 5 gold / balance (courts): over the two drawable halves, band excluded ----------
    if kind == "court":
        halves = G.difference(F.art_window_d(), G.rect_d(0, F.BAND_Y0, T.W, F.BAND_Y1 - F.BAND_Y0))
        win = _poly_mask(halves, (H3, W3), SCALE)
        n = win.sum()
        bal = {L: round(float(vis[L][win].sum() / n * 100), 1) for L in vis}
        bal["paper"] = round(100 - sum(bal.values()), 1)
        gold = bal.get("gold", 0.0)
        off = [f"{k} {bal[k]}% (target {lo}-{hi})" for k, (lo, hi) in BALANCE.items()
               if not (lo <= bal.get(k, 0) <= hi)]
        res["5"] = {"ok": gold <= 15.0, "gold_pct": gold, "balance": bal,
                    "window_px2": round(float(n) / SCALE / SCALE),
                    "detail": ([f"gold {gold}% > 15%"] if gold > 15 else []) +
                              (["balance: " + "; ".join(off)] if info.get("status") == "art" and off else [])}
    else:
        res["5"] = {"ok": None, "detail": ["n/a"]}

    # ---- 5r thin gold linework on red (§C.4) ----------------------------------------------
    goldm, redm = alpha["gold"] > 127, alpha["red"] > 127
    if goldm.any() and redm.any():
        thin_gold = goldm & ~_open(goldm, 4.0 * SCALE / 2)
        k = 2 * 3 * SCALE + 1
        red_near = uniform_filter(redm.astype(np.float32), size=k) >= 0.5
        cl = _clusters(thin_gold & red_near, 6 * SCALE * SCALE, SCALE)
        res["5r"] = {"ok": "warn" if cl else True, "regions": cl,
                     "detail": [f"thin gold on red at {c['bbox']}" for c in cl[:3]]}
    else:
        res["5r"] = {"ok": True if goldm.any() else None, "detail": []}

    # ---- 4c art hidden under a higher plate ------------------------------------------------
    hidden_flags = []
    solids = {}
    for A in order:
        m = alpha[A] > 250 if A != "paper" else None
        if m is not None and m.any():
            sm = _open(m, HIDE_OPEN * SCALE)
            if sm.any():                              # ≥ 2 px inside: ignore fills tucked under edges
                sm = binary_erosion(sm, iterations=int(HIDE_INSET * SCALE))
            solids[A] = sm
    for i, L in enumerate(order):
        if L == "paper" or not (alpha[L] > 127).any():
            continue
        for A in order[i + 1:]:
            if A not in solids or not solids[A].any():
                continue
            hid = (alpha[L] > 127) & solids[A]
            if hid.any():
                for c in _clusters(hid, HIDE_CLUSTER * SCALE * SCALE, SCALE):
                    c["layer"], c["under"] = L, A
                    hidden_flags.append(c)
    res["4c"] = {"ok": "warn" if hidden_flags else True, "regions": hidden_flags[:10],
                 "detail": [f"{c['layer']} hidden under the {c['under']} solid at {c['bbox']}"
                            for c in hidden_flags[:3]]}

    # ---- 11 back -------------------------------------------------------------------------
    if kind == "back":
        flood_d = G.rect_d(T.SAFE, T.SAFE, T.W - 2 * T.SAFE, T.H - 2 * T.SAFE, 18)
        flood = _poly_mask(flood_d, (H3, W3), SCALE)
        jade = alpha["jade"].astype(np.float32) / 255.0
        ko = float(1.0 - jade[flood].mean())
        R = 463.2
        lens_d = G.intersection(G.circle_d(181.8, 525, R), G.circle_d(568.2, 525, R))
        emb = _poly_mask(G.offset(lens_d, -12), (H3, W3), SCALE)
        frame = flood & ~_poly_mask(G.offset(lens_d, -3), (H3, W3), SCALE)
        J = alpha["jade"] > 127
        det = []
        fr_lr = _sym_clusters(J, J[:, ::-1], frame, SCALE)
        fr_ud = _sym_clusters(J, J[::-1, :], frame, SCALE)
        if fr_lr or fr_ud:
            det.append(f"frame not D2 at {[c['bbox'] for c in (fr_lr + fr_ud)[:3]]}")
        emb_res = {}
        e_ink = (~J) & emb
        placeholder = info.get("status") != "art"
        if e_ink.sum() > 50 * SCALE * SCALE:
            rot = _sym_clusters(J, J[::-1, ::-1], emb, SCALE)
            mir_lr = float((J != J[:, ::-1])[emb].mean())
            mir_ud = float((J != J[::-1, :])[emb].mean())
            emb_res = {"rot180_clusters": rot[:6], "mirror_lr": round(mir_lr, 5), "mirror_ud": round(mir_ud, 5)}
            if rot:
                det.append(f"emblem not C2 at {[c['bbox'] for c in rot[:3]]}")
            if min(mir_lr, mir_ud) < 0.01:
                det.append("emblem is mirror-symmetric (must be C2 only)")
        elif not placeholder:
            det.append("no emblem")
        if not (0.18 <= ko <= 0.22) and not placeholder:
            det.append(f"knockout coverage {ko:.1%} (target 18-22 %)")
        res["11"] = {"ok": not det, "knockout": round(ko, 4), "emblem": emb_res,
                     "frame_mirror_clusters": (fr_lr + fr_ud)[:6],
                     "detail": det + ([f"placeholder: coverage {ko:.1%}, no emblem (not judged)"]
                                      if placeholder else [])}
    else:
        res["11"] = {"ok": None, "detail": ["n/a"]}

    # ---- 12 raster part: thin features / narrow paper inside one layer --------------------------
    flags = {}
    for L in T.LAYERS:
        if L == "paper":
            continue
        M = alpha[L] > 127
        if kind == "back" and L == "jade":
            inner = _poly_mask(G.rect_d(T.SAFE + 2, T.SAFE + 2, T.W - 2 * T.SAFE - 4, T.H - 2 * T.SAFE - 4, 16),
                               (H3, W3), SCALE)
            thin, gaps = _morph(M, KO_LINE_MIN_BACK)     # reversed-out lines may be FINE / HAIRLINE
            inv_thin, _ = _morph(~M & inner)             # reversed-out lines: paper features of the flood
            thin = thin | inv_thin
        else:
            thin, gaps = _morph(M)
        t = _clusters(thin, LINE_CLUSTER * SCALE * SCALE, SCALE)
        g = _clusters(gaps, GAP_CLUSTER * SCALE * SCALE, SCALE)
        if t or g:
            flags[L] = {"thin": t, "gaps": g}
    res["_raster12"] = flags

    # composite at 750 for the deck-wide index overlay (top-left region)
    if kind != "back":
        col = T.SUIT_COLOR.get(info.get("suit") or "", T.RED if info.get("color") == "red" else T.INK)
        pg, cg = int(T.PAPER[3:5], 16), int(col[3:5], 16)
        cov = (pg - comp[:240, :124, 1].astype(np.float32)) / float(pg - cg)
        res["_index_region"] = cov > 0.5
    else:
        res["_index_region"] = None
    res["_comp"] = comp
    return res


def _flag_overlay(comp, r: dict, info):
    from PIL import Image, ImageDraw
    im = Image.fromarray(comp).convert("RGB")
    dr = ImageDraw.Draw(im)
    boxes = []
    for L, v in (r.get("12", {}).get("raster") or {}).items():
        boxes += [(c["bbox"], (255, 0, 170)) for c in v["thin"]] + [(c["bbox"], (0, 170, 255)) for c in v["gaps"]]
    for v in r.get("12", {}).get("vector") or []:
        x, y = v["at"]
        boxes.append(([x - 4, y - 4, x + 4, y + 4], (230, 30, 30)))
    for k, colr in (("4c", (255, 140, 0)), ("5r", (160, 0, 255))):
        for c in r.get(k, {}).get("regions") or []:
            boxes.append((c["bbox"], colr))
    for c in r.get("10a", {}).get("clusters") or []:
        boxes.append((c["bbox"], (0, 200, 0)))
    p = os.path.join(QA_DIR, "flags", f"{info['stem']}.png")
    if not boxes:
        if os.path.isfile(p):
            os.remove(p)                                  # stale overlay from an earlier run
        return None
    for (x0, y0, x1, y1), colr in boxes:
        dr.rectangle([x0 - 3, y0 - 3, x1 + 3, y1 + 3], outline=colr, width=2)
    os.makedirs(os.path.join(QA_DIR, "flags"), exist_ok=True)
    im.save(p)
    return p


WHITE_BLOB_MIN = 12   # px at 750 w: a real paper cover is a solid patch, not an AA edge


def white_check(info_white: dict | None) -> dict:
    """24: the white-stock variant contains no Limestone paint.

    Authoritative test is vector: no element outside the stock path is painted
    Limestone. The raster test only flags solid Limestone patches of at least
    WHITE_BLOB_MIN px; isolated anti-aliased pixels on gold edges over white
    (which can land within a few levels of Limestone) are ignored."""
    if not info_white or not os.path.isfile(info_white.get("svg", "")):
        return {"ok": False, "detail": ["white-stock build missing"]}
    svg_text = open(info_white["svg"]).read()
    detail = []
    root = ET.fromstring(svg_text)
    paper = T.PAPER.lower()
    painted = 0
    for el in root.iter():
        if el.get("class") == "stock":
            continue
        st = _style(el)
        for attr in ("fill", "stroke"):
            if _norm_color(el.get(attr) or st.get(attr)) == paper:
                painted += 1
    if painted:
        detail.append(f"{painted} element(s) painted Limestone on white stock (paper cover — use a geometric knockout)")
    a = _rsvg(svg_text, T.W)
    ref = np.array([int(T.PAPER[i:i + 2], 16) for i in (1, 3, 5)])
    lime = (np.abs(a[..., :3].astype(np.int16) - ref).max(-1) <= 3) & (a[..., 3] > 250)
    from scipy import ndimage
    lime = ndimage.binary_opening(lime, structure=np.ones((3, 3), bool))  # drop 1-2 px AA edge runs
    lab, n = ndimage.label(lime)
    sizes = np.bincount(lab.ravel())[1:] if n else np.array([], dtype=int)
    blobs = int((sizes >= WHITE_BLOB_MIN).sum())
    if blobs:
        detail.append(f"{blobs} solid Limestone patch(es) ≥ {WHITE_BLOB_MIN} px on white stock")
    return {"ok": not detail, "limestone_px": int(lime.sum()), "limestone_blobs": blobs, "detail": detail}


def check_piece(args) -> dict:
    info, info_white = args
    t0 = time.time()
    out = {"id": info["id"], "stem": info["stem"], "kind": info["kind"], "status": info.get("status")}
    try:
        svg_text = open(info["svg"]).read()
        out.update(xml_checks(svg_text, info))
        out["6"] = index_check(svg_text, info)
        out["9"] = pips_check(svg_text, info)
        pieces = card_geometry(svg_text)
        vec = vector_gaps(pieces, KO_LINE_MIN_BACK if info["kind"] == "back" else KO_LINE_MIN)
        out["10c"] = clearance_check(pieces, info)
        r = raster_checks(info, svg_text)
        idx = r.pop("_index_region")
        comp = r.pop("_comp")
        raster12 = r.pop("_raster12")
        out.update(r)
        det = [f"{v['gap']:.2f} px < {v['need']:g} ({v['rule']}; {v['what'][0]} / {v['what'][-1]}) at {v['at']}"
               for v in vec[:6]]
        det += [f"{L}: {len(v['thin'])} thin, {len(v['gaps'])} narrow-gap region(s) (raster)"
                for L, v in raster12.items()]
        out["12"] = {"ok": False if vec else ("warn" if raster12 else True),
                     "vector": vec[:40], "raster": raster12, "pieces": len(pieces), "detail": det}
        out["24"] = white_check(info_white)
        out["flags_png"] = _flag_overlay(comp, out, info)
        out["_index_region"] = idx
    except Exception:
        import traceback
        out["error"] = traceback.format_exc(limit=6)
    out["seconds"] = round(time.time() - t0, 2)
    return out


# =============================================================================
# deck-wide
# =============================================================================
def deck_index_overlay(results: list[dict]) -> dict:
    """6 (raster): the index region (x < 124, y < 240) of every face overlays:
    the rank area (y < 160) is identical across cards of a rank, the pip area
    across cards of a suit (at most a few AA pixels)."""
    by_rank, by_suit, bad = {}, {}, []
    for r in results:
        m = r.get("_index_region")
        if m is None or r["kind"] in ("back", "joker"):
            continue
        rank, suit = r["id"][:-1], r["id"][-1]
        by_rank.setdefault(rank, []).append((r["id"], m[:160]))
        by_suit.setdefault(suit, []).append((r["id"], m[160:]))
    worst = 0
    for groups in (by_rank, by_suit):
        for key, lst in groups.items():
            ref_id, ref = lst[0]
            for pid, m in lst[1:]:
                n = int((m ^ ref).sum())
                worst = max(worst, n)
                if n > 12:
                    bad.append(f"{pid} vs {ref_id}: {n} px differ")
    return {"ok": not bad, "worst_px": worst, "detail": bad[:10]}


def e2_clearances() -> dict:
    """§E.2 'verified clearances' as actually built, per suit (report only):
    L-column field pips vs the '10' index's right edge (brief: ≥ 35), and the
    10's centre pips vs the side columns (brief: ≥ 37)."""
    ten_right = IX.rank_bbox("10")[2]
    out = {}
    for s in T.SUITS:
        w, h = P.pip_size(s, T.PIP_U_FIELD)
        left = T.COL_L - w / 2
        centre_gap = (T.COL_C - w / 2) - (T.COL_L + w / 2)
        out[s] = {"field_pip_vs_10_index": round(left - ten_right, 2), "centre_vs_side": round(centre_gap, 2)}
    return out


COLS = [("1", "strk"), ("4", "pal"), ("4b", "budg"), ("4c", "hide"), ("5", "gold"), ("5r", "g/r"),
        ("6", "idx"), ("8", "safe"), ("9", "pips"), ("10a", "c2"), ("10c", "clr"), ("11", "back"),
        ("12", "gaps"), ("17", "svg"), ("25", "rndr"), ("24", "wht")]


def _sym(v):
    if v is None:
        return "·"
    ok = v.get("ok") if isinstance(v, dict) else v
    return {True: "✓", False: "✗", None: "·", "warn": "!"}.get(ok, "?")


def print_table(results, deck, dt):
    hdr = f"{'piece':12} {'status':11} " + " ".join(f"{name:>4}" for _, name in COLS) + "  notes"
    print(hdr)
    print("-" * len(hdr))
    for r in results:
        if "error" in r:
            print(f"{r['stem']:12} {'ERROR':11} {r['error'].splitlines()[-1]}")
            continue
        notes = []
        if r.get("5", {}).get("gold_pct") is not None and r["kind"] == "court":
            notes.append(f"gold {r['5']['gold_pct']}%")
        if r["kind"] == "back" and "knockout" in r.get("11", {}):
            notes.append(f"KO {r['11']['knockout']:.1%}")
        for k, _ in COLS:
            v = r.get(k)
            if isinstance(v, dict) and v.get("ok") in (False, "warn"):
                notes.append(f"[{k}] " + "; ".join(str(x) for x in v.get("detail", [])[:2]))
        row = f"{r['stem']:12} {str(r.get('status')):11} " + " ".join(f"{_sym(r.get(k)):>4}" for k, _ in COLS)
        print(row + ("  " + " | ".join(notes) if notes else ""))
    print("-" * len(hdr))
    io_ = deck["index_overlay"]
    print(f"deck-wide 6 (index overlay): {_sym(io_)} worst {io_['worst_px']} px"
          + ("; " + "; ".join(io_['detail'][:3]) if io_['detail'] else ""))
    e2 = deck["e2_clearances"]
    print("§E.2 clearances built (brief ≥ 35 / ≥ 37): " +
          ", ".join(f"{s} {v['field_pip_vs_10_index']:.1f}/{v['centre_vs_side']:.1f}" for s, v in e2.items()))
    tot = {"✓": 0, "✗": 0, "!": 0}
    for r in results:
        for k, _ in COLS:
            s = _sym(r.get(k))
            if s in tot:
                tot[s] += 1
    print(f"checks: {tot['✓']} pass, {tot['✗']} fail, {tot['!']} warn  ·  {len(results)} pieces in {dt:.1f}s")
    print("legend: ✓ pass  ✗ fail  ! warning (look at build/qa/flags/<stem>.png)  · n/a")


def run(ids: list[str], jobs: int | None = None) -> dict:
    t0 = time.time()
    # always rebuild what is checked, on both stocks, so every check sees the same art
    recs = {r["id"]: r for r in B.build(ids, "limestone")}
    white = {r["id"]: r for r in B.build(ids, "white", sheet=True)}
    jobs = jobs or os.cpu_count() or 4
    with ProcessPoolExecutor(jobs) as ex:
        results = list(ex.map(check_piece, [(recs[i], white.get(i)) for i in ids]))
    deck = {"index_overlay": deck_index_overlay(results), "e2_clearances": e2_clearances()}
    for r in results:
        r.pop("_index_region", None)
    dt = time.time() - t0
    report = {"generated": time.strftime("%Y-%m-%d %H:%M:%S"), "seconds": round(dt, 1),
              "thresholds": {"gap_parallel": GAP_PARALLEL, "gap_mark": GAP_MARK, "ko_line_min": KO_LINE_MIN,
                             "ko_line_min_back": KO_LINE_MIN_BACK, "parallel_run": PARALLEL_RUN, "raster_line_min": RASTER_LINE_MIN,
                             "raster_gap_min": RASTER_GAP_MIN, "raster_scale": SCALE,
                             "render_diff_max": RENDER_DIFF_MAX, "sym_cluster_px2": SYM_CLUSTER},
              "deck": deck, "pieces": results}
    os.makedirs(QA_DIR, exist_ok=True)
    with open(os.path.join(QA_DIR, "report.json"), "w") as fh:
        json.dump(report, fh, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o))
    print_table(results, deck, dt)
    return report


def main(argv=None):
    ap = argparse.ArgumentParser(prog="deck.qa", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("ids", nargs="*", default=["all"])
    ap.add_argument("--build", action="store_true", help="(kept for compatibility: QA always rebuilds)")
    ap.add_argument("-j", "--jobs", type=int, default=None)
    a = ap.parse_args(argv)
    ids = []
    for t in a.ids:
        for i in B.normalize(t):
            if i not in ids:
                ids.append(i)
    rep = run(ids, a.jobs)
    fails = sum(1 for r in rep["pieces"] for k, _ in COLS
                if isinstance(r.get(k), dict) and r[k].get("ok") is False) + \
        (0 if rep["deck"]["index_overlay"]["ok"] else 1) + sum(1 for r in rep["pieces"] if "error" in r)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
