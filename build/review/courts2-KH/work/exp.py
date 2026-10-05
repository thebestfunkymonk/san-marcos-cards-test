"""exp.py <tag> [python overrides...] — build KH with module-level overrides, render crops.
Crops (card px boxes) rendered at scale S."""
import sys, os, shutil, subprocess, tempfile, warnings, importlib, json
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); os.chdir(ROOT)
warnings.simplefilter('ignore')
from deck import build as B
from deck import courtkit as K
tag = sys.argv[1]
mods = sys.argv[2:]
import art.KH as KH
for m in mods:
    exec(m, {'KH': KH, 'K': K, 'np': __import__('numpy')})
out = os.path.join(ROOT, 'build/review/courts2-KH/work/exp', tag)
os.makedirs(out, exist_ok=True)
sc = KH.figure(); _lay = sc.layers(); KH.build = lambda: _lay
json.dump(sc.heal_log, open(os.path.join(out, 'heal.json'), 'w'), default=str, indent=0)
with tempfile.TemporaryDirectory() as sb:
    rr, rl = B.ROOT, B.load_art
    B.ROOT = sb; B.load_art = lambda p: KH if p == 'KH' else None
    info = B.build_piece('KH', 'limestone')
    B.ROOT, B.load_art = rr, rl
    shutil.copy(info['svg'], os.path.join(out, 'KH.svg'))
    shutil.copy(info['png'], os.path.join(out, 'KH.png'))
    shutil.copy(info['small'], os.path.join(out, 'KH-188.png'))
svg = os.path.join(out, 'KH.svg')
def crop(name, box, S):
    x0, y0, x1, y1 = box
    png = os.path.join(out, f'_full{S}.png')
    if not os.path.exists(png):
        subprocess.run(['rsvg-convert', '-w', str(int(750 * S)), svg, '-o', png], check=True)
    subprocess.run(['magick', png, '-crop', f'{int((x1-x0)*S)}x{int((y1-y0)*S)}+{int(x0*S)}+{int(y0*S)}', '+repage',
                    os.path.join(out, name + '.png')], check=True)
crop('top', (135, 50, 615, 520), 1)
crop('hL', (170, 340, 290, 460), 6)
crop('hR', (470, 400, 600, 520), 6)
crop('crown', (280, 90, 380, 160), 6)
subprocess.run(['magick', os.path.join(out, 'hL.png'), os.path.join(out, 'hR.png'), '+append', os.path.join(out, 'hands.png')])
hl = [e for e in sc.heal_log]
near = lambda e, box: box[0] <= e['at'][0] <= box[2] and box[1] <= e['at'][1] <= box[3]
for nm, box in (('L', (170, 340, 290, 460)), ('R', (470, 400, 600, 520))):
    print(nm, [(e['action'], e['role'], [round(v, 1) for v in e['at']], e['why'][:40], e.get('near')) for e in hl if near(e, box)])
print('HAND_LOG', K.HAND_LOG)
