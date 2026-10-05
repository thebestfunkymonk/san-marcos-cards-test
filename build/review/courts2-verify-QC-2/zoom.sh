#!/bin/bash
# zoom.sh name x y w h scale -> B_name.png A_name.png cmp_name.png via viewBox
S=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-QC-2
R=/home/luke/Projects/design/san-marcos-deck
n=$1; x=$2; y=$3; w=$4; h=$5; s=$6
W=$(python3 -c "print(int($w*$s))"); H=$(python3 -c "print(int($h*$s))")
for v in B A; do
  src=$R/cards/QC.svg; [ $v = B ] && src=$R/build/review/courts-before/cards/QC.svg
  sed "1s|width=\"750\" height=\"1050\" viewBox=\"0 0 750 1050\"|width=\"$W\" height=\"$H\" viewBox=\"$x $y $w $h\"|" $src > $S/_z_$v.svg
  rsvg-convert $S/_z_$v.svg -o $S/${v}_$n.png
done
magick $S/B_$n.png $S/A_$n.png -background '#888' -splice 6x0 +append $S/cmp_$n.png
