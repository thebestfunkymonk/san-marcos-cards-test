#!/usr/bin/env python3
"""Anatomy check for every ``hand5`` call in a court module.

    .venv/bin/python tools/hand_check.py art/KH.py            # or just: KH
    .venv/bin/python tools/hand_check.py KH QH JH --png /tmp/hand-check
    .venv/bin/python tools/hand_check.py art/JC.py --akimbo 2 --strict

The module is built in memory (``mod.build()``); nothing tracked is written.
``courtkit.hand5`` is wrapped for the duration of the build, so each call is
measured from the Hand it returned (``wrist_dir``, ``finger_dir``, digit tips),
never from the raster. One line is printed per hand, in call order:

    KH #1 art/KH.py:159 wrap L/back  fig L @ viewer R x=527 | thumb (..) index (..) | fingers 158 deg |
        forearm 24.2 deg | seam 41 px art side | A2 normal -10..90 ok | OK

Fields: pose, anatomical hand / view, which side of the card the hand sits on,
thumb and index tip positions, fingertip direction, forearm angle (the
direction from the wrist into the sleeve; ``->`` shows the angle after
``Hand.tucked`` re-aims it), distance from the hand to the seam, and the rule
check against ``library/hand-anatomy.md``:

  A1  the hand sits on its own side of the axis (L at viewer's right)
  A2  forearm angle inside the allowed range for the hand and position
        (normal / outboard / raised; ``--akimbo N`` selects the belt row)
  A3  fingertips do not point out toward the card edge
  A4  back view except for ``open`` gestures
  A7  both hands of a figure share one size factor
  chirality  thumb and index are on the anatomical side of the fingers

Any failed rule ends the line with ``FLAG(...)`` naming it. ``--strict`` exits
1 when any hand is flagged. ``--png DIR`` also composes the card in a sandbox
(like ``tools/preview.py``) and writes a 6x crop per hand with the forearm axis
(blue), thumb tip (magenta), index tip (orange) and little-finger tip (green).
"""
from __future__ import annotations

import argparse
import contextlib
import inspect
import io
import math
import os
import shutil
import sys
import tempfile
from dataclasses import dataclass, field

import numpy as np
from shapely.geometry import LineString, Point

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deck import courtkit as K  # noqa: E402
from deck import frames as F  # noqa: E402

AX = K.AX
OUTBOARD_X = 120.0          # abs(wrist x - AX) beyond which the outboard row applies
RAISED_Y = 300.0            # wrist above this y counts as raised
FINGERS_OUT_MAX = 0.5       # A3: outward x-component of the fingertip direction
SIZE_TOL = 0.03             # A7: relative size difference tolerated between hands
PNG_ZOOM = 6
PNG_PAD = 22.0

# A2 table (library/hand-anatomy.md): (row, lo, hi) degrees for the viewer's
# left hand (anatomical R) and the viewer's right hand (anatomical L).
A2 = {
    "R": {"normal": (90.0, 190.0), "outboard": (70.0, 190.0), "raised": (90.0, 170.0), "akimbo": (180.0, 240.0)},
    "L": {"normal": (-10.0, 90.0), "outboard": (-10.0, 110.0), "raised": (10.0, 90.0), "akimbo": (-60.0, 0.0)},
}
BACK_POSES = {"wrap", "cup", "rest", "hold_flat"}
# Sign of the thumb/index offset, left of an upright finger direction is negative (screen y down).
THUMB_SIGN = {("R", "back"): -1.0, ("L", "back"): +1.0, ("R", "palm"): +1.0, ("L", "palm"): -1.0}


# ----------------------------------------------------------------------------
# collection
# ----------------------------------------------------------------------------
@dataclass
class Record:
    index: int
    site: str
    pose: str
    result: object
    tucked_dir: np.ndarray | None = None
    kwargs: dict = field(default_factory=dict)


