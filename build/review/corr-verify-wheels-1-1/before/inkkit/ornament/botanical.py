"""Botanical motifs: leaves (solid / Jinkins-style outlined with half-hatching /
engraved), sprigs & laurel, wreaths, grass and wild-rice sprays, simple
flowers, bluebonnet racemes, palmate leaves and water ripples.

Angles are screen degrees (0 = +x, -90 = up). FILL d unless noted; line-art
styles take ``lw`` (line width) and return STROKE centrelines when lw=None
(generators whose output would then mix STROKE lines with solid FILL parts
need ``parts=True`` -> {'stroke': d, 'fill': d}).

Sprays are drawn in paint order with real occlusion: later leaves hide the
leaves and stem behind them (plus an optional paper ``gap``), so outlines never
cross and the stem never shows through a leaf. ``jitter``/``seed`` add small
deterministic variations of angle, size, bend and asymmetry.
"""
from __future__ import annotations

import math

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon

from .. import geom as G
from .. import tokens as T
from ..hatch import _clip, _parallel_lines, engrave
from ..stroke import stroke

__all__ = ["leaf_shape", "leaf", "sprig", "laurel", "wreath", "grass", "rice", "flower",
           "bluebonnet", "palmate_leaf", "ripples", "LEAF_SHAPES"]

LEAF_SHAPES = {
    # width profile along the midrib, t: 0 base -> 1 tip
    "lanceolate": lambda t: np.sin(np.pi * t ** 0.78) ** 0.9,
    "laurel": lambda t: np.sin(np.pi * t ** 0.72) ** 1.05,
    "ovate": lambda t: np.sin(np.pi * t ** 0.62) ** 0.75,
    "elliptic": lambda t: np.sin(np.pi * t) ** 0.75,
    "obovate": lambda t: np.sin(np.pi * t ** 1.45) ** 0.75,
    "willow": lambda t: np.sin(np.pi * t ** 0.85) ** 1.3,
    "round": lambda t: np.sin(np.pi * t) ** 0.5,
    "grain": lambda t: np.sin(np.pi * t) ** 0.62,
    "strap": lambda t: np.clip(np.minimum(t / 0.06, (1 - t) / 0.3), 0, 1) ** 0.7,
}
_LEAF_STYLES = ("solid", "outline", "engraved")
_HATCHES = ("half", "full", "veins", None)


def _bezier_mid(base, tip, bend, n=80):
    base = np.asarray(base, float); tip = np.asarray(tip, float)
    d = tip - base
    L = float(np.hypot(*d))
    nrm = np.array([d[1], -d[0]]) / max(L, 1e-9)
    ctrl = (base + tip) / 2 + nrm * bend * L
    t = np.linspace(0, 1, n)[:, None]
    return (1 - t) ** 2 * base + 2 * (1 - t) * t * ctrl + t ** 2 * tip


def leaf_shape(base, tip, width: float, shape: str = "lanceolate", bend: float = 0.12,
               asym: float = 0.0, n: int = 90):
    """(outline (N,2) closed, midrib (M,2), left_half, right_half) for a leaf
    from ``base`` to ``tip``. ``bend`` bows the midrib (fraction of length, +
    = toward the left normal); ``asym`` widens the left side (+) vs right."""
    base = np.asarray(base, float); tip = np.asarray(tip, float)
    if np.hypot(*(tip - base)) < 1e-9:
        raise ValueError("leaf: base and tip coincide")
    if not width > 0:
        raise ValueError(f"leaf: width must be > 0, got {width!r}")
    if isinstance(shape, str) and shape not in LEAF_SHAPES:
        raise ValueError(f"leaf shape must be one of {sorted(LEAF_SHAPES)} or a callable")
    mid = _bezier_mid(base, tip, bend, n)
    cv = G.Curve(mid)
    t = np.linspace(0, 1, n)
    P = cv.at(t)
    Nn = cv.normal(t)
    prof = LEAF_SHAPES[shape](np.clip(t, 0, 1)) if isinstance(shape, str) else shape(t)
    wl = 0.5 * width * prof * (1 + asym)
    wr = 0.5 * width * prof * (1 - asym)
    left = P + Nn * wl[:, None]
    right = P - Nn * wr[:, None]
    outline = np.vstack([left, right[::-1][1:-1]])
    lh = np.vstack([left, P[::-1][1:-1]])
    rh = np.vstack([right, P[::-1][1:-1]])
    return outline, P, lh, rh


def _valid(pg):
    pg = pg if pg.is_valid else shapely.make_valid(pg)
    if pg.geom_type == "GeometryCollection":
        pg = shapely.union_all([g for g in pg.geoms if g.geom_type in ("Polygon", "MultiPolygon")])
    return pg


def _signed_side(P, mid):
    """Signed distance of points P from the midrib polyline (+ = left of travel
    on screen), normalised later by the caller."""
    tree_pts = mid
    d = np.hypot(P[:, None, 0] - tree_pts[None, :, 0], P[:, None, 1] - tree_pts[None, :, 1])
    j = np.clip(np.argmin(d, axis=1), 0, len(mid) - 2)
    a, b = mid[j], mid[j + 1]
    cr = (b[:, 0] - a[:, 0]) * (P[:, 1] - a[:, 1]) - (b[:, 1] - a[:, 1]) * (P[:, 0] - a[:, 0])
    return -np.sign(cr) * d[np.arange(len(P)), j]


