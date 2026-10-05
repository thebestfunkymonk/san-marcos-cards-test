exec(open('work/back/pre_h.py').read())
BB.BOUGH["lenspar"]=dict(c=(181.8,525.0), radii=(258,282,306,330,354,378,402,426), sweep=80)
BB.BOUGH["tick"]=dict(tick=12.5, angle=48.0, pitch=8.8)
BB.BOUGH["lead"]=dict(len=150.0, tick=11.0, pitch=8.8, sides=(1,), angle=48.0)
BB.BOUGH["min_piece"]=36
for lf in BR.SHEAF["leaves"]: lf["w"] = lf["w"] + 4
from art import _back_frame as BF
BF.FIELD["solid"]=7
