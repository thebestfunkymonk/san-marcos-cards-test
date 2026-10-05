import re,sys
from collections import Counter
import xml.etree.ElementTree as ET
ns='{http://www.w3.org/2000/svg}'
def attrs(el):
    d=dict(el.attrib)
    st=d.pop('style',None)
    if st:
        for kv in st.split(';'):
            if ':' in kv:
                k,v=kv.split(':',1); d[k.strip()]=v.strip()
    return d
for f in sys.argv[1:]:
    t=ET.parse(f); r=t.getroot()
    print('=====',f)
    stats=Counter(); fills=Counter(); tags=Counter(); tr=Counter()
    def walk(el,layer,inh):
        a=attrs(el); inh=dict(inh)
        for k in ('stroke','stroke-width','fill','stroke-linecap','stroke-linejoin','stroke-miterlimit'):
            if k in a: inh[k]=a[k]
        if 'transform' in a: tr[a['transform'][:40]]+=1
        lid=a.get('id')
        if lid in ('paper','jade','red','gold','ink'): layer=lid
        tag=el.tag.replace(ns,'')
        tags[tag]+=1
        if tag in ('path','circle','ellipse','rect','line','polyline','polygon'):
            s=inh.get('stroke','none')
            if s not in ('none',None):
                stats[(layer,s,inh.get('stroke-width'),inh.get('stroke-linecap','butt'))]+=1
            fl=inh.get('fill','black')
            if fl!='none': fills[(layer,fl)]+=1
        for c in el: walk(c,layer,inh)
    walk(r,None,{})
    print('tags',dict(tags))
    print('transforms',dict(tr))
    for k,v in sorted(stats.items(),key=lambda x:(str(x[0][0]),str(x[0][2]))): print('  stroke',k,v)
    for k,v in sorted(fills.items(),key=str): print('  fill',k,v)
