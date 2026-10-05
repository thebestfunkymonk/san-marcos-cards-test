#!/bin/bash
# crop.sh name x y w h  (card px) -> before/after side by side at 3x
V=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KH-1
n=$1; x=$2; y=$3; w=$4; h=$5; s=${6:-3}
src=3x; [ "$s" = 6 ] && src=6x
X=$((x*s)); Y=$((y*s)); W=$((w*s)); H=$((h*s))
magick $V/before_$src.png -crop ${W}x${H}+${X}+${Y} +repage $V/${n}_before_${s}x.png
magick $V/after_$src.png -crop ${W}x${H}+${X}+${Y} +repage $V/${n}_after_${s}x.png
magick $V/${n}_before_${s}x.png $V/${n}_after_${s}x.png -background '#888' -splice 8x0 +append $V/${n}_ba_${s}x.png
