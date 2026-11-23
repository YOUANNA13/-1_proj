# Comparison Table: Theirs vs Ours

Owner: Paper Team. The Model Team fills the "Ours" columns from `runs.csv`.

Paper: Elesawy et al., *Automated multi-class PPE detection in Egyptian construction worksites using YOLO*, Discover Civil Engineering (2026) 3:157.
Paper training settings: COCO-pretrained weights, 50 epochs, batch 16, imgsz "640×460", Adam, Google Colab. Hardware for FPS not stated.

## Main table (overall)

`Ours-repro` = paper settings (D-009). `Ours-improved` = our best model. Fill in for CHV-test, EGY-test and combined.

### YOLOv8m

| Metric | Paper | Ours-repro CHV | Ours-repro EGY | Ours-repro All | Ours-improved |
|---|---|---|---|---|---|
| Precision | 0.92 | | | | |
| Recall | 0.85 | | | | |
| F1 | 0.88 | | | | |
| mAP50 | 0.92 | | | | |
| mAP50-95 | 0.54 | | | | |
| FPS | 41.32 (GPU unknown) | | | | |
| Params (M) | 25.84 | | | | |
| GFLOPs | 55.41 | | | | |

### YOLOv8n

| Metric | Paper | Ours-repro CHV | Ours-repro EGY | Ours-repro All | Ours-improved |
|---|---|---|---|---|---|
| Precision | 0.90 | | | | |
| Recall | 0.80 | | | | |
| F1 | not reported (row missing in Table 7) | | | | |
| mAP50 | 0.88 | | | | |
| mAP50-95 | 0.52 | | | | |
| FPS | 59.17 (GPU unknown) | | | | |
| Params (M) | 3.01 | | | | |
| GFLOPs | 6.23 | | | | |

## Per-class table (YOLOv8m)

| Class | Paper P | Paper R | Paper F1 | Paper AP50 | Paper AP50-95 | Ours P | Ours R | Ours F1 | Ours AP50 | Ours AP50-95 |
|---|---|---|---|---|---|---|---|---|---|---|
| person | 0.91 | 0.84 | 0.87 | 0.91 | 0.55 | | | | | |
| vest | 0.92 | 0.83 | 0.87 | 0.90 | 0.54 | | | | | |
| blue_helmet | 0.89 | 0.80 | 0.84 | 0.88 | 0.51 | | | | | |
| red_helmet | 0.98 | 0.90 | 0.94 | 0.96 | 0.53 | | | | | |
| white_helmet | 0.95 | 0.85 | 0.90 | 0.93 | 0.55 | | | | | |
| yellow_helmet | 0.90 | 0.88 | 0.89 | 0.93 | 0.59 | | | | | |

## All paper models, for reference (overall values from Tables 5–10)

| Model | P | R | F1 | mAP50 | mAP50-95 | FPS | Params (M) | GFLOPs |
|---|---|---|---|---|---|---|---|---|
| YOLOv5x | 0.88 | 0.86 | 0.87 | 0.90 | 0.52 | 26.32 | 86.21 | 203.90 |
| YOLOv5l | 0.89 | 0.86 | 0.88 | 0.90 | 0.52 | 52.36 | 20.87* | 47.90* |
| YOLOv5m | 0.91 | 0.86 | 0.88 | 0.90 | 0.52 | 42.02 | 46.14* | 107.70* |
| YOLOv5s | 0.90 | 0.81 | 0.85 | 0.87 | 0.50 | 63.69 | 7.03 | 15.80 |
| YOLOv5n | 0.87 | 0.78 | 0.82 | 0.85 | 0.45 | 84.75 | 1.77 | 4.20 |
| YOLOv5x6 | 0.93 | 0.85 | 0.89 | 0.90 | 0.53 | 21.01 | 140.02 | 208.00 |
| YOLOv5l6 | 0.93 | 0.84 | 0.88 | 0.90 | 0.53 | 32.57 | 76.16 | 110.00 |
| YOLOv5m6 | 0.92 | 0.85 | 0.88 | 0.88 | 0.51 | 46.73 | 35.28 | 49.00 |
| YOLOv5s6 | 0.90 | 0.78 | 0.84 | 0.85 | 0.48 | 63.69 | 12.33 | 16.20 |
| YOLOv5n6 | 0.78 | 0.83 | 0.80 | 0.80 | 0.43 | 87.72 | 3.10 | 4.20 |
| YOLOv8x | 0.91 | 0.86 | 0.88 | 0.91 | 0.54 | 20.37 | 68.13 | 214.55 |
| YOLOv8l | 0.90 | 0.86 | 0.88 | 0.91 | 0.54 | 28.49 | 43.61 | 125.77 |
| YOLOv8m | 0.92 | 0.85 | 0.88 | 0.92 | 0.54 | 41.32 | 25.84 | 55.41 |
| YOLOv8s | 0.90 | 0.85 | 0.87 | 0.89 | 0.53 | 38.61 | 68.13* | 26.06 |
| YOLOv8n | 0.90 | 0.80 | — | 0.88 | 0.52 | 59.17 | 3.01 | 6.23 |

\* Values that look wrong; see below.

## Inconsistencies in the paper

1. **Evaluation set is not consistent.** For `person`, TP+FN should be the same for every model, but it is 394 (v5x), 417 (v5m), 420 (v8m). It matches neither CHV-test (450 person boxes) nor CHV-valid (387). So the paper's numbers cannot be reproduced exactly (D-014).
2. The abstract says the best F1 (0.89) is YOLOv8m; Table 7 gives v8m 0.88 and v5x6 0.89.
3. The abstract says v5x6 is faster than v5l; Table 10 gives 21.01 vs 52.36 FPS, the opposite.
4. Table 10 params: v8s is listed as 68.13M (same as v8x; the official value is about 11.2M). v5l and v5m look swapped (official: v5m about 21.2M, v5l about 46.5M); their GFLOPs look swapped too.
5. The YOLOv8n row is missing from Table 7 (F1).
6. The GPU used for FPS is not stated, so FPS is not directly comparable.
7. Image size is given as "640×460", with originals "1024×1024", but CHV image sizes vary.
8. The paper claims 200 Egyptian images; we have 173, unlabelled. No separate results are given for the Egyptian data.
9. Accuracy is defined in the methods but never reported.
10. Tables 3 and 4 (mAP and speed per model) are Ultralytics' published COCO numbers, not the authors' measurements.

## Gaps we fill (from the paper's own limitations)

- Live camera stream instead of still images.
- Tracking (ByteTrack) for per-person events and no repeated alerts.
- Matching each helmet and vest to its person, instead of counting per image.
- Automated pipeline and web dashboard instead of Excel VBA and Power BI.
- Newer models (e.g. YOLO11).
- Better small-object detection (e.g. larger imgsz).
- Separate results on the Egyptian data.
