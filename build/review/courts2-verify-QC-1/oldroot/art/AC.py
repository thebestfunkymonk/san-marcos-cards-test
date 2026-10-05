"""art/AC.py: A♣ · The Reed (brief §H.15).

An Aquifer club (u 280) with one botanically true wild-rice plant knocked
out to paper (MEDIUM lines, solid paper grains and leaf halves: geometric
holes in the pip, never paint), read from the rock up:

* the plinth's two steps carry two strata lines; the culm stands on the
  upper one — the plant grows out of the limestone;
* two ribbon leaves (§G.4) sweep out from the stem base: their sheaths
  clasp the culm up the stem, and at the collar the blades rise as a lyre
  round it, bowing out, in, and curling out at the tips in the top lobe.
  Each is split on its midrib, the lit half (toward the culm) solid paper,
  the shaded half hatched perpendicular to the midrib;
* the culm rises up the stem into the top lobe and ends in the panicle's
  ERECT female part: a terminal spikelet and two alternating pairs of
  stiffly erect, awned spikelets on short spreading pedicels (§G.5);
* below it the panicle's male branch springs from the culm on each side,
  passes BEHIND the leaf (broken 4.2 px clear; its root stays hidden) and
  slants out and down into the side lobe, drooping at its end; its awnless
  florets hang PENDULOUS on pedicels, fanned about §G.5's ±150°
  (refs/smtx/wild_rice.jpg) — "drooping male florets fall into the side
  lobes".

Why this composition: blades bent round the side lobes under an arched
branch of florets (the previous draft) read at 188 px as a face — two
crescent eyes with lashes under two brows. Here the leaves stand upright
and frame the culm (a grass, not a tree), and the florets hang from
descending branches that belong visibly to the plant.

Outside, in gold FINE line: the keyline, and the wild-rice wreath (§G.6)
cupping the club's base from 4 to 8 o'clock on one continuous stem per
side, tied at 6 o'clock with a reed-node knot and ending at 4 o'clock in a
flowering spike. Its leaves are wild-rice RIBBON blades — §G.4's 10–14 : 1
on S midribs (outer 13.5 : 1, streaming tip-ward along the arc and
half-hatched across the tip half; inner 12 : 1, plain), three pairs per
side shrinking 6 % a pair: the previous short ~4 : 1 vesicas read as an
olive / laurel wreath, which §G.6 bans. The wreath lies behind the club
(anything reaching the keyline is broken 4.2 px clear of it); at r 194 the
inner blades clear the plinth outright. Gold prints above the Aquifer on
this card (§K; the system orders layers).
"""
from __future__ import annotations

from deck import tokens as T
from deck import motifs as M
from deck.cardsvg import layers_merge
from inkkit import geom as G

from art import _aces_common as A
from art import _aces_reed as R

SUIT = "C"
W = A.KO
CX = A.CX
TREAD = 14.0                              # §E.1 plinth tread 0.05 u
STEM_FOOT = 587.6                         # the stem meets the upper tread
STRATA = (STEM_FOOT + TREAD / 2, STEM_FOOT + 1.5 * TREAD)     # 594.6, 608.6: mid-tread
TREAD_HALF = (42.0, 56.0)                 # half-widths of the upper / lower tread

CULM_TOP = 372.0                          # the terminal spikelet's base
FEMALE = dict(tiers=2, pitch=14.0, first=13.0, L=16.0, wd=5.0, ped=8.0, spread=50.0, lean=18.0, awn=12.0,
              top_L=16.0)

# male branches (right; the left is the mirror): root y on the culm, start
# heading, (length, turn) arcs, florets [(fraction, hang°, pedicel)]
# the male florets: §G.5's vesica (3 : 1, a little smaller than the female
# spikelet), hung on pedicels at 70–84° — i.e. about §G.5's ±150° from the
# culm's axis, fanned and of two pedicel lengths so they DANGLE; hung
# plumb and evenly spaced (the previous draft) they read as a comb's teeth
FLORET = dict(L=14.0, wd=4.8)
MALE = [
    (452.0, -28.0, [(24.0, 0.0), (16.0, 50.0), (40.0, 8.0), (34.0, 22.0)],
     [(0.42, 74.0, 11.0), (0.59, 84.0, 8.0), (0.75, 70.0, 11.0), (0.89, 80.0, 8.0), (1.0, 0.0, 0.0)]),
]

# ribbon leaf (right): sheath up the stem, 6 px off the culm, to the collar
# above the stem's crotches; then the blade — an S of three tangent arcs
LEAF_SHEATH = [(382.4, 592.0), (381.9, 492.0)]
LEAF_H0 = -90.0
LEAF_TURNS = [(40.0, 32.0), (55.0, -30.0), (34.0, 38.0)]
LEAF_WIDTH = 14.0                         # 140 px blade: 10 : 1 (§G.4)
LEAF_HATCH = +1                           # the outer half is hatched, the half toward the culm lit

WREATH_R = 194.0                          # §G.6 wreath on a circle round the pip centre;
                                          # 194 lets the inner blades clear the plinth


def plinth() -> M.Frag:
    """§H.15 the plinth steps as two strata lines, each on its tread's middle,
    ending 7 px short of the step's ends (butt, like the fault-step rules)."""
    d = "".join(M.polyline_d([(CX - hw + 7.0, y), (CX + hw - 7.0, y)]) for hw, y in zip(TREAD_HALF, STRATA))
    return M.stroke(d, W, style="rule", role="strata")


def culm() -> M.Frag:
    return M.stroke(M.polyline_d([(CX, STRATA[0]), (CX, CULM_TOP)]), W, role="culm")


def female() -> M.Frag:
    return R.female_panicle(CX, CULM_TOP, **FEMALE)


def male() -> M.Frag:
    f = M.Frag()
    for root_y, h0, turns, fl in MALE:
        f += R.male_branch((CX, root_y), h0, turns, fl, **FLORET)
    return R.mirror(f)


def leaves() -> M.Frag:
    return R.mirror(R.leaf_with_sheath(LEAF_SHEATH, LEAF_H0, LEAF_TURNS, LEAF_WIDTH, LEAF_HATCH))


def spray() -> M.Frag:
    lv = leaves()
    # the male branches pass behind the leaves: broken 4.2 px clear of them
    males = M.cut(male(), lv.shape(), A.CLEAR)
    # ...and their roots stay hidden behind them too: the short stub left
    # between culm and leaf read at 750 px as a chevron (an arrowhead) on the
    # culm. Only the BRANCH stubs go; the pedicels are short by nature.
    stubs = A.drop_short(M.Frag([m for m in males.marks if m.role == "branch"]), 14.0)
    males = M.Frag([m for m in males.marks if m.role != "branch"]) + stubs
    return culm() + female() + males + lv + plinth()


def build():
    pip = A.knocked_pip(SUIT, spray(), color=T.INK)
    wr = A.behind(R.wreath(CX, A.CY, WREATH_R), SUIT)
    gold = A.keyline(SUIT) + wr + A.caption(SUIT)
    return layers_merge((pip + gold).fragments())
