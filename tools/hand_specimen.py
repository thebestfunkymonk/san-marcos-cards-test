"""Hand specimen sheet (legacy hands and the shared five-digit hand).

    .venv/bin/python tools/hand_specimen.py [--out build/review/v3-hands] [--courts] [--only ROW ...]

Draws the established kit poses and the shared ``hand5`` poses — grip (back
and palm view, at several shaft angles, the
'behind' thumb, a bar held from above and below), pinch (stems at several
angles), cup (orb from below), open hand (back,
palm, spread, curled) and the hand merged into its sleeve — for BOTH
chiralities and THREE sizes (hand length 70 / 85 / 100 px: ``size`` =
``courtkit.hand_size(face)``, a face's chin-to-hairline). Each cell is a
stand-alone scene on a jade ground (so every hand edge is an interior MEDIUM
edge, as on the card), with a gold stand-in for what the hand holds (no halo:
the attribute's contour runs under the fingers) and a red sleeve with a
coloured cuff the wrist is tucked into (``Hand.add_to`` or one merged Part).

Writes <out>/specimen.png (per cell: 3× on top, card size below),
<out>/specimen_1x.png (card size only, one row per pose) and
<out>/specimen_calls.json. ``--courts`` also writes <out>/courts/specimen.png
and specimen_1x.png: every hand item of the twelve courts (kit hands and the
court-local helpers alike), cropped from each court's own composed art.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import tempfile
import warnings

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import shapely.affinity  # noqa: E402
sys.path.insert(0, ROOT)

import numpy as np  # noqa: E402

from deck import tokens as T  # noqa: E402
from deck import courtkit as K  # noqa: E402

COURTS = ["KS", "QS", "JS", "KH", "QH", "JH", "KC", "QC", "JC", "KD", "QD", "JD"]
CELL = 150.0          # cell size, card px
SIZES = (70.0, 85.0, 100.0)
FONT = next((p for p in ("/usr/share/fonts/noto/NotoSans-Regular.ttf", os.path.join(ROOT, "fonts", "BarlowCondensed-Medium.ttf"))
             if os.path.isfile(p)), "Helvetica")


def _pt(v):
    return np.array([float(v[0]), float(v[1])])


# ---------------------------------------------------------------------------
# the specimen calls
# ---------------------------------------------------------------------------
def _grip(size, chir, *, axis=-90.0, shaft=18.0, view=None, thumb="over", bend=40.0):
    back = +1 if chir == "L" else -1
    hand = chir if view != "palm" else ("R" if chir == "L" else "L")
    w = tuple(K.fist_wrist((0.0, 0.0), axis, bend=bend, shaft_w=shaft, back=back, size=size))
    return {"fn": "fist", "args": ((0.0, 0.0), axis),
            "kw": {"shaft_w": shaft, "back": back, "wrist": w, "size": size, "hand": hand, "thumb": thumb},
            "obj": ("staff", axis, shaft)}


def _pinch(size, chir, *, axis=-90.0, stem=5.0, obj="stem"):
    back = +1 if chir == "L" else -1
    w = tuple(K.fist_wrist((0.0, 0.0), axis, bend=45.0, shaft_w=stem, back=back, size=size, grip="pinch"))
    return {"fn": "pinch", "args": ((0.0, 0.0), axis),
            "kw": {"stem_w": stem, "back": back, "wrist": w, "size": size},
            "obj": (obj, axis, stem)}


def _cup(size, chir, r=None):
    r = r if r is not None else 0.38 * size
    side = -1 if chir == "R" else +1
    return {"fn": "cup", "args": ((0.0, -0.25 * size), r),
            "kw": {"side": side, "wrist": (side * 0.45 * r, -0.25 * size + 1.80 * r), "size": size},
            "obj": ("orb", r)}


def _open(size, chir, *, view="back", angle=-60.0, spread=0.0, curl=0.0):
    a = math.radians(angle)
    at = (-0.42 * size * math.cos(a), -0.42 * size * math.sin(a))
    return {"fn": "open_hand", "args": (at, angle),
            "kw": {"size": size, "hand": chir, "view": view, "spread": spread, "curl": curl},
            "obj": None}


def _hand5(size, chir, pose, *, view="back", angle=-90.0, curl=0.0, spread=0.0, grip_w=22.0, cues=True):
    if pose == "wrap":
        at = (0.0, 0.0)
        obj = ("staff", angle, grip_w)
    else:
        at = (0.0, 0.0)
        obj = ("orb-meta", grip_w) if pose == "cup" else (
            ("flat-meta", grip_w, 22.0) if pose == "hold_flat" else None)
    return {"fn": "hand5", "args": (at, angle, pose),
            "kw": {"size": size, "hand": chir, "view": view, "curl": curl, "spread": spread,
                   "grip_w": grip_w, "cues": cues},
            "obj": obj}


# Per pose: the angle that puts the fingers roughly upward / across for a frontal figure, and the
# held-object width. ``angle`` is the wrist-to-fingertip direction, except wrap where it is the
# shaft axis toward the thumb end (fingers run perpendicular to it).
MATRIX_POSES = (("wrap", -90.0, 18.0), ("cup", -90.0, 62.0), ("rest", -20.0, 22.0),
                ("hold_flat", -75.0, 28.0), ("open", -90.0, 22.0))


def matrix_rows(size=85.0):
    """One row per pose; four cells each: L back, R back, L palm, R palm (the named anatomical hand
    seen from the named side). Labels carry hand, view, pose and angle."""
    R = []
    for pose, angle, grip in MATRIX_POSES:
        R.append((f"anatomy matrix · {pose} · angle {angle:g}° · L/R × back/palm",
                  [dict(_hand5(size, c, pose, view=v, angle=angle, grip_w=grip, curl=6.0),
                        label=f"{c} · {v} · {pose} · {angle:g}°")
                   for v in ("back", "palm") for c in ("L", "R")]))
    return R


def rows():
    """[(row title, [call, ...])] — every pose, both chiralities, three sizes."""
    R = []

    def sweep(title, make, **kw):
        R.append((title, [dict(make(s, c, **kw), label=f"{c} size {s:g}") for c in ("L", "R") for s in SIZES]))

    sweep("grip, back view (thumb over the fist), vertical staff 18", _grip)
    sweep("grip, palm view (hand= the other chirality)", _grip, view="palm")
    R.append(("grip at other angles (size 85)",
              [dict(_grip(85.0, c, axis=ax, shaft=sh, bend=b), label=f"{c} axis {ax:g} shaft {sh:g}")
               for c in ("L", "R") for ax, sh, b in ((-60.0, 14.0, 35.0), (-120.0, 22.0, 40.0), (180.0, 10.0, 40.0),
                                                      (0.0, 10.0, 40.0))]))
    sweep("grip, thumb='behind' (tip round the far side)", _grip, thumb="behind")
    sweep("grip, thin rod 8 (key, sceptre stem)", _grip, shaft=8.0)
    sweep("pinch: a stem between thumb and index", _pinch)
    R.append(("pinch at other angles (size 85): tilted stems",
              [dict(_pinch(85.0, c, axis=ax, stem=st), label=f"{c} axis {ax:g} stem {st:g}")
               for c in ("L", "R") for ax, st in ((-45.0, 5.0), (-70.0, 4.2), (-110.0, 6.0))]))
    sweep("cup: orb from below", _cup)
    sweep("open hand, back view, together", _open)
    sweep("open hand, palm view, together", _open, view="palm")
    sweep("open hand, back view, spread 7°", _open, spread=7.0, angle=-75.0)
    sweep("open hand, palm view, curled 25° (on the chest)", _open, view="palm", curl=25.0, angle=-30.0)
    R.append(("hand + sleeve as ONE outline (Hand.with_sleeve), size 85",
              [dict(_grip(85.0, c), label=f"{c} grip + sleeve", merge=True) for c in ("L", "R")]
              + [dict(_open(85.0, c, angle=-70.0), label=f"{c} open + sleeve", merge=True) for c in ("L", "R")]
              + [dict(_cup(85.0, c), label=f"{c} cup + sleeve", merge=True) for c in ("L", "R")]))

    def hand5_row(title, pose, *, view="back", angle=-90.0, curl=0.0, spread=0.0, grip_w=22.0,
                  sizes=SIZES):
        angles = angle if isinstance(angle, (tuple, list)) else (angle,)
        R.append((title, [dict(_hand5(s, c, pose, view=view, angle=a, curl=curl, spread=spread, grip_w=grip_w),
                               label=f"{c} size {s:g} · {a:g}°")
                         for c in ("L", "R") for s in sizes for a in angles]))

    hand5_row("hand5 wrap · back · vertical staff · five fingers + side thumb", "wrap", view="back",
              grip_w=18.0, sizes=SIZES)
    hand5_row("hand5 wrap · palm · vertical staff · short thumb beside index", "wrap", view="palm",
              grip_w=18.0, sizes=SIZES)
    hand5_row("hand5 wrap · back · staff at six angles", "wrap", view="back",
              angle=(-60.0, -90.0, -120.0, 0.0, 75.0, 180.0), grip_w=18.0, sizes=(85.0,))
    hand5_row("hand5 wrap · palm · horizontal and inverted staff", "wrap", view="palm",
              angle=(0.0, 180.0), grip_w=18.0, sizes=(85.0,))
    hand5_row("hand5 cup · palm · scalloped fingers follow orb rim", "cup", view="palm",
              grip_w=62.0)
    hand5_row("hand5 cup · back · scalloped fingers follow orb rim", "cup", view="back",
              grip_w=62.0)
    hand5_row("hand5 rest · back · relaxed fingers laid across the body", "rest", view="back",
              angle=0.0, curl=10.0)
    hand5_row("hand5 rest · palm · relaxed fingers laid across the body", "rest", view="palm",
              angle=0.0, curl=10.0)
    hand5_row("hand5 hold_flat · palm · scroll held under the fingers", "hold_flat", view="palm",
              angle=-75.0, curl=8.0, grip_w=28.0)
    hand5_row("hand5 hold_flat · back · scroll held under the fingers", "hold_flat", view="back",
              angle=-75.0, curl=8.0, grip_w=28.0)
    hand5_row("hand5 open · back · fingers together", "open", view="back", spread=2.0)
    hand5_row("hand5 open · palm · fingers spread", "open", view="palm", spread=12.0, curl=4.0)
    R.append(("hand5 + sleeve · one merged outer outline and cuff colour edge",
              [dict(_hand5(85.0, c, pose, view=v,
                           angle={"wrap": -90.0, "cup": -90.0, "rest": 0.0,
                                  "hold_flat": -75.0, "open": -90.0}[pose],
                           curl=8.0, grip_w=18.0),
                    label=f"{pose} · {c} · {v}", merge=True)
               for pose, v in (("wrap", "back"), ("cup", "palm"), ("rest", "back"),
                               ("hold_flat", "palm"), ("open", "back"))
               for c in ("L", "R")]))
    for pose in ("wrap", "cup", "rest", "hold_flat", "open"):
        for view in ("back", "palm"):
            hand5_row(f"hand5 {pose} · {view} · spread 12° + curl 4°", pose,
                      view=view, spread=12.0, curl=4.0,
                      grip_w=62.0 if pose == "cup" else 28.0)
    return R


# ---------------------------------------------------------------------------
# the courts' own hands (optional)
# ---------------------------------------------------------------------------
def court_cells(ids):
    """[(label, svg)]: every hand item of each court ('hand…' items of the
    scenes its ``build()`` composes: kit hands AND court-local ones), cropped
    from the court's own printed art, so the court-local hand helpers show."""
    from deck import build as B
    seen, out = [], []
    orig = K.Scene.compose

    def compose(self, *a, **kw):
        seen.append(self)
        return orig(self, *a, **kw)

    K.Scene.compose = compose
    try:
        for pid in ids:
            seen.clear()
            try:
                mod = B.load_art(pid)
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    layers = mod.build()
            except Exception as e:  # noqa: BLE001
                print(f"[courts] {pid}: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            body = "".join(f'<g id="{k}">{"".join(v)}</g>' for k, v in layers.items())
            names = set()
            for sc in seen:
                for it in sc.items:
                    nm = it.name
                    if (not nm.lower().startswith("hand") or "~" in nm or nm.endswith("-thumb") or nm in names
                            or it.occ is None or it.occ.is_empty):
                        continue
                    names.add(nm)
                    b = it.occ.bounds
                    ctr = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
                    out.append((f"{pid} {nm}", _svg_body(body, ctr, CELL)))
    finally:
        K.Scene.compose = orig
    return out


# ---------------------------------------------------------------------------
# drawing
# ---------------------------------------------------------------------------
def _scene(c):
    fn, a, kw = c["fn"], list(c["args"]), dict(c["kw"])
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        hand = getattr(K, fn)(*a, **kw)
    sc = K.Scene()
    ground = K.box(-2000, -2000, 3000, 3000)
    sc.part("ground", K.Part(ground, K.fill(ground, K.JADE), K.C.Frag(), {}))
    obj = c.get("obj")
    at = _pt(a[0]) if a else _pt(kw.get("at", (0, 0)))
    if obj and obj[0] in ("staff", "stem"):
        d = np.array([math.cos(math.radians(obj[1])), math.sin(math.radians(obj[1]))])
        lo = 75.0 if obj[0] == "staff" else 0.32 * float(kw.get("size") or 85.0)   # a stem runs on under the pinch
        sc.part("shaft", K.staff(tuple(at - d * lo), tuple(at + d * 75.0), obj[2]))
    elif obj and obj[0] == "orb":
        sc.part("orb", K.orb(tuple(at), obj[1]))
    elif obj and obj[0] == "orb-meta":
        sc.part("orb", K.orb(tuple(hand.hand.meta["object_center"]), hand.hand.meta["object_radius"]))
    elif obj and obj[0] == "flat-meta":
        center = tuple(hand.hand.meta["object_center"])
        width = hand.hand.meta["object_width"]
        height = hand.hand.meta["object_height"]
        slab = K.box(center[0] - width / 2, center[1] - height / 2,
                     center[0] + width / 2, center[1] + height / 2)
        slab = shapely.affinity.rotate(slab, float(a[1]), origin=center)
        sc.part("scroll", K.Part(slab, K.fill(slab, K.GOLD), K.outline(slab)))
    W = _pt(hand.wrist)
    u = _unit(hand.wrist_dir if hand.wrist_dir is not None else np.array([0.0, 1.0]))
    spec = K.SleeveSpec(base=tuple(W + u * 95.0), wrist=tuple(W), sag=0.0, width=1.5 * hand.wrist_w + 14.0,
                        wrist_w=hand.wrist_w + 10.0, cuff=11.0, folds=0, color=K.RED, cuff_color=K.JADE)
    if c.get("merge"):
        sl, cf = K.sleeve(K.SleeveSpec(**{**spec.__dict__, "wrist": tuple(W + u * 13.0),
                                          "cuff": 26.0, "cuff_color": K.GOLD, "wrist_w": hand.wrist_w + 6.0,
                                          "width": hand.wrist_w + 16.0}))
        cuff_edge = cf.shape.buffer(1.5).intersection(sl.shape)
        sleeve_fills = K.fill(sl.shape.difference(cuff_edge), K.RED) + K.fill(cuff_edge, K.GOLD)
        sleeve = K.Part(sl.shape.union(cf.shape), sleeve_fills,
                        sl.lines.select(lambda mark: mark.role != "outline"))
        sc.part("arm+hand", hand.with_sleeve(sleeve))
    else:
        sl, cf = K.sleeve(spec)
        sc.part("sleeve", sl)
        sc.part("cuff", cf)
        hand.add_to(sc, "hand", halo=0.0)
    focus = hand.hand.shape
    for item in sc.items:
        if item.name in {"orb", "scroll"} and item.occ is not None:
            focus = focus.union(item.occ)
    b = focus.bounds
    ctr = ((b[0] + b[2]) / 2, (b[1] + b[3]) / 2)
    return sc, ctr


def _unit(v):
    v = np.asarray(v, float)
    n = float(np.hypot(*v))
    return v / n if n > 1e-9 else np.array([0.0, 1.0])


def _svg(sc, ctr, size):
    body = "".join(f'<g id="{k}">{"".join(v)}</g>' for k, v in sc.layers().items())
    return _svg_body(body, ctr, size)


def _svg_body(body, ctr, size):
    x0, y0 = ctr[0] - size / 2, ctr[1] - size / 2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0:.2f} {y0:.2f} {size} {size}" '
            f'width="{size}" height="{size}"><rect x="{x0 - 5:.2f}" y="{y0 - 5:.2f}" width="{size + 10}" '
            f'height="{size + 10}" fill="{T.PAPER}"/>{body}</svg>')


