#!/bin/bash
# before/after montage for J♣ round 3 → build/review/courts2-JC/before-after.png
set -e
cd /home/luke/Projects/design/san-marcos-deck
M=build/review/courts2-JC/r3/mont
B=build/review/courts-before
rsvg-convert -w 2250 $B/cards/JC.svg -o $M/b3.png
rsvg-convert -w 2250 cards/JC.svg -o $M/a3.png
rsvg-convert -w 4500 $B/cards/JC.svg -o $M/b6.png
rsvg-convert -w 4500 cards/JC.svg -o $M/a6.png
rsvg-convert -w 750 cards/JC.svg -o $M/a750.png
rsvg-convert -w 188 cards/JC.svg -o $M/a188.png
magick $B/png/JC.png -background '#f3efe4' -alpha remove $M/b750.png; magick $B/small/JC.png -background '#f3efe4' -alpha remove $M/b188.png
magick $M/a750.png -background '#f3efe4' -alpha remove $M/a750.png; magick $M/a188.png -background '#f3efe4' -alpha remove $M/a188.png
lab(){ magick "$1" -background '#f3efe4' -gravity north -splice 0x34 -font /usr/share/fonts/noto/NotoSans-Regular.ttf -pointsize 22 -fill '#1a262c' -annotate +0+5 "$2" "$3"; }
crop(){ # src scale x y w h out
  magick $1 -crop $(( $5*$2 ))x$(( $6*$2 ))+$(( $3*$2 ))+$(( $4*$2 )) +repage $7; }
for s in b a; do
  if [ $s = a ]; then fy=335; fy6=350; else fy=350; fy6=362; fi    # the loom fist: 408 before, 388 after
  crop $M/${s}3.png 3 200 385 140 115 $M/${s}_hL3.png
  crop $M/${s}3.png 3 460 $fy 130 120 $M/${s}_hR3.png
  crop $M/${s}6.png 6 245 405 85 90 $M/${s}_hL6.png
  crop $M/${s}6.png 6 480 $fy6 95 95 $M/${s}_hR6.png
  crop $M/${s}6.png 6 240 425 70 90 $M/${s}_seam6.png
  crop $M/${s}6.png 6 440 380 90 80 $M/${s}_waistR6.png
  crop $M/${s}3.png 3 240 395 290 95 $M/${s}_belt3.png
  crop $M/${s}6.png 6 515 470 50 41 $M/${s}_foot6.png
  crop $M/${s}3.png 3 150 545 450 125 $M/${s}_bot3.png
  crop $M/${s}6.png 6 340 195 70 30 $M/${s}_eyes6.png
done
lab $M/b750.png "BEFORE 750" $M/L_b750.png; lab $M/a750.png "AFTER 750" $M/L_a750.png
magick $M/b188.png $M/a188.png -background '#f3efe4' -splice 8x0 +append $M/p188.png
lab $M/p188.png "188: before | after" $M/L_188.png
magick $M/L_b750.png $M/L_a750.png $M/L_188.png -background '#f3efe4' -gravity north +append $M/row1.png
pair(){ # name label
  magick $M/b_$1.png $M/a_$1.png -background '#1a262c' -splice 6x0 +append -chop 6x0 $M/pp_$1.png
  lab $M/pp_$1.png "$2  (before | after)" $M/L_$1.png; }
pair hL3 "belt hand 3x"; pair hR3 "loom fist 3x"; pair hL6 "belt hand 6x"; pair hR6 "loom fist + cuff 6x"
pair seam6 "far seam / little finger 6x"; pair waistR6 "near jerkin edge / belt 6x"; pair belt3 "belt + reed 3x"
pair foot6 "loom foot at the band 6x"; pair bot3 "180 copy 3x"; pair eyes6 "eyes 6x"
magick $M/L_hL3.png $M/L_hR3.png -background '#f3efe4' -gravity north +append $M/row2.png
magick $M/L_hL6.png $M/L_hR6.png -background '#f3efe4' -gravity north +append $M/row3.png
magick $M/L_seam6.png $M/L_waistR6.png $M/L_foot6.png -background '#f3efe4' -gravity north +append $M/row4.png
magick $M/L_belt3.png $M/L_eyes6.png -background '#f3efe4' -gravity north +append $M/row5.png
magick $M/L_bot3.png -background '#f3efe4' -gravity north +append $M/row6.png
magick $M/row1.png $M/row2.png $M/row3.png $M/row4.png $M/row5.png $M/row6.png -background '#f3efe4' -gravity center -append +repage build/review/courts2-JC/before-after.png
magick identify build/review/courts2-JC/before-after.png
