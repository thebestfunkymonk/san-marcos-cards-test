"""HEADWATERS ornament core: marks, fragments and the monoline toolkit.

Everything here follows research/creative-brief.md (the LAW):

* §B.2  only legal stroke widths {1.6, 2.1, 3.1, 4.2, 6.25}; caps/joins per use;
        hatch = FINE at a 7.0 pitch, butt caps meeting the contour centreline;
        circle terminals Ø6.3 on free ends; interlace gaps 4.2 each side.
* §C    only the palette tokens; each colour lives on its print layer.
* §I.12 >= 4.2 px clear between parallel strokes; knockout lines >= 2.5 px
        with gaps >= 3 px.
* §I.25 layer ids paper, jade, red, gold, ink.

The central object is :class:`Frag` — a list of :class:`Mark` (a stroked
centreline or a filled outline, each with its colour and layer). A Frag can be

* drawn **as line on ground** ("line" mode): :meth:`Frag.svg` /
  :meth:`Frag.layers` give per-layer SVG ``<path>`` fragments, and
* **subtracted from a solid** ("knockout" mode): :meth:`Frag.outline` is the
  exact geometric union of all its marks (stroke outlines made with
  skia-pathops), and :func:`knockout` returns ``solid − outline`` as one FILL d.

Geometry is authored at FINAL size — no scale transforms anywhere. Frags are
moved with rigid transforms only (translate / rotate / ±1 mirrors), which are
applied to the path data itself, so no SVG ``transform`` is ever emitted.

Angles are *screen degrees* (inkkit convention): 0 = +x, 90 = +y (down), so a
positive rotation is clockwise on screen. ``DIAG = -45`` is the brief's "45°"
hatch, rising to the right ("/").
"""
from __future__ import annotations

import functools
import math
from dataclasses import dataclass, replace
from typing import Callable, Iterable, Sequence

import numpy as np
import pathops
import shapely
import shapely.prepared
from shapely.geometry import LineString, MultiLineString, Polygon

from inkkit import geom as G
from inkkit.svg import fmt

from deck import tokens as T

__all__ = [
    # data model
    "Mark", "Frag", "frag", "LAYER_OF", "COLOR_OF", "STYLES",
    # construction
    "Turtle", "arc_d", "arc_between", "ellipse_arc_d", "circle_d", "ellipse_d", "polyline_d", "vesica_d", "lozenge_d",
    "polar", "strip_map", "polar_map", "sample_d",
    # marks
    "stroke", "fill", "dot", "terminal", "ring", "with_terminals", "dashes",
    # hatch
    "hatch", "half_hatch", "hatch_lines", "split_region", "DIAG",
    # booleans
    "knockout", "reversed_out", "cut", "interlace", "clip", "occlude", "region", "robust_union",
    # symmetry
    "c2", "cn", "d2", "bilateral", "mirror_x", "mirror_y", "rot180",
    # bubbles
    "bubble", "bubble_row", "bubble_path", "bubble_triad", "bubble_sizes",
    # QA
    "check", "knockout_report", "knockout_vs_line", "legal_width", "hatch_ends", "crossings", "specks",
    # cleanup after occlusion cuts
    "drop_specks", "prune_hatch",
]

# ---------------------------------------------------------------------------
# derived constants (each cites the brief section it comes from)
# ---------------------------------------------------------------------------
DIAG = -45.0                       # §B.2 "45°" hatch, drawn rising to the right ("/")
MIN_CLEAR = 4.2                    # §I.12 clear gap between parallel strokes
KO_MIN_LINE = 2.5                  # §I.12 knockout lines inside solids
KO_MIN_GAP = 3.0                   # §I.12 knockout gaps
BUBBLE_RING_HOLE = 3.0             # a ring bubble keeps >= 3 px clear inside (§I.12 knockout gap)
MIN_HATCH_LEN = 2 * T.FINE         # hatch pieces shorter than this are specks, dropped (§I.3 quality)
_W_TOL = 1e-6

# colour <-> print layer (§C, §K)
LAYER_OF = {T.INK: "ink", T.RED: "red", T.JADE: "jade", T.FOIL: "gold", T.PAPER: "paper",
            T.WHITE: "paper", T.BOARD: "paper"}
COLOR_OF = {"ink": T.INK, "red": T.RED, "jade": T.JADE, "gold": T.FOIL, "paper": T.PAPER}

# cap/join presets (§B.2 "Caps and joins")
STYLES = {
    # ornament and figure strokes
    "ornament": dict(cap="round", join="round", miter=4.0),
    # hatch lines: butt caps clipped to the contour centreline
    "hatch": dict(cap="butt", join="miter", miter=4.0),
    # frames, rules, fault-steps, lozenges, ashlar, arcades
    "rule": dict(cap="butt", join="miter", miter=4.0),
    # vesica leaves, spikelets, stalactite points, compass points
    "point": dict(cap="round", join="miter", miter=10.0),
}

_CAP = {"round": pathops.LineCap.ROUND_CAP, "butt": pathops.LineCap.BUTT_CAP,
        "square": pathops.LineCap.SQUARE_CAP}
_JOIN = {"round": pathops.LineJoin.ROUND_JOIN, "miter": pathops.LineJoin.MITER_JOIN,
         "bevel": pathops.LineJoin.BEVEL_JOIN}


def legal_width(w: float) -> float:
    """Return ``w`` if it is one of the brief's stroke widths (§B.2), else raise."""
    for lw in T.LEGAL_STROKES:
        if abs(float(w) - lw) < _W_TOL:
            return lw
    raise ValueError(f"illegal stroke width {w!r}: the brief allows only {T.LEGAL_STROKES}")


def _layer_for(color: str, layer: str | None) -> str:
    if layer is not None:
        if layer not in T.LAYERS:
            raise ValueError(f"unknown layer {layer!r}; use one of {T.LAYERS}")
        return layer
    try:
        return LAYER_OF[color]
    except KeyError:
        raise ValueError(f"colour {color!r} is not a palette token (§C)") from None


# ---------------------------------------------------------------------------
# data model
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Mark:
    """One drawn thing: a stroked centreline (``kind='stroke'``) or a filled
    outline (``kind='fill'``), with its style, colour and print layer.
    ``role`` is a free tag ('hatch', 'rule', 'terminal', 'bubble', ...)."""
    d: str
    kind: str = "stroke"
    w: float = T.FINE
    cap: str = "round"
    join: str = "round"
    miter: float = 4.0
    color: str = T.INK
    layer: str = "ink"
    role: str = ""

    def transformed(self, M) -> "Mark":
        return replace(self, d=G.transform(self.d, M))

    # exact outline of this one mark as a resolved skia path
    def skia(self) -> pathops.Path:
        """The mark's exact filled outline (strokes expanded with their own
        width, cap and join). Each SUBPATH is stroked and resolved on its
        own and the pieces are unioned pairwise, verified against GEOS
        (:func:`_union_verified`): one WINDING simplify of many touching
        subpaths (covert scallops, cut polylines) is not reliable. Cached by
        content; the returned path is a private copy."""
        return _sk_copy(_mark_skia(self.d, self.kind, float(self.w), self.cap, self.join, float(self.miter)))


