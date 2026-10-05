from rv import *
from deck.motifs import *
from inkkit import geom as G
import shapely, numpy as np, math
def ref(f): return shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05) for m in f.marks if m.d]).area
rng = np.random.default_rng(7)
cases = {
 "lion_mark40": lambda: lion_mark(0,0,40),
 "lion_mark_solid40": lambda: lion_mark(0,0,40,style="solid"),
 "rice_stalk": lambda: rice_stalk(0,0,-90,170),
 "ribbon_leaf": lambda: ribbon_leaf(0,0,-20,150),
 "rowel": lambda: rowel_star(0,0,40),
 "stalactite": lambda: stalactite(0,0),
 "comb_spray": lambda: comb_spray("M0 0 L0 -130", cone=11),
 "gill_plume": lambda: gill_plume("M0 110 C 6 70 24 40 40 20"),
 "rosette_R90": lambda: source_rosette(0,0,90),
 "salamander": lambda: blind_salamander(0,0),
 "wave_band": lambda: running_wave(0,200,0),
 "tooled_scroll": lambda: tooled_scroll(0,200,0),
 "cypress_cone": lambda: cypress_cone(0,0,11),
}
for name, fn in cases.items():
    base = fn(); nbad=0; worst=0
    for i in range(24):
        rot = float(rng.uniform(0,360)); tx,ty = rng.uniform(0,750), rng.uniform(0,1050)
        f = base.rotate(rot).translate(tx,ty)
        f = Frag(f.marks)  # fresh cache
        a=f.shape().area; r=ref(f)
        if abs(a-r)>0.01*r: nbad+=1; worst=max(worst,abs(a-r)/r)
    print(f"{name:20s} bad {nbad}/24 worst {worst:.2f}")
