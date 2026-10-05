# =============================================================================
# 7  hands (v3: ONE silhouette, FIVE fingers — four fingers and an opposable thumb)
# =============================================================================
#
# One hand language for every kit hand (COURT_GUIDE §4 "Hands"; client
# direction v3: "integrate, don't stack"):
#
# * ONE paper silhouette per hand. Palm, four fingers and the thumb are merged
#   into a single region and drawn as one contour (MEDIUM, CONTOUR where it is
#   the figure's edge). Nothing is laid over the hand: no separate thumb piece,
#   no block of bands with a digit stacked on top, no halo of its own.
# * a FEW open MEDIUM interior lines: each finger separation leaves the
#   notch between two fingertips where the two outline strokes' inner edges
#   meet (no round cap sitting in the notch as a bead) and stops short of the
#   knuckles (staggered); the thumb has at most one line, its underside, open
#   and never wrapping round its tip; the palm view adds one thenar crease.
#   Lines keep ≥ 7.3 px centre to centre (4.2 px of paper, §I.12).
# * no step, no cap: a grip's thumb IS the fist's top edge (back view: a
#   wedge flush with the index top, rising to the back of the hand; palm
#   view: the top band, its tip in the column of fingertips); the underside
#   of a fist is one curve from the little fingertip into the wrist.
# * nothing behind caps against the hand: with ``add_to(halo=0)`` the lines
#   of the objects behind end under the hand's outline stroke (LINE_TUCK).
# * five digits with character: tapered fingers with round tips, the middle
#   finger longest, the little finger shortest and narrowest, a slight fan; a
#   thumb of believable length rooted low in the palm (the thenar mound flows
#   into the back of the hand with no line across it); a real wrist taper.
# * sizes follow the FACE, not the object held: ``size`` is the hand length
#   (wrist crease → middle fingertip, open) ≈ the face's chin-to-hairline
#   (``hand_size(face)``); the knuckle breadth (= a fist's height) is
#   ``HAND_K × size``. The old ``h`` (fist height ≈ max(0.92 h, 32)) still works.
# * wrists merge into sleeves: ``Hand.add_to`` cuts the wrist run with the cuff
#   it finds (the cuff edge is the one line at the junction); for a sleeve
#   with no cuff, ``Hand.silhouette(run)`` / ``Hand.with_sleeve(sleeve)`` give
#   hand + forearm as ONE outline.
#
# Poses: ``fist`` (grip a staff / sceptre / rod / stem at any angle; back or
# palm view; a bar held from above with axis 180, from below with 0),
# ``pinch`` (a small object — flower stem, key, chalice stem — between the
# thumb and index tips, the other fingers curled and stepped back), ``cup``
# (an orb held from below: the palm under it, the fingertips over its lower
# rim, the thumb on its rim), ``flat`` / ``open_hand``
# (an open hand or gesture, palm or back, fingers together or spread).
# ``hand(pose, ...)`` dispatches to them.

FIST_H_MIN = 32.0        # fist height floor: four fingers at ≥ 8 px pitch
FIST_H_K = 0.92          # fist height per unit of the caller's (old) h
FIST_LEN_K = 1.04        # fingertips → knuckle ridge, per unit fist height
FIST_TIP_OUT = 5.0       # fingertip lobes show at most this far past the shaft's far edge
HAND_K = 0.42            # knuckle breadth (= fist height) per unit hand length
HAND_STUB = 7.0          # px a hand runs on past its wrist point, under the cuff
PARALLEL_MIN = GAP + MEDIUM          # 7.3: centre distance of two parallel MEDIUM lines (§I.12)
HEEL_CLOSE = 8.0         # ground between a heel and a haloed shaft narrower than 2 × this turns to paper
ARM_WORDS = ("cuff", "sleeve", "forearm", "arm", "gauntlet", "bracelet", "wrist")
CUFF_WORDS = ("cuff", "gauntlet", "bracelet", "wrist")
LINE_TUCK = 1e-3         # the 'halo' of an unhaloed hand: lines behind stop under its outline stroke
HAND_LOG: list = []      # construction warnings, newest last (also issued as HandWarning)

# grip proportions (index → little)
GRIP_FH = (0.265, 0.27, 0.25, 0.215)    # each finger's share of the fist height
GRIP_OUT = (0.85, 1.0, 0.85, 0.50)       # fingertip reach past the shaft (× tip_out): the middle longest
GRIP_TILT = (-1.0, 0.0, 3.0, 8.0)        # degrees: + lifts the fingertip toward the shaft's up end (a slight fan)
GRIP_TIP_R = 0.47                        # fingertip lobe radius × finger height
GRIP_LINE = (0.30, 0.24, 0.34)           # back view: finger lines stop this far (× fist length) short of the knuckles
GRIP_THUMB = dict(tip=0.06, root=0.165, rise=0.22, crease_back=1.0, crease_palm=1.0)
PINCH_REACH = 0.14       # pinch: the index fingertip curls this far (× fist height) past the stem
PINCH_STEP = 0.07        # pinch: each lower fingertip stands this much (× fist height) further back


def hand_size(fc) -> float:
    """The hand length that goes with a face (``Face`` or its anchors): its
    chin-to-hairline length (the classical 'a hand is a face')."""
    a = fc.anchors if hasattr(fc, "anchors") else fc
    cy, r = float(a["center"][1]), float(a["r"])
    return float(a["chin"][1]) - (cy - 0.62 * r)


class HandWarning(UserWarning):
    """A hand the kit can draw but a court should re-seat (wrist position)."""


def _hand_warn(msg):
    import warnings
    HAND_LOG.append(msg)
    warnings.warn(msg, HandWarning, stacklevel=3)


def _unit(v, default=(1.0, 0.0)):
    v = np.asarray(v, float)
    n = float(np.hypot(*v))
    return v / n if n > 1e-9 else np.asarray(default, float)


def _qbez(p0, c, p1, n=18):
    t = np.linspace(0.0, 1.0, n)[:, None]
    return (1 - t) ** 2 * p0 + 2 * (1 - t) * t * c + t ** 2 * p1


def _edge(p0, u0, p1, u1, n=18):
    """Points of a smooth edge leaving p0 along u0 and arriving at p1 along
    u1: a quadratic Bézier whose control point is where the two tangents
    meet (straight when they do not meet ahead of p0 and behind p1)."""
    p0, p1 = np.asarray(p0, float), np.asarray(p1, float)
    u0, u1 = _unit(u0), _unit(u1)
    L = float(np.hypot(*(p1 - p0)))
    A = np.array([[u0[0], u1[0]], [u0[1], u1[1]]])
    ctrl = (p0 + p1) / 2
    if abs(np.linalg.det(A)) > 1e-6:
        s, t = np.linalg.solve(A, p1 - p0)          # p0 + s u0 = p1 - t u1
        if 0.5 < s < 1.6 * L and 0.5 < t < 1.6 * L:
            ctrl = p0 + s * u0
    return _qbez(p0, ctrl, p1, n)


def _to_local(pt, at, rot, mirror):
    """Screen point → a hand's local frame (inverse of _rigid)."""
    ww = P(pt) - P(at)
    rr = math.radians(-rot)
    q = P(ww[0] * math.cos(rr) - ww[1] * math.sin(rr), ww[0] * math.sin(rr) + ww[1] * math.cos(rr))
    if mirror:
        q[0] = -q[0]
    return q


def _vec(M, v):
    """Apply the linear part of shapely matrix M to vector v."""
    a, b, d, e = M[0], M[1], M[2], M[3]
    return P(a * v[0] + b * v[1], d * v[0] + e * v[1])


def _crease(boundary, inside, keep=None, min_len=3.0):
    """The part of ``boundary`` (a region's outline) that lies inside
    ``inside`` (and inside ``keep``, when given): a digit's edge where it
    lies on the rest of the hand. → list of point arrays."""
    rings = [LineString(np.asarray(pg.exterior.coords)) for pg in _polys_of(boundary)]
    if not rings:
        return []
    ln = shapely.union_all(rings)
    z = inside.buffer(-0.05)
    if keep is not None:
        z = z.intersection(keep)
    res = ln.intersection(z)
    try:
        res = shapely.line_merge(res)
    except Exception:
        pass
    return [np.asarray(g.coords) for g in _lines_of(res) if g.length >= min_len]


def _arm_dir(armr, W, u_guess, reach=8.0):
    """The forearm direction (unit, from the wrist into the arm) implied by
    the arm region's edge through the wrist point ``W`` (a kit sleeve's
    cuff line), or None when W is not on that edge or the edge is not a
    clear line within 55° of square to ``u_guess``."""
    b = armr.boundary
    pw = Point(*W)
    if b.distance(pw) > 2.5:
        return None
    near = b.intersection(pw.buffer(reach, quad_segs=16))
    try:
        near = shapely.line_merge(near)
    except Exception:
        pass
    ls = [g for g in _lines_of(near) if g.length > 0.5 * reach]
    if not ls:
        return None
    g = min(ls, key=lambda gg: gg.distance(pw))
    xy = np.asarray(g.coords)
    e = _unit(xy[-1] - xy[0])
    # a straight run: every vertex within 1.2 px of the chord
    nrm = np.array([-e[1], e[0]])
    if np.max(np.abs((xy - xy[0]) @ nrm)) > 1.2:
        return None
    us = np.array([e[1], -e[0]])
    if armr.contains(Point(*(W + us * 3.0))) == armr.contains(Point(*(W - us * 3.0))):
        if float(np.dot(us, u_guess)) < 0:
            us = -us
    elif not armr.contains(Point(*(W + us * 3.0))):
        us = -us
    if float(np.dot(us, _unit(u_guess))) < math.cos(math.radians(55.0)):
        return None
    return us


def _digit(cen, widths, quad=16):
    """A tapered digit (finger, thumb, wrist sweep): the union of the hulls
    of consecutive discs along the centreline ``cen`` (diameters ``widths``,
    one per point, or a (root, tip) pair). Round root and round tip."""
    cen = np.asarray(cen, float)
    if np.ndim(widths) == 0 or len(widths) != len(cen):
        w0, w1 = (float(widths), float(widths)) if np.ndim(widths) == 0 else (float(widths[0]), float(widths[-1]))
        widths = np.linspace(w0, w1, len(cen))
    ds = [Point(*q).buffer(max(float(w) / 2, 0.3), quad_segs=quad) for q, w in zip(cen, widths)]
    if len(ds) == 1:
        return ds[0]
    return shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])


