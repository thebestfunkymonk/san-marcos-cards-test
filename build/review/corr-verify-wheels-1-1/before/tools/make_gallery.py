"""Generate the HEADWATERS presentation page (build/gallery/index.html).

    .venv/bin/python tools/make_gallery.py

The page references card PNGs (grid) and SVGs (lightbox) by relative path;
`files_manifest()` returns the published-path -> source-path map used when
publishing it as an Artifact.
"""
from __future__ import annotations

import html
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from deck import tokens as T  # noqa: E402

OUT = os.path.join(ROOT, "build", "gallery")
SUIT_SYM = {"S": "♠", "H": "♥", "C": "♣", "D": "♦"}
RANKS = ("A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K")
HOUSES = [
    ("S", "the Deep", "The Edwards Aquifer, limestone, the Balcones fault and the blind salamander."),
    ("H", "the Fount", "Spring Lake’s surface: the vents, the glass-bottom boats, Aquamaid heritage and song."),
    ("C", "the Reed", "The riverbanks: Texas wild-rice, bald cypress, heron and kingfisher, pecan."),
    ("D", "the Ford", "El Camino Real’s river crossing and the town: the courthouse dome, Justice, the road."),
]
NAMES = {
    "KS": "The King Beneath", "QS": "The Blind Oracle", "JS": "The Lantern Page",
    "KH": "The Ferryman King", "QH": "The Aquamaid Queen", "JH": "The Spring Minstrel",
    "KC": "The Cypress King", "QC": "The Wild-Rice Queen", "JC": "The River Squire",
    "KD": "The Warden of the Ford", "QD": "The Queen of Scales", "JD": "The Herald of the Road",
    "AS": "The Lion of the Source", "AH": "The Fount", "AC": "The Reed", "AD": "The Ford",
    "JOKER-RED": "The Fool", "JOKER-BLACK": "The Trickster", "BACK": "The Source",
}
TUCK = [  # (published name, source relative to ROOT, caption)
    ("tuck/TUCK-FRONT-mock.png", "build/tuck/TUCK-FRONT-mock.png", "Tuck front — gold foil and blind emboss on Deep Hole board"),
    ("tuck/TUCK-BACK-mock.png", "build/tuck/TUCK-BACK-mock.png", "Tuck back — the card back redrawn in foil"),
    ("tuck/SEAL-mock.png", "build/tuck/SEAL-mock.png", "Seal — the Texas blind salamander, NUSQUAM ALIBI"),
    ("tuck/TUCK-FLAT.png", "build/tuck/TUCK-FLAT.png", "Flat — every panel on the tuck dieline"),
]
PRESENT = ("tuck/presentation.png", None)  # resolved in _presentation()


def _stem(r: str, s: str) -> str:
    return f"{r}{s}"


def _label(stem: str) -> str:
    if stem.startswith("JOKER"):
        return ("Big" if stem.endswith("RED") else "Little") + " Joker"
    if stem == "BACK":
        return "Card back"
    return f"{stem[:-1]}{SUIT_SYM[stem[-1]]}"


def _presentation() -> str | None:
    for cand in ("build/tuck/presentation.png", "build/tuck/TUCK-presentation.png", "build/tuck/TUCK-PRESENTATION.png",
                 "build/tuck/tuck-presentation.png", "build/tuck/TUCK-FRONT-mock.png"):
        if os.path.isfile(os.path.join(ROOT, cand)):
            return cand
    return None


def files_manifest() -> dict[str, str]:
    m = {}
    for s in T.SUITS:
        for r in RANKS:
            st = _stem(r, s)
            m[f"png/{st}.png"] = f"build/png/{st}.png"
            m[f"svg/{st}.svg"] = f"cards/{st}.svg"
    for st in ("JOKER-RED", "JOKER-BLACK", "BACK"):
        m[f"png/{st}.png"] = f"build/png/{st}.png"
        m[f"svg/{st}.svg"] = f"cards/{st}.svg"
    for pub, src, _ in TUCK:
        if os.path.isfile(os.path.join(ROOT, src)):
            m[pub] = src
    p = _presentation()
    if p:
        m[PRESENT[0]] = p
    for pub, src in (("sheets/motifs-geometric.png", "build/motifs/sheet-geometric.png"),):
        if os.path.isfile(os.path.join(ROOT, src)):
            m[pub] = src
    return {k: v for k, v in m.items() if os.path.isfile(os.path.join(ROOT, v))}


