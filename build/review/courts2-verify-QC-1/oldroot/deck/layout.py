"""Pip-card layouts 2-10 — creative brief §E.2 exactly.

Columns L 222 / C 375 / R 528; rows T 198 / B 852; four-row columns at
y 198, 416, 634, 852. Pips are placed by the centre of their bounding box;
every pip centred below y = 525 is rotated 180° (y = 525 stays upright).
Field pip u = 116. Pip cards carry no border, frame or ornament.
"""
from __future__ import annotations

from deck import tokens as T
from deck import pips as P
from inkkit import svg as S

__all__ = ["LAYOUT", "positions", "pip_card_fragments", "ROWS4"]

L, C, R = T.COL_L, T.COL_C, T.COL_R
TOP, BOT, MID = T.ROW_T, T.ROW_B, T.CY
ROWS4 = tuple(TOP + (BOT - TOP) * k / 3 for k in range(4))       # 198, 416, 634, 852

LAYOUT: dict[int, list[tuple[float, float]]] = {
    2: [(C, TOP), (C, BOT)],
    3: [(C, TOP), (C, MID), (C, BOT)],
    4: [(L, TOP), (R, TOP), (L, BOT), (R, BOT)],
}
LAYOUT[5] = LAYOUT[4] + [(C, MID)]
LAYOUT[6] = [(x, y) for y in (TOP, MID, BOT) for x in (L, R)]
LAYOUT[7] = LAYOUT[6] + [(C, (TOP + MID) / 2)]                   # C361.5
LAYOUT[8] = LAYOUT[7] + [(C, (BOT + MID) / 2)]                   # C688.5
LAYOUT[9] = [(x, y) for y in ROWS4 for x in (L, R)] + [(C, MID)]
LAYOUT[10] = [(x, y) for y in ROWS4 for x in (L, R)] + [(C, (ROWS4[0] + ROWS4[1]) / 2),
                                                          (C, (ROWS4[2] + ROWS4[3]) / 2)]  # C307, C743


def positions(n: int) -> list[tuple[float, float, bool]]:
    """(cx, cy, rotated) for each pip of the n-spot (rotated iff cy > 525)."""
    return [(x, y, y > MID) for x, y in LAYOUT[int(n)]]


def pip_card_fragments(rank: str, suit: str) -> dict:
    """{suit layer: [pip paths]} for a 2-10 pip card (indices not included)."""
    col = T.SUIT_COLOR[suit]
    frags = [S.path(P.pip_d(suit, T.PIP_U_FIELD, x, y, rotate=rot), fill=col, class_="pip",
                    data_cx=x, data_cy=y, data_rot=int(rot))
             for x, y, rot in positions(int(rank))]
    return {T.SUIT_LAYER[suit]: frags}