def _leaf_parts(base, tip, width, *, shape="lanceolate", bend=0.12, style="outline", lw=1.4,
                hatch="half", hatch_spacing=None, hatch_lines=6, hatch_angle=90.0, side=1,
                vein=True, asym=0.0, tone=None, tip_clear=0.14, hatch_lw_ratio=0.8,
                light=None, vein_w=None):
    """Geometry of one leaf: {'sil': Polygon, 'lines': [(pts, closed)] (STROKE
    centrelines of the line art), 'hatch': [pts], 'fill': [d] (solid FILL)}."""
    if style not in _LEAF_STYLES:
        raise ValueError(f"leaf style must be one of {_LEAF_STYLES}, not {style!r}")
    if hatch not in _HATCHES:
        raise ValueError(f"leaf hatch must be one of {_HATCHES}, not {hatch!r}")
    outline, mid, lh, rh = leaf_shape(base, tip, width, shape, bend, asym)
    base = np.asarray(base, float); tip = np.asarray(tip, float)
    axis = (tip - base) / np.hypot(*(tip - base))
    ax_ang = math.degrees(math.atan2(axis[1], axis[0]))
    sil = _valid(Polygon(outline))
    out = {"sil": sil, "lines": [], "hatch": [], "fill": [], "hatch_lw": None}
    cv = G.Curve(mid)
    Lleaf = cv.length
    if style == "solid":
        d = G.poly_d(outline, True, orient="cw")
        if vein:
            vw = vein_w if vein_w is not None else max(T.MIN_REVERSED, width * 0.07)
            if width >= 4.5 * vw:
                cut = stroke(cv.sub(0.04, 0.82).pts, vw, "taper-end", taper=0.7,
                             min_width=vw * 0.8)
                d = G.difference(d, cut)
        out["fill"].append(d)
        return out
    out["lines"].append((outline, True))
    if vein:
        out["lines"].append((cv.sub(0.0, 0.9).pts, False))
    lw_ = lw if lw is not None else T.MIN_LINE
    hl = max(T.MIN_LINE, lw_ * hatch_lw_ratio)
    out["hatch_lw"] = hl
    if style == "outline" and hatch in ("half", "full"):
        # hatch region: the chosen half, leaving the tip clear
        n = len(mid)
        k_end = max(3, int(n * (1 - tip_clear)))
        halves = []
        if hatch == "full" or side > 0:
            halves.append((np.vstack([lh[:k_end], mid[:k_end][::-1]]), +1))
        if hatch == "full" or side < 0:
            right = rh[:n]
            halves.append((np.vstack([right[:k_end], mid[:k_end][::-1]]), -1))
        usable = Lleaf * (1 - tip_clear - 0.04)
        ang_rel = hatch_angle
        if hatch_spacing is None:
            sp = usable * abs(math.sin(math.radians(ang_rel))) / max(1, hatch_lines)
        else:
            sp = hatch_spacing
        sp = max(sp, hl + T.MIN_GAP)
        for poly, sg in halves:
            reg = _valid(Polygon(poly))
            if reg.is_empty:
                continue
            ang = ax_ang + 90 if ang_rel == 90 else ax_ang - sg * ang_rel
            ls = _clip(_parallel_lines(reg, ang, sp, sp * 0.5), reg)
            out["hatch"] += [l for l in ls if np.hypot(*(l[-1] - l[0])) > max(sp * 0.5, 2 * hl)]
    elif style == "outline" and hatch == "veins":
        for tt in np.linspace(0.16, 0.66, 4):
            for sg in (1, -1):
                p = cv.at(tt)
                a0 = math.radians(float(cv.angle(tt)) - sg * 50)
                a1 = math.radians(float(cv.angle(tt)) - sg * 20)
                L = width * 0.42 * (1 - tt * 0.45)
                q1 = p + np.array([math.cos(a0), math.sin(a0)]) * L * 0.5
                q2 = q1 + np.array([math.cos(a1), math.sin(a1)]) * L * 0.55
                vv = G.spline(np.array([p, q1, q2]))
                out["hatch"].append(vv)
    if style == "engraved":
        # smooth tone: lit side pale, shaded side dark, darkening toward the
        # shaded edge; lines run across the midrib
        L_side = side if light is None else light
        halfw = 0.5 * width

        def tone_fn(x, y):
            P = np.column_stack([np.ravel(x), np.ravel(y)])
            sd = np.clip(_signed_side(P, mid) / halfw, -1, 1)
            v = 0.42 - 0.5 * L_side * sd + 0.12 * np.abs(sd)
            return np.clip(v, 0, 1).reshape(np.shape(x))
        tf = tone or tone_fn
        sp = hatch_spacing or max(width / 7.0, 2.4)
        ls = _clip(_parallel_lines(sil, ax_ang + 90 - 30 * side, sp, 0.0), sil)
        body = engrave(ls, tf, wmin=0.0, wmax=sp * 0.62, gap=0.9, clip=sil, fade=sp * 0.9,
                       edge_gap=lw_ * 0.5, taper_len=sp * 2.5)
        out["fill"].append(body)
    return out


