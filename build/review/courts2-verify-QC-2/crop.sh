#!/bin/bash
# crop.sh name x y w h scale(3|6)  -> cmp_name.png (before | after)
S=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-QC-2
n=$1; x=$2; y=$3; w=$4; h=$5; s=${6:-3}
X=$((x*s)); Y=$((y*s)); W=$((w*s)); H=$((h*s))
magick $S/B$s.png -crop ${W}x${H}+${X}+${Y} +repage $S/B_$n.png
magick $S/A$s.png -crop ${W}x${H}+${X}+${Y} +repage $S/A_$n.png
magick $S/B_$n.png $S/A_$n.png -background '#888' -splice 6x0 +append $S/cmp_$n.png
