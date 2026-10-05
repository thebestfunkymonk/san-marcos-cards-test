"""Geometry proof for creative-brief.md: index, pip layouts, court frame + divider.
Pip silhouettes here are the construction described in brief section E (draft quality).
Run: .venv/bin/python research/creative-brief-layout.py && rsvg-convert research/creative-brief-layout.svg -o research/creative-brief-layout.png
"""
import sys, math
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from shapely.geometry import Point, Polygon, box
from shapely.ops import unary_union
from shapely import affinity
from inkkit.typeset import text_to_path, font_metrics
import os
S=os.path.dirname(os.path.abspath(__file__))+"/"
INK="#15242B"; RED="#AE2F2B"; PAPER="#F4EFE3"; JADE="#1D5A55"; GOLD="#B08D57"
def tangent_pts(c, r, p):
    # tangent points from external point p to circle (c,r)
    dx,dy=p[0]-c[0],p[1]-c[1]; d=math.hypot(dx,dy); a=math.acos(r/d); b=math.atan2(dy,dx)
    return [(c[0]+r*math.cos(b+a),c[1]+r*math.sin(b+a)),(c[0]+r*math.cos(b-a),c[1]+r*math.sin(b-a))]
def heart_unit():
    # width 1.00, height 0.92, top at y=0, centred x=0
    r=0.26; cl=(-0.24,0.26); cr=(0.24,0.26); p=(0,0.92)
    L=Point(cl).buffer(r,256); R=Point(cr).buffer(r,256)
    tl=tangent_pts(cl,r,p); tr=tangent_pts(cr,r,p)
    tl=min(tl,key=lambda q:q[0]); tr=max(tr,key=lambda q:q[0])
    tri=Polygon([tl,p,tr,(0.24,0.26),(-0.24,0.26)])
    return unary_union([L,R,tri,Polygon([(-0.24,0.26),(0.24,0.26),(0,0.6)])])
def plinth(y0, u=1.0):
    return unary_union([box(-0.13,y0,0.13,y0+0.05), box(-0.18,y0+0.05,0.18,y0+0.10)])
def spade_unit():
    h=affinity.scale(heart_unit(),1,-0.87,origin=(0,0)); h=affinity.translate(h,0,0.80)  # point up, body 0.80 tall
    stem=Polygon([(-0.035,0.62),(0.035,0.62),(0.10,1.00),(-0.10,1.00)])
    return unary_union([h,stem,plinth(1.00)])
def club_unit():
    r=0.245
    cs=[Point(0,r).buffer(r,256),Point(-0.275,0.53).buffer(r,256),Point(0.275,0.53).buffer(r,256)]
    core=Polygon([(0,0.30),(-0.2,0.55),(0.2,0.55)])
    stem=Polygon([(-0.035,0.55),(0.035,0.55),(0.10,0.94),(-0.10,0.94)])
    return unary_union(cs+[core,stem,plinth(0.94)])
def diamond_unit():
    w,h=0.80,1.12; pts=[(0,0),(w/2,h/2),(0,h),(-w/2,h/2)]
    # concave sides: sample arcs with 3% sagitta
    out=[]
    for i in range(4):
        a=pts[i]; b=pts[(i+1)%4]; L=math.hypot(b[0]-a[0],b[1]-a[1]); s=0.03*L
        mx,my=(a[0]+b[0])/2,(a[1]+b[1])/2; nx,ny=-(b[1]-a[1])/L,(b[0]-a[0])/L
        # inward normal points to centre (0,h/2)
        if (0-mx)*nx+(h/2-my)*ny<0: nx,ny=-nx,-ny
        for k in range(24):
            t=k/24; x=a[0]+(b[0]-a[0])*t; y=a[1]+(b[1]-a[1])*t; off=4*s*t*(1-t)
            out.append((x+nx*off,y+ny*off))
    return Polygon(out)
SH={"S":spade_unit(),"H":heart_unit(),"C":club_unit(),"D":diamond_unit()}
def d_of(g):
    polys=[g] if g.geom_type=="Polygon" else list(g.geoms)
    s=""
    for p in polys:
        for ring in [p.exterior]+list(p.interiors):
            c=list(ring.coords); s+="M"+"L".join(f"{x:.2f} {y:.2f}" for x,y in c)+"Z"
    return s
def pip(suit, cx, cy, u, rot=False):
    if suit=='H': u*=1.04
    g=SH[suit]; minx,miny,maxx,maxy=g.bounds
    g=affinity.scale(g,u,u,origin=(0,0)); g=affinity.translate(g,cx,cy-(miny+maxy)/2*u)
    if rot: g=affinity.rotate(g,180,origin=(cx,cy))
    return g
