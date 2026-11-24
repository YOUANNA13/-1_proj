# Decision Log

This file is the official record of every project decision.
**Rule:** after kickoff, no team changes a decision on its own. A change needs agreement from all three teams. Add a new entry that points to the decision it replaces; never delete old entries.

Format: `ID | Date | Decision | Why | Owner`

---

## Teams

| Team | Members | Responsibility |
|---|---|---|
| Model Team | Bavly, Youanna | Everything from preprocessing to live testing: splits, annotation, class mapping, training, reproducing the paper, improvements, evaluation, live pipeline (camera → detection → tracking → events) |
| Dashboard Team | Ziad, Shrouk, George | Dashboard, database, REST endpoints, WebSocket messages, statistics and Safety Index |
| Paper Team | Rodina, Katreen | Metrics, Theirs vs Ours table, collecting and comparing results, gaps, this decision log |

### Handoffs

| Handoff | From → To |
|---|---|
| Model results + run-log rows | Model Team → Paper Team |
| Live events / alert messages | Model Team → Dashboard Team |
| Decision log shared with everyone | Paper Team → all teams |

---

## Decisions

### D-001 · 2026-11-23 · CHV keeps its official split
- **Decision:** CHV uses its official 80/10/10 split, unchanged: train 1064 / valid 133 / test 133. Files: `splits/chv_{train,valid,test}.txt` (verbatim copies of `CHV_dataset/CHV_dataset/data split/`). Paths inside are relative to the `CHV_dataset/` folder.
- **Why:** it is the standard CHV benchmark split, it matches the paper's "80% training, 20% testing and validation", and it keeps our results comparable with other work.
- **Owner:** Model Team

### D-002 · 2026-11-23 · Egyptian images split 80/10/10, seed 42 (updated by D-015)
- **Decision:** the Egyptian images are split at random with `seed = 42`, 80/10/10. Files: `splits/egy_{train,valid,test}.txt`, produced by `scripts/make_splits.py` (re-running gives the same lists).
- **Current counts (after D-015):** 133 images → train 106 / valid 13 / test 14. (The first version split all 173 images: 138 / 17 / 18.)
- **Why:** same 80/10/10 layout as CHV. Random because we don't know which site each image came from.
- **Note:** a test set of 14 images is small, so Egyptian test numbers will be noisy. Report this as a limitation.
- **Owner:** Model Team

### D-003 · 2026-11-23 · Results reported per dataset
- **Decision:** every model is evaluated and reported separately on CHV-test, EGY-test and both combined.
- **Why:** the paper does not separate results by dataset; this is one of the gaps we fill.
- **Owner:** Model Team → Paper Team

### D-004 · 2026-11-23 · We annotate the Egyptian images ourselves
- **Decision:** the Egyptian images have no labels. We label them ourselves in YOLO format with the 6 class IDs from D-005. Process: pre-label with a CHV-trained model, then correct by hand, following a one-page annotation guide. Part of each person's work is spot-checked by someone else.
- **Status (2026-11-24): done.** Pre-labels from a CHV-trained YOLOv8m, then a full correction pass: tiled search for far objects with two extra detectors, every candidate checked by eye, missing helmets/vests added per person, and a final pass over all 133 images. 1394 boxes. Labels live in `annotations/egy/` (single source of truth); process and counts in `annotations/README.md`. `scripts/check_dataset.py` passes.
- **Why:** no labels are available.
- **Owner:** Model Team (leads); work split across the team

### D-005 · 2026-11-23 · Class mapping
- **Decision:** training and paper reproduction use 6 classes with fixed IDs: `0 person, 1 vest, 2 blue_helmet, 3 red_helmet, 4 white_helmet, 5 yellow_helmet`. The live system merges IDs 2–5 into `helmet`. Details: `docs/class_mapping.md`.
- **Why:** 6 classes keep us comparable with the paper; the live system doesn't need helmet colour.
- **Owner:** Model Team + Dashboard Team