def _render_leaf(parts, lw, occluder=None, gap=0.0):
    """-> (stroke_d, fill_d) for one leaf, hidden behind ``occluder``."""
    lines = parts["lines"]
    hatch = [(h, False) for h in parts["hatch"]]
    fills = list(parts["fill"])
    if occluder is not None and not occluder.is_empty:
        occ_l = occluder.buffer(gap + (lw or 0) / 2) if gap > 0 else occluder
        cut = lambda L: [(p, False) for p, _ in G.as_polys(G.clip_out(L, occ_l))] if L else []
        lines = cut(lines)
        hatch = cut(hatch)
        occ_f = G.from_shape(occluder.buffer(gap) if gap > 0 else occluder)
        fills = [G.difference(f, occ_f) for f in fills if f]
    if lw is None:
        return G.polys_d(lines + hatch), "".join(fills)
    d = G.outline(lines, lw) if lines else ""
    if hatch:
        d += G.outline(hatch, parts["hatch_lw"] or lw, cap="flat")
    return d, "".join(fills)


def leaf(base, tip, width: float, *, shape: str = "lanceolate", bend: float = 0.12,
         style: str = "outline", lw: float | None = 1.4, hatch: str | None = "half",
         hatch_spacing: float | None = None, hatch_lines: int = 6, hatch_angle: float = 90.0,
         side: int = 1, vein: bool = True, asym: float = 0.0, tone=None,
         tip_clear: float = 0.14, hatch_lw_ratio: float = 0.8, vein_w: float | None = None) -> str:
    """A leaf from ``base`` to ``tip``.

    style 'solid'    filled silhouette; ``vein`` knocks out a tapered midrib
                     when the leaf is big enough to hold a printable reversed line
          'outline'  monoline outline + midrib (Monarchs); ``hatch``:
                     'half' parallel hatch across one side (``side`` +1 left /
                     -1 right), 'full' both sides, 'veins' curved side veins,
                     None plain. Hatch is scaled to the leaf (``hatch_lines``
                     per half unless ``hatch_spacing``), at ``hatch_angle`` to
                     the midrib (90 = perpendicular), drawn at
                     ``hatch_lw_ratio``·lw with butt ends meeting the outline,
                     and the last ``tip_clear`` of the leaf stays unhatched
          'engraved' outline + tonal hatching from a smooth light model (lit
                     side pale, shaded side dark; ``tone`` overrides)
    -> FILL d (or STROKE centrelines if lw=None, 'outline' style only)."""
    p = _leaf_parts(base, tip, width, shape=shape, bend=bend, style=style, lw=lw, hatch=hatch,
                    hatch_spacing=hatch_spacing, hatch_lines=hatch_lines, hatch_angle=hatch_angle,
                    side=side, vein=vein, asym=asym, tone=tone, tip_clear=tip_clear,
                    hatch_lw_ratio=hatch_lw_ratio, vein_w=vein_w)
    if lw is None and style == "engraved":
        raise ValueError("leaf(style='engraved') is FILL-only: pass lw=<px>")
    st, fl = _render_leaf(p, lw)
    return st + fl


