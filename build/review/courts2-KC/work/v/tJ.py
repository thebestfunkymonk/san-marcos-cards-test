import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"cup":{"thumb_rim":-12.0, "thumb_tip": 6.0, "thumb_root": [-1.0, 0.2]}}')
def build():
    return KC.figure(OPTS).layers()
