"""Independent RASTER measurement of the corner wheels (verifier 2-0).
Render ONE plate of an output SVG in a corner window at SCALE x with rsvg-convert,
find the wheel as the ~54 px-square connected component (knockout for the jade plate,
foil for the tuck plates), then along the row and column through the wheel's rendered
centre list every run from the window's outer edge to the wheel (lengths by alpha
coverage, i.e. sub-pixel)."""
import re, subprocess, sys, json, os
import numpy as np
from PIL import Image
from scipy import ndimage

SCALE = 10
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE + "/raster"
os.makedirs(OUT, exist_ok=True)
ROOT = "/home/luke/Projects/design/san-marcos-deck"


def plate_svg(path, keep, vb):
    s = open(path).read()
    head, rest = s.split("<g id=", 1)
    rest = "<g id=" + rest
    groups = re.findall(r'(<g id="(\w+)".*?</g>)\s*(?=<g id="|</svg>)', rest, flags=re.S)
    names = [n for _, n in groups]
    body = "".join(g for g, n in groups if n == keep)
    assert keep in names, (keep, names)
    head = re.sub(r'viewBox="[^"]*"', 'viewBox="%g %g %g %g"' % vb, head, count=1)
    head = re.sub(r'(<svg[^>]*?)\swidth="[^"]*"', r'\1 width="%d"' % round(vb[2] * SCALE), head, count=1)
    head = re.sub(r'(<svg[^>]*?)\sheight="[^"]*"', r'\1 height="%d"' % round(vb[3] * SCALE), head, count=1)
    # keep <defs> (clip paths) that live in head
    return head + body + "\n</svg>\n", names


def render(path, keep, vb, tag):
    svg, names = plate_svg(path, keep, vb)
    fn = f"{OUT}/{tag}.svg"
    open(fn, "w").write(svg)
    png = f"{OUT}/{tag}.png"
    subprocess.run(["rsvg-convert", "-o", png, fn], check=True)
    return np.asarray(Image.open(png).convert("RGBA"))[:, :, 3].astype(float) / 255.0


def runs(v):
    """alpha profile -> [(on, start_u, end_u, coverage_len_u)]; on = alpha>0.5."""
    b = v > 0.5
    segs = []
    i, n = 0, len(v)
    while i < n:
        j = i
        while j < n and b[j] == b[i]:
            j += 1
        segs.append((bool(b[i]), int(i), int(j)))
        i = j
    res = []
    for on, i, j in segs:
        cov = v if on else 1 - v
        L = cov[i:j].sum()
        if i > 0:
            L += cov[i - 1]          # partial share in the neighbour pixel before
        if j < n:
            L += cov[j]              # and after
        res.append((bool(on), i / SCALE, j / SCALE, round(float(L) / SCALE, 3)))
    return res


def wheel(mask, vb):
    lab, n = ndimage.label(mask)
    sl = ndimage.find_objects(lab)
    cands = []
    for k, s in enumerate(sl, 1):
        h = (s[0].stop - s[0].start) / SCALE
        w = (s[1].stop - s[1].start) / SCALE
        if 50 < w < 60 and 50 < h < 60:
            cands.append((k, s, w, h))
    assert len(cands) == 1, [(c[2], c[3]) for c in cands]
    k, s, w, h = cands[0]
    comp = lab == k
    ys, xs = np.nonzero(comp)
    x0, x1 = xs.min() / SCALE + vb[0], (xs.max() + 1) / SCALE + vb[0]
    y0, y1 = ys.min() / SCALE + vb[1], (ys.max() + 1) / SCALE + vb[1]
    return comp, (x0, y0, x1, y1)


def measure(path, keep, vb, tag, knockout, cn):
    a = render(path, keep, vb, tag)
    mask = (a < 0.5) if knockout else (a > 0.5)
    comp, bb = wheel(mask, vb)
    cx, cy = (bb[0] + bb[2]) / 2, (bb[1] + bb[3]) / 2
    # the side toward the card edge
    left = cn in ("TL", "BL")
    top = cn in ("TL", "TR")
    ri = int((cy - vb[1]) * SCALE)          # row through the centre
    ci = int((cx - vb[0]) * SCALE)
    row = a[ri, :ci] if left else a[ri, ci:][::-1]
    col = a[:ri, ci] if top else a[ri:, ci][::-1]
    # profile = "ink" of the plate: foil alpha, or jade alpha for the back (runs report both kinds)
    return dict(bbox=[round(float(v), 2) for v in bb], centre=(round(float(cx), 2), round(float(cy), 2)),
                size=(round(float(bb[2] - bb[0]), 2), round(float(bb[3] - bb[1]), 2)),
                row=runs(row), col=runs(col), left=bool(left), top=bool(top))


def windows(ox, oy, W, H, s=140):
    return dict(TL=(ox, oy, s, s), TR=(ox + W - s, oy, s, s), BL=(ox, oy + H - s, s, s), BR=(ox + W - s, oy + H - s, s, s))


INSTANCES = [
    ("card-back", "cards/BACK.svg", "jade", True, (0, 0, 750, 1050)),
    ("card-back-white", "build/white/cards/BACK.svg", "jade", True, (0, 0, 750, 1050)),
    ("tuck-front", "tuck/TUCK-FRONT.svg", "foil", False, (0, 0, 769, 1069)),
    ("tuck-back", "tuck/TUCK-BACK.svg", "foil", False, (0, 0, 769, 1069)),
    ("flat-front", "tuck/TUCK-FLAT.svg", "foil", False, (225, 405, 769, 1069)),
    ("flat-back", "tuck/TUCK-FLAT.svg", "foil", False, (1219, 405, 769, 1069)),
]

if __name__ == "__main__":
    root = sys.argv[1] if len(sys.argv) > 1 else ROOT
    pref = sys.argv[2] if len(sys.argv) > 2 else "now"
    res = {}
    for name, rel, plate, ko, (ox, oy, W, H) in INSTANCES:
        p = os.path.join(root, rel)
        if not os.path.exists(p):
            continue
        for cn, vb in windows(ox, oy, W, H).items():
            r = measure(p, plate, vb, f"{pref}-{name}-{cn}", ko, cn)
            # local coords relative to the panel origin
            r["bbox_local"] = [round(r["bbox"][0] - ox, 2), round(r["bbox"][1] - oy, 2),
                               round(r["bbox"][2] - ox, 2), round(r["bbox"][3] - oy, 2)]
            res[f"{name}/{cn}"] = r
    json.dump(res, open(f"{HERE}/rmeas-{pref}.json", "w"), indent=1, default=lambda o: bool(o) if isinstance(o, np.bool_) else float(o))
    for k, r in res.items():
        def fmt(rs):
            return " ".join(("%s%.2f" % ("#" if on else "_", L)) for on, a, b, L in rs[:8])
        print(f"{k:22s} bbox_local={r['bbox_local']} size={r['size']}")
        print(f"{'':22s} row(from side): {fmt(r['row'])}")
        print(f"{'':22s} col(from top/bot): {fmt(r['col'])}")
