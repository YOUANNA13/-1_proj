# Metrics

Owner: Paper Team. Decision D-008.

## Model metrics

| Metric | Meaning |
|---|---|
| Precision (P) | Of everything the model detected, the share that was correct |
| Recall (R) | Of all real objects, the share the model found |
| F1 | Harmonic mean of P and R |
| mAP50 | Mean average precision at IoU 0.5 |
| mAP50-95 | Mean AP averaged over IoU 0.50 to 0.95, step 0.05 |
| Per-class AP | AP50 and AP50-95 for each of the 6 classes |
| FPS | Frames processed per second |
| Params | Number of learnable parameters (millions) |
| GFLOPs | Compute per image (billions of operations) |

### How we measure them (the paper does not say, so we fix it here)
- **Detection metrics:** Ultralytics `model.val()` with default settings, imgsz 640, on the test split. P, R and F1 are taken at the confidence that maximises F1, as Ultralytics reports them.
- **Reported per dataset:** CHV-test, EGY-test and both combined (D-003).
- **FPS:** batch 1, imgsz 640, after warm-up, averaged over the whole test set. Always state the GPU name and whether pre/post-processing is included. Report both if possible.
- **Params / GFLOPs:** from Ultralytics `model.info()` at imgsz 640.
- **Live mode:** also report detection metrics with helmet colours merged into one `helmet` class (3-class view).

## System metrics (live pipeline)

| Metric | Definition |
|---|---|
| Latency | Time from the frame's capture timestamp to the alert appearing on the dashboard. Report p50 and p95, in ms. |
| Event | A violation that lasts at least N seconds on the same tracked person. N is fixed by the Model Team before testing. |
| Event Precision | Of the alerts raised, the share that match a real violation |
| Event Recall | Of the real violations, the share that raised an alert |
| Duplicate alerts | Extra alerts raised for a violation that already had one |

### How we measure them
1. Record short scripted clips (2–3 min) with the lab camera: team members walking with and without helmet/vest.
2. Write down the real violation intervals for each clip (ground truth).
3. Run the live system on the clips and compare.

## Safety Index (from the paper, for the dashboard)

- Safety Index = 0.75 × helmet compliance + 0.25 × vest compliance. The weights can be changed per project.
- Tiers: **< 80%** Not Accepted · **80–90%** Needs Enhancement · **90–100%** Accepted.
