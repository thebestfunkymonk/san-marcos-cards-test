import sys, warnings
sys.path.insert(0, 'art'); warnings.simplefilter('ignore')
from deck import courtkit as K
import JD
sc = JD.figure()
print([it.name for it in sc.items])
for it in sc.items:
    if it.name.startswith('hand'):
        print('==', it.name, 'occ', it.occ.bounds if it.occ is not None else None)
        for m in it.frag.marks:
            print('  ', m.role, getattr(m,'layer',None), getattr(m,'sw',None), getattr(m,'kind',None), m.d[:90])