def _bend(p0, d0, length, curl_deg, n=12):
    """A digit centreline from ``p0`` heading ``d0`` (unit), ``length`` long,
    bending ``curl_deg`` (screen degrees, + clockwise) evenly along it."""
    pts = [P(p0)]
    h = math.atan2(d0[1], d0[0])
    step = length / n
    dh = math.radians(curl_deg) / n
    for _ in range(n):
        h += dh
        pts.append(pts[-1] + step * P(math.cos(h - dh / 2), math.sin(h - dh / 2)))
    return np.array(pts)


def _biggest(g, solid=True):
    """The largest polygon of g, its holes filled (a hand is one solid silhouette)."""
    ps = _polys_of(g)
    if not ps:
        return Polygon()
    pg = max(ps, key=lambda gg: gg.area)
    return Polygon(pg.exterior) if solid and pg.interiors else pg


def _open_line(pts, shape, *, start_on=True, inset=0.0, min_len=4.0):
    """An open interior line through ``pts`` kept inside ``shape`` (so it
    starts exactly on the outline when ``pts`` begins outside it). ``inset``
    > 0 keeps its free end that far inside the outline. → list of point
    arrays (MEDIUM line centrelines)."""
    ln = LineString(np.asarray(pts, float))
    z = shape.buffer(-inset) if inset > 0 else shape
    res = ln.intersection(z.buffer(-0.02))
    out = [np.asarray(g.coords) for g in _lines_of(res) if g.length >= min_len]
    if start_on and out:
        # only the piece that starts at the first contact with the outline
        p0 = Point(*np.asarray(pts, float)[0])
        out = [min(out, key=lambda q: p0.distance(Point(*q[0])))]
    return out


def _behind(T, d):
    """The half plane behind point T for a digit pointing d (toward T)."""
    T, d = P(T), _unit(d)
    n = np.array([-d[1], d[0]])
    return Polygon([tuple(T + n * BIG), tuple(T - n * BIG), tuple(T - n * BIG - d * BIG), tuple(T + n * BIG - d * BIG)])


def _webs(digits, cens, order=None):
    """Fill the wedge between neighbouring tapered digits behind their tips
    (so the notch between two fingertips is one clean V of their round tips,
    never a slit running back between the fingers). ``cens``: centrelines
    (root → tip). → region to union with the digits."""
    order = list(range(len(digits))) if order is None else order
    out = []
    for i, j in zip(order[:-1], order[1:]):
        parts = []
        for k in (i, j):
            c = np.asarray(cens[k], float)
            parts.append(digits[k].intersection(_behind(c[-1], c[-1] - c[-2])))
        out.append(shapely.union_all(parts).convex_hull)
    return shapely.union_all(out) if out else Polygon()


def _smooth_pts(pts, n=24):
    """Resample a polyline into a smooth curve (Chaikin twice) for drawing."""
    q = np.asarray(pts, float)
    for _ in range(2):
        if len(q) < 3:
            break
        a, b = q[:-1], q[1:]
        mid = np.empty((2 * len(a), 2))
        mid[0::2] = 0.75 * a + 0.25 * b
        mid[1::2] = 0.25 * a + 0.75 * b
        q = np.vstack([q[:1], mid, q[-1:]])
    return q


@dataclass
class Hand:
    """A built hand: ONE region (``hand``: palm, fingers and thumb merged)
    stacked in front of the scene by ``add_to``. ``thumb`` carries the thumb's
    own region for callers that use it as a blocker (``meta['merged']``: it
    is already part of ``hand`` and is never stacked). ``wrist``/``wrist_w``:
    where the arm meets the hand; ``wrist_dir``: the unit direction from the
    hand into the forearm there; ``stub``: px the hand runs on past ``wrist``,
    cut by the cuff in ``add_to``."""
    hand: Part
    thumb: Part
    wrist: np.ndarray
    wrist_w: float
    wrist_dir: np.ndarray | None = None
    stub: float = 0.0

    @property
    def shape(self):
        return self.hand.shape

    def silhouette(self, run=40.0, *, width=None):
        """The hand plus ``run`` px of forearm beyond the wrist (straight,
        ``width`` wide — default the wrist width), as ONE region: union it with
        a sleeve / arm region so the hand and arm share one outline."""
        if self.wrist_dir is None:
            return self.hand.shape
        W, u = P(self.wrist), _unit(self.wrist_dir)
        w = float(width) if width is not None else float(self.wrist_w)
        n = np.array([u[1], -u[0]])
        back = max(self.stub, 2.0)
        arm = Polygon([tuple(W - u * back + n * w / 2), tuple(W + u * run + n * w / 2),
                       tuple(W + u * run - n * w / 2), tuple(W - u * back - n * w / 2)])
        return _biggest(shapely.union(self.hand.shape, arm).buffer(0.6, quad_segs=8).buffer(-0.6, quad_segs=8))

    def with_sleeve(self, sleeve, *, color=None, cuff_line=True) -> Part:
        """Hand + sleeve as ONE Part with one continuous outline: ``sleeve`` is a
        Part (its fills keep its colour) or a region (filled ``color``). The
        hand's wrist runs into the sleeve; the colour edge between paper and
        sleeve is a MEDIUM line (``cuff_line``), the outer contour runs on
        from the sleeve into the hand without a corner or a T."""
        if isinstance(sleeve, Part):
            sr, sf, sl = sleeve.shape, sleeve.fills, sleeve.lines
        else:
            sr, sf, sl = R(sleeve), (fill(R(sleeve), color) if color else C.Frag()), C.Frag()
        hs = self.silhouette(run=self.wrist_w * 0.6)
        body = _biggest(shapely.union(hs, sr).buffer(1.0, quad_segs=8).buffer(-1.0, quad_segs=8))
        hand_r = self.hand.shape.difference(sr.buffer(-0.01)) if not self.wrist_dir is None else self.hand.shape
        hand_r = _biggest(hand_r)
        arm_r = body.difference(hand_r)
        fills = clip_in(sf, arm_r) if sf else C.Frag()
        lines = outline(body)
        lines += clip_in(sl.select(lambda m: m.role != "outline"), arm_r.buffer(0.01)) if sl else C.Frag()
        if cuff_line:
            edge = hand_r.boundary.intersection(body.buffer(-0.8))
            for g in _lines_of(shapely.line_merge(edge) if edge.geom_type == "MultiLineString" else edge):
                if g.length > 2.0:
                    lines += line(C.polyline_d(np.asarray(g.coords)), MEDIUM, role="cuffline")
        inner = self.hand.meta.get("inner", C.Frag())
        return Part(body, fills, lines + clip_in(inner, hand_r.buffer(0.5)),
                    {**self.hand.meta, "kind": self.hand.meta.get("kind", "") + "+sleeve", "hand_region": hand_r})

    def tucked(self, sc: "Scene | None" = None, cuff=None) -> Part:
        """The hand Part with its wrist run cut by the arm: ``cuff`` = item
        name(s) in ``sc`` or a region; default every item already in ``sc``
        whose name contains cuff / sleeve / forearm / arm / gauntlet /
        bracelet / wrist and that overlaps the run. When the wrist point lies
        on the arm's edge (a kit sleeve's cuff line), the wrist is first
        re-aimed along the forearm that edge implies and cut on that line, so
        the cuff edge is the one line at the junction."""
        hp = self.hand
        if self.stub <= 0 or self.wrist_dir is None or "inner" not in hp.meta:
            return hp
        W, u = P(self.wrist), _unit(self.wrist_dir)
        r0 = self.stub + self.wrist_w + 8.0
        disc = Point(*W).buffer(r0, quad_segs=16)
        regs, cuffs = [], []
        if cuff is None:
            if sc is not None:
                pw = Point(*W)
                for it in sc.items:
                    if (it.occ is not None and not it.occ.is_empty and it.occ.intersects(disc)
                            and any(w in it.name.lower() for w in ARM_WORDS)):
                        if it.occ.contains(pw) and it.occ.boundary.distance(pw) > 3.0:
                            continue                # a region the whole wrist sits on (an upper sleeve)
                        regs.append(it.occ)
                        if any(w in it.name.lower() for w in CUFF_WORDS):
                            cuffs.append(it.occ)
        elif isinstance(cuff, str) or (isinstance(cuff, (tuple, list)) and cuff and isinstance(cuff[0], str)):
            names = (cuff,) if isinstance(cuff, str) else tuple(cuff)
            regs = [it.occ for it in (sc.items if sc is not None else []) if it.name in names and it.occ is not None]
        else:
            regs = [R(cuff)]
        if not regs:
            return hp
        armr = shapely.union_all(regs)
        cuffr = shapely.union_all(cuffs) if cuffs else None
        us = _arm_dir(armr, W, u)
        if us is not None:
            if "rebuild" in hp.meta and float(np.dot(us, u)) < math.cos(math.radians(3.0)):
                hp = hp.meta["rebuild"](us)
            u = us
        n = np.array([u[1], -u[0]])
        zone = Polygon([tuple(W - 4.0 * u + n * r0), tuple(W - 4.0 * u - n * r0),
                        tuple(W + u * r0 - n * r0), tuple(W + u * r0 + n * r0)])
        run = hp.shape.intersection(zone)
        if run.is_empty:
            return hp
        # the hand runs over the sleeve's lip above a cuff (the kit cuff's top edge sags
        # 2.5 px below the sleeve's end) and stops at the cuff: one line at the junction
        lip = 3.6 if (cuffr is not None and us is not None) else 0.0
        lipz = Polygon([tuple(W - 0.2 * u + n * r0), tuple(W - 0.2 * u - n * r0),
                        tuple(W + lip * u - n * r0), tuple(W + lip * u + n * r0)]) if lip else Polygon()
        if cuffr is not None:
            cut = run.intersection(cuffr)
            deep = max(lip, self.stub - 1.0)
            cut = cut.union(run.intersection(armr.difference(cuffr)).intersection(
                halfplane(W + u * deep, W + u * deep + n, side=-1)))
            cut = cut.union(run.intersection(halfplane(W + u * deep, W + u * deep + n, side=-1)))
        else:
            cut = run.intersection(armr.difference(lipz))
            if us is not None:                      # everything past the cuff line goes, covered or not
                cut = cut.union(run.intersection(halfplane(W + u * lip, W + u * lip + n, side=-1)))
        if cut.area < 0.5:
            return hp
        shape = hp.shape.difference(cut)
        # drop the hairline spikes a cut along a nearly coincident cuff edge can leave
        shape = shape.buffer(-0.4, join_style=2, mitre_limit=4.0).buffer(0.4, join_style=2, mitre_limit=4.0)
        polys = _polys_of(shape)
        if not polys:
            return hp
        shape = max(polys, key=lambda g: g.area)
        beyond = Polygon([tuple(W + u * (lip + 1.5) + n * r0), tuple(W + u * (lip + 1.5) - n * r0),
                          tuple(W + u * r0 - n * r0), tuple(W + u * r0 + n * r0)])
        left = shape.intersection(beyond).difference(armr).area
        if left > 6.0:
            _hand_warn(f"hand at ({W[0]:.0f}, {W[1]:.0f}): {left:.0f} px² of the wrist shows past the cuff "
                       "(hand wider than the cuff opening, or the cuff not at the wrist)")
        inner = clip_in(hp.meta["inner"], shape.buffer(-0.5))
        return Part(shape, hp.fills, outline(shape) + inner,
                    {**hp.meta, "inner": inner, "tucked": True, "cutline": (W, u, max(lip, self.stub - 1.0))})

    def add_to(self, sc: "Scene", name: str, *, halo=HALO, halo_skip=(), halo_only=None, cuff=None):
        """Stack the hand in front (wrist tucked into the arm, see ``tucked``)
        as ONE item. With ``halo=0`` (the v3 default for a held attribute: the
        shaft runs under the fingers, sharing their contour) a hand closed on a
        HALOED attribute still carries that attribute's paper channel round
        its fingertips and heel, so the lobes end in paper."""
        hp = self.tucked(sc, cuff)
        if "inner" in hp.meta and not halo:
            tips = hp.meta.get("tipzone")
            heelz = hp.meta.get("heelzone")
            arms = tuple(it.name for it in sc.items if any(w in it.name.lower() for w in ARM_WORDS))
            for it in list(sc.items) if tips is not None else []:
                if it.halo > LINE_TUCK and it.occ is not None and not it.occ.is_empty and it.occ.intersects(hp.shape):
                    zone = hp.shape.intersection(it.occ.buffer(it.halo + MEDIUM / 2 + 3.5, quad_segs=12))
                    zone = zone.intersection(tips)
                    if zone.area > 1.0:
                        hz = zone.buffer(it.halo + MEDIUM / 2, quad_segs=12).intersection(
                            it.occ.buffer(it.halo + MEDIUM / 2 + 5.0, quad_segs=12))
                        sc.add(f"{name}~{it.name}", C.Frag(), zone, sil=False, halo=it.halo,
                               halo_skip=it.halo_skip, halo_only=it.halo_only, halo_zone=hz.union(zone))
                    if heelz is None:
                        continue
                    A = it.occ.buffer(it.halo + MEDIUM / 2, quad_segs=12)
                    armz = [a.occ for a in sc.items if a.name in arms and a.occ is not None]
                    arm_r = shapely.union_all(armz) if armz else Polygon()
                    near_arm = arm_r.intersection(hp.shape.buffer(3.0 * HEEL_CLOSE, quad_segs=8))
                    both = shapely.union_all([A, hp.shape, near_arm])
                    gap = both.buffer(HEEL_CLOSE, quad_segs=12).buffer(-HEEL_CLOSE, quad_segs=12).difference(both)
                    gap = gap.intersection(heelz)
                    if not arm_r.is_empty:
                        gap = gap.difference(arm_r)
                    cl = hp.meta.get("cutline")
                    if cl is not None:
                        Wc, uc, dp = cl
                        nc = np.array([uc[1], -uc[0]])
                        d2 = dp + 1.5 * HEEL_CLOSE
                        gap = gap.intersection(halfplane(Wc + uc * d2, Wc + uc * d2 + nc, side=+1))
                    gap = shapely.union_all([g for g in _polys_of(gap) if g.area > 2.0
                                             and g.distance(A) < 0.6 and g.distance(hp.shape) < 0.6]) \
                        if not gap.is_empty else gap
                    if gap.is_empty or gap.area < 2.0:
                        continue
                    occ = hp.shape.intersection(gap.buffer(2.0, quad_segs=8))
                    if occ.is_empty:
                        continue
                    sc.add(f"{name}~heel~{it.name}", C.Frag(), occ, sil=False, halo=it.halo,
                           halo_skip=tuple(it.halo_skip) + arms, halo_only=it.halo_only,
                           halo_zone=gap.union(occ))
        if halo:
            sc.add(name, hp.frag, hp.shape, halo=halo, halo_skip=halo_skip, halo_only=halo_only)
        else:
            # no paper channel, but the lines behind end UNDER the hand's outline stroke: a
            # line meeting the hand stops where its round cap reaches the stroke's inner edge,
            # so no cap shows as a bead inside the hand (fills behind are unchanged: their
            # trap stays under the outline)
            sc.add(name, hp.frag, hp.shape, halo=LINE_TUCK, halo_skip=halo_skip, halo_only=halo_only,
                   halo_zone=hp.shape.buffer(-MEDIUM / 2, quad_segs=8))
        th = self.thumb
        if th.shape is not None and not th.shape.is_empty and not th.meta.get("merged"):
            sc.add(name + "-thumb", th.frag, th.shape, halo=halo,
                   halo_skip=tuple(halo_skip) + (name,), halo_only=halo_only)
        return sc


