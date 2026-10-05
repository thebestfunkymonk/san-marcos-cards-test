"""var2.py <tag> [crops...] -- 'OLD=>NEW' ... : copy art/KD.py with literal replacements (each must match),
preview into work/var/<tag> (no white), crops: name:x0,y0,x1,y1@scale."""
import os, subprocess, sys
ROOT = '/home/luke/Projects/design/san-marcos-deck'
W = f'{ROOT}/build/review/courts2-KD/work'
args = sys.argv[1:]
tag = args.pop(0)
crops = []
while args and args[0] != '--':
    crops.append(args.pop(0))
if args:
    args.pop(0)
src = open(f'{ROOT}/art/KD.py').read()
for rep in args:
    old, new = rep.split('=>', 1)
    assert old in src, f'no match: {old!r}'
    src = src.replace(old, new, 1)
mp = f'{W}/var/v_{tag}.py'
open(mp, 'w').write(src)
out = f'{W}/var/{tag}'
r = subprocess.run([f'{ROOT}/.venv/bin/python', f'{ROOT}/tools/preview.py', mp, 'KD', out, '--no-white'],
                   capture_output=True, cwd=ROOT, text=True)
if r.returncode:
    print(r.stdout[-2000:], r.stderr[-3000:]); sys.exit(1)
for c in crops:
    spec, s = c.rsplit('@', 1)
    subprocess.run([f'{ROOT}/.venv/bin/python', f'{W}/crops.py', f'{out}/KD.svg', out, s, spec], check=True, cwd=ROOT)
print(out)
