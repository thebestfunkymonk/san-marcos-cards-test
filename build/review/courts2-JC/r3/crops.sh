#!/bin/bash
# crops.sh <svg> <outdir> : 3x/6x crops of every area of the J♣ top half
set -e
cd /home/luke/Projects/design/san-marcos-deck
svg=$1; o=$2; mkdir -p $o
rsvg-convert -w 2250 $svg -o $o/x3.png
rsvg-convert -w 4500 $svg -o $o/x6.png
rsvg-convert -w 750 $svg -o $o/x1.png
rsvg-convert -w 188 $svg -o $o/x188.png
c(){ s=$1; x=$2; y=$3; w=$4; h=$5; n=$6; magick $o/x$s.png -crop $((w*s))x$((h*s))+$((x*s))+$((y*s)) +repage $o/$n.png; }
c 3 200 385 140 110 hL3
c 6 245 405 70 80 hL6
c 3 470 335 120 120 hR3
c 6 490 350 85 95 hR6
c 6 330 170 100 110 face6
c 3 310 55 240 150 cap3
c 3 300 150 200 180 hair3
c 3 320 270 120 140 collar3
c 3 240 395 290 90 belt3
c 3 150 300 130 180 slL3
c 3 490 290 125 225 slR3
c 3 500 80 100 200 padT3
c 3 500 270 100 245 padB3
c 3 150 540 450 230 bot3
