import sys, os
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/build/review/corr-verify-wheels-1-0")
import vmeasure as V
from shapely.geometry import Polygon, box, Point
import shapely
os.chdir("/home/luke/Projects/design/san-marcos-deck")
ORIG = "/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/wheels/orig_out/"

def holes_of(svg):
    a = V.paths(svg, "jade")[0]
    jade = V.shape_of(a)
    big = max(V.comps(jade), key=lambda p: p.area)
    return [Polygon(r) for r in big.interiors], Polygon(big.exterior), jade

for tag, svg in (("BEFORE", ORIG + "BACK.svg"), ("AFTER", "cards/BACK.svg")):
    holes, ext, jade = holes_of(svg)
    wheel = [h for h in holes if 50 < h.bounds[2] - h.bounds[0] < 60 and h.bounds[0] < 100 and h.bounds[1] < 120][0]
    print("==", tag, "TL wheel bbox", [round(v, 2) for v in wheel.bounds])
    near = []
    for h in holes:
        if h is wheel:
            continue
        d = h.distance(wheel)
        if d < 14 and h.bounds[0] < 200 and h.bounds[1] < 250:
            near.append((round(d, 3), [round(v, 2) for v in h.bounds]))
    for n in sorted(near):
        print("   gap %.3f to hole bbox %s" % n)
    # jade bridge widths near the wheel: erode the jade near TL by 1.5 (i.e. <3 px wide bridges vanish)
    win = box(37.5, 37.5, 160, 200)
    jz = jade.intersection(win)
    thin = jz.difference(jz.buffer(-1.5).buffer(1.5 + 1e-6))
    thin = [g for g in V.comps(thin) if g.area > 0.05]
    print("   jade parts < 3.0 px wide in TL window:", len(thin), [([round(v, 1) for v in g.bounds], round(g.area, 2)) for g in thin][:10])
