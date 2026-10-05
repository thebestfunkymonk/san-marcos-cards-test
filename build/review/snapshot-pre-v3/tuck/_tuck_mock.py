"""Tuck MOCK-UPS (presentation only — never print files).

Only here may the foil wear the §C preview gradient (#8A6A34 -> #D8B56A ->
#F6E3A1) and the emboss plate be shown as relief (soft light / shadow
filters).  The print SVGs stay flat Lion Gold with the emboss as a
non-printing tooling plate.

    panel_mock     one panel, gradient foil + subtle blind emboss
    presentation   the closed box in 3/4 view (front, side A, the top with the
                   seal across the lid's closure) beside the A♠ and a card back
"""
from __future__ import annotations

import base64
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path

from deck import tokens as T
from inkkit.svg import fmt

from tuck import _tuck_common as K

FOIL = K.FOIL
BOARD = K.BOARD
A, B, CC = T.FOIL_PREVIEW          # #8A6A34, #D8B56A, #F6E3A1


def gradient(gid: str, x0, y0, x1, y1, *, reflect=True) -> str:
    stops = [(0.0, A), (0.28, B), (0.46, CC), (0.56, B), (0.78, A), (1.0, B)]
    st = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    sp = ' spreadMethod="reflect"' if reflect else ""
    return (f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{fmt(x0)}" y1="{fmt(y0)}" '
            f'x2="{fmt(x1)}" y2="{fmt(y1)}"{sp}>{st}</linearGradient>')


def gild(svg_frag: str, gid: str) -> str:
    """Swap flat Lion Gold for the preview gradient (mock-ups only)."""
    return re.sub(r'(stroke|fill)="' + re.escape(FOIL) + '"', rf'\1="url(#{gid})"', svg_frag)


FILTERS = """
<filter id="emb-sh" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.6"/></filter>
<filter id="emb-hi" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="1.1"/></filter>
<filter id="foil-sh" x="-5%" y="-5%" width="110%" height="110%"><feGaussianBlur stdDeviation="0.7"/></filter>
<filter id="grain" x="0" y="0" width="100%" height="100%">
  <feTurbulence type="fractalNoise" baseFrequency="0.9" numOctaves="2" seed="7" result="n"/>
  <feColorMatrix type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 0.05 0"/>
  <feComposite in2="SourceGraphic" operator="in"/>
</filter>
<filter id="soft" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
<filter id="soft2" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="5"/></filter>
"""


def panel_art(res: dict, w: float, h: float, gid: str, *, emboss=True, board=True, grain=True) -> str:
    """Board + emboss relief + gradient foil for one panel, in panel coords."""
    out = []
    if board:
        out.append(f'<rect x="0" y="0" width="{fmt(w)}" height="{fmt(h)}" fill="{BOARD}"/>')
        if grain:
            out.append(f'<rect x="0" y="0" width="{fmt(w)}" height="{fmt(h)}" fill="#fff" filter="url(#grain)"/>')
    if emboss:
        for d, level in res.get("emboss", []):
            k = 1.0 if level == 1 else 1.5
            out.append(f'<path d="{d}" fill="#000" fill-opacity="{0.42 * k:.2f}" '
                       f'transform="translate({1.3 * k:.2f} {1.7 * k:.2f})" filter="url(#emb-sh)"/>')
            out.append(f'<path d="{d}" fill="#fff" fill-opacity="{0.10 * k:.2f}" '
                       f'transform="translate({-1.0 * k:.2f} {-1.2 * k:.2f})" filter="url(#emb-hi)"/>')
            out.append(f'<path d="{d}" fill="#133330"/>')
    foil = K.foil_svg(res["foil"])
    out.append(f'<g opacity="0.55" transform="translate(0.6 0.9)" filter="url(#foil-sh)">'
               + re.sub(r'(stroke|fill)="' + re.escape(FOIL) + '"', r'\1="#061413"', foil) + "</g>")
    out.append(gild(foil, gid))
    return "".join(out)


