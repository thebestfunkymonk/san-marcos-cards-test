import sys, subprocess
sys.path.insert(0, ".")
from deck import tokens as T
from deck.motifs import core as C
from deck.motifs.sheet import layered_svg
def out(f, name, view, zoom=1.0, ground=T.PAPER, flood=None, under=()):
    svg = layered_svg(f, view, ground=ground, flood=flood, under=under)
    p = f"build/review/{name}.svg"
    open(p, "w").write(svg)
    subprocess.run(["rsvg-convert", "-z", str(zoom), p, "-o", f"build/review/{name}.png"], check=True)
