# JOKER_RED pass 2 progress log (solid-silhouette Fool)

## 0. Start
- Director's decision: pig as a SOLID Gill Red silhouette with geometric paper knockouts (sibling of JOKER_BLACK).
- Read brief §B §C §F.4 §H.17 §I §J, style.md, ART_CONTRACT §3.3, JOKER_BLACK code + render, current JOKER_RED (line-only, reads as donkey/rabbit).
- Refs added: research/refs/jokers/pig_skeleton_hog.png, pig_skeleton_dalton.jpg, pig_race_ocfair.jpg (pig over a hurdle, head down,
  forelegs folded, ears up, tail curled), pig_race_752.jpg (Wikimedia Commons).
- Old modules backed up to scratchpad before rewrite.

## 1. Iterations v01-v15 (new modules)
- New art/_joker_red_pose.py (Frame / BendFrame drafting frames, anatomy tables) and art/_joker_red_pig.py (ONE red solid,
  MEDIUM paper knockouts, red FINE hatch windows, eye almond + Aquifer dot, gold collar in a paper channel).
  JOKER_RED.py rewritten: ring's rump-side face cuts the red solid (+4.2 gap) so gold sits on paper; snout-side ring cut clear of the pig.
- Found: line-thin legs read as fingers/hands; straight tube body reads as a sleeve -> BendFrame spine arc (DIVE_R 560), belly sag,
  shorter stockier legs, cloven wedge trotters with dewclaws, belly half-hatch tract (rib-like), broad ear (arc bulge sign fixed).
- Collar: dags pointing back (toward body) read as a CROWN -> dags now hang toward the head (reads as jester collar).
- Next: collar spacing, eye, hind legs, tail loop, placement (snout above ripples), water, QA.

## 2. Iterations v16-v24
- Tail: loop with the end passing OVER the stalk (interlace gap 3.2); bubble trail starts at the tip.
- Hind legs: thin trailing gaskin/cannon with hock point knob (HOCKS); forelegs straight, reaching down the jaw
  ("diver's arms"), trotters now angular heraldic wedges (sharp toes, deep cleft notch; dewclaw on hind only).
- Head: deeper snout, larger disc (DISC_R 10x23), almond eye (17 x 13.4) + lid crease, shorter mouth.
- Collar: dags distributed on the VISIBLE part of the band (between the ear and the near foreleg).
- Draft QA v24: vector 12 clean; one raster paper wedge at the belly window corner -> windows opened by 2.6.

## 3. Session 2 restart (2026-09-24 03:20): v24 read as a cow/donkey head on a box body -> full redraw
- v24 modules backed up to scratchpad/jr_v24/. New refs: research/refs/jokers/pig_dive_flickr_*.jpg (Openverse/Flickr CC:
  show pigs leaving the diving tower -- 4904177262 is the key pose: body ~50 deg, head steeper, hind legs trailing, forelegs folded).
- Silhouette-first prototyping (scratchpad/p2/sil.py, full.py): canonical profile tables in a bent BODY frame + HEAD frame.
  Findings: thick legs read as bear/arm limbs -> legs ~0.2 D; long lanky torso reads as a sausage -> compact fat barrel
  (~1.9 D long, D 145 drafting at S 1.2); head in line reads anteater -> shorter wedge head (~0.75 D), flat disc end
  with a paper rim arc + two nostril holes; near foreleg forward (trotter leads), far foreleg folded (breaks the "two arms").
- v26-v35: knockouts (shoulder, ham, barrel line, mouth, lid, disc rim, ear base, far-leg edges, coronets, closed clefts),
  half-hatched ear inner half + belly crescent, gold collar (band + 5 dags + bells, bells kept clear of ear/foreleg),
  spiral tail. Reads as a pig at 750 and 188. Open: barrel inside the ring reads as a sack/bucket; 10c (hind trotter
  at x<130); QA 12 bridges.
