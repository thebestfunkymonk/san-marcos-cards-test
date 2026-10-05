# art/: one module per piece

This folder holds `art/<ID>.py`, one module per piece. Each module exposes
`build() -> {layer: [svg fragments]}`, drawn in card coordinates (750 × 1050, y down).

| IDs | You draw | The system adds |
|---|---|---|
| `KS QS JS KH QH JH KC QC JC KD QD JD` | the **top half only**, inside the art window x 139–611, y 55–511 (it may run into the band) | the clip, the 180° copy, the frame, the divider band, the medallion, the corner pips and the indices |
| `AS AH AC AD` | everything: the pip (`deck.frames.ace_pip_d`), the keyline (not on A♠), the emblem and the caption (A♠: the four-line legend, `frames.ACE_SPADE_LEGEND`) | the indices |
| `JOKER_RED JOKER_BLACK` | everything: the figure, the rule, the title and the subline | the vertical JOKER index |
| `BACK` | everything: the jade flood with geometric knockouts | the Limestone stock |

Rules:
- Use the layers `paper`, `jade`, `red`, `gold` and `ink`. They paint in that order (A♠/A♣: gold above ink), so a lower colour drawn over a higher colour's solid is **invisible** — cut it out of the solid (contract §2.1).
- Use only these stroke widths: 1.6, 2.1, 3.1, 4.2 and 6.25.
- Knockouts and interlace gaps must be geometry, never paper-coloured paint. Keep 4.2 px between parallel strokes, 3 px between separate marks, 2.5 px knockout lines (contract §5.1).
- Emit plain paths. No text, `<use>`/`<symbol>`, nested `<svg>`, scale transforms (attribute or CSS), filters, gradients, masks or opacity.

If a module is missing or raises an error, the piece builds as a placeholder.

The full contract covers coordinates, the layer table, the stroke tokens, the knockout recipes, the spacing QA measures, the helpers (`deck.pips`, `deck.frames`, `deck.motifs`), a skeleton module and the deviations from the brief (D1 spade, D2 plinth, D3 Q index, D4 ♠ step). It is in **[`deck/ART_CONTRACT.md`](../deck/ART_CONTRACT.md)**.

```sh
.venv/bin/python -m deck.build KS     # cards/KS.svg + build/png/KS.png + build/png/small/KS.png
.venv/bin/python -m deck.qa KS        # rebuilds KS, prints its §I checklist row;
                                      # details in build/qa/report.json, flags in build/qa/flags/KS.png
```
