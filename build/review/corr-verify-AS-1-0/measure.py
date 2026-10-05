import re, subprocess, sys, io
import numpy as np
from PIL import Image
from xml.etree import ElementTree as ET
OUT = 'build/review/corr-verify-AS-1-0/'
ET.register_namespace('', 'http://www.w3.org/2000/svg')
NS = '{http://www.w3.org/2000/svg}'

def strip(src, dst, shift=0.0, keep_index=False, only_index=False, layers=None):
    t = ET.parse(src); r = t.getroot()
    for g in list(r.iter(NS+'g')):
        for el in list(g):
            c = el.get('class', '') or ''
            isidx = 'index' in c
            if c == 'stock' or (isidx and not keep_index and not only_index) or (only_index and not isidx):
                g.remove(el)
        if layers is not None and g.get('id') not in layers:
            for el in list(g): g.remove(el)
    if shift:
        for g in r.iter(NS+'g'):
            if g.get('id') in ('ink', 'gold'):
                # wrap children in a translated group
                kids = list(g)
                for k in kids: g.remove(k)
                sub = ET.SubElement(g, NS+'g', {'transform': f'translate(0 {shift})'})
                for k in kids: sub.append(k)
    t.write(dst)

def render(svg, png, w=750):
    subprocess.run(['rsvg-convert', '-w', str(w), '-o', png, svg], check=True)
    return np.asarray(Image.open(png).convert('RGBA')).astype(float)/255

def stats(a, name, thr=0.05):
    al = a[..., 3]
    ys, xs = np.nonzero(al > thr)
    x0, x1, y0, y1 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
    Y, X = np.mgrid[0:al.shape[0], 0:al.shape[1]]
    cx = (al*(X+0.5)).sum()/al.sum(); cy = (al*(Y+0.5)).sum()/al.sum()
    print(f'{name}: bbox x {x0}-{x1} y {y0}-{y1} mid ({(x0+x1)/2:.1f},{(y0+y1)/2:.1f}) centroid ({cx:.1f},{cy:.1f})')
    return (x0, y0, x1, y1)

if __name__ == '__main__':
    strip('cards/AS.svg', OUT+'after_noidx.svg')
    strip('build/gallery/svg/AS.svg', OUT+'before_noidx.svg')
    strip('build/gallery/svg/AS.svg', OUT+'before_shift92.svg', shift=92)
    strip('build/white/cards/AS.svg', OUT+'afterW_noidx.svg')
    A = render(OUT+'after_noidx.svg', OUT+'after_noidx.png')
    B = render(OUT+'before_noidx.svg', OUT+'before_noidx.png')
    S = render(OUT+'before_shift92.svg', OUT+'before_shift92.png')
    W = render(OUT+'afterW_noidx.svg', OUT+'afterW_noidx.png')
    stats(B, 'before'); stats(A, 'after'); stats(S, 'before+92'); stats(W, 'white after')
    # per-layer
    for lay in ('ink', 'gold'):
        strip('cards/AS.svg', OUT+f'after_{lay}.svg', layers={lay})
        stats(render(OUT+f'after_{lay}.svg', OUT+f'after_{lay}.png'), f'after {lay}')
    # diff A vs S
    d = np.abs(A - S).max(axis=2)
    ys, xs = np.nonzero(d > 0.02)
    print('diff pixels >0.02:', len(ys))
    if len(ys):
        # cluster by row bands
        rows = sorted(set(ys.tolist()))
        bands = []; s = rows[0]; p = rows[0]
        for y in rows[1:]:
            if y > p+3: bands.append((s, p)); s = y
            p = y
        bands.append((s, p))
        for b in bands:
            m = (ys >= b[0]) & (ys <= b[1])
            print('  band y', b, 'x', xs[m].min(), xs[m].max(), 'n', m.sum(), 'maxdiff', d[ys[m], xs[m]].max().round(3))
    # white vs limestone
    dw = np.abs(A - W).max(axis=2)
    print('white vs limestone (no stock) max diff', dw.max())