def panel_mock(res: dict, w: float, h: float, *, pad: float = 0.0, bg: str = "#E6E0D3") -> str:
    gid = "g1"
    defs = FILTERS + gradient(gid, 0, 0, w * 0.55, h * 0.42)
    body = panel_art(res, w, h, gid)
    vw, vh = w + 2 * pad, h + 2 * pad
    bgr = f'<rect x="{fmt(-pad)}" y="{fmt(-pad)}" width="{fmt(vw)}" height="{fmt(vh)}" fill="{bg}"/>' if pad else ""
    sh = (f'<rect x="6" y="12" width="{fmt(w)}" height="{fmt(h)}" rx="4" fill="#000" fill-opacity="0.35" '
          f'filter="url(#soft2)"/>' if pad else "")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(vw)}" height="{fmt(vh)}" '
            f'viewBox="{fmt(-pad)} {fmt(-pad)} {fmt(vw)} {fmt(vh)}"><defs>{defs}</defs>{bgr}{sh}{body}</svg>')


# =============================================================================
# presentation: the closed box in 3/4 view
# =============================================================================
def _seal_parts():
    """(foil svg, die d, size) read from tuck/SEAL.svg (another finisher's
    file; read only)."""
    p = K.TUCK / "SEAL.svg"
    if not p.exists():
        return None
    root = ET.fromstring(p.read_text())
    ns = "{http://www.w3.org/2000/svg}"
    foil = die = None
    for g in root.iter(ns + "g"):
        if g.get("id") == "foil":
            foil = "".join(ET.tostring(ch, encoding="unicode").replace("ns0:", "").replace(":ns0", "")
                           for ch in g)
        if g.get("id") == "dieline":
            for ch in g.iter(ns + "path"):
                die = ch.get("d")
    size = float(root.get("width"))
    return foil, die, size


MOCK_CARDS = ("BACK", "AS")        # the deck renders the presentation mock embeds (build/png, 750 px)


def mock_inputs() -> list[dict]:
    """The card renders the presentation embeds, each checked against its
    art sources (art/<ID>.py + art/_<id>_*.py): a render older than any of
    its sources is STALE — the mock would show a card the deck no longer
    has (run ``python -m deck.build <ID>`` first, then this build)."""
    import hashlib
    import time as _t
    rows = []
    for cid in MOCK_CARDS:
        png = K.ROOT / "build" / "png" / f"{cid}.png"
        srcs = [q for q in [K.ROOT / "art" / f"{cid}.py", *sorted((K.ROOT / "art").glob(f"_{cid.lower()}_*.py"))]
                if q.exists()]
        newest = max(srcs, key=lambda q: q.stat().st_mtime) if srcs else None
        fmt_t = lambda t: _t.strftime("%m-%d %H:%M:%S", _t.localtime(t))
        row = dict(card=cid, png=str(png.relative_to(K.ROOT)), exists=png.exists())
        if png.exists():
            row.update(png_mtime=fmt_t(png.stat().st_mtime),
                       sha1=hashlib.sha1(png.read_bytes()).hexdigest()[:12])
        if newest is not None:
            row.update(newest_src=newest.name, src_mtime=fmt_t(newest.stat().st_mtime))
        row["fresh"] = bool(png.exists() and (newest is None or png.stat().st_mtime >= newest.stat().st_mtime))
        rows.append(row)
    return rows


def _png_uri(path: Path) -> str | None:
    if not path.exists():
        return None
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode()


