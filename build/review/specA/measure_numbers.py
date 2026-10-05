import xml.etree.ElementTree as ET, math, sys, glob, os
sys.path.insert(0,'.')
from inkkit import geom as G
from deck import tokens as T, layout as LY
NS='{http://www.w3.org/2000/svg}'
ranks=["2","3","4","5","6","7","8","9","10"]
rows=[]
idx_boxes={}
problems=[]
for s in "SHCD":
    for r in ranks:
        p=f"cards/{r}{s}.svg"
        root=ET.parse(p).getroot()
        assert root.get('viewBox')=="0 0 750 1050", root.get('viewBox')
        groups=[g.get('id') for g in root if g.tag==NS+'g']
        if groups!=list(T.LAYERS): problems.append((p,'groups',groups))
        # colours per layer
        for g in root:
            if g.tag!=NS+'g': continue
            for el in g.iter():
                f=el.get('fill'); st=el.get('stroke')
                if el.tag==NS+'path' and g.get('id')!='paper':
                    if f!=T.SUIT_COLOR[s] or st: problems.append((p,g.get('id'),f,st))
                    if g.get('id')!=T.SUIT_LAYER[s]: problems.append((p,'layer',g.get('id')))
        pips=[el for el in root.iter(NS+'path') if el.get('class')=='pip']
        exp=LY.positions(int(r))
        got=[]
        for el in pips:
            x0,y0,x1,y1=G.bbox(el.get('d'))
            cx,cy=(x0+x1)/2,(y0+y1)/2
            # rotation: spade/club apex at top when upright -> compare first point
            d=el.get('d'); 
            got.append((round(cx,2),round(cy,2),round(x1-x0,2),round(y1-y0,2), el.get('data-rot')))
        # rotation check by geometry: area centroid vs bbox centre
        for el in pips:
            sh=G.to_shape(el.get('d'))
            x0,y0,x1,y1=sh.bounds
            cyb=(y0+y1)/2
            rot=int(el.get('data-rot'))
            # for S,H,C: upright centroid is above/below? record
        e=sorted((x,y) for x,y,_ in exp); g2=sorted((c[0],c[1]) for c in got)
        if len(e)!=len(g2) or any(abs(a[0]-b[0])>0.01 or abs(a[1]-b[1])>0.01 for a,b in zip(e,g2)):
            problems.append((p,'positions',e,g2))
        sizes={(c[2],c[3]) for c in got}
        rows.append((r+s,len(pips),sizes))
        for cls in ('index-rank','index-pip'):
            for corner in ('tl','br'):
                els=[el for el in root.iter(NS+'path') if el.get('class')==cls and el.get('data-corner')==corner]
                assert len(els)==1,(p,cls,corner,len(els))
                idx_boxes[(r+s,cls,corner)]=[round(v,2) for v in G.bbox(els[0].get('d'))]
for row in rows: print(row)
print("problems:",problems[:10], len(problems))
# index boxes summary
import collections
for s in "SHCD":
    print(s,'pip tl',idx_boxes[("2"+s,'index-pip','tl')],'br',idx_boxes[("2"+s,'index-pip','br')])
for r in ranks:
    bx={tuple(idx_boxes[(r+s,'index-rank','tl')]) for s in "SHCD"}
    print('rank',r,bx)
# verify br == rot180(tl)
bad=0
for k,v in idx_boxes.items():
    if k[2]=='tl':
        b=idx_boxes[(k[0],k[1],'br')]
        exp=[750-v[2],1050-v[3],750-v[0],1050-v[1]]
        if any(abs(a-c)>0.02 for a,c in zip(b,exp)): bad+=1; print('rot mismatch',k,v,b)
print('br!=rot180(tl):',bad)
