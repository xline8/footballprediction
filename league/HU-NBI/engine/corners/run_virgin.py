"""HU-NBI corners VIRGIN read — 2025/2026, read ONCE (prereg).

Coordinator-written Phase C runner. Fit on built rows from seasons
2021/2022–2024/2025 only (fit_params' own train filter), predict the
virgin season 2025/2026 with the copied core unchanged. Feature state is
strictly pre-date by the FeatureBuilder/attach_naive construction.
Arms: gate_zero + plain (the two dev-passing arms)."""
import csv, json, math
from datetime import date
from pathlib import Path
import core
from core import FeatureBuilder, attach_naive, fit_params, model_prediction, baseline_prediction, over_prob

HERE = Path(__file__).resolve().parent
DATA = HERE.parents[1] / "data" / "hu_nbi.csv"
LINE = 9.5
VIRGIN = "2025/2026"
FIT_SEASONS = {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}


def load_all(path):
    out = []
    with open(path, newline="", encoding="utf-8") as fh:
        for raw in csv.DictReader(fh):
            if raw["season"] not in FIT_SEASONS | {VIRGIN}:
                continue
            if raw["corners_h"] == "" or raw["corners_a"] == "":
                continue
            out.append({
                "match_id": raw["match_id"], "season": raw["season"],
                "date": date.fromisoformat(raw["date"]),
                "home_id": raw["home_id"], "away_id": raw["away_id"],
                "home": raw["home_team"], "away": raw["away_team"],
                "ch": int(float(raw["corners_h"])), "ca": int(float(raw["corners_a"])),
                "sh": core.num(raw["total_shots_h"]), "sa": core.num(raw["total_shots_a"]),
                "poss_h": core.num(raw["possession_h"]), "poss_a": core.num(raw["possession_a"]),
                "bc_h": core.num(raw["big_chances_h"]), "bc_a": core.num(raw["big_chances_a"]),
                "bt_h": core.num(raw["box_touches_h"]), "bt_a": core.num(raw["box_touches_a"]),
            })
    return sorted(out, key=lambda r: (r["date"], r["match_id"]))


def ll(p, y):
    return -(y * math.log(max(p, 1e-12)) + (1 - y) * math.log(max(1 - p, 1e-12)))


def main():
    rows = attach_naive(FeatureBuilder(load_all(DATA)).build())
    train = [r for r in rows if r["season"] in FIT_SEASONS]
    target = [r for r in rows if r["season"] == VIRGIN]
    assert len(target) == 198, len(target)
    out = {"league": "HU-NBI", "market": "corners", "virgin_season": VIRGIN,
           "primary_line": LINE, "arms": {}, "baselines": {}}
    pred_dir = HERE.parents[1] / "predictions"
    pred_dir.mkdir(exist_ok=True)
    for arm in ("gate_zero", "plain"):
        params = fit_params(train, arm)
        pairs = [(r, over_prob(*model_prediction(r, params, arm), LINE)) for r in target]
        n = len(pairs)
        mean_p = sum(p for _, p in pairs) / n
        actual_rate = sum(int(r["y"] > LINE) for r, _ in pairs) / n
        out["arms"][arm] = {
            "n": n, "ll_9.5": sum(ll(p, int(r["y"] > LINE)) for r, p in pairs) / n,
            "mean_p": mean_p, "actual_rate": actual_rate,
            "calibration_breach_pp": (actual_rate - mean_p) * 100.0,
            "calibration_se_pp": math.sqrt(actual_rate * (1 - actual_rate) / n) * 100.0,
            "params": params,
            "beta_active_rows": sum(1 for r, _ in pairs if r.get("z_poss") is not None),
        }
        with (pred_dir / f"corners_virgin_{arm}.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=["match_id", "season", "date", "home_id", "away_id", "expected", "p_over", "actual"])
            w.writeheader()
            for r, p in pairs:
                mu, _ = model_prediction(r, params, arm)
                w.writerow({"match_id": r["match_id"], "season": r["season"], "date": r["date"].isoformat(),
                            "home_id": r["home_id"], "away_id": r["away_id"], "expected": mu,
                            "p_over": p, "actual": r["y"]})
    for name, kind in (("base_rate", "league_base_rate"), ("naive_trailing_10", "naive_trailing_10")):
        pairs = [(r, over_prob(*baseline_prediction(r, kind), LINE)) for r in target]
        out["baselines"][name] = {"n": len(pairs),
                                  "ll_9.5": sum(ll(p, int(r["y"] > LINE)) for r, p in pairs) / len(pairs)}
    (HERE / "results_virgin.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
