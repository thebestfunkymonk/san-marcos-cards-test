#!/bin/bash
# usage: mont.sh <out.png> <tag> name...  -- side-by-side of out/<name>/z_<tag>.png with labels
OUT=$1; TAG=$2; shift 2
args=()
for n in "$@"; do args+=(-label "$n" out/$n/z_$TAG.png); done
magick montage "${args[@]}" -tile ${#@}x1 -geometry +6+6 -pointsize 18 -background '#888' $OUT
