import sys, warnings
sys.path.insert(0, 'art'); warnings.simplefilter('ignore')
from deck import courtkit as K
import JD
from shapely.geometry import Point, LineString
sc = JD.figure()
items = {i.name: i for i in sc.items}
for c in ('cuffR','cuffL'):
    occ = items[c].occ
    g = occ.simplify(0.5)
    print(c, [tuple(round(v,1) for v in p) for p in g.exterior.coords])
belt = items['belt'].occ
print('belt bounds', [round(v,1) for v in belt.bounds])
# distance from cuffR corners to belt top line
bt = LineString([(250,441),(520,441)])
for p in items['cuffR'].occ.simplify(0.5).exterior.coords:
    d = bt.distance(Point(p))
    if d < 3: print('cuffR vertex near belt top', tuple(round(v,1) for v in p), round(d,2))
bb = LineString([(250,473),(520,473)])
for p in items['cuffR'].occ.simplify(0.5).exterior.coords:
    d = bb.distance(Point(p))
    if d < 3: print('cuffR vertex near belt bottom', tuple(round(v,1) for v in p), round(d,2))
print('map occ', [round(v,1) for v in items['map'].occ.bounds])
print('handL occ', [round(v,1) for v in items['handL'].occ.bounds])
