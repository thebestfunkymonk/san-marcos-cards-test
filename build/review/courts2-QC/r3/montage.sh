#!/bin/bash
# montage.sh OUT : before (courts-before) vs after (cards/QC.svg, build/png/QC.png, build/small or preview 188)
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-QC/r3/mont; mkdir -p $W
B=build/review/courts-before
A_SVG=cards/QC.svg; A750=build/png/QC.png; A188=$2
OUT=$1
C=build/review/courts2-QC/work/crop.sh
# hand crops at 3x
$C $B/cards/QC.svg 250 360 380 490 3 $W/bL.png; $C $A_SVG 250 360 380 490 3 $W/aL.png
$C $B/cards/QC.svg 470 370 600 500 3 $W/bR.png; $C $A_SVG 470 370 600 500 3 $W/aR.png
# close-ups 6x of each hand
$C $B/cards/QC.svg 272 380 347 470 6 $W/bL6.png; $C $A_SVG 272 380 347 470 6 $W/aL6.png
$C $B/cards/QC.svg 485 395 565 485 6 $W/bR6.png; $C $A_SVG 485 395 565 485 6 $W/aR6.png
# other areas
$C $B/cards/QC.svg 200 330 560 511 2 $W/b_gown.png; $C $A_SVG 200 330 560 511 2 $W/a_gown.png
for spec in "knop 515 268 567 300 8" "fancuff 240 400 320 470 5" "wristR 480 430 560 511 5" "uptip 405 330 470 380 6" "parting 355 145 415 190 6" "ferrule 270 350 330 400 5"; do
  set -- $spec; $C $B/cards/QC.svg $2 $3 $4 $5 $6 $W/b_$1.png; $C $A_SVG $2 $3 $4 $5 $6 $W/a_$1.png
done
L="-background #F4EFE3 -fill #15242B -font /usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf -pointsize 22"
lab() { magick $1 $L -gravity north -splice 0x34 -annotate +0+4 "$2" $1; }
cp $B/png/QC.png $W/b750.png; cp $A750 $W/a750.png
lab $W/b750.png "BEFORE 750"; lab $W/a750.png "AFTER 750"
magick $B/small/QC.png -filter point -resize 200% $W/b188.png; magick $A188 -filter point -resize 200% $W/a188.png
lab $W/b188.png "BEFORE 188 (x2)"; lab $W/a188.png "AFTER 188 (x2)"
lab $W/bL.png "before fan hand 3x"; lab $W/aL.png "after fan hand 3x"; lab $W/bR.png "before sceptre hand 3x"; lab $W/aR.png "after sceptre hand 3x"
lab $W/bL6.png "before fan hand 6x"; lab $W/aL6.png "after 6x"; lab $W/bR6.png "before sceptre hand 6x"; lab $W/aR6.png "after 6x"
lab $W/b_gown.png "before gown 2x (5 leaves)"; lab $W/a_gown.png "after gown 2x (1 + 3 leaves)"
for n in knop fancuff wristR uptip parting ferrule; do lab $W/b_$n.png "before $n"; lab $W/a_$n.png "after $n"; done
magick $W/b750.png $W/a750.png +append -bordercolor '#F4EFE3' -border 10 $W/row1.png
magick \( $W/b188.png $W/a188.png +append \) \( $W/bL.png $W/aL.png -append \) \( $W/bR.png $W/aR.png -append \) -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row2.png
magick $W/bL6.png $W/aL6.png $W/bR6.png $W/aR6.png -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row3.png
magick $W/b_gown.png $W/a_gown.png -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row4.png
magick \( $W/b_knop.png $W/a_knop.png $W/b_fancuff.png $W/a_fancuff.png $W/b_wristR.png $W/a_wristR.png -gravity north +append \) \( $W/b_uptip.png $W/a_uptip.png $W/b_parting.png $W/a_parting.png $W/b_ferrule.png $W/a_ferrule.png -gravity north +append \) -gravity west -append -bordercolor '#F4EFE3' -border 10 $W/row5.png
magick $W/row1.png $W/row2.png $W/row3.png $W/row4.png $W/row5.png -background '#F4EFE3' -gravity center -append $OUT
identify $OUT
