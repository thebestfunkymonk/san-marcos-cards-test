"""Text -> outlined SVG paths (no <text> in final art).

    from inkkit.typeset import text_to_path
    d, bbox, adv = text_to_path("Cinzel", "SAN MARCOS", 40, 375, 100, anchor="middle",
                                variations={"wght": 700}, tracking=120)

* ``font`` is a path or a short name resolved in ``<project>/fonts`` (prefix match,
  e.g. "Cinzel", "PlayfairDisplaySC-Bold", "EBGaramond").
* Variable fonts are instanced with fontTools' instancer (cached per location).
* Kerning: GPOS 'kern' pair adjustments (format 1 & 2, extension lookups) or a
  legacy 'kern' table.  ``tracking`` is in 1/1000 em (like InDesign).
"""
from __future__ import annotations

import unicodedata
import warnings
import math
import os
from functools import lru_cache

import numpy as np
from fontTools.pens.basePen import BasePen
from fontTools.ttLib import TTFont

from . import FONTS
from . import geom as G

__all__ = ["resolve_font", "load_font", "text_to_path", "text_on_path", "text_on_arc",
           "font_metrics", "measure"]


def resolve_font(name: str) -> str:
    """Font path from a file path or a short name in ``<project>/fonts``.
    Matching is case-insensitive and literal (``[wght]`` is not a glob
    pattern); on a prefix tie the exact stem wins, then the variable font,
    then a '-Regular' file, then the shortest name."""
    if os.path.isfile(name):
        return name
    cand = os.path.join(FONTS, name)
    if os.path.isfile(cand):
        return cand
    files = sorted(f for f in os.listdir(FONTS) if f.lower().endswith((".ttf", ".otf")))
    low = name.lower()
    exact = [f for f in files if f.lower() == low or os.path.splitext(f)[0].lower() == low]
    if exact:
        return os.path.join(FONTS, exact[0])
    hits = [f for f in files if f.lower().startswith(low)]
    if not hits:
        raise FileNotFoundError(f"font {name!r} not found in {FONTS}")

    def rank(f):
        stem = os.path.splitext(f)[0]
        base = stem.split("[")[0].split("-")[0].lower()
        return (base != low, "[" not in stem, "-regular" not in stem.lower(), len(stem), f)
    return os.path.join(FONTS, sorted(hits, key=rank)[0])


@lru_cache(maxsize=32)
def _load(path: str, var_items: tuple) -> TTFont:
    font = TTFont(path)
    if "fvar" in font:
        from fontTools.varLib import instancer
        axes = {a.axisTag: a.defaultValue for a in font["fvar"].axes}
        loc = dict(axes)
        for k, v in var_items:
            if k in axes:
                a = next(a for a in font["fvar"].axes if a.axisTag == k)
                loc[k] = max(a.minValue, min(a.maxValue, v))
        font = instancer.instantiateVariableFont(font, loc, inplace=False)
    return font


def load_font(font: str, variations: dict | None = None) -> TTFont:
    """Load (and instance) a font; cached."""
    return _load(resolve_font(font), tuple(sorted((variations or {}).items())))


class _CmdPen(BasePen):
    def __init__(self, glyphSet=None):
        super().__init__(glyphSet)  # glyphSet lets BasePen decompose composite glyphs
        self.cmds = []

    def _moveTo(self, p):
        self.cmds.append(("M", *p))

    def _lineTo(self, p):
        self.cmds.append(("L", *p))

    def _curveToOne(self, p1, p2, p3):
        self.cmds.append(("C", *p1, *p2, *p3))

    def _qCurveToOne(self, p1, p2):
        self.cmds.append(("Q", *p1, *p2))

    def _closePath(self):
        self.cmds.append(("Z",))

    def _endPath(self):
        pass


@lru_cache(maxsize=8192)
def _glyph_cmds(fid: int, gname: str) -> tuple:
    font = _FONT_BY_ID[fid]
    gs = font.getGlyphSet()
    pen = _CmdPen(gs)
    gs[gname].draw(pen)
    return tuple(pen.cmds)


_FONT_BY_ID: dict[int, TTFont] = {}


