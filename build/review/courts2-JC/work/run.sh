#!/bin/bash
# usage: run.sh <name> [--qa]   renders art/JC.py (current) into work/out/<name>
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-JC/work
N=$1; QA=$2; WHITE=${WHITE:---no-white}
mkdir -p $W/out/$N
.venv/bin/python tools/preview.py art/JC.py JC $W/out/$N $WHITE $QA 2>&1 | grep -v "^\[preview\]" | grep -E "✗|12 |5 |!|Warn|warn" || true
rsvg-convert -w 2250 $W/out/$N/JC.svg -o $W/out/$N/f3.png
rsvg-convert -w 4500 $W/out/$N/JC.svg -o $W/out/$N/f6.png
c3(){ magick $W/out/$N/f3.png -crop $(( ($4-$2)*3 ))x$(( ($5-$3)*3 ))+$(($2*3))+$(($3*3)) +repage $W/out/$N/$1.png; }
c6(){ magick $W/out/$N/f6.png -crop $(( ($4-$2)*6 ))x$(( ($5-$3)*6 ))+$(($2*6))+$(($3*6)) +repage $W/out/$N/$1.png; }
c3 handL 180 385 330 495
c3 handR 470 350 600 490
c6 handL6 235 405 335 485
c6 handR6 490 370 590 470
c3 face 285 130 485 330
c3 top 139 55 611 511
magick $W/out/$N/JC.png -crop 480x480+135+55 +repage $W/out/$N/top1.png
