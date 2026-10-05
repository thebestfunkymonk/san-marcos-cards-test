#!/bin/bash
# crop6.sh <name> <S> x0 y0 x1 y1  -- crop from out/<name>/f6.png (S=6) or f3 (S=3)
N=$1; S=$2; F=out/$N/f$S.png
magick $F -crop $(( ($5-$3)*S ))x$(( ($6-$4)*S ))+$(($3*S))+$(($4*S)) +repage out/$N/c_$3_$4_$S.png
echo out/$N/c_$3_$4_$S.png