def sprig(stem, *, count: int = 7, leaf_len: float = 26.0, leaf_w: float = 10.0,
          arrangement: str = "alternate", angle: float = 38.0, start: float = 0.12,
          end: float = 0.92, taper: float = 0.45, terminal: bool = True,
          stem_width: float = 2.0, stem_profile="taper-end", shape: str = "lanceolate",
          bend: float = 0.14, style: str = "solid", lw: float | None = 1.2,
          hatch: str | None = None, berries: int = 0, berry_r: float = 2.2,
          leaf_kw: dict | None = None, jitter: float = 0.0, seed: int = 1,
          gap: float | None = None, parts: bool = False):
    """Leaves along a stem path (d or points). ``arrangement`` 'alternate' |
    'opposite'; leaves lean forward at ``angle``° and shrink by ``taper``
    toward the tip; optional terminal leaf and ``berries``.

    Leaves are drawn in paint order (toward the tip on top) with occlusion:
    each leaf hides what lies behind it (the stem stops at leaf outlines);
    ``gap`` (default: 0 for outline style, the print gap for solid leaves)
    adds a paper margin round the covering leaf. ``jitter`` 0..1 varies angle
    (±8°), size (±10%), bend and asymmetry per leaf (deterministic ``seed``).
    -> FILL d; with ``lw=None`` (outline style) -> STROKE d, and ``parts=True``
    -> {'stroke': d, 'fill': d} (berries and solid parts are FILL)."""
    if arrangement not in ("alternate", "opposite"):
        raise ValueError(f"arrangement must be 'alternate' or 'opposite', not {arrangement!r}")
    if count < 1:
        raise ValueError("sprig: count must be >= 1")
    if style not in _LEAF_STYLES:
        raise ValueError(f"style must be one of {_LEAF_STYLES}")
    if lw is None and style != "outline":
        raise ValueError(f"sprig(style={style!r}) is FILL: lw=None (STROKE) needs style='outline'")
    rng = np.random.default_rng(seed)
    cv = G.curve(stem)
    kw = dict(shape=shape, bend=bend, style=style, lw=lw, hatch=hatch)
    kw.update(leaf_kw or {})
    gp = (T.MIN_GAP if style == "solid" else 0.0) if gap is None else gap
    leaves = []
    ts = np.linspace(start, end, count)
    for k, t in enumerate(ts):
        p = cv.at(t)
        hd = float(cv.angle(t))
        L = leaf_len * (1 - taper * t)
        W = leaf_w * (1 - taper * t)
        sides = (1, -1) if arrangement == "opposite" else ((1,) if k % 2 == 0 else (-1,))
        for sg in sides:
            j = rng.uniform(-1, 1, 4) * jitter
            a = math.radians(hd - sg * (angle + 8 * j[0]))
            Lk = L * (1 + 0.1 * j[1])
            tip = p + np.array([math.cos(a), math.sin(a)]) * Lk
            kk = {**kw, "bend": -sg * abs(kw["bend"]) * (1 + 0.35 * j[2]), "asym": 0.12 * j[3],
                  "side": -sg}
            leaves.append(_leaf_parts(p, tip, W * (1 + 0.1 * j[1]), **kk))
    if terminal:
        p = cv.at(1.0)
        hd = math.radians(float(cv.angle(1.0)))
        L = leaf_len * (1 - taper) * 1.05
        W = leaf_w * (1 - taper)
        tip = p + np.array([math.cos(hd), math.sin(hd)]) * L
        leaves.append(_leaf_parts(p, tip, W, **{**kw, "bend": 0.04}))
    # stem (bottom layer), hidden inside every leaf
    stem_pts = cv.pts
    sils = [lf["sil"] for lf in leaves]
    all_sil = shapely.union_all(sils) if sils else shapely.Polygon()
    if lw is None:
        stem_st = G.clip_out(stem_pts, all_sil)
        stem_fill = ""
    else:
        stem_st = ""
        stem_fill = G.difference(stroke(stem_pts, stem_width, stem_profile, taper=0.35,
                                        min_width=T.MIN_LINE),
                                 G.from_shape(all_sil.buffer(-(lw or 0) * 0.5)))
    strokes, fills = [stem_st], [stem_fill]
    for k, lf in enumerate(leaves):
        above = sils[k + 1:]
        occ = shapely.union_all(above) if above else None
        st, fl = _render_leaf(lf, lw, occ, gp)
        strokes.append(st)
        fills.append(fl)
    if berries:
        for k, t in enumerate(np.linspace(start + 0.05, end - 0.05, berries)):
            p = cv.at(t)
            n = cv.normal(t)
            sg = 1 if k % 2 else -1
            q = p + n * sg * (leaf_w * 0.35 + berry_r)
            fills.append(G.circle_d(q[0], q[1], berry_r))
    st, fl = "".join(strokes), "".join(fills)
    if parts:
        return {"stroke": st, "fill": fl}
    if lw is None and fl:
        raise ValueError("sprig(lw=None) has FILL parts (berries/solid leaves): pass parts=True")
    return st + fl


def laurel(stem, *, count: int = 9, leaf_len: float = 24.0, leaf_w: float = 8.5,
           angle: float = 30.0, berries: int = 0, **kw):
    """Laurel branch: opposite, slender, forward-leaning leaves (see
    :func:`sprig` for occlusion, jitter and styles). -> FILL d."""
    return sprig(stem, count=count, leaf_len=leaf_len, leaf_w=leaf_w, arrangement="opposite",
                 angle=angle, shape="laurel", taper=kw.pop("taper", 0.35), berries=berries, **kw)


def wreath(cx: float, cy: float, r: float, *, gap_deg: float = 60.0, open_at: str = "top",
           count: int = 10, leaf_len: float | None = None, leaf_w: float | None = None,
           stem_width: float = 1.8, tie: bool = True, **kw):
    """Laurel wreath: two mirrored branches on a circle, open at the top (or
    'bottom'), crossing at the other end. Keywords go to :func:`laurel`
    (``style``, ``lw``, ``jitter``, ``seed`` ...). -> FILL d."""
    if open_at not in ("top", "bottom"):
        raise ValueError(f"open_at must be 'top' or 'bottom', not {open_at!r}")
    if not r > 0:
        raise ValueError("wreath: r must be > 0")
    ll = leaf_len or r * 0.36
    lwid = leaf_w or ll * 0.36
    a = np.linspace(90 + 8, 270 - gap_deg / 2, 200)
    left = np.column_stack([cx + r * np.cos(np.radians(a)), cy + r * np.sin(np.radians(a))])
    want_parts = kw.pop("parts", False)
    br = laurel(left, count=count, leaf_len=ll, leaf_w=lwid, stem_width=stem_width, parts=True, **kw)
    kw2 = dict(kw)
    kw2["seed"] = kw.get("seed", 1) + 101
    br2 = laurel(left, count=count, leaf_len=ll, leaf_w=lwid, stem_width=stem_width, parts=True, **kw2)
    st = br["stroke"] + G.mirror_x(br2["stroke"], cx) if br2["stroke"] else br["stroke"]
    fl = br["fill"] + (G.mirror_x(br2["fill"], cx) if br2["fill"] else "")
    if open_at == "bottom":
        st = G.rotate180(st, cx, cy) if st else st
        fl = G.rotate180(fl, cx, cy) if fl else fl
    if tie:
        y = cy + r if open_at == "top" else cy - r
        fl += G.circle_d(cx, y, stem_width * 1.8)
    if want_parts:
        return {"stroke": st, "fill": fl}
    if kw.get("lw", 1.2) is None and fl:
        raise ValueError("wreath(lw=None) has FILL parts (tie/berries): pass parts=True")
    return st + fl


