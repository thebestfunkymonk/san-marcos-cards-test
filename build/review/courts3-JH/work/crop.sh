#!/bin/bash
# crop.sh <png3x> <x> <y> <w> <h> <out> [upscale%]  (card px coords; from a 3x render)
p=$1; x=$2; y=$3; w=$4; h=$5; out=$6; up=${7:-100}
magick "$p" -crop $((w*3))x$((h*3))+$((x*3))+$((y*3)) +repage -filter point -resize ${up}% "$out"
