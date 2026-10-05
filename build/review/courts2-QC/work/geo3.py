import sys, os, itertools
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
sc, fc = QC.figure()
it = {i.name: i for i in sc.items}
hair = it['hairR'].occ
cloak = it['cloak'].occ
base = dict(QC.SCEPTRE)
arm0 = base['arms'][0]
def test(ky, khw, pieces, tipf=(22.0,7.6), flor=None, h0=62.0):
    spec = dict(base); spec['knop_y']=ky; spec['knop_hw']=khw
    a = list(arm0); a[1]=h0; a[2]=pieces; a[5]=tipf
    if flor: a[4]=flor
    spec['arms']=(tuple(a),)
    sp = QC.S.rice_sceptre(QC.SCEPTRE_X, **spec)
    kn = K.R(K.rrect(541-khw, ky-6, 541+khw, ky+6, 5.5))
    head = sp.meta['head']
    dk = min(g.distance(kn) for g in K._polys_of(head) if g.distance(kn) > 0 and g.bounds[3] > 230)
    dh = head.distance(hair)
    dc = head.distance(cloak.exterior)
    bb = [round(v,1) for v in head.bounds]
    # cloak line clearance from knop bottom
    print(f"ky {ky} khw {khw} pieces {pieces} h0 {h0} tip {tipf}: floret-knop {dk:.2f}  head-hair {dh:.2f}  head-cloak {dc:.2f} bounds {bb}")
for ky, khw in ((281,13),(270,13),(270,12),(270.5,11.5),(270,11)):
    test(ky, khw, ((18.0,50.0),(32.0,60.0),(12.0,30.0)))
for pieces in (((18.0,50.0),(32.0,60.0),(6.0,30.0)), ((18.0,50.0),(30.0,60.0),(8.0,30.0)), ((18.0,48.0),(30.0,64.0),(8.0,30.0)),
               ((16.0,50.0),(30.0,62.0),(8.0,28.0)), ((18.0,50.0),(28.0,64.0),(10.0,30.0))):
    test(270.5, 11.5, pieces)
test(270.5, 11.5, ((18.0,50.0),(32.0,60.0),(12.0,30.0)), h0=66.0)
test(270.5, 11.5, ((18.0,50.0),(32.0,60.0),(12.0,30.0)), tipf=(18.0,7.6))
print('---')
fl0 = arm0[4]
for fr in ((0.35,0.61),(0.38,0.63),(0.40,0.64),(0.37,0.62)):
    flor = tuple((f,)+tuple(x[1:]) for f, x in zip(fr, fl0))
    for pieces in (((18.0,50.0),(28.0,64.0),(10.0,30.0)), ((18.0,48.0),(30.0,64.0),(8.0,30.0)), ((19.0,50.0),(29.0,64.0),(9.0,30.0))):
        test(270.5, 11.5, pieces, flor=flor)
print('===')
for fr in ((0.40,0.64),(0.42,0.65),(0.41,0.66)):
    flor = tuple((f,)+tuple(x[1:]) for f, x in zip(fr, fl0))
    for pieces in (((19.0,50.0),(29.0,64.0),(9.0,30.0)),):
        test(270.5, 13, pieces, flor=flor)
