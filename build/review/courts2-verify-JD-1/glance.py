import sys, collections
from deck import qa
import shapely
s=open(sys.argv[1]).read()
P=qa.card_geometry(s)
ink=[p for p in P if p["layer"]=="ink" and p["geom"].bounds[3]<=511.5 and p["kind"]!="fill"]
byel=collections.defaultdict(list)
for p in ink: byel[p["el"]].append(p["geom"])
G={k:shapely.union_all(v) for k,v in byel.items()}
ks=list(G); tree=shapely.STRtree([G[k] for k in ks])
for k in ks:
    for j in tree.query(G[k]):
        k2=ks[j]
        if k2<=k: continue
        x=G[k].intersection(G[k2])
        for q in getattr(x,'geoms',[x]):
            if not q.is_empty and 0<q.area<2.5:
                b=q.bounds
                if b[1]>55 and b[3]<511 and 139<b[0]<611:
                    print(k,k2,[round(v,1) for v in b],round(q.area,2))
