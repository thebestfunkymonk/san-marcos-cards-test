"""packx.py OUT.png key=val ...  -> run leaf_pack on the captured gown args with PACK overrides, overlay"""
import sys, os, time, json, subprocess, base64
sys.path.insert(0, "art"); sys.path.insert(0, ".")
import QC, _qc_gown as GW
from deck import courtkit as K
cap = {}
_g = GW.gown
def gown(shape, **k):
    cap.update(shape=shape, **k); return _g(shape, **k)
GW.gown = gown
sc, fc = QC.figure()
out = sys.argv[1]
over = {}
for a in sys.argv[2:]:
    k, v = a.split("=", 1); over[k] = eval(v)
shape = cap["shape"]; border = cap["border"]; exclude = cap["exclude"]; soft = cap["soft"]
it = {i.name: i for i in sc.items}
if over.pop("HIDE", False):
    over["hide"] = K.U(it["sleeveL"].occ, it["sleeveR"].occ).difference(K.U(it["cuffL"].occ, it["cuffR"].occ).buffer(8.0))
side = over.pop("SIDE", None)
pack = {**cap["pack"], **over}
inner = shape.buffer(-border, quad_segs=16)
allowed = inner.buffer(-2.5).difference(K.R(exclude))
over0 = over
if side == "L": allowed = allowed.intersection(K.box(0, 0, 375, 900))
if side == "R": allowed = allowed.intersection(K.box(375, 0, 900, 900))
tz = inner.buffer(-(3.0 + K.FINE / 2 + 0.3)).difference(K.R(exclude).buffer(-1.2))
t = time.time()
lf, placed = GW.leaf_pack(allowed, soft=soft, tip_zone=tz, **pack)
print("pack %.1fs" % (time.time() - t))
for b, L, W, bd, pg in placed:
    print("base (%.0f,%.0f) L %.0f W %.1f bounds %s vis %.2f" % (b[0], b[1], L, W, tuple(round(v) for v in pg.bounds),
          pg.difference(K.R(soft)).area / pg.area))
def d(g):
    from shapely.geometry import mapping
    s = ""
    for p in K._polys_of(g):
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords); s += "M" + " L".join("%.1f %.1f" % q for q in c) + "Z"
    return s
png = sys.argv[2] if False else "build/review/courts2-QC/r2/p0/QC.png"
b64 = base64.b64encode(open(png, "rb").read()).decode()
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1000" height="840" viewBox="150 280 500 420">
<image href="data:image/png;base64,{b64}" x="0" y="0" width="750" height="1050" opacity="0.45"/>
<path d="{d(allowed)}" fill="#0f0" fill-opacity="0.15" stroke="#080" stroke-width="0.8"/>
<path d="{d(K.R(soft))}" fill="#f0f" fill-opacity="0.18" stroke="#909" stroke-width="0.6"/>
''' + "".join(f'<path d="{d(pg)}" fill="#00f" fill-opacity="0.25" stroke="#00f" stroke-width="1"/>' for *_, pg in placed) + "</svg>"
open(out[:-4] + ".svg", "w").write(svg)
subprocess.run(["rsvg-convert", out[:-4] + ".svg", "-o", out], check=True)
