"""Sanity checks before training on CHV + Egyptian data. Exits non-zero on any problem.

Run from the project root after scripts/prepare_yolo_dirs.py:
    python -I scripts/check_dataset.py
"""
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
D = ROOT / "datasets"
problems = []
counts = {}

for ds in ("chv", "egy"):
    for part in ("train", "val", "test"):
        imgs = sorted((D / ds / "images" / part).glob("*.jpg"))
        labs = sorted((D / ds / "labels" / part).glob("*.txt"))
        ims, lbs = {p.stem for p in imgs}, {p.stem for p in labs}
        if ims != lbs:
            problems.append(f"{ds}/{part}: images without label {sorted(ims - lbs)[:5]}, labels without image {sorted(lbs - ims)[:5]}")
        cls = Counter()
        empty = 0
        for lab in labs:
            lines = [l for l in lab.read_text().splitlines() if l.strip()]
            if not lines:
                empty += 1
            for n, l in enumerate(lines):
                f = l.split()
                try:
                    c, v = int(f[0]), [float(x) for x in f[1:]]
                except ValueError:
                    problems.append(f"{lab}: line {n} not numeric"); continue
                if len(f) != 5 or not 0 <= c <= 5:
                    problems.append(f"{lab}: line {n} bad class/columns: {l}")
                elif not all(0 <= x <= 1 for x in v) or v[2] <= 0 or v[3] <= 0:
                    problems.append(f"{lab}: line {n} coords out of range: {l}")
                cls[c] += 1
        for p in imgs:
            try:
                with Image.open(p) as im:
                    im.verify()
            except Exception as e:
                problems.append(f"{p}: unreadable ({e})")
        counts[f"{ds}/{part}"] = (len(imgs), empty, dict(sorted(cls.items())))

# no image may appear in two splits, and the two datasets must not share file names
seen = {}
for p in D.glob("*/images/*/*.jpg"):
    key = p.name.lower()
    if key in seen:
        problems.append(f"duplicate file name: {p} and {seen[key]}")
    seen[key] = p

for k, (n, empty, cls) in counts.items():
    print(f"{k:10s} images={n:5d} empty_labels={empty:3d} boxes={sum(cls.values()):5d} per_class={cls}")
if problems:
    print(f"\n{len(problems)} PROBLEM(S):"); print("\n".join(problems[:50])); sys.exit(1)
print("\nAll checks passed.")
