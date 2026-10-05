exec(open('work/back/pre_h.py').read())
BB.BOUGH["lenspar"]=dict(c=(181.8,525.0), radii=(262,288,314,340,366,392,418), sweep=80)
BB.BOUGH["tick"]=dict(tick=13.5, angle=50.0, pitch=8.4)
BB.BOUGH["lead"]=dict(len=150.0, tick=12.0, pitch=8.4, sides=(1,), angle=50.0)
BB.BOUGH["min_piece"]=36
BR.SHEAF["leaves"]=[
    dict(at=95.0, way=[(228.0, 302.0), (242.0, 318.0), (250.0, 336.0)], w=24.0, hatch=1),
    dict(at=40.0, way=[(198.0, 272.0), (204.0, 296.0), (210.0, 322.0), (214.0, 345.0)], w=28.0, hatch=1),
    dict(at=4.0, way=[(168.0, 256.0), (169.0, 285.0), (171.0, 318.0), (173.0, 342.0), (174.0, 357.0)], w=28.0, hatch=1),
]
from art import _back_frame as BF
BF.FIELD["solid"]=5
