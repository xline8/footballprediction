"""Data loading, walk-forward evaluation, virgin metrics, and outputs
for G-SG (see prereg/PREREG_G_BY.md).

Engine: FI reference dc.py carried over verbatim (sweep
optimiser, 14 sweeps, damping 0.7, +0.25 smoothing, home init 0.28,
MAXG = 10, rho grid, decay HL = 270 days). Arms: gate_zero, shrink
(FI arms.py SHRINK mechanics only — the X2 arm is NOT ported: X2
was dropped for this league pre-fitting, EDA F4). Baselines:
climatology (FI harness) and naive trailing-10 (IL precedent:
per-team trailing-10 goals-for means, independent Poissons, no
home advantage).

Dev harness must not read 2025/2026 or 2026/2027 rows. The virgin function is
called once, only if Gate Zero passes the dev gate; if Gate Zero
fails dev, variants are moot and the virgin is NOT read. Set
SG_DEV_ONLY=1 to run dev only (no virgin read).
"""
import csv, json, math, os
from collections import deque
from datetime import date
from pathlib import Path

import numpy as np
from scipy.stats import poisson

from dc import DC
from arms import adjusted_lambdas, match_counts

ROOT = Path(__file__).resolve().parents[2]
SE = ROOT / "data" / "sg_matches.csv"
OUT = Path(__file__).resolve().parent

DEV_SEASONS = ("2022", "2023", "2024/2025")
VIRGIN_SEASON = "2025/2026"
ARMS = ("gate_zero", "shrink")


