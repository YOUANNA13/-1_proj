# PPE Detection: Reproduction + Live System

We reproduce the results of Elesawy et al. (2026), *Automated multi-class PPE detection in Egyptian construction worksites using YOLO* (Discover Civil Engineering 3:157), then fill its gaps with a live camera system and a web dashboard.

## Teams

| Team | Members |
|---|---|
| Model | Bavly, Youanna |
| Dashboard | Ziad, Shrouk, George |
| Paper | Rodina, Katreen |

## Start here

| File | What it holds |
|---|---|
| [docs/decisions.md](docs/decisions.md) | Every project decision (the official reference) |
| [docs/class_mapping.md](docs/class_mapping.md) | Class IDs, live mapping, violation statuses |
| [docs/metrics.md](docs/metrics.md) | Model and system metrics, and how they are measured |
| [docs/comparison_table.md](docs/comparison_table.md) | Theirs vs Ours, paper inconsistencies, gaps |
| [docs/api_contracts.md](docs/api_contracts.md) | DB tables, WebSocket messages, REST endpoints |
| [runs.csv](runs.csv) | Shared run log: one row per training/eval run |

## Data

Datasets are **not** stored in git. Put them at the repo root:

```
CHV_dataset/CHV_dataset/{images,annotations,data split}/   # CHV benchmark, 1330 images
OriginalDataset/IMG (n).JPG                                 # 173 Egyptian images (unlabelled)
```

Egyptian images come from the paper's repo: https://github.com/elnaqieb/PPE_Detection

## Splits (`splits/`)

| Dataset | train | valid | test | Source |
|---|---|---|---|---|
| CHV | 1064 | 133 | 133 | Official split, copied verbatim. Paths are relative to `CHV_dataset/` |
| Egyptian | 106 | 13 | 14 | `python -I scripts/make_splits.py`, seed 42, 40 near-duplicates left out (`splits/egy_removed_duplicates.txt`). Paths are relative to the repo root |

Egyptian labels: `annotations/egy/` (1394 boxes, reviewed; see `annotations/README.md`).
Build the YOLO folders with `python -I scripts/prepare_yolo_dirs.py` → `datasets/` (git-ignored),
then check them with `python -I scripts/check_dataset.py`.
Training configs: `configs/chv.yaml` (CHV only), `configs/chv_egy.yaml` (CHV + Egyptian), `configs/egy.yaml` (Egyptian only).

## Layout

```
docs/       decisions and contracts
splits/     train/valid/test image lists
scripts/    data scripts
model/      training, evaluation, live pipeline   (Model Team)
backend/    FastAPI + DB + WebSocket              (Dashboard Team)
dashboard/  React frontend                        (Dashboard Team)
```
