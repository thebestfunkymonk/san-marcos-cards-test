#!/bin/bash
# usage: run.sh <name> '<json opts>' [--qa]
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts3-KC/work
N=$1; O=${2:-"{}"}; QA=$3; WHITE=${WHITE:---no-white}
.venv/bin/python $W/variant.py $N "$O"
.venv/bin/python tools/preview.py $W/v/$N.py KC $W/out/$N $WHITE $QA 2>&1 | grep -v "^\[preview\]" | grep -E "✗|12 |5 " || true
rsvg-convert -w 2250 $W/out/$N/KC.svg -o $W/out/$N/f3.png
rsvg-convert -w 4500 $W/out/$N/KC.svg -o $W/out/$N/f6.png
c3(){ magick $W/out/$N/f3.png -crop $(( ($4-$2)*3 ))x$(( ($5-$3)*3 ))+$(($2*3))+$(($3*3)) +repage $W/out/$N/$1.png; }
c6(){ magick $W/out/$N/f6.png -crop $(( ($4-$2)*6 ))x$(( ($5-$3)*6 ))+$(($2*6))+$(($3*6)) +repage $W/out/$N/$1.png; }
c3 handL 220 355 360 505
c3 handR 460 360 590 480
c6 cup6 240 395 350 500
c6 fist6 478 368 578 468
c3 top 139 55 611 511
