"""Minimal string-based SVG builder with semantic print layers.

Elements are plain strings; ``Doc`` collects them into named layers
(``paper``, ``ink``, ``red``, ``foil`` ...) so each print separation can be
exported on its own with :meth:`Doc.save_layers`.

    from inkkit import svg
    doc = svg.Doc(750, 1050)
    doc.add(svg.path("M10 10L100 100", stroke="#13303B", stroke_width=2, fill="none"), layer="ink")
    doc.add(svg.path(G.circle_d(50, 50, 20), fill=tokens.PAPER), layer="ink")   # paper = knockout
    doc.save("out.svg")
    doc.save_layers("out-sep")        # out-sep-ink.svg ... (black ink, white knockouts)

Separation model (see :meth:`Doc.separations`): every printed layer becomes
a one-ink plate. Ink colours print black; paper/white fills — and anything
added with ``knockout=True`` — are knockouts and print white (no ink); every
layer ABOVE a plate knocks out of it (optionally choked by ``trap`` px)
unless it is listed in ``overprint``.
"""
from __future__ import annotations

import copy
import math
import os
import re
import warnings
import xml.etree.ElementTree as ET
from typing import Iterable

__all__ = [
    "fmt", "attrs", "el", "path", "g", "circle", "ellipse", "rect", "line", "polyline",
    "polygon", "use", "clip_path", "mask", "linear_gradient", "radial_gradient", "defs",
    "symbol", "translate", "rotate", "scale", "matrix", "tf", "foil_gradient", "Doc",
    "parse_color", "to_hex", "fit_paths",
]

SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
INKSCAPE_NS = "http://www.inkscape.org/namespaces/inkscape"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)
ET.register_namespace("inkscape", INKSCAPE_NS)


# ----------------------------------------------------------------------------
# number / attribute formatting
# ----------------------------------------------------------------------------
def fmt(v, nd: int = 2) -> str:
    """Format a number with at most ``nd`` decimals, no trailing zeros, no '-0'."""
    if isinstance(v, str):
        return v
    if isinstance(v, bool):
        return "1" if v else "0"
    if isinstance(v, int):
        return str(v)
    s = f"{float(v):.{nd}f}"
    if "." in s:
        s = s.rstrip("0").rstrip(".")
    if s in ("-0", ""):
        s = "0"
    return s


_RENAME = {"class_": "class", "href": "href", "xlink_href": "xlink:href", "viewBox": "viewBox",
           "sw": "stroke-width", "id_": "id"}
_NOT_ATTRS = {"layer": "Doc.add(..., layer=...)", "knockout": "Doc.add(..., knockout=True)"}


def _attr_name(k: str) -> str:
    if k in _RENAME:
        return _RENAME[k]
    if k.endswith("_"):
        k = k[:-1]
    if k in ("gradientUnits", "gradientTransform", "clipPathUnits", "maskUnits",
             "patternUnits", "preserveAspectRatio", "maskContentUnits", "spreadMethod",
             "patternTransform", "patternContentUnits"):
        return k
    return k.replace("_", "-")


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def attrs(**kw) -> str:
    """Build an attribute string. ``None``/False values are skipped;
    ``stroke_width`` -> ``stroke-width``; ``class_`` -> ``class``; ``sw`` is
    shorthand for stroke-width. If two keywords map to the same attribute the
    LAST one wins (so the output never has duplicate attributes)."""
    out: dict[str, str] = {}
    for k, v in kw.items():
        if k in _NOT_ATTRS:
            raise TypeError(f"{k!r} is not an SVG attribute — use {_NOT_ATTRS[k]}")
        if v is None or v is False:
            continue
        name = _attr_name(k)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            val = fmt(v)
        elif isinstance(v, (tuple, list)):
            val = " ".join(fmt(x) for x in v)
        else:
            val = str(v)
        out.pop(name, None)          # last value wins, placed last
        out[name] = _esc(val)
    return (" " + " ".join(f'{n}="{v}"' for n, v in out.items())) if out else ""