@contextlib.contextmanager
def collect_hand5():
    """Wrap ``courtkit.hand5`` and yield the list of Records it fills.

    The wrapper returns the original Hand untouched, so builds are unchanged.
    The Hand's ``rebuild`` callback is wrapped only to learn the direction
    ``Hand.tucked`` re-aims the wrist to.
    """
    original = K.hand5
    records: list[Record] = []

    def hook(at, angle=-90.0, pose="wrap", **kw):
        result = original(at, angle, pose, **kw)
        caller = inspect.stack()[1]
        site = f"{os.path.relpath(caller.filename, ROOT)}:{caller.lineno}"
        rec = Record(len(records) + 1, site, str(pose).lower(), result, kwargs=dict(kw))
        meta = result.hand.meta
        inner_rebuild = meta.get("rebuild")
        if inner_rebuild is not None:
            def rebuild(direction, _inner=inner_rebuild, _rec=rec):
                _rec.tucked_dir = _unit(direction)
                return _inner(direction)
            meta["rebuild"] = rebuild
        records.append(rec)
        return result

    K.hand5 = hook
    try:
        yield records
    finally:
        K.hand5 = original


# ----------------------------------------------------------------------------
# measurements
# ----------------------------------------------------------------------------
def _unit(v):
    v = np.asarray(v, float)
    return v / np.hypot(*v)


def deg(v) -> float:
    return math.degrees(math.atan2(float(v[1]), float(v[0])))


def _in_range(angle: float, lo: float, hi: float) -> bool:
    return (angle - lo) % 360.0 <= (hi - lo) + 1e-9


def forearm_row(hand: str, wrist, akimbo: bool = False) -> tuple[str, float, float]:
    """The A2 row (name, lo, hi) that applies to a hand at ``wrist``."""
    if akimbo:
        row = "akimbo"
    elif wrist[1] < RAISED_Y:
        row = "raised"
    elif abs(wrist[0] - AX) > OUTBOARD_X:
        row = "outboard"
    else:
        row = "normal"
    lo, hi = A2[hand][row]
    return row, lo, hi


def _lateral(f, p, centre):
    d = np.asarray(p, float) - centre
    return float(f[0] * d[1] - f[1] * d[0])


def chirality_ok(result, hand: str, view: str) -> bool:
    """Thumb and index lie on the anatomical side of the wrist->fingertips frame."""
    meta = result.hand.meta
    tips = np.asarray(meta["digit_tips"], float)
    centre = tips[:4].mean(axis=0)
    f = centre - np.asarray(result.wrist, float)
    f = f / np.hypot(*f)
    sign = THUMB_SIGN[(hand, view)]
    return (sign * _lateral(f, tips[4], centre) > 2.0 and sign * _lateral(f, tips[0], centre) > 2.0
            and sign * _lateral(f, tips[3], centre) < -2.0)


def measure(rec: Record, seam, *, akimbo: bool = False) -> dict:
    """Everything the report line shows, plus the flag list."""
    res = rec.result
    meta = res.hand.meta
    hand, view = meta["hand"], meta["view"]
    tips = [tuple(map(float, t)) for t in meta["digit_tips"]]
    thumb, index, little = tips[4], tips[0], tips[3]
    wrist = np.asarray(res.wrist, float)
    forearm = deg(res.wrist_dir)
    shown = deg(rec.tucked_dir) if rec.tucked_dir is not None else forearm
    shape = res.shape
    cx = float(shape.centroid.x)
    finger = deg(meta["finger_dir"])

    row, lo, hi = forearm_row(hand, wrist, akimbo)
    seam_dist = seam_side = None
    if seam is not None:
        pts = F.seam_points(seam)
        seam_dist = float(shape.distance(LineString(pts)))
        seam_y = float(np.interp(shape.centroid.x, pts[:, 0], pts[:, 1]))
        seam_side = "art side" if shape.centroid.y < seam_y else "BELOW SEAM"

    flags = []
    on_right = cx > AX
    if on_right != (hand == "L"):
        flags.append("A1 hand on the wrong side of the axis (fine only for a deliberate cross-body hand)")
    if not _in_range(shown, lo, hi):
        flags.append(f"A2 forearm {shown:.1f} outside {lo:g}..{hi:g} ({row})")
    out_x = float(meta["finger_dir"][0]) * (1.0 if cx > AX else -1.0)
    if out_x > FINGERS_OUT_MAX:
        flags.append(f"A3 fingers point out toward the card edge ({finger:.0f} deg)")
    if view == "palm" and rec.pose in BACK_POSES:
        flags.append(f"A4 palm view on a {rec.pose} grip (kit draws it as the other hand's back)")
    if not chirality_ok(res, hand, view):
        flags.append("chirality thumb/index not on the anatomical side")
    if seam_side == "BELOW SEAM":
        flags.append("hand centre is below the seam")
    return {
        "rec": rec, "hand": hand, "view": view, "pose": rec.pose, "x": cx, "viewer_side": "R" if on_right else "L",
        "thumb": thumb, "index": index, "little": little, "finger": finger, "forearm": forearm,
        "shown": shown, "tucked": rec.tucked_dir is not None and abs(((shown - forearm) + 180) % 360 - 180) > 0.5,
        "seam_dist": seam_dist, "seam_side": seam_side, "row": row, "range": (lo, hi),
        "size": float(meta["size"]), "wrist": wrist, "flags": flags,
    }


