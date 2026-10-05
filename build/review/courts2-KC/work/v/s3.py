import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"orb":{"stem":[-2.0,10.0],"stem_w":[7.4,9.0]}}')
def build():
    return KC.figure(OPTS).layers()
