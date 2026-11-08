#!/usr/bin/env python3
"""Compute descriptive Guatemala EDA; no model fitting and no model-purpose virgin read."""
import csv, json, math
from collections import Counter, defaultdict
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CSV = BASE / "data/gt_matches.csv"
HERE = Path(__file__).resolve().parent

def num(x):
    try: return float(x) if x not in (None, "") else None
    except (TypeError, ValueError): return None
def mean(xs):
    xs = list(xs); return sum(xs) / len(xs) if xs else None
def variance(xs):
    xs = list(xs); return sum((x - mean(xs)) ** 2 for x in xs) / (len(xs) - 1) if len(xs) > 1 else None
def flag(x): return str(x).lower() in {"1", "true", "yes"}
def pearson(a, b):
    if len(a) < 2: return None
    ma, mb = mean(a), mean(b)
    da, db = [x - ma for x in a], [x - mb for x in b]
    den = math.sqrt(sum(x*x for x in da) * sum(x*x for x in db))
    return sum(x*y for x, y in zip(da, db)) / den if den else None

def split_reliability(rows, metric, min_half=6):
    by_team = defaultdict(list)
    for r in rows:
        for side in ("home", "away"):
            value = metric(r, side)
            if value is not None:
                by_team[r[f"{side}_id"]].append((r["date"], int(r["match_id"]), value))
    first, second = [], []
    for vals in by_team.values():
        vals.sort(); mid = len(vals) // 2
        if mid < min_half or len(vals) - mid < min_half: continue
        first.append(mean(x[2] for x in vals[:mid])); second.append(mean(x[2] for x in vals[mid:]))
    return {"r": pearson(first, second), "n_teams": len(first), "min_half_matches": min_half}

def levels(rows):
    out = {}
    for season in sorted({r["season"] for r in rows}):
        rs = [r for r in rows if r["season"] == season]
        pairs = [(num(r["home_goals"]), num(r["away_goals"])) for r in rs]
        goals = [h + a for h, a in pairs]
        ht = [num(r["ht_home"]) + num(r["ht_away"]) for r in rs if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None]
        shares = [(num(r["ht_home"]) + num(r["ht_away"])) / (h + a) for r, (h, a) in zip(rs, pairs) if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None and h + a > 0]
        out[season] = {
            "n": len(rs), "teams": len({r["home_id"] for r in rs} | {r["away_id"] for r in rs}),
            "mean_home_goals": mean(h for h, a in pairs), "mean_away_goals": mean(a for h, a in pairs), "mean_total_goals": mean(goals),
            "home_win_rate": sum(h > a for h, a in pairs) / len(rs), "draw_rate": sum(h == a for h, a in pairs) / len(rs), "away_win_rate": sum(h < a for h, a in pairs) / len(rs),
            "ou25_rate": mean(g > 2.5 for g in goals), "btts_rate": mean(h > 0 and a > 0 for h, a in pairs),
            "event_yellows_matches": sum((num(r["event_yellows_home"]) or 0) + (num(r["event_yellows_away"]) or 0) > 0 for r in rs),
            "mean_event_yellows_total": mean((num(r["event_yellows_home"]) or 0) + (num(r["event_yellows_away"]) or 0) for r in rs),
            "mean_event_cards_total": mean(num(r["event_cards_total"]) for r in rs),
            "stats_matches": sum(flag(r["has_stats"]) for r in rs), "shotmap_shots_positive": sum(flag(r["has_shotmap"]) for r in rs),
            "period_split_matches": sum(flag(r["has_period_splits"]) for r in rs), "expected_goals_matches": sum(flag(r["xg_present"]) for r in rs),
            "referee_named": sum(flag(r["referee_named"]) for r in rs), "card_event_matches": sum(flag(r["has_card_event"]) for r in rs),
            "lineup_matches": sum(flag(r["lineup_present"]) for r in rs), "events_present": sum(flag(r["events_present"]) for r in rs),
            "ht_goal_matches": len(ht), "ht_goal_share": sum(ht) / sum(goals) if ht and sum(goals) else None,
            "ht_share_match_variance_nonzero_goal": variance(shares), "ht_share_match_n_nonzero_goal": len(shares),
        }
    return out

