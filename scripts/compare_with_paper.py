"""Print a side-by-side comparison of our runs with the paper (Elesawy et al. 2026).

Reads:  runs.csv              (one row per run x eval split, D-013)
        results/per_class.csv (per-class results)
Usage:  python -I scripts/compare_with_paper.py

New runs (bigger models, optimisations, ...) only need rows in runs.csv:
they show up automatically in section 4 (leaderboard) and section 5 (CHV vs EGY gap).
Standard library only, so it also runs on Colab.
"""
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOL = 0.02  # |ours - paper| <= TOL counts as "reproduced"

# Paper numbers (Tables 5-10). Paper evaluated on an unclear CHV-based set (see docs/comparison_table.md).
PAPER = {
    "yolov8m": dict(precision=0.92, recall=0.85, f1=0.88, map50=0.92, map50_95=0.54, fps=41.32, params_m=25.84, gflops=55.41),
    "yolov8s": dict(precision=0.90, recall=0.85, f1=0.87, map50=0.89, map50_95=0.53, fps=38.61, params_m=68.13, gflops=26.06),
}
PAPER_CLS_V8M = {  # class: (P, R, F1, AP50, AP50-95)
    "person": (0.91, 0.84, 0.87, 0.91, 0.55),
    "vest": (0.92, 0.83, 0.87, 0.90, 0.54),
    "blue_helmet": (0.89, 0.80, 0.84, 0.88, 0.51),
    "red_helmet": (0.98, 0.90, 0.94, 0.96, 0.53),
    "white_helmet": (0.95, 0.85, 0.90, 0.93, 0.55),
    "yellow_helmet": (0.90, 0.88, 0.89, 0.93, 0.59),
}
ACC = [("precision", "Precision"), ("recall", "Recall"), ("f1", "F1"), ("map50", "mAP50"), ("map50_95", "mAP50-95")]
COST = [("params_m", "Params (M)"), ("gflops", "GFLOPs"), ("fps", "FPS")]


def num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def fmt(v, nd=3):
    return "-" if v is None else f"{v:.{nd}f}"


def delta(ours, paper):
    return "-" if ours is None or paper is None else f"{ours - paper:+.3f}"


def verdict(ours, paper):
    if ours is None or paper is None:
        return ""
    d = ours - paper
    return "reproduced" if abs(d) <= TOL else ("ours higher" if d > 0 else "ours lower")


def table(title, header, rows):
    w = [max(len(str(x)) for x in col) for col in zip(header, *rows)]
    line = "+".join("-" * (n + 2) for n in w)
    print(f"\n{title}\n{line}")
    print("|".join(f" {str(h):<{n}} " for h, n in zip(header, w)))
    print(line)
    for r in rows:
        print("|".join(f" {str(c):<{n}} " for c, n in zip(r, w)))
    print(line)


