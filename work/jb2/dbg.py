import os, subprocess, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "work/jb2/src"))
import shapely
from inkkit import geom as G
import _joker_black_pose as P
import _joker_black_plumage as PL
A = PL.anatomy()
cols = ["#e6194b","#3cb44b","#4363d8","#f58231","#911eb4","#46f0f0","#f032e6","#bcf60c","#008080","#9a6324","#800000","#808000","#000075"]
els = ['<rect width="750" height="1050" fill="#fff"/>', f'<path d="{G.from_shape(A["core"])}" fill="#ddd"/>']
for i, f in enumerate(sorted(A["stack"], key=lambda f: f.z)):
    if f.name in ("body", "bill"): continue
    c = cols[i % len(cols)]
    els.append(f'<path d="{G.from_shape(f.poly)}" fill="none" stroke="{c}" stroke-width="0.8"/>')
    rp = f.poly.representative_point() if not f.poly.is_empty else None
    if rp is not None:
        els.append(f'<text x="{rp.x:.1f}" y="{rp.y:.1f}" font-size="5" fill="{c}">{f.name}</text>')
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 750 1050" width="750" height="1050">{"".join(els)}</svg>'
p = os.path.join(ROOT, "work/jb2/out/dbg.svg"); open(p, "w").write(svg)
subprocess.run(["rsvg-convert", "-w", "3000", p, "-o", "/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/jb/dbg.png"], check=True)
subprocess.run(["magick", "/tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/jb/dbg.png", "-crop", "900x1500+1080+1050", "+repage", os.path.join(ROOT, "work/jb2/out/dbg-crop.png")], check=True)
