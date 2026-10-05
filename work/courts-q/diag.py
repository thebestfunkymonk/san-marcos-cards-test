"""diag.py <module.py> [x,y ...] — compose a court's scene, print the heal log
(UNRESOLVED first) and the marks within 6 px of each point (role, kind, w, layer, dist)."""
import importlib.util
import os
import sys

ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "art"))
from shapely.geometry import Point  # noqa: E402
from deck.motifs import core as C  # noqa: E402

path = sys.argv[1]
spec = importlib.util.spec_from_file_location("m", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sc = mod.figure()
if isinstance(sc, tuple):
    sc = sc[0]
if hasattr(mod, "compose_scene"):
    res = mod.compose_scene(sc)
else:
    res = sc.compose()
log = sc.heal_log
unres = [e for e in log if "UNRES" in str(e).upper()]
print(f"heal log: {len(log)} entries, {len(unres)} unresolved")
for e in unres:
    print("  U", e)
if "-v" in sys.argv:
    for e in log:
        print("   ", e)
for a in sys.argv[2:]:
    if "," not in a:
        continue
    x, y = map(float, a.split(","))
    p = Point(x, y)
    print(f"--- near ({x},{y})")
    rows = []
    for i, m in enumerate(res.marks):
        try:
            s = C.Frag([m]).shape()
        except Exception:
            continue
        d = s.distance(p)
        if d < 6:
            rows.append((d, i, m.role, m.kind, m.w, m.layer))
    for r in sorted(rows):
        print("   d=%.2f  #%d role=%s kind=%s w=%s layer=%s" % r)

# ---- QA-12 style vector gaps on the composed marks (top half only) ----
if "--qa" in sys.argv:
    from deck import qa as QA
    import shapely
    pieces = []
    for lay in ("jade", "red", "gold", "ink"):
        runs, key, cur = [], None, []
        for i, m in enumerate(res.marks):
            if m.layer != lay or not m.d:
                continue
            if m.kind == "fill":
                if cur:
                    runs.append(cur)
                cur, key = [], None
                runs.append([i])
            else:
                k = (m.color, m.w, m.cap, m.join, m.miter)
                if k != key and cur:
                    runs.append(cur)
                    cur = []
                key = k
                cur.append(i)
        if cur:
            runs.append(cur)
        for run in runs:
            ms = [res.marks[i] for i in run]
            s = C.Frag(ms).shape()
            kind = "stroke" if ms[0].kind == "stroke" else "fill"
            for pg in getattr(s, "geoms", [s]):
                if pg.geom_type == "Polygon" and pg.area > 0.05:
                    # which marks make this piece
                    who = [j for j in run if C.Frag([res.marks[j]]).shape().intersects(pg.buffer(-0.01))]
                    tag = ",".join(f"#{j}:{res.marks[j].role}" for j in who[:3])
                    pieces.append({"geom": pg, "layer": lay, "kind": kind, "el": run[0], "cls": {tag}, "art": True})
    out = QA.vector_gaps(pieces)
    print(f"QA-12 on composed marks: {len(out)} issues")
    for o in out[:40]:
        print("  ", o["gap"], o["rule"], o["at"], o["what"], o["layers"])
