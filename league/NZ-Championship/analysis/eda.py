"""Deterministic Phase A EDA for New Zealand Championship (descriptive only)."""
import csv, json, math, statistics
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
M = list(csv.DictReader((HERE.parent / "data" / "nz_matches.csv").open()))
NUMERIC = {"home_goals", "away_goals", "ht_home_goals", "ht_away_goals", "ev_red_home", "ev_red_away", "goals_1h_total", "has_stats_all", "has_stats_half", "has_extra_time", "has_events", "sm_shots_home", "sm_sot_home", "sm_xg_home", "sm_xgot_home", "sm_xgot_n_home", "sm_shots_fh_home", "sm_shots_away", "sm_sot_away", "sm_xg_away", "sm_xgot_away", "sm_xgot_n_away", "sm_shots_fh_away"}
for r in M:
    for k in NUMERIC:
        r[k] = None if r[k] == "" else float(r[k])
SEASONS = ["2022", "2023", "2024", "2025", "2026"]

def mean(xs): return round(statistics.mean(xs), 4) if xs else None
def pearson(pairs):
    if len(pairs) < 2: return None
    mx, my = mean([x for x, _ in pairs]), mean([y for _, y in pairs]); xx = sum((x-mx)**2 for x, _ in pairs); yy = sum((y-my)**2 for _, y in pairs)
    return round(sum((x-mx)*(y-my) for x, y in pairs) / math.sqrt(xx*yy), 4) if xx and yy else None
def split_trait(seasons, gf=True, minimum=20):
    team = defaultdict(list)
    for r in M:
        if r["season"] not in seasons: continue
        for side, opp in (("home", "away"), ("away", "home")):
            team[r[f"{side}_team_id"]].append((r["date"], r["match_id"], r[f"{side}_goals"] if gf else r[f"{opp}_goals"]))
    pairs = []
    for vals in team.values():
        vals.sort(key=lambda x: (x[0], x[1]))
        if len(vals) >= minimum: pairs.append((mean([v[2] for i, v in enumerate(vals) if i % 2 == 0]), mean([v[2] for i, v in enumerate(vals) if i % 2 == 1])))
    return {"r": pearson(pairs), "n_teams": len(pairs), "min_matches": minimum}
def half_team_r(minimum=20):
    team = defaultdict(list)
    for r in M:
        total = r["home_goals"] + r["away_goals"]
        if not r["has_events"] or not total: continue
        for side in ("home", "away"):
            ft = r[f"{side}_goals"]
            if ft: team[r[f"{side}_team_id"]].append((r["date"], r["match_id"], r[f"ht_{side}_goals"] / ft))
    pairs = []
    for vals in team.values():
        vals.sort(key=lambda x: (x[0], x[1]))
        if len(vals) >= minimum: pairs.append((mean([v[2] for i, v in enumerate(vals) if i % 2 == 0]), mean([v[2] for i, v in enumerate(vals) if i % 2 == 1])))
    return {"r": pearson(pairs), "n_teams": len(pairs), "min_matches": minimum}
def ou(rows): return mean([r["home_goals"] + r["away_goals"] > 2.5 for r in rows])

levels = {}
for s in SEASONS:
    rows = [r for r in M if r["season"] == s]
    levels[s] = {"n": len(rows), "score_n": len(rows), "stats_n": int(sum(r["has_stats_all"] for r in rows)), "period_splits_n": int(sum(r["has_stats_half"] for r in rows)), "events_n": int(sum(r["has_events"] for r in rows)), "referee_named": sum(bool(r["referee"]) for r in rows), "shotmap_n": 0, "xg_n": 0, "plain_yellow_events_n": 0, "has_extra_time_n": int(sum(r["has_extra_time"] for r in rows)), "goals_per_match": mean([r["home_goals"] + r["away_goals"] for r in rows]), "home_goals_per_match": mean([r["home_goals"] for r in rows]), "away_goals_per_match": mean([r["away_goals"] for r in rows]), "home_win_rate": mean([r["home_goals"] > r["away_goals"] for r in rows]), "draw_rate": mean([r["home_goals"] == r["away_goals"] for r in rows]), "away_win_rate": mean([r["home_goals"] < r["away_goals"] for r in rows]), "ou2_5_over_rate": ou(rows), "btts_rate": mean([r["home_goals"] > 0 and r["away_goals"] > 0 for r in rows]), "event_red_home": int(sum(r["ev_red_home"] for r in rows)), "event_red_away": int(sum(r["ev_red_away"] for r in rows)), "event_red_total": int(sum(r["ev_red_home"] + r["ev_red_away"] for r in rows))}
