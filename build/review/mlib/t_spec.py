from rh import *
import math, numpy as np
from deck.motifs import geometric as M
from deck.motifs import lion as LI
from deck.motifs import fauna as FA
from inkkit import geom as G
from shapely.geometry import Point
def roles(f): 
    d = {}
    for m in f.marks: d[m.role] = d.get(m.role, 0) + len(G.flatten(m.d)) if m.kind == "stroke" else d.get(m.role, 0) + 1
    return d
r = M.source_rosette(0, 0, 130)
print("rosette roles", roles(r))
# rib twist
ribs = [p for m in r.marks if m.role == "rib" for p, _ in G.flatten(m.d)]
outer = [p for p in ribs if np.hypot(*p[0]) > 60]
p = outer[0]; a0 = math.degrees(math.atan2(p[0][1], p[0][0])); a1 = math.degrees(math.atan2(p[-1][1], p[-1][0]))
print("band rib r", round(np.hypot(*p[0]),1), "->", round(np.hypot(*p[-1]),1), "twist", round((a1 - a0 + 540) % 360 - 180, 2))
print("crater ribs", len([q for q in ribs if np.hypot(*q[-1]) < 25]))
bub = [m for m in r.marks if m.role == "bubble"]
print("bubble ring count", len(bub), "centreline dia", round(G.bbox(bub[0].d)[2]-G.bbox(bub[0].d)[0], 2))
waves = [m for m in r.marks if m.role == "wave"]
print("wave hooks", sum(len(G.flatten(m.d)) for m in waves), "rosette meta wave", r.meta.get('n_waves'), r.meta.get('wave_height'))
# vent roundel
v = M.vent_roundel(68.5, 74.5)
print("vent roundel ribs", sum(len(G.flatten(m.d)) for m in v.marks if m.role == "rib"))
# lens
geo = M.lens_geometry(); print("lens R", round(geo['R'],2), geo['c_left'], geo['c_right'])
lf = M.lens_field(geo, count=7, corners=[(37.5,37.5),(712.5,37.5),(37.5,1012.5),(712.5,1012.5)])
print("lens field widths", {m.w for m in lf.marks})
# reed ladder defaults
rl = M.reed_ladder((0,0),(0,300)); print("reed ladder roles", roles(rl))
# strata heights
# karst void sizes
kv = M.karst_voids(G.rect_d(0,0,200,120))
sz = sorted({round(G.bbox(m.d)[3]-G.bbox(m.d)[1]-2.1,1) for m in kv.marks if m.role=="void" and 'Z' in m.d.upper()})
print("karst void heights present", sz)
# drip fringe terminals
df = M.drip_fringe(0, 120, 0); print("drip terminals", sum(1 for m in df.marks if m.role=="terminal"), "drips", sum(1 for m in df.marks if m.role=="drip"))
# spring vent per §H.13
sv = LI.spring_vent(); print("spring vent rings", sum(1 for m in sv.marks if m.role=="vent"), "ribs", sum(len(G.flatten(m.d)) for m in sv.marks if m.role=="rib"))
# mane
mn = LI.mane_rings(375, 262); print("mane rings", len(mn.marks))
