"""Judge wrapper: run tools/preview.py with deck.qa's output dir redirected to scratch."""
import os
import sys

ROOT = "/home/luke/Projects/design/san-marcos-deck"
SCRATCH = os.path.join(ROOT, "work/ks-panel/judge-brief")
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

from deck import qa as Q  # noqa: E402

Q.QA_DIR = os.path.join(SCRATCH, "qa")
os.makedirs(Q.QA_DIR, exist_ok=True)

import preview  # noqa: E402

preview.main(sys.argv[1:])
