import numpy as np
from art import JH
from deck import courtkit as K
import shapely
from shapely.geometry import LineString, box, Point
sc = JH.figure()
it = {i.name: i for i in sc.items}
cuff=it["cuffR"].occ; body=it["fiddle-body"].occ; fa=it["forearmR"].occ; neck=it["fiddle-neck"].occ; hand=it["handR"].occ
# body contour points near x 535-575
bc = np.asarray(body.exterior.coords)
sel = bc[(bc[:,0]>530)&(bc[:,0]<580)&(bc[:,1]<320)]
print("body top contour pts:"); print(np.round(sel[np.argsort(sel[:,0])],1)[::3])
cc = np.asarray(cuff.exterior.coords)
print("cuff pts:"); print(np.round(cc,1)[::2])
# crossing of cuff boundary with body boundary
x = cuff.exterior.intersection(body.exterior)
print("cuff/body boundary crossings:", x)
# visible jade forearm piece
vis = fa.difference(K.U(neck,hand,body,cuff))
for g in K._polys_of(vis):
    print("vis forearm", [round(v,1) for v in g.bounds], round(g.area,1), "min width ~", round(2*max(0,max([g.buffer(-w).area>0 and w or 0 for w in np.arange(0.2,10,0.2)])),1))
# ink-free width of the visible jade wedge between cuff contour and body contour (strokes CONTOUR 6.25)
inner = vis.buffer(-K.CONTOUR/2)
print("jade after contour strokes:", round(inner.area,1), [round(v,1) for v in inner.bounds] if not inner.is_empty else None)
