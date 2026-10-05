#!/bin/bash
# id label cx cy (card px); crop S card px square at 3x
cd /home/luke/Projects/design/san-marcos-deck
D=build/review/courts2-consistency
F=/usr/share/fonts/noto/NotoSans-Regular.ttf
S=${S:-150}
P=$((S*3))
while read id lab cx cy; do
  [ -z "$id" ] && continue
  x=$(( (cx - S/2)*3 )); y=$(( (cy - S/2)*3 ))
  for v in after before; do
    magick $D/${v}_3x/$id.png -crop ${P}x${P}+$x+$y +repage -background '#555' -fill white -font $F -pointsize 22 -gravity north -splice 0x30 -annotate +0+2 "$id $lab ($v)" $D/crops/${id}_${lab}_${v}.png
  done
done <<'LIST'
KS L 292 445
KS R 522 440
QS L 310 442
QS R 532 455
JS L 287 432
JS R 538 195
KH L 215 408
KH R 540 462
QH L 315 445
QH R 528 448
JH L 252 438
JH R 543 270
KC L 292 445
KC R 524 418
QC L 308 430
QC R 530 440
JC L 275 425
JC R 530 400
KD L 360 420
KD R 530 398
QD L 220 454
QD R 544 424
JD L 255 455
JD R 456 400
LIST