def _render(svg, out, w):
    with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as fh:
        fh.write(svg)
        p = fh.name
    subprocess.run(["rsvg-convert", "-w", str(int(w)), p, "-o", out], check=True)
    os.remove(p)


def _font(px):
    from PIL import ImageFont
    try:
        return ImageFont.truetype(FONT, px)
    except Exception:  # noqa: BLE001
        return ImageFont.load_default()


def main(argv=None):
    from PIL import Image, ImageDraw
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=os.path.join(ROOT, "build", "review", "v3-hands"))
    ap.add_argument("--courts", action="store_true", help="also write <out>/courts/: the twelve courts' own hands")
    ap.add_argument("--only", nargs="*", type=int, help="row numbers to draw (0-based)")
    ap.add_argument("--matrix", action="store_true",
                    help="draw only the L/R × back/palm × pose anatomy matrix (labelled)")
    args = ap.parse_args(argv)
    os.makedirs(args.out, exist_ok=True)
    tmp = tempfile.mkdtemp(prefix="hands-")
    K.HAND_LOG.clear()
    R = matrix_rows() if args.matrix else rows()
    idx = args.only if args.only else list(range(len(R)))
    rows_svg, dump = [], []
    for ri in idx:
        title, calls = R[ri]
        cells = []
        for c in calls:
            try:
                sc, ctr = _scene(c)
                cells.append((c.get("label", ""), _svg(sc, ctr, CELL)))
            except Exception as e:  # noqa: BLE001
                print(f"[{title}] {c.get('label')}: {type(e).__name__}: {e}", file=sys.stderr)
                continue
            dump.append({"row": title, "label": c.get("label"), "fn": c["fn"],
                         "args": [list(map(float, x)) if isinstance(x, (tuple, list, np.ndarray)) else x
                                  for x in c["args"]],
                         "kw": {k: (list(map(float, v)) if isinstance(v, (tuple, list, np.ndarray)) else v)
                                for k, v in c["kw"].items()}})
        rows_svg.append((f"{ri}  {title}", cells))
    _sheets(rows_svg, args.out, tmp)
    with open(os.path.join(args.out, "specimen_calls.json"), "w") as fh:
        json.dump(dump, fh, indent=1, default=str)
    print(f"{len(dump)} hands -> {args.out}/specimen.png, specimen_1x.png")
    if args.courts:
        cc = court_cells(COURTS)
        per = {}
        for lab, svg in cc:
            per.setdefault(lab.split()[0], []).append((lab, svg))
        cr = [(pid, per[pid]) for pid in COURTS if pid in per]
        od = os.path.join(args.out, "courts")
        os.makedirs(od, exist_ok=True)
        _sheets(cr, od, tmp)
        print(f"{len(cc)} court hands -> {od}/specimen.png, specimen_1x.png")
    for w in K.HAND_LOG:
        print("  warn:", w)


