"""Card-level helpers: artboard constants, outlines, two-headed composition,
rendering (rsvg-convert) and contact sheets (PIL)."""
from __future__ import annotations

import hashlib
import os
import subprocess

from . import geom as G
from . import svg as S
from . import tokens

__all__ = ["W", "H", "R", "CX", "CY", "BLEED", "SAFE", "card_outline_d", "inset_outline_d",
           "clip_group", "rot180", "mirror", "two_headed", "new_card", "safe_zone",
           "render", "contact_sheet"]

W, H, R = 750.0, 1050.0, 37.5          # poker 2.5 x 3.5 in @ 300 ppi, 1/8in corner radius
CX, CY = W / 2, H / 2
BLEED = 37.5                           # 1/8 in (outside the artboard; add when exporting for print)
SAFE = 37.5                            # keep type/critical art 1/8 in inside trim



def card_outline_d(inset: float = 0.0, r: float | None = None) -> str:
    """Rounded card outline (optionally inset; radius shrinks with the inset)."""
    rr = (R - inset) if r is None else r
    return G.rect_d(inset, inset, W - 2 * inset, H - 2 * inset, max(rr, 0.0))


def inset_outline_d(inset: float, r: float | None = None) -> str:
    return card_outline_d(inset, r)


def _clip_id(clip_d: str, content: str, doc=None) -> str:
    if doc is not None:
        return doc.uid("ik-clip-")
    h = hashlib.sha1((clip_d + "\x00" + content).encode()).hexdigest()[:12]
    return f"ik-clip-{h}"


def clip_group(content: str, clip_d: str | None = None, id: str | None = None, doc=None) -> str:
    """Wrap content in a <g> clipped to ``clip_d`` (default: card outline).
    The <clipPath> is emitted inline so the result is self-contained. Its id
    is ``id``, else ``doc.uid('ik-clip-')`` when a Doc is given, else a content
    hash (``ik-clip-<sha1>``) — stable across runs and distinct for different
    content, so cards merged into one imposition sheet do not collide."""
    clip_d = clip_d or card_outline_d()
    cid = id or _clip_id(clip_d, content, doc)
    cp = S.clip_path(cid, S.path(clip_d))
    return cp + "\n" + S.g(content, clip_path=f"url(#{cid})")


def rot180(content: str, cx: float = CX, cy: float = CY) -> str:
    """Rotate SVG content 180° about the card centre."""
    return S.g(content, transform=S.rotate(180, cx, cy))


def mirror(content: str, axis: float = CX) -> str:
    """Mirror SVG content horizontally about x = axis."""
    return S.g(content, transform=S.matrix(-1, 0, 0, 1, 2 * axis, 0))


def two_headed(half: str, divider=None, box=None, stroke: str = tokens.INK,
               width: float = 2.0, clip: bool = True) -> str:
    """Compose a two-headed (court) design from its top half.

    half     SVG content drawn in the upper half of ``box`` (default whole card)
    divider  None | 'h' (horizontal rule) | 'diag' (split along the box diagonal,
             bottom-left -> top-right) | an SVG string drawn on top
    box      (x, y, w, h) court frame; the halves are clipped to it
    """
    x, y, w, h = box if box is not None else (0, 0, W, H)
    cx, cy = x + w / 2, y + h / 2
    if divider == "diag":
        top_poly = [(x, y), (x + w, y), (x, y + h)]
        top_d = G.poly_d(top_poly, True)
        div = S.path(f"M{S.fmt(x)} {S.fmt(y + h)}L{S.fmt(x + w)} {S.fmt(y)}", stroke=stroke,
                     stroke_width=width, fill="none")
    else:
        top_d = G.rect_d(x, y, w, h / 2)
        div = (S.path(f"M{S.fmt(x)} {S.fmt(cy)}H{S.fmt(x + w)}", stroke=stroke, stroke_width=width,
                      fill="none") if divider == "h" else "")
    if isinstance(divider, str) and divider not in ("h", "diag"):
        div = divider
    elif divider not in (None, "h", "diag"):
        raise ValueError("divider must be None, 'h', 'diag' or an SVG string")
    if clip:
        # one <clipPath>, referenced by both halves (the rotated copy's clip is
        # evaluated in its own rotated user space, so it clips the lower half)
        cid = _clip_id(top_d, half)
        cp = S.clip_path(cid, S.path(top_d))
        top = S.g(half, clip_path=f"url(#{cid})")
        return S.g(cp, top, rot180(top, cx, cy), div)
    return S.g(half, rot180(half, cx, cy), div)


