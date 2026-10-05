#!/bin/bash
# usage: crop.sh name x y w h scale(3|6)   (card px)
V=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-verify-KH-2
n=$1; x=$2; y=$3; w=$4; h=$5; s=$6
g="$(python3 -c "print(f'{int($w*$s)}x{int($h*$s)}+{int($x*$s)}+{int($y*$s)}')")"
magick $V/before_${s}x.png -crop $g +repage $V/${n}_before_${s}x.png
magick $V/after_${s}x.png -crop $g +repage $V/${n}_after_${s}x.png
magick $V/${n}_before_${s}x.png -bordercolor magenta -border 3 $V/${n}_after_${s}x.png -bordercolor magenta -border 3 +append $V/${n}_ba_${s}x.png
echo $V/${n}_ba_${s}x.png
