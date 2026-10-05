import sys, os, re, importlib.util, hashlib
from collections import Counter, defaultdict
ROOT="/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
path=sys.argv[1]
sys.path.insert(0, os.path.dirname(path))
spec=importlib.util.spec_from_file_location("m_"+os.path.basename(os.path.dirname(path)), path)
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
out=m.build()
out2=m.build()
h=lambda o: hashlib.md5(repr(sorted((k,(v if isinstance(v,str) else ''.join(v))) for k,v in o.items())).encode()).hexdigest()
print('deterministic', h(out)==h(out2), 'CUT_Y', getattr(m,'CUT_Y',None))
import xml.etree.ElementTree as ET
stats=Counter(); fills=Counter(); subpaths=Counter(); tags=Counter(); tr=Counter()
for layer,frags in out.items():
    s = frags if isinstance(frags,str) else ''.join(frags)
    root=ET.fromstring('<g xmlns="http://www.w3.org/2000/svg">'+s+'</g>')
    def walk(el,inh):
        a=dict(el.attrib); inh=dict(inh)
        for k in ('stroke','stroke-width','fill','stroke-linecap','stroke-linejoin','stroke-miterlimit','opacity','fill-rule'):
            if k in a: inh[k]=a[k]
        if 'transform' in a: tr[a['transform'][:30]]+=1
        tag=el.tag.split('}')[-1]; tags[tag]+=1
        if tag in ('path','circle','ellipse','rect','line','polyline','polygon'):
            d=a.get('d','')
            n=max(1,len(re.findall(r'[Mm]',d))) if tag=='path' else 1
            st=inh.get('stroke','none')
            if st!='none':
                key=(layer,st,inh.get('stroke-width'),inh.get('stroke-linecap','butt'),inh.get('stroke-linejoin','miter'))
                stats[key]+=1; subpaths[key]+=n
            fl=inh.get('fill','black')
            if fl!='none': fills[(layer,fl)]+=n
        for c in el: walk(c,inh)
    walk(root,{})
print('tags',dict(tags),'transforms',dict(tr))
for k in sorted(stats,key=str): print('  stroke',k,'elements',stats[k],'subpaths',subpaths[k])
for k in sorted(fills,key=str): print('  fill',k,'subpaths',fills[k])