def el(tag: str, *children, **kw) -> str:
    """Generic element. Children are element strings (or iterables of them);
    a child that is not markup (does not start with '<') is treated as text
    and XML-escaped."""
    body = _join(children)
    a = attrs(**kw)
    if body:
        return f"<{tag}{a}>{body}</{tag}>"
    return f"<{tag}{a}/>"


def _join(children) -> str:
    parts = []
    for c in children:
        if c is None:
            continue
        if isinstance(c, str):
            if c and not c.lstrip().startswith("<"):
                c = _esc(c)
            parts.append(c)
        else:
            parts.append(_join(c))
    return "\n".join(p for p in parts if p)


# ----------------------------------------------------------------------------
# colours
# ----------------------------------------------------------------------------
_CSS = dict(
    aliceblue="f0f8ff", antiquewhite="faebd7", aqua="00ffff", aquamarine="7fffd4", azure="f0ffff",
    beige="f5f5dc", bisque="ffe4c4", black="000000", blanchedalmond="ffebcd", blue="0000ff",
    blueviolet="8a2be2", brown="a52a2a", burlywood="deb887", cadetblue="5f9ea0", chartreuse="7fff00",
    chocolate="d2691e", coral="ff7f50", cornflowerblue="6495ed", cornsilk="fff8dc", crimson="dc143c",
    cyan="00ffff", darkblue="00008b", darkcyan="008b8b", darkgoldenrod="b8860b", darkgray="a9a9a9",
    darkgreen="006400", darkgrey="a9a9a9", darkkhaki="bdb76b", darkmagenta="8b008b",
    darkolivegreen="556b2f", darkorange="ff8c00", darkorchid="9932cc", darkred="8b0000",
    darksalmon="e9967a", darkseagreen="8fbc8f", darkslateblue="483d8b", darkslategray="2f4f4f",
    darkslategrey="2f4f4f", darkturquoise="00ced1", darkviolet="9400d3", deeppink="ff1493",
    deepskyblue="00bfff", dimgray="696969", dimgrey="696969", dodgerblue="1e90ff", firebrick="b22222",
    floralwhite="fffaf0", forestgreen="228b22", fuchsia="ff00ff", gainsboro="dcdcdc",
    ghostwhite="f8f8ff", gold="ffd700", goldenrod="daa520", gray="808080", green="008000",
    greenyellow="adff2f", grey="808080", honeydew="f0fff0", hotpink="ff69b4", indianred="cd5c5c",
    indigo="4b0082", ivory="fffff0", khaki="f0e68c", lavender="e6e6fa", lavenderblush="fff0f5",
    lawngreen="7cfc00", lemonchiffon="fffacd", lightblue="add8e6", lightcoral="f08080",
    lightcyan="e0ffff", lightgoldenrodyellow="fafad2", lightgray="d3d3d3", lightgreen="90ee90",
    lightgrey="d3d3d3", lightpink="ffb6c1", lightsalmon="ffa07a", lightseagreen="20b2aa",
    lightskyblue="87cefa", lightslategray="778899", lightslategrey="778899", lightsteelblue="b0c4de",
    lightyellow="ffffe0", lime="00ff00", limegreen="32cd32", linen="faf0e6", magenta="ff00ff",
    maroon="800000", mediumaquamarine="66cdaa", mediumblue="0000cd", mediumorchid="ba55d3",
    mediumpurple="9370db", mediumseagreen="3cb371", mediumslateblue="7b68ee",
    mediumspringgreen="00fa9a", mediumturquoise="48d1cc", mediumvioletred="c71585",
    midnightblue="191970", mintcream="f5fffa", mistyrose="ffe4e1", moccasin="ffe4b5",
    navajowhite="ffdead", navy="000080", oldlace="fdf5e6", olive="808000", olivedrab="6b8e23",
    orange="ffa500", orangered="ff4500", orchid="da70d6", palegoldenrod="eee8aa", palegreen="98fb98",
    paleturquoise="afeeee", palevioletred="db7093", papayawhip="ffefd5", peachpuff="ffdab9",
    peru="cd853f", pink="ffc0cb", plum="dda0dd", powderblue="b0e0e6", purple="800080",
    rebeccapurple="663399", red="ff0000", rosybrown="bc8f8f", royalblue="4169e1",
    saddlebrown="8b4513", salmon="fa8072", sandybrown="f4a460", seagreen="2e8b57",
    seashell="fff5ee", sienna="a0522d", silver="c0c0c0", skyblue="87ceeb", slateblue="6a5acd",
    slategray="708090", slategrey="708090", snow="fffafa", springgreen="00ff7f", steelblue="4682b4",
    tan="d2b48c", teal="008080", thistle="d8bfd8", tomato="ff6347", turquoise="40e0d0",
    violet="ee82ee", wheat="f5deb3", white="ffffff", whitesmoke="f5f5f5", yellow="ffff00",
    yellowgreen="9acd32")
