#!/bin/bash
# gq.sh name  -- print top-half raster gaps near the cone hand for out/<name>/KC.svg
/home/luke/Projects/design/san-marcos-deck/.venv/bin/python /home/luke/Projects/design/san-marcos-deck/build/review/courts2-KC/work/gaps.py out/$1/KC.svg | grep -E "TOTAL|\[3[0-4][0-9]\.[0-9], 4[0-9][0-9]|\[2[5-9][0-9]\.[0-9], 4[0-9][0-9]"