### D-006 · 2026-11-23 · Violations come from rules, not classes
- **Decision:** there is no `no_helmet` / `no_vest` class. A violation is derived by matching helmets and vests to each tracked person. Statuses: `compliant`, `no_helmet`, `no_vest`, `no_helmet_no_vest`.
- **Why:** the datasets have no "missing PPE" labels.
- **Owner:** Model Team + Dashboard Team

### D-007 · 2026-11-23 · Out of scope for v1
- **Decision:** gloves, safety shoes, masks and glasses are not detected or annotated in v1.
- **Why:** not in either dataset; the paper lists them as future work.
- **Owner:** all teams

### D-008 · 2026-11-23 · Metrics
- **Decision:** model and system metrics, and how they are measured, are fixed in `docs/metrics.md`.
- **Owner:** Paper Team

### D-009 · 2026-11-23 · Models to reproduce
- **Decision:** reproduce YOLOv8m (paper's best) and YOLOv8n (edge option) with the paper's settings: COCO-pretrained weights, 50 epochs, batch 16, imgsz 640, Adam. Improved versions (e.g. YOLO11) come after.
- **Owner:** Model Team

### D-010 · 2026-11-23 · Hardware
- **Decision:** the lab GPU is an NVIDIA GeForce GTX 1650 with 4 GB VRAM. The paper-reproduction runs train on Google Colab (as the paper did) so batch 16 fits. The GTX 1650 is used for live inference, FPS measurement and small experiments. Every FPS number names the GPU it was measured on.
- **Why:** YOLOv8m at batch 16 / imgsz 640 does not fit in 4 GB; a smaller batch would be a deviation from the paper.
- **Owner:** Model Team

### D-011 · 2026-11-23 · Tech stack
- **Decision:** Ultralytics (YOLOv8 / YOLO11) for detection; ByteTrack (`model.track`) for tracking; OpenCV for the camera; FastAPI for the backend; SQLite (PostgreSQL later if needed); React + Vite + Recharts for the dashboard; one GitHub repo with `model/`, `backend/`, `dashboard/`, `docs/`.
- **Owner:** all teams

### D-012 · 2026-11-23 · Contracts between the pipeline and the dashboard
- **Decision:** the live pipeline (Model Team) sends events to `POST /api/ingest/events`; the backend (Dashboard Team) stores them and pushes them over WebSocket. Tables, messages and endpoints: `docs/api_contracts.md`. Times are ISO-8601 UTC; boxes are pixel `[x1, y1, x2, y2]`; class names are exactly as in `docs/class_mapping.md`.
- **Owner:** Dashboard Team (owns the contract) + Model Team

### D-013 · 2026-11-23 · Shared run log
- **Decision:** every training or evaluation run gets one row in `runs.csv` at the repo root, including the git commit and seed.
- **Owner:** all teams (each team logs its own runs)

### D-015 · 2026-11-23 · Near-duplicate Egyptian images removed
- **Decision:** 40 of the 173 Egyptian images are near-duplicates (burst shots of the same scene) and are left out of the dataset; one image per scene is kept, so 133 remain. The list (removed → kept) is in `splits/egy_removed_duplicates.txt`. The raw files are not deleted.
- **Why:** with a random split, 10 of the 18 test images had a copy in train/val, which would make Egyptian test results look better than they are.
- **How found:** perceptual hashes (aHash/dHash), every group checked by eye. After removal, no pair of remaining images is close.
- **Owner:** Model Team

### D-016 · 2026-11-23 · Orange helmets are labelled `red_helmet`
- **Decision:** orange helmets (common on Egyptian sites, no class of their own) are labelled `red_helmet` (ID 3).
- **Why:** red is the closest of the 4 colours, and keeps the 6 class IDs unchanged.
- **Owner:** Model Team

### D-014 · 2026-11-23 · Known limitation: reproduction will not be exact
- **Decision:** we state openly that the paper's numbers cannot be reproduced exactly, because its evaluation set is unclear (see `docs/comparison_table.md`, "Inconsistencies in the paper").
- **Owner:** Paper Team
