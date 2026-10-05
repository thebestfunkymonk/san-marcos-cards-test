import xml.etree.ElementTree as ET, sys, glob, os
sys.path.insert(0,'.')
import shapely
from inkkit import geom as G
from deck import tokens as T
NS='{http://www.w3.org/2000/svg}'
bad=[]
for s in "SHC":
    for r in ["2","3","4","5","6","7","8","9","10"]:
        root=ET.parse(f"cards/{r}{s}.svg").getroot()
        for el in root.iter(NS+'path'):
            if el.get('class')!='pip': continue
            sh=G.to_shape(el.get('d')); x0,y0,x1,y1=sh.bounds; ym=(y0+y1)/2
            up=sh.intersection(shapely.box(x0-1,y0-1,x1+1,ym)).area
            lo=sh.intersection(shapely.box(x0-1,ym,x1+1,y1+1)).area
            upright = up>lo
            cy=(y0+y1)/2
            should_rot = cy>525+1e-6
            if upright==should_rot: bad.append((r+s,round(cy,1),'upright' if upright else 'rotated'))
print('rotation errors:',bad)
# Index on all non-number cards (tl) vs number-card references
ref={}
for s in "SHCD":
    root=ET.parse(f"cards/2{s}.svg").getroot()
    ref[s]=[G.bbox(el.get('d')) for el in root.iter(NS+'path') if el.get('class')=='index-pip' and el.get('data-corner')=='tl'][0]
for f in sorted(glob.glob('cards/*.svg')):
    stem=os.path.basename(f)[:-4]
    if stem in ('BACK',): continue
    root=ET.parse(f).getroot()
    rk=[el for el in root.iter(NS+'path') if el.get('class') in ('index-rank','index-joker')]
    pp=[el for el in root.iter(NS+'path') if el.get('class')=='index-pip']
    out=[stem,len(rk),len(pp)]
    for el in rk:
        if el.get('data-corner')=='tl': out.append(('rank',[round(v,2) for v in G.bbox(el.get('d'))]))
    for el in pp:
        if el.get('data-corner')=='tl':
            b=G.bbox(el.get('d')); out.append(('pip',[round(v,2) for v in b], 'OK' if all(abs(a-c)<0.01 for a,c in zip(b,ref[stem[-1]])) else 'DIFF'))
    if not stem[:-1].isdigit(): print(out)