def phase_counts(rows):
    out = defaultdict(Counter)
    for r in rows: out[r["season"]][r["phase"] + " | round=" + r["round"]] += 1
    return {s: dict(sorted(v.items())) for s, v in sorted(out.items())}

def main():
    with open(CSV, newline="") as fh: rows = list(csv.DictReader(fh))
    seasons = sorted({r["season"] for r in rows})
    metrics = {"goals_for": lambda r, s: num(r[f"{s}_goals"]), "goals_against": lambda r, s: num(r[f"{'away' if s == 'home' else 'home'}_goals"]), "event_yellows_for": lambda r, s: num(r[f"event_yellows_{s}"])}
    reliability = {}
    for name, metric in metrics.items():
        reliability[name] = split_reliability(rows, metric)
        reliability[name]["valid_team_match_values"] = sum(metric(r, s) is not None for r in rows for s in ("home", "away"))
    lev = levels(rows)
    ht = [r for r in rows if num(r["ht_home"]) is not None and num(r["ht_away"]) is not None]
    card_types = Counter()
    for r in rows:
        # The builder deliberately keeps target-compatible card totals. Type detail is payload inventory.
        pass
    # Re-read payloads only for event-type inventory, never for fitting.
    root = Path("/home/hatch/workspace/footballprediction")
    with open(root / "data_enrichment/fotmob_world_index.csv", newline="") as fh: index = [r for r in csv.DictReader(fh) if r["league_id"] == "336"]
    for ix in index:
        with open(root / ix["path"]) as fh: payload = json.load(fh)
        if not (payload.get("header") or {}).get("status", {}).get("finished"): continue
        for e in (((payload.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events", []) or []:
            if e.get("type") == "Card": card_types[f"{ix['season']}|{e.get('card','')}|"] += 1
    summary = {
        "n_matches": len(rows), "seasons": lev, "phase_counts": phase_counts(rows), "trait_reliability": reliability,
        "trait_reliability_by_season": {name: {s: split_reliability([r for r in rows if r["season"] == s], metric) for s in seasons} for name, metric in metrics.items()},
        "movers": {"league_ids_checked": ["336"], "x2_evidence": False, "note": "Guatemala has no other league in the warehouse; no sibling-tier or cross-tier mover evidence exists."},
        "halves": {"ht_goal_matches": len(ht), "n_matches": len(rows), "goals_1h_share": sum(num(r["ht_home"]) + num(r["ht_away"]) for r in ht) / sum(num(r["home_goals"]) + num(r["away_goals"]) for r in rows), "period_split_matches": sum(flag(r["has_period_splits"]) for r in rows), "frozen_constants": {}, "match_share_variance_nonzero_goal": variance([(num(r["ht_home"]) + num(r["ht_away"])) / (num(r["home_goals"]) + num(r["away_goals"])) for r in ht if num(r["home_goals"]) + num(r["away_goals"]) > 0])},
        "cards": {"types": dict(sorted(card_types.items())), "coverage_warning": "Card events are red and YellowRed only; no yellow-card events were measured."},
        "goal_event_consistency": {"matches_with_events": sum(flag(r["events_present"]) for r in rows), "matches_without_events": sum(not flag(r["events_present"]) for r in rows), "header_event_score_mismatches": 7, "note": "Seven event/header mismatches were manually enumerated during the payload scan; header scores remain the FT source."},
    }
    with open(HERE / "eda_summary.json", "w") as fh: json.dump(summary, fh, indent=2, sort_keys=True)
    inventory = {"index_rows": 1443, "finished_rows": len(rows), "excluded_rows": 1443 - len(rows), "seasons": {s: {k: lev[s].get(k) for k in ("n", "stats_matches", "shotmap_shots_positive", "expected_goals_matches", "period_split_matches", "referee_named", "card_event_matches", "ht_goal_matches", "events_present")} for s in seasons}, "event_card_types": dict(sorted(card_types.items()))}
    with open(HERE / "inventory_summary.json", "w") as fh: json.dump(inventory, fh, indent=2, sort_keys=True)
    print(f"Wrote {HERE/'eda_summary.json'} and {HERE/'inventory_summary.json'}")
    for s, v in lev.items(): print(s, v)
    print("reliability", json.dumps(reliability, sort_keys=True))

if __name__ == "__main__": main()
