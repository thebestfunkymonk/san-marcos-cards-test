"""Design tokens used by inkkit demos and as generator defaults.

Palette and line weights are the drop-in block from the HEADWATERS creative
brief (research/creative-brief.md §B.2 and §C). ``deck/tokens.py`` remains the
deck's single source of truth; this module mirrors it for the toolkit so the
demos render in the approved palette.

Print profiles give the minimum printable feature sizes at 300 ppi
(1 px = 0.0847 mm). They are used by :mod:`inkkit.preflight` and as the
``min_width`` floor of ornament generators. Confirm them with the printer.
"""
DRAFT = False  # palette replaced by the creative brief (2026-09-22)

# --- palette (brief §C) -------------------------------------------------------
PAPER = "#F4EFE3"   # Limestone: face ground (design on white too)
INK = "#15242B"     # Aquifer: spades/clubs, all key lines
RED = "#AE2F2B"     # Gill Red: hearts/diamonds, court red, seal paper
JADE = "#1D5A55"    # Spring Jade: court fills, card-back flood
FOIL = "#B08D57"    # Lion Gold: metallic ink (faces) / foil (tuck, seal), flat
BOARD = "#0F2B29"   # Deep Hole: tuck board
FOIL_PREVIEW = ("#8A6A34", "#D8B56A", "#F6E3A1")  # tuck/seal mock-ups ONLY
PALETTE = {"paper": PAPER, "ink": INK, "red": RED, "jade": JADE, "foil": FOIL, "board": BOARD}

# layer order used by the deck (bottom -> top): fills below lines
LAYERS = ("paper", "jade", "red", "gold", "ink")

# --- line weights at 750x1050 px (brief §B.2, the only legal stroke widths) -----
HAIRLINE = 1.6      # awns, em-rules on small type; the foil minimum
FINE = 2.1          # THE monoline: ornament, hatching, gold inner rules
MEDIUM = 3.1        # interior detail, knockout lines inside solid pips
RULE = 4.2          # court frame, outer rules
CONTOUR = 6.25      # figure silhouettes
HEAVY = CONTOUR     # legacy alias
HATCH_PITCH = 7.0   # FINE hatch at 7.0 px pitch (4.9 px gap)
TERMINAL_D = 6.3    # circle terminal on free line ends
DOT_DIAMETERS = (4.2, 6.3, 8.4)
INTERLACE_GAP = 4.2  # under-stroke breaks 4.2 px each side of the over-stroke

# --- print profiles (minimum feature sizes, px @ 300 ppi) -------------------------
PX_PER_MM = 300 / 25.4
PRINT_PROFILES = {
    # offset litho, one spot ink: 0.25 pt positive line, reversed lines need more
    "ink_offset": {"min_line": 1.05, "min_reversed": 1.8, "min_gap": 1.2},
    # metallic ink / foil per the brief (HAIRLINE is the foil minimum)
    "foil": {"min_line": 1.6, "min_reversed": 2.4, "min_gap": 2.4},
    # conservative hot-foil rule of thumb (0.2 mm line, 0.25 mm gap)
    "foil_strict": {"min_line": 2.4, "min_reversed": 3.0, "min_gap": 3.0},
}
MIN_LINE = PRINT_PROFILES["ink_offset"]["min_line"]      # default ornament floor
MIN_REVERSED = PRINT_PROFILES["ink_offset"]["min_reversed"]
MIN_GAP = PRINT_PROFILES["ink_offset"]["min_gap"]
