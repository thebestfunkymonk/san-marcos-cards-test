#!/bin/bash
# usage: zoom.sh name x y w h scale   -> before/after zoom crops via viewBox (card px)
V=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KH-2
R=/home/luke/Projects/design/san-marcos-deck
n=$1; x=$2; y=$3; w=$4; h=$5; s=$6
for which in before after; do
  if [ $which = before ]; then src=$R/build/review/courts-before/cards/KH.svg; else src=$R/cards/KH.svg; fi
  W=$(python3 -c "print(int($w*$s))"); H=$(python3 -c "print(int($h*$s))")
  sed -e "0,/<svg /s|width=\"750\" height=\"1050\" viewBox=\"0 0 750 1050\"|width=\"$W\" height=\"$H\" viewBox=\"$x $y $w $h\"|" $src > $V/.z_$which.svg
  rsvg-convert $V/.z_$which.svg -o $V/${n}_${which}_${s}x.png
done
magick $V/${n}_before_${s}x.png -bordercolor magenta -border 3 $V/${n}_after_${s}x.png -bordercolor magenta -border 3 +append $V/${n}_ba_${s}x.png
echo $V/${n}_ba_${s}x.png
