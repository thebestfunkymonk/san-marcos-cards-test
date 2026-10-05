import warnings
from art import JH
from deck import courtkit as K
import shapely
from shapely.geometry import LineString, box
sc = JH.figure()
items = {it.name: it for it in sc.items}
print([ (it.name, round(it.occ.area,1) if it.occ is not None and not it.occ.is_empty else None) for it in sc.items])
def b(n):
    o=items[n].occ; print(n, [round(v,1) for v in o.bounds])
for n in ["handR","cuffR","forearmR","fiddle-body","fiddle-neck","handL","cuffL","forearmL","bow","tunic","sleeveR","sleeveL","sash"]:
    if n in items: b(n)
cuff=items["cuffR"].occ; body=items["fiddle-body"].occ; hand=items["handR"].occ; neck=items["fiddle-neck"].occ
print("cuffR-body dist", cuff.distance(body), "overlap", round(cuff.intersection(body).area,1))
print("handR-body dist", round(hand.distance(body),2))
# visible cuff = cuff minus neck/hand/body
vis = cuff.difference(K.U(neck, hand, body))
print("visible cuff bounds", [round(v,1) for v in vis.bounds], round(vis.area,1))
fa=items["forearmR"].occ
visfa = fa.difference(K.U(neck,hand,body,cuff))
print("visible forearmR", [round(v,1) for v in visfa.bounds] if not visfa.is_empty else None, round(visfa.area,1))
# neck visible between hand and body
nv = neck.difference(K.U(hand, body))
for g in K._polys_of(nv):
    print(" neck vis piece", [round(v,1) for v in g.bounds], round(g.area,1))
