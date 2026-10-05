# corr-wheels progress (equal corner-wheel clearances)

## iter 0 — setup
- backups of owned files + outputs: scratchpad wheels/orig, wheels/orig_out
- instances: art/_back_frame.py ROUNDEL_C (card back) -> tuck back (derived, +9.5,+9.5); tuck/_tuck_front.py ROUNDEL_C; tuck flat places panels (follows). tuck panels (sides/ends) have no roundels. _back_vent.py sand boils: not corner wheels, untouched.

## iter 1 — measure + options (card back, previews in scratchpad wheels/opts)
- BEFORE (raster 8x, jade holes / foil): back wheel bbox TL 41.5–95.5 x 47.5–101.5 -> side 3.95 / top 9.95 (geom 41.45/47.45); tuck front 25.95 / 31.95 to fold; tuck back 51/57 (to box companion inner edge 43.05: 7.95 / 13.95)
- note: outer RULE is 4.2 wide, so the wheel top was flush (0.05) with the outer rule's outer edge; sides lapped 5.95 beyond it
- options: A (71.5,71.5) gaps 6.95, 3 px off each band centre, coverage 18.21 %; B (74.5,74.5) gaps 9.95, flush with outer rule, ladder 6 px off-axis (reads drifted inward); C bands equalised 28/28 (wheel centred on both, gaps 6.95) squeezes the wave band -> rejected (not minimal)
- choice: A. wheel on the corner diagonal midway between the two band centres; outer rule + companion become diagonal-symmetric round each wheel

## iter 2 — applied
- art/_back_frame.py: wheel_centre(companion, band_x, band_y) -> (c, c), c = companion + (22 + 34)/4; ROUNDEL_C = (71.5, 71.5); docstring deviation updated
- tuck/_tuck_front.py: ROUNDEL_C = _BF.wheel_centre(42, 64, 76) = (56, 56)
- deck.build BACK (+white) + deck.qa BACK: all pass, 12 warn (pre-existing, identical to baseline preview), KO 18.2 %
- tuck build: FRONT 12_gaps flagged 2 x 3.1 px medallion<->outer RULE (x 37.6 / 731.4, y 534.5): geometry pixel-identical to before; tuck QA run length was order-dependent (13.1 along rule vs 11.4 along ring) and piece order changed. Fixed foil_gaps to use the shorter patch (min of both directions, as its comment intended). Verified: old and new fronts + all panels give identical verdicts under min (no other pair affected).

## iter 3 — final (DONE)
- AFTER raster: back 7.0/7.0 all corners (geom 6.95/6.95, centre (71.5,71.5)); tuck front 29/29 (geom 28.95); tuck back 54/54 to fold (10.9/10.9 to box companion inner edge 43.05); tuck flat front/back panels identical
- deck.qa BACK: 10 pass, 0 fail, 1 warn (12 raster, identical to baseline); KO 18.21 %; frame D2 ok; emblem C2-not-mirror ok
- tuck QA: all pieces pass 1/4/8/12/17/25; FRONT margin 28.95 (was 25.95); tuck back outer ladders pixel-identical (only the card outer-rule end moved)
- crops: build/review/corr-wheels/

## round 2 — verifier findings
- round-1 state snapshotted: scratchpad wheels/round1 (+ r2pre = round-2 outputs before the docstring-only rebuild; byte-identical after)
- FIXED band-rail stagger: art/_back_frame.py flush_band_ends() + band_rails(); rules() trims each band's two rails to the pair's longer break. Back TL: side rails 100.47/102.65 -> 102.65/102.65, top rails 100.47/96.63 -> 100.47/100.47 (raster 10x, all 4 corners, both stocks). Ladder posts above top rung (y 109): 8.5/6.35 -> 6.35/6.35 (orig 4.27/4.27). Rails >= 4.60 px clear of the wheel.
- tuck/_tuck_front.py frame_rules() uses the same helper: side 84.97/87.15 -> 87.15/87.15, top 84.97/81.13 -> 84.97/84.97; posts above rung y 92.5: 5.35/5.35. Tuck back follows (+9.5): side 112.15, top 109.97 flush; tuck flat identical.
- wheel clearances unchanged (back 6.95/6.95, front 28.95/28.95, tuck back 53.95/53.95 to fold).
- deck.qa BACK: 10 pass / 0 fail / 1 warn, report.json identical to round 1 (KO 18.21 %, frame mirror clusters none, emblem C2 mirror_lr 0.213). tuck QA: all pass; FRONT raster tight-board 139 (orig 141).
- build_tuck.py foil_gaps: original version still flags the new front (2 x 3.1 px medallion<->outer RULE, run 13) -- kept the min-run fix (file is in my ownership list); orchestrator to accept/revert.
- NOT DONE (held): print export / gallery / mock-ups (outside ownership; unconfirmed scope), brief §H.19.4 + ART_CONTRACT §10 (outside ownership). Crops: build/review/corr-wheels/r2/
