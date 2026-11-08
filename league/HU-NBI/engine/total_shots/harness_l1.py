#!/usr/bin/env python3
"""HU-NBI total-shots Lane 1 corrected DEV harness.

Corrections vs shipped run_t_hu.py (prereg PREREG_L1_T_HUNBI):
 (a) M_BAR derived via gate_lib derive_level_prior over scored dev
     seasons (2022/2023-2024/2025, n=588) = 19.042517..., wired into
     model_l1 LevelLayer/TrailingR. Copied 24.9 forbidden.
 (b) True naive trailing-10 baseline: nb_over(naive_total, 40.0, 19.5)
     alone, NOT arm B's blended probabilities.
Base rate kept as shipped: prior-seasons over-19.5 rate per season.
Dev gate: pooled LL beats BOTH baselines AND per-season sign check
(arm LL < each baseline LL in EVERY scored season), via gate_lib.
"""
import csv, json, math, sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from gate_lib import assert_no_sealed_rows, derive_level_prior, log_loss, record_dev_pass
import model_l1
from model_l1 import ShotsRegressionStore, NaiveTracker, BaseRateTracker, LevelLayer, TrailingR, nb_over

DATA = HERE.parents[1] / "data" / "hu_nbi.csv"
SEASONS = ("2021/2022", "2022/2023", "2023/2024", "2024/2025")
SCORED = SEASONS[1:]
LINE = 19.5
LAM = 100.0
CELLS = [(hl, s, k) for hl in (30.0, 60.0, 120.0) for s in (0.5, 1.0) for k in (20.0, 50.0)]
REGISTRY = HERE / "dev_pass_registry_l1.json"
CANDIDATE = "L1-T-HU-NBI"


def load():
    out = []
    with DATA.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["season"] not in SEASONS:
                continue
            if r["total_shots_h"] == "" or r["total_shots_a"] == "":
                continue
            d = date.fromisoformat(r["date"])
            out.append({"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                        "day": d.toordinal(), "home_id": int(r["home_id"]), "away_id": int(r["away_id"]),
                        "home": r["home_team"], "away": r["away_team"],
                        "shots_h": float(r["total_shots_h"]), "shots_a": float(r["total_shots_a"])})
    assert_no_sealed_rows(out, {"2025/2026", "2026/2027"})
    return sorted(out, key=lambda x: (x["day"], x["match_id"]))


def over(mu, r):
    return nb_over(mu, r, LINE)


def pass_arm(rows, arm):
    """Exactly the shipped pass_arm, plus the true-naive probability per row."""
    reg = ShotsRegressionStore(rows, [LAM]); naive = NaiveTracker(); base = BaseRateTracker()
    layer = LevelLayer([CELLS[0]]); trailing = TrailingR(40.0); out = []
    for m in rows:
        eh, ea = reg.predict(m["home_id"], m["away_id"], m["day"], LAM)
        rh, ra = reg.league_mu(m["day"], LAM)
        nh, na = naive.predict(m["home_id"], m["away_id"], rh, ra)
        bh, ba = base.predict(m["day"])
        lt, ln, lb = eh + ea, nh + na, bh + ba
        f = layer.factor(0, m["day"])
        rr = 40.0 if arm in ("A", "B") else trailing.value(m["day"])
        mu = (lt + ln) / 2 * (f if arm == "B" else 1.0)
        p = .5 * over(lt, rr) + .5 * over(ln, rr) if arm != "B" else .5 * over(lt * f, 40.0) + .5 * over(ln * f, 40.0)
        if m["season"] in SCORED:
            out.append({"row": m, "season": m["season"], "y": m["shots_h"] + m["shots_a"], "p": p,
                        "expected": mu, "naive_p": over(ln, 40.0), "naive_total": ln})
        naive.update(m["home_id"], m["away_id"], m["shots_h"], m["shots_a"])
        base.update(m["day"], m["shots_h"], m["shots_a"])
        layer.update(0, m["day"], m["shots_h"] + m["shots_a"], mu)
        trailing.update(m["day"], m["shots_h"] + m["shots_a"])
    return out


