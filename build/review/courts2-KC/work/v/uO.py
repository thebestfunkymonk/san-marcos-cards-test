import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"cup":{"thumb_rim":4.0, "thumb_tip": 18.5}}')
def build():
    return KC.figure(OPTS).layers()
