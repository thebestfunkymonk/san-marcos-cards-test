from rh import *
from deck.motifs import hair as HR
from inkkit import geom as G
g = "M0 0 C 20 40 20 80 60 110"
f = HR.current_lines(g, 5, gold="alternate")
show(f, "hair-alt-8x", zoom=8, view=(20, 60, 85, 125))
# exposed gold fill boundary: gold fill outline minus (union of ink lines + terminals) buffered 0
gold = f.select(lambda m: m.layer == "gold").shape()
ink = f.select(lambda m: m.layer == "ink").shape()
exposed = gold.boundary.difference(ink.buffer(0.01))
print("gold-lock edge length NOT covered by an Aquifer line/terminal (px):", round(exposed.length, 1))
for gg in sorted(getattr(exposed, 'geoms', [exposed]), key=lambda g: -g.length)[:6]:
    print("   piece", round(gg.length, 1), [round(v, 1) for v in gg.bounds])
