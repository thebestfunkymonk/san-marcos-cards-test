import sys, json; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jc/lab")
from facelab import *
import _jc_paddle as PD
V = json.loads(sys.argv[2])
tiles = []
for i, v in enumerate(V):
    sc = K.Scene(rank="J")
    fn = PD.paddle3 if v.pop("v3", True) else PD.paddle
    sc.part("paddle", fn(548.0, **v))
    K.fist((548.0, 408.0), -90.0, shaft_w=22.0, back=-1, wrist=(524.0, 440.0), wrist_w=26.0, h=36.0).add_to(sc, "handR", halo=0.0)
    p = os.path.join(OUT, f"{sys.argv[1]}{i}.png")
    render([sc.compose()], (500, 90, 600, 470), p, 100)
    tiles.append(p)
subprocess.run(["magick", *tiles, "+append", os.path.join(OUT, f"{sys.argv[1]}.png")], check=True)
subprocess.run(["magick", os.path.join(OUT, f"{sys.argv[1]}.png"), "-resize", "25%", "-filter", "point", "-resize", "400%", os.path.join(OUT, f"{sys.argv[1]}_s.png")], check=True)
