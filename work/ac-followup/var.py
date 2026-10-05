"""variant: python work/ac-followup/var.py NAME 'dict(kw...)' ['dict(spike...)'] [r]"""
import sys, os, subprocess
sys.path.insert(0, os.getcwd())
name, kw = sys.argv[1], sys.argv[2]
spike = sys.argv[3] if len(sys.argv) > 3 else "None"
r = sys.argv[4] if len(sys.argv) > 4 else "190.0"
src = f'''
from art import AC as _AC
from art import _aces_common as A
from art import _aces_reed as R
from deck import tokens as T
from deck.cardsvg import layers_merge
KW = {kw}
def build():
    pip = A.knocked_pip("C", _AC.spray(), color=T.INK)
    wr = A.behind(R.wreath(_AC.CX, A.CY, {r}, spike={spike}, **KW), "C")
    gold = A.keyline("C") + wr + A.caption("C")
    return layers_merge((pip + gold).fragments())
'''
p = f"work/ac-followup/var_{name}.py"
open(p, "w").write(src)
subprocess.run([sys.executable, "work/ac-followup/render.py", name, p], check=True)