_RGB_RE = re.compile(r"rgba?\(\s*([^)]*)\)", re.I)


def parse_color(c) -> tuple[int, int, int] | None:
    """'#rgb' / '#rrggbb' / '#rrggbbaa' / 'rgb(r,g,b)' (ints or %) / CSS name
    (any case) -> (r, g, b); None for 'none', url(...), currentColor or junk."""
    if c is None:
        return None
    s = str(c).strip().lower()
    if not s or s in ("none", "transparent", "currentcolor", "inherit") or s.startswith("url("):
        return None
    if s.startswith("#"):
        h = s[1:]
        if len(h) in (3, 4):
            h = "".join(ch * 2 for ch in h[:3])
        if len(h) in (6, 8) and all(ch in "0123456789abcdef" for ch in h[:6]):
            return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return None
    m = _RGB_RE.fullmatch(s)
    if m:
        vals = [v.strip() for v in re.split(r"[,\s/]+", m.group(1)) if v.strip()][:3]
        if len(vals) != 3:
            return None
        out = []
        for v in vals:
            try:
                out.append(round(float(v[:-1]) * 2.55) if v.endswith("%") else round(float(v)))
            except ValueError:
                return None
        return tuple(max(0, min(255, x)) for x in out)
    if s in _CSS:
        h = _CSS[s]
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return None


def to_hex(c) -> str | None:
    rgb = parse_color(c)
    return None if rgb is None else "#%02X%02X%02X" % rgb


# ----------------------------------------------------------------------------
# element helpers
# ----------------------------------------------------------------------------
def path(d: str, **kw) -> str:
    """<path>. Common kwargs: fill, stroke, stroke_width (or sw), fill_rule,
    stroke_linecap, stroke_linejoin, opacity, transform, id."""
    if not d:
        return ""
    return el("path", d=d, **kw)


def g(*children, **kw) -> str:
    return el("g", *children, **kw) if _join(children) else ""


def circle(cx, cy, r, **kw) -> str:
    return el("circle", cx=cx, cy=cy, r=r, **kw)


def ellipse(cx, cy, rx, ry, **kw) -> str:
    return el("ellipse", cx=cx, cy=cy, rx=rx, ry=ry, **kw)


def rect(x, y, w, h, rx=None, ry=None, **kw) -> str:
    return el("rect", x=x, y=y, width=w, height=h, rx=rx, ry=ry, **kw)


def line(x1, y1, x2, y2, **kw) -> str:
    return el("line", x1=x1, y1=y1, x2=x2, y2=y2, **kw)


def _pts(pts) -> str:
    return " ".join(f"{fmt(x)},{fmt(y)}" for x, y in pts)


def polyline(pts, **kw) -> str:
    return el("polyline", points=_pts(pts), **kw)


def polygon(pts, **kw) -> str:
    return el("polygon", points=_pts(pts), **kw)