def grass(base, *, count: int = 9, height: float = 80.0, spread: float = 60.0,
          lean: float = 0.0, curl: float = 0.35, width: float = 3.2, seed: int = 3,
          jitter: float = 0.2, min_width: float | None = None) -> str:
    """Fan of tapered grass blades from ``base``; blades toward the outside of
    the fan are shorter and curve outward. Deterministic for ``seed``. -> FILL."""
    if count < 1:
        raise ValueError("grass: count must be >= 1")
    mw = T.MIN_LINE if min_width is None else min_width
    rng = np.random.default_rng(seed)
    bx, by = base
    out = []
    for k in range(count):
        u = (k / (count - 1) - 0.5) * 2 if count > 1 else 0.0
        a0 = -90 + lean + u * spread / 2 + rng.uniform(-4, 4) * jitter * 5
        L = height * (1 - 0.35 * abs(u)) * (1 + rng.uniform(-jitter, jitter))
        k_end = curl * (u if abs(u) > 0.05 else rng.choice([-0.4, 0.4])) * 2.2 / L * math.pi
        s = np.linspace(0, L, 120)
        kap = k_end * (s / L) ** 1.6
        th = math.radians(a0) + np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(s))])
        x = bx + np.concatenate([[0], np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) / 2 * np.diff(s))])
        y = by + np.concatenate([[0], np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) / 2 * np.diff(s))])
        out.append(stroke(np.column_stack([x, y]), width * (1 - 0.3 * abs(u)),
                          lambda t: (1 - np.clip(t, 0, 1)) ** 0.9 * (0.35 + 0.65 * np.clip(t / 0.08, 0, 1)),
                          cap="round", min_width=mw))
    return "".join(out)


def rice(stem, *, grains: int = 14, grain_len: float = 12.0, grain_w: float = 3.2,
         awn: float = 14.0, start: float = 0.35, angle: float = 18.0, pedicel: float = 3.0,
         stem_width: float = 1.8, lw: float | None = None, leaves: int = 0,
         leaf_len: float | None = None, leaf_w: float | None = None, current: float = 0.0,
         seed: int = 2, min_width: float | None = None) -> str:
    """Texas wild-rice (Zizania texana, found only in the San Marcos River):
    a nodding panicle of slender spikelets on short pedicels along the upper
    stem, each with a fine awn continuing from the grain tip, plus optional
    long ribbon ``leaves`` rising from the base and streaming with the
    ``current`` (degrees of downstream lean; the leaves wave like the real
    plant's submerged blades). All lines are at least the print minimum.
    -> FILL d."""
    if not 0 <= start < 1:
        raise ValueError("rice: start must be in [0, 1)")
    if grains < 1:
        raise ValueError("rice: grains must be >= 1")
    mw = T.MIN_LINE if min_width is None else min_width
    lw_ = max(mw, lw if lw is not None else mw)
    cv = G.curve(stem)
    parts = [stroke(cv.pts, stem_width, "taper-end", taper=0.25, min_width=mw)]
    ts = np.linspace(start, 0.97, grains)
    span = max(1e-6, 1 - start)
    for k, t in enumerate(ts):
        p = cv.at(t)
        hd = float(cv.angle(t))
        sg = 1 if k % 2 == 0 else -1
        a = math.radians(hd - sg * angle)
        u = np.array([math.cos(a), math.sin(a)])
        sc = 1 - 0.35 * (t - start) / span
        q0 = p + u * pedicel * sc
        q1 = q0 + u * grain_len * sc
        parts.append(G.outline([(np.array([p, q0 + u * 0.8]), False)], lw_))
        parts.append(leaf(q0, q1, max(grain_w * sc, 2.2 * mw), shape="grain", bend=0.0,
                          style="solid", vein=False))
        if awn:
            aw = q1 + u * awn * sc
            parts.append(stroke(np.array([q1 - u * 1.0, aw]), lw_ * 1.2, "taper-end", taper=0.9,
                                min_width=mw))
    if leaves:
        rng = np.random.default_rng(seed)
        b = cv.pts[0]
        L0 = leaf_len or cv.length * 1.1
        W0 = leaf_w or max(3.5, L0 * 0.022)
        base_hd = float(cv.angle(0.0))
        for k in range(leaves):
            u = (k / max(1, leaves - 1) - 0.5) * 2 if leaves > 1 else 0.0
            hd0 = base_hd + current + u * 28 + rng.uniform(-5, 5)
            L = L0 * (1 - 0.25 * abs(u)) * rng.uniform(0.85, 1.05)
            s = np.linspace(0, L, 160)
            # streaming blade: bends downstream and waves gently
            kap = (math.radians(current) * 0.9 / L) * (s / L) + 0.006 * np.sin(2 * math.pi * s / (L * 0.45) + k)
            th = math.radians(hd0) + np.concatenate([[0], np.cumsum((kap[1:] + kap[:-1]) / 2 * np.diff(s))])
            x = b[0] + np.concatenate([[0], np.cumsum((np.cos(th[1:]) + np.cos(th[:-1])) / 2 * np.diff(s))])
            y = b[1] + np.concatenate([[0], np.cumsum((np.sin(th[1:]) + np.sin(th[:-1])) / 2 * np.diff(s))])
            mid = np.column_stack([x, y])
            cvl = G.Curve(mid)
            tt = np.linspace(0, 1, 160)
            P = cvl.at(tt)
            Nn = cvl.normal(tt)
            prof = LEAF_SHAPES["strap"](tt)
            wv = 0.5 * W0 * prof
            poly = np.vstack([P + Nn * wv[:, None], (P - Nn * wv[:, None])[::-1]])
            d = G.resolve(G.poly_d(poly, True))
            if lw is not None:
                d = G.union(G.outline(d, lw_), G.outline(cvl.sub(0.03, 0.8).pts, lw_))
            parts.append(d)
    return "".join(parts)


