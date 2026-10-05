"""Print QD's heal log summary (by part and near)."""
import collections, os, sys
ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + "/art")
import QD
sc = QD.figure(); sc.compose()
log = sc.heal_log
print("heal entries:", len(log))
if log and isinstance(log[0], dict):
    cnt = collections.Counter()
    for e in log:
        cnt[tuple((k, str(v)[:30]) for k, v in e.items() if k in ("kind", "role", "near", "action", "what"))] += 1
    for k, v in cnt.most_common(40):
        print(v, k)
    if "-v" in sys.argv:
        for e in log:
            print(e)
else:
    for e in log[:80]:
        print(e)
