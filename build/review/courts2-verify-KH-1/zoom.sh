#!/bin/bash
# zoom.sh name x y w h scale [which=after|before|both]
V=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KH-1
R=/home/luke/Projects/design/san-marcos-deck
n=$1; x=$2; y=$3; w=$4; h=$5; s=$6; which=${7:-after}
W=$(python3 -c "print(int($w*$s))"); H=$(python3 -c "print(int($h*$s))")
do_one() { src=$1; tag=$2
  sed "0,/<svg /s|<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"750\" height=\"1050\" viewBox=\"0 0 750 1050\">|<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"$W\" height=\"$H\" viewBox=\"$x $y $w $h\">|" $src > $V/_tmp_$tag.svg
  rsvg-convert $V/_tmp_$tag.svg -o $V/${n}_${tag}_${s}x.png
}
case $which in
 after) do_one $R/cards/KH.svg after;;
 before) do_one $R/build/review/courts-before/cards/KH.svg before;;
 both) do_one $R/cards/KH.svg after; do_one $R/build/review/courts-before/cards/KH.svg before
   magick $V/${n}_before_${s}x.png $V/${n}_after_${s}x.png -background '#888' -splice 8x0 +append $V/${n}_ba_${s}x.png;;
esac
