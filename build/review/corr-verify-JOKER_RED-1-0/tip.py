import sys; sys.path.insert(0,'.')
exec(open(sys.argv[1]).read().split("print('---- band')")[0].replace("print(", "(lambda *a, **k: None)("))
c = np.array(ctr) + (dx, dy)
for end, rng in (('ear', np.arange(31.3, 40.0, 0.5)), ('leg', np.arange(80.0, 86.3, 0.5))):
    print(end)
    for a in rng:
        d = np.array([math.cos(math.radians(a)), math.sin(math.radians(a))])
        ln = shapely.LineString([c + d*(R-20), c + d*(R+5)])
        s = ln.intersection(col)
        p = c + d*R
        print('  angle %.1f  arc pos (%.1f,%.1f) radial gold %.2f' % (a, p[0], p[1], s.length))
# inscribed width via erosion
for w in (1.6, 3.1):
    er = col.buffer(-w/2).buffer(w/2)
    lost = col.difference(er)
    parts = [g for g in getattr(lost,'geoms',[lost]) if g.area > 0.3]
    print('gold thinner than', w, [(round(g.centroid.x,1), round(g.centroid.y,1), round(g.area,2), round(g.length/2,1)) for g in parts])
# crossing angle between band's outer edge and the ear gap line near the tip
