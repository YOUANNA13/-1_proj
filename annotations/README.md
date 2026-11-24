# Egyptian image annotations

`egy/IMG (n).txt` — one YOLO label file per image (133 images, decision D-004/D-015).
Format: `class x_center y_center width height`, normalised 0–1, class IDs from `docs/class_mapping.md`.
Coordinates are in the **upright** image frame (EXIF rotation applied; `IMG (164)` rotated 90° CCW,
see `scripts/prepare_yolo_dirs.py`). Always build the training folders with that script.

## How the labels were made (2026-11-24)

1. **Pre-labels:** YOLOv8m trained on CHV (Colab, CHV-val mAP50 0.91) predicted boxes on all images.
2. **Duplicate scenes removed:** 40 near-duplicate images left out (D-015).
3. **Wrong boxes fixed:** helmets on bare heads / caps / head cloths, objects labelled as helmets, wrong colours.
4. **Missed far objects:** every image scanned in overlapping tiles with two extra detectors
   (a PPE model and a COCO YOLOv8x person model); 512 candidate boxes checked one by one on zoomed crops
   → 372 accepted, 140 rejected.
5. **Missing helmet/vest per person:** every person with no helmet or vest box checked by eye;
   73 helmet/vest boxes added, 20 false person boxes removed.
6. **Full pass over all 133 images** with every box drawn: remaining errors fixed by hand
   (wrong/duplicate boxes removed, hidden workers added, one sideways photo rotated).
7. **Checks:** `python -I scripts/check_dataset.py` passes (classes 0–5, valid coordinates,
   every image has a label file, no file in two splits).

## Result

| | images | boxes | person | vest | blue | red | white | yellow |
|---|---|---|---|---|---|---|---|---|
| all | 133 | 1394 | 592 | 415 | 6 | 16 | 111 | 254 |

8 images contain no workers and have empty label files on purpose (background images):
IMG 7, 10, 11, 12, 14, 15, 34, 83.

## Known limits

- Workers only a few pixels tall, where helmet use can't be judged, are not labelled (same rule as CHV).
- Some hand-added boxes for small, partly hidden workers are less tight than model boxes.
- Blue (6) and red (16) helmets are rare in this data; per-class results for them on EGY-test will be noisy.
