import re, subprocess, sys, io
import numpy as np
from PIL import Image

def strip(svg_text):
    # drop elements whose class contains index, and class="stock"
    out = re.sub(r'<path[^>]*class="[^"]*index[^"]*"[^>]*/>', '', svg_text)
    out = re.sub(r'<path[^>]*class="stock"[^>]*/>', '', out)
    out = re.sub(r'<g[^>]*class="[^"]*index[^"]*"[^>]*>.*?</g>', '', out, flags=re.S)
    return out

def render(svg_text, w=750):
    p = subprocess.run(['rsvg-convert', '-w', str(w), '-f', 'png'], input=svg_text.encode(), capture_output=True, check=True)
    im = Image.open(io.BytesIO(p.stdout)).convert('RGBA')
    return np.asarray(im).astype(float)/255.0

def stats(a, y0=0, y1=1050, x0=0, x1=750, thr=0.1, label=''):
    al = a[..., 3].copy()
    m = np.zeros_like(al); m[y0:y1, x0:x1] = 1
    al = al*m
    ys, xs = np.nonzero(al > thr)
    if len(ys) == 0:
        print(label, 'empty'); return None
    W = al.sum()
    yy, xx = np.mgrid[0:al.shape[0], 0:al.shape[1]]
    cx = (al*(xx+0.5)).sum()/W; cy = (al*(yy+0.5)).sum()/W
    bb = (xs.min(), xs.max()+1, ys.min(), ys.max()+1)
    print(f"{label}: bbox x {bb[0]}-{bb[1]} y {bb[2]}-{bb[3]} mid ({(bb[0]+bb[1])/2:.1f},{(bb[2]+bb[3])/2:.1f}) centroid ({cx:.1f},{cy:.1f}) mass {W:.0f}")
    return bb, (cx, cy)

if __name__ == '__main__':
    for f in sys.argv[1:]:
        t = open(f).read()
        s = strip(t)
        print('==', f, 'removed index:', t.count('index') - s.count('index'))
        a = render(s)
        stats(a, label='all')
        stats(a, y0=0, y1=745, label='figure (y<745)')
        stats(a, y0=745, y1=1050, label='caption (y>=745)')
