import re, sys, subprocess, io
import numpy as np
from PIL import Image
sys.path.insert(0, '.')
from inkkit import geom as G
import shapely
from shapely.geometry import LineString

SVG = sys.argv[1] if len(sys.argv) > 1 else 'cards/JOKER-BLACK.svg'
s = open(SVG).read()

def layers(s):
    out = []
    for gm in re.finditer(r'<g id="(\w+)"[^>]*>(.*?)</g>', s, re.S):
        lid = gm.group(1)
        for pm in re.finditer(r'<path ([^>]*?)/>', gm.group(2), re.S):
            a = pm.group(1)
            att = dict(re.findall(r'([\w-]+)="([^"]*)"', a))
            out.append((lid, att))
    return out

P = layers(s)
def shape_of(att):
    d = att.get('d', '')
    if att.get('fill', '') not in ('none', '') and 'stroke' not in att:
        return G.to_shape(d, tol=0.02)
    w = float(att.get('stroke-width', 0))
    cap = att.get('stroke-linecap', 'butt')
    polys = G.flatten(d, 0.02)
    gs = []
    for pts, closed in polys:
        ls = LineString(pts)
        gs.append(ls.buffer(w/2, cap_style='round' if cap == 'round' else 'flat', join_style='round' if att.get('stroke-linejoin')=='round' else 'mitre', quad_segs=16))
    return shapely.union_all(gs)

def render(svg_text, zoom=1):
    p = subprocess.run(['rsvg-convert', '-z', str(zoom), '-f', 'png'], input=svg_text.encode(), capture_output=True, check=True)
    return Image.open(io.BytesIO(p.stdout)).convert('RGBA')

def strip(s, drop_caption=False):
    t = re.sub(r'<path [^>]*class="stock"[^>]*/>', '', s)
    t = re.sub(r'<path [^>]*class="index[^"]*"[^>]*/>', '', t)
    return t

if __name__ == '__main__':
    for lid, att in P:
        if att.get('class') in ('stock',) or 'index' in att.get('class', ''):
            continue
        g = shape_of(att)
        print(lid, att.get('class', ''), att.get('fill'), att.get('stroke-width'), [round(v, 1) for v in g.bounds], round(g.area, 1))
    im = render(strip(s))
    a = np.asarray(im)[:, :, 3].astype(float) / 255
    ys, xs = np.nonzero(a > 0.1)
    print('alpha bbox', xs.min(), xs.max()+1, ys.min(), ys.max()+1, 'mid', (xs.min()+xs.max()+1)/2, (ys.min()+ys.max()+1)/2)
    Y, X = np.mgrid[0:a.shape[0], 0:a.shape[1]]
    print('alpha centroid', (a*X).sum()/a.sum()+0.5, (a*Y).sum()/a.sum()+0.5)