def _card(stem: str, cls: str = "", caption: bool = False) -> str:
    name = NAMES.get(stem, "")
    alt = f"{_label(stem)}" + (f" — {name}" if name else "")
    cap = ""
    if caption:
        cap = (f'<figcaption><span class="cap-rank">{html.escape(_label(stem))}</span>'
               f'{"<span class=cap-name>" + html.escape(name) + "</span>" if name else ""}</figcaption>')
    return (f'<figure class="card {cls}"><button type="button" class="card-btn" data-stem="{stem}" '
            f'aria-label="Enlarge {html.escape(alt)}"><img src="png/{stem}.png" alt="{html.escape(alt)}" '
            f'loading="lazy" width="750" height="1050"></button>{cap}</figure>')


def build() -> str:
    os.makedirs(OUT, exist_ok=True)
    m = files_manifest()
    has = lambda pub: pub in m  # noqa: E731

    houses = []
    for s, house, theme in HOUSES:
        cards = "".join(_card(_stem(r, s), caption=True) for r in ("K", "Q", "J", "A"))
        col = "red" if s in "HD" else "ink"
        houses.append(f'''
<article class="house">
  <header class="house-head">
    <span class="house-suit suit-{col}" aria-hidden="true">{SUIT_SYM[s]}</span>
    <div><h3>House of {house}</h3><p>{theme}</p></div>
  </header>
  <div class="row-cards">{cards}</div>
</article>''')

    deck_rows = []
    for s, house, _ in HOUSES:
        cards = "".join(_card(_stem(r, s), "mini") for r in RANKS)
        deck_rows.append(f'<div class="suit-row"><h3 class="label">{SUIT_SYM[s]} {house}</h3>'
                         f'<div class="grid-13">{cards}</div></div>')
    extras = "".join(_card(st, "mini", caption=True) for st in ("JOKER-RED", "JOKER-BLACK", "BACK"))

    tuck_figs = "".join(
        f'<figure class="tuck-fig"><img src="{pub}" alt="{html.escape(cap)}" loading="lazy">'
        f'<figcaption>{html.escape(cap)}</figcaption></figure>'
        for pub, src, cap in TUCK if has(pub))
    tuck_section = f'''
<section class="section" id="box" aria-labelledby="box-h">
  <div class="section-head"><p class="eyebrow">The box</p><h2 id="box-h">Board, foil and a seal</h2>
  <p class="lede">Deep Hole board — named for Spring Lake’s deepest vent — with one gold foil and blind emboss. The
  seal carries the Texas blind salamander, which lives nowhere else on Earth.</p></div>
  <div class="tuck-grid">{tuck_figs}</div>
</section>''' if tuck_figs else ""

    swatches = [("Limestone", T.PAPER, "Paper · the face ground"), ("Aquifer", T.INK, "Ink 1 · ♠ ♣ and every key line"),
                ("Gill Red", T.RED, "Ink 2 · ♥ ♦ and court red"), ("Spring Jade", T.JADE, "Ink 3 · court fills, card-back flood"),
                ("Lion Gold", T.FOIL, "Metallic ink · foil on the box"), ("Deep Hole", T.BOARD, "Tuck board")]
    sw = "".join(f'<li class="swatch"><span class="chip" style="background:{hx}"></span>'
                 f'<span class="sw-name">{n}</span><span class="sw-hex">{hx}</span><span class="sw-role">{role}</span></li>'
                 for n, hx, role in swatches)
    weights = [("Hairline", T.HAIRLINE, "awns, caption rules"), ("Fine", T.FINE, "the monoline · all ornament and hatching"),
               ("Medium", T.MEDIUM, "court detail, knockout lines"), ("Rule", T.RULE, "frames, upper eyelids"),
               ("Contour", T.CONTOUR, "court silhouettes")]
    wt = "".join(f'<li class="weight"><span class="bar" style="height:{w * 1.2:.2f}px"></span>'
                 f'<span class="w-name">{n}</span><span class="w-val">{w:g} px · {w / 300 * 72:.2f} pt</span>'
                 f'<span class="w-role">{role}</span></li>' for n, w, role in weights)
    motif_fig = ('<figure class="sheet"><img src="sheets/motifs-geometric.png" alt="Ornament library specimen sheet" '
                 'loading="lazy"><figcaption>The ornament library: Source Rosette, running wave, strata, reed ladder, '
                 'karst voids, stalactites, vent roundels — each drawn on paper and reversed out of jade.</figcaption>'
                 '</figure>') if has("sheets/motifs-geometric.png") else ""

    hero_visual = (f'<figure class="hero-shot"><img src="{PRESENT[0]}" alt="The HEADWATERS tuck box in gold foil on '
                   f'dark green board, sealed with a red salamander seal, beside the Ace of Spades and the card back"></figure>'
                   if has(PRESENT[0]) else
                   f'<div class="fan" aria-label="The Ace of Spades, the King of Spades and the card back">'
                   f'{_card("AS", "c1")}{_card("KS", "c2")}{_card("BACK", "c3")}</div>')
    lightbox_data = json.dumps(
        [{"stem": st, "label": _label(st), "name": NAMES.get(st, "")}
         for st in [_stem(r, s) for s, *_ in HOUSES for r in RANKS] + ["JOKER-RED", "JOKER-BLACK", "BACK"]])

    page = f'''<title>HEADWATERS Playing Cards</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600&family=Barlow:ital,wght@0,400;0,500;1,400&family=Roboto+Slab:wght@500;700&display=swap">
<style>
:root {{
  --ground: #F4EFE3; --ground-2: #ECE5D5; --text: #15242B; --muted: #55625F; --rule: rgba(21,36,43,.16);
  --gold: #8F7040; --jade: #1D5A55; --red: #AE2F2B; --board: #0F2B29; --board-text: #EFE7D4; --board-gold: #C9A66A;
  --shadow: 0 1px 2px rgba(15,43,41,.10), 0 8px 24px -8px rgba(15,43,41,.28);
  --slab: "Roboto Slab", Rockwell, "Courier New", Georgia, serif;
  --cond: "Barlow Condensed", "Arial Narrow", "Helvetica Neue", Arial, sans-serif;
  --body: "Barlow", "Helvetica Neue", Arial, sans-serif;
}}
@media (prefers-color-scheme: dark) {{
  :root:not([data-theme="light"]) {{
    color-scheme: dark;
    --ground: #0C1F1E; --ground-2: #102826; --text: #E9E2D1; --muted: #A2B1AB; --rule: rgba(233,226,209,.14);
    --gold: #C9A66A; --jade: #6FA79F; --red: #E07A73; --board: #081716; --board-text: #EFE7D4; --board-gold: #C9A66A;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 28px -10px rgba(0,0,0,.7);
  }}
}}
:root[data-theme="dark"] {{
  color-scheme: dark;
  --ground: #0C1F1E; --ground-2: #102826; --text: #E9E2D1; --muted: #A2B1AB; --rule: rgba(233,226,209,.14);
  --gold: #C9A66A; --jade: #6FA79F; --red: #E07A73; --board: #081716; --board-text: #EFE7D4; --board-gold: #C9A66A;
  --shadow: 0 1px 2px rgba(0,0,0,.4), 0 10px 28px -10px rgba(0,0,0,.7);
}}
* {{ box-sizing: border-box; }}
[hidden] {{ display: none !important; }}
body {{ background: var(--ground); color: var(--text); font: 400 16px/1.55 var(--body); padding-inline: 0; }}
.wrap {{ max-width: 1180px; margin-inline: auto; padding-inline: clamp(16px, 4vw, 40px); }}
h1, h2, h3 {{ text-wrap: balance; margin: 0; }}
.label, .eyebrow {{ font: 600 13px/1.2 var(--cond); letter-spacing: .22em; text-transform: uppercase; color: var(--gold); margin: 0; }}
img {{ display: block; max-width: 100%; height: auto; }}

/* hero: the box world */
.hero {{ background: var(--board); color: var(--board-text); padding-block: clamp(40px, 7vw, 88px); overflow: hidden; }}
.hero-grid {{ display: grid; grid-template-columns: minmax(0, .9fr) minmax(0, 1.25fr); gap: clamp(28px, 5vw, 64px); align-items: center; }}
.kicker {{ font: 600 13px/1 var(--cond); letter-spacing: .3em; text-transform: uppercase; color: var(--board-gold); margin: 0 0 18px; }}
.wordmark {{ font: 700 clamp(36px, 4.4vw, 60px)/1 var(--slab); letter-spacing: .06em; color: var(--board-gold); overflow-wrap: anywhere; }}
.subline {{ display: flex; align-items: center; gap: 12px; margin: 18px 0 0; font: 600 clamp(12px, 1.5vw, 15px)/1.3 var(--cond);
  letter-spacing: .24em; text-transform: uppercase; color: var(--board-text); }}
.subline::before, .subline::after {{ content: ""; flex: 0 0 28px; height: 1.5px; background: var(--board-gold); }}
.tagline {{ font: italic 400 clamp(20px, 2.4vw, 26px)/1.3 var(--body); margin: 26px 0 0; color: var(--board-text); }}
.story {{ margin: 22px 0 0; max-width: 58ch; color: color-mix(in srgb, var(--board-text) 82%, transparent); }}
.fan {{ position: relative; aspect-ratio: 1.12; max-width: 560px; justify-self: center; width: 100%; }}
.fan .card {{ position: absolute; width: 46%; margin: 0; }}
.fan .card img {{ border-radius: 5.4% / 3.9%; box-shadow: 0 20px 40px -16px rgba(0,0,0,.65); }}
.fan .c1 {{ left: 2%; top: 9%; transform: rotate(-9deg); }}
.fan .c2 {{ left: 27%; top: 2%; z-index: 2; }}
.fan .c3 {{ left: 52%; top: 9%; transform: rotate(9deg); }}
.hero-shot {{ margin: 0; }}
.hero-shot img {{ border-radius: 8px; box-shadow: 0 24px 60px -24px rgba(0,0,0,.7); }}

/* sections */
.section {{ padding-block: clamp(48px, 7vw, 88px); border-top: 1px solid var(--rule); }}
.section-head {{ display: grid; gap: 10px; margin-bottom: clamp(24px, 3.5vw, 40px); max-width: 68ch; }}
.section-head h2 {{ font: 700 clamp(28px, 3.6vw, 40px)/1.1 var(--slab); letter-spacing: .01em; }}
.lede {{ margin: 0; color: var(--muted); font-size: 17px; }}

.card {{ margin: 0; }}
.card-btn {{ all: unset; display: block; cursor: zoom-in; border-radius: 5.4% / 3.9%; }}
.card-btn:focus-visible {{ outline: 2px solid var(--gold); outline-offset: 4px; }}
.card-btn img {{ border-radius: 5.4% / 3.9%; box-shadow: var(--shadow); transition: transform .25s ease; }}
@media (hover: hover) {{ .card-btn:hover img {{ transform: translateY(-3px); }} }}
figcaption {{ display: grid; gap: 1px; margin-top: 10px; }}
.cap-rank {{ font: 600 13px/1.2 var(--cond); letter-spacing: .16em; text-transform: uppercase; color: var(--gold); }}
.cap-name {{ font: 500 15px/1.3 var(--body); }}

.houses {{ display: grid; gap: clamp(36px, 5vw, 56px); }}
.house-head {{ display: flex; gap: 16px; align-items: flex-start; margin-bottom: 18px; }}
.house-suit {{ font: 400 40px/1 var(--body); width: 44px; text-align: center; }}
.suit-red {{ color: var(--red); }} .suit-ink {{ color: var(--text); }}
.house-head h3 {{ font: 700 22px/1.2 var(--slab); }}
.house-head p {{ margin: 4px 0 0; color: var(--muted); max-width: 60ch; }}
.row-cards {{ display: grid; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: clamp(12px, 2.4vw, 28px); }}

.suit-row {{ margin-bottom: 28px; }}
.suit-row .label {{ margin-bottom: 12px; }}
.grid-13 {{ display: grid; grid-template-columns: repeat(13, minmax(0, 1fr)); gap: 8px; }}
.extras {{ display: grid; grid-template-columns: repeat(3, minmax(0, 170px)); gap: 20px; margin-top: 12px; }}

.tuck-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(16px, 3vw, 32px); }}
.tuck-fig {{ margin: 0; }}
.tuck-fig img {{ border-radius: 6px; background: var(--ground-2); }}
.tuck-fig figcaption {{ color: var(--muted); font-size: 14px; }}

.system {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: clamp(28px, 4vw, 48px); }}
.swatches, .weights {{ list-style: none; margin: 14px 0 0; padding: 0; display: grid; gap: 10px; }}
.swatch {{ display: grid; grid-template-columns: 44px 1fr auto; grid-template-rows: auto auto; column-gap: 14px; align-items: center; }}
.chip {{ grid-row: span 2; width: 44px; height: 44px; border-radius: 50%; box-shadow: inset 0 0 0 1px var(--rule); }}
.sw-name {{ font: 600 16px/1.2 var(--body); }}
.sw-hex {{ font: 500 14px/1 var(--cond); letter-spacing: .08em; color: var(--muted); font-variant-numeric: tabular-nums; }}
.sw-role {{ grid-column: 2 / 4; color: var(--muted); font-size: 14px; }}
.weight {{ display: grid; grid-template-columns: 90px 1fr; grid-template-rows: auto auto; column-gap: 16px; align-items: center; }}
.bar {{ grid-row: span 2; display: block; width: 90px; background: var(--text); border-radius: 1px; }}
.w-name {{ font: 600 16px/1.2 var(--body); }}
.w-val {{ font: 500 14px/1.2 var(--cond); letter-spacing: .06em; color: var(--muted); font-variant-numeric: tabular-nums; }}
.w-role {{ display: none; }}
.type-spec {{ margin-top: 14px; display: grid; gap: 14px; }}
.spec-index {{ font: 600 64px/1 var(--cond); letter-spacing: -.01em; }}
.spec-slab {{ font: 700 30px/1 var(--slab); letter-spacing: .12em; color: var(--gold); }}
.spec-micro {{ font: 600 13px/1 var(--cond); letter-spacing: .24em; text-transform: uppercase; }}
.sheet {{ margin: clamp(28px, 4vw, 44px) 0 0; }}
.sheet img {{ border-radius: 6px; }}
.sheet figcaption {{ color: var(--muted); font-size: 14px; }}

.specs {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; margin: 0; border-top: 1px solid var(--rule); }}
.specs div {{ padding: 16px 16px 16px 0; border-bottom: 1px solid var(--rule); }}
.specs dt {{ font: 600 13px/1.2 var(--cond); letter-spacing: .18em; text-transform: uppercase; color: var(--gold); }}
.specs dd {{ margin: 6px 0 0; font-variant-numeric: tabular-nums; }}
footer {{ padding-block: 40px 56px; color: var(--muted); font-size: 14px; border-top: 1px solid var(--rule); }}
footer .wordmark-sm {{ font: 700 18px/1 var(--slab); letter-spacing: .12em; color: var(--gold); }}

/* lightbox */
.lb {{ position: fixed; inset: 0; z-index: 50; background: rgba(8,20,19,.92); display: grid; grid-template-rows: 1fr auto;
  padding: calc(16px + env(safe-area-inset-top, 0px)) 16px calc(16px + env(safe-area-inset-bottom, 0px)); }}
.lb-stage {{ display: grid; place-items: center; min-height: 0; }}
.lb-stage img {{ max-height: 100%; max-width: 100%; width: auto; height: 100%; object-fit: contain; border-radius: 3.6% / 2.6%; }}
.lb-bar {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; color: #EFE7D4; padding-top: 12px; }}
.lb-title {{ font: 600 15px/1.3 var(--cond); letter-spacing: .16em; text-transform: uppercase; }}
.lb-title em {{ font: italic 400 16px var(--body); letter-spacing: 0; text-transform: none; color: #C9A66A; margin-left: 8px; }}
.lb button {{ font: 600 13px/1 var(--cond); letter-spacing: .16em; text-transform: uppercase; color: #EFE7D4;
  background: transparent; border: 1px solid rgba(239,231,212,.35); border-radius: 999px; padding: 10px 14px; cursor: pointer; }}
.lb button:focus-visible {{ outline: 2px solid #C9A66A; outline-offset: 2px; }}
.lb-nav {{ display: flex; gap: 8px; }}

@media (max-width: 900px) {{
  .hero-grid, .system {{ grid-template-columns: 1fr; }}
  .grid-13 {{ grid-template-columns: repeat(7, minmax(0, 1fr)); }}
  .specs {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
}}
@media (max-width: 560px) {{
  .row-cards {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
  .grid-13 {{ grid-template-columns: repeat(4, minmax(0, 1fr)); }}
  .tuck-grid {{ grid-template-columns: 1fr; }}
  .extras {{ grid-template-columns: repeat(3, minmax(0, 1fr)); }}
  .specs {{ grid-template-columns: 1fr; }}
}}
@media (prefers-reduced-motion: reduce) {{ .card-btn img {{ transition: none; }} }}
</style>

<header class="hero">
  <div class="wrap hero-grid">
    <div>
      <p class="kicker">Named for St. Mark · 1689</p>
      <h1 class="wordmark">HEADWATERS</h1>
      <p class="subline">Playing cards of the San Marcos springs</p>
      <p class="tagline">Long may it flow.</p>
      <p class="story">Where the Balcones fault splits Hill Country from plain, the Edwards Aquifer rises through more
      than two hundred spring openings at seventy-two degrees, every day of the year. HEADWATERS deals the springs’
      imagined court in four houses: the Deep, the Fount, the Reed and the Ford. Every royal wears two faces, the
      figure and its reflection.</p>
    </div>
    {hero_visual}
  </div>
</header>

<main class="wrap">
  <section class="section" id="houses" aria-labelledby="houses-h" style="border-top:0">
    <div class="section-head"><p class="eyebrow">The courts</p><h2 id="houses-h">Four houses of the springs</h2>
    <p class="lede">Twelve bespoke two-headed courts, drawn in one monoline hand: a bold contour, flat fills in three
    inks and metallic gold, and half-hatching for tone. Each house has its own divider line through the centre. The
    Deep has a fault-step, the Fount a ripple, the Reed a reed and the Ford a row of stepping stones.</p></div>
    <div class="houses">{"".join(houses)}</div>
  </section>

  <section class="section" id="deck" aria-labelledby="deck-h">
    <div class="section-head"><p class="eyebrow">Fifty-five cards</p><h2 id="deck-h">The full deck</h2>
    <p class="lede">Number cards are kept deliberately quiet: one ink, generous paper, and pips drawn from circles and
    straight lines. The spade and club stand on a small fault-step plinth, a nod to the Balcones escarpment. Select any
    card to see it full size.</p></div>
    {"".join(deck_rows)}
    <h3 class="label" style="margin-top:8px">Jokers and back</h3>
    <div class="extras">{extras}</div>
  </section>

  {tuck_section}

  <section class="section" id="system" aria-labelledby="system-h">
    <div class="section-head"><p class="eyebrow">Design system</p><h2 id="system-h">Four inks, five line weights</h2>
    <p class="lede">Every stroke in the deck is one of five widths, and every colour is one of these tokens. Paper
    marks are cut as geometry, so each ink separates cleanly onto its own plate.</p></div>
    <div class="system">
      <div><h3 class="label">Palette</h3><ul class="swatches">{sw}</ul></div>
      <div>
        <h3 class="label">Line weights at 300 ppi</h3><ul class="weights">{wt}</ul>
        <h3 class="label" style="margin-top:28px">Type</h3>
        <div class="type-spec">
          <div class="spec-index" aria-label="Index figures in Barlow Condensed SemiBold">A 10 K Q J</div>
          <div class="spec-slab">HEADWATERS</div>
          <div class="spec-micro">— Never known to cease —</div>
        </div>
      </div>
    </div>
    {motif_fig}
  </section>

  <section class="section" id="print" aria-labelledby="print-h">
    <div class="section-head"><p class="eyebrow">Production</p><h2 id="print-h">Ready for the press</h2></div>
    <dl class="specs">
      <div><dt>Format</dt><dd>Poker, 2.5 × 3.5 in, 1/8 in corner radius</dd></div>
      <div><dt>Artwork</dt><dd>Vector SVG at 750 × 1050 (300 ppi); no live type</dd></div>
      <div><dt>Bleed</dt><dd>0.125 in each side (825 × 1125); stock only crosses trim</dd></div>
      <div><dt>Inks</dt><dd>Aquifer, Gill Red, Spring Jade + metallic gold (spot)</dd></div>
      <div><dt>Separations</dt><dd>One black plate per ink, from geometric knockouts</dd></div>
      <div><dt>Box</dt><dd>Deep Hole board, gold foil, blind emboss; seal on red paper</dd></div>
    </dl>
  </section>
</main>
<footer><div class="wrap"><span class="wordmark-sm">HEADWATERS</span> · Playing cards of the San Marcos springs.
Drawn in the spirit of Curtis Jinkins’ Monarchs and Drifters; all artwork is original.</div></footer>

<div class="lb" id="lightbox" hidden role="dialog" aria-modal="true" aria-labelledby="lb-title">
  <div class="lb-stage"><img id="lb-img" alt=""></div>
  <div class="lb-bar">
    <div class="lb-title" id="lb-title"></div>
    <div class="lb-nav">
      <button type="button" id="lb-prev" aria-label="Previous card">Prev</button>
      <button type="button" id="lb-next" aria-label="Next card">Next</button>
      <button type="button" id="lb-close">Close</button>
    </div>
  </div>
</div>
<script>
(() => {{
  const cards = {lightbox_data};
  const lb = document.getElementById('lightbox'), img = document.getElementById('lb-img'),
        title = document.getElementById('lb-title');
  let i = 0, opener = null;
  const show = (k) => {{
    i = (k + cards.length) % cards.length;
    const c = cards[i];
    img.src = 'svg/' + c.stem + '.svg';
    img.alt = c.label + (c.name ? ' — ' + c.name : '');
    title.innerHTML = '';
    title.append(c.label);
    if (c.name) {{ const em = document.createElement('em'); em.textContent = c.name; title.append(em); }}
  }};
  const open = (stem, btn) => {{
    opener = btn; show(Math.max(0, cards.findIndex(c => c.stem === stem)));
    lb.hidden = false; document.body.style.overflow = 'hidden';
    document.getElementById('lb-close').focus();
  }};
  const close = () => {{ lb.hidden = true; document.body.style.overflow = ''; if (opener) opener.focus(); }};
  document.addEventListener('click', (e) => {{
    const b = e.target.closest('.card-btn'); if (b) open(b.dataset.stem, b);
  }});
  document.getElementById('lb-prev').onclick = () => show(i - 1);
  document.getElementById('lb-next').onclick = () => show(i + 1);
  document.getElementById('lb-close').onclick = close;
  lb.addEventListener('click', (e) => {{ if (e.target === lb || e.target.classList.contains('lb-stage')) close(); }});
  document.addEventListener('keydown', (e) => {{
    if (lb.hidden) return;
    if (e.key === 'Escape') close();
    else if (e.key === 'ArrowLeft') show(i - 1);
    else if (e.key === 'ArrowRight') show(i + 1);
  }});
}})();
</script>
'''
    path = os.path.join(OUT, "index.html")
    with open(path, "w") as f:
        f.write(page)
    with open(os.path.join(OUT, "files.json"), "w") as f:
        json.dump(m, f, indent=1)
    return path


if __name__ == "__main__":
    p = build()
    print(p, len(files_manifest()), "files")