def presentation(front: dict, back: dict, panels: dict, *, yaw=30.0, pitch=16.0, s=1.0) -> str:
    th, ph = math.radians(yaw), math.radians(pitch)
    ct, st, cp, sp = math.cos(th), math.sin(th), math.cos(ph), math.sin(ph)
    PW, PH, D = K.PW, K.PH, K.DEPTH
    W, H = 2600.0, 1760.0
    ox, oy = 560.0, 360.0                          # screen position of the front's top-left corner

    def M(a, b, c, d, e, f):
        return f"matrix({a * s:.5f} {b * s:.5f} {c * s:.5f} {d * s:.5f} {ox + e * s:.3f} {oy + f * s:.3f})"
    m_front = M(ct, st * sp, 0, cp, 0, 0)
    m_side = M(st, -ct * sp, 0, cp, PW * ct, PW * st * sp)
    m_top = M(ct, st * sp, -st, ct * sp, D * st, -D * ct * sp)

    defs = FILTERS
    defs += gradient("gf", 0, 0, PW * 0.6, PH * 0.45)
    defs += gradient("gs", 0, -200, D * 1.6, PH * 0.5)
    defs += gradient("gt", 0, 0, PW * 0.5, D * 1.4)
    defs += ('<linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#EDE8DD"/>'
             '<stop offset="1" stop-color="#D6CDBB"/></linearGradient>')
    defs += ('<radialGradient id="pool" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#000" '
             'stop-opacity="0.45"/><stop offset="1" stop-color="#000" stop-opacity="0"/></radialGradient>')
    out = [f'<rect width="{fmt(W)}" height="{fmt(H)}" fill="url(#bg)"/>']

    # cards to the right of the box, fanned, with shadows
    for name, dx, dy, rot in zip(MOCK_CARDS, (1640, 1520), (470, 430), (9.0, -4.0)):
        uri = _png_uri(K.ROOT / "build" / "png" / f"{name}.png")
        if not uri:
            continue
        out.append(f'<g transform="translate({dx} {dy}) rotate({rot} 375 525) scale(0.98)">'
                   f'<rect x="10" y="22" width="750" height="1050" rx="37.5" fill="#000" fill-opacity="0.28" '
                   f'filter="url(#soft2)"/>'
                   f'<clipPath id="cc{dx}"><rect width="750" height="1050" rx="37.5"/></clipPath>'
                   f'<image href="{uri}" width="750" height="1050" clip-path="url(#cc{dx})"/></g>')

    # the box's contact shadow
    fy0 = oy + (PH * cp) * s
    out.append(f'<ellipse cx="{ox + PW * ct * s * 0.62:.1f}" cy="{fy0 + 18:.1f}" rx="{PW * 0.78 * s:.1f}" '
               f'ry="{70 * s:.1f}" fill="url(#pool)"/>')

    def face(mat, content, shade, clip_w, clip_h, cid):
        return (f'<g transform="{mat}"><clipPath id="{cid}"><rect width="{fmt(clip_w)}" height="{fmt(clip_h)}"/>'
                f'</clipPath><g clip-path="url(#{cid})">{content}'
                f'<rect width="{fmt(clip_w)}" height="{fmt(clip_h)}" fill="{shade[0]}" fill-opacity="{shade[1]}"/>'
                f'</g></g>')
    side_res = dict(foil=panels["side_a"], emboss=[])
    top_res = dict(foil=panels["top"], emboss=[])
    out.append(face(m_side, panel_art(side_res, D, PH, "gs"), ("#000", 0.34), D, PH, "cs"))
    out.append(face(m_front, panel_art(front, PW, PH, "gf"), ("#fff", 0.0), PW, PH, "cf"))
    out.append(face(m_top, panel_art(top_res, PW, D, "gt"), ("#fff", 0.05), PW, D, "ct"))
    out.append(f'<g transform="{m_front}"><path d="M0 0H{fmt(PW)}" stroke="#fff" stroke-opacity="0.25" '
               f'stroke-width="1.5"/><path d="M{fmt(PW)} 0V{fmt(PH)}" stroke="#000" stroke-opacity="0.25" '
               f'stroke-width="2"/></g>')

    # the seal across the lid's closure: the lid tucks in behind the BACK, so the seal is laid over the
    # back's top edge — its lower half lies on the top face (the upper half runs down the back, unseen)
    sp_ = _seal_parts()
    if sp_:
        sfoil, die, size = sp_
        c = size / 2
        sfoil_g = gild(sfoil, "gseal")
        defs += gradient("gseal", 0, 0, size * 0.7, size * 0.5)
        body = (f'<path d="{die}" fill="{T.RED}"/><clipPath id="sdie"><path d="{die}"/></clipPath>'
                f'<g clip-path="url(#sdie)">{sfoil_g}</g>')
        out.append(f'<g transform="{m_top}"><clipPath id="st"><rect width="{fmt(PW)}" height="{fmt(D)}"/></clipPath>'
                   f'<g clip-path="url(#st)"><g transform="translate({fmt(PW / 2 - c)} {fmt(-c)})">'
                   f'<path d="{die}" fill="#000" fill-opacity="0.35" transform="translate(1.5 3)" '
                   f'filter="url(#soft2)"/>{body}'
                   f'<rect x="0" y="0" width="{fmt(size)}" height="{fmt(size)}" fill="#fff" fill-opacity="0.06" '
                   f'clip-path="url(#sdie)"/></g></g></g>')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{fmt(W)}" height="{fmt(H)}" '
            f'viewBox="0 0 {fmt(W)} {fmt(H)}"><defs>{defs}</defs>{"".join(out)}</svg>')
