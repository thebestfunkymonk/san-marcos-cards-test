"""tryvar.py 'python-assignments' ... : apply to art.KH, build SVG to a temp file, print exact balance + heal log size."""
import sys, subprocess, os
sys.path.insert(0, '.')
from art import KH
from deck import courtkit as K
import numpy as np
for spec in sys.argv[1:]:
    import importlib
    importlib.reload(KH)
    exec(spec, KH.__dict__)
    sc = KH.figure(); res = sc.compose()
    log = [e for e in sc.heal_log if e['action'] != 'fill-hole' and e['role'] not in ('nose', 'lip', 'lion-nose')]
    print(spec, '| heal', len(log))
    for e in log: print('   ', e['action'], e['role'], e['at'], e['why'][:40], e.get('near'))
