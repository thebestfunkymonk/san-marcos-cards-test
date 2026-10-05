"""Print-layered card documents (creative brief §B.1, §I.25, §K).

``CardDoc`` writes a 750 x 1050 SVG whose body is exactly five layer groups,
bottom to top::

    <g id="paper">  <g id="jade">  <g id="red">  <g id="gold">  <g id="ink">

(§K: "On the A♠ and the aces, gold sits above the suit ink" — pass
``order=ACE_ORDER`` for A♠/A♣ so the gold emblem prints over the Aquifer
silhouette; for A♥/A♦ the default order already puts gold above red.)

Every layer group is clipped to the card outline (r 37.5). The paper layer
holds the stock: the rounded card filled Limestone, or white for QA
(``stock="white"``, §0.3.5 "white with no tint plate"). Nothing else may be
paper-coloured — knockouts are geometric (see ``deck/ART_CONTRACT.md``).

Utilities
---------
``rot180(fragment)``             180° copy about (375, 525) (a pure rotation).
``two_headed(layers, clip_d)``   courts: clip each layer's top-half art to
                                 ``clip_d`` (default: the frame's art window
                                 above the band) and add its 180° copy.
``continuous_two_headed(layers, seam)``  continuous courts: ``two_headed`` with
                                 ``frames.seam_clip_d(seam)`` — the window on
                                 the seam's top side, grown 0.5 px across it
                                 so the halves overlap (no AA hairline).
``layers_merge(a, b, ...)``      concatenate {layer: [fragments]} dicts.
"""
from __future__ import annotations

import os
import re

from inkkit import geom as G
from inkkit import svg as S
from deck import tokens as T

__all__ = ["CardDoc", "rot180", "two_headed", "continuous_two_headed", "layers_merge", "ACE_ORDER", "STOCKS",
           "card_outline_d"]

ACE_ORDER = ("paper", "jade", "red", "ink", "gold")
STOCKS = {"limestone": T.PAPER, "white": T.WHITE}
_SVG_NS = "http://www.w3.org/2000/svg"


def card_outline_d(inset: float = 0.0, r: float | None = None) -> str:
    rr = T.CORNER_R - inset if r is None else r
    return G.rect_d(inset, inset, T.W - 2 * inset, T.H - 2 * inset, max(rr, 0.0))


def rot180(fragment: str, cx: float = T.CX, cy: float = T.CY) -> str:
    """The fragment rotated 180° about the card centre (no scaling)."""
    if not fragment:
        return ""
    return f'<g transform="rotate(180 {S.fmt(cx)} {S.fmt(cy)})">{fragment}</g>'


def layers_merge(*dicts) -> dict:
    """Merge {layer: [fragments]} dicts (fragment order preserved)."""
    out: dict[str, list[str]] = {}
    for d in dicts:
        if not d:
            continue
        for k, v in d.items():
            if k not in T.LAYERS:
                raise ValueError(f"unknown layer {k!r}; layers are {T.LAYERS}")
            if isinstance(v, str):
                v = [v]
            out.setdefault(k, []).extend(x for x in v if x)
    return out


def two_headed(layers: dict, clip_d: str | None = None, clip_id: str = "court-art") -> dict:
    """Two-headed court construction (§F.1): per layer, clip the top-half art
    to ``clip_d`` and add its 180° copy about (375, 525).

    ``clip_d`` defaults to ``deck.frames.court_clip_d()`` — the chamfered art
    window above the divider band (the band then hides the cut). Each layer
    gets its own <clipPath> (id ``{clip_id}-{layer}``) so that every layer
    group stays self-contained for plate separation. The clip is geometric:
    no paper-coloured cover is involved."""
    if clip_d is None:
        from deck import frames
        clip_d = frames.court_clip_d()
    out = {}
    for layer, frags in layers.items():
        frags = [f for f in ([frags] if isinstance(frags, str) else frags) if f]
        if not frags:
            continue
        cid = f"{clip_id}-{layer}"
        body = "".join(frags)
        cp = f'<defs><clipPath id="{cid}" clipPathUnits="userSpaceOnUse"><path d="{clip_d}"/></clipPath></defs>'
        top = f'<g clip-path="url(#{cid})">{body}</g>'
        out[layer] = [cp, f'<g class="court-top">{top}</g>', f'<g class="court-rot">{rot180(top)}</g>']
    return out


