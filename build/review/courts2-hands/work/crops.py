"""Render hand crops (3x) for before/after: python crops.py <cards_dir> <out_dir> [IDs]"""
import os, subprocess, sys
HANDS = {  # id: [(name, cx, cy)] card px centres of each hand crop (round 2 positions)
    "KS": [("L", 290, 450), ("R", 520, 425)], "QS": [("L", 310, 430), ("R", 525, 455)],
    "JS": [("L", 285, 430), ("R", 540, 185)], "KH": [("L", 222, 400), ("R", 540, 455)],
    "QH": [("L", 325, 435), ("R", 530, 440)], "JH": [("L", 250, 440), ("R", 540, 275)],
    "KC": [("L", 292, 445), ("R", 525, 420)], "QC": [("L", 305, 420), ("R", 525, 440)],
    "JC": [("L", 280, 450), ("R", 530, 415)], "KD": [("L", 382, 410), ("R", 530, 400)],
    "QD": [("L", 225, 445), ("R", 545, 420)], "JD": [("L", 255, 470), ("R", 460, 400)],
}
S = 130  # crop size in card px
def main():
    src, out = sys.argv[1], sys.argv[2]
    ids = sys.argv[3:] or list(HANDS)
    os.makedirs(out, exist_ok=True)
    for pid in ids:
        big = os.path.join(out, f"{pid}_3x.png")
        subprocess.run(["rsvg-convert", "-w", "2250", os.path.join(src, f"{pid}.svg"), "-o", big], check=True)
        for nm, cx, cy in HANDS[pid]:
            x0, y0 = int((cx - S / 2) * 3), int((cy - S / 2) * 3)
            subprocess.run(["magick", big, "-crop", f"{S*3}x{S*3}+{x0}+{y0}", "+repage",
                            os.path.join(out, f"{pid}_{nm}.png")], check=True)
            x0, y0 = int(cx - S / 2), int(cy - S / 2)
        subprocess.run(["rsvg-convert", "-w", "750", os.path.join(src, f"{pid}.svg"), "-o",
                        os.path.join(out, f"{pid}_1x.png")], check=True)
        os.remove(big)
if __name__ == "__main__":
    main()
