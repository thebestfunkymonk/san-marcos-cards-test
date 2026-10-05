import sys, importlib; sys.path.insert(0,'.')
from art import KH
vals = [float(v) for v in sys.argv[1:]]
from deck import courtkit as K
for v in vals:
    KH.ROBE = K.MantleSpec(neck_y=v, neck_heading=170.0, run=140.0, corner_r=34.0, side_heading=97.0)
    sc = KH.figure(); res = sc.compose()
    log = [e for e in sc.heal_log if e['action'] != 'fill-hole' and e['role'] not in ('nose', 'lip', 'lion-nose')]
    print(v, len(log))
    for e in log: print('   ', e['action'], e['role'], e['at'], e['why'][:40], e.get('near'))
