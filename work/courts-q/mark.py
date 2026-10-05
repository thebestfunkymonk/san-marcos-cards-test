import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck"); sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")
from deck import build as B, courtkit as K
from deck.motifs import core as C
from inkkit import geom as G
mod = B.load_art(sys.argv[1])
sc = mod.figure(); sc = sc[0] if isinstance(sc, tuple) else sc
res = mod.compose_scene(sc) if hasattr(mod, "compose_scene") else sc.compose()
for i in map(int, sys.argv[2:]):
    m = res.marks[i]
    s = G.to_shape(m.d, tol=0.05) if m.kind == "fill" else C.Frag([m]).shape()
    print(i, m.role, m.kind, m.layer, [ (round(p.area,1), [round(v,1) for v in p.bounds]) for p in K._polys_of(s)][:12])