def _kerner(font: TTFont):
    cache = getattr(font, "_inkkit_kern", None)
    if cache is not None:
        return cache
    subtables = []
    if "GPOS" in font and font["GPOS"].table.FeatureList:
        gpos = font["GPOS"].table
        lookup_ids = set()
        for fr in gpos.FeatureList.FeatureRecord:
            if fr.FeatureTag == "kern":
                lookup_ids.update(fr.Feature.LookupListIndex)
        for li in sorted(lookup_ids):
            lk = gpos.LookupList.Lookup[li]
            for st in lk.SubTable:
                if lk.LookupType == 9:
                    st = st.ExtSubTable
                if getattr(st, "LookupType", 2) != 2 and lk.LookupType not in (2, 9):
                    continue
                if not hasattr(st, "Format") or not hasattr(st, "Coverage"):
                    continue
                cov = {g: i for i, g in enumerate(st.Coverage.glyphs)}
                if st.Format == 1:
                    sets = []
                    for ps in st.PairSet:
                        sets.append({r.SecondGlyph: (r.Value1.XAdvance if r.Value1 and hasattr(r.Value1, "XAdvance") else 0)
                                     for r in ps.PairValueRecord})
                    subtables.append(("f1", cov, sets))
                elif st.Format == 2:
                    c1 = st.ClassDef1.classDefs if st.ClassDef1 else {}
                    c2 = st.ClassDef2.classDefs if st.ClassDef2 else {}
                    subtables.append(("f2", cov, (c1, c2, st.Class1Record)))
    legacy = None
    if not subtables and "kern" in font:
        try:
            legacy = font["kern"].kernTables[0].kernTable
        except Exception:
            legacy = None

    def kern(a: str, b: str) -> float:
        total = 0.0
        for kind, cov, data in subtables:
            i = cov.get(a)
            if i is None:
                continue
            if kind == "f1":
                v = data[i].get(b)
                if v is not None:
                    return float(v or 0)
            else:
                c1, c2, recs = data
                k1, k2 = c1.get(a, 0), c2.get(b, 0)
                try:
                    v1 = recs[k1].Class2Record[k2].Value1
                except (IndexError, AttributeError):
                    continue
                v = getattr(v1, "XAdvance", 0) if v1 is not None else 0
                if v:
                    return float(v)
        if legacy:
            return float(legacy.get((a, b), 0))
        return total

    font._inkkit_kern = kern
    return kern


def font_metrics(font: str, variations: dict | None = None) -> dict:
    """unitsPerEm, ascender, descender, capHeight, xHeight (font units)."""
    f = load_font(font, variations)
    upm = f["head"].unitsPerEm
    os2 = f["OS/2"] if "OS/2" in f else None
    cap = getattr(os2, "sCapHeight", 0) if os2 else 0
    xh = getattr(os2, "sxHeight", 0) if os2 else 0
    if not cap:
        cap = int(upm * 0.7)
    if not xh:
        xh = int(upm * 0.5)
    hhea = f["hhea"]
    return {"upm": upm, "ascender": hhea.ascent, "descender": hhea.descent, "capHeight": cap,
            "xHeight": xh}


def _layout(font, text, size, variations, tracking, kerning, missing="warn"):
    if missing not in ("warn", "raise", "ignore"):
        raise ValueError("missing must be 'warn', 'raise' or 'ignore'")
    if not size > 0:
        raise ValueError(f"font size must be > 0, got {size!r}")
    f = load_font(font, variations)
    fid = id(f)
    _FONT_BY_ID[fid] = f
    upm = f["head"].unitsPerEm
    sc = size / upm
    cmap = f.getBestCmap()
    hmtx = f["hmtx"]
    kern = _kerner(f) if kerning else None
    glyphs = []
    x = 0.0
    prev = None
    absent, ctrl = [], []
    for ch in text:
        if unicodedata.category(ch) in ("Cc", "Cf") and ch not in ("\u200d",):
            ctrl.append(ch)
            continue
        gname = cmap.get(ord(ch))
        if gname is None:
            absent.append(ch)
            if missing == "raise":
                raise ValueError(f"{os.path.basename(resolve_font(font))} has no glyph for {ch!r}")
            gname = ".notdef"
        if prev is not None and kern is not None:
            x += kern(prev, gname) * sc
        adv = hmtx[gname][0] * sc
        glyphs.append((gname, x, adv))
        x += adv + tracking / 1000.0 * size
        prev = gname
    total = x - (tracking / 1000.0 * size if glyphs else 0)
    if missing == "warn" and (absent or ctrl):
        msg = []
        if absent:
            msg.append(f"no glyph for {''.join(sorted(set(absent)))!r} (drawn as .notdef)")
        if ctrl:
            msg.append(f"skipped control characters {sorted(set(ctrl))!r} (text is single-line)")
        warnings.warn(f"text_to_path({os.path.basename(resolve_font(font))}): " + "; ".join(msg),
                      stacklevel=3)
    return f, fid, sc, glyphs, total


def measure(font: str, text: str, size: float, variations: dict | None = None,
            tracking: float = 0.0, kerning: bool = True) -> float:
    """Advance width in px."""
    return _layout(font, text, size, variations, tracking, kerning, "ignore")[4]


def _baseline_shift(font, size, variations, baseline):
    if baseline in ("alphabetic", "baseline", None):
        return 0.0
    m = font_metrics(font, variations)
    s = size / m["upm"]
    if baseline in ("middle", "central", "cap-middle"):
        return m["capHeight"] * s / 2
    if baseline == "x-middle":
        return m["xHeight"] * s / 2
    if baseline in ("hanging", "top", "cap"):
        return m["capHeight"] * s
    if baseline in ("bottom", "descender"):
        return m["descender"] * s
    raise ValueError(baseline)


