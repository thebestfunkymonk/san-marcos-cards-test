import sys, os, warnings, traceback
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
from deck import build as B
for pid in ["KS","QS","JS","KH","QH","JH","KC","QC","JC","KD","QD","JD"]:
    try:
        mod = B.load_art(pid)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            r = mod.figure() if hasattr(mod, "figure") else mod.build()
        hw = [str(x.message)[:110] for x in w if "Hand" in type(x.message).__name__]
        print(pid, "OK", len(hw), "hand warnings", hw[:3])
    except Exception as e:
        print(pid, "FAIL", type(e).__name__, e); traceback.print_exc(limit=2)
