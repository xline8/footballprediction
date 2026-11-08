"""S-UA harness — written for CN per PREREG_S_CN.md.

The model architecture (model.py Engine) is the copied production v5
pattern; this harness is CN-local bookkeeping (the TH/RU harness it was
copied alongside carried another league's primary line in its virgin
calibration aliases, so it was not reused). Protocol:
- era 2023+ only; warm-up 2023 (updates state, never scored);
- dev scored 2024+2025 (n=480); virgin 2026 (n=240) read ONCE, only
  for arms recorded as dev-passing in results_dev.json;
- walk-forward per-match chronological (date, match_id),
  predict-then-update, date-grouped via the engine's own state;
- baselines: league base rate (era rows strictly before the scored
  season, per-line over-rate) and naive trailing-10 (engine output).
Calibration = actual - predicted.
"""
import csv, json, math, os
import numpy as np
from model import Engine, load_matches, NB_R, LINES

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DATA = os.path.join(ROOT, "data", "ua_matches.csv")
OUT = os.path.dirname(__file__)
PRED_DIR = os.path.join(ROOT, "predictions")
ARMS = ("GZ", "RS")
PRIMARY = 6.5
DEV_SEASONS = {"2022/2023", "2023/2024", "2024/2025"}
SCORED = {"2023/2024", "2024/2025"}
VIRGIN_SEASON = "2025/2026"
HALVES_SOT_1H = 0.4580


def ll(p, y):
    p = min(max(p, 1e-12), 1 - 1e-12)
    return -(y * math.log(p) + (1 - y) * math.log(1 - p))


def actual(m, line):
    return 1.0 if m["sot_h"] + m["sot_a"] > line else 0.0


def block(rows, prob_fn):
    """rows: list of (match, pred). prob_fn(pred, line) -> prob."""
    ans = {"pooled": {}, "seasons": {}, "n": len(rows)}
    for L in LINES:
        vals = [ll(prob_fn(p, L), actual(m, L)) for m, p in rows]
        ans["pooled"][f"ll_{L}"] = sum(vals) / len(vals)
        for s in sorted({m["season"] for m, _ in rows}):
            z = [ll(prob_fn(p, L), actual(m, L)) for m, p in rows if m["season"] == s]
            ans["seasons"].setdefault(s, {})[f"ll_{L}"] = sum(z) / len(z)
            ans["seasons"][s]["n"] = len(z)
    ps = [prob_fn(p, PRIMARY) for _, p in rows]
    ys = [actual(m, PRIMARY) for m, _ in rows]
    ans["pooled"]["mean_p_primary"] = sum(ps) / len(ps)
    ans["pooled"]["actual_over_primary"] = sum(ys) / len(ys)
    return ans


def run_walk(ms, arm, scored_seasons):
    eng = Engine(ms, arm)
    rows = []
    for m in ms:
        if m["season"] in scored_seasons:
            rows.append((m, eng.predict(m)))
        eng.update(m)
    return rows, eng


def base_rate_probs(ms, scored_seasons, line):
    """Per scored season: over-rate of era rows strictly before season start."""
    out = {}
    for s in scored_seasons:
        cutoff = min(m["date"] for m in ms if m["season"] == s)
        prior = [m for m in ms if m["date"] < cutoff]
        out[s] = sum(actual(m, line) for m in prior) / len(prior)
    return out