def main():
    runs = list(csv.DictReader(open(ROOT / "runs.csv", newline="", encoding="utf-8")))
    cls_path = ROOT / "results/per_class.csv"
    per_cls = list(csv.DictReader(open(cls_path, newline="", encoding="utf-8"))) if cls_path.exists() else []
    get = {(r["run_id"], r["eval_split"]): r for r in runs}

    def val(run_id, split, key):
        r = get.get((run_id, split))
        return num(r[key]) if r else None

    print("=" * 78)
    print("OURS vs PAPER  (Elesawy et al. 2026, Discover Civil Engineering 3:157)")
    print("A = trained on CHV only | B = trained on CHV + Egyptian | same paper settings")
    print(f"'reproduced' = within +/-{TOL} of the paper. Paper test set is unclear (D-014).")
    print("=" * 78)

    # 1-2. Reproduction per model
    for i, (model, p) in enumerate(PAPER.items(), 1):
        a, b = f"repro_{model}_chv", f"repro_{model}_chv_egy"
        rows = []
        for key, name in ACC:
            bc = val(b, "chv_test", key)
            rows.append([name, fmt(p[key], 2), fmt(val(a, "chv_test", key)), fmt(bc), delta(bc, p[key]),
                         verdict(bc, p[key]), fmt(val(b, "egy_test", key)), fmt(val(b, "all_test", key))])
        for key, name in COST:
            bc = val(b, "chv_test", key)
            if key == "fps":
                note = "not comparable (paper GPU unknown)"
            elif bc and abs(bc - p[key]) / p[key] > 0.10:
                note = "PAPER VALUE WRONG"
            else:
                note = "matches"
            rows.append([name, fmt(p[key], 2), fmt(val(a, "chv_test", key), 2), fmt(bc, 2), "", note, "", ""])
        table(f"{i}. {model.upper()}: reproduction",
              ["Metric", "Paper", "A CHV-test", "B CHV-test", "B - Paper", "Verdict", "B EGY-test", "B All-test"], rows)

    # 3. Per class (paper gives per-class values for YOLOv8m only)
    b = "repro_yolov8m_chv_egy"
    pc = {(r["run_id"], r["eval_split"], r["cls"]): r for r in per_cls}
    rows = []
    for c, (pp, pr, pf, pap, pap95) in PAPER_CLS_V8M.items():
        ch, eg = pc.get((b, "chv_test", c)), pc.get((b, "egy_test", c))
        ap = num(ch["AP50"]) if ch else None
        rows.append([c, fmt(pap, 2), fmt(ap), delta(ap, pap), verdict(ap, pap),
                     fmt(pap95, 2), fmt(num(ch["AP50_95"]) if ch else None),
                     fmt(num(eg["AP50"]) if eg else None) if eg else "no boxes in test"])
    table("3. YOLOV8M per class (B model)",
          ["Class", "Paper AP50", "B CHV AP50", "B - Paper", "Verdict", "Paper AP50-95", "B CHV AP50-95", "B EGY AP50"], rows)

    # 4. Leaderboard: every run in runs.csv, per eval split
    ref = PAPER["yolov8m"]["map50"]
    for split, label in (("chv_test", "CHV-test"), ("egy_test", "EGY-test"), ("all_test", "All-test")):
        rs = sorted((r for r in runs if r["eval_split"] == split), key=lambda r: -(num(r["map50"]) or 0))
        if not rs:
            continue
        rows = [[r["run_id"], r["model"], r["dataset"], fmt(num(r["map50"])), fmt(num(r["map50_95"])),
                 fmt(num(r["f1"])), fmt(num(r["params_m"]), 2), fmt(num(r["gflops"]), 2),
                 delta(num(r["map50"]), ref) if split == "chv_test" else ""] for r in rs]
        table(f"4. Leaderboard on {label} (sorted by mAP50)",
              ["Run", "Model", "Trained on", "mAP50", "mAP50-95", "F1", "Params", "GFLOPs",
               "vs paper best (v8m 0.92)"], rows)

    # 5. Domain gap: CHV-test vs EGY-test for runs evaluated on both (paper reports none)
    rows = []
    for run_id in dict.fromkeys(r["run_id"] for r in runs):
        c, e = val(run_id, "chv_test", "map50"), val(run_id, "egy_test", "map50")
        if c is not None and e is not None:
            rows.append([run_id, fmt(c), fmt(e), f"{e - c:+.3f}"])
    if rows:
        table("5. CHV vs Egyptian gap (mAP50) - not reported in the paper",
              ["Run", "CHV-test", "EGY-test", "EGY - CHV"], rows)

    print("\nNotes:")
    print(" - EGY-test is small (14 images, 179 boxes, 1 blue helmet, 0 red): per-class EGY numbers are noisy.")
    print(" - FPS in runs.csv = full pipeline incl. image loading (I/O bound); see 'notes' column for model-only speed.")
    print(" - Paper inconsistencies: docs/comparison_table.md")


if __name__ == "__main__":
    main()
