"""Kickoff split for the Egyptian images: 80% train / 10% valid / 10% test, fixed seed.
Same 80/10/10 layout as the official CHV split.
Near-duplicate images listed in splits/egy_removed_duplicates.txt are left out (D-015).

Run from the project root:
    python -I scripts/make_splits.py

Writes splits/<dataset>_{train,valid,test}.txt with one
image path per line, relative to the project root. Re-running with the same
seed and the same image folders gives exactly the same files.
"""
import random
import re
import sys
from pathlib import Path

SEED = 42
TRAIN_RATIO = 0.8
VALID_RATIO = 0.1  # the rest (~10%) is test
ROOT = Path(__file__).resolve().parent.parent

# CHV is NOT split here: it keeps its official 80/10/10 split
# (1064/133/133) in CHV_dataset/CHV_dataset/data split/.
DATASETS = {
    "egy": ROOT / "OriginalDataset",
}
IMG_EXT = {".jpg", ".jpeg", ".png"}


def natural_key(p: Path):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", p.name)]


def removed_duplicates(name: str, out_dir: Path):
    """Image names listed on the left of '->' in splits/<name>_removed_duplicates.txt (D-015)."""
    f = out_dir / f"{name}_removed_duplicates.txt"
    if not f.exists():
        return set()
    lines = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")]
    return {l.split("->")[0].strip() for l in lines}


def split(name: str, folder: Path, out_dir: Path):
    skip = removed_duplicates(name, out_dir)
    images = sorted(
        (p for p in folder.iterdir() if p.suffix.lower() in IMG_EXT and p.name not in skip),
        key=natural_key,
    )
    if skip:
        print(f"{name}: skipped {len(skip)} near-duplicate images")
    rng = random.Random(SEED)
    shuffled = images[:]
    rng.shuffle(shuffled)
    n_train = round(len(shuffled) * TRAIN_RATIO)
    n_valid = round(len(shuffled) * VALID_RATIO)
    parts = {
        "train": sorted(shuffled[:n_train], key=natural_key),
        "valid": sorted(shuffled[n_train:n_train + n_valid], key=natural_key),
        "test": sorted(shuffled[n_train + n_valid:], key=natural_key),
    }
    for part, files in parts.items():
        lines = [p.relative_to(ROOT).as_posix() for p in files]
        (out_dir / f"{name}_{part}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{name}: total={len(images)} " + " ".join(f"{k}={len(v)}" for k, v in parts.items()))


def main():
    out_dir = ROOT / "splits"
    out_dir.mkdir(exist_ok=True)
    for name, folder in DATASETS.items():
        if not folder.is_dir():
            sys.exit(f"missing folder: {folder}")
        split(name, folder, out_dir)


if __name__ == "__main__":
    main()
