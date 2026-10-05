import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"robe":{"flute_kw":{"vy":-400.0,"widths":[34.0,10.0],"centre":30.0,"skip":[]}},"pockets":false}')
def build():
    return KC.figure(OPTS).layers()
