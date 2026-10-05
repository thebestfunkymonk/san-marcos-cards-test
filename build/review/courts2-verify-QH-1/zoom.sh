#!/bin/bash
# usage: zoom.sh in.svg x y w h scale out.png
in=$1; x=$2; y=$3; w=$4; h=$5; s=$6; out=$7
tmp=$(mktemp --suffix=.svg)
sed "0,/<svg [^>]*>/s//<svg xmlns=\"http:\/\/www.w3.org\/2000\/svg\" width=\"$w\" height=\"$h\" viewBox=\"$x $y $w $h\">/" "$in" > $tmp
rsvg-convert -w $(python3 -c "print(int($w*$s))") $tmp -o $out
rm $tmp