def a7_flags(rows: list[dict]) -> None:
    """A7: one size factor per figure. Adds a flag to every hand that deviates."""
    if len(rows) < 2:
        return
    sizes = [r["size"] for r in rows]
    if (max(sizes) - min(sizes)) / max(sizes) > SIZE_TOL:
        for r in rows:
            r["flags"].append(f"A7 hand sizes differ ({', '.join(f'{s:.1f}' for s in sizes)})")


def format_line(pid: str, m: dict) -> str:
    rec = m["rec"]
    side = f"fig {m['hand']} @ viewer {m['viewer_side']} x={m['x']:.0f}"
    thumb, index = m["thumb"], m["index"]
    arrow = f"{m['forearm']:.1f}->{m['shown']:.1f}" if m["tucked"] else f"{m['forearm']:.1f}"
    seam = "seam n/a" if m["seam_dist"] is None else f"seam {m['seam_dist']:.0f} px {m['seam_side']}"
    lo, hi = m["range"]
    rule = f"A2 {m['row']} {lo:g}..{hi:g} {'ok' if _in_range(m['shown'], lo, hi) else 'OUT'}"
    verdict = "OK" if not m["flags"] else "FLAG(" + "; ".join(m["flags"]) + ")"
    return (f"{pid} #{rec.index} {rec.site} {m['pose']} {m['hand']}/{m['view']} {side} | "
            f"thumb ({thumb[0]:.1f},{thumb[1]:.1f}) index ({index[0]:.1f},{index[1]:.1f}) | "
            f"fingers {m['finger']:.0f} deg | forearm {arrow} deg | {seam} | {rule} | {verdict}")


# ----------------------------------------------------------------------------
# module loading and crops
# ----------------------------------------------------------------------------
def _resolve(arg: str) -> tuple[str, str]:
    """(module path, piece id) from ``KH`` or ``art/KH.py`` or any path."""
    if os.path.isfile(arg):
        path = os.path.abspath(arg)
    else:
        path = os.path.join(ROOT, "art", f"{arg}.py")
        if not os.path.isfile(path):
            raise SystemExit(f"hand_check: no module for {arg!r} (looked for {path})")
    return path, os.path.splitext(os.path.basename(path))[0]


def build_module(path: str, pid: str, *, compose_dir: str | None = None):
    """Build a module's art with hand5 collected. Returns (module, records, card svg or None).

    With ``compose_dir`` the card is composed into that sandbox (as
    ``tools/preview.py`` does); otherwise only ``mod.build()`` runs."""
    import preview  # tools/preview.py: sandbox composition, never touches cards/ or build/
    mod = preview._load_module(path, pid)
    svg = None
    with collect_hand5() as records:
        if compose_dir is None:
            mod.build()
        else:
            from deck import build as B
            info = preview._compose(mod, B.normalize(pid)[0], "limestone", compose_dir)
            if info.get("error"):
                raise SystemExit(f"hand_check: {pid} failed to build:\n{info['error']}")
            svg = info["svg"]
    return mod, records, svg


