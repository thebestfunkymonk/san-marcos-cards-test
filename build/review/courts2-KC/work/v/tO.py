import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"cup":{"thumb_root": [-0.3, 0.12], "thumb_rim": 2.0}}')
def build():
    return KC.figure(OPTS).layers()