def run_dev():
    ms = load_matches(DATA, DEV_SEASONS)
    scored = [m for m in ms if m["season"] in SCORED]
    assert len(scored) == 462, len(scored)
    assert not any(m["season"] == VIRGIN_SEASON for m in ms)
    results = {}
    for arm in ARMS:
        rows, _ = run_walk(ms, arm, SCORED)
        results[arm] = rows
    out = {"protocol": {"league": "UA-PremierLeague", "dev_seasons_loaded": sorted(DEV_SEASONS),
                        "warmup": "2022/2023", "scored": sorted(SCORED), "n": len(scored),
                        "primary_line": PRIMARY, "sign_convention": "actual_minus_predicted"},
           "n": len(scored), "arms": {}, "baselines": {}}
    for arm in ARMS:
        out["arms"][arm] = block(results[arm], lambda p, L: p["probs"][L])
    # baselines scored on the GZ row set (identical match set across arms)
    rows = results["GZ"]
    rates = {L: base_rate_probs(ms, SCORED, L) for L in LINES}
    out["baselines"]["league_base_rate"] = block(rows, lambda p, L, _m=None: 0.0)  # placeholder replaced below
    # base-rate block needs per-match season lookup; compute directly:
    def base_block():
        ans = {"pooled": {}, "seasons": {}, "n": len(rows)}
        for L in LINES:
            vals = [ll(rates[L][m["season"]], actual(m, L)) for m, _ in rows]
            ans["pooled"][f"ll_{L}"] = sum(vals) / len(vals)
            for s in sorted(SCORED):
                z = [ll(rates[L][m["season"]], actual(m, L)) for m, _ in rows if m["season"] == s]
                ans["seasons"].setdefault(s, {})[f"ll_{L}"] = sum(z) / len(z)
                ans["seasons"][s]["n"] = len(z)
        ps = [rates[PRIMARY][m["season"]] for m, _ in rows]
        ys = [actual(m, PRIMARY) for m, _ in rows]
        ans["pooled"]["mean_p_primary"] = sum(ps) / len(ps)
        ans["pooled"]["actual_over_primary"] = sum(ys) / len(ys)
        return ans
    out["baselines"]["league_base_rate"] = base_block()
    out["baselines"]["naive"] = block(rows, lambda p, L: p["naive_probs"][L])
    # dev gate: pooled LL@9.5 beats BOTH baselines
    b_ll = min(out["baselines"]["league_base_rate"]["pooled"][f"ll_{PRIMARY}"],
               out["baselines"]["naive"]["pooled"][f"ll_{PRIMARY}"])
    out["dev_pass"] = {a: bool(out["arms"][a]["pooled"][f"ll_{PRIMARY}"] < b_ll) for a in ARMS}
    if not out["dev_pass"]["GZ"]:
        out["dev_pass"] = {a: False for a in ARMS}  # Gate Zero dev failure => variants moot
    with open(os.path.join(OUT, "results_dev.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(OUT, "predictions_dev.csv"), "w", newline="") as f:
        fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
                  "actual_target", "arm", "predicted_mean", "p_over_6_5", "p_over_7_5", "p_over_8_5",
                  "baseline_league_p_over_6_5", "baseline_naive_p_over_6_5"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for arm in ARMS:
            for m, p in results[arm]:
                q = {"match_id": m["match_id"], "season": m["season"], "date": m["date"].isoformat(),
                     "home_team_id": m["home_id"], "away_team_id": m["away_id"],
                     "home": m["home_name"], "away": m["away_name"],
                     "actual_target": m["sot_h"] + m["sot_a"], "arm": arm,
                     "predicted_mean": p["exp_h"] + p["exp_a"],
                     "baseline_league_p_over_6_5": rates[PRIMARY][m["season"]],
                     "baseline_naive_p_over_6_5": p["naive_probs"][PRIMARY]}
                q.update({f"p_over_{str(L).replace('.', '_')}": p["probs"][L] for L in LINES})
                w.writerow(q)
    return out


def virgin_metrics(rows, prob_fn):
    out = {"n": len(rows)}
    for L in LINES:
        ps = [prob_fn(p, L) for _, p in rows]; ys = [actual(m, L) for m, _ in rows]
        dif = [y - p for p, y in zip(ps, ys)]
        out[f"ll_{L}"] = sum(ll(p, y) for p, y in zip(ps, ys)) / len(ps)
        out[f"mean_p_{L}"] = sum(ps) / len(ps)
        out[f"actual_over_{L}"] = sum(ys) / len(ys)
        out[f"calibration_diff_{L}"] = sum(dif) / len(dif)
        out[f"calibration_se_{L}"] = float(np.std(dif, ddof=1) / math.sqrt(len(dif))) if len(dif) > 1 else 0.0
    return out


def run_virgin():
    dev = json.load(open(os.path.join(OUT, "results_dev.json")))
    passing = [a for a in ARMS if dev["dev_pass"].get(a)]
    if not passing:
        raise SystemExit("no dev-passing arm; virgin must NOT be read")
    ms = load_matches(DATA, DEV_SEASONS | {VIRGIN_SEASON})
    vms = [m for m in ms if m["season"] == VIRGIN_SEASON]
    assert len(vms) == 223, len(vms)
    allrows = {}
    out = {"protocol": {"league": "UA-PremierLeague", "virgin_season": VIRGIN_SEASON, "n": len(vms),
                        "scored_arms": passing, "primary_line": PRIMARY,
                        "sign_convention": "actual_minus_predicted"},
           "n": len(vms), "arms": {}, "baselines": {}}
    for a in passing:
        rows, eng = run_walk(ms, a, {VIRGIN_SEASON})
        allrows[a] = (rows, eng)
        out["arms"][a] = virgin_metrics(rows, lambda p, L: p["probs"][L])
    rows = allrows[passing[0]][0]
    rates = {L: base_rate_probs(ms, {VIRGIN_SEASON}, L) for L in LINES}
    out["baselines"]["league_base_rate"] = virgin_metrics(
        rows, lambda p, L, _r=rates: _r[L][VIRGIN_SEASON])
    # naive from the GZ run if present, else first passing arm (naive is arm-independent)
    naive_rows = allrows["GZ"][0] if "GZ" in allrows else rows
    out["baselines"]["naive"] = virgin_metrics(naive_rows, lambda p, L: p["naive_probs"][L])
    # gate legs
    best_base = min(out["baselines"][b][f"ll_{PRIMARY}"] for b in out["baselines"])
    gz_ll = out["arms"]["GZ"][f"ll_{PRIMARY}"] if "GZ" in out["arms"] else None
    eligible = []
    for a in passing:
        v = out["arms"][a]
        leg_i = (gz_ll is None or v[f"ll_{PRIMARY}"] <= gz_ll) and v[f"ll_{PRIMARY}"] <= best_base
        diff = abs(v[f"calibration_diff_{PRIMARY}"]); se = v[f"calibration_se_{PRIMARY}"]
        leg_ii = diff <= 0.01 + se
        v["calibration_status"] = "clean" if diff <= 0.01 else ("provisional" if leg_ii else "fail")
        if a == "GZ":
            leg_iii = True
        else:
            wins = sum(1 for s in SCORED
                       if dev["arms"][a]["seasons"][s][f"ll_{PRIMARY}"] <= dev["arms"]["GZ"]["seasons"][s][f"ll_{PRIMARY}"])
            leg_iii = wins >= 1
        v["legs"] = {"i_ll": bool(leg_i), "ii_calibration": bool(leg_ii), "iii_sign": bool(leg_iii)}
        if leg_i and leg_ii and leg_iii:
            eligible.append(a)
    chosen = min(eligible, key=lambda a: (out["arms"][a][f"ll_{PRIMARY}"], ARMS.index(a))) if eligible else None
    out["shipped_arm"] = chosen
    with open(os.path.join(OUT, "results_virgin.json"), "w") as f:
        json.dump(out, f, indent=2)
    with open(os.path.join(OUT, "predictions_virgin.csv"), "w", newline="") as f:
        fields = ["match_id", "season", "date", "home_team_id", "away_team_id", "home", "away",
                  "actual_target", "arm", "predicted_mean", "p_over_6_5", "p_over_7_5", "p_over_8_5",
                  "baseline_league_p_over_6_5", "baseline_naive_p_over_6_5"]
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for a in passing:
            for m, p in allrows[a][0]:
                q = {"match_id": m["match_id"], "season": m["season"], "date": m["date"].isoformat(),
                     "home_team_id": m["home_id"], "away_team_id": m["away_id"],
                     "home": m["home_name"], "away": m["away_name"],
                     "actual_target": m["sot_h"] + m["sot_a"], "arm": a,
                     "predicted_mean": p["exp_h"] + p["exp_a"],
                     "baseline_league_p_over_6_5": rates[PRIMARY][VIRGIN_SEASON],
                     "baseline_naive_p_over_6_5": p["naive_probs"][PRIMARY]}
                q.update({f"p_over_{str(L).replace('.', '_')}": p["probs"][L] for L in LINES})
                w.writerow(q)
    eng = allrows[chosen or passing[0]][1]
    league_means = {}
    for d in eng.reg.divs:
        mh, ma = eng.reg.means(d, vms[-1]["day"] + 1)
        league_means[d] = {"home": mh, "away": ma}
    with open(os.path.join(OUT, "fitted_params_virgin.json"), "w") as f:
        json.dump({"arms": passing, "shipped_arm": chosen, "nb_r": NB_R, "league_means": league_means,
                   "halves_sot_1h_share": None,  # UA FT-only: no halves source exists (prereg)
                   "regression": {d: {"teams": x["teams"], "theta": x["theta"].tolist()}
                                  for d, x in eng.reg.divs.items()}}, f, indent=2)
    if chosen is not None:
        os.makedirs(PRED_DIR, exist_ok=True)
        rows = allrows[chosen][0]
        with open(os.path.join(PRED_DIR, "s_ua_virgin_predictions.csv"), "w", newline="") as f:
            cols = ["arm", "match_id", "date", "home_team", "away_team", "actual_total_sot",
                    "exp_sot_home", "exp_sot_away", "exp_sot_total"] + \
                   [f"ft_p_over_{L}" for L in LINES]
            w = csv.DictWriter(f, fieldnames=cols); w.writeheader()
            for m, p in rows:
                total = p["exp_h"] + p["exp_a"]
                row = {"arm": chosen, "match_id": m["match_id"], "date": m["date"],
                       "home_team": m["home_name"], "away_team": m["away_name"],
                       "actual_total_sot": m["sot_h"] + m["sot_a"],
                       "exp_sot_home": p["exp_h"], "exp_sot_away": p["exp_a"], "exp_sot_total": total}
                for L in LINES:
                    row[f"ft_p_over_{L}"] = p["probs"][L]
                w.writerow(row)
    return out
