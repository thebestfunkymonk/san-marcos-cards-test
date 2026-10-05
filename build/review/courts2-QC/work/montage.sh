#!/bin/bash
# montage.sh AFTER_SVG AFTER_PNG750 AFTER_PNG188 OUT
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-QC/work/mont; mkdir -p $W
B=build/review/courts-before
A_SVG=$1; A750=$2; A188=$3; OUT=$4
C=build/review/courts2-QC/work/crop.sh
# hand crops at 3x (card px 110x110 -> 330)
$C $B/cards/QC.svg 255 360 375 480 3 $W/bL.png; $C $A_SVG 255 360 375 480 3 $W/aL.png
$C $B/cards/QC.svg 485 380 605 500 3 $W/bR.png; $C $A_SVG 485 380 605 500 3 $W/aR.png
# close-ups 8x of each hand
$C $B/cards/QC.svg 280 380 345 465 6 $W/bL6.png; $C $A_SVG 280 380 345 465 6 $W/aL6.png
$C $B/cards/QC.svg 490 400 565 470 6 $W/bR6.png; $C $A_SVG 490 400 565 470 6 $W/aR6.png
# other fixes at 5x
for spec in "knop 505 250 580 305" "parting 355 150 415 195" "ferrule 270 350 330 400" "wedge 205 325 255 365" "notch 290 432 330 470" "strip 495 440 560 512"; do
  set -- $spec; $C $B/cards/QC.svg $2 $3 $4 $5 5 $W/b_$1.png; $C $A_SVG $2 $3 $4 $5 5 $W/a_$1.png
done
L="-background #F4EFE3 -fill #15242B -font /usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf -pointsize 22"
lab() { magick $1 $L -gravity north -splice 0x34 -annotate +0+4 "$2" $1; }
cp $B/png/QC.png $W/b750.png; cp $A750 $W/a750.png
lab $W/b750.png "BEFORE 750"; lab $W/a750.png "AFTER 750"
magick $B/small/QC.png -filter point -resize 200% $W/b188.png; magick $A188 -filter point -resize 200% $W/a188.png
magick $B/small/QC.png $W/b188_1x.png; magick $A188 $W/a188_1x.png
lab $W/b188.png "BEFORE 188 (x2)"; lab $W/a188.png "AFTER 188 (x2)"
for n in bL aL bR aR bL6 aL6 bR6 aR6; do :; done
lab $W/bL.png "before fan hand 3x"; lab $W/aL.png "after fan hand 3x"; lab $W/bR.png "before sceptre hand 3x"; lab $W/aR.png "after sceptre hand 3x"
lab $W/bL6.png "before 6x"; lab $W/aL6.png "after 6x"; lab $W/bR6.png "before 6x"; lab $W/aR6.png "after 6x"
for n in knop parting ferrule wedge notch strip; do lab $W/b_$n.png "before $n 5x"; lab $W/a_$n.png "after $n 5x"; done
magick $W/b750.png $W/a750.png +append -bordercolor '#F4EFE3' -border 10 $W/row1.png
magick \( $W/b188.png $W/a188.png +append \) \( $W/bL.png $W/aL.png -append \) \( $W/bR.png $W/aR.png -append \) -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row2.png
magick $W/bL6.png $W/aL6.png $W/bR6.png $W/aR6.png -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row3.png
magick \( $W/b_knop.png $W/a_knop.png $W/b_parting.png $W/a_parting.png $W/b_ferrule.png $W/a_ferrule.png -gravity north +append \) \( $W/b_wedge.png $W/a_wedge.png $W/b_notch.png $W/a_notch.png $W/b_strip.png $W/a_strip.png -gravity north +append \) -append -bordercolor '#F4EFE3' -border 10 $W/row4.png
magick $W/row1.png $W/row2.png $W/row3.png $W/row4.png -background '#F4EFE3' -gravity center -append $OUT
identify $OUT
