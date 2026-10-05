import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"fist_wrist":{"bend":45.0,"dist":1.0},"sleeveR":{"wrist_w":32.0}}')
def build():
    return KC.figure(OPTS).layers()
