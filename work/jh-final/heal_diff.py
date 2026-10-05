import sys; sys.path.insert(0,'.'); sys.path.insert(0,'work/jh-final')
import importlib
def log(modname):
    M = importlib.import_module(modname)
    sc = M.figure(); sc.compose()
    return [(e['action'], e['role'], tuple(round(v) for v in e['at']), tuple(e.get('near', []))) for e in sc.heal_log]
a = log('jhorig.JH'); b = log('art.JH')
sa, sb = set(a), set(b)
print('baseline', len(a), 'now', len(b))
print('NEW:'); [print(' ', x) for x in b if x not in sa]
print('GONE:'); [print(' ', x) for x in a if x not in sb]