def new_card(bg: str = tokens.PAPER, layers=("paper", "ink", "red", "foil"), title=None,
             knockout_colors=None) -> S.Doc:
    """A 750x1050 Doc with the rounded card filled with ``bg`` on the (unprinted)
    paper layer. ``knockout_colors`` (default: tokens.PAPER and white) are the
    fills that separations treat as knockouts."""
    doc = S.Doc(W, H, layers=layers, title=title, knockout_colors=knockout_colors)
    if bg:
        doc.add(S.path(card_outline_d(), fill=bg), layer="paper")
    return doc


def safe_zone(show_bleed: bool = False) -> str:
    """Debug overlay: trim (cyan), safe zone (magenta dashed), centre cross."""
    parts = [S.path(card_outline_d(), fill="none", stroke="#00AEEF", stroke_width=1),
             S.path(card_outline_d(SAFE), fill="none", stroke="#EC008C", stroke_width=1,
                    stroke_dasharray="6 4"),
             S.path(f"M{CX - 12} {CY}H{CX + 12}M{CX} {CY - 12}V{CY + 12}", stroke="#EC008C",
                    stroke_width=0.8, fill="none")]
    if show_bleed:
        parts.append(S.rect(-BLEED, -BLEED, W + 2 * BLEED, H + 2 * BLEED, fill="none",
                            stroke="#00AEEF", stroke_width=1, stroke_dasharray="2 3"))
    return S.g(*parts, id="safe-zone")


def render(svg_path: str, png_path: str, width: int = 750, background: str | None = None) -> str:
    """Render with rsvg-convert at ``width`` px (``background`` e.g. '#FFFFFF'
    fills transparent areas). Raises RuntimeError with rsvg's message on failure."""
    os.makedirs(os.path.dirname(os.path.abspath(png_path)), exist_ok=True)
    cmd = ["rsvg-convert", "-w", str(int(width)), svg_path, "-o", png_path]
    if background:
        cmd[1:1] = ["-b", background]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"rsvg-convert failed: {r.stderr.strip()}")
    return png_path


def contact_sheet(png_paths, out_png: str, cols: int = 4, gap: int = 24, bg: str = "#2B2B2B",
                  cell_width: int | None = None, round_corners: bool = False) -> str:
    """Tile PNGs into one sheet (PIL). ``round_corners`` masks card corners."""
    from PIL import Image, ImageDraw
    ims = [Image.open(p).convert("RGBA") for p in png_paths]
    if not ims:
        raise ValueError("no images")
    cw = cell_width or max(i.width for i in ims)
    ims = [i if i.width == cw else i.resize((cw, int(i.height * cw / i.width)), Image.LANCZOS)
           for i in ims]
    ch = max(i.height for i in ims)
    rows = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw + (cols + 1) * gap, rows * ch + (rows + 1) * gap), bg)
    for k, im in enumerate(ims):
        if round_corners:
            m = Image.new("L", im.size, 0)
            rr = int(R / W * im.width)
            ImageDraw.Draw(m).rounded_rectangle([0, 0, im.width - 1, im.height - 1], rr, fill=255)
            im.putalpha(Image.composite(im.getchannel("A"), m, m))
        r_, c_ = divmod(k, cols)
        sheet.alpha_composite(im, (gap + c_ * (cw + gap), gap + r_ * (ch + gap)))
    os.makedirs(os.path.dirname(os.path.abspath(out_png)), exist_ok=True)
    sheet.convert("RGB").save(out_png)
    return out_png