class Frag:
    """A motif fragment: an ordered list of :class:`Mark`.

    Build with the helpers (:func:`stroke`, :func:`dot`, :func:`hatch`, ...),
    combine with ``+`` / ``+=``, move with :meth:`translate`, :meth:`rotate`,
    :meth:`mirror_x`, :meth:`mirror_y`, :meth:`rot180` (rigid only).

    Output:
      * ``layers()``      {layer: svg-fragment}  — "line" mode, per print layer
      * ``svg(layer)``    the fragment for one layer ('' if empty)
      * ``outline()``     FILL d: exact union of every mark (for knockouts)
      * ``shape()``       the same as a shapely geometry
      * ``to_fill()``     a Frag whose marks are all FILL outlines (strokes expanded)
    """

    __slots__ = ("marks", "_outline", "_shape", "meta")

    def __init__(self, marks: Iterable[Mark] = (), meta: dict | None = None):
        self.marks: list[Mark] = list(marks)
        self._outline: dict = {}
        self._shape: dict = {}
        # copy list values (warnings, ...) so composed Frags never alias them
        self.meta: dict = {k: (list(v) if isinstance(v, list) else v) for k, v in (meta or {}).items()}

    # -- composition --------------------------------------------------------
    def __add__(self, other: "Frag") -> "Frag":
        return Frag(self.marks + list(other.marks), _merge_meta(self.meta, other.meta))

    def __iadd__(self, other: "Frag") -> "Frag":
        self.marks.extend(other.marks)
        self.meta = _merge_meta(self.meta, other.meta)
        self._outline.clear(); self._shape.clear()
        return self

    def add(self, *others: "Frag") -> "Frag":
        for o in others:
            if o is not None:
                self += o
        return self

    def __len__(self):
        return len(self.marks)

    def __bool__(self):
        return bool(self.marks)

    def __repr__(self):
        by = {}
        for m in self.marks:
            by[m.layer] = by.get(m.layer, 0) + 1
        return f"Frag({len(self.marks)} marks {by})"

    def select(self, pred: Callable[[Mark], bool]) -> "Frag":
        """Sub-fragment of the marks for which ``pred(mark)`` is true."""
        return Frag([m for m in self.marks if pred(m)], self.meta)

    def recolor(self, color: str, layer: str | None = None) -> "Frag":
        """Same geometry in another palette colour (and its layer)."""
        lay = _layer_for(color, layer)
        return Frag([replace(m, color=color, layer=lay) for m in self.marks], self.meta)

    # -- rigid transforms (applied to the path data; no SVG transforms) ------
    def transformed(self, M) -> "Frag":
        a, b, c, d = M[:4]
        det = a * d - b * c
        # rigid = orthonormal linear part: unit columns, orthogonal, det ±1
        # (rejects scales, non-uniform det-1 stretches and shears)
        if (abs(abs(det) - 1.0) > 1e-9 or abs(a * a + b * b - 1) > 1e-9
                or abs(c * c + d * d - 1) > 1e-9 or abs(a * c + b * d) > 1e-9):
            raise ValueError("Frag transforms must be rigid (rotation/translation/±1 mirror): "
                             "author at final size instead of scaling (§B.2 Scaling)")
        meta = dict(self.meta)
        return Frag([m.transformed(M) for m in self.marks], meta)

    def translate(self, dx: float, dy: float = 0.0) -> "Frag":
        return self.transformed((1, 0, 0, 1, dx, dy))

    def rotate(self, deg: float, cx: float = 0.0, cy: float = 0.0) -> "Frag":
        if deg % 360 == 0:
            return Frag(self.marks, self.meta)
        a = math.radians(deg)
        c, s = math.cos(a), math.sin(a)
        return self.transformed((c, s, -s, c, cx - c * cx + s * cy, cy - s * cx - c * cy))

    def place(self, x: float, y: float, rot: float = 0.0) -> "Frag":
        """Rotate by ``rot`` about the local origin, then move the origin to (x, y)."""
        return self.rotate(rot).translate(x, y)

    def mirror_x(self, axis: float = T.CX) -> "Frag":
        """Mirror about the vertical line x = axis."""
        return self.transformed((-1, 0, 0, 1, 2 * axis, 0))

    def mirror_y(self, axis: float = T.CY) -> "Frag":
        """Mirror about the horizontal line y = axis."""
        return self.transformed((1, 0, 0, -1, 0, 2 * axis))

    def rot180(self, cx: float = T.CX, cy: float = T.CY) -> "Frag":
        return self.transformed((-1, 0, 0, -1, 2 * cx, 2 * cy))

    # -- output: line mode ---------------------------------------------------
    def layers(self) -> dict[str, str]:
        """{layer: svg fragment} in brief layer order (§K). Strokes of one style
        share a ``<path>``; each FILL mark is its own ``<path>``."""
        out = {}
        for lay in T.LAYERS:
            s = self.svg(lay)
            if s:
                out[lay] = s
        return out

    def fragments(self) -> dict[str, list[str]]:
        """{layer: [svg fragment]} — the shape Track A's art contract and
        ``deck.frames`` hooks consume (added by Track B2; see README)."""
        return {k: [v] for k, v in self.layers().items()}

    def items(self):
        """Mapping-style view of :meth:`fragments`, so a Frag can be returned
        wherever a ``{layer: [fragments]}`` dict is expected (e.g.
        ``deck.frames.lion_mark_fragments`` → ``medallion_fragments``)."""
        return self.fragments().items()

    def svg(self, layer: str | None = None) -> str:
        """SVG ``<path>`` elements for ``layer`` (all layers if None), in mark order.
        Consecutive stroke marks with identical style are merged into one path."""
        parts: list[str] = []
        run_key, run_d = None, []

        def flush():
            nonlocal run_key, run_d
            if run_key is not None and run_d:
                color, w, cap, join, miter = run_key
                parts.append(_path_el("".join(run_d), stroke=color, stroke_width=w, fill="none",
                                      stroke_linecap=cap, stroke_linejoin=join,
                                      stroke_miterlimit=miter if join == "miter" else None))
            run_key, run_d = None, []

        for m in self.marks:
            if layer is not None and m.layer != layer:
                continue
            if not m.d:
                continue
            if m.kind == "fill":
                flush()
                parts.append(_path_el(m.d, fill=m.color))
            else:
                key = (m.color, legal_width(m.w), m.cap, m.join, m.miter)
                if key != run_key:
                    flush()
                    run_key = key
                run_d.append(m.d)
        flush()
        return "\n".join(parts)

    # -- output: geometry ------------------------------------------------------
    def outline(self, layer: str | None = None, *, grow: float = 0.0) -> str:
        """FILL d: exact union of all marks (optionally one layer), strokes
        expanded with their width/cap/join. ``grow`` px offsets the union
        outward (round) — e.g. a clearance zone. Cached."""
        key = (layer, round(grow, 4))
        if key in self._outline:
            return self._outline[key]
        paths = [m.skia() for m in self.marks if m.d and (layer is None or m.layer == layer)]
        d = robust_union(paths)
        if grow and d:
            d = G.from_shape(G.to_shape(d, tol=0.02).buffer(grow, quad_segs=16))
        self._outline[key] = d
        return d

    def shape(self, layer: str | None = None, *, grow: float = 0.0):
        """Shapely geometry of the exact union of the marks (flattened at 0.02 px)."""
        key = (layer, round(grow, 4))
        if key not in self._shape:
            # the GEOS union of the per-mark outlines: independent of the pathops
            # union in outline(), which knockout() verifies against it
            parts = [_sk_shape(m.skia()) for m in self.marks if m.d and (layer is None or m.layer == layer)]
            s = shapely.union_all(parts) if parts else Polygon()
            if not s.is_valid:
                s = shapely.make_valid(s)
            if grow:
                s = s.buffer(grow, quad_segs=16)
            self._shape[key] = s
        return self._shape[key]

    def to_fill(self) -> "Frag":
        """Every mark as a FILL outline (same colour/layer). Useful where a
        plate must contain fills only."""
        out = []
        for m in self.marks:
            if m.kind == "fill":
                out.append(m)
            else:
                out.append(replace(m, kind="fill", d=G.from_skia(m.skia())))
        return Frag(out, self.meta)

    def bbox(self) -> tuple[float, float, float, float]:
        d = self.outline()
        if not d:
            raise ValueError("bbox of empty Frag")
        return G.bbox(d)


def _path_el(d: str, **kw) -> str:
    from inkkit.svg import path
    return path(d, **kw)


def _merge_meta(a: dict, b: dict) -> dict:
    """Merge two meta dicts: ``b`` wins for plain keys, but 'warnings' lists
    are concatenated (order kept, duplicates dropped) so composing a card
    never loses a brief-forced spacing warning."""
    out = {k: (list(v) if isinstance(v, list) else v) for k, v in a.items()}
    for k, v in b.items():
        if k == "warnings":
            out[k] = list(dict.fromkeys(list(a.get(k, [])) + list(v)))
        else:
            out[k] = list(v) if isinstance(v, list) else v
    return out


# ---------------------------------------------------------------------------
# robust unions (knockout geometry)
# ---------------------------------------------------------------------------
# skia-pathops keeps true curves, but ONE WINDING simplify of many overlapping
# contours (or even a single pairwise op) can silently mis-resolve
# near-coincident geometry: converging darter spines, touching scallop
# subpaths, shared tangents (review 2026-09: knockouts that filled a darter in
# at some rotations). Every union below is therefore built from individually
# resolved pieces, pairwise, and VERIFIED against a GEOS union of the same
# pieces; a cluster that disagrees is replaced by the GEOS result (flattened
# at 0.02 px). test_motifs.test_knockout_matches_line_mode raster-compares
# knockout mode with the renderer's line mode for every specimen.
UNION_TOL_ABS = 2.0        # px²: a union may differ from the GEOS reference by at most this ...
UNION_TOL_REL = 0.005      # ... or this fraction of its area (flattening noise), else the reference is used


def _union_tol(area: float) -> float:
    return max(UNION_TOL_ABS, UNION_TOL_REL * float(area))


def _disagree(a, b) -> float:
    """Area (px²) where two geometries REALLY disagree: their symmetric
    difference opened by 0.08 px, so flattening slivers (< 0.05 px wide)
    along long contours do not count but a wrongly filled or dropped region
    (a spine, a scallop, a cap) does."""
    sd = a.symmetric_difference(b)
    if sd.is_empty:
        return 0.0
    return float(sd.buffer(-0.08, quad_segs=2).area)


_DISAGREE_TOL = 0.5        # px² of real disagreement tolerated before the GEOS reference is used


def _npts(p: pathops.Path) -> int:
    """Number of points of a skia path (its complexity; ``len(p)`` counts contours)."""
    return len(p.points)


def _sk_copy(p: pathops.Path) -> pathops.Path:
    q = pathops.Path(fillType=p.fillType)
    q.addPath(p)
    return q


def _sk_rings(p: pathops.Path, tol: float = 0.02) -> list[np.ndarray]:
    """Closed rings of a skia path, curves flattened to ``tol`` px (direct
    from the verbs: no d-string round trip)."""
    V = pathops.PathVerb
    rings, cur = [], []

    def flush():
        if len(cur) >= 3:
            rings.append(np.asarray(cur, float))
    for verb, pts in p:
        if verb == V.MOVE:
            flush()
            cur = [pts[0]]
        elif verb == V.LINE:
            cur.append(pts[0])
        elif verb == V.QUAD:
            p0, p1, p2 = np.asarray(cur[-1], float), np.asarray(pts[0], float), np.asarray(pts[1], float)
            n = max(1, int(math.ceil(math.sqrt(float(np.hypot(*(p0 - 2 * p1 + p2))) / (4 * tol)))))
            t = np.linspace(0, 1, n + 1)[1:, None]
            cur.extend(((1 - t) ** 2 * p0 + 2 * (1 - t) * t * p1 + t * t * p2).tolist())
        elif verb == V.CUBIC:
            p0 = np.asarray(cur[-1], float)
            p1, p2, p3 = (np.asarray(q, float) for q in pts)
            M = max(float(np.hypot(*(p0 - 2 * p1 + p2))), float(np.hypot(*(p1 - 2 * p2 + p3))))
            n = max(1, int(math.ceil(math.sqrt(0.75 * M / tol))))
            t = np.linspace(0, 1, n + 1)[1:, None]
            u = 1 - t
            cur.extend((u ** 3 * p0 + 3 * u * u * t * p1 + 3 * u * t * t * p2 + t ** 3 * p3).tolist())
        elif verb == V.CLOSE:
            flush()
            cur = []
        else:                                            # conic: convert a copy and start over
            q = _sk_copy(p)
            q.convertConicsToQuads(tol)
            return _sk_rings(q, tol)
    flush()
    return rings


