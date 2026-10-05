import sys, os, tempfile, shutil
ROOT = os.getcwd()
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'build/review/corr-verify-AS-1-0/rollback'))
import art.AS as mod
print('loaded', mod.__file__)
from deck import build as B
with tempfile.TemporaryDirectory() as sb:
    real_root, real_load = B.ROOT, B.load_art
    B.ROOT = sb; B.load_art = lambda p: mod if p == 'AS' else None
    info = B.build_piece('AS', 'limestone')
    B.ROOT, B.load_art = real_root, real_load
    shutil.copy(info['svg'], 'build/review/corr-verify-AS-1-0/rollback_AS.svg')
