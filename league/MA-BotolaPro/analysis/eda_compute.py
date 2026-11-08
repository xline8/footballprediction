"""EDA computations for MA-BotolaPro. Dev-era data ONLY (seasons up to
2024/2025; count traits on the rich era 2024-11-01..2025-05-12).
The virgin 2025/2026 and confirmatory 2026/2027 are never read here."""
import csv, json, math, random, statistics
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader((HERE.parent / "data" / "ma_botola_matches.csv").open()))
def f(v): return float(v) if v not in (None, "") else None
DEV = ["2021/2022", "2022/2023", "2023/2024", "2024/2025"]
out = {}
# levels per season (goals, all rows)
lev = {}
for s in DEV:
    rs = [r for r in rows if r["season"] == s]
    g = [int(r["home_goals"]) + int(r["away_goals"]) for r in rs]
    lev[s] = {"n": len(rs), "goals_per_match": round(statistics.mean(g), 4),
              "home_goals": round(statistics.mean([int(r["home_goals"]) for r in rs]), 4),
              "away_goals": round(statistics.mean([int(r["away_goals"]) for r in rs]), 4),
              "over25_rate": round(sum(1 for x in g if x > 2.5) / len(g), 4),
              "home_win_rate": round(sum(1 for r in rs if int(r["home_goals"]) > int(r["away_goals"])) / len(rs), 4)}
out["goals_levels"] = lev
# rich-era count levels (2024/2025, date >= 2024-11-01)
rich = [r for r in rows if r["season"] == "2024/2025" and r["date"] >= "2024-11-01"]
out["rich_2024_2025"] = {"n_matches": len(rich)}
sr = [r for r in rich if r["has_stats_all"] == "1"]
out["rich_2024_2025"]["n_stats"] = len(sr)
for key, col in (("sot", "ShotsOnTarget"), ("corners", "corners"), ("total_shots", "total_shots")):
    vals = [f(r[f"{col}_home"]) + f(r[f"{col}_away"]) for r in sr]
    out["rich_2024_2025"][key] = {"mean": round(statistics.mean(vals), 4),
        "over_rates": {str(L): round(sum(1 for v in vals if v > L) / len(vals), 4) for L in (6.5,7.5,8.5,9.5,10.5,20.5,21.5,22.5,23.5,24.5,25.5)}}
yv = [f(r["yellow_home"]) + f(r["yellow_away"]) for r in rich]
out["rich_2024_2025"]["yellows_unified"] = {"mean": round(statistics.mean(yv), 4),
    "over_rates": {str(L): round(sum(1 for v in yv if v > L) / len(yv), 4) for L in (2.5,3.5,4.5,5.5)}}
poss = [f(r["BallPossesion_home"]) for r in sr]
out["rich_2024_2025"]["possession_home_mean"] = round(statistics.mean(poss), 3)
# scored-dev window (2025-01-01..) distributions for line choice
scored_stats = [r for r in sr if r["date"] >= "2025-01-01"]
out["scored_dev_stats_n"] = len(scored_stats)
scored_all = [r for r in rich if r["date"] >= "2025-01-01"]
out["scored_dev_matches_n"] = len(scored_all)
# halves: goals 1H share from goal-event times, dev seasons pooled
dev_rows = [r for r in rows if r["season"] in DEV]
tg = sum(int(r["home_goals"]) + int(r["away_goals"]) for r in dev_rows)
htg = sum(int(r["ht_home_goals"]) + int(r["ht_away_goals"]) for r in dev_rows)
out["goals_1h_share_dev"] = round(htg / tg, 4)
out["goals_event_check"] = {"goal_events": sum(int(r["goal_events"]) for r in dev_rows), "score_goals": tg}
# per-match 1H share variance decomposition (goals): true variance of match share
shares = []
for r in dev_rows:
    t = int(r["home_goals"]) + int(r["away_goals"]); h = int(r["ht_home_goals"]) + int(r["ht_away_goals"])
    if t > 0: shares.append((h, t))
p = htg / tg
noise = statistics.mean([p * (1 - p) / t for h, t in shares])
obs_var = statistics.variance([h / t for h, t in shares])
out["goals_1h_share_var"] = {"observed_var": round(obs_var, 5), "binomial_noise_var": round(noise, 5), "true_var": round(max(obs_var - noise, 0.0), 5)}
# cards 1H share, rich dev era
ty = sum(yv); hty = sum(int(r["ht_yellows"]) for r in rich)
out["yellows_1h_share_rich_dev"] = round(hty / ty, 4) if ty else None
# split-half reliability: random half split of team-matches, corr of team means
team_rows = list(csv.DictReader((HERE.parent / "data" / "ma_botola_team_matches.csv").open()))
def split_half(team_data, col, seed=7):
    rnd = random.Random(seed)
    by = {}
    for r in team_data:
        v = f(r[col])
        if v is None: continue
        by.setdefault(r["team_id"], []).append(v)
    a, b, ids = [], [], []
    for tid, vs in by.items():
        if len(vs) < 8: continue
        idx = list(range(len(vs))); rnd.shuffle(idx)
        h1 = [vs[i] for i in idx[: len(vs) // 2]]; h2 = [vs[i] for i in idx[len(vs) // 2:]]
        a.append(statistics.mean(h1)); b.append(statistics.mean(h2)); ids.append(tid)
    if len(a) < 5: return None
    ma, mb = statistics.mean(a), statistics.mean(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    return {"n_teams": len(a), "r": round(cov / (statistics.pstdev(a) * statistics.pstdev(b)), 3)}
rel = {}
dev_team = [r for r in team_rows if r["season"] in DEV]
rel["goals_for"] = split_half(dev_team, "goals_for"); rel["goals_against"] = split_half(dev_team, "goals_against")
rich_team = [r for r in team_rows if r["season"] == "2024/2025" and r["date"] >= "2024-11-01"]
for col in ("ShotsOnTarget_for", "ShotsOnTarget_against", "corners_for", "corners_against", "total_shots_for", "total_shots_against", "yellow_for", "yellow_against", "BallPossesion_for"):
    rel[col] = split_half(rich_team, col)
out["split_half_reliability"] = rel
# entrants: first-season GF/GA vs league (descriptive, dev seasons after seed)
ent = []
seasons_sorted = DEV
prev = None
for s in seasons_sorted:
    cur = {r["team_id"] for r in team_rows if r["season"] == s}
    if prev is not None:
        for tid in cur - prev:
            mine = [r for r in team_rows if r["season"] == s and r["team_id"] == tid]
            alls = [r for r in team_rows if r["season"] == s]
            ent.append({"season": s, "team_id": tid,
                        "gf_pm": round(statistics.mean([int(r["goals_for"]) for r in mine]), 3),
                        "ga_pm": round(statistics.mean([int(r["goals_against"]) for r in mine]), 3),
                        "league_gf_pm": round(statistics.mean([int(r["goals_for"]) for r in alls]), 3)})
    prev = cur
out["entrants"] = ent
if ent:
    out["entrant_gaps"] = {"dGF": round(statistics.mean([e["gf_pm"] - e["league_gf_pm"] for e in ent]), 4),
                           "dGA": round(statistics.mean([e["ga_pm"] - e["league_gf_pm"] for e in ent]), 4), "n": len(ent)}
out["referee_nonempty_dev"] = sum(1 for r in dev_rows if r["referee"])
out["period_splits_any"] = sum(int(r["has_period_splits_content"]) for r in rows)
out["shotmap_any"] = sum(int(r["has_shotmap"]) for r in rows)
(HERE / "eda_summary.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
