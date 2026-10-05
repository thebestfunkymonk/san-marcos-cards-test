#!/bin/bash
# mk.sh NAME "python statements to append after the constants"  -> var/NAME/QC.png etc
cd /home/luke/Projects/design/san-marcos-deck
n=$1; shift
d=build/review/courts2-QC/r3/var
sed 's#sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))#sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")#' art/QC.py > $d/QC_$n.py
python3 - "$d/QC_$n.py" "$*" <<'PY'
import sys
p, extra = sys.argv[1], sys.argv[2]
s = open(p).read()
i = s.index("\ndef head_group")
s = s[:i] + "\n# ---- variant\n" + extra.replace(";;", "\n") + "\n" + s[i:]
open(p, "w").write(s)
PY
.venv/bin/python tools/preview.py $d/QC_$n.py QC $d/$n --no-white > $d/$n.log 2>&1
