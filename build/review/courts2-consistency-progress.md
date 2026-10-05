# courts2-consistency — art-director deck-wide consistency pass (read-only on project files)

Scratch: build/review/courts2-consistency/
## Iteration log
- it0: recorded current kit hand calls (work/calls.json: 19 kit hands; KS L, KC L, QC R, JD both not kit fist/flat — custom/cup); rendered after_small (188); row montages K/Q/J at 750 + 188 (+ before 188).
- it1: montages: hands_all_3x.png (24 hands, same 3x scale, labelled), hands_all_1x.png (card size), hands_before_after_3x.png + pairs/ba_*.png, palmview_fists_3x.png, backview_{left,right}_3x.png, row_{K,Q,J}_750.png, row_{K,Q,J}_188(.png|_before.png), rows_188_ba.png, contact_before_after.png, top/pair_*.png (750 top halves b|a), faces_1/2.png (3x b|a), diff_all.png (pixel diff overlay), win/<ID>.png (3x art windows).
- it2: deck.qa courts → 162 pass / 0 fail / 6 warn (raster pattern-level only: KS 6, QS 2, KH 12, KC 8, QC 2 thin+12, QD 2); rebuild md5-identical (work/md5_pre/post). Copy: qa-courts.json.
- it3 findings: hand family consistent (back-view fist ×14, palm-view fist ×6, cup ×2, flat ×2). Remaining: QC sceptre arms lost lower outline + orphan stub (QC-verify-2 regression, unfixed; ink 18.9 at ceiling); QC R palm-view thumb = only outlier vs KS/QH/KC/JC/KD R; JC belt-hand ulnar edge forks from the jade panel seam at the cuff corner (JC-verify-2, unfixed); KD left gauntlet top edge fused sleeve+cuff outline wedge ~2x MEDIUM (KD-verify-2, unfixed); balance drifts QD red 12.1→10.9, QS jade 14.7→13.5 (low).
