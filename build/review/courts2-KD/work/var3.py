"""var3.py <tag> [--crop name:x0,y0,x1,y1@s ...] 'NAME = expr' ... : art/KD.py with overrides appended before figure();
preview into work/var3/<tag>; crops (default hands + keyarm + chest)."""
import os, subprocess, sys
ROOT = '/home/luke/Projects/design/san-marcos-deck'
W = f'{ROOT}/build/review/courts2-KD/work'
tag = sys.argv[1]
crops, ovs = [], []
args = sys.argv[2:]
i = 0
while i < len(args):
    if args[i] == '--crop':
        crops.append(args[i + 1]); i += 2
    else:
        ovs.append(args[i]); i += 1
src = open(f'{ROOT}/art/KD.py').read()
src = src.replace('\n\ndef figure', '\n' + '\n'.join(ovs) + '\n\n\ndef figure', 1)
os.makedirs(f'{W}/var3', exist_ok=True)
mp = f'{W}/var3/v_{tag}.py'
open(mp, 'w').write(src)
out = f'{W}/var3/{tag}'
r = subprocess.run([f'{ROOT}/.venv/bin/python', f'{ROOT}/tools/preview.py', mp, 'KD', out, '--no-white'],
                   capture_output=True, text=True, cwd=ROOT)
if r.returncode:
    print(r.stderr[-3000:]); sys.exit(1)
if 'PLACEHOLDER' in r.stderr:
    print(r.stderr[-3000:]); sys.exit(1)
if not crops:
    crops = ['handL:318,362,428,462@6', 'keyarm:495,395,575,511@6', 'chest:300,280,480,511@3', 'cuffLc:300,440,380,511@6']
by = {}
for c in crops:
    spec, s = c.rsplit('@', 1)
    by.setdefault(s, []).append(spec)
for s, specs in by.items():
    subprocess.run([f'{ROOT}/.venv/bin/python', f'{W}/crops.py', f'{out}/KD.svg', out, s] + specs, check=True, cwd=ROOT)
print(out)
