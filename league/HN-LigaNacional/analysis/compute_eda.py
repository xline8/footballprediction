#!/usr/bin/env python3
"""Compute descriptive Honduras EDA; no model fitting or predictions."""
import csv, json, math
from collections import defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data/hn_matches.csv"
HERE = Path(__file__).resolve().parent

def num(x):
    try: return float(x) if x not in (None, "") else None
    except (TypeError, ValueError): return None
def mean(xs):
    xs = list(xs); return sum(xs) / len(xs) if xs else None
def variance(xs):
    xs = list(xs); return sum((x - mean(xs)) ** 2 for x in xs) / (len(xs) - 1) if len(xs) > 1 else None
def pct(n, d): return n / d if d else None

def match_stats(rows):
    pairs = [(num(r["home_goals"]), num(r["away_goals"])) for r in rows]
    totals = [h + a for h, a in pairs]
    cards = [num(r["event_cards_total"]) for r in rows]
    return {"n": len(rows), "home_goals": sum(h for h, _ in pairs), "away_goals": sum(a for _, a in pairs), "total_goals": sum(totals),
            "mean_home_goals": mean(h for h, _ in pairs), "mean_away_goals": mean(a for _, a in pairs), "mean_total_goals": mean(totals),
            "home_win_rate": pct(sum(h > a for h, a in pairs), len(rows)), "draw_rate": pct(sum(h == a for h, a in pairs), len(rows)), "away_win_rate": pct(sum(h < a for h, a in pairs), len(rows)),
            "ou25_rate": pct(sum(t > 2.5 for t in totals), len(rows)), "btts_rate": pct(sum(h > 0 and a > 0 for h, a in pairs), len(rows)), "card_events_per_match": mean(cards)}

def split_reliability(rows, metric, min_half=6):
    by_team = defaultdict(list)
    for r in rows:
        for side in ("home", "away"):
            value = metric(r, side)
            by_team[r[f"{side}_id"]].append((r["date"], int(r["match_id"]), value))
    first, second = [], []
    for vals in by_team.values():
        vals.sort(); mid = len(vals) // 2
        if mid < min_half or len(vals) - mid < min_half: continue
        first.append((sum(v for _, _, v in vals[:mid]), len(vals[:mid])))
        second.append((sum(v for _, _, v in vals[mid:]), len(vals[mid:])))
    a = [s / n for s, n in first]; b = [s / n for s, n in second]
    if len(a) < 2: r = None
    else:
        ma, mb = mean(a), mean(b); da = [x - ma for x in a]; db = [x - mb for x in b]; den = math.sqrt(sum(x*x for x in da) * sum(x*x for x in db)); r = sum(x*y for x, y in zip(da, db)) / den if den else None
    return {"r": r, "n_teams": len(a), "min_half_matches": min_half, "half_rate_definition": "sum of team goals / team matches"}

def levels(rows):
    out = {}
    for season in sorted({r["season"] for r in rows}): out[season] = match_stats([r for r in rows if r["season"] == season])
    return out

def main():
    with open(CSV, newline="") as fh: rows = list(csv.DictReader(fh))
    regular = [r for r in rows if r["stage"] == "regular"]; playoffs = [r for r in rows if r["stage"] == "playoff"]
    by_phase = {}
    for key in sorted({(r["season"], r["phase"]) for r in regular}): by_phase[f"{key[0]} | {key[1]}"] = match_stats([r for r in regular if (r["season"], r["phase"]) == key])
    reliability = {"goals_for": split_reliability(regular, lambda r, s: num(r[f"{s}_goals"])), "goals_against": split_reliability(regular, lambda r, s: num(r[f"{'away' if s == 'home' else 'home'}_goals"]))}
    recoverable = [r for r in rows if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None]
    nonzero_pairs = []
    for r in recoverable:
        total = num(r["home_goals"]) + num(r["away_goals"])
        if total > 0:
            nonzero_pairs.append(((num(r["ht_home"]) + num(r["ht_away"])) / total, total))
    nonzero = [share for share, _ in nonzero_pairs]
    recoverable_goals = [num(r["home_goals"]) + num(r["away_goals"]) for r in recoverable]
    half_goals = sum(num(r["ht_home"]) + num(r["ht_away"]) for r in recoverable)
    recoverable_total_goals = sum(recoverable_goals)
    recoverable_share = half_goals / recoverable_total_goals
    expected_binomial_variance = mean(recoverable_share * (1 - recoverable_share) / total for _, total in nonzero_pairs)
    observed_share_variance = variance(nonzero)
    excess_true_variance = observed_share_variance - expected_binomial_variance
    true_sd_pp = math.sqrt(max(0.0, excess_true_variance)) * 100
    variance_noise = 2 * observed_share_variance / math.sqrt(len(nonzero) - 1)
    halves_verdict = "CONSTANT_FROZEN" if abs(excess_true_variance) <= variance_noise else "NO_CONSTANT_FROZEN"
    summary = {"n_matches": len(rows), "regular_matches": len(regular), "playoff_matches": len(playoffs), "seasons": levels(regular), "phases": by_phase,
               "playoffs_by_phase": {k: match_stats([r for r in playoffs if f"{r['season']} | {r['phase']}" == k]) for k in sorted({f"{r['season']} | {r['phase']}" for r in playoffs})},
               "trait_reliability": reliability, "halves": {"recoverable_matches": len(recoverable), "recoverable_share": pct(len(recoverable), len(rows)), "goals_1h": half_goals, "goals_total_recoverable_matches": recoverable_total_goals, "goals_1h_share": recoverable_share, "nonzero_goal_matches": len(nonzero), "match_share_variance_nonzero_goal": observed_share_variance, "observed_share_variance": observed_share_variance, "expected_binomial_variance": expected_binomial_variance, "excess_true_variance": excess_true_variance, "true_sd_pp": true_sd_pp, "variance_noise_threshold": variance_noise, "frozen_constant_question": "Is true per-match 1H-share variance approximately 0?", "verdict": halves_verdict, "frozen_constant": recoverable_share},
               "awarded_matches": [{"match_id": r["match_id"], "season": r["season"], "date": r["date"], "home": r["home"], "away": r["away"], "score": f"{r['home_goals']}-{r['away_goals']}"} for r in rows if r["awarded"]],
               "format": {"regular": {s: sum(r["stage"] == "regular" and r["season"] == s for r in rows) for s in sorted({r["season"] for r in rows})}, "playoff": {s: sum(r["stage"] == "playoff" and r["season"] == s for r in rows) for s in sorted({r["season"] for r in rows})}}
    }
    with open(HERE / "eda_summary.json", "w") as fh: json.dump(summary, fh, indent=2, sort_keys=True)
    print(f"Wrote {HERE/'eda_summary.json'}")
    print(json.dumps({"seasons": summary["seasons"], "trait_reliability": reliability, "halves": summary["halves"], "format": summary["format"]}, indent=2, sort_keys=True))

if __name__ == "__main__": main()
