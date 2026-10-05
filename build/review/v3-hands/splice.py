"""Splice build/review/v3-hands/sec7_dev.py into deck/courtkit.py between the §7 and §8 headers."""
import os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
KP = os.path.join(ROOT, "deck", "courtkit.py")
DEV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sec7_dev.py")
L = open(KP).read().split("\n")
i = [k for k, l in enumerate(L) if l.startswith("# 7  hands")][0] - 1
j = [k for k, l in enumerate(L) if l.startswith("# 8  garments")][0] - 1
assert L[i].startswith("# ====") and L[j].startswith("# ====")
new = open(DEV).read().rstrip("\n").split("\n")
L = L[:i] + new + ["", ""] + L[j:]
open(KP, "w").write("\n".join(L))
print(f"spliced §7: {len(new)} lines")
