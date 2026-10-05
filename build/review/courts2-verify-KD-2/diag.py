import sys, warnings
warnings.simplefilter("ignore")
sys.path.insert(0, ".")
import shapely
from shapely.geometry import Point, box
from deck import courtkit as K
from art import KD
sc = KD.figure()
pts = [tuple(map(float, a.split(","))) for a in sys.argv[1:]]
for it in sc.items:
    occ = it.occ
    for p in pts:
        P = Point(p)
        hit_occ = occ is not None and occ.buffer(0.5).contains(P)
        hit_line = False
        if it.frag:
            for m in it.frag.marks:
                if m.kind == "fill" or not m.d: continue
                for ln in K._stroke_lines(m.d):
                    g = ln if hasattr(ln, "distance") else shapely.LineString(ln)
                    if g.distance(P) <= m.w/2 + 0.6:
                        hit_line = (m.role, m.w); break
                if hit_line: break
        if hit_occ or hit_line:
            print(p, it.name, "occ" if hit_occ else "", hit_line or "")
print("heal log:")
for h in sc.heal_log: print("  ", h)
