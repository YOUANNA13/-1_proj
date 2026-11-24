"""Build the YOLO folder layout Ultralytics expects, without touching the raw data.

Run from the project root (with the project venv):
    .venv/Scripts/python -I scripts/prepare_yolo_dirs.py

Creates (git-ignored):
    datasets/chv/images/{train,val,test}/ppe_XXXX.jpg     hard links to the raw CHV images
    datasets/chv/labels/{train,val,test}/ppe_XXXX.txt     copies of the raw CHV annotations
    datasets/egy/images/{train,val,test}/IMG (n).jpg      Egyptian images, EXIF rotation baked in
    datasets/egy/labels/{train,val,test}/IMG (n).txt      copies of annotations/egy/IMG (n).txt

Which image goes in which split comes only from splits/*.txt (decisions D-001, D-002).

Why bake in EXIF rotation: 19 Egyptian phone photos carry an EXIF orientation tag.
Some tools apply it and some don't, which would put boxes on the wrong spot.
Rotating the pixels once and dropping the tag makes every tool see the same image.
"""
import os
import shutil
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent.parent
SPLITS = ROOT / "splits"
OUT = ROOT / "datasets"
PART = {"train": "train", "valid": "val", "test": "test"}  # split file name -> folder name
# Photos stored sideways with no EXIF tag: rotated 90° counter-clockwise here.
# Their labels in annotations/egy/ are already in the upright frame.
ROTATE_CCW = {"IMG (164)"}


def link_or_copy(src: Path, dst: Path):
    if dst.exists():
        dst.unlink()
    try:
        os.link(src, dst)
    except OSError:
        shutil.copy2(src, dst)


def read_list(name: str):
    return [l.strip() for l in (SPLITS / name).read_text(encoding="utf-8").splitlines() if l.strip()]


def build_chv():
    chv_root = ROOT / "CHV_dataset"  # paths in the official split files are relative to this
    ann_dir = chv_root / "CHV_dataset" / "annotations"
    for part, folder in PART.items():
        img_out = OUT / "chv" / "images" / folder
        lab_out = OUT / "chv" / "labels" / folder
        img_out.mkdir(parents=True, exist_ok=True)
        lab_out.mkdir(parents=True, exist_ok=True)
        files = read_list(f"chv_{part}.txt")
        for rel in files:
            img = chv_root / rel
            link_or_copy(img, img_out / img.name)
            shutil.copy2(ann_dir / (img.stem + ".txt"), lab_out / (img.stem + ".txt"))
        print(f"chv {folder}: {len(files)}")


def build_egy():
    rotated = 0
    ann_dir = ROOT / "annotations" / "egy"  # one label file per image, same name (D-004)
    egy_root = OUT / "egy"
    if egy_root.exists():
        shutil.rmtree(egy_root)  # rebuilt from splits/ every time, so no stale images remain
    for part, folder in PART.items():
        img_out = egy_root / "images" / folder
        lab_out = egy_root / "labels" / folder
        img_out.mkdir(parents=True, exist_ok=True)
        lab_out.mkdir(parents=True, exist_ok=True)
        files = read_list(f"egy_{part}.txt")
        for rel in files:
            src = ROOT / rel
            lab = ann_dir / (src.stem + ".txt")
            if lab.exists():
                shutil.copy2(lab, lab_out / lab.name)
            dst = img_out / (src.stem + ".jpg")
            with Image.open(src) as im:
                if src.stem in ROTATE_CCW:
                    ImageOps.exif_transpose(im).rotate(90, expand=True).save(dst, quality=95)
                    rotated += 1
                    continue
                if im.getexif().get(274, 1) != 1:
                    ImageOps.exif_transpose(im).save(dst, quality=95)
                    rotated += 1
                    continue
            link_or_copy(src, dst)
        print(f"egy {folder}: {len(files)}")
    print(f"egy images with EXIF rotation baked in: {rotated}")


if __name__ == "__main__":
    build_chv()
    build_egy()
