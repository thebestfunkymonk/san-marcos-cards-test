#!/bin/bash
# usage: crop.sh name x0 y0 x1 y1 [zoom-extra]  (card px) -> 3-up cmp: pre | start | now at 3x (optionally upscaled)
V=/home/luke/Projects/design/san-marcos-deck/build/review/courts3-verify-JH-r1
n=$1; x0=$2; y0=$3; x1=$4; y1=$5; z=${6:-100}
w=$(( (x1-x0)*3 )); h=$(( (y1-y0)*3 )); X=$((x0*3)); Y=$((y0*3))
for s in pre start now; do
  magick $V/${s}3x.png -crop ${w}x${h}+${X}+${Y} +repage -filter point -resize ${z}% -bordercolor '#ff00ff' -border 2 $V/_c_$s.png
done
magick $V/_c_pre.png $V/_c_start.png $V/_c_now.png +append $V/$n.png
rm -f $V/_c_*.png
echo $V/$n.png
