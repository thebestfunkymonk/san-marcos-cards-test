"""Render isolated QD parts at 3x for fast iteration (not deck output).

    .venv/bin/python work/qd/part_test.py <name> x0 y0 x1 y1 [scale]
"""
from __future__ import annotations

import importlib
import os
import subprocess
import sys

ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "art"))

from deck import courtkit as K      # noqa: E402
from deck import tokens as T        # noqa: E402
import _qd_parts as Q               # noqa: E402

OUT = os.path.join(ROOT, "work/qd/out/parts")


def render(frag, box, path, scale=3):
    x0, y0, x1, y1 = box
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1 - x0}" height="{y1 - y0}" fill="{T.PAPER}"/>']
    lay = frag.layers()
    for L in T.LAYERS:
        if lay.get(L):
            parts.append(lay[L])
    w = int((x1 - x0) * scale)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1 - x0} {y1 - y0}" width="{w}" '
           f'height="{int(w * (y1 - y0) / (x1 - x0))}">' + "".join(parts) + "</svg>")
    with open(path.replace(".png", ".svg"), "w") as fh:
        fh.write(svg)
    subprocess.run(["rsvg-convert", "-w", str(w), path.replace(".png", ".svg"), "-o", path], check=True)


def scene_spike():
    sc = K.Scene()
    bg = K.box(150, 330, 340, 480)
    sc.add("bg", K.fill(bg, K.RED) + K.outline(bg), bg, sil=False)
    pb = Q.paintbrush5((288.0, 478.0), (206.0, 240.0), spike=78.0, spread=40.0, top=(22.0, 12.0),
        bracts=((0.00, -1, 26.0, 13.0, 0.5), (0.14, +1, 26.0, 13.0, 0.5), (0.34, -1, 23.0, 12.5, 0.55),
                (0.48, +1, 22.0, 12.0, 0.6), (0.64, -1, 18.0, 11.0, 0.7)))
    sc.add("pb", pb.frag, pb.shape, sil=False, halo=K.HALO)
    pb2 = Q.paintbrush4((330.0, 478.0), (330.0, 250.0), spike=62.0,
        fingers=((-22.0, 34.0, 12.5), (-11.0, 44.0, 12.5), (0.0, 50.0, 13.0), (11.0, 44.0, 12.5), (22.0, 34.0, 12.5)),
        lower=((-50.0, 28.0, 10.0), (50.0, 28.0, 10.0)), dip=0.62, dip_sag=5.0, fan_c=20.0, inner_lines='red')
    sc.add("pb2", pb2.frag, pb2.shape, sil=False)
    return sc


def main():
    name = sys.argv[1]
    box = tuple(float(v) for v in sys.argv[2:6])
    scale = float(sys.argv[6]) if len(sys.argv) > 6 else 3
    os.makedirs(OUT, exist_ok=True)
    if name.startswith("spike"):
        sc = scene_spike()
    else:
        mod = importlib.import_module("QD")
        sc = mod.figure()
    f = sc.compose()
    render(f, box, os.path.join(OUT, f"{name}.png"), scale)
    print(os.path.join(OUT, f"{name}.png"), "heal", len(sc.heal_log))


if __name__ == "__main__":
    main()
