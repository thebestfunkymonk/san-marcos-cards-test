#!/bin/bash
# usage: crops.sh <dir containing JS.svg>  -> writes x3.png, hR.png, hL.png, sal.png, sheet.png in dir
set -e
D=$1
rsvg-convert -w 2250 $D/JS.svg -o $D/x3.png
magick $D/x3.png -crop 420x420+1410+390 +repage $D/hR.png
magick $D/x3.png -crop 420x420+690+1080 +repage $D/hL.png
magick $D/x3.png -crop 420x300+1350+630 +repage $D/sal.png
magick $D/hR.png $D/hL.png +append $D/hands.png
