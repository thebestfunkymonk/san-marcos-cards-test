import sys, os
sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
SBP='/home/luke/Projects/design/san-marcos-deck/build/review/specA/sb'
sys.path.insert(0, SBP); sys.modules.pop('art', None)
import art; print('art package from', art.__file__)
pid = sys.argv[1] if len(sys.argv)>1 else 'QH'
a=build(pid); w=build(pid,'white')
print('status', a['status'], (a.get('error') or '')[-600:])
r=check(a,w)
print(row(r))
for k,_ in Q.COLS:
    v=r.get(k) or {}
    if v.get('ok') in (False,'warn'): print(' ',k, v.get('detail')[:5])
print('balance', r['5'].get('balance'), 'gold', r['5'].get('gold_pct'), '10c', r['10c'])
print('png', a['png'])
