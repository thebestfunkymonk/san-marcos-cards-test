# v3-system progress (continuous double-head support)

## iter 0 — survey
- read build.py, cardsvg.py, frames.py, qa.py, ART_CONTRACT.md, tools/preview.py
- plan: frames seam API (seam_points / seam_d / seam_clip_d / seam_top_d / seam_debug_svg), build opts in via DOUBLE_HEAD/SEAM,
  cardsvg.two_headed overlap, court_frame_fragments(band=False), qa 10b (band structure) + 10s (seam continuity), check 5 window.

## iter 1 — implemented + proven (2026-10-01)
- frames: DOUBLE_HEAD_MODES, SEAM_ANGLE 28, SEAM_OVERLAP 0.5 (0.25 still showed AA hairline; 0.5 = 0 levels in rsvg+resvg),
  SEAM_DRAW_PAST 12; double_head_mode, seam_points (angle | half/full point list | path d | dict), seam_top_d, seam_clip_d,
  seam_draw_d, seam_d, seam_y_at, seam_partner, seam_strip_d, seam_spec, seam_debug_svg, seam_debug_png,
  CLI `python -m deck.frames seam <svg|ID> [--module|--seam] [--out]`; court_frame_fragments(double_head=...)
- cardsvg.continuous_two_headed; build records double_head + seam in manifest
- qa: 10b band-structure (✗), 10s seam continuity (! ; extended-top re-render diff in 0.9–6 px strip), check 5 whole window
  for continuous, flags overlay magenta; tools/preview.py writes <STEM>-seam.png and prints warn as "!"
- ART_CONTRACT: §3.1 split, new §3.1b, §6/§7/§8/§9, §10 client-direction entry
- test court build/review/v3-system/test_court.py (SEAM_TEST=clean|curve|broken): clean+curve all ✓ incl. 10s;
  broken flags 4 C2-paired breaks (10s) + 4c/12 near-misses. Legacy: deck.qa courts → 174 pass, 0 fail, 6 warn (raster 12, pre-existing)

## iter 2 — re-verify after courtkit churn + legacy-cut guard (2026-10-01)
- re-ran test court clean/curve/broken: unchanged (clean/curve 10s ✓, broken flags C2-paired breaks)
- legacy: all 12 art/ courts built+QA'd via tools/preview.py into scratchpad (not cards/, to avoid clobbering other agents'
  in-progress builds): 0 ✗; only pre-existing raster-12 "!" warnings
- smoke test: copy of art/KH.py + DOUBLE_HEAD="continuous" (build/review/v3-system/realart/) exposed a 10s blind spot:
  band-mode art (cut at y 511, medallion hole) leaves paper on BOTH sides of the seam → no colour diff.
  Added qa.legacy_cut (+ LEGACY_CUT_MIN 24 px) inside 10s: art just above y 511 / paper just below, where seam is lower.
  KH copy → flags x 142–339 (198 px); clean/curve test courts → no false positive. ART_CONTRACT §(10s) updated.