def _sk_shape(p: pathops.Path):
    """A resolved skia path as valid shapely geometry (flattened at 0.02 px)."""
    rings = _sk_rings(p, 0.02)
    if not rings:
        return Polygon()
    g = G._rings_to_shape_oriented(rings)
    return g if g.is_valid else shapely.make_valid(g)


# a cluster bigger than this is unioned by GEOS alone (pathops trees on dense
# polylines are slow); smaller ones keep pathops' exact curves when verified
_SK_TREE_MAX_PIECES = 24
_SK_TREE_MAX_VERBS = 1500


def _sk_union_tree(paths: list) -> pathops.Path:
    """Pairwise (balanced tree) exact union with pathops.op — never one big
    WINDING simplify, which skia gets wrong on near-coincident geometry."""
    grp = [p for p in paths if len(p)]
    if not grp:
        return pathops.Path()
    while len(grp) > 1:
        nxt = []
        for k in range(0, len(grp) - 1, 2):
            nxt.append(G._sk_op(grp[k], grp[k + 1], pathops.PathOp.UNION))
        if len(grp) % 2:
            nxt.append(grp[-1])
        grp = nxt
    return grp[0]


def _sk_clusters(paths: list) -> list[list]:
    """Group paths into clusters whose bounding boxes touch (connected
    components). Disjoint clusters can simply be concatenated."""
    if len(paths) < 2:
        return [paths] if paths else []
    boxes = [shapely.box(*p.bounds).buffer(0.01, join_style="mitre") for p in paths]
    tree = shapely.STRtree(boxes)
    parent = list(range(len(paths)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    a_idx, b_idx = tree.query(boxes, predicate="intersects")
    for i, j in zip(a_idx, b_idx):
        ri, rj = find(int(i)), find(int(j))
        if ri != rj:
            parent[ri] = rj
    groups: dict[int, list] = {}
    for i, p in enumerate(paths):
        groups.setdefault(find(i), []).append(p)
    return list(groups.values())


def _union_verified(paths: Sequence[pathops.Path]) -> pathops.Path:
    """Exact union of RESOLVED skia paths. Bounding-box clusters are unioned
    pairwise with pathops and each cluster is verified against the GEOS
    union of its pieces; a cluster whose result differs by more than
    max(2 px², 0.5 %) is replaced by the GEOS union."""
    paths = [p for p in paths if len(p)]
    out = pathops.Path(fillType=pathops.FillType.WINDING)
    for grp in _sk_clusters(paths):
        if len(grp) == 1:
            out.addPath(grp[0])
            continue
        ref = shapely.union_all([_sk_shape(p) for p in grp])
        if not ref.is_valid:
            ref = shapely.make_valid(ref)
        u, bad = None, math.inf
        if len(grp) <= _SK_TREE_MAX_PIECES and sum(_npts(p) for p in grp) <= _SK_TREE_MAX_VERBS:
            try:
                u = _sk_union_tree(grp)
                bad = _disagree(_sk_shape(u), ref)
            except Exception:                           # pragma: no cover - defensive
                u, bad = None, math.inf
        if u is None or bad > _DISAGREE_TOL:
            u = G.to_skia(G.from_shape(ref))
        out.addPath(u)
    return out


def _cmds_skia(cmds) -> pathops.Path:
    """pathops.Path from absolute commands (parse_d output), subpaths left open unless Z."""
    p = pathops.Path()
    start = None
    open_ = False
    for c in cmds:
        t = c[0]
        if t == "M":
            p.moveTo(c[1], c[2])
            start, open_ = (c[1], c[2]), True
            continue
        if t == "Z":
            p.close()
            open_ = False
            continue
        if not open_ and start is not None:
            p.moveTo(*start)
            open_ = True
        if t == "L":
            p.lineTo(c[1], c[2])
        elif t == "C":
            p.cubicTo(*c[1:])
        elif t == "Q":
            p.quadTo(*c[1:])
    return p


def _resolved(p: pathops.Path) -> pathops.Path:
    try:
        p.simplify(fix_winding=True)
    except pathops.PathOpsError:   # pragma: no cover - defensive
        p = G.to_skia(G.resolve(G.from_skia(p)))
    return p


_GEOS_CAP = {"round": "round", "butt": "flat", "square": "square"}
_GEOS_JOIN = {"round": "round", "miter": "mitre", "bevel": "bevel"}


def _stroke_ref(subs, w: float, cap: str, join: str, miter: float):
    """GEOS reference outline of a stroke: every subpath's centreline
    (flattened at 0.02 px) buffered by w/2 with the same caps and joins.
    Exact for round and bevel joins; for miter joins GEOS clips an
    over-limit miter at the limit where SVG bevels it, so the caller gets
    both bounds: (upper = limited mitre, lower = bevel)."""
    hi, lo = [], []
    capg = _GEOS_CAP[cap]
    for cmds in subs:
        for pts, closed in G.flatten(cmds, 0.02):
            if len(pts) == 1 or (len(pts) >= 2 and float(np.abs(np.diff(pts, axis=0)).sum()) < 1e-9):
                if cap == "round":
                    g = shapely.Point(*pts[0]).buffer(w / 2, quad_segs=16)
                    hi.append(g); lo.append(g)
                continue
            if closed and len(pts) >= 3:
                line = shapely.LinearRing(pts)
            else:
                line = LineString(np.vstack([pts, pts[:1]]) if closed else pts)
            kw = dict(cap_style=capg, quad_segs=16)
            if join == "miter":
                hi.append(line.buffer(w / 2, join_style="mitre", mitre_limit=miter, **kw))
                lo.append(line.buffer(w / 2, join_style="bevel", **kw))
            else:
                g = line.buffer(w / 2, join_style=_GEOS_JOIN[join], **kw)
                hi.append(g); lo.append(g)
    return shapely.union_all(hi) if hi else Polygon(), shapely.union_all(lo) if lo else Polygon()


def _outside(a, b) -> float:
    """Area of ``a`` really outside ``b`` (slivers < 0.05 px wide ignored)."""
    d = a.difference(b)
    return 0.0 if d.is_empty else float(d.buffer(-0.08, quad_segs=2).area)


@functools.lru_cache(maxsize=40000)
def _mark_skia(d: str, kind: str, w: float, cap: str, join: str, miter: float) -> pathops.Path:
    """Resolved outline of one mark (see :meth:`Mark.skia`). Do not mutate the result.

    Strokes: each subpath is stroked by skia and resolved on its own, the
    pieces unioned pairwise (GEOS alone for big dense clusters), and the
    result VERIFIED against a GEOS buffer of the centrelines
    (:func:`_stroke_ref`) — skia's simplify can mis-resolve even a single
    self-overlapping stroke outline (a karst crescent, review 2026-09). If
    they disagree the GEOS outline is used."""
    if kind == "fill":
        return _resolved(G.to_skia(d))
    subs = [c for c in G._split_subpaths(G.parse_d(d)) if not (len(c) < 2 and c[0][0] == "M")]
    if not subs:
        return pathops.Path()
    pieces = []
    for cmds in subs:
        p = _cmds_skia(cmds)
        p.stroke(w, _CAP[cap], _JOIN[join], miter)
        p.convertConicsToQuads(0.01)
        pieces.append(_resolved(p))
    hi, lo = _stroke_ref(subs, w, cap, join, miter)
    out = pathops.Path(fillType=pathops.FillType.WINDING)
    for grp in _sk_clusters([p for p in pieces if len(p)]):
        if len(grp) == 1:
            out.addPath(grp[0])
        elif len(grp) <= _SK_TREE_MAX_PIECES and sum(_npts(p) for p in grp) <= _SK_TREE_MAX_VERBS:
            try:
                out.addPath(_sk_union_tree(grp))
            except Exception:                           # pragma: no cover - defensive
                return G.to_skia(G.from_shape(hi))
        else:
            return G.to_skia(G.from_shape(hi))          # big dense cluster: GEOS outright
    got = _sk_shape(out)
    if join == "miter":
        ok = _outside(lo, got) <= _DISAGREE_TOL and _outside(got, hi) <= _DISAGREE_TOL
    else:
        ok = _disagree(got, hi) <= _DISAGREE_TOL
    return out if ok else G.to_skia(G.from_shape(hi))


def robust_union(paths: Sequence[pathops.Path]) -> str:
    """Exact union of resolved skia paths as FILL d, VERIFIED against a GEOS
    (shapely) union of the same outlines. pathops keeps true curves but can
    silently mis-resolve near-coincident geometry (converging spines, shared
    tangents); any cluster whose result differs from the reference by more
    than max(2 px², 0.5 %) is replaced by the GEOS union (flattened at 0.02 px)."""
    paths = [p for p in paths if len(p)]
    if not paths:
        return ""
    return G.from_skia(_union_verified(paths))


def frag(*parts: Frag) -> Frag:
    """Concatenate fragments (None is skipped; an empty part still
    contributes its meta, e.g. warnings)."""
    f = Frag()
    for p in parts:
        if p is not None:
            f += p
    return f


# ---------------------------------------------------------------------------
# exact path construction
# ---------------------------------------------------------------------------
def _f(v: float) -> str:
    return fmt(float(v), 3)


def polar(cx: float, cy: float, r: float, deg: float) -> np.ndarray:
    """Point at screen angle ``deg`` on a circle."""
    a = math.radians(deg)
    return np.array([cx + r * math.cos(a), cy + r * math.sin(a)])


def arc_d(cx: float, cy: float, r: float, a0: float, a1: float, *, move: bool = True) -> str:
    """Exact circular arc from screen angle a0 to a1 (a1 > a0 → clockwise on
    screen) as SVG ``A`` commands. Spans >= 360 are split."""
    p0 = polar(cx, cy, r, a0)
    out = [f"M{_f(p0[0])} {_f(p0[1])}"] if move else []
    span = a1 - a0
    n = max(1, int(math.ceil(abs(span) / 179.0)))
    sweep = 1 if span > 0 else 0
    for k in range(1, n + 1):
        p = polar(cx, cy, r, a0 + span * k / n)
        out.append(f"A{_f(r)} {_f(r)} 0 0 {sweep} {_f(p[0])} {_f(p[1])}")
    return "".join(out)


def circle_d(cx: float, cy: float, r: float) -> str:
    """Closed circle (clockwise on screen, FILL convention)."""
    return G.circle_d(cx, cy, r)


def ellipse_arc_d(cx: float, cy: float, rx: float, ry: float, a0: float, a1: float,
                  rot: float = 0.0, *, move: bool = True) -> str:
    """Exact elliptic arc (parametric angles a0→a1, screen degrees) as SVG
    ``A`` commands; ``rot`` rotates the ellipse axes."""
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))

    def pt(t):
        x, y = rx * math.cos(math.radians(t)), ry * math.sin(math.radians(t))
        return cx + c * x - s * y, cy + s * x + c * y
    x0, y0 = pt(a0)
    out = [f"M{_f(x0)} {_f(y0)}"] if move else []
    span = a1 - a0
    n = max(1, int(math.ceil(abs(span) / 179.0)))
    sweep = 1 if span > 0 else 0
    for k in range(1, n + 1):
        x, y = pt(a0 + span * k / n)
        out.append(f"A{_f(rx)} {_f(ry)} {_f(rot)} 0 {sweep} {_f(x)} {_f(y)}")
    return "".join(out)


