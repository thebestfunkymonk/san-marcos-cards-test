#!/bin/bash
# before/after montage for J♣ round 2 → build/review/courts2-JC/before-after.png
set -e
cd /home/luke/Projects/design/san-marcos-deck
M=build/review/courts2-JC/r2/mont
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
  crop $M/${s}3.png 3 200 385 140 110 $M/${s}_hL3.png
  if [ $s = a ]; then fy=335; fy6=345; else fy=350; fy6=362; fi    # the loom fist moved 404 → 388 (before: 408)
  crop $M/${s}3.png 3 470 $fy 120 120 $M/${s}_hR3.png
  crop $M/${s}6.png 6 225 395 95 90 $M/${s}_hL6.png
  crop $M/${s}6.png 6 475 $fy6 100 80 $M/${s}_hR6.png
  crop $M/${s}3.png 3 250 400 260 80 $M/${s}_belt3.png
  crop $M/${s}6.png 6 440 60 100 100 $M/${s}_plume6.png
  crop $M/${s}6.png 6 470 395 70 60 $M/${s}_cuffR6.png
  crop $M/${s}3.png 3 400 555 160 110 $M/${s}_bot3.png
  crop $M/${s}6.png 6 340 195 70 30 $M/${s}_eyes6.png
done
lab $M/b750.png "BEFORE 750" $M/L_b750.png; lab $M/a750.png "AFTER 750" $M/L_a750.png
magick $M/b188.png $M/a188.png -background '#f3efe4' -splice 0x0 +append $M/p188.png
lab $M/p188.png "188: before | after" $M/L_188.png
magick $M/L_b750.png $M/L_a750.png $M/L_188.png -background '#f3efe4' -gravity north +append $M/row1.png
pair(){ # name label
  magick $M/b_$1.png $M/a_$1.png -background '#1a262c' -splice 6x0 +append -chop 6x0 $M/pp_$1.png
  lab $M/pp_$1.png "$2  (before | after)" $M/L_$1.png; }
pair hL3 "belt hand 3x"; pair hR3 "loom fist 3x"; pair hL6 "belt hand wrist/thumb 6x"; pair hR6 "loom fist 6x"
pair belt3 "belt + reed 3x"; pair plume6 "plume 6x"; pair cuffR6 "loom cuff / belt end 6x"; pair bot3 "180° copy, belt hand 3x"; pair eyes6 "eyes 6x"
magick $M/L_hL3.png $M/L_hR3.png -background '#f3efe4' -gravity north +append $M/row2.png
magick $M/L_hL6.png $M/L_hR6.png $M/L_cuffR6.png -background '#f3efe4' -gravity north +append $M/row3.png
magick $M/L_belt3.png $M/L_bot3.png -background '#f3efe4' -gravity north +append $M/row4.png
magick $M/L_plume6.png $M/L_eyes6.png -background '#f3efe4' -gravity north +append $M/row5.png
magick $M/row1.png $M/row2.png $M/row3.png $M/row4.png $M/row5.png -background '#f3efe4' -gravity center -append +repage build/review/courts2-JC/before-after.png
magick identify build/review/courts2-JC/before-after.png
