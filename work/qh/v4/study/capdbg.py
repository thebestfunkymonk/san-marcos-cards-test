import sys
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck")
sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study")
from render import render
from deck import courtkit as K
from art import _qh_cap as CP
import cap1
v = cap1.V[sys.argv[1]]
cap = CP.Cap(**v["cap"])
f = cap.base().frag
for rw in v["rows"]:
    pt = cap.row(**rw)
    f = f + pt.frag
    print("row", len(pt.meta["petals"]), [round(q["reg"].area) for q in pt.meta["petals"]],
          "hatch marks", sum(1 for m in pt.lines.marks if m.role == "hatch"))
render(f, f"/home/luke/Projects/design/san-marcos-deck/work/qh/v4/study/out/capdbg_{sys.argv[1]}.png", box=(300, 110, 460, 230), scale=4.0)
