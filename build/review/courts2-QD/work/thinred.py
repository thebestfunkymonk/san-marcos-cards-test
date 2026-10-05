"""thinred.py [module] — visible cape-red pieces narrower than 4.2 px (from the Scene geometry)."""
import sys, os, importlib.util, warnings
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art"); warnings.simplefilter("ignore")
from deck import courtkit as K
from inkkit import geom as G
path = sys.argv[1] if len(sys.argv) > 1 else ROOT + "/art/QD.py"
spec = importlib.util.spec_from_file_location("qdmod", path); m = importlib.util.module_from_spec(spec)
sys.path.insert(0, os.path.dirname(os.path.abspath(path))); spec.loader.exec_module(m)
sc = m.figure()
names = [i.name for i in sc.items]; k = names.index("cape"); cape = sc.items[k]
red = K.U(*[G.to_shape(mk.d, tol=0.05) for mk in cape.frag.marks if mk.kind == "fill" and mk.layer == "red"])
from shapely.geometry import LineString
def _strokes(frag):
    out = []
    for mk in frag.marks:
        if mk.kind == "stroke" and mk.d:
            for pts, closed in G.as_polys(mk.d, 0.1):
                pts = list(map(tuple, pts)) + ([tuple(pts[0])] if closed else [])
                if len(pts) > 1:
                    out.append(LineString(pts).buffer(mk.w / 2, quad_segs=6))
    return K.U(*out)
own = _strokes(cape.frag)
zones = []
for it in sc.items[k + 1:]:
    if it.occ is None or it.occ.is_empty:
        continue
    if it.halo and (it.halo_only is None or "cape" in it.halo_only) and "cape" not in it.halo_skip:
        zones.append(it.halo_zone if it.halo_zone is not None else it.occ.buffer(it.halo + K.MEDIUM / 2))
    zones.append(it.occ.buffer((K.CONTOUR if it.sil else K.MEDIUM) / 2))
vis = red.difference(own).difference(K.U(*zones)).intersection(K.box(139, 55, 611, 511))
op = vis.buffer(-2.1, quad_segs=8).buffer(2.1, quad_segs=8)
thin = vis.difference(op.buffer(0.05))
for g in sorted(K._polys_of(thin), key=lambda g: -g.area):
    if g.area > 2.0:
        b = g.bounds
        print(f"area {g.area:6.1f} bbox ({b[0]:.1f},{b[1]:.1f})-({b[2]:.1f},{b[3]:.1f})")
print("red area", round(red.area), "vis", round(vis.area), "thin total", round(thin.area, 1))
from shapely.geometry import Point
p = Point(254, 440)
print("vis contains (254,440)?", vis.contains(p), "red?", red.contains(p), "own?", own.contains(p), "zones?", K.U(*zones).contains(p))
print([ (mk.layer, mk.role) for mk in cape.frag.marks][:30])
if len(sys.argv) > 3:
    svg, out = sys.argv[2], sys.argv[3]
    import subprocess
    tmp = out + ".base.png"
    subprocess.run(["rsvg-convert", "-w", "1500", svg, "-o", tmp], check=True)
    import shapely.affinity as A
    t = A.scale(thin, 2, 2, origin=(0, 0))
    paths = []
    for g in K._polys_of(t):
        if g.area < 8: continue
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in g.exterior.coords)
        paths += ["-draw", f"polygon {pts}"]
    subprocess.run(["magick", tmp, "-fill", "magenta", "-stroke", "none"] + paths + ["-crop", "944x912+278+110", "+repage", out], check=True)
