"""var.py <tag> 'NAME = expr' ... : copy art/KD.py with top-level constants overridden, preview it into work/var/<tag>, crop the left hand."""
import os, re, subprocess, sys
ROOT = '/home/luke/Projects/design/san-marcos-deck'
W = f'{ROOT}/build/review/courts2-KD/work'
tag = sys.argv[1]
src = open(f'{ROOT}/art/KD.py').read()
for ov in sys.argv[2:]:
    name, expr = ov.split('=', 1)
    name = name.strip()
    pat = re.compile(rf'^{re.escape(name)}\s*=.*$', re.M)
    if pat.search(src):
        src = pat.sub(lambda m: f'{name} = {expr.strip()}', src, count=1)
    else:
        src = src.replace('\n\ndef figure', f'\n{name} = {expr.strip()}\n\ndef figure', 1)
os.makedirs(f'{W}/var', exist_ok=True)
mp = f'{W}/var/v_{tag}.py'
open(mp, 'w').write(src)
out = f'{W}/var/{tag}'
subprocess.run([f'{ROOT}/.venv/bin/python', f'{ROOT}/tools/preview.py', mp, 'KD', out, '--no-white'], check=True,
               capture_output=True, cwd=ROOT)
subprocess.run([f'{ROOT}/.venv/bin/python', f'{W}/crops.py', f'{out}/KD.svg', out, '6', 'handL:330,360,450,470'], check=True, cwd=ROOT)
subprocess.run([f'{ROOT}/.venv/bin/python', f'{W}/crops.py', f'{out}/KD.svg', out, '3', 'mid:300,300,500,480'], check=True, cwd=ROOT)
print(out)
