"""Preview an art module from ANY path, without touching art/, cards/ or build/png/.

Use this for drafts and competing candidates (e.g. three K♠ attempts):

    .venv/bin/python tools/preview.py <module.py> <PIECE_ID> <out_dir> [--qa] [--no-white]

It composes the piece exactly as ``deck.build`` does (clip + 180° copy + frame +
band + pips + indices for courts; indices for aces/jokers), then writes to
<out_dir>:

    <STEM>.svg            the card (Limestone stock)
    <STEM>.png            750 px wide
    <STEM>-188.png        188 px wide (25 % legibility check)
    <STEM>-1500.png       1500 px wide (detail check; crop from this)
    <STEM>-white.png      750 px on white stock (unless --no-white)

With --qa it also runs the machine checks from ``deck.qa`` on the draft and
prints them (and writes <out_dir>/<STEM>-qa.json).
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from deck import build as B  # noqa: E402


def _load_module(path: str, pid: str):
    spec = importlib.util.spec_from_file_location(f"preview_{pid}_{abs(hash(path))}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    spec.loader.exec_module(mod)
    return mod


def _compose(mod, pid: str, stock: str, sandbox: str) -> dict:
    """Run deck.build.build_piece with the draft module, writing into a sandbox."""
    real_root, real_load = B.ROOT, B.load_art
    try:
        B.ROOT = sandbox
        B.load_art = lambda p: mod if p == pid else None
        info = B.build_piece(pid, stock)
    finally:
        B.ROOT, B.load_art = real_root, real_load
    if info.get("error"):
        print(f"[preview] art module raised — rendered as PLACEHOLDER:\n{info['error']}", file=sys.stderr)
    return info


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("module")
    ap.add_argument("pid")
    ap.add_argument("out_dir")
    ap.add_argument("--qa", action="store_true")
    ap.add_argument("--no-white", action="store_true")
    a = ap.parse_args(argv)

    pid = B.normalize(a.pid)[0]
    stem = B.stem(pid)
    out = os.path.abspath(a.out_dir)
    os.makedirs(out, exist_ok=True)
    mod = _load_module(os.path.abspath(a.module), pid)

    with tempfile.TemporaryDirectory(prefix="preview-") as sb:
        info = _compose(mod, pid, "limestone", sb)
        svg = os.path.join(out, f"{stem}.svg")
        shutil.copy(info["svg"], svg)
        shutil.copy(info["png"], os.path.join(out, f"{stem}.png"))
        shutil.copy(info["small"], os.path.join(out, f"{stem}-188.png"))
        subprocess.run(["rsvg-convert", "-w", "1500", svg, "-o", os.path.join(out, f"{stem}-1500.png")], check=True)
        info_white = None
        if not a.no_white:
            info_white = _compose(mod, pid, "white", sb)
            shutil.copy(info_white["png"], os.path.join(out, f"{stem}-white.png"))
        print(f"[preview] {pid}: status={info['status']} -> {out}/{stem}{{.svg,.png,-188.png,-1500.png,-white.png}}")

        if a.qa:
            from deck import qa as Q
            info = dict(info, svg=svg)
            res = Q.check_piece((info, info_white))
            res.pop("_index_region", None)
            json.dump(res, open(os.path.join(out, f"{stem}-qa.json"), "w"), indent=1, default=str)
            if res.get("error"):
                print(res["error"])
            for k, v in res.items():
                if isinstance(v, dict) and "ok" in v:
                    mark = "✓" if v["ok"] is True else ("n/a" if v["ok"] is None else "✗")
                    detail = "; ".join(map(str, v.get("detail", [])))[:300]
                    print(f"  {k:>4} {mark} {detail}")


if __name__ == "__main__":
    main()
