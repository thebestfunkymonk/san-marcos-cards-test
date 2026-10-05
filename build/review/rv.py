"""Review helpers (scratch). Render Frags in line / knockout mode."""
import subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs.sheet import layered_svg
OUT = ROOT / "build" / "review"

def save(f, name, view=None, zoom=4.0, ground=T.PAPER, flood=None, flood_d=None, under=(), pad=8, renderer="rsvg"):
    if view is None:
        x0, y0, x1, y1 = f.bbox()
        view = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    svg = layered_svg(f, view, ground=ground, flood=flood, flood_d=flood_d, under=under)
    p = OUT / f"{name}.svg"
    p.write_text(svg)
    png = OUT / f"{name}.png"
    if renderer == "rsvg":
        subprocess.run(["rsvg-convert", "-z", str(zoom), str(p), "-o", str(png)], check=True)
    else:
        subprocess.run(["resvg", "--zoom", str(zoom), str(p), str(png)], check=True)
    return png
