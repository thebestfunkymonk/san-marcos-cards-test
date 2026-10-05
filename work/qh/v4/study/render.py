"""Render a Scene (or Frag) crop: render(sc_or_frag, out.png, box, scale, heal=True)."""
import os, subprocess, sys, time
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import tokens as T, frames as F


def render(sc, out, box=(128, 44, 622, 540), scale=3.0, small=None, guides=True):
    t0 = time.time()
    frag = sc.compose() if hasattr(sc, "compose") else sc
    x0, y0, x1, y1 = box
    L = frag.layers()
    parts = [f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="{T.PAPER}"/>']
    for lay in T.LAYERS:
        if lay in L:
            parts.append(L[lay])
    if guides:
        parts.append(f'<path d="{F.art_window_d()}" fill="none" stroke="#999" stroke-width="0.6"/>')
        parts.append(f'<path d="{F.corner_pip_d("H")}" fill="{T.RED}"/>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x0} {y0} {x1-x0} {y1-y0}" width="{int((x1-x0)*scale)}" '
           f'height="{int((y1-y0)*scale)}">' + "".join(parts) + "</svg>")
    sp = out[:-4] + ".svg"
    open(sp, "w").write(svg)
    subprocess.run(["rsvg-convert", sp, "-o", out], check=True)
    if small:
        subprocess.run(["rsvg-convert", "-w", str(int((x1 - x0) * small)), sp, "-o", out[:-4] + "-s.png"], check=True)
    log = getattr(sc, "heal_log", [])
    print(f"{out}: {time.time()-t0:.1f}s heal {len(log)}")
    return log
