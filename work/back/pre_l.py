exec(open('work/back/pre_k.py').read())
BB.BOUGH["tick"]=dict(tick=15.0, angle=50.0, pitch=8.4)
BB.BOUGH["lenspar"]=dict(c=(181.8,525.0), radii=(262,288,314,340,366,392,418), sweep=80)
for lf, w in zip(BR.SHEAF["leaves"], (26.0, 30.0, 30.0)): lf["w"] = w
BF.FIELD["solid"]=6
from art import _back_emblem as BE
BE.BUBBLES["n"]=4; BE.BUBBLES["min_r"]=15.0