def use(ref: str, x=None, y=None, **kw) -> str:
    """<use href="#ref">. ``ref`` may be given with or without '#'."""
    if not ref.startswith("#"):
        ref = "#" + ref
    return el("use", href=ref, x=x, y=y, **kw)


def clip_path(id: str, *children, **kw) -> str:
    return el("clipPath", *children, id=id, **kw)


def mask(id: str, *children, **kw) -> str:
    return el("mask", *children, id=id, **kw)


def _stops(stops) -> str:
    out = []
    for s in stops:
        if len(s) == 2:
            off, col = s
            op = None
        else:
            off, col, op = s
        out.append(el("stop", offset=off, stop_color=col, stop_opacity=op))
    return "".join(out)


def linear_gradient(id: str, stops, x1=0, y1=0, x2=1, y2=0, units="objectBoundingBox", **kw) -> str:
    """stops: [(offset 0..1, color[, opacity]), ...]"""
    return el("linearGradient", _stops(stops), id=id, x1=x1, y1=y1, x2=x2, y2=y2,
              gradientUnits=units, **kw)


def radial_gradient(id: str, stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None,
                    units="objectBoundingBox", **kw) -> str:
    return el("radialGradient", _stops(stops), id=id, cx=cx, cy=cy, r=r, fx=fx, fy=fy,
              gradientUnits=units, **kw)


def defs(*children) -> str:
    return el("defs", *children)


def symbol(id: str, *children, viewBox=None, **kw) -> str:
    vb = " ".join(fmt(v) for v in viewBox) if viewBox is not None else None
    return el("symbol", *children, id=id, viewBox=vb, **kw)


def foil_gradient(id: str, base: str = "#B8955A", angle: float = 35.0, units="userSpaceOnUse",
                  box=(0, 0, 750, 1050)) -> str:
    """A metallic-looking linear gradient (preview only; print uses a foil
    separation). ``base`` is any colour :func:`parse_color` accepts."""
    rgb = parse_color(base)
    if rgb is None:
        raise ValueError(f"foil_gradient: cannot parse colour {base!r}")
    r, gg, b = rgb

    def shade(f):
        if f >= 1:
            c = [int(v + (255 - v) * (f - 1)) for v in (r, gg, b)]
        else:
            c = [int(v * f) for v in (r, gg, b)]
        return "#%02X%02X%02X" % tuple(max(0, min(255, v)) for v in c)

    stops = [(0.0, shade(0.72)), (0.22, shade(1.35)), (0.40, shade(0.92)), (0.55, shade(1.18)),
             (0.72, shade(0.70)), (0.88, shade(1.30)), (1.0, shade(0.85))]
    x, y, w, h = box
    cx, cy = x + w / 2, y + h / 2
    a = math.radians(angle)
    L = 0.5 * (abs(w * math.cos(a)) + abs(h * math.sin(a)))
    return linear_gradient(id, stops, cx - L * math.cos(a), cy - L * math.sin(a),
                           cx + L * math.cos(a), cy + L * math.sin(a), units=units)


# ----------------------------------------------------------------------------
# transforms
# ----------------------------------------------------------------------------
def translate(x, y=0) -> str:
    return f"translate({fmt(x)} {fmt(y)})"


def rotate(a, cx=None, cy=None) -> str:
    if cx is None:
        return f"rotate({fmt(a)})"
    return f"rotate({fmt(a)} {fmt(cx)} {fmt(cy)})"


def scale(sx, sy=None) -> str:
    return f"scale({fmt(sx, 4)})" if sy is None else f"scale({fmt(sx, 4)} {fmt(sy, 4)})"


def matrix(a, b, c, d, e, f) -> str:
    return "matrix(" + " ".join(fmt(v, 5) for v in (a, b, c, d)) + f" {fmt(e)} {fmt(f)})"


def tf(*parts) -> str:
    """Compose transform strings: tf(translate(10,0), rotate(45))."""
    return " ".join(p for p in parts if p)