def continuous_two_headed(layers: dict, seam=None, clip_id: str = "court-art") -> dict:
    """Continuous double-head (ART_CONTRACT §3.1b): clip the top-half art to
    the seam's top side inside the art window and add the 180° copy. The
    clip runs ``frames.SEAM_OVERLAP`` past the seam, so its rotation (the
    bottom half's clip) overlaps it by 1 px and the two halves meet with no
    anti-aliased paper hairline. Nothing marks the seam."""
    from deck import frames
    return two_headed(layers, frames.seam_clip_d(seam), clip_id=clip_id)


class CardDoc:
    """One card: 750 x 1050 viewBox, card-outline clip, five layer groups.

    CardDoc(card_id, stock="limestone", order=LAYERS, title=None, paper=True)
      .add(layer, *fragments)       append SVG fragment strings to a layer
      .add_layers({layer: [...]})   add a whole layer dict
      .add_def(fragment)            document-level <defs> content
      .to_string(bleed=False) / .save(path, bleed=False)   (bleed: §B.1 825 x 1125 print file)
    ``paper=False`` leaves the paper layer empty (BACK: its art supplies the
    stock and the flood itself)."""

    def __init__(self, card_id: str = "", stock: str = "limestone", order=T.LAYERS,
                 title: str | None = None, paper: bool = True):
        if stock not in STOCKS:
            raise ValueError(f"stock must be one of {sorted(STOCKS)}")
        if sorted(order) != sorted(T.LAYERS):
            raise ValueError(f"order must be a permutation of {T.LAYERS}")
        self.card_id = card_id
        self.stock = stock
        self.paper_color = STOCKS[stock]
        self.order = tuple(order)
        self.title = title or card_id
        self._layers: dict[str, list[str]] = {k: [] for k in self.order}
        self._defs: list[str] = []
        if paper:
            self.add("paper", S.path(card_outline_d(), fill=self.paper_color, class_="stock"))

    def add(self, layer: str, *fragments) -> "CardDoc":
        if layer not in self._layers:
            raise ValueError(f"unknown layer {layer!r}; layers are {T.LAYERS}")
        for f in fragments:
            if f is None:
                continue
            if isinstance(f, str):
                if f:
                    self._layers[layer].append(f)
            else:
                self.add(layer, *f)
        return self

    def add_layers(self, layers: dict | None) -> "CardDoc":
        for k, v in (layers or {}).items():
            self.add(k, v)
        return self

    def add_def(self, fragment: str) -> "CardDoc":
        if fragment:
            self._defs.append(fragment)
        return self

    def stock_fill(self, fragment: str) -> str:
        """Recolour Limestone fills in a PAPER-layer fragment to this stock
        (white-stock QA renders of art that draws its own paper, e.g. BACK)."""
        if self.paper_color == T.PAPER:
            return fragment
        return re.sub(re.escape(T.PAPER), self.paper_color, fragment, flags=re.I)

    def to_string(self, bleed: bool = False) -> str:
        """The card SVG. ``bleed=True`` writes the §B.1 print file: 825 x 1125
        (the viewBox grown by BLEED = 37.5 px per side, no transform), with the
        paper layer extended to the bleed edge as a plain rectangle (the
        background only; the die cuts the corners). Every other layer keeps
        the card-outline clip — no art crosses the trim."""
        b = T.BLEED if bleed else 0.0
        w, h = T.W + 2 * b, T.H + 2 * b
        head = (f'<svg xmlns="{_SVG_NS}" width="{S.fmt(w)}" height="{S.fmt(h)}" '
                f'viewBox="{S.fmt(-b)} {S.fmt(-b)} {S.fmt(w)} {S.fmt(h)}">')
        parts = [head, f"<title>{S._esc(self.title)}</title>",
                 f'<defs><clipPath id="card" clipPathUnits="userSpaceOnUse">'
                 f'<path d="{card_outline_d()}"/></clipPath>{"".join(self._defs)}</defs>']
        for name in self.order:
            body = self._layers[name]
            if name == "paper" and self.paper_color != T.PAPER:
                body = [self.stock_fill(b_) for b_ in body]
            if name == "paper" and bleed:
                body = [S.path(G.rect_d(-b, -b, w, h), fill=self.paper_color, class_="stock bleed")] + \
                       [x for x in body if 'class="stock"' not in x]
                inner = "\n".join(body)
                parts.append(f'<g id="{name}">\n{inner}\n</g>')
                continue
            inner = "\n".join(body)
            parts.append(f'<g id="{name}" clip-path="url(#card)">' + (f"\n{inner}\n" if inner else "") + "</g>")
        parts.append("</svg>\n")
        return "\n".join(parts)

    def save(self, path: str, bleed: bool = False) -> str:
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(self.to_string(bleed=bleed))
        return path
