# JOKER_RED final pass -- art director's major notes (2026-09-24)

Notes: (1) the ring's ~34 px paper face splits the pig (rump reads as a second small animal) -> carry the red barrel
through the ring as two gold wires with body between (4.2 gaps), or cut the face to <= 10 px; (2) the hatched belly
lens reads as a folded wing / shell -> crescent <= 14 px along the belly line, or drop it.

Working copies: scratchpad jr/src (backup of the installed files in jr/bak).

## Log
- Started: read JOKER_RED.py, _joker_red_{pose,pig,water}.py, prior progress/critique (JOKER_RED-2-*), brief §H.17, §B.2.
- v00: baseline preview of the installed files (scratchpad jr/v00): the rump + hind legs + tail beyond a 34 px paper
  ring face read as a small leaping animal; the big hatched lens read as a wing.
- v01 (note 1): the ring's rump-side half now passes in front as TWO WIRES -- the red is cut GAP (4.2) clear of each
  gold wire only, so a 12 px red band of loin shows between the wires and the barrel runs on into the ham; rivets
  that would land on the red are dropped (no gold on red, §C rule 4; a moated rivet would sever the 12 px band).
- v02 (note 2): the lens + barrel line replaced by a narrow crescent window along the belly edge (<= 12.5 px wide,
  tapering to both ends, 3.6 px red rim, FINE red hatch 45 deg to the axis).
- v03: ham line dropped -- it sat on the ring's outer wire, so the wire's channel cut it into two orphan stubs (and
  the channel now marks the ham's front). Crescent lengthened (u -58..36). Preview QA: all pass.
- v04: a short ham (thigh) line restored just beyond the outer wire, from the stifle fold up and back toward the hip,
  bowing toward the head against the ring's arc (it models the thigh the hind legs spring from, not a second rim).
- v05/v06: dead code removed (ring_face, belly lens, square_ends, forms_split, BARREL_LINE); docstrings updated.
  Measured: crescent max width 12.4 px, length ~86 px; red loin band between the wires 12.0 px (3 red pieces:
  rump 7248 px², band 1471 px², barrel+head 35239 px²). SVG identical to v04.

## Final (2026-09-24 09:58)
- Installed art/JOKER_RED.py, art/_joker_red_pig.py, art/_joker_red_pose.py (_joker_red_water.py unchanged).
- deck.build JOKER_RED (+ --stock white); deck.qa JOKER_RED: 12 pass, 0 fail, 0 warn
  (strk pal budg hide g/r idx safe clr gaps svg rndr wht).
- Review: build/review/final-JOKER_RED-{pair,before-after,188-before-after-black,crop3x-ring,crop3x-barrel}.png.
- Note: `deck.qa JOKER_RED` rewrites build/qa/report.json with this piece only; a full-deck qa run restores the rest.
