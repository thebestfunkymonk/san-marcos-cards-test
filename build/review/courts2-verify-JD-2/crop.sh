#!/bin/bash
# crop.sh name x0 y0 x1 y1 [scale 3|8]
n=$1; x0=$2; y0=$3; x1=$4; y1=$5; s=${6:-3}
if [ "$s" = 8 ]; then k=8; B=b8.png; A=a8.png; else k=3; B=b3.png; A=a3.png; fi
W=$(( (x1-x0)*k )); H=$(( (y1-y0)*k )); X=$((x0*k)); Y=$((y0*k))
magick $B -crop ${W}x${H}+${X}+${Y} +repage b_$n.png
magick $A -crop ${W}x${H}+${X}+${Y} +repage a_$n.png
magick b_$n.png -bordercolor '#ff00ff' -border 3 a_$n.png -border 3 +append ba_$n.png
