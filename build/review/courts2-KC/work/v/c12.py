import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"fist_wrist":{"bend":50.0,"dist":0.85},"fist":{"wrist_w":26.0},"cup":{"fw":12.0}}')
def build():
    return KC.figure(OPTS).layers()
