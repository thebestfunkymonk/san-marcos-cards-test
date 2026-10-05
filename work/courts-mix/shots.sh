#!/bin/bash
# shots.sh <svg> <outprefix> : 3x render and crops
svg=$1; o=$2
rsvg-convert -w 2250 "$svg" -o "$o-3x.png"
magick "$o-3x.png" -crop 1440x1400+405+150 +repage -resize 50% "$o-top.png"
