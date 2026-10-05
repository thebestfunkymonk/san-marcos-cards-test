"""exp.py <tag> [python overrides...] — build KH with module-level overrides into r2/exp/<tag>/:
KH.svg/png/188, heal.json, crops (hands 6x, cuffs 12x, top 750), balance. Prints heal entries near the arms."""
import sys, os, shutil, subprocess, tempfile, warnings, json, hashlib
ROOT = '/home/luke/Projects/design/san-marcos-deck'
sys.path.insert(0, ROOT); sys.path.insert(0, ROOT + '/build/review/courts2-KH/work'); os.chdir(ROOT)
warnings.simplefilter('ignore')
from deck import build as B
from deck import courtkit as K
import numpy as np
tag = sys.argv[1]
import art.KH as KH
import art._kh_parts as KP
import art._kh_hands as KHN
for m in sys.argv[2:]:
    exec(m, {'KH': KH, 'K': K, 'np': np, 'KP': KP, 'KHN': KHN})
out = os.path.join(ROOT, 'build/review/courts2-KH/work/r2/exp', tag)
shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
K.HAND_LOG.clear() if hasattr(K.HAND_LOG, 'clear') else None
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
print('md5', hashlib.md5(open(svg, 'rb').read()).hexdigest())
def crop(name, box, S):
    x0, y0, x1, y1 = box
    png = os.path.join(out, f'_full{S}.png')
    if not os.path.exists(png):
        subprocess.run(['rsvg-convert', '-w', str(int(750 * S)), svg, '-o', png], check=True)
    subprocess.run(['magick', png, '-crop', f'{int((x1-x0)*S)}x{int((y1-y0)*S)}+{int(x0*S)}+{int(y0*S)}', '+repage',
                    os.path.join(out, name + '.png')], check=True)
crop('top', (135, 50, 615, 520), 1)
crop('armL', (139, 350, 300, 511), 4)
crop('armR', (450, 380, 611, 511), 4)
crop('cuffL', (145, 395, 215, 465), 10)
crop('cuffR', (545, 425, 611, 495), 10)
subprocess.run(['magick', os.path.join(out, 'armL.png'), os.path.join(out, 'armR.png'), '-background', '#888', '-splice', '6x0', '+append', os.path.join(out, 'arms.png')])
subprocess.run(['magick', os.path.join(out, 'cuffL.png'), os.path.join(out, 'cuffR.png'), '-background', '#888', '-splice', '6x0', '+append', os.path.join(out, 'cuffs.png')])
near = lambda e, box: box[0] <= e['at'][0] <= box[2] and box[1] <= e['at'][1] <= box[3]
base = json.load(open(ROOT + '/build/review/courts2-KH/work/r2/heal_r2start.json'))
bkey = {(e['action'], e['role'], tuple(round(v) for v in e['at'])) for e in base}
for e in sc.heal_log:
    k = (e['action'], e['role'], tuple(round(v) for v in e['at']))
    flag = '' if k in bkey else 'NEW '
    if e['role'] in ('outline', 'contour', 'fold', 'seam', 'binding', 'wrap', 'finger', 'thumb') or flag:
        print(' ', flag, e['action'], e['role'], [round(v, 1) for v in e['at']], e['why'][:48], e.get('near'))
print('HAND_LOG', K.HAND_LOG)
from bal import balance
print('balance', balance(svg))
