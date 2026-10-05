"""Draft wrapper: art/KH.py composed WITHOUT heal (looks only; not QA-valid)."""
import importlib, sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
import art.KH as KH
importlib.reload(KH)


def build():
    return KH.figure().layers(heal_gaps=False)
