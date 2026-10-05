import sys; sys.path.insert(0,'.')
import numpy as np
from deck import courtkit as K
import art.KD as KD
from art import _kd_body as B
import shapely
from shapely.geometry import LineString, Point
SASH=KD.SASH; su=(np.array(SASH[1])-np.array(SASH[0])); su/=np.hypot(*su); sn=np.array([su[1],-su[0]])
grip=np.array(SASH[0])+su*KD.GRIP_T-sn*(KD.SASH_W/2-KD.GRIP_IN)
fkw=dict(shaft_w=KD.GRIP_W,back=-1,h=KD.FIST["h"],reach=KD.FIST["reach"],knuckle=KD.FIST["knuckle"])
WL=tuple(K.fist_wrist(tuple(grip),KD.GRIP_AXIS,**KD.WRIST_L,**fkw))
BL=KD.ARM_L_BASE
print("grip",grip,"WL",WL,"BL",BL)
sl,_=K.sleeve(K.SleeveSpec(base=BL,wrist=WL,sag=6.0,width=64.0,wrist_w=38.0,cuff=1.0,color=K.RED))
cf=B.gauntlet(WL,np.array(WL)-np.array(BL),**KD.CUFF_L)
print("gauntlet coords", np.round(np.array(cf.shape.exterior.coords)[::max(1,len(cf.shape.exterior.coords)//12)],1))
out=sl.shape.difference(cf.shape)
print("sleeve outside gauntlet near cuff:")
# check sleeve boundary distance to gauntlet boundary along the stretch
bd=sl.shape.exterior
for t in np.linspace(0,1,200):
    p=bd.interpolate(t,normalized=True)
    d=cf.shape.exterior.distance(p)
    inside=cf.shape.contains(p)
    if d<8 and not inside: print(round(p.x,1),round(p.y,1),'d=',round(d,2))
