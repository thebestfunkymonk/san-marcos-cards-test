from rh import *
from deck.motifs import fauna as FA
from inkkit import geom as G
import numpy as np
for r in (74, 50, 30):
    g = FA.blind_salamander(0, 0, radius=r)
    L = g.meta['length']
    k = (L/300)**0.5
    body = g.select(lambda m: m.role=="outline").bbox()
    gills = g.select(lambda m: m.role in ("spine","barb","tip"))
    limbs = g.select(lambda m: m.role in ("limb","toe"))
    # longest limb piece
    lp = [ (G.Curve(p).length) for m in g.marks if m.role=="limb" for p,_ in G.flatten(m.d)]
    gl = [ (G.Curve(p).length) for m in g.marks if m.role=="spine" for p,_ in G.flatten(m.d)]
    head_w = 2*10.6*k
    print(f"radius {r}: spine L={L:.0f} k={k:.2f} body bbox {body[2]-body[0]:.0f}x{body[3]-body[1]:.0f} head width≈{head_w:.1f} gill spine lengths {[round(x) for x in gl]} limb pieces {len(lp)} {[round(x) for x in lp]}")
    gr = [m for m in g.marks if m.role=="groove"]
    pts = [G.flatten(m.d)[0][0] for m in gr]
    mids = np.array([p.mean(axis=0) for p in pts])
    # spacing between consecutive grooves on the same side
    dd = [np.hypot(*(mids[i+2]-mids[i])) for i in range(0,len(mids)-2,2)]
    print("   costal groove centre spacing (same side) min", round(min(dd),2), "-> clear", round(min(dd)-2.1,2))
g = FA.blind_salamander(0, 0, radius=30)
col = {"limb": T.RED, "toe": T.RED, "spine": T.JADE, "barb": T.JADE, "tip": T.JADE}
f2 = C.Frag([__import__('dataclasses').replace(m, color=col.get(m.role, T.INK), layer=C.LAYER_OF[col.get(m.role, T.INK)]) for m in g.marks])
show(f2, "sal-r30-roles-8x", zoom=8)