def flower(cx: float, cy: float, r: float, *, petals: int = 5, shape: str = "round",
           center: float = 0.24, style: str = "solid", lw: float | None = 1.2, rot: float = -90.0,
           stamens: bool = True) -> str:
    """Simple radial flower. shape 'round' | 'pointed' | 'heart' (notched tip);
    style 'solid' (petals filled, centre knocked out with a ring; FILL-only)
    or 'outline' (STROKE with lw=None). -> FILL d."""
    if shape not in ("round", "pointed", "heart"):
        raise ValueError(f"flower shape must be round|pointed|heart, not {shape!r}")
    if style not in ("solid", "outline"):
        raise ValueError(f"flower style must be 'solid' or 'outline', not {style!r}")
    if petals < 2 or not r > 0:
        raise ValueError("flower: petals >= 2 and r > 0 required")
    petal_lines = []
    solids = []
    for k in range(petals):
        a = math.radians(rot + 360.0 * k / petals)
        u = np.array([math.cos(a), math.sin(a)])
        nn = np.array([-u[1], u[0]])
        t = np.linspace(0, 1, 80)
        if shape == "pointed":
            wprof = np.sin(np.pi * t ** 0.75) ** 0.8 * 0.36
        elif shape == "heart":
            wprof = np.sin(np.pi * t ** 0.55) ** 0.55 * 0.42
        else:
            wprof = np.sin(np.pi * t ** 0.6) ** 0.55 * 0.40
        rr = r * (center * 0.8 + (1 - center * 0.8) * t)
        c = np.array([cx, cy]) + np.outer(rr, u)
        left = c + np.outer(wprof * r, nn)
        right = c - np.outer(wprof * r, nn)
        poly = np.vstack([left, right[::-1]])
        if shape == "heart":
            tipn = np.array([cx, cy]) + u * r * 0.86
            notch = Polygon([tipn, tipn + u * r * 0.3 + nn * r * 0.12, tipn + u * r * 0.3 - nn * r * 0.12])
            pg = _valid(Polygon(poly)).difference(notch)
            if pg.geom_type != "Polygon":
                pg = max(getattr(pg, "geoms", [pg]), key=lambda g: g.area)
            poly = np.asarray(pg.exterior.coords)[:-1]
        if style == "solid":
            solids.append(G.poly_d(poly, True, orient="cw"))
        else:
            petal_lines.append((poly, True))
    if style == "solid":
        body = G.union(*solids)
        hole = G.circle_d(cx, cy, r * center * 1.05)
        body = G.difference(body, hole)
        out = body + G.circle_d(cx, cy, r * center * 0.62)
        if stamens:
            for k in range(petals):
                a = math.radians(rot + 360.0 * (k + 0.5) / petals)
                q = np.array([cx, cy]) + np.array([math.cos(a), math.sin(a)]) * r * center * 0.85
                out += G.circle_d(q[0], q[1], max(r * 0.035 + 0.3, T.MIN_LINE / 2))
        return out
    petal_lines.append((G.arc_pts(cx, cy, r * center, 0, 360)[:-1], True))
    if lw is None:
        return G.polys_d(petal_lines)
    return G.outline(petal_lines, lw)


def _ell(c, rx, ry, rot, n=48):
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    P = np.column_stack([rx * np.cos(a), ry * np.sin(a)])
    r = math.radians(rot)
    R = np.array([[math.cos(r), -math.sin(r)], [math.sin(r), math.cos(r)]])
    return P @ R.T + np.asarray(c, float)


