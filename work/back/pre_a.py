from art import _back_bough as BB, _back_rice as BR, _back_emblem as BE, _back_vent as BV, _back_geo as BG
BB.BOUGH["lenspar"]=dict(c=(181.8,525.0), radii=(262,294,326,358,390,422), sweep=80)
BB.BOUGH["tick"]=dict(tick=15.0, angle=45.0, pitch=9.8, stagger=True)
BB.BOUGH["pieces"]=True; BB.BOUGH["min_piece"]=40
for lf in BR.SHEAF["leaves"]: lf["w"]=26.0
_orig = BE.emblem
def emblem():
    d = _orig()
    d["vents"] = BG.c2(BV.vent())
    return d
BE.emblem = emblem
