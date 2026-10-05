import re, sys
sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck')
import shapely
from shapely.geometry import Point, box
from inkkit import geom as G
def load(svg='cards/JOKER-RED.svg'):
    s=open(svg).read()
    layers={}
    for m in re.finditer(r'<g id="(\w+)"[^>]*>(.*?)</g>',s,re.S):
        lid=m.group(1); out=[]
        for p in re.finditer(r'<path ([^>]*)/>',m.group(2)):
            a=p.group(1)
            d=re.search(r' ?d="([^"]*)"',' '+a).group(1)
            cls=re.search(r'class="([^"]*)"',a); cls=cls.group(1) if cls else ''
            sw=re.search(r'stroke-width="([^"]*)"',a)
            fill=re.search(r'fill="([^"]*)"',a).group(1) if 'fill=' in a else None
            cap=re.search(r'stroke-linecap="(\w+)"',a); join=re.search(r'stroke-linejoin="(\w+)"',a)
            if sw and (fill in (None,'none')):
                w=float(sw.group(1))
                pass
                out.append(dict(kind='stroke',d=d,w=w,cls=cls,cap=cap.group(1) if cap else None,join=join.group(1) if join else None))
            else:
                out.append(dict(kind='fill',d=d,cls=cls,shape=G.to_shape(d,tol=0.02)))
        layers[lid]=out
    return layers
