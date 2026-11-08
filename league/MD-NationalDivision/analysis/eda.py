"""MD-NationalDivision EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection.
Reads the built CSVs only. Virgin 2025 appears in inventory counts/
coverage only (its levels are inventory, NOT used to choose lines/arms
-- line selection uses the dev scored window 2022-2024 defined here).
2026 is inventory only.
Outputs: eda_summary.json + inventory_summary.json + charts/*.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
M = pd.read_csv(HERE.parent / "data" / "md_matches.csv", parse_dates=["date"])
IDX = pd.read_csv("/home/hatch/league-remote/inbox-muse2/MD-NationalDivision/index_231.csv")
def _yr(season): return int(str(season).split("/")[0])
M["yr"] = M.season.map(_yr)
IDX["yr"] = IDX.season.map(_yr)
LINEUP = {str(s): int(((IDX.yr == _yr(s)) & (IDX.has_lineup.astype(str).str.lower() == "true")).sum())
          for s in M.season.unique()}
OUT = {"seasons": {}}

M["tot_goals"] = M.home_goals + M.away_goals
M["tot_yell_ev"] = M.ev_yellow_home + M.ev_yellow_away
M.loc[~M.has_events.astype(bool), "tot_yell_ev"] = np.nan
M["tot_yell_plain"] = M.ev_yellow_home + M.ev_yellow_away - M.ev_yellowred_home - M.ev_yellowred_away
M.loc[~M.has_events.astype(bool), "tot_yell_plain"] = np.nan

for s, d in M.groupby("season"):
    OUT["seasons"][str(s)] = {
        "n": int(len(d)), "stats": int(d.has_stats_all.sum()),
        "splits": int(d.has_stats_half.sum()), "events": int(d.has_events.sum()),
        "shotmap": int(d.has_shotmap.sum()),
        "lineup": LINEUP.get(str(s)),
        "goals_pm": float(d.tot_goals.mean()),
        "sot_pm": None, "corners_pm": None, "shots_pm": None,
        "yell_ev_pm": float(d.tot_yell_ev.mean()) if d.tot_yell_ev.notna().any() else None,
        "yell_plain_pm": float(d.tot_yell_plain.mean()) if d.tot_yell_plain.notna().any() else None,
        "yell_stats_pm": None,
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
        "awarded": int(d.awarded.sum()),
        "home_win_rate": float((d.home_goals > d.away_goals).mean()),
        "draw_rate": float((d.home_goals == d.away_goals).mean()),
        "over25_rate": float((d.tot_goals > 2.5).mean()),
        "main_n": int((d.phase == "main").sum()),
    }

# Event-feed yellows by season: plain Yellow events exist in NO season
OUT["event_cards_by_season"] = {}
for s, d in M.groupby("season"):
    ev = d[d.has_events.astype(bool)]
    OUT["event_cards_by_season"][str(s)] = {
        "n_events_matches": int(len(ev)),
        "yellow_plain_total": int(d.ev_yellow_home.sum() + d.ev_yellow_away.sum()
                                  - d.ev_yellowred_home.sum() - d.ev_yellowred_away.sum()),
        "yellowred_total": int(d.ev_yellowred_home.sum() + d.ev_yellowred_away.sum()),
        "red_total": int(d.ev_red_home.sum() + d.ev_red_away.sum()),
    }

# Empty-events matches: are they scoreless? (missing, never zero)
ee = M[~M.has_events.astype(bool)]
OUT["empty_events"] = {"n_total": int(len(ee)),
                       "n_with_goals": int(((ee.home_goals + ee.away_goals) > 0).sum()),
                       "goals_in_them": int((ee.home_goals + ee.away_goals).sum()),
                       "all_scoreless": bool(((ee.home_goals + ee.away_goals) == 0).all())}

# Halves constants — DEV ERA ONLY (<= 2024), event times, awarded excluded
dev = M[(M.yr <= 2024) & (~M.awarded.astype(bool))]
dev_ev = dev[dev.has_events.astype(bool)]
g1 = int((dev_ev.ht_home_goals.fillna(0) + dev_ev.ht_away_goals.fillna(0)).sum())
gtot = int((dev_ev.home_goals + dev_ev.away_goals).sum())
y1 = int((dev_ev.ht_yellow_home.fillna(0) + dev_ev.ht_yellow_away.fillna(0)).sum())
ytot = int((dev_ev.ev_yellow_home + dev_ev.ev_yellow_away).sum())
OUT["halves_dev"] = {
    "goals_events": {"share_1h": g1 / gtot if gtot else None, "n_goals": gtot,
                     "n_matches": int(len(dev_ev)), "note": "event times, dev era, awarded excluded"},
    "yellows_events": {"share_1h": y1 / ytot if ytot else None, "n_yellows": ytot,
                       "n_matches": int(len(dev_ev)),
                       "note": "no plain Yellow events in any season; event yellows are YellowRed only — NOT a frozen constant (no K market)"},
    "sot": None, "corners": None, "total_shots": None,
    "yellows_stats": None,
}

# Trait reliability: split-half (odd/even chronological team matches) corr of team per-match means, dev era
tm = pd.read_csv(HERE.parent / "data" / "md_team_matches.csv", parse_dates=["date"])
def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return float(j.a.corr(j.b)), int(len(j))
tm["yr"] = tm.season.map(_yr)
dev_tm = tm[tm.yr <= 2024]
OUT["trait_reliability_dev"] = {}
for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {"split_half_r": r, "n_teams": n}

# Season-to-season correlation of team GF/GA per match (dev era, adjacent seasons)
season_means = {}
for s, d in dev_tm.groupby("season"):
    g = d.groupby("team_id").agg(gf=("goals_for", "mean"), ga=("goals_against", "mean"))
    season_means[_yr(s)] = g
OUT["season_to_season"] = {}
for s1, s2 in [(2021, 2022), (2022, 2023), (2023, 2024)]:
    j = season_means[s1].join(season_means[s2], lsuffix="_1", rsuffix="_2", how="inner")
    OUT["season_to_season"][f"{s1}-{s2}"] = {
        "n_teams_common": int(len(j)),
        "gf_corr": float(j.gf_1.corr(j.gf_2)) if len(j) > 2 else None,
        "ga_corr": float(j.ga_1.corr(j.ga_2)) if len(j) > 2 else None,
    }

# Entrant transitions (dev era): team's first season in corpus after absence from previous season
seasons_sorted = sorted(M.season.unique())
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if _yr(s) >= 2025:  # virgin/later: do not measure
            continue
        d = tm[(tm.team_id == tid) & (tm.season == s)]
        lg = tm[tm.season == s]
        transitions.append({"season": str(s), "team_id": int(tid),
                            "team": str(d.team.iloc[0]) if len(d) else None,
                            "n_matches": int(len(d)),
                            "gf_diff": float(d.goals_for.mean() - lg.goals_for.mean()),
                            "ga_diff": float(d.goals_against.mean() - lg.goals_against.mean())})
    prev_teams = cur
OUT["entrant_transitions_dev"] = transitions
prior = [t for t in transitions]
if len(prior) >= 3:
    import math
    g = max(math.log(.8), min(math.log(1.25), sum(t["gf_diff"] for t in prior) / len(prior)))
    c = max(math.log(.8), min(math.log(1.25), sum(t["ga_diff"] for t in prior) / len(prior)))
    OUT["x2_offset_dev"] = {"n_transitions": len(prior), "g_log": g, "c_log": c,
                            "gf_diff_mean": float(sum(t["gf_diff"] for t in prior) / len(prior)),
                            "ga_diff_mean": float(sum(t["ga_diff"] for t in prior) / len(prior))}
else:
    OUT["x2_offset_dev"] = {"n_transitions": len(prior), "g_log": None, "c_log": None}

# Line selection on DEV SCORED window only (2022/2023–2024/2025; warm-up 2021/2022)
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}
gw = M[(M.yr >= 2022) & (M.yr <= 2024)]
OUT["lines"] = {"goals_ou": pick_line(gw.tot_goals, [1.5, 2.5, 3.5])}
OUT["home_win_rate_dev_scored"] = float((gw.home_goals > gw.away_goals).mean())
OUT["draw_rate_dev_scored"] = float((gw.home_goals == gw.away_goals).mean())
OUT["dev_scored_n"] = int(len(gw))
OUT["virgin_n"] = int((M.season.astype(str) == "2025/2026").sum())
OUT["reserve_n"] = int((M.season.astype(str) == "2026/2027").sum())

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"league": "MD-NationalDivision", "fotmob_id": 231, "matches_total": int(len(M)),
       "index_rows": 556, "csv_rows": int(len(M)), "team_rows": int(len(tm)),
       "seasons": OUT["seasons"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps(OUT, indent=1))

# Charts
ch = HERE / "charts"; ch.mkdir(exist_ok=True)
ss = pd.DataFrame(OUT["seasons"]).T
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(ss.index, ss.goals_pm, marker="o", label="goals/match")
ax.plot(ss.index, ss.over25_rate, marker="s", label="OU2.5 over-rate")
ax.legend(); ax.set_title("MD-NationalDivision levels by season (dev seasons 2021/2022–2024/2025; virgin 2025/2026; reserve 2026/2027)"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(ch / "levels_by_season.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(ss.index, ss.stats / ss.n, label="stats coverage")
ax.bar(ss.index, ss.events / ss.n, alpha=.6, label="events coverage")
ax.legend(); ax.set_title("Feed coverage by season (stats 0% everywhere)"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(ch / "coverage_by_season.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
names = [k for k in OUT["trait_reliability_dev"]]
vals = [OUT["trait_reliability_dev"][k]["split_half_r"] for k in names]
ax.barh(names, vals); ax.axvline(.5, color="k", lw=.8)
ax.set_title("Trait reliability (split-half r, dev era)")
fig.tight_layout(); fig.savefig(ch / "trait_reliability.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
hv = OUT["halves_dev"]["goals_events"]["share_1h"]
ax.barh(["goals_1h_share (dev, events)"], [hv]); ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.6); ax.set_title("1H share of goals — dev era (frozen halves constant)")
fig.tight_layout(); fig.savefig(ch / "halves_constants.png", dpi=110); plt.close(fig)
print("charts done")
