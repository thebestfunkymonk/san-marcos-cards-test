#!/bin/bash
# usage: run2.sh <name> '<json opts>' region... ; region = tag:x0,y0,x1,y1,S  (no QA, fast)
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-KC/work
N=$1; O=${2:-"{}"}; shift 2
.venv/bin/python $W/variant.py $N "$O"
.venv/bin/python tools/preview.py $W/v/$N.py KC $W/out/$N --no-white 2>&1 | grep -v "^\[preview\]" | grep -iE "error|trace|warn" || true
for r in "$@"; do
  tag=${r%%:*}; IFS=, read x0 y0 x1 y1 s <<< "${r#*:}"
  $W/zoom.sh $W/out/$N/KC.svg $W/out/$N/z_$tag.png $x0 $y0 $x1 $y1 $s
done
