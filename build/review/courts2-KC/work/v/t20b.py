import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"cup":{"thumb_tip":20.0,"thumb_root":[-0.4,0.12]}}')
def build():
    return KC.figure(OPTS).layers()
