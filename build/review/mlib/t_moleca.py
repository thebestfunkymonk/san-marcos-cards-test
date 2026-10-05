from rh import *
from deck.motifs import lion as LI
from deck.motifs.sheet_figurative import spade_live, spade_h13
from inkkit import geom as G
sil = spade_live()
f = LI.lion_moleca(375, 262, silhouette=sil)
show(f, "moleca-head-6x", zoom=6, ground=T.PAPER, under=[(sil, T.INK)], view=(305,190,445,380))
show(f, "moleca-wing-4x", zoom=4, ground=T.PAPER, under=[(sil, T.INK)], view=(420,170,545,420))
# counts
prim = [m for m in f.marks if m.role=="leaf"]
print("feather outlines (leaf role) total:", len(prim), "-> per wing", len(prim)/2)
cov = [p for m in f.marks if m.role=="covert" for p,_ in G.flatten(m.d)]
print("covert subpaths", len(cov))
p = LI.lion_moleca_parts(375,262,silhouette=sil)
print("vent warnings", p["vent"].meta.get("warnings"))
# eyes: almond? pupil touching lids
