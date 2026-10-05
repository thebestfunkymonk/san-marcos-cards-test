import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"robe":{"flute_kw":{"vy":-400.0,"widths":[34.0,10.0],"centre":30.0,"skip":[103.0,113.0,191.0,201.0]}}}')
def build():
    return KC.figure(OPTS).layers()