def bluebonnet(base, height: float = 110.0, *, whorls: int = 10, width: float = 30.0,
               stem_width: float = 2.4, tip_whorls: int = 3, spots: bool = True,
               parts: bool = False, lean: float = 0.0, style: str = "solid",
               lw: float | None = 1.2, hatch: bool = True):
    """Texas bluebonnet (Lupinus texensis) raceme, stylised: stacked pairs of
    up-tilted banner petals (each with the white banner 'eye' spot) over a
    small keel, shrinking to a pale pointed tip.

    style 'solid'    flat silhouettes, the eye spots knocked out
          'outline'  line art: each banner and keel outlined at ``lw`` with the
                     upper florets occluding the lower ones, one half of every
                     banner half-hatched (``hatch``), eye spots as small rings
          'engraved' outline + tonal hatching (shaded toward the stem)
    -> FILL d, or with ``parts=True`` a dict {'stem', 'flowers', 'tip'} so the
    florets can print blue and the tip white/cream."""
    if style not in ("solid", "outline", "engraved"):
        raise ValueError(f"bluebonnet style must be solid|outline|engraved, not {style!r}")
    if whorls < 1:
        raise ValueError("bluebonnet: whorls must be >= 1")
    if not height > 0:
        raise ValueError("bluebonnet: height must be > 0")
    bx, by = base
    top = np.array([bx + math.sin(math.radians(lean)) * height, by - height])
    stem_pts = G.spline(np.array([[bx, by], [bx + (top[0] - bx) * 0.4, by - height * 0.5], top]))
    cv = G.Curve(stem_pts)
    stem_d = stroke(cv.sub(0, 0.9).pts, stem_width, "taper-end", taper=0.2, min_width=T.MIN_LINE)
    t0 = 0.30
    florets = []   # (polygon, is_tip, spot centre, spot r, axis angle)
    for k in range(whorls):
        t = t0 + (0.93 - t0) * (k / (whorls - 1) if whorls > 1 else 0.5)
        p = cv.at(t)
        up = cv.tangent(t)
        sc = 1 - 0.58 * (t - t0) / (0.93 - t0)
        s = width * 0.5 * sc
        is_tip = k >= whorls - tip_whorls
        ang = math.degrees(math.atan2(up[1], up[0])) + 90
        kc = p + G.rotate(np.array([[0, s * 0.22]]), ang)[0]
        florets.append((_ell(kc, s * 0.3, s * 0.34, ang), is_tip, None, 0.0, ang, "keel"))
        for sg in (-1, 1):
            c = p + G.rotate(np.array([[sg * s * 0.58, -s * 0.12]]), ang)[0]
            cc = p + G.rotate(np.array([[sg * s * 0.52, -s * 0.30]]), ang)[0]
            florets.append((_ell(c, s * 0.62, s * 0.44, ang + sg * 30), is_tip, cc, s * 0.13,
                            ang + sg * 30, "banner"))
    q0 = cv.at(0.93)
    bud = stroke(np.array([q0, cv.at(1.0) + cv.tangent(1.0) * width * 0.12]), width * 0.34,
                 lambda t: np.sin(np.pi * np.clip(t, 0, 1) ** 0.55) ** 0.8)
    if style == "solid":
        flowers = [G.poly_d(f[0], True, orient="cw") for f in florets if not f[1]]
        tip = [G.poly_d(f[0], True, orient="cw") for f in florets if f[1]] + [bud]
        holes = [G.circle_d(f[2][0], f[2][1], f[3]) for f in florets
                 if spots and not f[1] and f[2] is not None]
        fl = G.union(*flowers) if flowers else ""
        if holes and fl:
            fl = G.difference(fl, *holes)
        tp = G.union(*tip) if tip else ""
        if parts:
            return {"stem": stem_d, "flowers": fl, "tip": tp}
        return stem_d + fl + tp
    # --- line art: paint lower florets first, upper ones occlude them --------------
    lw_ = lw if lw is not None else T.MIN_LINE
    sils = [_valid(Polygon(f[0])) for f in florets]
    bud_pg = G.to_shape(bud)
    out_f, out_t = [], []
    for k, (pts, is_tip, spot, sr, ang, kind) in enumerate(florets):
        above = sils[k + 1:] + [bud_pg]
        occ = shapely.union_all(above)
        lines = [(pts, True)]
        hatch_lines = []
        reg = sils[k]
        if kind == "banner" and not is_tip:
            if spots and spot is not None:
                lines.append((G.arc_pts(spot[0], spot[1], max(sr, 1.4 * lw_), 0, 360)[:-1], True))
            if hatch and style == "outline":
                axis = G.rotate(np.array([[0.0, -1.0], [0.0, 1.0]]) * 40, ang)
                ctr = np.mean(pts, axis=0)
                half_reg = reg.intersection(shapely.Polygon(np.vstack([ctr + axis[0], ctr + axis[1],
                                                                        ctr + axis[1] + G.rotate(np.array([[40.0, 0]]), ang)[0],
                                                                        ctr + axis[0] + G.rotate(np.array([[40.0, 0]]), ang)[0]])))
                if spots and spot is not None:
                    half_reg = half_reg.difference(shapely.Point(spot).buffer(max(sr, 1.4 * lw_) + lw_))
                sp = max(lw_ + T.MIN_GAP, 0.16 * math.sqrt(reg.area))
                hatch_lines = _clip(_parallel_lines(half_reg, ang + 45, sp), half_reg) if not half_reg.is_empty else []
        vis = G.clip_out(lines, occ)
        segs = [(p_, False) for p_, _ in G.as_polys(vis)]
        hl = [(h, False) for h in hatch_lines]
        if hl:
            hl = [(p_, False) for p_, _ in G.as_polys(G.clip_out(hl, occ))]
        if style == "engraved" and not is_tip:
            tone = lambda x, y: np.full(np.shape(x), 0.55)
            ls = _clip(_parallel_lines(reg, ang + 60, max(2.4, 0.12 * math.sqrt(reg.area))), reg)
            body = engrave(ls, tone, wmax=1.6, gap=0.9, clip=reg.difference(occ), fade=2.0)
        else:
            body = ""
        if lw is None:
            d = G.polys_d(segs + hl)
        else:
            d = (G.outline(segs, lw_) if segs else "") + (G.outline(hl, max(T.MIN_LINE, lw_ * 0.8), cap="flat") if hl else "")
        (out_t if is_tip else out_f).append(d + body)
    tip_d = "".join(out_t) + (G.outline(bud, lw_) if lw is not None else G.polys_d(G.as_polys(bud)))
    if parts:
        return {"stem": stem_d, "flowers": "".join(out_f), "tip": tip_d}
    return stem_d + "".join(out_f) + tip_d


