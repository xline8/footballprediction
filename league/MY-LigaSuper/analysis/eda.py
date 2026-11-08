"""CSV-only Phase A EDA for Malaysia Liga Super."""
import csv, json, math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent; CSV = HERE.parent / "data" / "my_ligasuper_matches.csv"; OUT = HERE / "eda_summary.json"
SEASONS = ["2021", "2022", "2023", "2024/2025", "2025/2026", "2026/2027"]; DEV = ["2022", "2023", "2024/2025"]
rows = list(csv.DictReader(CSV.open()))
for r in rows:
    for k in ["home_goals", "away_goals", "home_team_id", "away_team_id", "goal_events", "half_events", "card_events", "yellow_events", "red_events", "yellowred_events", "has_events", "is_awarded", "has_stats", "has_shotmap", "referee_named"]: r[k] = int(r[k])
    r["g"] = r["home_goals"] + r["away_goals"]
model = [r for r in rows if not r["is_awarded"]]


def level(rs):
    n = len(rs)
    return {"n": n, "goals_per_match": sum(r["g"] for r in rs) / n, "home_goals": sum(r["home_goals"] for r in rs) / n, "away_goals": sum(r["away_goals"] for r in rs) / n,
            "HW": sum(r["home_goals"] > r["away_goals"] for r in rs) / n, "D": sum(r["home_goals"] == r["away_goals"] for r in rs) / n, "AW": sum(r["home_goals"] < r["away_goals"] for r in rs) / n,
            "OU1.5": sum(r["g"] > 1 for r in rs) / n, "OU2.5": sum(r["g"] > 2 for r in rs) / n, "OU3.5": sum(r["g"] > 3 for r in rs) / n, "BTTS": sum(r["home_goals"] > 0 and r["away_goals"] > 0 for r in rs) / n}


def corr(x, y):
    mx, my = sum(x) / len(x), sum(y) / len(y); a = sum((v - mx) ** 2 for v in x); b = sum((v - my) ** 2 for v in y)
    return sum((u - mx) * (v - my) for u, v in zip(x, y)) / math.sqrt(a * b) if a and b else None


def split_reliability(seasons):
    gf1, gf2, ga1, ga2 = [], [], [], []
    for s in seasons:
        f = defaultdict(list); a = defaultdict(list)
        rs = sorted([r for r in model if r["season"] == s], key=lambda r: (r["date"], int(r["match_id"])))
        for r in rs:
            f[r["home_team_id"]].append(r["home_goals"]); a[r["home_team_id"]].append(r["away_goals"])
            f[r["away_team_id"]].append(r["away_goals"]); a[r["away_team_id"]].append(r["home_goals"])
        for t in f:
            h = len(f[t]) // 2
            if h >= 5 and len(f[t]) - h > 0:
                gf1.append(sum(f[t][:h]) / h); gf2.append(sum(f[t][h:]) / (len(f[t]) - h)); ga1.append(sum(a[t][:h]) / h); ga2.append(sum(a[t][h:]) / (len(a[t]) - h))
    return {"n_team_seasons": len(gf1), "gf_r": corr(gf1, gf2), "ga_r": corr(ga1, ga2)}


def halves(rs):
    used = [r for r in rs if r["goals_1h"] != "" and r["goal_events"] == r["g"]]
    positive = [r for r in used if r["g"] > 0]; total = sum(r["g"] for r in used); g1 = sum(int(r["goals_1h"]) for r in used)
    p = g1 / total; shares = [int(r["goals_1h"]) / r["g"] for r in positive]; m = sum(shares) / len(shares)
    obs = sum((x - m) ** 2 for x in shares) / len(shares); exp = sum(p * (1 - p) / r["g"] for r in positive) / len(positive)
    return {"matches_used": len(used), "matches_with_goals": len(positive), "first_half_goals": g1, "goals": total, "share": p, "observed_variance": obs, "binomial_noise_expectation": exp, "variance_ratio": obs / exp, "implied_true_variance": max(0, obs - exp), "implied_true_sd": math.sqrt(max(0, obs - exp))}


def total_dispersion(rs):
    vals = [r["g"] for r in rs]; mean = sum(vals) / len(vals); var = sum((x - mean) ** 2 for x in vals) / len(vals)
    return {"n": len(vals), "mean": mean, "variance": var, "variance_to_mean": var / mean}


def shrink_counts(target):
    order = {s: i for i, s in enumerate(SEASONS)}; prior = [r for r in model if order[r["season"]] < order[target]]; counts = defaultdict(int)
    for r in prior: counts[r["home_team_id"]] += 1; counts[r["away_team_id"]] += 1
    ids = {r["home_team_id"] for r in model if r["season"] == target} | {r["away_team_id"] for r in model if r["season"] == target}; vals = {str(t): counts[t] for t in ids}
    return {"n_0": sum(v == 0 for v in vals.values()), "n_1_to_5": sum(1 <= v <= 5 for v in vals.values()), "n_6_to_29": sum(6 <= v <= 29 for v in vals.values()), "n_30_plus": sum(v >= 30 for v in vals.values()), "team_prior_match_counts": vals}


inv = json.loads((HERE / "inventory_summary.json").read_text())
out = {"league": "MY-LigaSuper", "model_rows": len(model), "levels_by_season": {s: level([r for r in model if r["season"] == s]) for s in SEASONS},
       "dev_pooled": level([r for r in model if r["season"] in DEV]), "virgin_pooled": level([r for r in model if r["season"] == "2025/2026"]), "reserve_pooled": level([r for r in model if r["season"] == "2026/2027"]),
       "windows": {"warmup": "2021", "dev_scored": DEV, "dev_scored_n": 469, "virgin": "2025/2026 (inventory-only)", "confirmatory_reserve": "2026/2027 partial (inventory-only)"},
       "trait_reliability": {"dev_era_2021_2025": split_reliability(SEASONS[:4]), "scored_window_2022_2025": split_reliability(DEV), "all_model": split_reliability(SEASONS[:5])},
       "goals_1h_share": {"per_season": {s: halves([r for r in model if r["season"] == s]) for s in SEASONS}, "dev_pooled": halves([r for r in model if r["season"] in DEV]), "all_model": halves(model)},
       "total_goals_dispersion": {"by_season": {s: total_dispersion([r for r in model if r["season"] == s]) for s in SEASONS}, "dev_pooled": total_dispersion([r for r in model if r["season"] in DEV])},
       "entrants_by_season": inv["entrants_by_team_id"], "shrink_expectation_by_target_season": {s: shrink_counts(s) for s in DEV},
       "format": {"team_counts": inv["team_counts_by_season"], "rounds": {s: len(inv["rounds_by_season"][s]) for s in SEASONS}, "regular_phase_only": True},
       "absence_counts_by_season": inv["content_absence_zero_counts_by_season"],
       "feed_inventory": {"stats_zero": sum(not r["has_stats"] for r in rows), "shotmap_zero": sum(not r["has_shotmap"] for r in rows), "referee_zero": sum(not r["referee_named"] for r in rows), "yellow_events_zero": sum(r["yellow_events"] for r in rows), "events_present": sum(r["has_events"] for r in rows), "eventless": sum(not r["has_events"] for r in rows)}}
OUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n"); print(json.dumps(out, indent=2, sort_keys=True))
