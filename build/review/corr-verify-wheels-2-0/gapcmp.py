"""Run three variants of the tuck foil_gaps §I.12 check on the tuck FRONT/BACK foil of
the sandbox this is run in: orig (order-dependent, run measured along piece a),
min (the fixer's), max (strict, run along the longer of the two)."""
import sys, os, json, importlib.util
import numpy as np, shapely, shapely.ops
sys.path.insert(0, os.getcwd())
from tuck import build_tuck as BT
from tuck import _tuck_common as K

def variant(mode):
    def fg(shape, *, sep=3.0, par=4.2, run_min=12.0, parallel=True):
        geoms = [g for g in getattr(shape, "geoms", [shape]) if g.area > 0.05]
        arr = np.array(geoms, dtype=object)
        tree = shapely.STRtree(arr)
        out = []
        pairs = tree.query(arr, predicate="dwithin", distance=par)
        def _run(p, q):
            pn, _ = shapely.ops.nearest_points(p, q)
            near_p = p.intersection(q.buffer(par + 0.1, quad_segs=4))
            patches = [g for g in getattr(near_p, "geoms", [near_p]) if g.distance(pn) < 0.3]
            near = shapely.union_all(patches) if patches else near_p
            if near.is_empty: return 0.0
            rr = near.minimum_rotated_rectangle
            if rr.geom_type != "Polygon": return 0.0
            xy = np.asarray(rr.exterior.coords)
            return max(np.linalg.norm(xy[1] - xy[0]), np.linalg.norm(xy[2] - xy[1]))
        for i, j in zip(*pairs):
            if i >= j: continue
            a, b = geoms[i], geoms[j]
            d = float(shapely.distance(a, b))
            if d < 0.08: continue
            if d < sep - 0.08:
                p1, p2 = shapely.ops.nearest_points(a, b)
                out.append(("sep", round(d, 2), None, None, round((p1.x + p2.x) / 2, 1), round((p1.y + p2.y) / 2, 1)))
            elif parallel and d < par - 0.08:
                ra, rb = _run(a, b), _run(b, a)
                run = {"orig": ra, "min": min(ra, rb), "max": max(ra, rb)}[mode]
                p1, p2 = shapely.ops.nearest_points(a, b)
                out.append(("par" if run >= run_min else "near", round(d, 2), round(ra, 1), round(rb, 1),
                            round((p1.x + p2.x) / 2, 1), round((p1.y + p2.y) / 2, 1)))
        return out
    return fg

b = BT.build_all()
res = {}
for name, frag, par in (("FRONT", b["front"]["foil"], True), ("BACK", b["back"]["foil"], False),
                        ("SIDE-A", b["panels"]["side_a"], True), ("SIDE-B", b["panels"]["side_b"], True),
                        ("TOP", b["panels"]["top"], True), ("BOTTOM", b["panels"]["bottom"], True)):
    sh = frag.shape()
    for mode in ("orig", "min", "max"):
        r = variant(mode)(sh, parallel=par)
        flagged = [x for x in r if x[0] in ("sep", "par")]
        res[f"{name}/{mode}"] = dict(flagged=flagged, near=[x for x in r if x[0] == "near"])
        print(name, mode, "flagged:", flagged)
    print(name, "near-parallel pairs (<4.2, run both ways):", res[f"{name}/min"]["near"] + [x for x in res[f"{name}/min"]["flagged"] if x[0]=="par"])
json.dump(res, open(sys.argv[1], "w"), indent=1)
