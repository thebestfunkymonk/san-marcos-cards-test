# followup-AC progress (wreath leaves: olive/laurel vesicas -> wild-rice ribbons)

- [start] backups: work/ac-followup/{AC,_aces_reed,_aces_common}_orig.py.
- [cycle 1] v0 render work/ac-followup/out/v0 (QA12 warn: gold 2 thin/12 gaps, vector 0). Root cause: library rice_wreath_arc keeps inner-leaf WIDTH when it scales the length (inner 34.8 x 5.3 = ~5:1 drawn), outer 58x5.3. Explored library params (a1-a3: bundling/tangles) then own construction (work/ac-followup/reed_w.py, b1..f2). Chosen f1: r 194, 3 pairs, outer 100/13.5:1 angle 10 bend(-10,14) tip-hatched, inner 62/12:1 angle 26 bend(-6,14) plain; vector 0, wreath 7.6 px clear of keyline zone.
- [cycle 1] integrated: art/_aces_reed.py wreath() rewritten (wreath_blade + BLADE_OUTER/INNER), art/AC.py WREATH_R 194 + docstring. _aces_common.py untouched.
- [done] deck.build AC (limestone + white) + deck.qa AC: 11 pass, 0 fail, 1 warn (12 raster gold: 8 thin = the sharp miter-10 blade tips, 12 narrow-gap = blade/stem junction wedges; vector QA-12 clean, 0). v0 was the same warn class (2 thin, 12 narrow-gap; narrow-gap count is capped at 12).
  Blades: outer 100 -> 94 -> 88.4 px at 13.5:1 (W 7.4 -> 6.5; ~10.5:1 to the stroke's outer edge), inner 62 -> 58.3 -> 54.8 at 12:1 (W 5.2 -> 4.6; ~8.5:1 outer edge), all S midribs (outer bend -10/+14, inner -6/+14). Stem: one unbroken subpath per side (194 px) + 10 px run-on up the spike. Wreath 7.6 px clear of the keyline zone (no blade cut behind the plinth).
  _aces_common.py byte-identical to backup -> A♥/A♦/A♠ unaffected.
  Renders: build/png/AC.png, build/png/small/AC.png, build/white/png/AC.png, build/review/followup-AC-before-after.png, build/review/followup-AC-wreath3x.png, build/review/followup-AC-wreath-right3x.png
