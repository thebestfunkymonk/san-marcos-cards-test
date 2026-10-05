# final-tuck progress (AD major notes on the tuck)

## 2026-09-24 session 1
- Note 1 (stale A♠ in mocks): build/png/AS.png is current (09-24 09:34, cat-faced lion); the mocks were
  built 09-23 23:52. Fix = re-run `python -m tuck.build_tuck` (with mocks) LAST, after the lion work.
- Note 2 (lion andante body): tuck/_tuck_lion.py redrawn — BODY table replaced:
  * near fore advanced + flexed at the carpus onto the ledge; it now passes IN FRONT of the outer (chest)
    mane row (mane split into mane_in / mane_out, parts()/order in lion_andante) so the forearm shows;
  * far fore raked back (hatched), far hind swinging forward (hatched), near hind pushing off (stifle
    forward, gaskin raked back to a sharp hock, cannon raked back into the ripples); buttock slimmed;
  * MEDIUM form lines: shoulder (triceps arc) + haunch (loin → flank fold) in torso();
  * underside (belly + far flank) half-hatched 7.0 below a FINE terminator between the form lines;
  * far legs hatched mirrored (-135) with phase origins chosen so no trap slivers (only the 2 old
    wing traps remain; was 11).
- Original module backed up at scratchpad _tuck_lion.orig.py (session-local).
- build_tuck --no-mock: all pieces pass (FRONT ! 146 tight-board warnings — check vs before).
- Hatch direction: belly + far legs mirrored (-135, "\") — crosses the MEDIUM shoulder/haunch lines square;
  lion tight-board warnings 526 px² → 355 px² (21 → 18 clusters); traps 11 → 2 (both old, in the wing).
- Near forepaw widened (heel -78.5); elbow reshaped so a chest-row lock tip is hidden (no trap).
- build_tuck + _tuck_mock: new `mock_inputs()` freshness guard — presentation embeds (BACK, AS) are
  checked against art/<ID>.py + art/_<id>_*.py; stale → "!! STALE" warning + QA `mock_inputs.ok = false`.
- FINAL full `python -m tuck.build_tuck` (with mocks) 09-24 10:22: all pieces ✓ (1/4/8/12/17/25), copy ✓,
  mock inputs fresh ✓ (AS.png 09:34:23 ≥ AS.py 03:28; BACK.png 09:34:48). FRONT ! 141 tight-board (warn).
  TUCK-PRESENTATION now shows the current cat-faced A♠.
- Seal not touched (not in this agent's ownership; SEAL.svg read-only by the mock).
- If build/png/AS.png or BACK.png is rebuilt after 10:22, re-run `python -m tuck.build_tuck` (the guard
  will not flag a newer PNG; it only flags PNGs older than their art sources).
