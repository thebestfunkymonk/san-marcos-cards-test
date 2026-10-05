#!/bin/bash
# montage.sh OUT A188 : before (courts-before) vs after (cards/QC.svg, build/png/QC.png, A188) — round 3
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-QC/r4/mont; mkdir -p $W
B=build/review/courts-before
A_SVG=cards/QC.svg; A750=build/png/QC.png; A188=$2
S0=build/review/courts2-QC/work_r4/QC_card_start.svg       # round-3 start (the regression)
OUT=$1
C=build/review/courts2-QC/work/crop.sh
$C $B/cards/QC.svg 250 360 380 490 3 $W/bL.png; $C $A_SVG 250 360 380 490 3 $W/aL.png
$C $B/cards/QC.svg 470 370 600 500 3 $W/bR.png; $C $A_SVG 470 370 600 500 3 $W/aR.png
$C $B/cards/QC.svg 272 380 347 470 6 $W/bL6.png; $C $A_SVG 272 380 347 470 6 $W/aL6.png
$C $B/cards/QC.svg 495 395 565 480 6 $W/bR6.png; $C $S0 495 395 565 480 6 $W/sR6.png; $C $A_SVG 495 395 565 480 6 $W/aR6.png
# the sceptre head: before / round-3 start (regression) / after
for f in b s a; do case $f in b) sv=$B/cards/QC.svg;; s) sv=$S0;; a) sv=$A_SVG;; esac
  $C $sv 480 215 605 300 4 $W/${f}_arms.png; $C $sv 532 232 560 256 16 $W/${f}_stub.png; done
$C $B/cards/QC.svg 210 250 340 400 3 $W/b_fan.png; $C $S0 210 250 340 400 3 $W/s_fan.png; $C $A_SVG 210 250 340 400 3 $W/a_fan.png
L="-background #F4EFE3 -fill #15242B -font /usr/share/fonts/Adwaita/AdwaitaSans-Regular.ttf -pointsize 22"
lab() { magick $1 $L -gravity north -splice 0x34 -annotate +0+4 "$2" $1; }
cp $B/png/QC.png $W/b750.png; cp $A750 $W/a750.png
lab $W/b750.png "BEFORE 750"; lab $W/a750.png "AFTER 750"
magick $B/small/QC.png -filter point -resize 200% $W/b188.png; magick $A188 -filter point -resize 200% $W/a188.png
lab $W/b188.png "BEFORE 188 (x2)"; lab $W/a188.png "AFTER 188 (x2)"
lab $W/bL.png "before fan hand 3x"; lab $W/aL.png "after fan hand 3x"; lab $W/bR.png "before sceptre hand 3x"; lab $W/aR.png "after sceptre hand 3x"
lab $W/bL6.png "before fan hand 6x"; lab $W/aL6.png "after 6x"
lab $W/bR6.png "before sceptre hand 6x"; lab $W/sR6.png "round-2 thumb (knob) 6x"; lab $W/aR6.png "after: kit thumb bar, tip 0.50 6x"
lab $W/b_arms.png "before sceptre arms 4x"; lab $W/s_arms.png "round-3 start: lower outlines lost 4x"; lab $W/a_arms.png "after 4x"
lab $W/b_stub.png "before 16x"; lab $W/s_stub.png "start: stub, nubs 16x"; lab $W/a_stub.png "after 16x"
lab $W/b_fan.png "before fan 3x"; lab $W/s_fan.png "round-3 start fan 3x"; lab $W/a_fan.png "after (vanes sweep out sooner) 3x"
magick $W/b750.png $W/a750.png +append -bordercolor '#F4EFE3' -border 10 $W/row1.png
magick \( $W/b188.png $W/a188.png +append \) \( $W/bL.png $W/aL.png -append \) \( $W/bR.png $W/aR.png -append \) -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row2.png
magick $W/bL6.png $W/aL6.png $W/bR6.png $W/sR6.png $W/aR6.png -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row3.png
magick $W/b_arms.png $W/s_arms.png $W/a_arms.png -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row4.png
magick $W/b_stub.png $W/s_stub.png $W/a_stub.png $W/b_fan.png $W/s_fan.png $W/a_fan.png -gravity north +append -bordercolor '#F4EFE3' -border 10 $W/row5.png
magick $W/row1.png $W/row2.png $W/row3.png $W/row4.png $W/row5.png -background '#F4EFE3' -gravity center -append $OUT
identify $OUT
