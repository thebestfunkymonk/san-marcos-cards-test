import sys, os, re, time; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
import xml.etree.ElementTree as ET
import shapely, numpy as np
from inkkit import geom as G, svg as S
from deck import tokens as T
PL=os.path.join(SB,'planted'); os.makedirs(PL,exist_ok=True)
t=time.time()
base=build('BACK'); basew=build('BACK','white')
print('built', base['status'], round(time.time()-t,1))
src=open(base['svg']).read(); srcw=open(basew['svg']).read()
r0=check(base,basew); print('baseline', row(r0,['11','10a','12','8']), r0['11'].get('knockout'), r0['11'].get('detail'))
# find the jade flood path
m=re.search(r'<g id="jade"[^>]*>\s*(<path d="([^"]+)"[^>]*>)', src)
d=m.group(2); el=m.group(1)
flood=G.to_shape(d)
print('flood pieces', getattr(flood,'geoms',[flood]).__len__() if hasattr(flood,'geoms') else 1, 'area', round(flood.area))
def solid_point(x0,y0,x1,y1,rad):
    best=None
    for x in np.arange(x0,x1,1.0):
        for y in np.arange(y0,y1,1.0):
            p=shapely.Point(x,y)
            if flood.contains(p):
                dd=flood.boundary.distance(p)
                if dd>=rad and (best is None or dd>best[2]): best=(x,y,dd)
    return best
def run(name, new_d_fn, keys=('11',)):
    nd=new_d_fn(d)
    t2=src.replace(d, nd, 1); tw2=srcw.replace(d, nd, 1)
    a=dict(base); w=dict(basew)
    a['svg']=os.path.join(PL,name+'.svg'); w['svg']=os.path.join(PL,name+'.white.svg'); a['stem']=name; w['stem']=name
    open(a['svg'],'w').write(t2); open(w['svg'],'w').write(tw2)
    r=check(a,w)
    print(f'{name:36}', row(r, list(keys)), r['11'].get('knockout'), r['11'].get('detail'))
# emblem solid spot (inside lens, off-axis), frame solid spot (side band / spandrel)
pe=solid_point(420,560,520,700,4.5); pf=solid_point(85,150,160,260,4.5)
print('emblem solid pt',pe,'frame solid pt',pf)
for nm,p in (('emblem',pe),('frame',pf)):
    if p is None: print('no solid spot for',nm); continue
    x,y,_=p
    run(f'B1_{nm}_extra_hole_4.2', lambda dd: G.difference(dd, G.circle_d(x,y,2.1)))
    run(f'B2_{nm}_extra_hole_6.3', lambda dd: G.difference(dd, G.circle_d(x,y,3.15)))
    # a HAIRLINE knockout line, 40 px long, on one side only
    ang=0.0
    seg=G.poly_d([(x-3,y-20),(x+3,y+20)])
    run(f'B3_{nm}_extra_HAIRLINE_line', lambda dd: G.difference(dd, G.outline(seg, T.HAIRLINE)))
    run(f'B4_{nm}_extra_FINE_line', lambda dd: G.difference(dd, G.outline(seg, T.FINE)))
