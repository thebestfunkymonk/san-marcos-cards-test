import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"cup":{"thumb_rim":-8.0, "thumb_tip": 12.0, "thumb_root": [-0.6, 0.12]}}')
def build():
    return KC.figure(OPTS).layers()
