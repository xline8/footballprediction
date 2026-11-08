"""S-BO shots-on-target harness (BO adaptation of the S-PY harness).

Frozen in league/BO-PrimeraDivision/prereg/PREREG_S_BO.md: seed 2025 rounds
1-10, dev scored 2025 rounds 11-30 in four expanding 5-round blocks,
virgin 2026 regular (transitional). Primary line 11.5. Calibration is
actual - predicted. Dev groups by round-block, not by season.
"""
import csv, json, math, os
import numpy as np
from model import Engine, load_matches, NB_R, LINES, nb_over

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
DATA = os.path.join(ROOT, "league", "BO-PrimeraDivision", "data", "bo_matches.csv")
OUT = os.path.dirname(__file__)
ARMS = ("GZ", "RS")
DEV_BLOCKS = ("r11-15", "r16-20", "r21-25", "r26-30")
VIRGIN = "2026"
HALF = .4555
PRIMARY = 11.5


def ll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def actual(m, L):
    return float(m["sot_h"] + m["sot_a"] > L)


def metric(rows):
    o = {"pooled": {}, "blocks": {}, "n": len(rows)}
    for L in LINES:
        o["pooled"][f"ll_{L}"] = sum(ll(p["probs"][L], actual(m, L)) for m, p in rows) / len(rows)
        for s in sorted({m["block"] for m, _ in rows}):
            z = [ll(p["probs"][L], actual(m, L)) for m, p in rows if m["block"] == s]
            o["blocks"].setdefault(s, {})[f"ll_{L}"] = sum(z) / len(z)
            o["blocks"][s]["n"] = len(z)
    return o


def baseline(scored_rows, all_matches, kind):
    # League base rate: pooled over-rate of ALL prior matches (seed + earlier
    # scored rows), strictly before the scored row's date. The PY harness
    # computed this over the scored rows only, which gives q=0 for the first
    # scored block and inflates the baseline LL; that defect is fixed here.
    vals = []
    for m, p in scored_rows:
        if kind == "naive":
            q = p["naive_probs"][PRIMARY]
        else:
            prior = [x for x in all_matches if x["date"] < m["date"]]
            q = sum(actual(x, PRIMARY) for x in prior) / len(prior)
        vals.append((m, q))
    return {"pooled": {"ll_11.5": sum(ll(q, actual(m, PRIMARY)) for m, q in vals) / len(vals)}, "n": len(vals)}


def run_dev():
    ms = load_matches(DATA, {"2025"})
    assert not any(m["season"] == VIRGIN for m in ms)
    out = {"protocol": "S-BO frozen prereg", "arms": {}, "baselines": {}}
    rb = {}
    for a in ARMS:
        e = Engine(ms, a)
        rows = []
        for m in ms:
            if m["block"] in DEV_BLOCKS:
                rows.append((m, e.predict(m)))
            e.update(m)
        rb[a] = rows
        out["arms"][a] = metric(rows)
    out["n"] = len(rb["GZ"])
    out["baselines"] = {k: baseline(rb["GZ"], ms, k) for k in ("league_base_rate", "naive")}
    out["dev_pass"] = {a: out["arms"][a]["pooled"]["ll_11.5"] < min(x["pooled"]["ll_11.5"] for x in out["baselines"].values()) for a in ARMS}
    json.dump(out, open(os.path.join(OUT, "results_dev.json"), "w"), indent=2)
    return out


def vmetrics(rows):
    ps = np.array([p["probs"][PRIMARY] for _, p in rows])
    ys = np.array([actual(m, PRIMARY) for m, _ in rows])
    d = ys - ps  # actual - predicted
    return {"ll_11.5": sum(ll(p, y) for p, y in zip(ps, ys)) / len(ps), "calibration_diff": float(d.mean()), "calibration_se": float(d.std(ddof=1) / math.sqrt(len(d))), "n": len(ps)}


