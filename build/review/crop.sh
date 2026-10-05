#!/bin/bash
# usage: crop.sh svg zoom x y w h out   (x,y,w,h in svg px)
svg=$1; z=$2; x=$3; y=$4; w=$5; h=$6; out=$7
tmp=$(mktemp --suffix=.png)
rsvg-convert -z $z "$svg" -o $tmp
magick $tmp -crop $(python3 -c "print(f'{int($w*$z)}x{int($h*$z)}+{int($x*$z)}+{int($y*$z)}')") +repage "$out"
rm $tmp
