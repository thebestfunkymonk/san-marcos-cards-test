#!/bin/bash
# usage: crop.sh name x0 y0 x1 y1 scale(3|6|10)  -> before_/after_/cmp_ name
V=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KD-2
n=$1; x0=$2; y0=$3; x1=$4; y1=$5; s=$6
W=$(( (x1-x0)*s )); H=$(( (y1-y0)*s )); X=$(( x0*s )); Y=$(( y0*s ))
for w in before after; do magick $V/${w}_${s}x.png -crop ${W}x${H}+${X}+${Y} +repage $V/${w}_${n}_${s}x.png; done
magick $V/before_${n}_${s}x.png -bordercolor white -border 0x0 \( $V/after_${n}_${s}x.png \) -background '#888' -splice 0x0 +append $V/cmp_${n}_${s}x.png
