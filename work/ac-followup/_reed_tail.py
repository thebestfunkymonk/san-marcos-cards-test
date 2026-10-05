# =============================================================================
# the gold wreath (outside the club)
# =============================================================================
# §G.4 ribbon blades for the wreath: (length of the knot-ward pair, length :
# width, angle off the stem, S bend (b0, b1) — + turns away from the stem,
# and whether the blade is half-hatched across its tip half). The OUTER blades
# (convex side) are long and stream tip-ward along the arc; the INNER ones
# (toward the club) are shorter, stand further off and stay plain.
BLADE_OUTER = dict(L=100.0, ratio=13.5, angle=10.0, bend=(-10.0, 14.0), hatch=True)
BLADE_INNER = dict(L=62.0, ratio=12.0, angle=26.0, bend=(-6.0, 14.0), hatch=False)


def wreath_blade(p, heading: float, side: int, L: float, W: float, angle: float, bend, hatch: bool):
    """One wild-rice ribbon blade springing TANGENTIALLY from the stem at
    ``p`` (stem heading ``heading``) on ``side`` (+1 = left of travel): a
    sheath (petiole) leaves on the stem's heading and turns ``angle``° away
    over 0.1 L, and the blade continues it on a §G.4 S midrib of two tangent
    arcs turning ``bend`` = (b0, b1)° (+ = away from the stem), with a vesica
    profile L × W. Blades are narrower than 12.6 px, so (the deck's narrow
    ribbon, deck.motifs.rice) no midrib is drawn and a ``hatch``-ed blade is
    hatched across its tip half — the ribbon turning over. → (Frag, filled
    region, blade base)."""
    pet = max(6.0, 0.1 * L)
    _, pp, _ = forms.arc_path(p[0], p[1], heading, [(pet, -side * angle)])
    q = pp[-1]
    lf = RI.ribbon_leaf(q[0], q[1], heading - side * angle, L, W, bend=(-side * bend[0], -side * bend[1]),
                        hatch=side if hatch else 0, narrow="tip", full=False, color=GOLD)
    f = M.stroke(M.polyline_d(pp), FINE, color=GOLD, role="petiole") + lf
    return f, M.region(M.polyline_d(lf.meta["outline"], closed=True)), q


def wreath(cx: float, cy: float, r: float, *, pairs: int = 3, outer: dict | None = None,
           inner: dict | None = None, spike: dict | None = None, knot_deg: float = 90.0,
           tip_deg: float = 30.0, step_deg: float = 14.0, first: float = 0.55, shrink: float = 0.06) -> M.Frag:
    """§G.6 / §H.15 the wild-rice half-wreath cupping the club from 4 to 8
    o'clock: ONE continuous arc stem per side (radius ``r`` round the pip
    centre) from the reed-node knot at 6 o'clock (``knot_deg``) to 4 o'clock
    (``tip_deg``), where it runs on into a flowering spike (§G.5).

    * Every ``step_deg`` (14°) of stem from ``first`` × pitch, ``pairs`` PAIRS
      of ribbon blades (§G.4) spring tangentially from it, each pair 6 %
      (``shrink``) smaller than the last toward the tip. Blades keep §G.4's
      10–14 : 1 (``outer`` / ``inner`` specs, :data:`BLADE_OUTER` /
      :data:`BLADE_INNER`) on S midribs, so the wreath reads as wild-rice
      GRASS: short 4 : 1 vesicas on a stem read as olive / laurel, which
      §G.6 bans (art-director review). Three pairs: a fourth, at 50°, would
      reach its blades into the spike.
    * Tip-ward blades lie over knot-ward ones (T-junctions on the front
      outline, hatch included); the blades break 4.2 px clear of the spike's
      lines (interlace); the stem is never broken by its own blades.
    * The spike: three erect awned spikelets on 8 px pedicels, so every
      spikelet stands >= 3 px clear of the stalk; the stem runs on 10 px up
      its stalk (drawn over it), so the first pedicel springs from ONE line.
    * The two stems run into the knot's node ellipse and end on its rim; the
      cut ends splay below it (deck.motifs.rice's reed-node knot)."""
    outer = dict(BLADE_OUTER, **(outer or {}))
    inner = dict(BLADE_INNER, **(inner or {}))
    pts = G.arc_pts(cx, cy, r, knot_deg, tip_deg, n=400)
    cv = G.Curve(pts)
    pitch = math.radians(step_deg) * r
    units, bases = [], []
    for k in range(pairs):
        s = (first + k) * pitch
        p, t = cv.at_s(s), cv.tangent_s(s)
        a = math.degrees(math.atan2(t[1], t[0]))
        sc = (1 - shrink) ** k
        # +1 = left of travel: on the right-hand branch (knot -> 4 o'clock) that is the inside
        for side, spec in ((1, inner), (-1, outer)):
            L = spec["L"] * sc
            f, reg, q = wreath_blade(p, a, side, L, L / spec["ratio"], spec["angle"], spec["bend"], spec["hatch"])
            units.append((f, reg))
            bases.append(q)
    # the flowering spike on the stem's end
    p, t = cv.at_s(cv.length), cv.tangent_s(cv.length)
    sk = dict(n_female=3, n_male=0, spikelet_len=12.0, awn=15.0, female_spread=64.0, pedicel=8.0, f_pitch=14.0)
    sk.update(spike or {})
    length = sk.pop("length", 44.0)
    sp = M.rice_stalk(p[0], p[1], math.degrees(math.atan2(t[1], t[0])), length, color=GOLD, **sk)
    # stacking, back to front: knot-ward blades lie under tip-ward ones
    lv, front = M.Frag(), None
    for f, reg in units[::-1]:
        lv += M.occlude(f, front) if front is not None else f
        front = reg if front is None else front.union(reg)
    lv = M.cut(lv, sp.shape(), A.CLEAR)
    lv = M.prune_hatch(M.drop_specks(lv, 4.2, roles=None), 1.3)
    # ONE continuous stem, running on 10 px up the spike's stalk
    stem = M.stroke(M.polyline_d(pts) + M.polyline_d([p - t * 1.0, p + t * 10.0]), FINE, color=GOLD, role="stem")
    branch = stem + lv + sp
    out = branch + branch.mirror_x(cx)
    knot = RI._reed_knot((cx, pts[0][1]), 90.0, color=GOLD)
    out = M.drop_specks(M.occlude(out, knot.meta["zone"]), 4.2, roles=None) + knot
    out.meta.update(stem=pts, bases=bases, pairs=pairs)
    return out
