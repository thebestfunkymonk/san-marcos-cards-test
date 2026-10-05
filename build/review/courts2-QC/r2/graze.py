import sys
sys.argv = [sys.argv[0], "/dev/null"] + sys.argv[1:]
exec(open("build/review/courts2-QC/r2/packx.py").read().split("def d(g)")[0])
soft_r = K.R(soft)
for r in (3.0, 4.2):
  for b, L, W, bd, pg in placed:
    vis = pg.difference(soft_r)
    near = soft_r.buffer(r + 1.0)
    both = pg.union(soft_r)
    gap = both.buffer(r, quad_segs=8).buffer(-r, quad_segs=8).difference(both).intersection(pg.buffer(r + 1.0))
    thin = vis.difference(vis.buffer(-r, quad_segs=8).buffer(r, quad_segs=8)).intersection(near)
    print(r, "leaf", tuple(round(v) for v in pg.bounds), "gap", [(round(g.area,1), tuple(round(v) for v in g.bounds)) for g in K._polys_of(gap) if g.area > 2],
          "thin", [(round(g.area,1), tuple(round(v) for v in g.bounds)) for g in K._polys_of(thin) if g.area > 2])
