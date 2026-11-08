"""EDA computations for AT-2Liga (Phase 3). Reads only the Phase-2 CSVs
plus, for the mover check (F4), the parent tier's warehouse membership
(league_id 38 team ids per season, read from the shared index + JSON
headers in the main checkout). Writes eda_summary.json.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "at2_matches.csv"
TEAM = HERE.parent / "data" / "at2_team_matches.csv"
MAIN = Path.home() / "workspace" / "footballprediction"
rng = np.random.default_rng(20261110)

df = pd.read_csv(DATA)
tm = pd.read_csv(TEAM)
out = {}

COMPLETE = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026"]
DEV = ["2022/2023", "2023/2024", "2024/2025"]

# ---- levels -------------------------------------------------------------
df["goals"] = df.home_goals + df.away_goals
df["sot"] = df.ShotsOnTarget_home + df.ShotsOnTarget_away
df["corn"] = df.corners_home + df.corners_away
df["shots"] = df.total_shots_home + df.total_shots_away
df["yell"] = df.yellow_home + df.yellow_away
levels = {}
for s, g in df.groupby("season"):
    levels[s] = {
        "n": int(len(g)), "teams": int(len(set(g.home_team_id) | set(g.away_team_id))),
        "goals": float(g.goals.mean()), "home_goals": float(g.home_goals.mean()),
        "away_goals": float(g.away_goals.mean()),
        "hw": float((g.home_goals > g.away_goals).mean()),
        "dr": float((g.home_goals == g.away_goals).mean()),
        "btts": float(((g.home_goals > 0) & (g.away_goals > 0)).mean()),
        "over25": float((g.goals > 2.5).mean()),
        "sot": float(g.sot.mean()), "corners": float(g.corn.mean()),
        "shots": float(g.shots.mean()), "yellows": float(g.yell.mean()),
        "reds_ev": float((g.ev_red_home.fillna(0) + g.ev_red_away.fillna(0)).mean()),
        "stats_n": int(g.has_stats_all.sum()), "events_n": int(g.has_events.sum()),
    }
out["levels"] = levels
pooled = df[df.season.isin(COMPLETE)]
out["pooled"] = {k: float(pooled[k].mean()) for k in ("goals", "sot", "corn", "shots", "yell")}
out["dispersion"] = {k: float(pooled[k].var() / pooled[k].mean()) for k in ("goals", "sot", "corn", "shots", "yell")}

# ---- split-half trait reliability (career-pooled, 30 seeded splits) -----
def split_half(col_for, col_against=None, min_tm=24):
    res = {}
    for label, col in (("for", col_for), ("against", col_against)):
        if col is None:
            continue
        t = tm.dropna(subset=[col]).copy()
        t = t[t.groupby("team_id")["match_id"].transform("size") >= min_tm]
        rs = []
        for _ in range(30):
            t["half"] = rng.integers(0, 2, len(t))
            # assign halves within team by shuffling
            t["half"] = t.groupby("team_id")["match_id"].transform(
                lambda s: rng.permutation(np.arange(len(s)) % 2))
            a = t[t.half == 0].groupby("team_id")[col].mean()
            b = t[t.half == 1].groupby("team_id")[col].mean()
            j = a.index.intersection(b.index)
            if len(j) >= 8:
                rs.append(np.corrcoef(a[j], b[j])[0, 1])
        res[label] = {"r": float(np.mean(rs)), "teams": int(len(j)) if rs else 0}
    return res

out["reliability"] = {
    "goals": split_half("goals_for", "goals_against"),
    "sot": split_half("ShotsOnTarget_for", "ShotsOnTarget_against"),
    "corners": split_half("corners_for", "corners_against"),
    "shots": split_half("total_shots_for", "total_shots_against"),
    "yellows_ev": split_half("yellow_events_for", "yellow_events_against"),
    "possession": split_half("BallPossesion_for", "BallPossesion_against"),
}
# corners vs possession / box-touch-style per-match correlations
sub = df.dropna(subset=["corners_home", "BallPossesion_home"])
out["corn_corr_poss_home"] = float(np.corrcoef(sub.corners_home, sub.BallPossesion_home)[0, 1])

# ---- halves: event-derived shares + variance decomposition --------------
def halves(get_1h, get_ft, label):
    d = df[df.has_events].copy()
    one = get_1h(d); ft = get_ft(d)
    ok = ft > 0
    share_match = (one[ok] / ft[ok])
    const = float(one.sum() / ft.sum())
    # binomial noise floor: E[p(1-p)/n] with p=const
    floor = float((const * (1 - const) / ft[ok]).mean())
    true_var = float(share_match.var() - floor)
    return {"const_ratio_of_sums": const, "n_matches": int(ok.sum()),
            "obs_var": float(share_match.var()), "noise_floor": floor,
            "true_var": true_var}

out["halves_goals"] = halves(
    lambda d: d.ht_home_goals + d.ht_away_goals, lambda d: d.home_goals + d.away_goals, "goals")
out["halves_yellows"] = halves(
    lambda d: d.ev_yellow_1h_home + d.ev_yellow_1h_away, lambda d: d.ev_yellow_home + d.ev_yellow_away, "yellows")
# team-level 1H goal share split-half
tm2 = df[df.has_events].copy()
rows = []
for _, r in tm2.iterrows():
    rows.append((r.home_team_id, r.ht_home_goals, r.home_goals))
    rows.append((r.away_team_id, r.ht_away_goals, r.away_goals))
tt = pd.DataFrame(rows, columns=["team_id", "h1", "ft"])
tt = tt[tt.groupby("team_id")["ft"].transform("size") >= 24]
rs = []
for _ in range(30):
    tt["half"] = tt.groupby("team_id")["ft"].transform(lambda s: rng.permutation(np.arange(len(s)) % 2))
    ga = tt[tt.half == 0].groupby("team_id")[["h1", "ft"]].sum()
    gb = tt[tt.half == 1].groupby("team_id")[["h1", "ft"]].sum()
    a = ga.h1 / ga.ft.clip(lower=1)
    b = gb.h1 / gb.ft.clip(lower=1)
    j = a.index.intersection(b.index)
    rs.append(np.corrcoef(a[j], b[j])[0, 1])
out["halves_goals_team_share_r"] = float(np.mean(rs))

# ---- movers (F4): entrant classes vs parent corpus ----------------------
import csv as _csv
idx = [r for r in _csv.DictReader((MAIN / "data_enrichment" / "fotmob_world_index.csv").open())
       if r["league_id"] == "38"]
bl_members = {}
for r in idx:
    d = json.loads((MAIN / r["path"]).read_text())
    g = d.get("general") or {}
    s = bl_members.setdefault(r["season"], set())
    s.add((g.get("homeTeam") or {}).get("id")); s.add((g.get("awayTeam") or {}).get("id"))
seasons_sorted = sorted(df.season.unique())
B_TEAMS = {1915, 10248, 1921, 1952, 292054}  # Liefering, Austria Wien II, Sturm Graz II, Rapid Wien II, FC Juniors OOe (LASK)
movers = []
for i, s in enumerate(seasons_sorted):
    if i == 0:
        continue
    cur = set(df[df.season == s].home_team_id) | set(df[df.season == s].away_team_id)
    prev = set(df[df.season == seasons_sorted[i - 1]].home_team_id) | set(df[df.season == seasons_sorted[i - 1]].away_team_id)
    prev_bl = bl_members.get(seasons_sorted[i - 1], set())
    for tid in cur - prev:
        cls = "relegated_from_bundesliga" if tid in prev_bl else "from_below_or_returning"
        movers.append({"season": s, "team_id": int(tid), "class": cls, "is_bteam": tid in B_TEAMS})
out["entrants"] = movers
# first-season GF/GA gap vs league mean (goals per team-match)
tm_all = tm.copy()
lg_mean = tm_all.groupby("season")[["goals_for", "goals_against"]].mean()
gaps = {}
for cls in ("relegated_from_bundesliga", "from_below_or_returning"):
    gf, ga, n = [], [], 0
    for m in movers:
        if m["class"] != cls or m["season"] == "2026/2027":
            continue
        t = tm_all[(tm_all.team_id == m["team_id"]) & (tm_all.season == m["season"])]
        if len(t) < 10:
            continue
        gf.append(t.goals_for.mean() - lg_mean.loc[m["season"], "goals_for"])
        ga.append(t.goals_against.mean() - lg_mean.loc[m["season"], "goals_against"])
        n += 1
    if n:
        gaps[cls] = {"n_entrants": n, "gf_gap": float(np.mean(gf)), "ga_gap": float(np.mean(ga))}
out["mover_gaps"] = gaps
out["bteam_seasons"] = {str(t): sorted(df[(df.home_team_id == t) | (df.away_team_id == t)].season.unique().tolist())
                        for t in sorted(B_TEAMS)}

# ---- primary-line candidates: dev over-rates ----------------------------
dev = df[df.season.isin(DEV)]
out["dev_over_rates"] = {
    "goals_2.5": float((dev.goals > 2.5).mean()),
    "sot": {str(L): float((dev.dropna(subset=["sot"]).sot > L).mean()) for L in (7.5, 8.5, 9.5)},
    "corners": {str(L): float((dev.dropna(subset=["corn"]).corn > L).mean()) for L in (8.5, 9.5, 10.5)},
    "cards": {str(L): float((dev.dropna(subset=["yell"]).yell > L).mean()) for L in (3.5, 4.5, 5.5)},
    "shots": {str(L): float((dev.dropna(subset=["shots"]).shots > L).mean()) for L in (17.5, 18.5, 19.5)},
    "dev_n_stats": int(dev.has_stats_all.sum()), "dev_n_total": int(len(dev)),
    "virgin_n_stats": int(df[df.season == "2025/2026"].has_stats_all.sum()),
    "virgin_n_total": int((df.season == "2025/2026").sum()),
}
out["referee_named"] = int(df.referee.notna().sum())
out["name_variants"] = {str(k): sorted(set(v)) for k, v in
                        df.groupby("home_team_id")["home_team"].unique().items() if len(set(v)) > 1}

(HERE / "eda_summary.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
