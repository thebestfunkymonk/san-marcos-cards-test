#!/bin/bash
D=$1
rsvg-convert -w 2250 $D/JS.svg -o $D/x3.png
magick $D/x3.png -crop 300x270+1410+600 +repage $D/sal3.png
magick $D/JS.png -crop 100x90+470+200 +repage -resize 300% $D/sal1.png
