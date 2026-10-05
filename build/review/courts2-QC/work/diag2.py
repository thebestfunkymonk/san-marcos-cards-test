import sys, os
sys.path.insert(0, os.path.abspath('art')); sys.path.insert(0, os.path.abspath('.'))
import QC
from deck import courtkit as K
def fg(sc, parts=None):
    for nm, part in (parts or QC.FN.fan(QC.FIST_L, QC.FAN_AXIS, QC.PLUMES, **QC.FAN_KW)):
        sc.part(nm, part)
if len(sys.argv) > 1 and sys.argv[1] == 'nohalo':
    QC.fan_group = fg
sc, fc = QC.figure()
res = QC.Q.compose(sc)
x0, y0, x1, y1 = map(float, sys.argv[2].split(',')) if len(sys.argv) > 2 else (280, 365, 320, 400)
for e in sc.heal_log:
    x, y = e['at']
    if x0 <= x <= x1 and y0 <= y <= y1:
        print(e)