def text_to_path(font: str, text: str, size: float, x: float = 0.0, y: float = 0.0,
                 anchor: str = "start", baseline: str = "alphabetic",
                 variations: dict | None = None, tracking: float = 0.0,
                 kerning: bool = True, missing: str = "warn") -> tuple[str, tuple, float]:
    """Outline ``text``. Returns (d, bbox(x0,y0,x1,y1), advance_px).

    anchor    'start' | 'middle' | 'end'   (horizontal alignment at x)
    baseline  'alphabetic' | 'middle' (cap-height centre at y) | 'top' | 'x-middle' | 'bottom'
    tracking  letter-spacing in 1/1000 em
    missing   characters the font lacks: 'warn' (default; drawn as .notdef),
              'raise' or 'ignore'. Control characters (e.g. '\\n') are skipped
              with a warning — set one line per call. No shaping: combining
              marks are placed after their base letter (use precomposed
              characters such as 'é').
    """
    if anchor not in ("start", "middle", "end"):
        raise ValueError(f"anchor must be start|middle|end, not {anchor!r}")
    f, fid, sc, glyphs, total = _layout(font, text, size, variations, tracking, kerning, missing)
    x0 = x - {"start": 0.0, "middle": total / 2, "end": total}[anchor]
    y0 = y + _baseline_shift(font, size, variations, baseline)
    cmds = []
    for gname, gx, _ in glyphs:
        for c in _glyph_cmds(fid, gname):
            if c[0] == "Z":
                cmds.append(c); continue
            v = list(c[1:])
            for j in range(0, len(v), 2):
                v[j] = x0 + gx + v[j] * sc
                v[j + 1] = y0 - v[j + 1] * sc
            cmds.append((c[0], *v))
    d = G.cmds_to_d(cmds)
    if d:
        bb = G.bbox(d)
    else:
        bb = (x0, y0, x0 + total, y0)
    return d, bb, total


def text_on_path(font: str, text: str, size: float, path, offset: float = 0.0,
                 align: str = "middle", at: float = 0.5, baseline: str = "middle",
                 variations: dict | None = None, tracking: float = 0.0,
                 kerning: bool = True, flip: bool = False, missing: str = "warn") -> str:
    """Set text along a path (each glyph rotated to the local tangent).

    align/at: 'start' places the text start at arc-fraction ``at``; 'middle' centres
    it there; 'end' ends it there. ``offset`` shifts glyphs along the path's left
    normal (px). ``flip`` reverses the path direction (text on the bottom of a
    circle reads left-to-right)."""
    cv = G.curve(path)
    if flip:
        cv = cv.reversed()
        at = 1 - at
    if align not in ("start", "middle", "end"):
        raise ValueError(f"align must be start|middle|end, not {align!r}")
    f, fid, sc, glyphs, total = _layout(font, text, size, variations, tracking, kerning, missing)
    s_at = at * cv.length
    s0 = s_at - {"start": 0.0, "middle": total / 2, "end": total}[align]
    ysh = _baseline_shift(font, size, variations, baseline)
    out = []
    for gname, gx, adv in glyphs:
        sc_mid = s0 + gx + adv / 2
        p = cv.at_s(sc_mid)
        T = cv.tangent_s(sc_mid, h=max(adv / 2, 0.5))
        nL = np.array([T[1], -T[0]])
        base = p + nL * offset
        ang = math.degrees(math.atan2(T[1], T[0]))
        cmds = []
        for c in _glyph_cmds(fid, gname):
            if c[0] == "Z":
                cmds.append(c); continue
            v = list(c[1:])
            for j in range(0, len(v), 2):
                lx = v[j] * sc - adv / 2
                ly = -v[j + 1] * sc + ysh
                v[j], v[j + 1] = lx, ly
            cmds.append((c[0], *v))
        gd = G.cmds_to_d(cmds)
        if gd:
            gd = G.rotate(gd, ang)
            out.append(G.translate(gd, base[0], base[1]))
    return "".join(out)


def text_on_arc(font: str, text: str, size: float, cx: float, cy: float, r: float,
                center_deg: float | None = None, bottom: bool = False, **kw) -> str:
    """Text centred at angle ``center_deg`` (screen degrees; default -90 = top, or 90
    when ``bottom``) on a circle of radius r (cap-middle on the circle by default).
    ``bottom=True`` runs counter-clockwise so lower-arc text reads left-to-right."""
    if center_deg is None:
        center_deg = 90.0 if bottom else -90.0
    n = 720
    if not bottom:
        a = np.radians(np.linspace(center_deg - 180, center_deg + 180, n))
    else:
        a = np.radians(np.linspace(center_deg + 180, center_deg - 180, n))
    pts = np.column_stack([cx + r * np.cos(a), cy + r * np.sin(a)])
    return text_on_path(font, text, size, pts, at=0.5, align="middle", **kw)
