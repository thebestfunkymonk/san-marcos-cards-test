import sys; sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/jh/exp")
from part import show
from art import _jh_parts as JP
import subprocess
tiles = []
for i, (h, turns, kw) in enumerate([(-75, [(150, 45), (80, 55), (44, 60), (30, 40)], dict(hw_max=22, belly=0.42, stagger=12, locks=5, lock_depth=7, n=3, lock_from=0.25, root_hw=5)),
                                  (-80, [(130, 55), (70, 60), (40, 60), (28, 40)], dict(hw_max=22, belly=0.42, stagger=12, locks=6, lock_depth=6.5, n=3, lock_from=0.22, root_hw=5)),
                                  (-85, [(120, 60), (80, 50), (44, 70)], dict(hw_max=21, belly=0.4, stagger=12, locks=5, lock_depth=7, n=3, lock_from=0.25, root_hw=5))]):
    pl = JP.plume((382, 184), h, turns, **kw)
    print(i, pl.meta["n_lines"], [round(v) for v in pl.shape.bounds])
    show([pl], (330, 40, 530, 200), f"plume{i}", 400)
    tiles.append(f"work/jh/exp/plume{i}.png")
subprocess.run(["magick", *tiles, "+append", "work/jh/exp/plume.png"])
