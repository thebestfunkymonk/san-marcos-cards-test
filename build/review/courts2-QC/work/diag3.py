import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
neck, rd = map(float, sys.argv[1:3])
QC.FAN_KW = dict(QC.FAN_KW, neck=neck, root_dy=rd)
sc, fc = QC.figure()
res = QC.Q.compose(sc)
n = 0
for e in sc.heal_log:
    x, y = e['at']
    if 270 <= x <= 330 and 350 <= y <= 400:
        print(' ', e); n += 1
print(neck, rd, 'near-ferrule heal entries', n, 'total', len(sc.heal_log))
