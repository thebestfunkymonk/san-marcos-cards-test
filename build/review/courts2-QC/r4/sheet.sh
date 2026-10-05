#!/bin/bash
# sheet.sh <svg> <outdir> : 3x/6x crops of the QC review areas + 180° copy
set -e
SVG=$1; O=$2; mkdir -p $O
rsvg-convert -w 2250 $SVG -o $O/3x.png
rsvg-convert -w 4500 $SVG -o $O/6x.png
c3() { magick $O/3x.png -crop $(( ($3-$1)*3 ))x$(( ($4-$2)*3 ))+$(( $1*3 ))+$(( $2*3 )) +repage $O/$5.png; }
c6() { magick $O/6x.png -crop $(( ($3-$1)*6 ))x$(( ($4-$2)*6 ))+$(( $1*6 ))+$(( $2*6 )) +repage $O/$5.png; }
c3 490 380 580 500 hR3
c6 500 390 570 480 hR6
c3 255 365 355 475 hL3
c6 265 375 345 470 hL6
c6 505 225 600 300 arms6
c6 510 265 572 300 knop6
c6 262 338 325 395 ferrule6
c6 345 130 425 180 crown6
c3 320 160 450 300 face3
# 180° copy: (x, y) -> (750 - x, 1050 - y)
c3 170 550 260 670 hR3rot
c3 395 575 495 685 hL3rot
