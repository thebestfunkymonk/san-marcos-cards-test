"""cand.py <name> <overrides.py> — build QH with module constants overridden (exec'd in QH's namespace),
write <out>/<name>.svg and crops (leaf 6x, leaf 750x4, top 750)."""
import sys, os, subprocess, tempfile, shutil, importlib, importlib.util
sys.path.insert(0, '.')
sys.path.insert(0, 'tools')
name, ov = sys.argv[1], sys.argv[2]
out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cand')
os.makedirs(out, exist_ok=True)
spec = importlib.util.spec_from_file_location(f"qh_cand_{name}", 'art/QH.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
exec(open(ov).read(), mod.__dict__)
import preview as PV
from deck import build as B
with tempfile.TemporaryDirectory() as sb:
    info = PV._compose(mod, 'QH', 'limestone', sb)
    svg = os.path.join(out, f'{name}.svg')
    shutil.copy(info['svg'], svg)
    shutil.copy(info['png'], os.path.join(out, f'{name}.png'))
R = os.path.dirname(os.path.abspath(__file__))
subprocess.run(['python3', f'{R}/grid.py', svg, '520', '150', '90', '165', '5', os.path.join(out, f'{name}_leaf5x.png'), '10'], check=True)
subprocess.run(['magick', os.path.join(out, f'{name}.png'), '-crop', '120x200+490+100', '+repage', '-scale', '300%', os.path.join(out, f'{name}_leaf750x3.png')], check=True)
print('ok', name)
