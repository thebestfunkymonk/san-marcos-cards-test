import os, sys, json
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import art.QH as Q
ov = json.loads(os.environ.get('QHV', '{}'))
for k, v in ov.items():
    cur = getattr(Q, k)
    if isinstance(cur, dict):
        setattr(Q, k, {**cur, **v})
    elif isinstance(cur, tuple) and k == 'PETAL_ROWS':
        setattr(Q, k, tuple(v))
    else:
        setattr(Q, k, tuple(v) if isinstance(v, list) else v)
def build():
    return Q.figure().layers()