def load(path, allowed=None):
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if allowed is not None and r["season"] not in allowed:
                continue
            rows.append({"match_id": r["match_id"], "season": r["season"],
                         "date": date.fromisoformat(r["date"]),
                         "hi": int(r["home_team_id"]), "ai": int(r["away_team_id"]),
                         "home": r["home_team"], "away": r["away_team"],
                         "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                         "xgh": None, "xga": None})  # no xG in this feed: X1 goals-only fallback
    return sorted(rows, key=lambda r: (r["date"], r["match_id"]))


def _fit_predict(train, target, arm):
    cutoff = min(r["date"] for r in target)
    prior = [r for r in train if r["date"] < cutoff]
    model = DC().fit(prior, cutoff)
    movers = set()
    mult = {}  # no X2 arm in this league (dropped pre-fitting, EDA F4)
    return model, movers, mult, match_counts(prior)


def _scores(rows, probs):
    ll = rps = oull = 0.0
    for r, p in zip(rows, probs):
        y = (1, 0, 0) if r["yh"] > r["ya"] else ((0, 1, 0) if r["yh"] == r["ya"] else (0, 0, 1))
        pp = [p["ph"], p["pd"], p["pa"]]
        ll -= math.log(max(pp[y.index(1)], 1e-12))
        rps += 0.5 * ((pp[0] - y[0]) ** 2 + (pp[0] + pp[1] - y[0] - y[1]) ** 2)
        over = int(r["yh"] + r["ya"] > 2.5)
        oull -= math.log(max(p["over25"] if over else 1 - p["over25"], 1e-12))
    n = len(rows)
    return {"n": n, "ll_1x2": ll / n, "rps": rps / n, "oull_2_5": oull / n}


def _clim(train):
    n = len(train)
    hw = sum(r["yh"] > r["ya"] for r in train) / n
    dr = sum(r["yh"] == r["ya"] for r in train) / n
    return [hw, dr, 1 - hw - dr], sum(r["yh"] + r["ya"] > 2.5 for r in train) / n


class Trailing10:
    """Per-team trailing-10 goals-for means (matches strictly before
    the scored match, chronological by date). IL precedent."""

    def __init__(self, league_mean):
        self.hist = {}
        self.league_mean = league_mean

    def feed(self, rows):
        for r in rows:
            self.hist.setdefault(r["hi"], deque(maxlen=10)).append(float(r["yh"]))
            self.hist.setdefault(r["ai"], deque(maxlen=10)).append(float(r["ya"]))

    def _probs(self, lh, la):
        ks = np.arange(11)
        m = np.outer(poisson.pmf(ks, lh), poisson.pmf(ks, la))
        ph = float(np.tril(m, -1).sum())
        pd = float(np.trace(m))
        pa = float(np.triu(m, 1).sum())
        tot = ks[:, None] + ks[None, :]
        return {"ph": ph, "pd": pd, "pa": pa, "over25": float(m[tot > 2.5].sum())}

    def rows_for(self, target):
        rows = []
        for r in target:
            mh = self.hist.get(r["hi"], [])
            ma = self.hist.get(r["ai"], [])
            lh = float(np.mean(mh)) if len(mh) else self.league_mean
            la = float(np.mean(ma)) if len(ma) else self.league_mean
            p = self._probs(lh, la)
            rows.append({"match_id": r["match_id"], **p, "yh": r["yh"], "ya": r["ya"]})
            self.hist.setdefault(r["hi"], deque(maxlen=10)).append(float(r["yh"]))
            self.hist.setdefault(r["ai"], deque(maxlen=10)).append(float(r["ya"]))
        return rows


def _model_probs(model, target, arm, mult, counts):
    probs = []
    for r in target:
        lh, la = adjusted_lambdas(model, r["hi"], r["ai"], arm, set(), mult, counts)
        p = model.probs(lh, la)
        p.update({"lh": lh, "la": la})
        probs.append(p)
    return probs


def run_dev():
    rows = load(SE, {"2021", "2022", "2023", "2024/2025"})
    result = []
    gate = {}
    warmup = [r for r in rows if r["season"] == "2021"]
    league_mean = (sum(r["yh"] + r["ya"] for r in warmup) / (2 * len(warmup)))
    t10 = Trailing10(league_mean)
    t10.feed(warmup)
    pooled_rows = {"model": {}, "clim": [], "naive": []}
    for arm in ARMS:
        pooled_rows["model"][arm] = []
    for season in DEV_SEASONS:
        target = [r for r in rows if r["season"] == season]
        train = [r for r in rows if r["date"] < min(x["date"] for x in target)]
        # baselines: once per season (arm-independent)
        cp, co = _clim(train)
        cprobs = [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target]
        met = _scores(target, cprobs)
        met.update({"arm": "gate_zero", "season": season, "kind": "climatology"})
        result.append(met)
        pooled_rows["clim"] += list(zip(target, cprobs))
        nprobs = [{k: v for k, v in nr.items() if k in ("ph", "pd", "pa", "over25")}
                  for nr in t10.rows_for(target)]
        met = _scores(target, nprobs)
        met.update({"arm": "gate_zero", "season": season, "kind": "naive_trailing_10"})
        result.append(met)
        pooled_rows["naive"] += list(zip(target, nprobs))
        for arm in ARMS:
            model, movers, mult, counts = _fit_predict(train, target, arm)
            probs = _model_probs(model, target, arm, mult, counts)
            met = _scores(target, probs)
            met.update({"arm": arm, "season": season, "kind": "model"})
            result.append(met)
            pooled_rows["model"][arm] += list(zip(target, probs))
    pooled = {}
    for arm in ARMS:
        met = _scores([x[0] for x in pooled_rows["model"][arm]], [x[1] for x in pooled_rows["model"][arm]])
        met.update({"arm": arm, "season": "pooled", "kind": "model"})
        result.append(met)
        pooled[arm] = met
    met = _scores([x[0] for x in pooled_rows["clim"]], [x[1] for x in pooled_rows["clim"]])
    met.update({"arm": "gate_zero", "season": "pooled", "kind": "climatology"})
    result.append(met)
    pooled_clim = met
    met = _scores([x[0] for x in pooled_rows["naive"]], [x[1] for x in pooled_rows["naive"]])
    met.update({"arm": "gate_zero", "season": "pooled", "kind": "naive_trailing_10"})
    result.append(met)
    pooled_naive = met
    # Dev gate: pooled 1X2 LL, RPS and OU2.5 LL must beat BOTH baselines.
    for arm in ARMS:
        m = pooled[arm]
        gate[arm] = bool(m["ll_1x2"] < pooled_clim["ll_1x2"] and m["ll_1x2"] < pooled_naive["ll_1x2"]
                         and m["rps"] < pooled_clim["rps"] and m["rps"] < pooled_naive["rps"]
                         and m["oull_2_5"] < pooled_clim["oull_2_5"] and m["oull_2_5"] < pooled_naive["oull_2_5"])
    _write_dev(result, gate)
    _print_table(result, "dev")
    print("dev gate:", gate)
    return result, gate


def _write_dev(result, gate):
    (OUT / "results_dev.json").write_text(json.dumps({"rows": result, "gate": gate}, indent=2) + "\n")
    fields = ["arm", "season", "kind", "n", "ll_1x2", "rps", "oull_2_5"]
    with open(OUT / "results_dev.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows({k: r.get(k) for k in fields} for r in result)


def virgin_metrics(dev_gate, arms=None):
    """Read the virgin ONCE. Only for dev-passing arms. Call only if
    Gate Zero passed the dev gate (checked by the caller)."""
    arms = arms or [a for a in ARMS if dev_gate.get(a)]
    rows = load(SE, {"2021", "2022", "2023", "2024/2025", VIRGIN_SEASON})
    train = [r for r in rows if r["season"] != VIRGIN_SEASON]
    target = [r for r in rows if r["season"] == VIRGIN_SEASON]
    cp, co = _clim(train)
    clim_met = _scores(target, [{"ph": cp[0], "pd": cp[1], "pa": cp[2], "over25": co} for _ in target])
    league_mean = sum(r["yh"] + r["ya"] for r in train) / (2 * len(train))
    t10v = Trailing10(league_mean)
    t10v.feed(train)
    naive_met = _scores(target, t10v.rows_for(target))
    result = {"climatology": clim_met, "naive_trailing_10": naive_met, "arms": {}}
    # per-season dev sign check for the variant (leg iii), from results_dev.json
    dev = json.loads((OUT / "results_dev.json").read_text())
    per_season = {}
    for r in dev["rows"]:
        if r["kind"] == "model":
            per_season.setdefault(r["arm"], {})[r["season"]] = r["ll_1x2"]
    fitted = None
    for arm in arms:
        model, movers, mult, counts = _fit_predict(train, target, arm)
        probs = _model_probs(model, target, arm, mult, counts)
        met = _scores(target, probs)

        def se(vals):
            m = sum(vals) / len(vals)
            return (sum((x - m) ** 2 for x in vals) / (len(vals) - 1)) ** 0.5 / math.sqrt(len(vals))

        cal_hw = sum(p["ph"] for p in probs) / len(probs) - sum(r["yh"] > r["ya"] for r in target) / len(target)
        cal_ou = sum(p["over25"] for p in probs) / len(probs) - sum(r["yh"] + r["ya"] > 2.5 for r in target) / len(target)
        se_hw = se([p["ph"] - (r["yh"] > r["ya"]) for p, r in zip(probs, target)])
        se_ou = se([p["over25"] - (r["yh"] + r["ya"] > 2.5) for p, r in zip(probs, target)])
        entry = {"metrics": met,
                 "calibration": {
                     "home_win_diff_pp": cal_hw * 100, "home_win_se_pp": se_hw * 100,
                     "over25_diff_pp": cal_ou * 100, "over25_se_pp": se_ou * 100},
                 "n": len(target)}
        if arm in ("shrink",):
            entry["sign_check_seasons"] = sum(
                1 for s in DEV_SEASONS if per_season[arm][s] <= per_season["gate_zero"][s])
        result["arms"][arm] = entry
        if arm == "gate_zero":
            fitted = model
        # per-match virgin rows for the verdict / predictions
        with open(OUT / f"virgin_rows_{arm}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["match_id", "ph", "pd", "pa", "over25", "lh", "la", "yh", "ya"])
            w.writeheader()
            w.writerows({"match_id": r["match_id"], "ph": p["ph"], "pd": p["pd"], "pa": p["pa"],
                         "over25": p["over25"], "lh": p["lh"], "la": p["la"], "yh": r["yh"], "ya": r["ya"]}
                        for r, p in zip(target, probs))
    (OUT / "results_virgin.json").write_text(json.dumps(result, indent=2) + "\n")
    if fitted is not None:
        (OUT / "fitted_params_virgin.json").write_text(json.dumps(
            {"a": dict(fitted.a), "d": dict(fitted.d), "h": fitted.h,
             "rho": fitted.rho, "mu": fitted.mu, "arm": "gate_zero",
             "fit_on": "all matches <= 2024/2025"}, indent=2) + "\n")
    _print_table(result, "virgin")
    return result


def _print_table(data, label):
    print(label)
    if label == "dev":
        print("arm season kind n ll_1x2 rps oull_2_5")
        for r in data:
            print(f'{r["arm"]} {r["season"]} {r["kind"]} {r["n"]} {r["ll_1x2"]:.6f} {r["rps"]:.6f} {r["oull_2_5"]:.6f}')
    else:
        print("arm n ll_1x2 rps oull_2_5 clim_ll naive_ll cal_hw_pp cal_ou_pp")
        for a, r in data["arms"].items():
            m = r["metrics"]
            print(f'{a} {m["n"]} {m["ll_1x2"]:.6f} {m["rps"]:.6f} {m["oull_2_5"]:.6f} '
                  f'{data["climatology"]["ll_1x2"]:.6f} {data["naive_trailing_10"]["ll_1x2"]:.6f} '
                  f'{r["calibration"]["home_win_diff_pp"]:.2f} {r["calibration"]["over25_diff_pp"]:.2f}')
