"""Review render helper (scratch)."""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs.sheet import layered_svg
OUT = Path(__file__).resolve().parent

def show(f, name, view=None, zoom=4.0, flood=None, ground=T.PAPER, under=(), flood_d=None, pad=8, resvg=False):
    if view is None:
        x0, y0, x1, y1 = f.bbox()
        view = (x0 - pad, y0 - pad, x1 + pad, y1 + pad)
    svg = layered_svg(f, view, ground=ground, flood=flood, flood_d=flood_d, under=under)
    p = OUT / f"{name}.svg"
    p.write_text(svg)
    png = OUT / f"{name}.png"
    subprocess.run(["rsvg-convert", "-z", str(zoom), str(p), "-o", str(png)], check=True)
    if resvg:
        subprocess.run(["resvg", "--zoom", str(zoom), str(p), str(OUT / f"{name}.resvg.png")], check=True)
    return png
