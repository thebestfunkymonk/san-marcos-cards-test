import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"orb":{"stem":[-1.0,7.5],"stem_w":[6.6,7.6]}}')
def build():
    return KC.figure(OPTS).layers()
