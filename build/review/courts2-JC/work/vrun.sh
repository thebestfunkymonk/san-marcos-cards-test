#!/bin/bash
# usage: vrun.sh <name> '<python statements applied to module JC>' [--qa]
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-JC/work
N=$1; STMTS=$2; QA=$3; WHITE=${WHITE:---no-white}
mkdir -p $W/v $W/out/$N
cat > $W/v/$N.py <<PY
import sys, os
sys.path.insert(0, '/home/luke/Projects/design/san-marcos-deck/art')
import JC
from deck import courtkit as K
$STMTS
build = JC.build
figure = JC.figure
PY
.venv/bin/python tools/preview.py $W/v/$N.py JC $W/out/$N $WHITE $QA 2>&1 | grep -v "^\[preview\]" | grep -E "✗|12 |5 |Warn|warn|Error|error|Traceback" || true
rsvg-convert -w 2250 $W/out/$N/JC.svg -o $W/out/$N/f3.png
rsvg-convert -w 4500 $W/out/$N/JC.svg -o $W/out/$N/f6.png
c3(){ magick $W/out/$N/f3.png -crop $(( ($4-$2)*3 ))x$(( ($5-$3)*3 ))+$(($2*3))+$(($3*3)) +repage $W/out/$N/$1.png; }
c6(){ magick $W/out/$N/f6.png -crop $(( ($4-$2)*6 ))x$(( ($5-$3)*6 ))+$(($2*6))+$(($3*6)) +repage $W/out/$N/$1.png; }
c3 handL 180 385 350 495
c3 handR 460 350 600 490
c6 handL6 235 405 335 485
c6 handR6 490 370 590 470
c3 face 285 130 485 330
magick $W/out/$N/JC.png -crop 480x480+135+55 +repage $W/out/$N/top1.png
