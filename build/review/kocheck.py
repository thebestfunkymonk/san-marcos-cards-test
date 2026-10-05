import sys, math; sys.path.insert(0,".")
import shapely
from deck.motifs import fauna as FA, core as C, lion as L, rice as R, geometric as M, hair as H
from inkkit import geom as G
def check(name, f):
    po = G.to_shape(f.outline(), tol=0.05).area
    sh = shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05).buffer(0) for m in f.marks if m.d]).area
    flag = "  <-- MISMATCH" if abs(po-sh) > 0.02*sh + 5 else ""
    print(f"{name:40s} pathops {po:9.1f} shapely {sh:9.1f}{flag}")
a=-60
x = 375 + 175*math.cos(math.radians(a)); y = 525 + 175*math.sin(math.radians(a))
d = FA.fountain_darter(x, y, 100, rot=a+90)
check("darter orbit", d); check("darter orbit rot180", d.rot180()); check("darter C2 pair", d + d.rot180())
for r in range(0, 360, 30):
    check(f"darter plain rot{r}", FA.fountain_darter(375, 525, 100, rot=r))
check("salamander seal", FA.blind_salamander(165,165))
check("salamander rot180", FA.blind_salamander(165,165).rot180())
check("lion moleca", L.lion_moleca())
check("lion andante", L.lion_andante(384.5,540))
check("lion mark 40", L.lion_mark(375,525,40))
check("rice stalk", R.rice_stalk(300,600,-120,170))
check("rice stalk rot180", R.rice_stalk(300,600,-120,170).rot180())
check("ribbon leaf", R.ribbon_leaf(300,500,-30,150))
check("ribbon leaf rot180", R.ribbon_leaf(300,500,-30,150).rot180())
check("rosette", M.source_rosette(375,525,130))
check("gill plume", FA.gill_plume("M0 110 C 6 70 24 40 40 20"))