def arc_between(c, r: float, p_from, p_to, cw: bool = True, *, move: bool = False) -> str:
    """Arc of the circle (c, r) from ``p_from`` to ``p_to`` (both on it),
    clockwise on screen if ``cw``."""
    a0 = math.degrees(math.atan2(p_from[1] - c[1], p_from[0] - c[0]))
    a1 = math.degrees(math.atan2(p_to[1] - c[1], p_to[0] - c[0]))
    if cw:
        while a1 <= a0:
            a1 += 360
    else:
        while a1 >= a0:
            a1 -= 360
    return arc_d(c[0], c[1], r, a0, a1, move=move)


def ellipse_d(cx: float, cy: float, rx: float, ry: float, rot: float = 0.0) -> str:
    return G.ellipse_d(cx, cy, rx, ry, rot)


def polyline_d(pts, closed: bool = False) -> str:
    pts = np.asarray(pts, float)
    if len(pts) < 2:
        return ""
    s = f"M{_f(pts[0][0])} {_f(pts[0][1])}" + "".join(f"L{_f(x)} {_f(y)}" for x, y in pts[1:])
    return s + ("Z" if closed else "")


def vesica_d(p0, p1, width: float) -> str:
    """Closed vesica (two circular arcs) from tip ``p0`` to tip ``p1`` with
    maximum ``width``. Clockwise on screen."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    L = float(np.hypot(*(p1 - p0)))
    s = width / 2.0
    c = L / 2.0
    R = (c * c + s * s) / (2 * s)
    return (f"M{_f(p0[0])} {_f(p0[1])}A{_f(R)} {_f(R)} 0 0 1 {_f(p1[0])} {_f(p1[1])}"
            f"A{_f(R)} {_f(R)} 0 0 1 {_f(p0[0])} {_f(p0[1])}Z")


def lozenge_d(cx: float, cy: float, length: float, width: float, rot: float = 0.0) -> str:
    """Closed rhombus centred at (cx, cy), long axis at screen angle ``rot``."""
    a = math.radians(rot)
    u = np.array([math.cos(a), math.sin(a)])
    v = np.array([-math.sin(a), math.cos(a)])
    c = np.array([cx, cy])
    pts = [c - u * length / 2, c - v * width / 2, c + u * length / 2, c + v * width / 2]
    return polyline_d(pts, closed=True)


class Turtle:
    """Tangent-continuous path builder with exact arcs (SVG ``A``).

    ``t = Turtle(x, y, heading)`` then ``t.fd(L)``, ``t.arc(r, sweep)``
    (sweep > 0 turns right = clockwise on screen, < 0 turns left),
    ``t.line_to(x, y)``, ``t.jump(x, y, heading)`` (new subpath).
    ``t.d()`` exact path data, ``t.pts(step)`` a dense polyline,
    ``t.pos`` / ``t.heading`` the current state.
    """

    def __init__(self, x: float = 0.0, y: float = 0.0, heading: float = 0.0):
        self.x, self.y, self.h = float(x), float(y), float(heading)
        self._d: list[str] = [f"M{_f(x)} {_f(y)}"]
        self._segs: list[list] = [[]]          # per subpath: ('L', p0, p1) | ('A', c, r, a0, a1)
        self._starts = [(self.x, self.y)]

    @property
    def pos(self) -> np.ndarray:
        return np.array([self.x, self.y])

    @property
    def heading(self) -> float:
        return self.h

    def fd(self, L: float) -> "Turtle":
        a = math.radians(self.h)
        x1, y1 = self.x + L * math.cos(a), self.y + L * math.sin(a)
        self._segs[-1].append(("L", (self.x, self.y), (x1, y1)))
        self._d.append(f"L{_f(x1)} {_f(y1)}")
        self.x, self.y = x1, y1
        return self

    def line_to(self, x: float, y: float) -> "Turtle":
        dx, dy = x - self.x, y - self.y
        if abs(dx) + abs(dy) > 1e-12:
            self.h = math.degrees(math.atan2(dy, dx))
        self._segs[-1].append(("L", (self.x, self.y), (x, y)))
        self._d.append(f"L{_f(x)} {_f(y)}")
        self.x, self.y = float(x), float(y)
        return self

    def arc(self, r: float, sweep: float) -> "Turtle":
        """Turn by ``sweep`` degrees along a circle of radius ``r``."""
        if abs(sweep) < 1e-12:
            return self
        side = 1.0 if sweep > 0 else -1.0
        n = np.array([math.cos(math.radians(self.h + 90 * side)), math.sin(math.radians(self.h + 90 * side))])
        c = np.array([self.x, self.y]) + r * n
        a0 = math.degrees(math.atan2(self.y - c[1], self.x - c[0]))
        a1 = a0 + sweep
        self._segs[-1].append(("A", tuple(c), r, a0, a1))
        self._d.append(arc_d(c[0], c[1], r, a0, a1, move=False))
        p = polar(c[0], c[1], r, a1)
        self.x, self.y = float(p[0]), float(p[1])
        self.h += sweep
        return self

    def jump(self, x: float, y: float, heading: float | None = None) -> "Turtle":
        self.x, self.y = float(x), float(y)
        if heading is not None:
            self.h = float(heading)
        self._d.append(f"M{_f(x)} {_f(y)}")
        self._segs.append([])
        self._starts.append((self.x, self.y))
        return self

    def close(self) -> "Turtle":
        self._d.append("Z")
        return self

    def d(self) -> str:
        return "".join(self._d)

    def pts(self, step: float = 0.25) -> list[np.ndarray]:
        """Dense polylines, one per subpath (for strip mapping / regions)."""
        out = []
        for segs, st in zip(self._segs, self._starts):
            P = [np.array(st)]
            for s in segs:
                if s[0] == "L":
                    p0, p1 = np.array(s[1]), np.array(s[2])
                    n = max(1, int(math.ceil(np.hypot(*(p1 - p0)) / step)))
                    t = np.linspace(0, 1, n + 1)[1:, None]
                    P.extend(p0 + (p1 - p0) * t)
                else:
                    c, r, a0, a1 = s[1], s[2], s[3], s[4]
                    n = max(2, int(math.ceil(abs(math.radians(a1 - a0)) * r / step)))
                    a = np.radians(np.linspace(a0, a1, n + 1)[1:])
                    P.extend(np.column_stack([c[0] + r * np.cos(a), c[1] + r * np.sin(a)]))
            out.append(np.array(P))
        return out


def sample_d(d: str, step: float = 0.25) -> list[tuple[np.ndarray, bool]]:
    """Dense (points, closed) polylines of any path data."""
    out = []
    for pts, closed in G.flatten(d, 0.01):
        if len(pts) >= 2:
            cv = G.Curve(pts, closed)
            if cv.length > 0:
                out.append((cv.resample(step), closed))
    return out


def strip_map(uv: np.ndarray, frame: Callable[[np.ndarray], np.ndarray]) -> np.ndarray:
    """Apply a mapping ``frame(uv) -> xy`` to local strip coordinates."""
    return frame(np.asarray(uv, float))


def polar_map(cx: float, cy: float, r_base: float, theta0: float = -90.0, outward: bool = True):
    """Frame for a ring: local u (px along the base circle, + = clockwise on
    screen) and v (px up from the base; up = outward if ``outward``) → page xy.
    Local motifs are authored with y DOWN, so local 'up' is −y: pass pts with
    columns (u, y_local) and the map uses v = −y_local."""
    sgn = 1.0 if outward else -1.0

    def f(P):
        u, yl = P[..., 0], P[..., 1]
        th = np.radians(theta0) + u / r_base
        r = r_base + sgn * (-yl)
        return np.stack([cx + r * np.cos(th), cy + r * np.sin(th)], axis=-1)
    return f


# ---------------------------------------------------------------------------
# marks
# ---------------------------------------------------------------------------
def stroke(d, w: float = T.FINE, *, style: str = "ornament", terminals: str | None = None,
           color: str = T.INK, layer: str | None = None, role: str = "") -> Frag:
    """A monoline stroke. ``w`` must be a legal width (§B.2); ``style`` picks
    caps/joins from :data:`STYLES` ('ornament' | 'hatch' | 'rule' | 'point').
    ``d`` may be path data, a point array or a list of point arrays.
    ``terminals`` = 'start' | 'end' | 'both' adds Ø6.3 circle terminals at the
    free ends of every open subpath (§B.2)."""
    lw = legal_width(w)
    st = STYLES[style]
    lay = _layer_for(color, layer)
    if not isinstance(d, str):
        d = _to_d(d)
    if not d:
        return Frag()
    f = Frag([Mark(d, "stroke", lw, st["cap"], st["join"], st["miter"], color, lay, role)])
    if terminals:
        f += with_terminals(d, terminals, color=color, layer=lay)
    return f


def _to_d(x) -> str:
    if isinstance(x, np.ndarray) and x.ndim == 2:
        return polyline_d(x)
    if isinstance(x, (list, tuple)) and x and isinstance(x[0], np.ndarray) and x[0].ndim == 2:
        return "".join(polyline_d(p) for p in x)
    return G.polys_d(G.as_polys(x))


def fill(d: str, *, color: str = T.INK, layer: str | None = None, role: str = "") -> Frag:
    """A filled shape (resolved and wound clockwise so fills compose by union)."""
    if not d:
        return Frag()
    return Frag([Mark(G.resolve(d), "fill", 0.0, "butt", "miter", 4.0, color,
                      _layer_for(color, layer), role)])


def dot(x: float, y: float, d: float = T.TERMINAL_D, *, color: str = T.INK,
        layer: str | None = None, role: str = "dot") -> Frag:
    """A solid dot of diameter ``d`` (the brief's dots are Ø 4.2 / 6.3 / 8.4)."""
    return Frag([Mark(G.circle_d(x, y, d / 2), "fill", 0.0, "butt", "miter", 4.0, color,
                      _layer_for(color, layer), role)])


def terminal(x: float, y: float, **kw) -> Frag:
    """The Ø6.3 circle terminal (§B.2) as a solid dot."""
    kw.setdefault("role", "terminal")
    return dot(x, y, T.TERMINAL_D, **kw)


def ring(x: float, y: float, d: float, w: float = T.FINE, **kw) -> Frag:
    """A stroked circle of centreline diameter ``d``."""
    return stroke(G.circle_d(x, y, d / 2), w, **kw)


def with_terminals(d: str, ends: str = "both", *, color: str = T.INK, layer: str | None = None) -> Frag:
    """Ø6.3 terminal dots centred on the free ends of each open subpath of ``d``."""
    f = Frag()
    for pts, closed in G.flatten(d, 0.01):
        if closed or len(pts) < 2:
            continue
        if ends in ("start", "both"):
            f += terminal(*pts[0], color=color, layer=layer)
        if ends in ("end", "both"):
            f += terminal(*pts[-1], color=color, layer=layer)
    return f


def dashes(pts: np.ndarray, on: float = 8.0, off: float = 6.0, *, phase: float = 0.0,
           min_len: float = 2.0) -> list[np.ndarray]:
    """Split a polyline into explicit dash polylines (``on`` px drawn, ``off``
    px gap, starting ``phase`` px into the pattern). Geometric, so knockouts
    and renderers agree. Pieces shorter than ``min_len`` are dropped."""
    cv = G.Curve(np.asarray(pts, float))
    L = cv.length
    out = []
    s = -phase
    per = on + off
    while s < L:
        a, b = max(s, 0.0), min(s + on, L)
        if b - a >= min_len:
            k = max(2, int(math.ceil((b - a) / 0.5)) + 1)
            out.append(cv.at_s(np.linspace(a, b, k)))
        s += per
    return out


# ---------------------------------------------------------------------------
# regions and hatching
# ---------------------------------------------------------------------------
def region(x):
    """Any closed pathlike → valid shapely (Multi)Polygon (flattened at 0.01 px)."""
    if isinstance(x, shapely.Geometry):
        g = x
    elif isinstance(x, Frag):
        g = x.shape()
    else:
        g = G.to_shape(x, tol=0.01)
    if not g.is_valid:
        g = shapely.make_valid(g)
    return g


def hatch_lines(reg, angle: float = DIAG, pitch: float = T.HATCH_PITCH, *,
                origin=None, min_len: float = MIN_HATCH_LEN) -> list[np.ndarray]:
    """Straight parallel lines at ``angle`` (screen degrees), ``pitch`` apart,
    clipped exactly to ``reg``. Without ``origin`` the set is centred in the
    region along the step direction (end margins ≈ one pitch, so the last
    gap matches the rest); with ``origin`` = (x, y) one line passes through
    that point (use it to align hatch across neighbouring cells)."""
    g = region(reg)
    if g.is_empty:
        return []
    a = math.radians(angle)
    u = np.array([math.cos(a), math.sin(a)])
    v = np.array([-math.sin(a), math.cos(a)])
    coords = np.vstack([np.asarray(p.exterior.coords) for p in _polys(g)])
    proj = coords @ v
    vmin, vmax = float(proj.min()), float(proj.max())
    along = coords @ u
    umin, umax = float(along.min()) - 5, float(along.max()) + 5
    if origin is None:
        span = vmax - vmin
        n = int(round(span / pitch)) - 1
        if n < 1:
            n = 1 if span > 2 * T.FINE + 1 else 0
        offs = (vmin + vmax) / 2 + (np.arange(n) - (n - 1) / 2) * pitch
    else:
        o = float(np.asarray(origin, float) @ v)
        k0 = math.floor((vmin - o) / pitch)
        k1 = math.ceil((vmax - o) / pitch)
        offs = o + np.arange(k0, k1 + 1) * pitch
    lines = [LineString([u * umin + v * o, u * umax + v * o]) for o in offs]
    if not lines:
        return []
    res = shapely.intersection(MultiLineString(lines), g)
    out = []
    for ln in _lines(res):
        c = np.asarray(ln.coords)
        if len(c) >= 2 and np.hypot(*(c[-1] - c[0])) >= min_len:
            out.append(c[[0, -1]] if len(c) > 2 and _straight(c) else c)
    return out


def _straight(c):
    d = c[-1] - c[0]
    n = np.hypot(*d)
    if n == 0:
        return True
    perp = np.abs((c - c[0]) @ np.array([-d[1], d[0]]) / n)
    return perp.max() < 1e-6


def _polys(g):
    if g.is_empty:
        return []
    if g.geom_type == "Polygon":
        return [g]
    return [p for p in getattr(g, "geoms", []) if p.geom_type == "Polygon" and not p.is_empty] + \
        [q for p in getattr(g, "geoms", []) if p.geom_type == "MultiPolygon" for q in p.geoms]


def _lines(g):
    if g.is_empty:
        return []
    if g.geom_type == "LineString":
        return [g]
    out = []
    for p in getattr(g, "geoms", []):
        out += _lines(p)
    return out


def hatch(reg, angle: float = DIAG, pitch: float = T.HATCH_PITCH, *, origin=None,
          w: float = T.FINE, color: str = T.INK, layer: str | None = None,
          min_len: float = MIN_HATCH_LEN) -> Frag:
    """FINE hatch (§B.2) filling a whole region, butt caps on the region's
    boundary (which should be a contour centreline drawn by the caller)."""
    lines = hatch_lines(reg, angle, pitch, origin=origin, min_len=min_len)
    return stroke(lines, w, style="hatch", color=color, layer=layer, role="hatch") if lines else Frag()


def split_region(shape, split="left", side: int | None = None):
    """Return the half of ``shape`` selected by ``split``:

    * 'left' | 'right' | 'top' | 'bottom' — split by the vertical/horizontal
      line through the bbox centre, keep that half;
    * ((x0, y0), (x1, y1)) — split by that (infinite) line; keep ``side``
      (+1 = left of the p0→p1 direction on screen, −1 = right; default +1);
    * a polyline / path d (e.g. an S midrib) — its ends are extended
      tangentially; keep ``side`` as above.
    """
    g = region(shape)
    if g.is_empty:
        return g
    x0, y0, x1, y1 = g.bounds
    big = 4 * (x1 - x0 + y1 - y0) + 100
    if isinstance(split, str) and split in ("left", "right", "top", "bottom"):
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        box = {"left": (x0 - 1, y0 - 1, mx, y1 + 1), "right": (mx, y0 - 1, x1 + 1, y1 + 1),
               "top": (x0 - 1, y0 - 1, x1 + 1, my), "bottom": (x0 - 1, my, x1 + 1, y1 + 1)}[split]
        return g.intersection(shapely.box(*box))
    side = 1 if side is None else side
    if isinstance(split, str):
        P = sample_d(split, 0.5)[0][0]
    else:
        P = np.asarray(split, float)
    if len(P) == 2:
        # straight split: exact half-plane
        u = P[1] - P[0]
        u = u / max(np.hypot(*u), 1e-12)
        nl = np.array([u[1], -u[0]])              # screen-left normal of p0→p1 (y down)
        nrm = nl if side > 0 else -nl
        c = P[0]
        quad = [c - u * big, c + u * big, c + u * big + nrm * big, c - u * big + nrm * big]
        return g.intersection(Polygon(quad))
    from shapely.ops import split as _split
    t0 = P[0] - P[1]; t0 /= max(np.hypot(*t0), 1e-12)
    t1 = P[-1] - P[-2]; t1 /= max(np.hypot(*t1), 1e-12)
    P = np.vstack([P[0] + t0 * big, P, P[-1] + t1 * big])
    ls = LineString(P)
    keep = []
    for pc in _polys(_split(g, ls)) if not g.is_empty else []:
        if pc.area < 1e-6:
            continue
        rp = pc.representative_point()
        q = np.array([rp.x, rp.y])
        i = int(np.clip(np.argmin(np.hypot(*(P - q).T)), 0, len(P) - 2))
        # nearest segment by projection
        best, bi = 1e18, i
        for j in range(max(0, i - 3), min(len(P) - 1, i + 3)):
            a, b = P[j], P[j + 1]
            ab = b - a
            t = np.clip(((q - a) @ ab) / max(ab @ ab, 1e-12), 0, 1)
            dd = np.hypot(*(a + ab * t - q))
            if dd < best:
                best, bi = dd, j
        a, b = P[bi], P[bi + 1]
        cr = (b[0] - a[0]) * (q[1] - a[1]) - (b[1] - a[1]) * (q[0] - a[0])
        if (cr < 0) == (side > 0):                 # screen-left ⇔ negative cross (y down)
            keep.append(pc)
    return shapely.union_all(keep) if keep else Polygon()


def half_hatch(shape, split="left", angle: float | str = DIAG, *, side: int | None = None,
               pitch: float = T.HATCH_PITCH, origin=None, w: float = T.FINE,
               color: str = T.INK, layer: str | None = None, min_len: float = MIN_HATCH_LEN) -> Frag:
    """Jinkins half-hatching (§B.2): FINE hatch at a 7.0 pitch filling exactly
    one half of ``shape``. See :func:`split_region` for ``split``/``side``.
    ``angle`` in screen degrees, or 'perp' (perpendicular to the split's
    chord — leaves) / 'para'. Hatch lines end (butt) on the contour and split
    centrelines; draw those with :func:`stroke` to cover the joins."""
    part = split_region(shape, split, side)
    if isinstance(angle, str):
        ch = _chord_angle(split, shape)
        angle = ch + 90.0 if angle == "perp" else ch
    return hatch(part, angle, pitch, origin=origin, w=w, color=color, layer=layer, min_len=min_len)


def _chord_angle(split, shape) -> float:
    if isinstance(split, str) and split in ("left", "right"):
        return 90.0
    if isinstance(split, str) and split in ("top", "bottom"):
        return 0.0
    P = sample_d(split, 1.0)[0][0] if isinstance(split, str) else np.asarray(split, float)
    d = P[-1] - P[0]
    return math.degrees(math.atan2(d[1], d[0]))


# ---------------------------------------------------------------------------
# booleans: knockout, cut / interlace, clip
# ---------------------------------------------------------------------------
def knockout(solid, *frags: Frag, grow: float = 0.0) -> str:
    """GEOMETRIC knockout (§I.25): ``solid`` (FILL d) minus the exact union of
    every mark of ``frags`` → FILL d. Nothing paper-coloured is painted; the
    lines are holes in the solid. ``grow`` widens the holes (px).

    The pathops result is verified against an independent GEOS reference
    (the solid minus the union of every mark's own outline, :meth:`Frag.shape`);
    where they disagree by more than 0.5 px² the GEOS result is returned, so
    a knockout never fills in or drops a line (see :func:`knockout_vs_line`)."""
    frags = [f for f in frags if f]
    parts = [f.outline(grow=grow) if grow else f.outline() for f in frags]
    parts = [p for p in parts if p]
    if not parts:
        return G.resolve(solid)
    s_hol = shapely.union_all([f.shape(grow=grow) if grow else f.shape() for f in frags])
    sol = G._sk_simplified(G.to_skia(solid))
    s_sol = _sk_shape(sol)
    ref = s_sol.difference(s_hol)
    if not ref.is_valid:
        ref = shapely.make_valid(ref)
    holes_sk = [G.to_skia(p) for p in parts]            # outline() is already resolved
    if sum(_npts(h) for h in holes_sk) > 4 * _SK_TREE_MAX_VERBS:
        return G.from_shape(ref)                        # dense (occluded / clipped polylines): GEOS outright
    holes = holes_sk[0] if len(holes_sk) == 1 else _union_verified(holes_sk)
    try:
        res = G._sk_op(sol, holes, pathops.PathOp.DIFFERENCE)
        if _disagree(_sk_shape(res), ref) <= _DISAGREE_TOL:
            return G.from_skia(res)
    except Exception:                                   # pragma: no cover - defensive
        pass
    return G.from_shape(ref)


def reversed_out(solid, *frags: Frag, color: str = T.JADE, layer: str | None = None) -> Frag:
    """A Frag holding ``solid`` with ``frags`` knocked out of it (line reversed
    out to paper, e.g. the card back on the jade flood)."""
    return fill(knockout(solid, *frags), color=color, layer=layer, role="flood")


def cut(f: Frag, obstacle, gap: float = T.INTERLACE_GAP) -> Frag:
    """Break ``f`` where it meets ``obstacle`` (a Frag — its marks' outlines —
    or any FILL pathlike / shapely geometry), leaving ``gap`` px CLEAR between
    ``obstacle``'s edge and what remains of each mark (round caps accounted
    for). Stroke marks are cut on their centrelines (they stay strokes); fill
    marks are differenced. → new Frag."""
    obs = obstacle.shape() if isinstance(obstacle, Frag) else region(obstacle)
    if obs.is_empty:
        return Frag(f.marks, f.meta)
    out = []
    cache: dict[float, object] = {}
    for m in f.marks:
        if m.kind == "fill":
            zone = cache.setdefault(("f", gap), obs.buffer(gap, quad_segs=16) if gap > 0 else obs)
            d = G.from_shape(G.to_shape(m.d, tol=0.01).difference(zone))
            if d:
                out.append(replace(m, d=d))
            continue
        # clearance of the stroke's end from the obstacle edge:
        # round cap reaches w/2 past the cut; butt corners reach up to w/2 at
        # oblique crossings — keep w/2 for both (conservative).
        reach = gap + m.w / 2
        zone = cache.setdefault(("s", reach), obs.buffer(reach, quad_segs=16))
        pieces = _clip_out_lines(m.d, zone)
        if pieces:
            out.append(replace(m, d="".join(polyline_d(p) for p in pieces)))
    return Frag(out, f.meta)


def _clip_out_lines(d: str, zone) -> list[np.ndarray]:
    lines = []
    for pts, closed in G.flatten(d, 0.01):
        if len(pts) < 2:
            continue
        lines.append(LineString(np.vstack([pts, pts[:1]]) if closed else pts))
    if not lines:
        return []
    res = shapely.difference(MultiLineString(lines), zone)
    try:
        res = shapely.line_merge(res)
    except shapely.errors.GEOSException:  # pragma: no cover
        pass
    out = []
    for ln in _lines(res):
        c = np.asarray(ln.coords)
        if len(c) >= 2 and ln.length > 0.3:
            out.append(c)
    return out


def interlace(under: Frag, over: Frag, gap: float = T.INTERLACE_GAP) -> Frag:
    """Interlace (§B.2): the UNDER fragment breaks with ``gap`` px clear each
    side of the OVER fragment's strokes. Returns ``cut(under) + over``."""
    return cut(under, over, gap) + over


def clip(f: Frag, reg, *, inside: bool = True, keep_caps: bool = False) -> Frag:
    """Keep the parts of ``f`` inside ``reg`` (``inside=False``: outside).
    Stroke centrelines are clipped (ends then sit on the region boundary —
    right for hatch and for lines that meet a contour); with ``keep_caps`` the
    region is first shrunk by w/2 so round caps stay inside."""
    g = region(reg)
    out = []
    for m in f.marks:
        if m.kind == "fill":
            s = G.to_shape(m.d, tol=0.01)
            s = s.intersection(g) if inside else s.difference(g)
            d = G.from_shape(s)
            if d:
                out.append(replace(m, d=d))
            continue
        zone = g.buffer(-m.w / 2 if inside else m.w / 2) if keep_caps else g
        lines = [LineString(np.vstack([p, p[:1]]) if c else p) for p, c in G.flatten(m.d, 0.01) if len(p) >= 2]
        if not lines:
            continue
        ml = MultiLineString(lines)
        res = shapely.intersection(ml, zone) if inside else shapely.difference(ml, zone)
        try:
            res = shapely.line_merge(res)
        except shapely.errors.GEOSException:  # pragma: no cover
            pass
        pieces = [np.asarray(l.coords) for l in _lines(res) if l.length > 0.3]
        if pieces:
            out.append(replace(m, d="".join(polyline_d(p) for p in pieces)))
    return Frag(out, f.meta)


def occlude(f: Frag, front) -> Frag:
    """OCCLUSION by T-junction (the line-art convention for a thing that lies
    BEHIND another and does not re-emerge beyond it): every part of ``f``
    inside ``front`` — the region bounded by the front object's contour
    CENTRELINE (a shapely geometry, FILL d, or a Frag's filled outline) — is
    removed, so stroke centrelines (hatch included) end exactly on that
    centreline and the front contour's own stroke covers the joint. Use
    :func:`cut` / :func:`interlace` (4.2 px gaps) only where an under-line
    passes beneath and continues on the other side (§B.2 interlace)."""
    return clip(f, front, inside=False)


# ---------------------------------------------------------------------------
# symmetry
# ---------------------------------------------------------------------------
def mirror_x(f: Frag, axis: float = T.CX) -> Frag:
    return f.mirror_x(axis)


def mirror_y(f: Frag, axis: float = T.CY) -> Frag:
    return f.mirror_y(axis)


def rot180(f: Frag, cx: float = T.CX, cy: float = T.CY) -> Frag:
    return f.rot180(cx, cy)


def c2(f: Frag, cx: float = T.CX, cy: float = T.CY) -> Frag:
    """``f`` plus its 180° copy about (cx, cy) — two-way symmetry (§H.19)."""
    return f + f.rot180(cx, cy)


def cn(f: Frag, n: int, cx: float = T.CX, cy: float = T.CY, start: float = 0.0) -> Frag:
    """n rotated copies about (cx, cy) (C_N). n even ⇒ C2-safe."""
    out = Frag()
    for k in range(n):
        out += f.rotate(start + 360.0 * k / n, cx, cy)
    return out


def bilateral(f: Frag, axis: float = T.CX) -> Frag:
    """``f`` plus its mirror about x = axis."""
    return f + f.mirror_x(axis)


def d2(f: Frag, cx: float = T.CX, cy: float = T.CY) -> Frag:
    """Four copies: identity, mirror-x, mirror-y, rot180 (the back frame's D2)."""
    return f + f.mirror_x(cx) + f.mirror_y(cy) + f.rot180(cx, cy)


# ---------------------------------------------------------------------------
# bubbles (§G.9 bubble beading)
# ---------------------------------------------------------------------------
def _bubble_outer(d: float, style: str, w: float) -> float:
    return d if style == "dot" else d + w


def _auto_style(dmin: float, w: float) -> str:
    """Rings when the smallest ring keeps a >= 3 px hole, otherwise dots."""
    return "ring" if dmin - w >= BUBBLE_RING_HOLE else "dot"


def bubble(x: float, y: float, d: float, *, style: str = "auto", w: float = T.FINE,
           color: str = T.INK, layer: str | None = None) -> Frag:
    """One bubble. 'ring' = stroked circle of CENTRELINE diameter ``d``;
    'dot' = solid disc of diameter ``d``; 'auto' picks ring when the hole
    would be >= 3 px (d − w >= 3)."""
    st = _auto_style(d, w) if style == "auto" else style
    if st == "dot":
        return dot(x, y, d, color=color, layer=layer, role="bubble")
    return stroke(G.circle_d(x, y, d / 2), w, color=color, layer=layer, role="bubble")


def bubble_sizes(d0: float, n: int, ratio: float = 1.2) -> list[float]:
    """Diameters growing ×``ratio`` (§G.9)."""
    return [d0 * ratio ** k for k in range(n)]


def bubble_row(p0, p1, sizes: Sequence[float], *, style: str = "auto", w: float = T.FINE,
               color: str = T.INK, layer: str | None = None) -> Frag:
    """Bubbles of the given diameters with CENTRES of the first and last on
    ``p0`` and ``p1`` (rise direction p0 → p1) and equal clear gaps between
    neighbours. Raises if they do not fit with >= 3 px clear."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    st = _auto_style(min(sizes), w) if style == "auto" else style
    D = [_bubble_outer(s, st, w) for s in sizes]
    L = float(np.hypot(*(p1 - p0)))
    u = (p1 - p0) / L if L > 0 else np.array([0.0, -1.0])
    n = len(sizes)
    if n == 1:
        return bubble(*p0, sizes[0], style=st, w=w, color=color, layer=layer)
    inner = L - D[0] / 2 - D[-1] / 2 - sum(D[1:-1])
    g = inner / (n - 1)
    if g < KO_MIN_GAP - 1e-6:
        raise ValueError(f"bubble_row: clear gap {g:.2f} px < {KO_MIN_GAP} (sizes too big for the run)")
    f = Frag()
    s = 0.0
    for k, (d, Do) in enumerate(zip(sizes, D)):
        if k:
            s += D[k - 1] / 2 + g + Do / 2
        f += bubble(*(p0 + u * s), d, style=st, w=w, color=color, layer=layer)
    f.meta["bubble_gap"] = g
    return f


def bubble_path(path, d0: float, *, ratio: float = 1.2, gap: float | None = None, n: int | None = None,
                style: str = "auto", w: float = T.FINE, color: str = T.INK,
                layer: str | None = None, d_max: float | None = None) -> Frag:
    """Bubbles along a path (start = bottom of the rise), growing ×``ratio``.
    ``gap`` = clear gap (default 0.6 × the mean outer diameter, >= 3 px).
    Stops at the path end or after ``n`` bubbles; sizes cap at ``d_max``."""
    cv = G.Curve(path if not isinstance(path, str) else sample_d(path, 0.25)[0][0])
    sizes = []
    k = 0
    while n is None or k < n:
        d = d0 * ratio ** k
        if d_max is not None:
            d = min(d, d_max)
        sizes.append(d)
        k += 1
        if n is None and k > 200:
            break
    st = _auto_style(min(sizes), w) if style == "auto" else style
    f = Frag()
    s = 0.0
    prev = None
    for k, d in enumerate(sizes):
        Do = _bubble_outer(d, st, w)
        if prev is not None:
            g = gap if gap is not None else max(KO_MIN_GAP, 0.6 * (prev + Do) / 2)
            s += prev / 2 + g + Do / 2
        if s > cv.length + 1e-6:
            break
        f += bubble(*cv.at_s(s), d, style=st, w=w, color=color, layer=layer)
        prev = Do
    return f


def bubble_triad(x: float, y: float, angle: float = -45.0, sizes=(4.2, 6.3, 8.4), *,
                 gap: float = KO_MIN_GAP + 0.5, style: str = "dot", w: float = T.FINE,
                 color: str = T.INK, layer: str | None = None) -> Frag:
    """Three bubbles on a line through (x, y) (the middle one's centre) at
    screen ``angle``; sizes in order along the direction. Symmetric sizes
    (6, 10, 6) give a C2-symmetric mark."""
    a = math.radians(angle)
    u = np.array([math.cos(a), math.sin(a)])
    D = [_bubble_outer(s, style, w) for s in sizes]
    c = np.array([x, y])
    p0 = c - u * (D[0] / 2 + gap + D[1] / 2)
    p2 = c + u * (D[1] / 2 + gap + D[2] / 2)
    return (bubble(*p0, sizes[0], style=style, w=w, color=color, layer=layer)
            + bubble(*c, sizes[1], style=style, w=w, color=color, layer=layer)
            + bubble(*p2, sizes[2], style=style, w=w, color=color, layer=layer))


# ---------------------------------------------------------------------------
# QA
# ---------------------------------------------------------------------------
def check(f: Frag) -> list[str]:
    """Rule violations in a Frag: illegal widths/colours/layers, colour on the
    wrong layer. Returns a list of messages (empty = clean)."""
    msgs = []
    for i, m in enumerate(f.marks):
        if m.kind == "stroke":
            try:
                legal_width(m.w)
            except ValueError as e:
                msgs.append(f"mark {i}: {e}")
        if m.color not in T.LEGAL_COLORS:
            msgs.append(f"mark {i}: colour {m.color} not in palette")
        if m.layer not in T.LAYERS:
            msgs.append(f"mark {i}: layer {m.layer} not in {T.LAYERS}")
        elif m.color in LAYER_OF and LAYER_OF[m.color] != m.layer:
            msgs.append(f"mark {i}: colour {m.color} on layer {m.layer}")
    return msgs


def knockout_report(solid, ko_d: str, *, min_line: float = KO_MIN_LINE,
                    min_gap: float = KO_MIN_GAP, res: float = 0.25) -> dict:
    """Morphological check of a knockout (§I.12). Rasterises at ``res`` px and
    reports the paper-line area that vanishes under an opening of ``min_line``
    (lines thinner than that) and the solid area that vanishes under an
    opening of ``min_gap`` (gaps narrower than that), in px² and as a fraction.
    Small non-zero values are expected at sharp tips and V-junctions."""
    from scipy import ndimage
    gs = region(solid)
    gk = region(ko_d) if ko_d else Polygon()
    x0, y0, x1, y1 = gs.bounds
    W = int(math.ceil((x1 - x0) / res)) + 4
    H = int(math.ceil((y1 - y0) / res)) + 4
    xs = x0 - 2 * res + (np.arange(W) + 0.5) * res
    ys = y0 - 2 * res + (np.arange(H) + 0.5) * res
    X, Y = np.meshgrid(xs, ys)
    inside_solid = shapely.contains_xy(gs, X, Y)
    ink = shapely.contains_xy(gk, X, Y) if not gk.is_empty else np.zeros_like(inside_solid)
    paper = inside_solid & ~ink

    def disk(r):
        k = int(math.ceil(r / res))
        yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
        return (xx * res) ** 2 + (yy * res) ** 2 <= r * r
    open_paper = ndimage.binary_opening(paper, structure=disk(min_line / 2 * 0.98))
    open_ink = ndimage.binary_opening(ink, structure=disk(min_gap / 2 * 0.98))
    a = res * res
    thin_lines = float((paper & ~open_paper).sum() * a)
    thin_gaps = float((ink & ~open_ink).sum() * a)
    return {"paper_area": float(paper.sum() * a), "ink_area": float(ink.sum() * a),
            "thin_line_area": thin_lines, "thin_line_frac": thin_lines / max(paper.sum() * a, 1e-9),
            "thin_gap_area": thin_gaps, "thin_gap_frac": thin_gaps / max(ink.sum() * a, 1e-9),
            "coverage": float(paper.sum() / max(inside_solid.sum(), 1))}


def _centrelines(f: Frag, roles_out=("hatch",)):
    out = []
    for i, m in enumerate(f.marks):
        if m.kind != "stroke" or m.role in roles_out:
            continue
        for pts, cl in G.flatten(m.d, 0.05):
            if len(pts) > 1:
                out.append((i, m.role, LineString(np.vstack([pts, pts[:1]]) if cl else pts)))
    return out


def hatch_ends(f: Frag, tol: float = 1.3) -> list[tuple[float, float, float]]:
    """§B.2 / §I.3 QA: every hatch line must butt onto a drawn contour. Returns
    the hatch END points lying more than ``tol`` px from every non-hatch
    stroke centreline and fill boundary of ``f`` (x, y, distance) — hatch
    ending in mid-air. Empty = clean."""
    lines = [g for _, _, g in _centrelines(f)]
    lines += [G.to_shape(m.d, tol=0.05).boundary for m in f.marks if m.kind == "fill" and m.d]
    if not lines:
        return []
    U = shapely.union_all(lines)
    bad = []
    for m in f.marks:
        if m.kind != "stroke" or m.role != "hatch":
            continue
        for pts, cl in G.flatten(m.d, 0.05):
            for q in (pts[0], pts[-1]):
                dd = float(U.distance(shapely.Point(*q)))
                if dd > tol:
                    bad.append((float(q[0]), float(q[1]), dd))
    return bad


def crossings(f: Frag, end_tol: float = 1.0, roles_out=("hatch",)) -> list[tuple[str, str, float, float]]:
    """§I.13 QA: plain X crossings between distinct stroke centrelines (the
    under-stroke was not broken). Intersections within ``end_tol`` px of
    either line's end are T-junctions / joins and are not counted. Returns
    [(role_a, role_b, x, y)]. Empty = clean."""
    segs = _centrelines(f, roles_out)
    if len(segs) < 2:
        return []
    tree = shapely.STRtree([g for _, _, g in segs])
    out = []
    for a_i, (_, ra, a) in enumerate(segs):
        for b_i in tree.query(a):
            b_i = int(b_i)
            if b_i <= a_i:
                continue
            rb, b = segs[b_i][1], segs[b_i][2]
            inter = a.intersection(b)
            if inter.is_empty:
                continue
            ends = [shapely.Point(g.coords[k]) for g in (a, b) for k in (0, -1)]
            for g in getattr(inter, "geoms", [inter]):
                pts = [g] if g.geom_type == "Point" else ([shapely.Point(g.coords[0])] if g.geom_type == "LineString" else [])
                for pt in pts:
                    if min(e.distance(pt) for e in ends) < end_tol:
                        continue
                    if not _transversal(a, b, pt):
                        continue                      # a cusp resting on a line (touch), not an X
                    key = (ra, rb, round(pt.x, 1), round(pt.y, 1))
                    if key not in out:
                        out.append(key)
    return out


def _transversal(a, b, pt, h: float = 1.5) -> bool:
    """True if line ``b`` passes from one side of line ``a`` to the other at
    ``pt`` (a real crossing), False if it only touches (a cusp on the line)."""
    sb = b.project(pt)
    sa = a.project(pt)
    pa0, pa1 = a.interpolate(max(sa - h, 0)), a.interpolate(min(sa + h, a.length))
    ta = np.array([pa1.x - pa0.x, pa1.y - pa0.y])
    if np.hypot(*ta) < 1e-9:
        return True
    sides = []
    for sgn in (-1, 1):
        q = b.interpolate(min(max(sb + sgn * h, 0), b.length))
        v = np.array([q.x - pt.x, q.y - pt.y])
        sides.append(ta[0] * v[1] - ta[1] * v[0])
    return sides[0] * sides[1] < -1e-6


def knockout_vs_line(f: Frag, rotations: Sequence[float] = (0.0, 30.0, 137.0, 180.0), *, mirror: bool = True,
                     zoom: float = 2.0, pad: float = 8.0, renderer: str = "rsvg-convert",
                     save: str | None = None) -> dict:
    """§I.25 / §B.2 QA: does KNOCKOUT mode cut exactly the ink that LINE mode
    paints? ``f`` is tiled at each rotation (and mirrored), rigidly; line
    mode is rendered by the real renderer (strokes + fills in black on
    white) and knockout mode as a white flood with every tile knocked out
    in ONE :func:`knockout` call; the two rasters (``zoom`` px per card px)
    are compared. Returns {'bad_px', 'ink_px', 'frac', 'tiles': [(label,
    bad_px)]}: ``bad_px`` counts pixels whose value differs by more than
    half the range (anti-aliasing never does). A wrong union shows as
    hundreds of bad pixels."""
    import subprocess
    import tempfile
    from pathlib import Path as _P
    from PIL import Image
    variants = [(f"rot{r:g}", f.rotate(r, 0.0, 0.0) if r else f) for r in rotations]
    if mirror:
        variants.append(("mirror", f.mirror_x(0.0)))
    tiles, x = [], pad
    y0 = pad
    for label, g in variants:
        if not g:
            continue
        bx0, by0, bx1, by1 = g.bbox()
        t = g.translate(x - bx0, y0 - by0)
        tiles.append((label, t, (x - pad / 2, x + bx1 - bx0 + pad / 2)))
        x += bx1 - bx0 + pad
    if not tiles:
        return {"bad_px": 0, "ink_px": 0, "frac": 0.0, "tiles": []}
    Wd = x
    Ht = max(t.bbox()[3] for _, t, _ in tiles) + pad
    canvas = f"M0 0H{Wd:.2f}V{Ht:.2f}H0Z"
    black = Frag([replace(m, color=T.INK, layer="ink") for _, t, _ in tiles for m in t.marks])
    head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{Wd:.2f}" height="{Ht:.2f}" '
            f'viewBox="0 0 {Wd:.2f} {Ht:.2f}">')
    line_svg = head + f'<path d="{canvas}" fill="#FFFFFF"/>' + black.svg() + "</svg>"
    ko = knockout(canvas, *[t for _, t, _ in tiles])
    ko_svg = head + f'<path d="{canvas}" fill="{T.INK}"/><path d="{ko}" fill="#FFFFFF"/></svg>'
    with tempfile.TemporaryDirectory() as td:
        ims = []
        for name, s in (("line", line_svg), ("ko", ko_svg)):
            p = _P(td) / f"{name}.svg"
            p.write_text(s)
            png = _P(td) / f"{name}.png"
            if renderer == "resvg":
                subprocess.run(["resvg", "--zoom", str(zoom), str(p), str(png)], check=True, capture_output=True)
            else:
                subprocess.run([renderer, "-z", str(zoom), str(p), "-o", str(png)], check=True, capture_output=True)
            ims.append(np.asarray(Image.open(png).convert("L"), dtype=np.int16))
    a, b = ims
    h, w_ = min(a.shape[0], b.shape[0]), min(a.shape[1], b.shape[1])
    a, b = a[:h, :w_], b[:h, :w_]
    bad = np.abs(a - b) > 128
    if save:                                     # a diff image: red = line only, blue = knockout only
        rgb = np.repeat(((a // 2) + 127).astype(np.uint8)[..., None], 3, axis=2)
        rgb[bad & (a < 128)] = (220, 0, 0)
        rgb[bad & (a >= 128)] = (0, 0, 220)
        Image.fromarray(rgb).save(save)
    out_tiles = []
    for label, _, (u0, u1) in tiles:
        c0, c1 = int(u0 * zoom), int(math.ceil(u1 * zoom))
        out_tiles.append((label, int(bad[:, c0:c1].sum())))
    ink = int((a < 128).sum())
    return {"bad_px": int(bad.sum()), "ink_px": ink, "frac": float(bad.sum()) / max(ink, 1), "tiles": out_tiles}


def specks(f: Frag, min_len: float = 3.0, roles=None) -> list[tuple[str, float, float, float]]:
    """§I.14 QA: open stroke sub-paths shorter than ``min_len`` px (stubs an
    occlusion cut left behind, which print as stray dots). Returns
    [(role, x, y, length)]."""
    out = []
    for m in f.marks:
        if m.kind != "stroke" or (roles is not None and m.role not in roles):
            continue
        for pts, cl in G.flatten(m.d, 0.05):
            if cl or len(pts) < 2:
                continue
            L = float(np.hypot(*np.diff(pts, axis=0).T).sum())
            if L < min_len:
                out.append((m.role, float(pts[0][0]), float(pts[0][1]), L))
    return out


# ---------------------------------------------------------------------------
# cleanup after occlusion / interlace cuts (§I.14 no ragged ends, §B.2 hatch)
# ---------------------------------------------------------------------------
def drop_specks(f: Frag, min_len: float = 4.2, roles=None) -> Frag:
    """Remove the stubs an occlusion cut leaves behind: open stroke sub-paths
    shorter than ``min_len`` px (``roles`` = a tuple of roles to clean, None
    = every stroke), which would otherwise print as stray round-cap dots
    (§I.14). Closed sub-paths (rings, outlines) are kept whole."""
    out = []
    for m in f.marks:
        if m.kind != "stroke" or (roles is not None and m.role not in roles):
            out.append(m)
            continue
        keep = [(pts, cl) for pts, cl in G.flatten(m.d, 0.05)
                if cl or (len(pts) > 1 and G.Curve(pts).length >= min_len)]
        if keep:
            out.append(replace(m, d="".join(polyline_d(p, closed=cl) for p, cl in keep)))
    return Frag(out, f.meta)


def prune_hatch(f: Frag, tol: float = 1.3, *, against: Frag | None = None) -> Frag:
    """§B.2 / §I.3: drop every hatch piece (role 'hatch') with an end lying
    more than ``tol`` px from every drawn contour — the non-hatch stroke
    centrelines and fill edges of ``f`` (plus ``against``, e.g. a front
    part it was occluded by). After cuts, a hatch line whose contour was
    cut away would otherwise stop in mid-air."""
    ref = f if against is None else f + against
    lines = [g for _, _, g in _centrelines(ref)]
    lines += [G.to_shape(m.d, tol=0.05).boundary for m in ref.marks if m.kind == "fill" and m.d]
    if not lines:
        return Frag([m for m in f.marks if m.role != "hatch"], f.meta)
    U = shapely.union_all(lines)
    tree = shapely.prepared.prep(U.buffer(tol, quad_segs=4))
    out = []
    for m in f.marks:
        if m.kind != "stroke" or m.role != "hatch":
            out.append(m)
            continue
        keep = []
        for pts, cl in G.flatten(m.d, 0.05):
            if len(pts) < 2:
                continue
            if cl or (tree.contains(shapely.Point(*pts[0])) and tree.contains(shapely.Point(*pts[-1]))):
                keep.append((pts, cl))
        if keep:
            out.append(replace(m, d="".join(polyline_d(p, closed=cl) for p, cl in keep)))
    return Frag(out, f.meta)
