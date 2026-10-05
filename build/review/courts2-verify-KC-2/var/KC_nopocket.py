import os, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
from art import KC as _K
def build():
    return _K.figure({"pockets": False}).layers()