def _xf(g, M):
    """Apply the rigid 2×3 matrix M (a, b, c, d, e, f) to shapely g."""
    return shapely.affinity.affine_transform(g, M)


def _rigid(origin, deg, mirror_x=False):
    """Local → screen: optional mirror about local x = 0, rotate by ``deg``
    (screen, clockwise), translate to ``origin``. Returns (M for shapely,
    M for Frag.transformed)."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    mx = -1.0 if mirror_x else 1.0
    A, Bm, Cm, Dm = c * mx, -s, s * mx, c
    ox, oy = origin
    return (A, Bm, Cm, Dm, ox, oy), (A, Cm, Bm, Dm, ox, oy)


def _scallops(p_from, p_to, n, sag):
    """n scallops from p_from to p_to bulging ``sag`` to the screen-left. → d
    (continuing a path; no M)."""
    pts = [p_from + (p_to - p_from) * k / n for k in range(n + 1)]
    return "".join(arc_sag(pa, pb, sag, move=False) for pa, pb in zip(pts[:-1], pts[1:])), pts


def _junction_smooth(shape, keep_out, r=2.6):
    """Fill the concave notches of ``shape`` (closing, radius r) except inside
    ``keep_out`` (fingertip notches stay crisp)."""
    closed = shape.buffer(r, quad_segs=10).buffer(-r, quad_segs=10)
    return shape.union(closed.difference(keep_out))


def _lines_frag(polys, role, w=MEDIUM):
    f = C.Frag()
    for pts in polys:
        if len(pts) >= 2:
            f += line(C.polyline_d(pts), w, role=role)
    return f


# -----------------------------------------------------------------------------
# grip: a fist closed round a cylinder (and the pinch)
# -----------------------------------------------------------------------------
def _trim_start(pts, shape, d=None, step=0.2):
    """Cut the start of polyline ``pts`` (which begins ON ``shape``'s
    outline, in a notch) until it is ``d`` px from the outline: the line then
    leaves the notch where the two outline strokes' inner edges meet, so it
    continues the outline's V and its round cap never sits in the notch as a
    dark bead. → point array or None."""
    d = 0.42 * MEDIUM if d is None else d
    ln = LineString(np.asarray(pts, float))
    L = ln.length
    b = shape.boundary
    s = 0.0
    while s < L and b.distance(ln.interpolate(s)) < d:
        s += step
    if s > L - 2.0:
        return None
    return np.asarray(shapely.ops.substring(ln, s, L).coords)


def _notch_lines(pts, shape, *, min_len=4.0):
    """An open interior line from a notch of ``shape``: ``pts`` start outside
    it (beyond the notch) and run inward; clipped to the shape and trimmed
    off the notch (``_trim_start``). → list of point arrays."""
    out = []
    for q in _open_line(pts, shape, min_len=min_len):
        q = _trim_start(q, shape)
        if q is not None and LineString(q).length >= min_len:
            out.append(q)
    return out


def _clean(g, r_open=1.0, r_close=0.7):
    """One smooth solid silhouette: an opening (drops spurs and hairline
    nicks' rims) then a small closing (fills nicks), holes filled."""
    g = _biggest(g)
    g = g.buffer(-r_open, quad_segs=8).buffer(r_open, quad_segs=8)
    g = g.buffer(r_close, quad_segs=8).buffer(-r_close, quad_segs=8)
    return _biggest(g)


def _grip_frame(at, axis_deg, shaft_w, back, h, size, reach, knuckle, thumb="over", pinch=False):
    """The local frame of a grip (shaft vertical through the origin, its UP
    end toward −y, knuckles toward +x; mirrored for ``back`` = −1)."""
    hb = max(HAND_K * float(size), FIST_H_MIN) if size is not None else max(FIST_H_K * float(h), FIST_H_MIN)
    a = shaft_w / 2.0
    t_up = GRIP_THUMB["rise"] * hb if thumb == "over" else 0.0
    if pinch:                                      # the index finger crosses the stem at ``at``
        y0 = -0.5 * GRIP_FH[0] * hb
        ytop = y0 - t_up
    else:
        ytop = -(hb + t_up) / 2.0
        y0 = ytop + t_up
    y1 = y0 + hb
    yc = (y0 + y1) / 2
    tip_out = min(max(float(reach), 2.5), FIST_TIP_OUT) if not pinch else PINCH_REACH * hb
    x_tip = -a - tip_out
    Lf = max(FIST_LEN_K * hb, 2 * a + tip_out + max(float(knuckle), 12.0))
    x_kn = x_tip + Lf
    rot = axis_deg + 90.0
    return dict(hb=hb, a=a, t_up=t_up, ytop=ytop, y0=y0, y1=y1, yc=yc, tip_out=tip_out, x_tip=x_tip,
                Lf=Lf, x_kn=x_kn, rot=rot, mir=back < 0)


def fist(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, wrist=None, wrist_w=None, h=34.0, size=None,
         reach=7.0, knuckle=11.0, thumb_r=5.6, hand=None, view=None, arm=None, stub=HAND_STUB,
         hidden_wrist=False, thumb="over", grip="power") -> Hand:
    """A hand closed round a cylinder (sceptre, staff, rod, key, paddle, fiddle
    neck, trumpet, stem, rope) whose axis passes through ``at`` pointing
    ``axis_deg`` (screen degrees of the shaft's UP end; −90 = vertical; any
    angle, the hand turns with the shaft). ONE silhouette, five digits:

    * the FOUR FINGERS wrap across the front of the shaft (the shaft shows
      above and below, its contour running under the fingers' — no halo):
      tapered digits with round tips curling round the shaft's far edge (≤ 5
      px past it, the middle finger furthest, the little finger shortest,
      narrowest and lifted a little so the underside rounds up into its
      tip); three open finger lines from the notches between the tips,
      toward the knuckles at staggered lengths;
    * the THUMB is the fist's top edge: it lies along the index finger from
      the back of the hand, its top sloping down from the back-of-hand
      contour to a small round tip at the shaft's near edge (no step, no
      overhang); its only line is its underside, open, from the tip toward
      the knuckle line (short in the back view, to the knuckles in the palm
      view). ``thumb='behind'``: the top of the fist is the index finger and
      only the thumb's tip shows, a small lobe beside the index fingertip
      past the shaft's far edge;
    * the BACK OF THE HAND is the rounded knuckle end; the WRIST tapers out
      of it to ``wrist`` (``fist_wrist`` gives a good point) along the
      forearm (``arm``; ``Hand.add_to`` re-aims it along the sleeve it finds)
      and runs ``stub`` px on into the sleeve; the HEEL leaves the little
      finger in a smooth curve 7.3 px off the shaft.

    Size: ``size`` = the hand length (``hand_size(face)``; the fist is
    ``HAND_K × size`` tall), else the old ``h`` (fist ≈ max(0.92 h, 32)).
    ``grip='pinch'``: a light hold of a thin object (see ``pinch``).

    Chirality: the construction is a back-of-hand view — a LEFT hand when
    ``back`` = +1 (knuckles toward the wrist side), a RIGHT hand when −1.
    ``hand='L'|'R'`` (the figure's hand) that does not match is drawn as the
    PALM view (``view='palm'``): the finger lines stop at the shaft's near
    edge (the curled fingertips) and the thumb's underside runs to the
    knuckles. ``HandWarning``s (also in ``HAND_LOG``) flag wrists inside the
    knuckle line, bent > 65°, far from the knuckles (``hidden_wrist``
    silences them). Returns a Hand."""
    pinch_ = grip == "pinch"
    F = _grip_frame(at, axis_deg, shaft_w, back, h, size, reach, knuckle, thumb, pinch_)
    hb, a, y0, y1, yc, ytop = F["hb"], F["a"], F["y0"], F["y1"], F["yc"], F["ytop"]
    Lf, x_kn, tip_out, rot, mir, t_up = F["Lf"], F["x_kn"], F["tip_out"], F["rot"], F["mir"], F["t_up"]
    M, Mf = _rigid(at, rot, mirror_x=mir)
    dorsal = "L" if back > 0 else "R"
    if view is None:
        view = "back" if (hand is None or str(hand).upper()[:1] == dorsal) else "palm"
    where = f"fist at ({float(at[0]):.0f}, {float(at[1]):.0f})"

    # ---- the four fingers: tapered digits, round tips, a slight fan -----------------------
    fh = [k * hb for k in GRIP_FH]
    tops = [y0 + sum(fh[:k]) for k in range(4)]
    x_root = x_kn - 0.30 * hb
    fingers, tipc, tipr, cens, fronts = [], [], [], [], []
    for k in range(4):
        yck = tops[k] + fh[k] / 2
        r_t = GRIP_TIP_R * fh[k]
        if pinch_ and k > 0:                        # curled into the palm, stepped back off the stem
            front = a + PARALLEL_MIN + 0.8 + (k - 1) * PINCH_STEP * hb
            tilt = (0.0, 5.0, 9.0, 14.0)[k]
        elif pinch_:
            front = -a - PINCH_REACH * hb
            tilt = 0.0
        else:
            front = -a - tip_out * GRIP_OUT[k]
            tilt = GRIP_TILT[k]
        root = P(max(x_root, front + 2 * r_t + 4.0), yck)
        Lk = float(root[0] - (front + r_t))
        tr = math.radians(tilt)
        tip = root + Lk * P(-math.cos(tr), -math.sin(tr))
        cen = _qbez(tip, (tip + root) / 2 + P(0.0, -0.035 * Lk), root, 12)
        fingers.append(_digit(cen, np.linspace(2 * r_t, fh[k] + 1.0, len(cen))))
        cens.append(cen)
        tipc.append(tip)
        tipr.append(r_t)
        fronts.append(front)
    block = shapely.union_all(fingers + [_webs(fingers, [c[::-1] for c in cens])])
    # the knuckle end: the fingers' roots merge into one rounded ridge
    ridge = _digit(np.array([[x_kn - 0.32 * hb, y0 + 0.30 * fh[0]], [x_kn - 0.32 * hb, y1 - 0.30 * fh[3]]]),
                   0.62 * hb)
    x_ridge = (max(fronts[1:]) + 2 * max(tipr)) if pinch_ else -a + 2.0
    ridge = ridge.intersection(shapely.box(x_ridge, y0 - 0.5, BIG, y1 + 0.5))
    # ... and never below the little finger's lower edge (the underside rounds up into its tip)
    d3 = _unit(cens[3][-1] - cens[3][0])
    n3 = P(-d3[1], d3[0]) if d3[0] > 0 else P(d3[1], -d3[0])
    if n3[1] < 0:
        n3 = -n3
    lo3 = cens[3][-1] + n3 * (fh[3] + 1.0) / 2
    hp3 = halfplane(lo3, lo3 + d3, side=+1)
    if not hp3.contains(Point(*cens[3][-1])):
        hp3 = halfplane(lo3, lo3 + d3, side=-1)
    ridge = ridge.intersection(hp3) if not ridge.is_empty else ridge
    tipzone_l = shapely.union_all([Point(*q).buffer(r + 2.4, quad_segs=12) for q, r in zip(tipc, tipr)])
    block = _biggest(_junction_smooth(block.union(ridge), tipzone_l, r=2.2))
    # pinch: ground between the stem and the curled fingers' tips (nothing fills it)
    carve = Polygon()
    if pinch_:
        carve = shapely.union_all([shapely.box(-BIG, tops[k], fronts[k] + tipr[k],
                                               BIG if k == 3 else tops[k] + fh[k] + 0.6) for k in (1, 2, 3)])
        carve = carve.difference(shapely.union_all(fingers[1:])).difference(fingers[0].buffer(0.01))

    # ---- the thumb ---------------------------------------------------------------------
    th = GRIP_THUMB
    rt, rr = th["tip"] * hb, th["root"] * hb
    band = thumb == "over" and (pinch_ or view == "palm")
    if thumb == "over":
        if band:
            # palm view / pinch: the thumb wraps round the front of the shaft as the fist's top
            # band, its round tip in the column of fingertips beside the index tip (the notch
            # between them is where its one line starts)
            rt = 0.5 * t_up
            x_tf = (-a - 0.5) if pinch_ else (-a - 0.45 * tip_out * GRIP_OUT[0])
            Tc = P(x_tf + rt, y0 - rt + 0.8)
        else:
            # back view: a wedge along the top of the index finger, its top flush with the
            # index top at the shaft's near edge and rising to the back of the hand
            x_tf = a + 5.5                          # clear of the shaft's edge where it meets the top
            Tc = P(x_tf + rt, y0 + rt - 0.4)
        Rc = P(x_kn + (0.0 if band else 0.08) * hb, y0 - t_up + rr)
        cen_t = _qbez(Tc, (Tc + Rc) / 2 + P(0.0, -0.03 * hb), Rc, 16)
        w_t = np.linspace(2 * rt, 2 * rr, len(cen_t))
        thumb_r = _digit(cen_t, w_t)
        # its underside (for the crease)
        nt = np.array([_unit(cen_t[min(i + 1, len(cen_t) - 1)] - cen_t[max(i - 1, 0)]) for i in range(len(cen_t))])
        nt = np.column_stack([-nt[:, 1], nt[:, 0]])
        nt[nt[:, 1] < 0] *= -1
        under_t = cen_t + nt * (w_t[:, None] / 2)
    else:                                          # 'behind': only its tip, beside the index tip
        rtb = 0.12 * hb
        Tc = P(tipc[0][0] - tipr[0] - 0.15 * rtb, tipc[0][1] + 0.12 * fh[0])
        thumb_r = _digit(np.array([P(-a + 1.0, Tc[1]), Tc]), 2 * rtb)

    # ---- the wrist -------------------------------------------------------------------
    W = P(x_kn, yc) + hb * P(0.55, 0.62) if wrist is None else _to_local(wrist, at, rot, mir)
    Bs = P(x_kn - 0.20 * hb, yc + 0.03 * hb)       # the back-of-hand mass the wrist grows from
    chord = W - Bs
    off = math.degrees(math.atan2(chord[1], chord[0]))
    dist = float(np.hypot(*(W - P(x_kn, yc))))
    if W[0] < x_kn - 4.0 and not hidden_wrist:
        _hand_warn(f"{where}: wrist {x_kn - W[0]:.0f} px inside the knuckle line (move it out along the hand axis)")
    if abs(off) > 65.0 and not hidden_wrist:
        _hand_warn(f"{where}: wrist bent {off:.0f}° off the hand axis (≤ 65° reads)")
    if dist > 1.3 * hb and not hidden_wrist:
        _hand_warn(f"{where}: wrist {dist:.0f} px from the knuckles (> 1.3 × {hb:.0f}): a long bare wrist; "
                   "move the cuff up the forearm")
    x_min = a + PARALLEL_MIN                       # the heel's floor below the fist
    hK = 0.46 * hb                                 # half-breadth of the back at the knuckles

    def build(u):
        """hand region and interior lines (local) for a forearm direction u."""
        u = _unit(u)
        n_th = np.array([u[1], -u[0]])             # the thumb side of the wrist
        hw = min(float(wrist_w) if wrist_w is not None else BIG, 0.68 * hb) / 2.0
        hw_in = hw
        Wb = W - n_th * hw
        x_floor = x_min + 0.16 * hb
        if Wb[0] < x_floor and Wb[1] > y1 and n_th[0] > 1e-3:
            hw_in = min(hw, max((W[0] - x_floor) / n_th[0], 0.55 * hw))
            Wb = W - n_th * hw_in
            if Wb[0] < x_min + 0.5:
                hw_in = max((W[0] - x_min - 0.5) / n_th[0], 0.25 * hw)
                Wb = W - n_th * hw_in
        # the wrist: one tapered sweep from the knuckle mass, arriving along the forearm,
        # with a slight waist just before the cuff
        Lw = float(np.hypot(*(W - Bs)))
        C_ = W - u * 0.45 * Lw
        nseg = max(10, int(Lw / 2.5))
        tt = np.linspace(0.0, 1.0, nseg + 1)
        cen_ = list(_qbez(Bs, C_, W, nseg + 1)) + [W + u * stub * 0.5, W + u * stub]
        prof = [t * t * (3 - 2 * t) for t in tt]
        wid = [hK + (hw - hK) * p for p in prof] + [hw, hw]
        shift = [n_th * (hw - hw_in) / 2 * p for p in prof] + [n_th * (hw - hw_in) / 2] * 2
        wid = [w_ - (hw - hw_in) / 2 * p for w_, p in zip(wid, prof + [1.0, 1.0])]
        ds = [Point(*(q + s_)).buffer(max(rw, 0.5), quad_segs=16) for q, s_, rw in zip(cen_, shift, wid)]
        neck = shapely.union_all([shapely.union(d0, d1).convex_hull for d0, d1 in zip(ds[:-1], ds[1:])])
        neck = neck.intersection(halfplane(W + u * stub, W + u * stub + n_th, side=+1))
        if pinch_:
            neck = neck.difference(carve)
        # the heel: a smooth curve from the little finger into the wrist, off the shaft
        # the underside: ONE curve from the little fingertip's lowest point into the wrist
        P3 = tipc[3] + n3 * tipr[3]
        H = _edge(P3, d3, Wb, u, 24)
        clear = Polygon()
        if u[1] > -0.3:
            heel = Polygon([tuple(q) for q in list(H) + [W, Bs, tipc[3]]]).buffer(0)
            neck = neck.union(heel)
            far = P3 - d3 * 400.0
            clear = Polygon([tuple(far + n3 * 0.3), tuple(P3 + n3 * 0.3)] + [tuple(q) for q in H[1:]]
                            + [tuple(Wb + u * 400.0), tuple(Wb + u * 400.0 + n3 * 400.0),
                               tuple(far + n3 * 400.0)]).buffer(0)
            trimmed = neck.difference(clear)
            if not trimmed.is_empty:
                neck = _biggest(trimmed)
        # the thenar: the thumb's root flows into the back of the hand (no notch, no line)
        parts = [block, neck]
        if thumb == "over":
            # (on along the wrist's top so the thumb's knuckle rounds into it, no dip)
            Qw = _qbez(Bs, C_, W, 11)[2]
            rq = hK + (hw - hK) * 0.10
            root_join = shapely.union_all([Point(*Rc).buffer(rr, quad_segs=16),
                                           Point(*Bs).buffer(hK, quad_segs=16),
                                           Point(*Qw).buffer(rq, quad_segs=16)]).convex_hull
            root_join = root_join.intersection(shapely.box(x_kn - 0.36 * Lf, -BIG, BIG, BIG))
            parts += [thumb_r, root_join]
        else:
            parts += [thumb_r]
        hand_ = shapely.union_all(parts)
        floor = clear
        if not floor.is_empty:
            hand_ = _biggest(hand_.difference(floor))
        if pinch_:
            hand_ = _biggest(hand_.difference(carve))
        tz = tipzone_l.union(Point(*Tc).buffer((rt if thumb == "over" else 0.115 * hb) + 2.6, quad_segs=12))
        keep_out = tz.union(clear.buffer(0.3)).union(floor).union(carve.buffer(2.0))
        hand_ = _junction_smooth(hand_, keep_out, r=0.20 * hb)
        hand_ = _clean(hand_, r_open=2.0)

        # ---- interior lines: open, from the notches -------------------------------------
        inner = C.Frag()
        lines_ = []
        # finger separations k-1 | k: from the notch between the tips toward the knuckles
        for k in (1, 2, 3):
            ca, cb = cens[k - 1], cens[k]
            wa, wb = fh[k - 1], fh[k]
            mid = (ca * wb + cb * wa) / (wa + wb)          # the seam between the two fingers
            if pinch_:
                # from the notch where the curled tip meets the finger above, along its top edge
                dk = _unit(cb[-1] - cb[0])
                nk = P(dk[1], -dk[0]) if dk[0] > 0 else P(-dk[1], dk[0])
                if nk[1] > 0:
                    nk = -nk
                p0 = cb[0] + nk * tipr[k] - dk * 6.0
                xe = x_kn - (0.10 if k == 1 else 0.04) * Lf
                if view == "palm":
                    xe = fronts[k] + 2 * tipr[k] + 4.0
                p1 = cb[-1] + nk * (fh[k] + 1.0) / 2
                p1 = p0 + (p1 - p0) * max(0.2, (xe - p0[0]) / max(p1[0] - p0[0], 1e-6))
                pts = np.linspace(p0, p1, 16)
            else:
                ext = mid[0] + _unit(mid[0] - mid[2]) * 8.0
                mid = np.vstack([mid, mid[-1] + _unit(mid[-1] - mid[-3]) * Lf])
                xe = x_kn - GRIP_LINE[k - 1] * Lf if view == "back" else a + 1.5 + (k == 2) * 2.0
                if k == 1 and thumb == "over" and not band:
                    xe = min(xe, x_tf - 3.5)          # clear of the thumb's crease
                cut = LineString(np.vstack([ext, mid])).intersection(shapely.box(-BIG, -BIG, xe, BIG))
                gs = [g for g in _lines_of(cut) if g.length > 1.0]
                if not gs:
                    continue
                pts = np.asarray(max(gs, key=lambda g: g.length).coords)
            lines_ += _notch_lines(pts, hand_)
        inner += _lines_frag(lines_, "finger")
        # the thumb's underside: from its tip toward the knuckle line, open
        if thumb == "over":
            body = block.union(neck)
            span = x_kn - 0.02 * hb - Tc[0]            # never past the knuckle line
            stop = Tc[0] + (th["crease_back"] if view == "back" else th["crease_palm"]) * span
            if band:
                # from the notch between its tip and the index tip, along its underside
                for pts in _crease(thumb_r, body, keep=shapely.box(-BIG, -BIG, stop, BIG), min_len=4.0):
                    if np.hypot(*(pts[-1] - Tc)) < np.hypot(*(pts[0] - Tc)):
                        pts = pts[::-1]
                    q = _trim_start(pts, hand_)
                    if q is not None and LineString(q).length > 4.0:
                        inner += line(C.polyline_d(q), MEDIUM, role="thumb")
            else:
                # a branch off the top contour at the tip, down and back along its underside
                y_end = float(np.interp(stop, under_t[:, 0], under_t[:, 1]))
                p0, p1 = P(x_tf - 1.0, y0 - 1.6), P(stop, y_end)
                ctrl = P(x_tf + 3.0 * rt, y_end + 0.4)
                for q in _notch_lines(_qbez(p0, ctrl, p1, 24), hand_):
                    inner += line(C.polyline_d(q), MEDIUM, role="thumb")
        # ('behind': the notches above and below its tip lobe are the only separation)
        return hand_, inner, 2 * hw

    drawn = dorsal if view == "back" else ("R" if dorsal == "L" else "L")
    tipzone = _xf(shapely.box(-BIG, -BIG, -a + 1.0, BIG), M)       # the fingertip side of the shaft
    heelzone = _xf(shapely.box(a - 1.0, y1 - 1.0, BIG, BIG), M)     # below the fingers, knuckle side
    base_meta = {"kind": "pinch" if pinch_ else "fist", "hand": drawn, "view": view, "block_h": hb,
                 "block_len": Lf, "wrist_off_deg": off, "size": hb / HAND_K}
    Ws = _xf(Point(*W), M)
    Ws = P(Ws.x, Ws.y)

    def place(u_local):
        hl, il, ww = build(u_local)
        hs, is_ = _xf(hl, M), il.transformed(Mf)
        meta = {**base_meta, "inner": is_, "rebuild": rebuild, "tipzone": tipzone, "heelzone": heelzone}
        return Part(hs, C.Frag(), outline(hs) + is_, meta), ww, _unit(_vec(M, _unit(u_local)))

    def _loc_vec(v):
        return _to_local(P(at) + P(v), at, rot, mir)

    def rebuild(u_screen):
        """the same hand with its wrist arriving along screen direction u_screen."""
        return place(_loc_vec(u_screen))[0]

    u0 = _loc_vec(arm) if arm is not None else chord
    part, ww, us = place(u0)
    return Hand(part, Part(_xf(thumb_r, M), C.Frag(), C.Frag(), {"merged": True}), Ws, ww, us, float(stub))


def pinch(at, axis_deg=-90.0, *, stem_w=5.0, back=+1, wrist=None, size=None, h=34.0, **kw) -> Hand:
    """A small object held between the thumb and the index finger — a flower
    stem, a key, a chalice stem — ``at`` is where it passes between their
    tips, ``axis_deg`` its up direction (tested from −45 to −135: an object
    held up and away; a lantern ring or bail is a GRIP, ``fist`` with axis
    180, the fingers hooked over the bar).
    The index finger crosses the object and curls round it; the thumb lies
    along the index finger, its tip pressing the object; the other three
    fingers are curled into the palm, each stepped further back, their round
    tips clear of the object, so the object runs on below the index finger
    over open ground. Same options as ``fist`` (``wrist``, ``hand``,
    ``view``, ``arm`` …)."""
    return fist(at, axis_deg, shaft_w=stem_w, back=back, wrist=wrist, size=size, h=h, grip="pinch",
                **{"reach": 4.0, **kw})


def clear_of_hand(holes, hand, *, gap=GAP_MARK):
    """Knockouts (paper bubbles, drops …) near a hand: each hole is kept only
    when it lies hidden under the hand (within its outline's half-width) or
    stands ≥ ``gap`` clear of the outline — a hole ON the contour reads as a
    stray paper crescent. ``holes``: a region (one polygon per hole) or a
    fill region with interior rings; ``hand``: a region (``Hand.hand.shape``).
    → the same kind of region with the offending holes filled back."""
    holes, hand = R(holes), R(hand)
    under = hand.buffer(MEDIUM / 2 - 0.3, quad_segs=8)

    def ok(g):
        return under.contains(g) or g.distance(hand) >= MEDIUM / 2 + gap

    if any(len(pg.interiors) for pg in _polys_of(holes)):
        return shapely.union_all([Polygon(pg.exterior, [r for r in pg.interiors if ok(Polygon(r))])
                                  for pg in _polys_of(holes)])
    kept = [g for g in _polys_of(holes) if ok(g)]
    return shapely.union_all(kept) if kept else Polygon()


def fist_geom(at, axis_deg=-90.0, *, shaft_w=22.0, back=+1, h=34.0, size=None, reach=7.0, knuckle=11.0,
              thumb="over", grip="power"):
    """The frame facts of ``fist(...)`` with these arguments (no drawing):
    fist height ``hb``, length ``Lf``, the knuckle point ``kn`` and the
    back-of-hand mass ``Bs`` (screen points), the hand-axis unit ``axis``
    (from the fingertips toward the knuckles) and ``down`` (along the shaft
    toward its lower end). For placing wrists and cuffs."""
    F = _grip_frame(at, axis_deg, shaft_w, back, h, size, reach, knuckle, thumb, grip == "pinch")
    M, _ = _rigid(at, F["rot"], mirror_x=F["mir"])
    hb, x_kn, yc = F["hb"], F["x_kn"], F["yc"]

    def S(q):
        g = _xf(Point(*q), M)
        return P(g.x, g.y)
    o = S(P(0.0, 0.0))
    return {"hb": hb, "Lf": F["Lf"], "kn": S(P(x_kn, yc)), "Bs": S(P(x_kn - 0.20 * hb, yc + 0.03 * hb)),
            "axis": _unit(S(P(1.0, 0.0)) - o), "down": _unit(S(P(0.0, 1.0)) - o), "y1": F["y1"], "a": F["a"]}


def fist_wrist(at, axis_deg=-90.0, *, bend=40.0, dist=0.85, shaft_w=22.0, back=+1, h=34.0, size=None, reach=7.0,
               knuckle=11.0, grip="power"):
    """Where a fist's wrist reads best: ``dist`` × the fist height from the
    back-of-hand mass, ``bend``° off the hand axis toward the shaft's lower
    end (0 = straight out along the knuckles; ``fist`` warns past 65°).
    → screen point."""
    g = fist_geom(at, axis_deg, shaft_w=shaft_w, back=back, h=h, size=size, reach=reach, knuckle=knuckle, grip=grip)
    b = math.radians(bend)
    return g["Bs"] + g["hb"] * dist * (math.cos(b) * g["axis"] + math.sin(b) * g["down"])


# -----------------------------------------------------------------------------
# cup: an orb held from below
# -----------------------------------------------------------------------------
CUP_OVER = (0.20, 0.27, 0.23, 0.12)      # each fingertip's reach up over the sphere's lower rim (× r)
CUP_FW = (1.02, 1.04, 1.0, 0.88)         # finger width relative to a quarter of the knuckle breadth
CUP_KN = 0.30                            # knuckle row: this × finger width below the sphere's bottom


def _orb_low_latitude(r):
    """The kit ``orb``'s lowest ripple latitude as y(x) (sphere-local), or None."""
    y_end = -r + 5.5 + 8.2 + 10.6 + 13.8
    if y_end >= r - 2.0:
        return None
    sag = 2.6 + 0.10 * (y_end + r)
    dx = math.sqrt(max(r * r - y_end * y_end, 1.0))
    return lambda x: y_end + sag * max(0.0, 1.0 - (x / dx) ** 2)


def cup(c, r, *, side=-1, wrist=None, wrist_w=None, grip=None, fw=None, thumb_w=None,
        thumb_from=72.0, thumb_to=24.0, knuckle=3.0, converge=0.80, stub=HAND_STUB, size=None,
        spread=1.10, clear_y="orb") -> Hand:
    """A hand holding a sphere (orb, cone, bowl, lantern) from below: ONE
    silhouette, the palm UNDER the sphere and only the fingertips over it.

    * the palm sits below the sphere, its knuckle row just under the
      sphere's bottom; it tapers into the wrist (the little-finger side
      swelling a little) and runs ``stub`` px on into the sleeve;
    * four short fingers curl up the sphere's near lower rim: tapered, round
      tips on an arc following the rim (only the tips overlap the sphere,
      well below its equator), the middle finger highest, the little finger
      short and narrow, fanning a little (``spread``: tip spacing / knuckle
      spacing); three open lines from the notches between the tips stop at
      the knuckle row;
    * the THUMB is a short lobe from the thumb-side edge of the palm, its
      round tip resting on the sphere's rim ``thumb_to`` + 8° below the
      equator (a short lobe, never a hook along the rim); the web between it and the index
      finger is a wide, smooth V of the outline.

    ``side`` −1: thumb toward +x (screen right), +1: toward −x. The hand's
    scale follows ``size`` (``hand_size(face)``) when given, else ``fw`` or
    0.34 r per finger. ``grip`` (default 0.36) scales how far the tips reach
    over the rim. ``clear_y``: a sphere-local y (or a function of x) the
    fingertips stay ≥ 6.3 px below — by default the kit ``orb``'s lowest
    ripple latitude, so the ripples run whole above the fingers and are
    never chopped into dashes between the tips (None: no limit). The best
    wrist is ≈ 1.6–1.9 r below the sphere's centre, a little toward the
    little-finger side. Returns a Hand."""
    c = P(c)
    if size is not None:
        fw = HAND_K * float(size) / 4.0
    fw = fw if fw is not None else r * 0.34
    sd = -1.0 if side < 0 else 1.0                   # the little finger's x side
    ts = -sd                                         # the thumb's x side
    reach_k = min(max((0.36 if grip is None else float(grip)) / 0.36, 0.6), 1.6)
    fws = [fw * k for k in CUP_FW]
    span = sum(fws)
    # knuckle row (index on the thumb side), centred a little toward the little finger
    order = list(range(4)) if ts < 0 else list(range(3, -1, -1))     # left → right finger ids
    xs, x = {}, -span / 2 + sd * 0.06 * span
    for fid in order:
        xs[fid] = x + fws[fid] / 2
        x += fws[fid]
    y_kn = r + CUP_KN * fw + 0.02 * float(knuckle)
    lat = _orb_low_latitude(r) if clear_y == "orb" else (
        None if clear_y is None else (clear_y if callable(clear_y) else (lambda x, _y=float(clear_y): _y)))
    CLR = GAP + MEDIUM / 2 + FINE / 2 + 0.6          # a fingertip's top below a latitude
    tips0 = []
    for k in range(4):
        xt = xs[k] * spread
        rho = r * (1.0 - CUP_OVER[k] * reach_k)
        yt = math.sqrt(max(rho * rho - xt * xt, 0.25 * rho * rho))
        tips0.append(P(xt, yt + 0.44 * fws[k] * 0.2))
    lat_mode = None
    if lat is not None:
        # the ripple latitude either runs whole ABOVE the fingertips, or (when that would push
        # them off the sphere) passes BEHIND the fingers below the notches, hidden from the
        # index to the little finger: never chopped into dashes between the tips
        below = [max(t[1], lat(t[0]) + CLR + 0.44 * fws[k]) for k, t in enumerate(tips0)]
        if max(b - t[1] for b, t in zip(below, tips0)) <= 0.12 * r:
            lat_mode = "above"
            for k, t in enumerate(tips0):
                t[1] = below[k]
        else:
            lat_mode = "behind"
            for k, t in enumerate(tips0):
                t[1] = min(t[1], lat(t[0]) - (MEDIUM / 2 + FINE / 2 + 1.5))
    fing, tipc, cens, tipr, kns = [], [], [], [], []
    for k in range(4):
        xk = xs[k]
        kn = P(xk, y_kn + 0.06 * abs(xk) ** 1.5 / max(r, 1.0) ** 0.5)
        rt_ = 0.44 * fws[k]
        tip = tips0[k]
        xt = tip[0]
        mid = (kn + tip) / 2 + P(0.08 * (xt - xk) + 0.04 * xt, 0.0)
        cen = _qbez(kn + P(0.0, 0.45 * fws[k]), mid, tip, 12)
        fing.append(_digit(cen, np.linspace(fws[k] + 0.8, 2 * rt_, len(cen))))
        cens.append(cen)
        tipc.append(tip)
        tipr.append(rt_)
        kns.append(kn)
    fingers = shapely.union_all(fing + [_webs(fing, cens, order)])
    tipz = shapely.union_all([Point(*q).buffer(rr_ + 2.6, quad_segs=12) for q, rr_ in zip(tipc, tipr)])
    fingers = _biggest(_junction_smooth(fingers, tipz, r=2.0))
    W = P(sd * 0.45 * r, 1.8 * r) if wrist is None else P(wrist) - c
    if W[1] > 2.1 * r + 22.0:
        _hand_warn(f"cup at ({c[0]:.0f}, {c[1]:.0f}): wrist {W[1]:.0f} px below the sphere centre "
                   f"(best ≈ {1.6 * r:.0f}–{1.9 * r:.0f}): a long palm; move the cuff up")
    hw = min(float(wrist_w) if wrist_w is not None else BIG, 0.68 * span) / 2.0
    kc = P(np.mean([q[0] for q in kns]), y_kn)
    # the thumb: a short lobe from the palm's thumb-side edge up to the rim
    tw = float(thumb_w) if thumb_w is not None else 1.0 * fw
    a_t = math.radians(min(max(float(thumb_to) + 8.0, 22.0), 60.0))
    t_tip = P(ts * (r - 0.15 * tw) * math.cos(a_t), (r - 0.15 * tw) * math.sin(a_t))
    while lat_mode == "above" and t_tip[1] - 0.43 * tw < lat(t_tip[0]) + CLR and a_t < math.radians(75.0):
        a_t += math.radians(2.0)                   # the thumb's tip below the ripple latitude too
        t_tip = P(ts * (r - 0.15 * tw) * math.cos(a_t), (r - 0.15 * tw) * math.sin(a_t))
    i_idx = 0
    t_root = P(xs[i_idx] + ts * 0.05 * fws[i_idx], y_kn + 0.55 * fw)

    def build(u):
        u = _unit(u, (0.0, 1.0))
        n = np.array([u[1], -u[0]])
        Wl, Wr = (W + n * hw, W - n * hw) if (n[0] < 0) else (W - n * hw, W + n * hw)
        lft, rgt = order[0], order[-1]
        kl = P(xs[lft] - fws[lft] / 2 - 0.2, kns[lft][1] + 0.9 * fw)
        kr = P(xs[rgt] + fws[rgt] / 2 + 0.2, kns[rgt][1] + 0.9 * fw)
        # the palm's sides: down from the knuckles, curving into the wrist; the little-finger
        # side swells (hypothenar), the thumb side is straighter (the thumb grows from it)
        dn = _unit(P(0.0, 1.0) + 0.8 * u)
        le = _edge(kl, _unit(dn + P(0.25, 0.0)) if Wl[0] > kl[0] else dn, Wl, u, 20)
        re_ = _edge(kr, _unit(dn + P(-0.25, 0.0)) if Wr[0] < kr[0] else dn, Wr, u, 20)
        for pts_, is_little in ((le, sd < 0), (re_, sd > 0)):
            ch = _unit(pts_[-1] - pts_[0])
            nn_ = np.array([-ch[1], ch[0]])
            if float(np.dot(nn_, pts_[0] - kc)) < 0:
                nn_ = -nn_
            tt_ = np.linspace(0.0, 1.0, len(pts_))[:, None]
            bulge = (0.035 if is_little else 0.0) * span
            pts_ += nn_ * bulge * np.sin(np.pi * tt_) ** 1.3
        ring = ([P(kl[0], y_kn - 0.6 * fw)] + list(le) + [Wl + u * stub, Wr + u * stub] + list(re_[::-1])
                + [P(kr[0], y_kn - 0.6 * fw)])
        palm = _biggest(Polygon([tuple(q) for q in ring]).buffer(0))
        # the thumb, rooted in the thenar on the palm's edge
        root = t_root + P(0.0, 0.10 * fw)
        d_t = _unit(t_tip - root)
        mid_t = (root + t_tip) / 2 + np.array([d_t[1], -d_t[0]]) * (0.10 * tw) * (1 if ts * d_t[1] < 0 else -1)
        cen_t = _qbez(root, mid_t, t_tip, 12)
        thumb = _digit(cen_t, np.linspace(1.15 * tw, 0.86 * tw, len(cen_t)))
        # the thenar: the thumb's lower half flows into the palm and on into the wrist
        Wt = Wl if ts < 0 else Wr
        low_t = thumb.intersection(shapely.box(-BIG, y_kn - 0.1 * fw, BIG, BIG))
        thenar = shapely.union_all([low_t, Point(*Wt).buffer(0.5), Point(*W).buffer(0.5),
                                    Point(*kns[i_idx]).buffer(0.5)]).convex_hull if not low_t.is_empty else Polygon()
        hand_ = shapely.union_all([fingers, palm, thumb, thenar])
        keep = tipz.union(Point(*t_tip).buffer(0.43 * tw + 2.6, quad_segs=12))
        # the web between thumb and index finger: a wide smooth V (closing only there)
        webc = (t_tip + tipc[i_idx]) / 2
        webz = Point(*((webc + kns[i_idx]) / 2)).buffer(0.9 * fw)
        hand_ = _junction_smooth(hand_, keep.union(shapely.box(-BIG, -BIG, BIG, BIG).difference(webz)), r=0.55 * fw)
        hand_ = _junction_smooth(hand_, keep.union(webz), r=0.30 * fw)
        hand_ = _clean(hand_, r_open=1.4, r_close=0.9)
        inner = C.Frag()
        lines_ = []
        stops = {frozenset((0, 1)): 0.15, frozenset((1, 2)): 0.0, frozenset((2, 3)): 0.25}
        for i in range(3):
            ka, kb_ = order[i], order[i + 1]
            ca, cb = cens[ka], cens[kb_]
            wa, wb = fws[ka], fws[kb_]
            seam = (ca * wb + cb * wa) / (wa + wb)                      # knuckle → tips
            ext = seam[-1] + _unit(seam[-1] - seam[-3]) * 8.0
            # stop at (or a little above) the knuckle row, staggered
            s_ = stops[frozenset((ka, kb_))]
            end = seam[0] + (seam[-1] - seam[0]) * (0.18 + s_)
            q = np.vstack([ext, seam[::-1]])
            q = q[q[:, 1] <= end[1] + 1e-6]
            if len(q) >= 2:
                lines_ += _notch_lines(np.vstack([q, end]), hand_)
        inner += _lines_frag(lines_, "finger")
        return hand_, inner, thumb

    Mt = (1, 0, 0, 1, c[0], c[1])
    meta0 = {"kind": "cup", "size": 4 * fw / HAND_K}

    def place(u):
        hl, il, tl = build(u)
        hs, is_ = _xf(hl, Mt), il.translate(c[0], c[1])
        return Part(hs, C.Frag(), outline(hs) + is_, {**meta0, "inner": is_, "rebuild": rebuild}), tl

    def rebuild(u_screen):
        return place(P(u_screen))[0]

    u0 = _unit(W - kc, (0.0, 1.0))
    part, tl = place(u0)
    return Hand(part, Part(_xf(tl, Mt), C.Frag(), C.Frag(), {"merged": True}), W + c, 2 * hw, u0, float(stub))


# -----------------------------------------------------------------------------
# open hand: flat on the chest, a gesture, a blessing
# -----------------------------------------------------------------------------
OPEN_LEN = (0.89, 1.0, 0.94, 0.74)       # finger length (index → little) relative to the middle
OPEN_KN = (0.025, 0.0, 0.025, 0.075)     # knuckle set-back (× hand length) from the middle finger's
OPEN_FW = (1.02, 1.04, 1.0, 0.86)        # finger width relative to a quarter of the knuckle breadth
OPEN_STOP = (0.20, 0.10, 0.24)           # finger lines stop this far (× finger length) short of the knuckles


def flat(at, angle=0.0, *, side=-1, length=56.0, width=30.0, wrist_w=None, tips=None,
         knuckle=0.55, thumb_deg=32.0, thumb_len=0.44, taper=0.78, curl=0.0, stub=0.0, size=None,
         hand=None, view="back", spread=0.0, palm_crease=None) -> Hand:
    """An open hand (on the chest, a bodice, a belt, a hilt; a gesture) from
    ``at`` (the wrist) pointing ``angle`` (screen degrees): ONE silhouette.

    * the palm tapers from the knuckle row (``knuckle`` × length along, the
      index and little knuckles set back on an arc) to a wrist ``taper`` ×
      ``width`` wide (never wider than ``wrist_w``), the little-finger edge
      swelling a little (hypothenar), running ``stub`` px on behind ``at``
      (tucked into a cuff by ``Hand.add_to``);
    * four tapered fingers ≈ 45 % of the hand's length with round tips, the
      middle longest, the little finger short and narrow; ``spread``° opens
      them (0: together, their separations three open lines from the tip
      notches almost to the knuckles; ≥ 4: apart, the gaps drawn by the
      contour); ``curl``° bends them softly toward the little-finger side;
      ``tips`` (old API) sets how far each stops short of ``length``;
    * the THUMB opens from about mid-palm on a wide, smooth V web,
      ``thumb_deg``° off the index edge, ``thumb_len`` × length long from
      its root low in the thenar (its free part ≈ half the middle finger),
      its last joint bending a little back toward the fingers;
    * ``view='palm'`` adds the thenar crease ('life line'): from the web
      between thumb and index round the thumb's mound toward the wrist,
      its hollow toward the thumb, ≈ 0.35 × the palm long (``palm_crease``
      forces it on or off).

    Size: ``size`` = the hand length (``hand_size(face)``; overrides
    ``length``/``width``). Chirality: ``side`` −1 puts the thumb on the
    screen-left of the pointing direction; ``hand='L'|'R'`` with ``view``
    sets it instead (a right hand seen from the back has its thumb on the
    left of the pointing direction). Returns a Hand."""
    if size is not None:
        length, width = float(size), HAND_K * float(size)
    if hand is not None:
        right = str(hand).upper()[:1] == "R"
        side = -1 if right == (view == "back") else +1
    L = float(length)
    kb = float(width)
    ts = -1.0 if side < 0 else 1.0                 # local y of the thumb side
    fw0 = kb / 4.0
    fws = [fw0 * k for k in OPEN_FW]
    xk = L * float(knuckle)
    ww = min(float(wrist_w) if wrist_w is not None else BIG, taper * kb) / 2.0
    Lmid = L - xk
    # finger centres across the knuckle line (index on the thumb side)
    ys, y = [], ts * kb / 2
    for k in range(4):
        ys.append(y - ts * fws[k] / 2)
        y -= ts * fws[k]
    if tips is not None:
        lens = [max(L - xk - float(tips[k]), 0.3 * Lmid) for k in range(4)]
    else:
        lens = [Lmid * OPEN_LEN[k] for k in range(4)]
    sp = float(spread)
    fing, tipc, cens, kns = [], [], [], []
    for k in range(4):
        kx = xk - OPEN_KN[k] * L
        base = P(kx - 0.12 * Lmid, ys[k])
        ang_k = ts * (1.5 - k) * (sp if sp else 1.0)       # a hint of fan even together
        d0 = P(math.cos(math.radians(ang_k)), math.sin(math.radians(ang_k)))
        # curling: the fingers bend toward the palm (foreshortened: shorter), with only a
        # little sideways sweep toward the little finger; their tips stay in one smooth row
        cl = -ts * 0.45 * float(curl) * (0.7 + 0.3 * k / 3.0)
        lk = (lens[k] + 0.12 * Lmid) * (1.0 - 0.45 * math.sin(math.radians(min(float(curl), 80.0))))
        cen = _bend(base, d0, lk - 0.45 * fws[k], cl, n=12)
        fing.append(_digit(cen, np.linspace(fws[k] + 0.9, (0.84 if sp else 0.90) * fws[k], len(cen))))
        tipc.append(cen[-1])
        cens.append(cen)
        kns.append(P(kx, ys[k]))
    tipr = [0.45 * fws[k] * (0.84 if sp else 0.90) / 0.9 for k in range(4)]
    if sp:
        # apart: only the webs at their roots join them (a quarter of the way up)
        webs = shapely.union_all([shapely.union(fing[k], fing[k + 1]).convex_hull.intersection(
            _behind(cens[k][3], cens[k][-1] - cens[k][0])) for k in range(3)])
    else:
        webs = _webs(fing, cens)
    fingers = shapely.union_all(fing + [webs])
    tipz = shapely.union_all([Point(*q).buffer(tipr[k] + 2.6, quad_segs=12) for k, q in enumerate(tipc)])
    fingers = _junction_smooth(fingers, tipz, r=1.6 if sp else 2.0)

    # the palm: one convex mass from the wrist to the knuckle row, the hypothenar swelling
    kx0, kx3 = xk - OPEN_KN[0] * L, xk - OPEN_KN[3] * L
    hyp_r = 0.20 * kb
    hyp_c = P(0.42 * xk, -ts * (0.5 * (ww + kb / 2) - hyp_r + 0.02 * kb))
    edge_i = P(kx0 - 0.10 * Lmid, ys[0] + ts * (fws[0] / 2 - 2.0))
    edge_l = P(kx3 - 0.16 * Lmid, ys[3] - ts * (fws[3] / 2 - 2.0))
    palm = shapely.union_all([
        Point(-stub, -ww + 2.0).buffer(2.0), Point(-stub, ww - 2.0).buffer(2.0),
        Point(*edge_i).buffer(2.0, quad_segs=8), Point(*edge_l).buffer(2.0, quad_segs=8),
        Point(*hyp_c).buffer(hyp_r, quad_segs=16)]).convex_hull
    # the thumb: CMC low on the thumb side; a straight metacarpal in the thenar mound,
    # then the free part opening thumb_deg° off the index edge, its last joint bending back
    root = P(0.10 * L, ts * (ww - 0.11 * kb))
    web_x = 0.36 * L + 0.10 * xk                   # the V's bottom: about mid-palm
    Lt = L * float(thumb_len)
    a0 = math.radians(float(thumb_deg))
    d_free = P(math.cos(a0), ts * math.sin(a0))
    # the metacarpal runs along the thumb-side edge to the web, the free part turns out
    mcp = P(web_x - 0.02 * L, ts * (kb / 2 + 0.02 * kb))
    L1 = float(np.hypot(*(mcp - root)))
    L2 = max(Lt - L1, 0.62 * lens[1])
    L2 = min(L2, 0.70 * lens[1])                   # its free part ≈ half the middle finger (+ the joint)
    L2 *= 1.0 - 0.25 * math.sin(math.radians(min(float(curl), 80.0)))
    bend_t = -ts * 8.0                             # the last joint bends back a little toward the fingers
    cen2 = _bend(mcp, d_free, L2, bend_t, n=10)
    cen1 = np.linspace(root, mcp, 6)
    cen_t = np.vstack([cen1[:-1], cen2])
    wt = np.concatenate([np.linspace(0.38 * kb, 0.30 * kb, 5),
                         0.29 * kb - 0.06 * kb * np.linspace(0.0, 1.0, len(cen2)) ** 0.8])
    thumb = _digit(cen_t, wt)
    tip_t = cen_t[-1]
    # the thenar mound: from the thumb's root into the palm and the wrist (no notch)
    mound = 0.45 * root + 0.55 * mcp + P(0.0, ts * 0.02 * kb)    # the thenar swells a little past the metacarpal
    thenar = shapely.union_all([Point(*root).buffer(0.20 * kb, quad_segs=12),
                                Point(*mound).buffer(0.165 * kb, quad_segs=12),
                                Point(*(mcp - d_free * 0.04 * L)).buffer(0.14 * kb, quad_segs=12),
                                Point(*P(-stub, ts * (ww - 2.0))).buffer(2.0)]).convex_hull
    body = shapely.union_all([fingers, palm, thenar])
    hand_ = shapely.union_all([body, thumb])
    keep = tipz.union(Point(*tip_t).buffer(0.12 * kb + 2.6, quad_segs=12))
    if sp:
        keep = keep.union(shapely.union_all([shapely.union(fing[k], fing[k + 1]).convex_hull.difference(
            _behind(cens[k][3], cens[k][-1] - cens[k][0])) for k in range(3)]))
    # the palm's edges run smoothly into the outer fingers (no knob at a finger's root)
    between = shapely.union_all([shapely.union(fing[k], fing[k + 1]).convex_hull.difference(
        _behind(cens[k][len(cens[k]) // 3], cens[k][-1] - cens[k][0])) for k in range(3)])
    # the V between the thumb's free part and the index finger (kept open: only its bottom rounds)
    webz = Polygon([tuple(mcp - d_free * 0.06 * L), tuple(tip_t + d_free * 0.1 * kb),
                    tuple(tipc[0])]).buffer(0.06 * kb)
    hand_ = _junction_smooth(hand_, keep.union(between).union(webz), r=0.16 * kb)
    # the web between thumb and index: a wide V with a round bottom
    hand_ = _junction_smooth(hand_, keep.union(shapely.box(-BIG, -BIG, BIG, BIG).difference(webz)), r=0.07 * kb)
    hand_ = _clean(hand_, r_open=1.2, r_close=1.0)
    inner = C.Frag()
    lines_ = []
    if not sp:
        for k in (1, 2, 3):
            ca, cb = cens[k - 1], cens[k]
            n_ = min(len(ca), len(cb))
            wa, wb = fws[k - 1], fws[k]
            mid = (ca[:n_] * wb + cb[:n_] * wa) / (wa + wb)
            ext = mid[-1] + _unit(mid[-1] - mid[-2]) * 9.0
            m2 = np.vstack([ext, mid[::-1]])
            # from the notch back toward the knuckles, stopping a little short (staggered)
            fl = 0.5 * (lens[k - 1] + lens[k])
            keep_len = float(np.hypot(*(ext - mid[-1]))) + (1.0 - OPEN_STOP[k - 1]) * fl \
                - float(np.hypot(*(mid[0] - mid[-1]))) * 0.0
            acc, out = 0.0, [m2[0]]
            for p0, p1 in zip(m2[:-1], m2[1:]):
                s = float(np.hypot(*(p1 - p0)))
                if acc + s >= keep_len:
                    out.append(p0 + (p1 - p0) * (keep_len - acc) / max(s, 1e-9))
                    break
                out.append(p1)
                acc += s
            lines_ += _notch_lines(np.array(out), hand_)
    inner += _lines_frag(lines_, "finger")
    if (view == "palm") if palm_crease is None else palm_crease:
        # the thenar crease ('life line'): from just inside the web between thumb and index,
        # round the thumb's mound toward the wrist, its hollow facing the thumb
        clear_ = MEDIUM + GAP_MARK + 0.4
        zone = hand_.buffer(-clear_)
        others = [LineString(q) for q in lines_ if len(q) >= 2]
        if others:
            zone = zone.difference(shapely.union_all(others).buffer(clear_))
        web_v = P(web_x + 0.02 * L, ts * (kb / 2 - 0.02 * kb))
        Lc = 0.35 * xk
        start = web_v + P(0.02 * L, -ts * 0.17 * kb)        # inside the palm, below the web
        end = start + P(-0.90 * Lc, -ts * 0.05 * Lc)        # toward the wrist
        ctrl = (start + end) / 2 + P(0.0, -ts * 0.30 * Lc)  # bowing away from the thumb: hollow toward it
        pts = _qbez(start, ctrl, end, 20)
        lines_c = [q for q in _open_line(pts, zone, start_on=False) if len(q) >= 2]
        lines_c = [max(lines_c, key=lambda q: LineString(q).length)] if lines_c else []
        inner += _lines_frag(lines_c, "crease")
    M, Mf = _rigid(at, angle, mirror_x=False)
    hand_s = _xf(hand_, M)
    inner_s = inner.transformed(Mf)
    u = _unit(_vec(M, P(-1.0, 0.0)))
    drawn = None if hand is None else str(hand).upper()[:1]
    meta = {"kind": "flat", "inner": inner_s, "view": view, "hand": drawn, "size": L}
    return Hand(Part(hand_s, C.Frag(), outline(hand_s) + inner_s, meta),
                Part(_xf(thumb, M), C.Frag(), C.Frag(), {"merged": True}), P(at), 2 * ww, u, float(stub))


def open_hand(at, angle=-90.0, *, size, hand="R", view="back", spread=0.0, curl=0.0, thumb_deg=40.0,
              thumb_len=0.46, stub=HAND_STUB, wrist_w=None, **kw) -> Hand:
    """An open hand of the figure's ``hand`` ('L'|'R') seen from ``view``
    ('back'|'palm'), wrist at ``at``, fingers pointing ``angle``; ``size`` =
    ``hand_size(face)``. ``spread``° apart (0: together), ``curl``° softly
    closing. A thin front door to ``flat``."""
    return flat(at, angle, size=size, hand=hand, view=view, spread=spread, curl=curl, thumb_deg=thumb_deg,
                thumb_len=thumb_len, stub=stub, wrist_w=wrist_w, **kw)


def hand(pose, *args, **kw) -> Hand:
    """One door to every hand: ``pose`` 'grip' (``fist``), 'pinch'
    (``pinch``), 'cup' (``cup``), 'open' (``open_hand``) or 'flat'
    (``flat``); the rest is passed on."""
    fn = {"grip": fist, "fist": fist, "pinch": pinch, "hold": pinch, "cup": cup, "orb": cup,
          "open": open_hand, "flat": flat, "gesture": open_hand}[pose]
    return fn(*args, **kw)
