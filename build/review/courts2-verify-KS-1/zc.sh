#!/bin/bash
# zc.sh svg x y w h scale out
svg=$1; x=$2; y=$3; w=$4; h=$5; s=$6; out=$7
W=$(python3 -c "print(int($w*$s))"); H=$(python3 -c "print(int($h*$s))")
sed -E "0,/<svg [^>]*>/s//<svg xmlns=\"http:\/\/www.w3.org\/2000\/svg\" width=\"$W\" height=\"$H\" viewBox=\"$x $y $w $h\">/" "$svg" > /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zc_tmp.svg
rsvg-convert /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/zc_tmp.svg -o "$out"