pooled_dev = [r for r in M if r["season"] in ("2023", "2024")]
phase_levels = {p: {"n": sum(r["phase"] == p for r in M), "goals_per_match": mean([r["home_goals"] + r["away_goals"] for r in M if r["phase"] == p])} for p in ("regular", "final")}
half_rows = [r for r in M if r["season"] in ("2023", "2024", "2025", "2026") and r["has_events"] and r["home_goals"] + r["away_goals"] > 0]
total_ft = sum(r["home_goals"] + r["away_goals"] for r in half_rows); total_1h = sum(r["goals_1h_total"] for r in half_rows); p = total_1h / total_ft
shares = [r["goals_1h_total"] / (r["home_goals"] + r["away_goals"]) for r in half_rows]; noise = [p * (1-p) / (r["home_goals"] + r["away_goals"]) for r in half_rows]
entrants = []
for s in range(2022, 2027):
    season = str(s); prior = {r["home_team_id"] for r in M if r["season"] == str(s-1)} | {r["away_team_id"] for r in M if r["season"] == str(s-1)}; ids = {r["home_team_id"] for r in M if r["season"] == season} | {r["away_team_id"] for r in M if r["season"] == season}
    league_rows = [r for r in M if r["season"] == season]; league_team_mean = sum(r["home_goals"] + r["away_goals"] for r in league_rows) / (2 * len(league_rows))
    for tid in sorted(ids - prior, key=lambda x: int(x)):
        rows = [r for r in league_rows if r["home_team_id"] == tid or r["away_team_id"] == tid]; row = rows[0]; name = row["home_team"] if row["home_team_id"] == tid else row["away_team"]
        gf = mean([r["home_goals"] if r["home_team_id"] == tid else r["away_goals"] for r in rows]); ga = mean([r["away_goals"] if r["home_team_id"] == tid else r["home_goals"] for r in rows])
        entrants.append({"season": season, "team_id": tid, "team": name, "matches": len(rows), "gf_per_match": gf, "ga_per_match": ga, "league_mean_goals_per_team_match": round(league_team_mean, 4), "gf_deviation": round(gf-league_team_mean, 4), "ga_deviation": round(ga-league_team_mean, 4), "origin": "unassigned"})
summary = {"n_matches": len(M), "seasons": SEASONS, "levels": levels, "pooled_outcomes": {"home_win_rate": mean([r["home_goals"] > r["away_goals"] for r in M]), "draw_rate": mean([r["home_goals"] == r["away_goals"] for r in M]), "away_win_rate": mean([r["home_goals"] < r["away_goals"] for r in M])}, "dev_over_rate_ou2_5": ou(pooled_dev), "dev_over_rate_ou2_5_by_season": {s: ou([r for r in M if r["season"] == s]) for s in ("2023", "2024")}, "phase_levels": phase_levels, "f2": {"goals_for": split_trait(SEASONS, True), "goals_against": split_trait(SEASONS, False), "by_season": {s: {"goals_for": split_trait([s], True, 8), "goals_against": split_trait([s], False, 8)} for s in SEASONS}, "per_season_note": "Extremely noisy: 5v5 split halves at the >=8 threshold.", "not_testable": ["sot", "corners", "shots", "cards"]}, "f3": {"n_matches_with_events_and_goals": len(half_rows), "total_ft_goals": total_ft, "total_1h_goals": total_1h, "goals_1h_share": round(p, 4), "frozen_constant": 0.4123, "constant_supported": round(p, 4) == 0.4123, "by_season": {}, "observed_variance": round(statistics.variance(shares), 6), "binomial_noise_floor_mean": round(statistics.mean(noise), 6), "variance_excess_over_noise": round(statistics.variance(shares) - statistics.mean(noise), 6), "team_split_half": half_team_r()}}
for s in ("2023", "2024", "2025", "2026"):
    rr = [r for r in half_rows if r["season"] == s]; den = sum(r["home_goals"] + r["away_goals"] for r in rr); ss = [r["goals_1h_total"] / (r["home_goals"] + r["away_goals"]) for r in rr]
    ns = [p * (1-p) / (r["home_goals"] + r["away_goals"]) for r in rr]
    summary["f3"]["by_season"][s] = {"n": len(rr), "share": round(sum(r["goals_1h_total"] for r in rr) / den, 4), "observed_variance": round(statistics.variance(ss), 6), "binomial_noise_floor_mean": round(statistics.mean(ns), 6)}
summary.update({"f4": {"entrants": entrants, "no_origin_assignment": True}, "f5_event_red_total_by_season": {s: levels[s]["event_red_total"] for s in SEASONS}, "f6_referees_named": sum(bool(r["referee"]) for r in M), "team_id_count": len({r["home_team_id"] for r in M} | {r["away_team_id"] for r in M}), "eventless_match_ids": [r["match_id"] for r in M if not r["has_events"]], "extra_time_match_ids": [r["match_id"] for r in M if r["has_extra_time"]], "name_variants": {"613344": ["Eastern Suburbs", "Eastern Suburbs AFC"]}})
json.dump(summary, (HERE / "eda_summary.json").open("w"), indent=2)
inventory = {"index_rows": 229, "built_match_rows": len(M), "built_team_match_rows": len(M)*2, "by_season": levels, "phase_counts": dict(Counter(r["phase"] for r in M)), "eventless_match_ids": summary["eventless_match_ids"], "extra_time_match_ids": summary["extra_time_match_ids"], "team_id_count": summary["team_id_count"], "name_variants": summary["name_variants"], "coverage": {"scores": "221/221", "events": "178/221", "stats": "0/221", "shotmap_present_empty": "221/221", "lineup": "0/221", "referee_named": "0/221", "halfs_timestamps": "221/221"}}
json.dump(inventory, (HERE / "inventory_summary.json").open("w"), indent=2)
print(json.dumps(summary, indent=2))
