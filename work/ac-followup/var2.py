"""variant with scratch reed_w.wreath: python work/ac-followup/var2.py NAME 'dict(kw...)'"""
import sys, os, subprocess
sys.path.insert(0, os.getcwd())
name, kw = sys.argv[1], sys.argv[2]
src = f'''
import sys
sys.path.insert(0, "work/ac-followup")
import reed_w as RW
from art import AC as _AC
from art import _aces_common as A
from deck import tokens as T
from deck.cardsvg import layers_merge
KW = {kw}
def build():
    pip = A.knocked_pip("C", _AC.spray(), color=T.INK)
    wr = A.behind(RW.wreath(_AC.CX, A.CY, KW.pop("r", 190.0), **KW), "C")
    gold = A.keyline("C") + wr + A.caption("C")
    return layers_merge((pip + gold).fragments())
'''
p = f"work/ac-followup/var_{name}.py"
open(p, "w").write(src)
subprocess.run([sys.executable, "work/ac-followup/render.py", name, p], check=True)
