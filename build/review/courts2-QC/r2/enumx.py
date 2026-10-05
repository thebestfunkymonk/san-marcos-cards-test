import sys, pickle
exec(open("build/review/courts2-QC/r2/packx.py").read().split("t = time.time()")[0])
pack.update(gap=-1.0, max_n=100000)
lf, placed = GW.leaf_pack(allowed, soft=soft, tip_zone=tz, **pack)
print(len(placed))
pickle.dump([(tuple(b), L, W, bd, pg) for b, L, W, bd, pg in placed], open(sys.argv[1][:-4] + ".pkl", "wb"))
# best pairs
import itertools
best = []
for (i, a), (j, b) in itertools.combinations(enumerate(placed), 2):
    if a[4].distance(b[4]) >= 6.6:
        best.append((a[1] + b[1], i, j))
best.sort(reverse=True)
for s_, i, j in best[:15]:
    a, b = placed[i], placed[j]
    print(s_, [(tuple(round(v) for v in x[0]), x[1]) for x in (a, b)])
