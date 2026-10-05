import sys; sys.path.insert(0,'/home/luke/Projects/design/san-marcos-deck/build/review/specA')
from harness import *
import time
for pid in ['10S','7H','9C','8D','QD','JS','KH']:
    t=time.time()
    a=build(pid); w=build(pid,'white')
    r=check(a,w)
    print(pid, a['status'], row(r), round(time.time()-t,1),'s')
    bad={k:v for k,v in details(r,[k for k,_ in Q.COLS]).items() if v and (r.get(k) or {}).get('ok') in (False,'warn')}
    if bad: print('   ',bad)
