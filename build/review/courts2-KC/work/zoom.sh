#!/bin/bash
# zoom.sh <svg> <out.png> x0 y0 x1 y1 scale  -- render a card region at scale via viewBox
SVG=$1; OUT=$2; X0=$3; Y0=$4; X1=$5; Y1=$6; S=$7
W=$(( (X1-X0)*S )); H=$(( (Y1-Y0)*S ))
TMP=$(mktemp --suffix=.svg)
sed -E "0,/<svg[^>]*>/s//<svg xmlns=\"http:\/\/www.w3.org\/2000\/svg\" xmlns:xlink=\"http:\/\/www.w3.org\/1999\/xlink\" viewBox=\"$X0 $Y0 $((X1-X0)) $((Y1-Y0))\" width=\"$W\" height=\"$H\">/" "$SVG" > $TMP
rsvg-convert $TMP -o $OUT
rm $TMP
