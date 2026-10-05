import xml.etree.ElementTree as ET, sys, math
sys.path.insert(0,'.')
import numpy as np, shapely
from inkkit import geom as G
from deck import tokens as T
NS='{http://www.w3.org/2000/svg}'
def els(root, cls):
    out=[]
    for g in root:
        if g.tag!=NS+'g': continue
        for el in g.iter():
            if cls in (el.get('class') or '').split(): out.append((g.get('id'),el))
    return out
for card in sys.argv[1:]:
    root=ET.parse(f'cards/{card}.svg').getroot()
    print('=====',card,[g.get('id') for g in root if g.tag==NS+'g'])
    for cls in ['frame','frame-inner','band-rule','partition','medallion','house-mark','corner-pip']:
        for layer,el in els(root,cls):
            d=el.get('d'); a={k:el.get(k) for k in ('fill','stroke','stroke-width','stroke-linecap','stroke-linejoin','stroke-miterlimit','data-corner')}
            a={k:v for k,v in a.items() if v}
            polys=G.as_polys(d,0.05)
            bb=[round(v,2) for v in G.bbox(d)]
            print(f'{cls:12} {layer:5} {a} bbox={bb} subpaths={len(polys)}')
            if cls in ('frame','frame-inner'):
                for pts,closed in polys:
                    print('   verts', np.round(np.asarray(pts),2).tolist()[:10], 'closed',closed)
            if cls=='band-rule':
                for pts,closed in polys: print('   ', np.round(np.asarray(pts)[[0,-1]],2).tolist())