# ----------------------------------------------------------------------------
# separations (recolouring an element tree for one printing plate)
# ----------------------------------------------------------------------------
_SKIP = {"mask", "clipPath", "defs", "linearGradient", "radialGradient", "pattern", "symbol",
         "title", "desc", "metadata", "style", "filter", "marker"}
_OPACITY = ("opacity", "fill-opacity", "stroke-opacity")


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _style_dict(s: str | None) -> dict:
    out = {}
    for part in (s or "").split(";"):
        if ":" in part:
            k, v = part.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def _parse_fragment(fragment: str) -> ET.Element:
    return ET.fromstring(f'<g xmlns="{SVG_NS}" xmlns:xlink="{XLINK_NS}" '
                         f'xmlns:inkscape="{INKSCAPE_NS}">{fragment}</g>')


class _Sep:
    """Recolours element trees for one plate (see Doc.separations)."""

    def __init__(self, mono, knockout_hex, white, trap, flatten_opacity, defs_by_id):
        self.mono, self.ko, self.white = mono, knockout_hex, white
        self.trap, self.flatten = trap, flatten_opacity
        self.defs = defs_by_id
        self.inks: set = set()
        self.warned_opacity = False

    def paint(self, value, role):
        """Map one fill/stroke value. role: 'ink' | 'ko' (everything -> white)."""
        if value is None:
            return None
        v = value.strip()
        if v.lower() in ("none", "transparent"):
            return "none"
        if v.lower() == "inherit":
            return v
        if role == "ko":
            return self.white
        if v.lower().startswith("url("):
            self.inks.add("url")
            return self.mono
        hx = to_hex(v)
        if hx is None:               # currentColor / junk: treat as ink
            return self.mono
        if hx in self.ko:
            return self.white
        self.inks.add(hx)
        return self.mono

    def expand_uses(self, node):
        for parent in list(node.iter()):
            for i, ch in enumerate(list(parent)):
                if _local(ch.tag) != "use":
                    continue
                ref = ch.get("href") or ch.get(f"{{{XLINK_NS}}}href") or ""
                tgt = self.defs.get(ref.lstrip("#"))
                if tgt is None or (_local(tgt.tag) == "symbol" and tgt.get("viewBox")):
                    continue
                grp = ET.Element(f"{{{SVG_NS}}}g")
                for k, v in ch.attrib.items():
                    if k not in ("href", f"{{{XLINK_NS}}}href", "x", "y", "width", "height", "id"):
                        grp.set(k, v)
                x, y = ch.get("x", "0"), ch.get("y", "0")
                t = grp.get("transform", "")
                if x not in ("0", "") or y not in ("0", ""):
                    t = f"{t} translate({x} {y})".strip()
                if t:
                    grp.set("transform", t)
                body = copy.deepcopy(tgt)
                if _local(body.tag) == "symbol":
                    for sub in list(body):
                        grp.append(sub)
                else:
                    body.attrib.pop("id", None)
                    grp.append(body)
                parent[i] = grp
                self.expand_uses(grp)

    def walk(self, node, role):
        tag = _local(node.tag)
        if tag in _SKIP:
            return
        st = _style_dict(node.get("style"))
        for prop in ("fill", "stroke"):
            val = st.pop(prop, None) or node.get(prop)
            if val is not None:
                node.set(prop, self.paint(val, role))
        for prop in _OPACITY:
            val = st.pop(prop, None)
            if val is None:
                val = node.get(prop)
            if val is None:
                continue
            if self.flatten:
                node.attrib.pop(prop, None)
                if not self.warned_opacity and val.strip() not in ("1", "1.0"):
                    warnings.warn("separations: opacity flattened to 1 (a spot plate cannot hold "
                                  "transparency; use a tint layer instead)", stacklevel=4)
                    self.warned_opacity = True
            else:
                node.set(prop, val)
        if st:
            node.set("style", ";".join(f"{k}:{v}" for k, v in st.items()))
        else:
            node.attrib.pop("style", None)
        if role == "ko" and self.trap > 0:
            self._choke(node, tag)
        for ch in list(node):
            self.walk(ch, role)

    def _choke(self, node, tag):
        """Shrink an upper-layer knockout by ``trap`` px so the plate below
        spreads under it (a trap). FILL paths are inset geometrically;
        strokes get thinner."""
        sw = node.get("stroke-width")
        if node.get("stroke") not in (None, "none") and sw:
            try:
                node.set("stroke-width", fmt(max(0.0, float(sw) - 2 * self.trap)))
            except ValueError:
                pass
        if tag == "path" and node.get("fill") != "none" and node.get("d"):
            from . import geom as G
            node.set("d", G.offset(node.get("d"), -self.trap, join="miter") or "M0 0z")


