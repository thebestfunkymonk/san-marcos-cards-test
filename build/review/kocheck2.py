import sys; sys.path.insert(0,".")
import shapely
from deck.motifs import rice as R, hair as H, fauna as FA, lion as L, geometric as M
from inkkit import geom as G
def check(name, f):
    po = G.to_shape(f.outline(), tol=0.05)
    sh = shapely.union_all([G.to_shape(G.from_skia(m.skia()), tol=0.05).buffer(0) for m in f.marks if m.d])
    print(f"{name:32s} pathops {po.area:9.1f} bounds {[round(v,1) for v in po.bounds]}  shapely {sh.area:9.1f} bounds {[round(v,1) for v in sh.bounds]}")
check("wreath arc", R.rice_wreath_arc(0,0,150))
import deck.motifs.sheet_figurative as SF
check("tuck lens demo", SF.tuck_lens_demo())
check("lion mark solid 40", L.lion_mark(0,0,40,style="solid"))
check("current lines", H.current_lines("M0 0 C 20 40 20 80 60 110", 4))