def virgin(dev):
    passing = [a for a in ARMS if dev["dev_pass"].get(a)]
    ms = load_matches(DATA, {"2025", VIRGIN})
    out = {"protocol": {"virgin_season": VIRGIN, "transitional": True}, "read_arms": passing, "arms": {}, "baselines": {}, "dev_gate": dev["dev_pass"]}
    rb = {}
    for a in passing:
        e = Engine(ms, a)
        rows = []
        for m in ms:
            if m["season"] == VIRGIN:
                rows.append((m, e.predict(m)))
            e.update(m)
        rb[a] = (rows, e)
        out["arms"][a] = vmetrics(rows)
    if passing:
        e = Engine(ms, "GZ")
        rows = []
        for m in ms:
            if m["season"] == VIRGIN:
                rows.append((m, e.predict(m)))
            e.update(m)
        rate = sum(actual(m, PRIMARY) for m in ms if m["season"] != VIRGIN) / sum(m["season"] != VIRGIN for m in ms)
        # NOTE: the PY harness fed the GZ *model* probs into vmetrics for the
        # naive baseline; here the naive baseline honestly uses naive_probs.
        nps = np.array([p["naive_probs"][PRIMARY] for _, p in rows])
        nys = np.array([actual(m, PRIMARY) for m, _ in rows])
        nd = nys - nps
        out["baselines"] = {"league_base_rate": {"ll_11.5": sum(ll(rate, actual(m, PRIMARY)) for m, _ in rows) / len(rows), "rate": rate}, "naive": {"ll_11.5": sum(ll(p, y) for p, y in zip(nps, nys)) / len(nps), "calibration_diff": float(nd.mean()), "calibration_se": float(nd.std(ddof=1) / math.sqrt(len(nd))), "n": len(nps)}}
    gzll = out["arms"].get("GZ", {}).get("ll_11.5", float("inf"))
    base = min((x["ll_11.5"] for x in out["baselines"].values()), default=float("inf"))
    eligible = []
    for a, v in out["arms"].items():
        sign = a == "GZ" or sum(dev["arms"][a]["blocks"][s]["ll_11.5"] <= dev["arms"]["GZ"]["blocks"][s]["ll_11.5"] for s in DEV_BLOCKS) >= 2
        v["leg_i"] = bool(v["ll_11.5"] <= gzll and v["ll_11.5"] <= base)
        v["leg_ii"] = bool(abs(v["calibration_diff"]) <= .01 or abs(v["calibration_diff"]) <= .01 + v["calibration_se"])
        v["leg_iii"] = bool(sign)
        v["virgin_(i)"] = v["leg_i"]
        v["virgin_(ii)"] = v["leg_ii"]
        v["virgin_(iii)"] = v["leg_iii"]
        if v["leg_i"] and v["leg_ii"] and v["leg_iii"]:
            eligible.append(a)
    chosen = min(eligible, key=lambda a: (out["arms"][a]["ll_11.5"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = chosen
    out["verdict"] = "PASS" if chosen else "FAIL"
    out["calibration_breach_plus_se_pp"] = {a: (abs(v["calibration_diff"]) - .01 - v["calibration_se"]) * 100 for a, v in out["arms"].items()}
    json.dump(out, open(os.path.join(OUT, "results_virgin.json"), "w"), indent=2)
    if chosen:
        write_predictions(rb[chosen][0], chosen)
        json.dump({"arm": chosen, "nb_r": NB_R}, open(os.path.join(OUT, "fitted_params_virgin.json"), "w"), indent=2)
    else:
        json.dump({"virgin_read": bool(passing), "shipped_arm": None}, open(os.path.join(OUT, "fitted_params_virgin.json"), "w"), indent=2)
    return out


def write_predictions(rows, arm):
    path = os.path.join(OUT, "..", "..", "predictions", "s_bo_virgin_predictions.csv")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    cols = ["arm", "match_id", "date", "home_team", "away_team", "actual_total_sot", "exp_sot_home", "exp_sot_away", "exp_sot_total"] + [f"ft_p_over_{L}" for L in LINES] + [f"1h_p_over_{L}" for L in (4.5, 5.5, 6.5)] + [f"2h_p_over_{L}" for L in (5.5, 6.5, 7.5)]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for m, p in rows:
            total = p["exp_h"] + p["exp_a"]
            q = {"arm": arm, "match_id": m["match_id"], "date": m["date"], "home_team": m["home"], "away_team": m["away"], "actual_total_sot": m["sot_h"] + m["sot_a"], "exp_sot_home": p["exp_h"], "exp_sot_away": p["exp_a"], "exp_sot_total": total}
            for L in LINES:
                q[f"ft_p_over_{L}"] = p["probs"][L]
            for L in (4.5, 5.5, 6.5):
                q[f"1h_p_over_{L}"] = nb_over(HALF * total, NB_R, L)
            for L in (5.5, 6.5, 7.5):
                q[f"2h_p_over_{L}"] = nb_over((1 - HALF) * total, NB_R, L)
            w.writerow(q)
