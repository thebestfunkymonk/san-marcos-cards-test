"""J♣ render tool (work only): preview art/JC.py and cut the crops I look at.

    .venv/bin/python work/jc/rt.py [tag] [--qa]

writes work/jc/out/<tag>/JC{.png,-188.png,-1500.png,-white.png} plus
face3x.png, top.png, hands.png, paddle.png, small4x.png, and prints the heal
log (face / hand entries and UNRESOLVED) and the §C.2 balance when --qa.
"""
import json
import os
import subprocess
import sys

ROOT = "/home/luke/Projects/design/san-marcos-deck"
sys.path.insert(0, ROOT)
os.chdir(ROOT)

tag = sys.argv[1] if len(sys.argv) > 1 and not sys.argv[1].startswith("-") else "cur"
qa = "--qa" in sys.argv
out = os.path.join(ROOT, "work/jc/out", tag)
os.makedirs(out, exist_ok=True)

cmd = [".venv/bin/python", "tools/preview.py", "art/JC.py", "JC", out] + (["--qa"] if qa else [])
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout[-3000:])
if r.returncode or "PLACEHOLDER" in r.stderr:
    print(r.stderr[-4000:])
svg = os.path.join(out, "JC.svg")
big = os.path.join(out, "JC-2250.png")
subprocess.run(["rsvg-convert", "-w", "2250", svg, "-o", big], check=True)


def crop(src, x0, y0, x1, y1, k, name):
    subprocess.run(["magick", src, "-crop", f"{int((x1 - x0) * k)}x{int((y1 - y0) * k)}+{int(x0 * k)}+{int(y0 * k)}",
                    "+repage", os.path.join(out, name)], check=True)


crop(big, 290, 70, 480, 300, 3, "face3x.png")
crop(os.path.join(out, "JC-1500.png"), 135, 50, 615, 515, 2, "top.png")
crop(big, 190, 340, 600, 515, 3, "hands.png")
crop(big, 420, 55, 612, 300, 3, "paddle.png")
subprocess.run(["magick", os.path.join(out, "JC-188.png"), "-filter", "point", "-resize", "400%",
                os.path.join(out, "small4x.png")], check=True)

# heal log from a direct build
sys.path.insert(0, os.path.join(ROOT, "art"))
import importlib.util  # noqa: E402

spec = importlib.util.spec_from_file_location("jc_mod", os.path.join(ROOT, "art/JC.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sc = mod.figure()
sc.compose()
log = sc.heal_log
print(f"heal log: {len(log)} entries")
by = {}
for e in log:
    by.setdefault((e["action"], e["role"], e.get("layer")), []).append(e)
for k, v in sorted(by.items(), key=lambda kv: -len(kv[1])):
    print(f"  {len(v):3d}  {k}  e.g. at {v[0]['at']} {v[0]['why']} near={v[0].get('near')}")
if qa:
    j = json.load(open(os.path.join(out, "JC-qa.json")))
    print("balance:", j.get("5", {}).get("balance"))