def fit_paths(svg_text: str, tol: float = 0.05, corner: float = 40.0) -> str:
    """Refit every ``d="..."`` in an SVG string with cubic Béziers
    (:func:`inkkit.geom.fit_curves`): smaller (1.2–3.5×), editable files."""
    from . import geom as G

    def rep(m):
        try:
            return f' d="{G.fit_curves(m.group(1), tol, corner)}"'
        except ValueError:
            return m.group(0)
    return re.sub(r'\sd="([^"]*)"', rep, svg_text)


# ----------------------------------------------------------------------------
# document
# ----------------------------------------------------------------------------
class Doc:
    """An SVG document made of named layers.

    Doc(w=750, h=1050, viewBox=None, bg=None, layers=('paper','ink','red','foil'),
        title=None, knockout_colors=None, id_prefix='')

    ``knockout_colors`` (default tokens.PAPER and white) are the fills that
    separations print as knockouts; ``id_prefix`` namespaces ``uid()`` so
    several cards can share one imposition sheet.

    * ``add(content, layer='ink', knockout=False)`` appends element string(s)
      to a layer. ``knockout=True`` marks content that hides what is beneath
      it: it is drawn as given in the composite and prints as a knockout
      (no ink) on every plate. Paper/white fills are knockouts automatically.
    * ``layer_style(name, **attrs)`` sets attributes on the layer group
      (e.g. default ``fill``).
    * ``add_def(content)`` adds to <defs>; ``uid(prefix)`` gives unique ids.
    * ``save(path, fit=None)`` / ``to_string()`` / ``separations()`` /
      ``save_layers(prefix)`` / ``render(png)``.
    """

    def __init__(self, w: float = 750, h: float = 1050, viewBox=None, bg: str | None = None,
                 layers: Iterable[str] = ("paper", "ink", "red", "foil"), title: str | None = None,
                 knockout_colors: Iterable[str] | None = None, id_prefix: str = ""):
        self.w, self.h = w, h
        self.viewBox = tuple(viewBox) if viewBox is not None else (0, 0, w, h)
        self.title = title
        self.id_prefix = id_prefix
        self._defs: list[str] = []
        self._layers: dict[str, list[tuple[str, bool]]] = {name: [] for name in layers}
        self._layer_attrs: dict[str, dict] = {name: {} for name in layers}
        self._ids: dict[str, int] = {}
        if knockout_colors is None:
            from . import tokens
            knockout_colors = (tokens.PAPER, "#FFFFFF")
        self.knockout_colors = {to_hex(c) for c in knockout_colors if to_hex(c)}
        if bg:
            self.add(rect(*self.viewBox, fill=bg), layer=next(iter(self._layers), "paper"))

    # ids / defs --------------------------------------------------------------
    def uid(self, prefix: str = "id") -> str:
        n = self._ids.get(prefix, 0) + 1
        self._ids[prefix] = n
        return f"{self.id_prefix}{prefix}{n}"

    def add_def(self, *content: str) -> "Doc":
        for c in content:
            if c:
                self._defs.append(c)
        return self

    # layers ------------------------------------------------------------------
    def layer_style(self, name: str, **kw) -> "Doc":
        self._layers.setdefault(name, [])
        self._layer_attrs.setdefault(name, {}).update(kw)
        return self

    def add(self, *content, layer: str = "ink", knockout: bool = False) -> "Doc":
        lst = self._layers.setdefault(layer, [])
        self._layer_attrs.setdefault(layer, {})
        for c in content:
            if c is None:
                continue
            if isinstance(c, str):
                if c:
                    lst.append((c, knockout))
            else:
                self.add(*c, layer=layer, knockout=knockout)
        return self

    @property
    def layers(self) -> list[str]:
        return [k for k, v in self._layers.items() if v]

    # output --------------------------------------------------------------------
    def _head(self) -> str:
        vb = " ".join(fmt(v) for v in self.viewBox)
        return (f'<svg xmlns="{SVG_NS}" xmlns:xlink="{XLINK_NS}" xmlns:inkscape="{INKSCAPE_NS}" '
                f'width="{fmt(self.w)}" height="{fmt(self.h)}" viewBox="{vb}">')

    def _layer_group(self, name: str, mono: str | None = None) -> str:
        items = self._layers.get(name) or []
        if not items:
            return ""
        if mono:  # legacy single-plate recolour (no upper-layer knockouts)
            return self._plate_group(name, [], mono, 0.0, True, _Sep(
                mono, self.knockout_colors, "#FFFFFF", 0.0, True, self._defs_by_id()))
        body = "\n".join(c for c, _ in items)
        la = dict(self._layer_attrs.get(name, {}))
        return f'<g id="layer-{name}" inkscape:groupmode="layer" inkscape:label="{name}"' \
               f'{attrs(**la)}>\n{body}\n</g>'

    def _defs_by_id(self) -> dict:
        if not self._defs:
            return {}
        try:
            root = _parse_fragment("\n".join(self._defs))
        except ET.ParseError:
            return {}
        return {e.get("id"): e for e in root.iter() if e.get("id")}

    def _plate_group(self, name, upper, mono, trap, flatten, sep: _Sep) -> str:
        la = dict(self._layer_attrs.get(name, {}))
        parts = []

        def emit(content, layer_attrs, role):
            node = _parse_fragment(content)
            sep.expand_uses(node)
            # the layer group's own fill/stroke is inherited by the item; an
            # unset fill defaults to black, which is ink
            for prop, default in (("fill", "currentColor"), ("stroke", None)):
                v = layer_attrs.get(prop)
                if v is not None or default:
                    node.set(prop, str(v if v is not None else default))
            sep.walk(node, role)
            wa = attrs(fill=node.get("fill"), stroke=node.get("stroke"))
            parts.append(f"<g{wa}>{_inner(node)}</g>")

        for c, ko in self._layers[name]:
            emit(c, la, "ko" if ko else "ink")
        for uname in upper:
            ula = self._layer_attrs.get(uname, {})
            for c, _ in self._layers[uname]:
                emit(c, ula, "ko")
        for k in ("fill", "stroke", "opacity", "fill_opacity", "stroke_opacity"):
            la.pop(k, None)
        return (f'<g id="layer-{name}" inkscape:groupmode="layer" inkscape:label="{name}"'
                f'{attrs(**la)}>\n' + "\n".join(parts) + "\n</g>")

    def to_string(self, layers: Iterable[str] | None = None, mono: str | None = None,
                  extra: str = "") -> str:
        names = list(layers) if layers is not None else list(self._layers)
        parts = [self._head()]
        if self.title:
            parts.append(f"<title>{_esc(self.title)}</title>")
        if self._defs:
            parts.append("<defs>\n" + "\n".join(self._defs) + "\n</defs>")
        for n in names:
            grp = self._layer_group(n, mono)
            if grp:
                parts.append(grp)
        if extra:
            parts.append(extra)
        parts.append("</svg>\n")
        return "\n".join(parts)

    def separations(self, mono: str = "#000000", exclude=("paper",), knockout: bool = True,
                    overprint: Iterable[str] = (), trap: float = 0.0,
                    flatten_opacity: bool = True, white: str = "#FFFFFF") -> dict[str, str]:
        """One SVG string per printed layer (layer order = paint order):

        * this layer's ink colours -> ``mono``; paper/white fills and
          ``knockout=True`` content -> ``white`` (knocked out, no ink);
        * with ``knockout`` every layer ABOVE it (except those in
          ``overprint``) is painted ``white`` on top, i.e. knocks out of this
          plate; ``trap`` px chokes those knockouts so this ink spreads
          slightly under the upper colour (typical 0.1 mm ≈ 1.2 px);
        * masks, clip paths and defs are left untouched; ``<use>`` references
          to defs are expanded so they separate correctly; opacity is
          flattened (with a warning).
        A warning is issued when a plate mixes several ink colours."""
        overprint = set(overprint)
        order = [n for n in self._layers if self._layers[n]]
        defs_by_id = self._defs_by_id()
        out = {}
        for k, n in enumerate(order):
            if n in exclude:
                continue
            upper = [u for u in order[k + 1:] if knockout and u not in overprint and u not in exclude]
            sep = _Sep(mono, self.knockout_colors, white, trap, flatten_opacity, defs_by_id)
            grp = self._plate_group(n, upper, mono, trap, flatten_opacity, sep)
            inks = sorted(i for i in sep.inks if i != "url")
            if len(inks) > 1:
                warnings.warn(f"separation {n!r} mixes ink colours {inks}; a plate prints one ink",
                              stacklevel=2)
            parts = [self._head()]
            if self.title:
                parts.append(f"<title>{_esc(self.title)} — {n} plate</title>")
            if self._defs:
                parts.append("<defs>\n" + "\n".join(self._defs) + "\n</defs>")
            parts += [grp, "</svg>\n"]
            out[n] = "\n".join(parts)
        return out

    def save(self, filename: str, fit: float | None = None, **kw) -> str:
        """Write the composite SVG. ``fit`` (px tolerance, e.g. 0.05) refits
        all path data with cubic Béziers for a much smaller, editable file."""
        os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
        s = self.to_string(**kw)
        if fit:
            s = fit_paths(s, fit)
        with open(filename, "w", encoding="utf-8") as fh:
            fh.write(s)
        return filename

    def save_layers(self, prefix: str, mono: str | None = "#000000",
                    exclude=("paper",), **kw) -> list[str]:
        """Write one plate SVG per printed layer: ``{prefix}-{layer}.svg``
        (see :meth:`separations` for the knockout model and options).
        ``mono=None`` writes each layer in its preview colours instead."""
        out = []
        if mono is None:
            for n in self.layers:
                if n in exclude:
                    continue
                fn = f"{prefix}-{n}.svg"
                self.save(fn, layers=[n])
                out.append(fn)
            return out
        fit = kw.pop("fit", None)
        for n, s in self.separations(mono, exclude, **kw).items():
            fn = f"{prefix}-{n}.svg"
            os.makedirs(os.path.dirname(os.path.abspath(fn)), exist_ok=True)
            with open(fn, "w", encoding="utf-8") as fh:
                fh.write(fit_paths(s, fit) if fit else s)
            out.append(fn)
        return out

    def render(self, png: str, width: int = 750, svg_path: str | None = None,
               background: str | None = None) -> str:
        """Save (to ``svg_path`` or next to the PNG) and render with rsvg-convert."""
        from .card import render as _render
        sp = svg_path or os.path.splitext(png)[0] + ".svg"
        self.save(sp)
        return _render(sp, png, width, background=background)


def _inner(node: ET.Element) -> str:
    """Serialise the children of a parsed wrapper <g> without namespace noise."""
    s = ET.tostring(node, encoding="unicode", short_empty_elements=True)
    # strip the wrapper element (first tag) and its closing tag
    start = s.index(">") + 1
    if s.endswith("/>") and start == len(s):
        return ""
    end = s.rfind("</")
    return s[start:end]
