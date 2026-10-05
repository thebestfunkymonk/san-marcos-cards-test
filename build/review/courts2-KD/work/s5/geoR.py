import sys; sys.path.insert(0,'.')
import numpy as np
from deck import courtkit as K
import art.KD as KD
from art import _kd_body as B
KEY_X=KD.KEY_X; ARM_R=KD.ARM_R
WR=tuple(K.fist_wrist((KEY_X,384.0),-90.0,bend=ARM_R["bend"],dist=ARM_R["dist"],**KD.KEY_FIST))
BR=ARM_R["base"]
ur=(np.array(WR)-np.array(BR))/np.hypot(*(np.array(WR)-np.array(BR)))
WRc=tuple(np.array(WR)-np.array([ur[1],-ur[0]])*ARM_R["shift"])
slR,_=K.sleeve(K.SleeveSpec(base=BR,wrist=tuple(np.array(WRc)-ur*4.0-np.array([ur[1],-ur[0]])*2.0),sag=ARM_R["sag"],width=ARM_R["width"],wrist_w=ARM_R["wrist_w"],cuff=1.0,color=K.RED))
key_cut=K.box(0,0,750,750).difference(K.box(KEY_X-11.0,0,KEY_X+11.0,750).buffer(K.HALO+K.MEDIUM/2+K.MEDIUM/2))
cf=B.gauntlet(WRc,np.array(WRc)-np.array(BR),mirror=True,keep_in=key_cut,**KD.CUFF_R)
print("WR",WR,"WRc",WRc)
print(np.round(np.array(cf.shape.exterior.coords),1)[::3])
bd=slR.shape.exterior
for t in np.linspace(0,1,300):
    p=bd.interpolate(t,normalized=True)
    d=cf.shape.exterior.distance(p)
    if d<8 and not cf.shape.contains(p) and p.x<KEY_X-11-K.HALO: print(round(p.x,1),round(p.y,1),'d=',round(d,2))
