import sys, warnings; sys.path.insert(0,'.'); warnings.simplefilter('ignore')
import art.KH as KH
variants = {
 'a': [((-36.0, 30.0), (-41.2, 60.0), (-37.0, 88.0), -180.0, 4.8)],
 'b': [((-36.0, 30.0), (-41.4, 57.0), (-38.5, 81.0), -180.0, 4.8)],
 'c': [((-36.0, 30.0), (-41.2, 60.0), (-36.0, 86.0), -200.0, 4.2)],
 'd': [((-36.0, 30.0), (-41.0, 56.0), (-38.0, 78.0), -190.0, 4.8)],
 'e': [((-36.0, 30.0), (-41.2, 59.0), (-37.0, 85.0), -180.0, 4.4)],
}
l2 = ((-19.0, 76.0), (-18.4, 89.0), (-14.5, 99.0), -180.0, 4.0)
for k, v in variants.items():
    KH.BEARD_LOCKS = {'mode': 'manual', 'locks': v + [l2]}
    sc = KH.figure(); sc.layers()
    hits = [(e['action'], e['role'], [round(x, 1) for x in e['at']], e.get('near')) for e in sc.heal_log
            if e['role'] in ('current', 'terminal') or (380 < e['at'][0] < 430 and 280 < e['at'][1] < 310)]
    print(k, hits)
