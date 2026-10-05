import sys; sys.path.insert(0,'.')
import importlib
QH = importlib.import_module('art.QH')
sc = QH.figure(); res = sc.compose()
for e in sc.heal_log:
    if e.get('role') in ('outline','contour','current') and 380<=e['at'][0]<=470 and 150<=e['at'][1]<=260: print(e)
    if e.get('action') not in ('trim',) : 
        a=e['at']
        if 380<=a[0]<=470 and 150<=a[1]<=260: print('X', e)
