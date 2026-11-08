"""EDA computations for LV-Virsliga. Dev-era data ONLY (seasons up to
2025; count traits on the stats era 2025). The virgin 2026 is never
read here. Halves constants are frozen from 2025 only (per the build
brief). Writes analysis/eda_summary.json."""
import csv, json, math, random, statistics
from pathlib import Path
HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader((HERE.parent / "data" / "lv_virsliga_matches.csv").open()))
def f(v): return float(v) if v not in (None, "") else None
DEV = ["2021", "2022", "2023", "2024", "2025"]
out = {}
# --- goals levels per dev season ---
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
# --- 2025 count levels (stats era, dev) ---
s25 = [r for r in rows if r["season"] == "2025"]
assert len(s25) == 180 and all(r["has_stats_all"] == "1" for r in s25)
out["stats_2025"] = {"n_matches": len(s25)}
for key, col in (("sot", "ShotsOnTarget"), ("corners", "corners"), ("total_shots", "total_shots")):
    vals = [f(r[f"{col}_home"]) + f(r[f"{col}_away"]) for r in s25]
    out["stats_2025"][key] = {"mean": round(statistics.mean(vals), 4),
        "over_rates": {str(L): round(sum(1 for v in vals if v > L) / len(vals), 4)
                       for L in (5.5, 6.5, 7.5, 8.5, 9.5, 10.5, 11.5, 24.5, 25.5, 26.5, 27.5, 28.5, 29.5)}}
yv = [f(r["yellow_home"]) + f(r["yellow_away"]) for r in s25]
out["stats_2025"]["yellows_events"] = {"mean": round(statistics.mean(yv), 4),
    "over_rates": {str(L): round(sum(1 for v in yv if v > L) / len(yv), 4) for L in (2.5, 3.5, 4.5, 5.5, 6.5)}}
ys = [f(r["yellow_stats_home"]) + f(r["yellow_stats_away"]) for r in s25]
out["stats_2025"]["yellows_stats_broken"] = {"mean": round(statistics.mean(ys), 4),
    "zero_matches": sum(1 for v in ys if v == 0)}
poss = [f(r["BallPossesion_home"]) for r in s25]
out["stats_2025"]["possession_home_mean"] = round(statistics.mean(poss), 3)
bc = [f(r["big_chance_home"]) + f(r["big_chance_away"]) for r in s25]
out["stats_2025"]["big_chance"] = {"mean": round(statistics.mean(bc), 4)}
# --- scored dev window for count markets: warm-up before 2025-05-01 ---
scored = [r for r in s25 if r["date"] >= "2025-05-01"]
warmup = [r for r in s25 if r["date"] < "2025-05-01"]
out["count_dev_window"] = {"warmup_n": len(warmup), "scored_n": len(scored),
                           "warmup_dates": [warmup[0]["date"], warmup[-1]["date"]],
                           "scored_dates": [scored[0]["date"], scored[-1]["date"]]}
for key, col in (("sot", "ShotsOnTarget"), ("corners", "corners"), ("total_shots", "total_shots")):
    vals = [f(r[f"{col}_home"]) + f(r[f"{col}_away"]) for r in scored]
    out["count_dev_window"][key] = {"mean": round(statistics.mean(vals), 4),
        "over_rates": {str(L): round(sum(1 for v in vals if v > L) / len(vals), 4)
                       for L in (7.5, 8.5, 9.5, 10.5, 25.5, 26.5, 27.5, 28.5)}}
yv_s = [f(r["yellow_home"]) + f(r["yellow_away"]) for r in scored]
out["count_dev_window"]["yellows"] = {"mean": round(statistics.mean(yv_s), 4),
    "over_rates": {str(L): round(sum(1 for v in yv_s if v > L) / len(yv_s), 4) for L in (3.5, 4.5, 5.5)}}
# --- halves constants, 2025 only ---
def share_1h(rows_, total_col, h1_col):
    tot = sum(f(r[total_col]) for r in rows_)
    h1 = sum(f(r[h1_col]) for r in rows_)
    return round(h1 / tot, 4), tot, h1
def var_decomp(rows_, total_fn, h1_fn):
    shares = [(h1_fn(r), total_fn(r)) for r in rows_]
    shares = [(h, t) for h, t in shares if t > 0]
    p = sum(h for h, t in shares) / sum(t for h, t in shares)
    noise = statistics.mean([p * (1 - p) / t for h, t in shares])
    obs = statistics.variance([h / t for h, t in shares])
    return {"p_1h": round(p, 4), "observed_var": round(obs, 5),
            "binomial_noise_var": round(noise, 5), "true_var": round(max(obs - noise, 0.0), 5)}
hc = {}
for key, col in (("sot", "ShotsOnTarget"), ("corners", "corners"), ("total_shots", "total_shots")):
    s, tot, h1 = share_1h(s25, f"{col}_home", f"{col}_home_1h")
    # totals need home+away: recompute properly
    tot = sum(f(r[f"{col}_home"]) + f(r[f"{col}_away"]) for r in s25)
    h1 = sum(f(r[f"{col}_home_1h"]) + f(r[f"{col}_away_1h"]) for r in s25)
    hc[key] = {"share_1h": round(h1 / tot, 4), "n_total": tot, "n_1h": h1}
    hc[key].update(var_decomp(s25, lambda r, c=col: f(r[f"{c}_home"]) + f(r[f"{c}_away"]),
                              lambda r, c=col: f(r[f"{c}_home_1h"]) + f(r[f"{c}_away_1h"])))
