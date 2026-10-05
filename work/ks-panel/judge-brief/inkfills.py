import sys, os, re, importlib.util
ROOT="/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from inkkit import geom as G
import xml.etree.ElementTree as ET
path=sys.argv[1]
sys.path.insert(0, os.path.dirname(path))
spec=importlib.util.spec_from_file_location("m_"+os.path.basename(os.path.dirname(path)), path)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out=m.build()
tot={}
for layer,frags in out.items():
    s = frags if isinstance(frags,str) else ''.join(frags)
    root=ET.fromstring('<g xmlns="http://www.w3.org/2000/svg">'+s+'</g>')
    items=[]
    def walk(el,inh):
        a=dict(el.attrib); inh=dict(inh)
        for k in ('stroke','fill'):
            if k in a: inh[k]=a[k]
        tag=el.tag.split('}')[-1]
        if tag=='path' and inh.get('fill','black')!='none':
            items.append(a['d'])
        for c in el: walk(c,inh)
    walk(root,{})
    if layer=='ink':
        for d in items:
            sh=G.to_shape(d)
            geoms=getattr(sh,'geoms',[sh])
            for g in sorted(geoms,key=lambda g:-g.area)[:8]:
                b=g.bounds
                print('  ink fill piece area %.1f bbox (%.0f,%.0f)-(%.0f,%.0f) holes %d'%(g.area,*b,len(g.interiors)))
            print('  ink-fill element pieces', len(geoms), 'total area %.0f'%sh.area)
