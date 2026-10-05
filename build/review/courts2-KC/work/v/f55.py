import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"fist_wrist":{"bend":55.0,"dist":0.95}}')
def build():
    return KC.figure(OPTS).layers()