def score(xs, key="p"):
    def ll(z):
        return sum(log_loss(x[key], 1.0 if x["y"] > LINE else 0.0) for x in z) / len(z)
    return {"n": len(xs), "ll_19.5": ll(xs),
            "per_season": {s: {"n": len(z), "ll_19.5": ll(z)} for s in SCORED for z in [[x for x in xs if x["season"] == s]]}}


def dev():
    rows = load()
    scored_vals = [x["shots_h"] + x["shots_a"] for x in rows if x["season"] in SCORED]
    mbar = derive_level_prior(scored_vals)
    assert math.isclose(mbar, 19.042517006802722, abs_tol=1e-9), mbar
    model_l1.set_m_bar(mbar)
    allp = {arm: pass_arm(rows, arm) for arm in ("A", "B", "C")}
    # True naive: identical across arms (tracker state arm-independent) - verify.
    ref = [(x["row"]["match_id"], x["naive_p"]) for x in allp["A"]]
    for arm in ("B", "C"):
        assert [(x["row"]["match_id"], x["naive_p"]) for x in allp[arm]] == ref, f"naive differs in {arm}"
    baselines = {}
    # base rate: shipped definition, prior-seasons over rate
    base_xs = []
    for x in allp["A"]:
        prior = [z for z in rows if z["season"] < x["season"]]
        rate = sum(z["shots_h"] + z["shots_a"] > LINE for z in prior) / len(prior)
        base_xs.append({**x, "p": rate})
    baselines["base_rate"] = score(base_xs)
    baselines["naive_trailing_10_true"] = score([{**x, "p": x["naive_p"]} for x in allp["A"]])
    arms = {arm: score(xs) for arm, xs in allp.items()}
    gate = {}
    for arm in ("A", "B", "C"):
        pooled = arms[arm]["ll_19.5"] < baselines["base_rate"]["ll_19.5"] and arms[arm]["ll_19.5"] < baselines["naive_trailing_10_true"]["ll_19.5"]
        sign = all(arms[arm]["per_season"][s]["ll_19.5"] < baselines[b]["per_season"][s]["ll_19.5"]
                   for s in SCORED for b in ("base_rate", "naive_trailing_10_true"))
        gate[arm] = {"pooled_beats_base_rate": arms[arm]["ll_19.5"] < baselines["base_rate"]["ll_19.5"],
                     "pooled_beats_naive_true": arms[arm]["ll_19.5"] < baselines["naive_trailing_10_true"]["ll_19.5"],
                     "per_season_sign_all_seasons_both_baselines": sign, "dev_pass": bool(pooled and sign)}
    out = {"protocol": {"league": "HU-NBI", "candidate": CANDIDATE, "dev_seasons_loaded": list(SEASONS),
                        "scored": list(SCORED),
                        "M_BAR": mbar, "M_BAR_derivation": "derive_level_prior over scored dev seasons 2022/2023-2024/2025, n=588, sum=11197.0",
                        "shipped_M_BAR": 24.9, "primary_line": LINE,
                        "naive_definition": "nb_over(naive_trailing_10_total, 40.0, 19.5) alone"},
           "arms": arms, "baselines": baselines, "gate": gate}
    (HERE / "results_dev_l1.json").write_text(json.dumps(out, indent=2) + "\n")
    with (HERE / "predictions_dev_l1.csv").open("w", newline="", encoding="utf-8") as fh:
        fields = ["match_id", "season", "date", "home_id", "away_id", "arm", "expected", "p_over", "naive_p_true", "actual"]
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader()
        for arm, xs in allp.items():
            for x in xs:
                w.writerow({"match_id": x["row"]["match_id"], "season": x["season"], "date": x["row"]["date"],
                            "home_id": x["row"]["home_id"], "away_id": x["row"]["away_id"], "arm": arm,
                            "expected": x["expected"], "p_over": x["p"], "naive_p_true": x["naive_p"], "actual": x["y"]})
    dev_pass_any = gate["B"]["dev_pass"] or gate["C"]["dev_pass"]
    record_dev_pass(str(REGISTRY), CANDIDATE, dev_pass_any, str(HERE / "results_dev_l1.json"))
    print(json.dumps(out, indent=2))
    return out


if __name__ == "__main__":
    dev()
