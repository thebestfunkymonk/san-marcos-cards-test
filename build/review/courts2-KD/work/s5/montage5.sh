#!/bin/bash
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-KD/work/s5/final
P=.venv/bin/python
C=build/review/courts2-KD/work/crops.py
mkdir -p $W/b $W/a
BS=build/review/courts-before/cards/KD.svg
AS=cards/KD.svg
for s in 3 6; do :; done
$P $C $BS $W/b 3 handL:300,340,450,490 handR:470,330,600,511 cuffL:270,410,390,511 chest:300,280,480,511 hem:230,380,610,511
$P $C $AS $W/a 3 handL:300,340,450,490 handR:470,330,600,511 cuffL:270,410,390,511 chest:300,280,480,511 hem:230,380,610,511
$P $C $BS $W/b 6 handL6:318,350,428,462 handR6:490,350,590,440 g6:285,410,365,490
$P $C $AS $W/a 6 handL6:318,350,428,462 handR6:490,350,590,440 g6:285,410,365,490
$P $C $BS $W/b 10 kb:498,380,562,432 st:338,372,402,412
$P $C $AS $W/a 10 kb:498,380,562,432 st:338,372,402,412
lab() { magick "$1" +repage -background "#f3efe4" -gravity center -extent "%[fx:max(w,340)]x%[h]" -gravity north -background '#f3efe4' -splice 0x26 -font Adwaita-Sans -pointsize 18 -fill '#15232b' -annotate +0+3 "$2" "$3"; }
pair() { # name label
  lab $W/b/$1.png "BEFORE  $2" $W/b_$1.png; lab $W/a/$1.png "AFTER  $2" $W/a_$1.png
  magick $W/b_$1.png $W/a_$1.png -bordercolor '#f3efe4' -border 6 +append $W/p_$1.png
}
cp build/review/courts-before/png/KD.png $W/b/c750.png; cp build/png/KD.png $W/a/c750.png
magick build/review/courts-before/small/KD.png \( build/review/courts-before/small/KD.png -scale 200% \) -background '#f3efe4' -gravity center +append $W/b/c188.png
$P -c "
import subprocess
subprocess.run(['rsvg-convert','-w','188','$AS','-o','$W/a/_188.png'],check=True)"
magick $W/a/_188.png \( $W/a/_188.png -scale 200% \) -background '#f3efe4' -gravity center +append $W/a/c188.png
for n in c750 c188 chest_3x handL_3x handR_3x cuffL_3x handL6_6x handR6_6x kb_10x st_10x; do :; done
pair c750 "750 px"
pair c188 "188 px (1x, 2x)"
pair chest_3x "chest 3x (sash grip, gather)"
pair handL_3x "sash hand 3x"
pair handR_3x "key hand + forearm 3x"
pair cuffL_3x "sash gauntlet vs hem 3x"
pair handL6_6x "sash hand 6x"
pair handR6_6x "key hand 6x"
pair kb_10x "key-hand heel 10x"
pair st_10x "sash edge T into the fist 10x"
pair hem_3x "arms + hem 3x"
pair g6_6x "sash gauntlet 6x (sleeve tucked under)"
# the AD touch-up item: round-3 state (s4) vs now
lab build/review/courts2-KD/work/s5/it0/g6_6x.png "ROUND 3  sleeve edge outside cuff: wedge" $W/s4_g6.png; lab $W/a/g6_6x.png "NOW  one 3.1 px cuff edge" $W/s5_g6.png
magick $W/s4_g6.png $W/s5_g6.png -bordercolor '#f3efe4' -border 6 +append $W/p_ad.png
magick $W/p_c750.png $W/p_c188.png -background '#f3efe4' -gravity center -append $W/r1.png
magick $W/p_chest_3x.png $W/p_handL_3x.png $W/p_cuffL_3x.png -background '#f3efe4' -gravity north +append $W/r2.png
magick $W/p_handR_3x.png $W/p_handL6_6x.png $W/p_handR6_6x.png -background '#f3efe4' -gravity north +append $W/r3.png
magick $W/p_kb_10x.png $W/p_st_10x.png $W/p_g6_6x.png -background '#f3efe4' -gravity north +append $W/r4.png
magick $W/p_hem_3x.png $W/p_ad.png -background '#f3efe4' -gravity north +append $W/r5.png
magick $W/r1.png $W/r2.png $W/r3.png $W/r4.png $W/r5.png -background '#f3efe4' -gravity center -append build/review/courts2-KD/before-after.png
magick identify build/review/courts2-KD/before-after.png
