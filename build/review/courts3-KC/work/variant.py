"""usage: variant.py <name> '<json opts>' -> writes work/v/<name>.py that builds KC.figure(opts)"""
import sys, json, os
name, opts = sys.argv[1], sys.argv[2]
d = os.path.dirname(os.path.abspath(__file__))
open(os.path.join(d, 'v', name + '.py'), 'w').write(f'''import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads({opts!r})
def build():
    return KC.figure(OPTS).layers()
''')