- v36-v46: pig shifted up-left along its axis and steepened (HB 58): the rump, ham line, hind legs and tail now sit
  outside the ring's rump-side rim (hindquarters read as "behind the rim"), head + forelegs out front below.
  Leaf-shaped prick ear (was a horn); barrel rounder (belly v 90, back arched, convex barrel line); collar
  convex toward the head, bells kept clear of ear/foreleg. QA fixes: hoof coronet/cleft 3.4 px inside the edge,
  rounded hoof tips, belly hatch window squared parallel to the hatch, solid cleaned after the ring cut, ear-root
  and tail-root fillets, first bubble clears the whole tail. v45: preview QA all clear.
- v47-v57: tried offsetting the pig across the ring (rejected: the ring's front half then slices the belly);
  hind legs lifted to trail up-left (10c clear); belly tract widened to a band along the belly (reads as the
  barrel's shaded underside); hoof half-hatch windows tried (too small: read as "A" glyphs) -> reverted to coronet
  arc + short separate cleft near the toe (a joined cleft read as a "T"); leg creases closed (r 3).
  Collar: now gold on a PAPER GROUND (moat with the V's between dags closed) -- no red slivers; dags hang along
  the head axis, fanned +-14 deg, evenly spaced bells: reads as a jester collar, not a crown. QA clear.
- v58-v62: shoulder line shortened (no longer arches over the back: the "helmet" read gone); hind legs given a real
  hock angle (point of the hock proud, dorsal, cannon angling back-ventral); disc, ear and tail curl enlarged for
  the 188 read; nostrils/disc-rim margins for §I.12. QA clear.
- v63-v64: red crumbs between the collar's paper ground and the ear filled (the ear now stands on the collar
  ground); ear hatch window kept RIM + KO/2 inside the ear so the base line keeps a red rim.
- Official: deck.build JOKER_RED (+ --stock white) and deck.qa JOKER_RED -> 12 pass, 0 fail, 0 warn.
- v65-v70 (critique: at 3x the head pointing ~80 deg read as a COW's face seen from the front -- the dorsal ear
  stuck out sideways like a cow's, the symmetric muzzle with two nostrils at the bottom): ear swept BACK along the
  neck (tip up the page, as the dive would lay it) and broadened; snout slimmed, chin set back so the disc
  overhangs the mouth; HEAD_FLEX 10 -> -4 (head ~65 deg: the head now reads unmistakably in PROFILE as a pig);
  collar's ventral end curves toward the head (no throat "teardrop" lobe); ring's snout-side half also clears the
  collar gold. QA clear.
- v71-v77: dive steepened HB 58 -> 61 (still reads in profile); ham line shortened to the thigh's front (it ran
  concentric with the ring and read as a second rim); hind-leg gaskin tops tucked into the ham (a far-leg crescent
  crumb gone); tail redrawn as a spiral hook (stalk + 215 deg + inward 110 deg turn, end clear of the stalk; the
  earlier curl's end touched the stalk); tighter tail-root fillet. Docstrings rewritten for the solid construction;
  unused hoof-window code removed.

## 4. Final (2026-09-24 ~04:15)
- deck.build JOKER_RED (+ --stock white); deck.qa JOKER_RED: 12 pass, 0 fail, 0 warn (strk pal budg hide g/r idx
  safe clr gaps svg rndr wht).
- Review renders: build/review/JOKER_RED-2-pair.png (with JOKER-BLACK), JOKER_RED-2-188-pair.png,
  JOKER_RED-2-1500.png, JOKER_RED-2-crop3x-{head,rump,forelegs-collar}.png.
- Deviations to flag: trotters carry coronet + cleft knockouts, not hatch (hoof half-hatch windows were ~5 px
  and read as glyphs at 3x); dive is 61 deg at mid-barrel (45 at the rump, 72 at the shoulders), head 68.5 deg ("slight diagonal" read as off-vertical, kept
  for the profile read); collar sits on a paper ground (no Aquifer contour: Aquifer is eye-only per §C budget).

## 5. Senior pass (2026-09-24) -- critique build/review/JOKER_RED-2-critique.md
- Fresh-eyes verdict: four islands (rump+claws, bucket barrel, crown, severed head). Fix list: reattach head (thin moat
  collar), ear on the poll, streamlined slimmer barrel with paper inside the ring, heraldic jointed legs with cloven
  notches, both fore trotters forward and breaking out below, knockouts as form lines, shorter tail stalk.
- Working copies: scratchpad/fr3/src (backup of the pass-2 final in scratchpad/fr3/bak).
- s00-s15 (silhouette sketches, scratchpad/fr3/sk.py; flat + dive modes): slimmer streamlined torso (D 126, length ~2 D),
  bigger head with deeper jowl and flared disc, bigger laid-back ear; heraldic volant legs: both fore trotters forward
  (parallel to the head, the near one leading), hind legs trailing in line (splayed / vertical legs read as a raised arm
  or frog kick); cloven trotters with a V NOTCH in the outline (hoof_poly). Head raised (-24 flex) read as a begging
  dog; steep body + raised head read as rearing -> body 58 deg, head flex -14, DIVE_R 700.
- v01-v12 (full previews, scratchpad/fr3/vNN): collar gold on a 3.6 moat only (no ground band) -> head attached;
  dags fanned 30 deg so the bells clear each other, red crumbs inside the collar dropped; tried pig inside the ring
  with only legs crossing the rim (v04/v05: legs vanish, pig "stands in a porthole") and a smaller pig (can with a dome)
  -> kept the big pig with the ring's face across the loin and the whole ham + ham line + legs + tail beyond the rim
  (v11: hindquarters read as one end of the same pig). Belly band hatched at 45 deg; nostrils moved inside the disc;
  trotter cleft dashes removed (the notch carries it), coronet kept.
- v13-v22: rejected a lean Tamworth torso (v14: a tube/can inside the ring) and a pig sized to sit inside the porthole
  (v15: rump cropped, tail lost). Kept v11 geometry (S 1.12, BODY_O (352,306), HB 58, DIVE_R 700). Belly tract
  re-cut as a crescent LENS (barrel line bowed dorsally) hatched at 45 deg to the axis (axis-parallel read as a shell,
  horizontal as a grille) -> the barrel reads round, not a can. Hind legs: hock bent the right way (thigh back-ventral,
  gaskin back-dorsal with the hock point dorsal, cannon back-ventral) -- the reversed bend read as a waving arm;
  legs trailing together up-left. Shoulder line moved back off the collar (it read as a second collar). Head: mouth
  line along the lip, eye almond enlarged (dot >= 3 px clear), lid crease dropped (read as an angry brow and crowded
  the dorsal edge), jowl line dropped (clipped). Collar dags broader (0.8) fanned 22 deg. Preview QA clean (v22).
- v23-v37: ear swept back (tip -60,-38) and rooted on the poll in front of the collar; collar moved back behind
  the jowl (the ear now lies over it, joining head to neck); mouth line parallel inside the jaw; tail stalk points
  back and the curl turns AWAY from the rump (a left-turning curl sat on the croup like a lid handle); trotter cleft
  cut as a V after the leg's closing, and the leg-to-torso fillet limited to near the torso (the r7 closing had
  filled the clefts); head drawn 1.1x (HEAD_SCALE) for heraldic emphasis; eye a longer almond (17 x 10.4, dot 3.1 px
  clear) -- the round eye read googly. Docstrings rewritten (Tamworth-type pig, moat collar, belly lens).
- Installed in art/ (JOKER_RED.py, _joker_red_pose.py, _joker_red_pig.py, _joker_red_water.py unchanged);
  deck.build JOKER_RED (+ --stock white); deck.qa JOKER_RED: 12 pass, 0 fail, 0 warn.
- Final (senior): review set regenerated from the official build -- JOKER_RED-2-{pair,188-pair,1500,before-after,
  crop3x-head,crop3x-rump,crop3x-forelegs-collar,crop3x-barrel}.png; resolution appended to JOKER_RED-2-critique.md.
