"""Raster verification (8x) of the corner-wheel gaps from the rendered output.

Each corner is rendered with rsvg-convert through a cropped viewBox at 8 px / px.
Per pixel, "ink coverage" t in [0,1] is the projection of the colour between the
ground colour and the ink colour (card back: jade = ground in the flood, the
wheel is a paper HOLE; tuck: board ground, foil ink).  Along the row / column
through the wheel centre we integrate the ground run between the container edge
and the wheel, and also find the subpixel 50 % edges.
"""
import os, re, subprocess, sys, json
import numpy as np
from PIL import Image

ROOT = "/home/luke/Projects/design/san-marcos-deck"
OUT = os.path.join(ROOT, "build/review/corr-verify-wheels-1-0/raster")
os.makedirs(OUT, exist_ok=True)
S = 8


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float)


def render_crop(svg, x0, y0, w, h, tag):
    s = open(svg).read()
    s2 = re.sub(r'<svg([^>]*?)width="[^"]*"([^>]*?)height="[^"]*"([^>]*?)viewBox="[^"]*"',
                lambda m: '<svg%swidth="%d"%sheight="%d"%sviewBox="%g %g %g %g"' % (m.group(1), w * S, m.group(2), h * S,
                                                                               m.group(3), x0, y0, w, h), s, count=1)
    tmp = os.path.join(OUT, tag + ".svg")
    open(tmp, "w").write(s2)
    png = os.path.join(OUT, tag + ".png")
    subprocess.run(["rsvg-convert", "-o", png, tmp], check=True)
    os.remove(tmp)
    return np.asarray(Image.open(png).convert("RGB"), float)


def coverage(img, ground, ink):
    g, k = hexrgb(ground), hexrgb(ink)
    v = k - g
    t = ((img - g) @ v) / (v @ v)
    return np.clip(t, 0, 1)


def edges_1d(prof):
    """subpixel 0.5 crossings of a 1-D profile (in pixel units, pixel centres at i+0.5)"""
    xs = []
    for i in range(len(prof) - 1):
        a, b = prof[i], prof[i + 1]
        if (a - 0.5) * (b - 0.5) < 0:
            xs.append(i + 0.5 + (0.5 - a) / (b - a))
    return xs


def measure(svg, corner, W, H, cx, cy, ground, ink, ox=0.0, oy=0.0, tag="", pad=12, span=110):
    """corner: TL/TR/BL/BR; (cx, cy): the wheel centre in panel coords (from the vector pass, only to pick
    the scan line); container edges at 0/W and 0/H in panel coords (+ox, oy).  Returns the ground run from
    the container edge to the wheel along the scan lines through the wheel centre, and the 0.5 edges."""
    # crop window covering the corner with some outside margin
    x0 = (ox - pad) if corner[1] == "L" else (ox + W - span)
    y0 = (oy - pad) if corner[0] == "T" else (oy + H - span)
    img = render_crop(svg, x0, y0, span + pad, span + pad, tag)
    return img, x0, y0


if __name__ == "__main__":
    pass


def runs_along(prof):
    """0.5 crossings of the ink-coverage profile (pixel units)."""
    return edges_1d(prof)


def scan(svg, W, H, c_tl, ground, ink, ox=0.0, oy=0.0, label="", alpha_edge=True, extra=None):
    """For each corner: render a 8x crop, take the row through the wheel centre and the column through it,
    and report (a) the wheel's outer 50 % edge measured from the container edge, (b) where the container
    edge itself was found in the raster (alpha edge of the panel / the flood edge)."""
    res = {}
    cx_tl, cy_tl = c_tl
    for k in ("TL", "TR", "BL", "BR"):
        cx = cx_tl if k[1] == "L" else W - cx_tl
        cy = cy_tl if k[0] == "T" else H - cy_tl
        pad, span = 12, 110
        x0 = (ox - pad) if k[1] == "L" else (ox + W - span)
        y0 = (oy - pad) if k[0] == "T" else (oy + H - span)
        n = span + pad
        s = open(svg).read()
        s2 = re.sub(r'<svg([^>]*?)width="[^"]*"([^>]*?)height="[^"]*"([^>]*?)viewBox="[^"]*"',
                    lambda m: '<svg%swidth="%d"%sheight="%d"%sviewBox="%g %g %g %g"' % (
                        m.group(1), n * S, m.group(2), n * S, m.group(3), x0, y0, n, n), s, count=1)
        tag = f"{label}-{k}"
        tmp = os.path.join(OUT, tag + ".svg")
        open(tmp, "w").write(s2)
        png = os.path.join(OUT, tag + ".png")
        subprocess.run(["rsvg-convert", "-o", png, tmp], check=True)
        os.remove(tmp)
        rgba = np.asarray(Image.open(png).convert("RGBA"), float)
        rgb, A = rgba[..., :3], rgba[..., 3] / 255.0
        t = coverage(rgb, ground, ink)
        # pixel index of the centre
        ic = (cy - oy + oy - y0) * S if False else (cy + oy - y0) * S
        jc = (cx + ox - x0) * S
        r0, r1 = int(ic) - 2, int(ic) + 3
        c0, c1 = int(jc) - 2, int(jc) + 3
        row = t[r0:r1].mean(axis=0)
        col = t[:, c0:c1].mean(axis=1)
        arow = A[r0:r1].mean(axis=0)
        acol = A[:, c0:c1].mean(axis=1)
        out = {}
        for axis, prof, aprof, lo in (("side", row, arow, x0), ("tb", col, acol, y0)):
            near = k[1] == "L" if axis == "side" else k[0] == "T"
            if not near:
                prof, aprof = prof[::-1], aprof[::-1]
            e = [v / S for v in edges_1d(prof)]
            ea = [v / S for v in edges_1d(aprof)]
            out[axis] = dict(ink_edges=[round(v, 3) for v in e[:8]], alpha_edges=[round(v, 3) for v in ea[:2]])
        res[k] = out
    return res


if __name__ == "__main__":
    os.chdir(ROOT)
    allres = {}
    # ---- card back: jade flood (ink = jade) on paper; the wheel is a paper hole ----
    r = scan("cards/BACK.svg", 750, 1050, (71.5, 71.5), "#F4EFE3", "#1D5A55", label="back")
    print("CARD BACK (lime), jade-coverage 0.5 crossings from the crop's outer edge (crop starts 12 px outside"
          " the card edge for near corners)")
    for k, v in r.items():
        for ax in ("side", "tb"):
            e = v[ax]["ink_edges"]
            # crop starts at -12 (near) → card coords = e - 12 ; far corners: crop reversed from W/H+? handle below
            print(f"  {k} {ax}: edges {e}")
    allres["back"] = r
    r = scan("build/white/cards/BACK.svg", 750, 1050, (71.5, 71.5), "#FFFFFF", "#1D5A55", label="backwhite")
    allres["back_white"] = r
    for k, v in r.items():
        print("  white", k, v["side"]["ink_edges"], v["tb"]["ink_edges"])
    json.dump(allres, open(os.path.join(OUT, "raster.json"), "w"), indent=1)
