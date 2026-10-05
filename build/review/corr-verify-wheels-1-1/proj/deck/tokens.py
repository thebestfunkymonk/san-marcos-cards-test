"""HEADWATERS design tokens — verbatim from research/creative-brief.md §B, §C, §D.

This file is the single source of truth for colours, stroke widths and type.
Do not hard-code any of these values elsewhere; import them.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "fonts"

# --- Artboard (§B.1) -------------------------------------------------------
W, H = 750, 1050
CX, CY = 375, 525
CORNER_R = 37.5
SAFE = 37.5
BLEED = 37.5

# --- Palette (§C) ----------------------------------------------------------
PAPER = "#F4EFE3"   # Limestone (face ground; design on white too)
WHITE = "#FFFFFF"   # alternate stock for QA only
INK   = "#15242B"   # Aquifer: ♠♣ pips/indices, all key lines
RED   = "#AE2F2B"   # Gill Red: ♥♦ pips/indices, court red, seal paper
JADE  = "#1D5A55"   # Spring Jade: court fills, card-back flood
FOIL  = "#B08D57"   # Lion Gold: metallic ink (faces) / foil (tuck, seal), flat
BOARD = "#0F2B29"   # Deep Hole: tuck board
FOIL_PREVIEW = ("#8A6A34", "#D8B56A", "#F6E3A1")  # tuck/seal mock-ups ONLY
PALETTE = {"paper": PAPER, "ink": INK, "red": RED, "jade": JADE, "foil": FOIL, "board": BOARD}
LEGAL_COLORS = {PAPER, WHITE, INK, RED, JADE, FOIL, BOARD}

# Layer ids required in every card SVG (§I.25, §K), bottom to top.
LAYERS = ("paper", "jade", "red", "gold", "ink")

# --- Line weights (§B.2) — the only legal stroke widths ----------------------
HAIRLINE, FINE, MEDIUM, RULE, CONTOUR = 1.6, 2.1, 3.1, 4.2, 6.25
LEGAL_STROKES = (HAIRLINE, FINE, MEDIUM, RULE, CONTOUR)
HATCH_PITCH = 7.0
TERMINAL_D = 6.3
DOT_DIAMETERS = (4.2, 6.3, 8.4)
INTERLACE_GAP = 4.2

# --- Typography (§D) -------------------------------------------------------
FONT_INDEX = FONTS / "BarlowCondensed-SemiBold.ttf"
FONT_MICRO_MEDIUM = FONTS / "BarlowCondensed-Medium.ttf"   # tuck side panels only, cap >= 18
FONT_SLAB = FONTS / "RobotoSlab[wght].ttf"                 # use variations={"wght": 700}
SLAB_VARIATIONS = {"wght": 700}

INDEX_AXIS_X = 84
INDEX_FONT_SIZE = 137.14      # cap height 96
INDEX_CAP_TOP = 46
INDEX_BASELINE = 142
INDEX_TEN_TRACKING = -20      # 1/1000 em, "10" only
INDEX_PIP_U = 62
INDEX_PIP_TOP = 164
JOKER_INDEX_FONT_SIZE = 62.86 # cap 44
JOKER_INDEX_CAP_TOPS = (46, 96, 146, 196, 246)

# --- Suits -----------------------------------------------------------------
SUITS = ("S", "H", "C", "D")
SUIT_COLOR = {"S": INK, "C": INK, "H": RED, "D": RED}
SUIT_LAYER = {"S": "ink", "C": "ink", "H": "red", "D": "red"}
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
HOUSES = {"S": "Deep", "H": "Fount", "C": "Reed", "D": "Ford"}

# Pip unit sizes (§E.1)
PIP_U_INDEX, PIP_U_COURT, PIP_U_FIELD, PIP_U_ACE_SPADE, PIP_U_ACE = 62, 88, 116, 340, 280
HEART_OPTICAL = 1.04

# --- Pip-card layout (§E.2) -------------------------------------------------
COL_L, COL_C, COL_R = 222, 375, 528
ROW_T, ROW_B = 198, 852

# --- Court frame (§F.1) ----------------------------------------------------
FRAME_X0, FRAME_Y0, FRAME_X1, FRAME_Y1 = 128, 44, 622, 1006
FRAME_CHAMFER = 18
FRAME_INNER_INSET = 7
ART_WINDOW = (139, 55, 611, 511)   # x0, y0, x1, y1 — drawable top half
COURT_PIP_BOX = (146, 62, 234, 159)
BAND_Y0, BAND_Y1 = 511, 539