def _sheets(rows_svg, out, tmp):
    """specimen.png (each cell 3x over card size, labelled) and specimen_1x.png
    (card size only, one row per pose), composed with PIL on a grey ground."""
    from PIL import Image, ImageDraw
    GREY = (154, 154, 154)
    C3, C1, PAD = int(CELL * 3), int(CELL), 6
    big_rows, small_rows = [], []
    n = 0
    for title, cells in rows_svg:
        ims3, ims1 = [], []
        for lab, svg in cells:
            p3, p1 = os.path.join(tmp, f"c{n}_3.png"), os.path.join(tmp, f"c{n}_1.png")
            n += 1
            _render(svg, p3, C3)
            _render(svg, p1, C1)
            ims3.append((lab, Image.open(p3).convert("RGB")))
            ims1.append(Image.open(p1).convert("RGB"))
        if not ims3:
            continue
        cw, ch = C3 + 2 * PAD, 34 + C3 + PAD + C1 + PAD + 24
        row = Image.new("RGB", (cw * len(ims3), ch), GREY)
        d = ImageDraw.Draw(row)
        d.text((8, 4), title, fill=(0, 0, 0), font=_font(24))
        for i, (lab, im) in enumerate(ims3):
            x = i * cw + PAD
            row.paste(im, (x, 34))
            row.paste(ims1[i], (x + (C3 - C1) // 2, 34 + C3 + PAD))
            d.text((x + 4, 34 + C3 + PAD + C1 + 2), lab, fill=(17, 17, 17), font=_font(17))
        big_rows.append(row)
        sr = Image.new("RGB", (330 + (C1 + PAD) * len(ims1), C1 + PAD), GREY)
        ImageDraw.Draw(sr).text((4, C1 // 2 - 8), title[:52], fill=(0, 0, 0), font=_font(12))
        for i, im in enumerate(ims1):
            sr.paste(im, (330 + i * (C1 + PAD), PAD // 2))
        small_rows.append(sr)
    for rows_, name in ((big_rows, "specimen.png"), (small_rows, "specimen_1x.png")):
        if not rows_:
            continue
        W = max(r.width for r in rows_)
        sheet = Image.new("RGB", (W, sum(r.height for r in rows_)), GREY)
        y = 0
        for r in rows_:
            sheet.paste(r, (0, y))
            y += r.height
        sheet.save(os.path.join(out, name))


if __name__ == "__main__":
    main()