COLX=(222,375,528); T,B=198,852
rows4=[T+(B-T)*k/3 for k in range(4)]
LAY={2:[(375,T),(375,B)],3:[(375,T),(375,525),(375,B)],4:[(222,T),(528,T),(222,B),(528,B)]}
LAY[5]=LAY[4]+[(375,525)]
LAY[6]=[(x,y) for x in (222,528) for y in (T,525,B)]
LAY[7]=LAY[6]+[(375,(T+525)/2)]
LAY[8]=LAY[7]+[(375,(B+525)/2)]
LAY[9]=[(x,y) for x in (222,528) for y in rows4]+[(375,525)]
LAY[10]=[(x,y) for x in (222,528) for y in rows4]+[(375,(rows4[0]+rows4[1])/2),(375,(rows4[2]+rows4[3])/2)]
FONT="BarlowCondensed-SemiBold.ttf"; VAR=None
m=font_metrics(FONT,VAR); SIZE=96/(m["capHeight"]/m["upm"])
AXIS=84; CAPTOP=46; BASE=142
def index(rank,suit,col):
    tr=-20 if rank=="10" else 0
    d,bb,adv=text_to_path(FONT,rank,SIZE,0,BASE,variations=VAR,tracking=tr)
    w=bb[2]-bb[0]; tx=AXIS-w/2-bb[0]
    p=pip(suit,AXIS,0,62); mnx,mny,mxx,mxy=p.bounds; p=affinity.translate(p,0,154-mny)
    g=f'<path d="{d}" transform="translate({tx:.2f},0)" fill="{col}"/><path d="{d_of(p)}" fill="{col}"/>'
    return g+f'<g transform="rotate(180 375 525)">{g}</g>', (bb[0]+tx,bb[2]+tx), p.bounds
def card(rank,suit):
    col=INK if suit in "SC" else RED
    body=f'<rect width="750" height="1050" rx="37.5" fill="{PAPER}"/>'
    ix,xr,pb=index(str(rank) if isinstance(rank,int) else rank,suit,col)
    body+=ix
    if isinstance(rank,int):
        u=116
        for (x,y) in LAY[rank]:
            body+=f'<path d="{d_of(pip(suit,x,y,u,rot=y>525.5))}" fill="{col}"/>'
    else:
        c=18
        def cham(x0,y0,x1,y1,c):
            return f"M{x0+c} {y0}H{x1-c}L{x1} {y0+c}V{y1-c}L{x1-c} {y1}H{x0+c}L{x0} {y1-c}V{y0+c}Z"
        body+=f'<path d="{cham(128,44,622,1006,18)}" fill="none" stroke="{INK}" stroke-width="4.2" stroke-linejoin="miter"/>'
        body+=f'<path d="{cham(135,51,615,999,15.1)}" fill="none" stroke="{GOLD}" stroke-width="2.1" stroke-linejoin="miter"/>'
        p=pip(suit,0,0,88); mnx,mny,mxx,mxy=p.bounds; p=affinity.translate(p,146-mnx,62-mny)
        body+=f'<path d="{d_of(p)}" fill="{col}"/><path d="{d_of(affinity.rotate(p,180,origin=(375,525)))}" fill="{col}"/>'
        body+=f'<path d="M135 511H615M135 539H615" stroke="{INK}" stroke-width="2.1"/>'
        body+=f'<circle cx="375" cy="525" r="28" fill="{PAPER}" stroke="{INK}" stroke-width="2.1"/><circle cx="375" cy="525" r="22" fill="none" stroke="{GOLD}" stroke-width="2.1"/>'
        body+='<rect x="139" y="55" width="472" height="456" fill="none" stroke="#1D5A55" stroke-width="1" stroke-dasharray="3 3"/>'
    body+='<rect x="37.5" y="37.5" width="675" height="975" fill="none" stroke="#e0a" stroke-width="1" stroke-dasharray="6 4"/>'
    return body, xr
cards=[(10,"S"),(10,"H"),(9,"C"),(8,"D"),(7,"H"),(6,"C"),(5,"S"),(3,"D"),("K","S"),("Q","H"),("J","C"),("A","D")]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d"><rect width="100%%" height="100%%" fill="#333"/>'%(6*385+10,2*535+10)]
for k,(r,s) in enumerate(cards):
    b,xr=card(r,s); rr,cc=divmod(k,6)
    svg.append(f'<g transform="translate({10+cc*385},{10+rr*535}) scale(0.5)">{b}</g>')
    print(r,s,"index x-extent",[round(v,1) for v in xr])
svg.append("</svg>"); open(S+"creative-brief-layout.svg","w").write("".join(svg))
for s in "SHCD":
    g=SH[s]; print(s,"unit bounds",[round(v,3) for v in g.bounds])