# goals 1H share from event times, 2025
tg = sum(int(r["home_goals"]) + int(r["away_goals"]) for r in s25)
htg = sum(int(r["ht_home_goals"]) + int(r["ht_away_goals"]) for r in s25)
hc["goals"] = {"share_1h": round(htg / tg, 4), "n_total": tg, "n_1h": htg}
hc["goals"].update(var_decomp(s25, lambda r: int(r["home_goals"]) + int(r["away_goals"]),
                              lambda r: int(r["ht_home_goals"]) + int(r["ht_away_goals"])))
# yellows 1H share from event times, 2025
ty = sum(yv); hty = sum(int(float(r["ht_yellows"])) for r in s25)
hc["yellow_cards"] = {"share_1h": round(hty / ty, 4), "n_total": int(ty), "n_1h": hty}
hc["yellow_cards"].update(var_decomp(s25, lambda r: int(float(r["yellow_home"]) + float(r["yellow_away"])),
                                  lambda r: int(float(r["ht_yellows"]))))
out["halves_constants_2025"] = hc
out["goals_event_check_2025"] = {"goal_events": sum(int(r["goal_events"]) for r in s25), "score_goals": tg}
# --- split-half reliability ---
team_rows = list(csv.DictReader((HERE.parent / "data" / "lv_virsliga_team_matches.csv").open()))
def split_half(team_data, col, seed=7):
    rnd = random.Random(seed)
    by = {}
    for r in team_data:
        v = f(r[col])
        if v is None: continue
        by.setdefault(r["team_id"], []).append(v)
    a, b = [], []
    for tid, vs in by.items():
        if len(vs) < 8: continue
        idx = list(range(len(vs))); rnd.shuffle(idx)
        h1 = [vs[i] for i in idx[: len(vs) // 2]]; h2 = [vs[i] for i in idx[len(vs) // 2:]]
        a.append(statistics.mean(h1)); b.append(statistics.mean(h2))
    if len(a) < 5: return None
    ma, mb = statistics.mean(a), statistics.mean(b)
    sa, sb = statistics.pstdev(a), statistics.pstdev(b)
    if sa == 0 or sb == 0: return {"n_teams": len(a), "r": None, "note": "zero variance in a half"}
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b)) / len(a)
    return {"n_teams": len(a), "r": round(cov / (statistics.pstdev(a) * statistics.pstdev(b)), 3)}
rel = {}
dev_team = [r for r in team_rows if r["season"] in DEV]
rel["goals_for"] = split_half(dev_team, "goals_for"); rel["goals_against"] = split_half(dev_team, "goals_against")
s25_team = [r for r in team_rows if r["season"] == "2025"]
for col in ("ShotsOnTarget_for", "ShotsOnTarget_against", "corners_for", "corners_against",
            "total_shots_for", "total_shots_against", "yellow_for", "yellow_against",
            "BallPossesion_for", "big_chance_for", "fouls_for"):
    rel[col] = split_half(s25_team, col)
out["split_half_reliability"] = rel
# --- entrants ---
ent = []
prev = None
for s in DEV:
    cur = {r["team_id"] for r in team_rows if r["season"] == s}
    if prev is not None:
        for tid in sorted(cur - prev):
            mine = [r for r in team_rows if r["season"] == s and r["team_id"] == tid]
            alls = [r for r in team_rows if r["season"] == s]
            ent.append({"season": s, "team_id": tid, "team": mine[0]["team"],
                        "n_matches": len(mine),
                        "gf_pm": round(statistics.mean([int(r["goals_for"]) for r in mine]), 3),
                        "ga_pm": round(statistics.mean([int(r["goals_against"]) for r in mine]), 3),
                        "league_gf_pm": round(statistics.mean([int(r["goals_for"]) for r in alls]), 3),
                        "league_ga_pm": round(statistics.mean([int(r["goals_against"]) for r in alls]), 3)})
    prev = cur
out["entrants"] = ent
if ent:
    out["entrant_gaps"] = {"dGF": round(statistics.mean([e["gf_pm"] - e["league_gf_pm"] for e in ent]), 4),
                           "dGA": round(statistics.mean([e["ga_pm"] - e["league_ga_pm"] for e in ent]), 4), "n": len(ent)}
# --- referee (2025, dev) ---
refs = {}
for r in s25:
    if r["referee"]:
        refs.setdefault(r["referee"], []).append(float(r["yellow_home"]) + float(r["yellow_away"]))
out["referee_2025"] = {"n_matches_with_ref": sum(1 for r in s25 if r["referee"]),
                       "n_referees": len(refs),
                       "per_referee": {k: {"n": len(v), "yellows_pm": round(statistics.mean(v), 2)} for k, v in sorted(refs.items())}}
out["period_splits_any"] = sum(int(r["has_period_splits_content"]) for r in rows)
out["shotmap_any"] = sum(int(r["has_shotmap"]) for r in rows)
(HERE / "eda_summary.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
