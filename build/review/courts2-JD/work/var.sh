#!/bin/bash
# var.sh <tag> <python-replace-script>  : copy art/JD.py -> work/v_<tag>.py, apply edits (python: t = t.replace(...)), preview
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-JD/work
f=$W/v_$1.py
.venv/bin/python - "$f" "$2" <<'PY'
import sys
f, code = sys.argv[1], sys.argv[2]
t = open('art/JD.py').read()
t = t.replace('sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))', 'sys.path.insert(0, "/home/luke/Projects/design/san-marcos-deck/art")')
exec(code)
open(f, 'w').write(t)
PY
bash $W/pv.sh $f $1 ${3:---qa}
