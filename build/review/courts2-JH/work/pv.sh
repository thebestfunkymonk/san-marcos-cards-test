#!/bin/bash
# pv.sh <module.py> <tag>  -> out/<tag>/{JH.png,JH-188.png,JH-1500.png,hL.png,hR.png}
cd /home/luke/Projects/design/san-marcos-deck
W=build/review/courts2-JH/work
O=$W/out/$2; mkdir -p $O
.venv/bin/python tools/preview.py $1 JH $O ${3:---qa} > $O/pv.log 2>&1 || { tail -30 $O/pv.log; exit 1; }
svg=$O/JH.svg
$W/zoom.sh $svg 490 225 100 110 6 $O/hR.png g
$W/zoom.sh $svg 205 385 100 120 6 $O/hL.png g
grep -E "^\s*(✗|!|FAIL|WARN)|balance|fail|warn" $O/pv.log | head -20
