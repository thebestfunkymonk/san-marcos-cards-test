#!/bin/bash
# usage: crops.sh <svg> <scale> <outprefix> name:x0,y0,x1,y1 ...
S=$1; K=$2; O=$3; shift 3
rsvg-convert -w $((750*K)) $S -o /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/big_$K.png
for a in "$@"; do n=${a%%:*}; r=${a#*:}; IFS=, read x0 y0 x1 y1 <<< "$r"
magick /tmp/claude-1000/-home-luke-Projects-design/55d08c26-3490-4d22-8bb1-5d547fef47ba/scratchpad/big_$K.png -crop $(( (x1-x0)*K ))x$(( (y1-y0)*K ))+$((x0*K))+$((y0*K)) +repage ${O}_$n.png
done
