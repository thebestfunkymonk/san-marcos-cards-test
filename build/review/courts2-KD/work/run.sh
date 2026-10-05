#!/bin/bash
# run.sh <tag> [crop specs at 3x...] : preview art/KD.py into work/<tag>, heal log (non-hatch), standard crops
set -e
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-KD/work
P=.venv/bin/python
T=$1; shift
$P tools/preview.py art/KD.py KD $W/$T 2>&1 | tail -1
$P $W/probe.py art/KD.py 2>&1 | grep -v '"hatch"' > $W/$T/heal.txt || true
$P $W/crops.py $W/$T/KD.svg $W/$T/c 3 top:139,55,611,511 handL:300,340,450,490 handR:470,330,600,511 "$@"
$P $W/crops.py $W/$T/KD.svg $W/$T/c 6 handL:318,362,428,462 handR:490,350,590,440
cat $W/$T/heal.txt | head -70