def write_crop(svg: str, pid: str, m: dict, out_dir: str) -> str:
    from PIL import Image, ImageDraw
    import zoom as Z

    rec = m["rec"]
    x0, y0, x1, y1 = rec.result.shape.bounds
    forearm_end = m["wrist"] + _unit([math.cos(math.radians(m["shown"])), math.sin(math.radians(m["shown"]))]) * 36.0
    pts = [(x0, y0), (x1, y1), tuple(forearm_end)]
    xs, ys = zip(*pts)
    cx, cy = (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2
    half = max(max(xs) - min(xs), max(ys) - min(ys)) / 2 + PNG_PAD
    box = (cx - half, cy - half, 2 * half, 2 * half)
    path = os.path.join(out_dir, f"{pid}-hand{rec.index}-{m['pose']}-{m['hand']}-{m['view']}.png")
    with contextlib.redirect_stdout(io.StringIO()):
        Z.zoom(svg, *box, PNG_ZOOM, path)
    img = Image.open(path).convert("RGB")
    d = ImageDraw.Draw(img)

    def px(p):
        return ((p[0] - box[0]) * PNG_ZOOM, (p[1] - box[1]) * PNG_ZOOM)

    d.line([px(m["wrist"]), px(forearm_end)], fill=(30, 90, 255), width=4)
    ex, ey = px(forearm_end)
    d.ellipse([ex - 6, ey - 6, ex + 6, ey + 6], fill=(30, 90, 255))
    for key, color, r in (("thumb", (230, 0, 200), 9), ("index", (255, 140, 0), 7), ("little", (0, 170, 60), 7)):
        x, y = px(m[key])
        d.ellipse([x - r, y - r, x + r, y + r], outline=color, width=3)
    d.text((6, 6), f"{pid} #{rec.index} {m['pose']} {m['hand']}/{m['view']} forearm {m['shown']:.1f}", fill=(0, 0, 0))
    img.save(path)
    return path


# ----------------------------------------------------------------------------
def check_module(arg: str, *, png_dir: str | None = None, akimbo=(), out=print) -> list[dict]:
    path, pid = _resolve(arg)
    sandbox = tempfile.mkdtemp(prefix="hand-check-") if png_dir else None
    try:
        mod, records, svg = build_module(path, pid, compose_dir=sandbox)
        seam = getattr(mod, "SEAM", None) if F.double_head_mode(mod) == "continuous" else None
        rows = [measure(rec, seam, akimbo=rec.index in akimbo) for rec in records]
        a7_flags(rows)
        if not rows:
            out(f"{pid}: no hand5 calls")
        for m in rows:
            out(format_line(pid, m))
        if png_dir and svg:
            os.makedirs(png_dir, exist_ok=True)
            for m in rows:
                out(f"{pid} #{m['rec'].index} crop -> {write_crop(svg, pid, m, png_dir)}")
        return rows
    finally:
        if sandbox:
            shutil.rmtree(sandbox, ignore_errors=True)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("modules", nargs="+", help="court module path (art/KH.py) or piece id (KH)")
    ap.add_argument("--png", metavar="DIR", help="write a 6x annotated crop per hand into DIR (scratch)")
    ap.add_argument("--akimbo", type=int, nargs="*", default=[], metavar="N",
                    help="1-based hand numbers resting on a belt/hip (use the akimbo A2 row)")
    ap.add_argument("--strict", action="store_true", help="exit 1 when any hand is flagged")
    a = ap.parse_args(argv)
    flagged = False
    for arg in a.modules:
        for m in check_module(arg, png_dir=a.png, akimbo=set(a.akimbo)):
            flagged |= bool(m["flags"])
    return 1 if (a.strict and flagged) else 0


if __name__ == "__main__":
    sys.exit(main())
