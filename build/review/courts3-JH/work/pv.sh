#!/bin/bash
# pv.sh <tag> [--qa] -> out/<tag>/{JH.svg,JH.png,JH-188.png,JH-1500.png,JH-white.png, JH3x.png}
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts3-JH/work
O=$W/out/$1; mkdir -p $O
.venv/bin/python tools/preview.py art/JH.py JH $O ${2:---qa} > $O/pv.log 2>&1 || { tail -30 $O/pv.log; exit 1; }
rsvg-convert -w 2250 $O/JH.svg -o $O/JH3x.png
grep -E "✗|!|FAIL|WARN|balance|jade|fail|warn|heal" $O/pv.log | head -30
