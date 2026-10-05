import os, sys, json
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck')
import art.KH as Q
ov = json.loads(os.environ.get('KHV', '{}'))
for k, v in ov.items():
    cur = getattr(Q, k)
    if isinstance(cur, dict) and isinstance(v, dict):
        setattr(Q, k, {**cur, **v})
    else:
        setattr(Q, k, tuple(v) if isinstance(v, list) else v)
def build():
    return Q.figure().layers()
