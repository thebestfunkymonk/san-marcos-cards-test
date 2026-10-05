import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
from shapely.geometry import mapping
neck, rd = map(float, sys.argv[1:3]); out = sys.argv[3]
parts = dict(QC.FN.fan(QC.FIST_L, QC.FAN_AXIS, QC.PLUMES, **dict(QC.FAN_KW, neck=neck, root_dy=rd)))
cols = ['red', 'blue', 'green', 'orange', 'purple']
def d_of(g):
    s = ''
    for pg in K._polys_of(g):
        for ring in [pg.exterior] + list(pg.interiors):
            c = list(ring.coords); s += 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in c) + 'Z'
    return s
body = ''
for i in range(5):
    body += f'<path d="{d_of(parts[f"plume{i}"].shape)}" fill="none" stroke="{cols[i]}" stroke-width="0.3"/>'
body += f'<path d="{d_of(parts["ferrule"].shape)}" fill="none" stroke="black" stroke-width="0.4"/>'
body += f'<path d="{d_of(parts["handle"].shape)}" fill="none" stroke="gray" stroke-width="0.3"/>'
svg = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="270 350 60 50" width="1200" height="1000"><rect x="0" y="0" width="750" height="1050" fill="white"/>{body}</svg>'
open(out, 'w').write(svg)