def palmate_leaf(base, angle: float = -90.0, size: float = 40.0, *, leaflets: int = 5,
                 spread: float = 150.0, petiole: float = 0.5, style: str = "solid",
                 lw: float | None = 1.0, width_ratio: float = 0.3) -> str:
    """Palmate (lupine) leaf: ``leaflets`` lanceolate leaflets fanned over
    ``spread``° at the end of a petiole. style 'solid' | 'outline' (half-
    hatched) | 'engraved'. -> FILL d."""
    if leaflets < 1:
        raise ValueError("palmate_leaf: leaflets must be >= 1")
    if lw is None:
        raise ValueError("palmate_leaf is FILL (tapered petiole): pass lw=<px>")
    b = np.asarray(base, float)
    a = math.radians(angle)
    hub = b + np.array([math.cos(a), math.sin(a)]) * size * petiole
    parts = [stroke(np.array([b, hub]), max(1.0, size * 0.05), "taper-end", taper=0.3,
                    min_width=T.MIN_LINE)]
    for k in range(leaflets):
        u = (k / (leaflets - 1) - 0.5) if leaflets > 1 else 0.0
        ak = math.radians(angle + u * spread)
        L = size * (1 - 0.3 * abs(u) * 2 * 0.5)
        tip = hub + np.array([math.cos(ak), math.sin(ak)]) * L
        parts.append(leaf(hub, tip, L * width_ratio, shape="lanceolate", bend=0.05 * np.sign(u),
                          style=style, lw=lw, hatch="half" if style == "outline" else None, vein=True))
    return "".join(parts)


def ripples(cx: float, cy: float, r0: float = 12.0, *, count: int = 5, spacing: float = 10.0,
            growth: float = 1.18, ry_ratio: float = 0.3, width: float = 2.4,
            breaks: int = 2, break_deg: float = 26.0, rot: float = 0.0, seed: int = 5,
            fade: float = 0.55, min_width: float | None = None) -> str:
    """Concentric water ripples in perspective (ellipses ``ry_ratio`` tall),
    each broken into ``breaks`` arcs with tapered ends (``breaks=0`` draws
    whole rings); rings thin out and the gaps drift for a natural look.
    -> FILL d."""
    if count < 1:
        raise ValueError("ripples: count must be >= 1")
    if breaks < 0:
        raise ValueError("ripples: breaks must be >= 0")
    mw = T.MIN_LINE if min_width is None else min_width
    rng = np.random.default_rng(seed)
    out = []
    r = r0
    step = spacing
    for i in range(count):
        wi = max(mw, width * (1 - fade * i / max(1, count - 1)))
        if breaks == 0:
            a = np.radians(np.linspace(0, 360, max(80, int(2 * math.pi * r)), endpoint=False))
            P = np.column_stack([r * np.cos(a), r * ry_ratio * np.sin(a)])
            if rot:
                P = G.rotate(P, rot)
            out.append(G.outline([(P + np.array([cx, cy]), True)], wi))
        else:
            offs = 90.0 / breaks + rng.uniform(-18, 18)
            seg = 360.0 / breaks
            for b in range(breaks):
                a0 = offs + b * seg + break_deg / 2
                a1 = offs + (b + 1) * seg - break_deg / 2
                a = np.radians(np.linspace(a0, a1, max(40, int((a1 - a0) * r / 40))))
                P = np.column_stack([r * np.cos(a), r * ry_ratio * np.sin(a)])
                if rot:
                    P = G.rotate(P, rot)
                P = P + np.array([cx, cy])
                out.append(stroke(P, wi, "taper-both", taper=0.22, min_width=mw))
        r += step
        step *= growth
    return "".join(out)
