import sys, json
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import importlib
from art import KC
OPTS = json.loads('{"orb_drop": [[270.0,427.5],[328.2,429.3],[326.6,440.2],[331.7,436.3],[268.3,395.1],[331.1,399.1]]}')
def build():
    return KC.figure(OPTS).layers()
