import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"cup":{"thumb_rim":-9.0, "thumb_tip": 16.0, "thumb_root": [-0.75, 0.15]}}')
def build():
    return KC.figure(OPTS).layers()
