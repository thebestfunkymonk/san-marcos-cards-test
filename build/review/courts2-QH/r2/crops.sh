#!/bin/bash
# crops.sh in.svg outdir — standard QH review crops
in=$1; o=$2; mkdir -p $o
G=/home/luke/Projects/design/san-marcos-deck/build/review/courts2-QH/r2/grid.py
rsvg-convert -w 750 $in -o $o/750.png
rsvg-convert -w 188 $in -o $o/188.png
rsvg-convert -w 2250 $in -o $o/3x.png
magick $o/750.png -crop 472x456+139+55 +repage $o/top750.png
magick $o/3x.png -crop 390x270+800+1180 +repage $o/handL_3x.png
magick $o/3x.png -crop 300x330+1470+1160 +repage $o/handR_3x.png
magick $o/3x.png -crop 330x300+1050+450 +repage $o/head_3x.png
magick $o/3x.png -crop 300x480+1500+450 +repage $o/leaf_3x.png
magick $o/3x.png -crop 240x150+1050+780 +repage $o/collar_3x.png
magick $o/3x.png -crop 330x120+1440+1110 +repage $o/armletR_3x.png
# 180-degree copy: hands in the bottom half (card 750x1050 -> 3x 2250x3150)
magick $o/3x.png -crop 390x270+1060+1700 +repage $o/rot_handL_3x.png
magick $o/3x.png -crop 300x330+530+1660 +repage $o/rot_handR_3x.png
