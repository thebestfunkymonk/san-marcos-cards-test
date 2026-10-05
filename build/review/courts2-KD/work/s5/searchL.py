import sys, itertools; sys.path.insert(0,'.')
import numpy as np
from deck import courtkit as K
import art.KD as KD
from art import _kd_body as B
from shapely.geometry import Point, LineString
SASH=KD.SASH; su=(np.array(SASH[1])-np.array(SASH[0])); su/=np.hypot(*su); sn=np.array([su[1],-su[0]])
grip=np.array(SASH[0])+su*KD.GRIP_T-sn*(KD.SASH_W/2-KD.GRIP_IN)
fkw=dict(shaft_w=KD.GRIP_W,back=-1,h=KD.FIST["h"],reach=KD.FIST["reach"],knuckle=KD.FIST["knuckle"])
WL=np.array(K.fist_wrist(tuple(grip),KD.GRIP_AXIS,**KD.WRIST_L,**fkw)); BL=np.array(KD.ARM_L_BASE)
u=(WL-BL)/np.hypot(*(WL-BL)); n=np.array([u[1],-u[0]])
G=B.gauntlet(tuple(WL),WL-BL,**KD.CUFF_L).shape
nrm=n; a0,a1=WL+nrm*KD.CUFF_L['width']/2, WL-nrm*KD.CUFF_L['width']/2
Bc=WL-u*KD.CUFF_L['depth']; b0,b1=Bc+nrm*KD.CUFF_L['flare']/2, Bc-nrm*KD.CUFF_L['flare']/2
print('corners a0',a0.round(1),'a1',a1.round(1),'b0',b0.round(1),'b1',b1.round(1))
base_sl,_=K.sleeve(K.SleeveSpec(base=tuple(BL),wrist=tuple(WL),sag=6.0,width=64.0,wrist_w=38.0,cuff=1.0,color=K.RED))
vis0=base_sl.shape.difference(G)
def ev(k,t,w,s):
    W=WL-u*k+n*t
    sl,_=K.sleeve(K.SleeveSpec(base=tuple(BL),wrist=tuple(W),sag=s,width=64.0,wrist_w=w,cuff=1.0,color=K.RED))
    X=sl.shape.exterior.intersection(G.exterior)
    pts=[X] if X.geom_type=='Point' else list(getattr(X,'geoms',[]))
    pts=[p for p in pts if p.geom_type=='Point']
    if len(pts)!=2: return None
    cl=[]
    for p in pts:
        q=np.array(p.coords[0])
        # on the bottom edge? depth along u from WL
        dep=np.dot(WL-q,u)
        if dep<KD.CUFF_L['depth']-5: return None
        cl.append(min(np.hypot(*(q-b0)),np.hypot(*(q-b1))))
    vis=sl.shape.difference(G)
    # visible width just below the cuff: width across at depth+6
    return min(cl), cl, vis.symmetric_difference(vis0).area, [np.array(p.coords[0]).round(1) for p in pts]
res=[]
for k in [0,4,8,12,16]:
  for t in [-4,-2,0,2,4]:
    for w in range(26,40,2):
      for s in [0,2,4,6]:
        r=ev(k,t,w,s)
        if r and r[0]>=6.0: res.append((r[2],k,t,w,s,r[1],r[3]))
res.sort(key=lambda z:z[0])
for z in res[:25]: print(round(z[0]),z[1:5],np.round(z[5],1),z[6])
