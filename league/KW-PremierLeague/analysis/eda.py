"""KW-PremierLeague EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection.
Reads the built CSVs only. Virgin 2025/2026 and reserve 2026/2027 appear
in inventory counts/coverage only (levels are inventory, NOT used to
choose lines/arms — line selection uses the dev scored window
2021/2022-2024/2025 defined here; warm-up = 2021 calendar season).

Season order (canonical, frozen in PREPROCESSING.md): the dual labels
"2021" and "2021/2022" are DISTINCT seasons (disjoint match ids and
dates; Kuwait switched calendar -> split format mid-2021), ordered
2021 < 2021/2022 < 2022/2023 < 2023/2024 < 2024/2025 < 2025/2026 <
2026/2027.
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
SEASONS = ["2021", "2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
SORD = {s: i for i, s in enumerate(SEASONS)}
DEV_MAX = SORD["2024/2025"]
DEV_SCORED = ["2021/2022", "2022/2023", "2023/2024", "2024/2025"]
M = pd.read_csv(HERE.parent / "data" / "kw_matches.csv", parse_dates=["date"])
IDX = pd.read_csv(Path(__file__).resolve().parents[3] / "data_enrichment" / "fotmob_world_index.csv")
M["so"] = M.season.map(SORD)
LINEUP = {s: int((IDX[IDX.season == s].has_lineup.astype(str).str.lower() == "true").sum())
          for s in SEASONS}
IDX_N = {s: int((IDX.season == s).sum()) for s in SEASONS}
OUT = {"seasons": {}}

M["tot_goals"] = M.home_goals + M.away_goals
M["tot_yell_ev"] = M.ev_yellow_home + M.ev_yellow_away
M.loc[~M.has_events.astype(bool), "tot_yell_ev"] = np.nan
M["tot_red_ev"] = M.ev_red_home + M.ev_red_away
M.loc[~M.has_events.astype(bool), "tot_red_ev"] = np.nan

for s in SEASONS:
    d = M[M.season == s]
    OUT["seasons"][s] = {
        "n_played": int(len(d)), "n_index_rows": IDX_N[s],
        "n_unplayed_fixtures": IDX_N[s] - int(len(d)),
        "stats": int(d.has_stats_all.sum()),
        "splits": int(d.has_stats_half.sum()), "events": int(d.has_events.sum()),
        "shotmap": int(d.has_shotmap.sum()),
        "lineup": LINEUP.get(s),
        "referee": int(d.has_referee.sum()),
        "goals_pm": float(d.tot_goals.mean()) if len(d) else None,
        "sot_pm": None, "corners_pm": None, "shots_pm": None,
        "yell_ev_pm": float(d.tot_yell_ev.mean()) if d.tot_yell_ev.notna().any() else None,
        "red_ev_pm": float(d.tot_red_ev.mean()) if d.tot_red_ev.notna().any() else None,
        "yell_stats_pm": None,
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
        "awarded": int(d.awarded.sum()),
        "home_win_rate": float((d.home_goals > d.away_goals).mean()) if len(d) else None,
        "draw_rate": float((d.home_goals == d.away_goals).mean()) if len(d) else None,
        "over25_rate": float((d.tot_goals > 2.5).mean()) if len(d) else None,
        "main_n": int((d.phase == "main").sum()),
        "championship_n": int((d.phase == "championship").sum()),
        "relegation_n": int((d.phase == "relegation").sum()),
    }

# Event-feed cards by season: plain Yellow events exist in NO season
OUT["event_cards_by_season"] = {}
for s in SEASONS:
    d = M[M.season == s]
    ev = d[d.has_events.astype(bool)]
    OUT["event_cards_by_season"][s] = {
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

# Halves constants — DEV ERA ONLY (<= 2024/2025), event times, awarded excluded.
# NOTE: the event feed exists in dev ONLY in 2024/2025 (87/111 matches);
# the constant is frozen from that single dev season's event matches.
dev = M[(M.so <= DEV_MAX) & (~M.awarded.astype(bool))]
dev_ev = dev[dev.has_events.astype(bool)]
g1 = int((dev_ev.ht_home_goals.fillna(0) + dev_ev.ht_away_goals.fillna(0)).sum())
gtot = int((dev_ev.home_goals + dev_ev.away_goals).sum())
OUT["halves_dev"] = {
    "goals_events": {"share_1h": g1 / gtot if gtot else None, "n_goals": gtot,
                     "n_matches": int(len(dev_ev)),
                     "seasons_with_events": sorted(dev_ev.season.unique().tolist()),
                     "note": "event times, dev era, awarded excluded; events exist in dev only in 2024/2025"},
    "yellows_events": None,
    "yellows_note": "no plain Yellow events in ANY season (0 in corpus); no stats yellows; no K market — no constant",
    "sot": None, "corners": None, "total_shots": None,
    "yellows_stats": None,
}

# Trait reliability: split-half (odd/even chronological team matches) corr of team per-match means, dev era
tm = pd.read_csv(HERE.parent / "data" / "kw_team_matches.csv", parse_dates=["date"])
def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return float(j.a.corr(j.b)), int(len(j))
tm["so"] = tm.season.map(SORD)
dev_tm = tm[tm.so <= DEV_MAX]
OUT["trait_reliability_dev"] = {}
for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {"split_half_r": r, "n_teams": n}

# Season-to-season correlation of team GF/GA per match (dev era, adjacent seasons)
season_means = {}
for s in SEASONS[:DEV_MAX + 1]:
    d = dev_tm[dev_tm.season == s]
    season_means[s] = d.groupby("team_id").agg(gf=("goals_for", "mean"), ga=("goals_against", "mean"))
OUT["season_to_season"] = {}
for s1, s2 in zip(SEASONS[:DEV_MAX], SEASONS[1:DEV_MAX + 1]):
    j = season_means[s1].join(season_means[s2], lsuffix="_1", rsuffix="_2", how="inner")
    OUT["season_to_season"][f"{s1}->{s2}"] = {
        "n_teams_common": int(len(j)),
        "gf_corr": float(j.gf_1.corr(j.gf_2)) if len(j) > 2 else None,
        "ga_corr": float(j.ga_1.corr(j.ga_2)) if len(j) > 2 else None,
    }

# Entrant transitions (dev era): team's season in corpus after absence from previous season
prev_teams, transitions = set(), []
for s in SEASONS:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if SORD[s] > DEV_MAX:  # virgin/later: do not measure
            continue
        d = tm[(tm.team_id == tid) & (tm.season == s)]
        lg = tm[tm.season == s]
        transitions.append({"season": s, "team_id": int(tid),
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
                            "ga_diff_mean": float(sum(t["ga_diff"] for t in prior) / len(prior)),
                            "gf_negative": int(sum(1 for t in prior if t["gf_diff"] < 0)),
                            "ga_positive": int(sum(1 for t in prior if t["ga_diff"] > 0))}
else:
    OUT["x2_offset_dev"] = {"n_transitions": len(prior), "g_log": None, "c_log": None}

# Line selection on DEV SCORED window only (2021/2022-2024/2025; warm-up 2021)
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}
gw = M[M.season.isin(DEV_SCORED)]
OUT["lines"] = {"goals_ou": pick_line(gw.tot_goals, [1.5, 2.5, 3.5])}
OUT["home_win_rate_dev_scored"] = float((gw.home_goals > gw.away_goals).mean())
OUT["draw_rate_dev_scored"] = float((gw.home_goals == gw.away_goals).mean())
OUT["mean_team_goals_dev_scored"] = float(gw.tot_goals.sum() / (2 * len(gw)))
OUT["dev_scored_n"] = int(len(gw))
OUT["warmup_n"] = int((M.season == "2021").sum())
OUT["virgin_n"] = int((M.season == "2025/2026").sum())
OUT["reserve_n"] = int((M.season == "2026/2027").sum())

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"league": "KW-PremierLeague", "fotmob_id": 529, "matches_total_played": int(len(M)),
       "index_rows": int(len(IDX)), "csv_rows": int(len(M)), "team_rows": int(len(tm)),
       "seasons": OUT["seasons"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps(OUT, indent=1))

# Charts
ch = HERE / "charts"; ch.mkdir(exist_ok=True)
ss = pd.DataFrame(OUT["seasons"]).T
ss.index = SEASONS
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(ss.index, ss.goals_pm, marker="o", label="goals/match")
ax.plot(ss.index, ss.over25_rate, marker="s", label="OU2.5 over-rate")
ax.legend(); ax.set_title("KW-PremierLeague levels by season (dev <= 2024/2025; virgin 2025/2026; reserve 2026/2027)"); ax.grid(alpha=.3)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
fig.tight_layout(); fig.savefig(ch / "levels_by_season.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(ss.index, ss.stats / ss.n_played, label="stats coverage")
ax.bar(ss.index, ss.events / ss.n_played, alpha=.6, label="events coverage")
ax.legend(); ax.set_title("Feed coverage by season (stats 0% everywhere; events only from 2024/2025)"); ax.grid(alpha=.3)
plt.setp(ax.get_xticklabels(), rotation=30, ha="right")
fig.tight_layout(); fig.savefig(ch / "coverage_by_season.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
names = [k for k in OUT["trait_reliability_dev"]]
vals = [OUT["trait_reliability_dev"][k]["split_half_r"] for k in names]
ax.barh(names, vals); ax.axvline(.5, color="k", lw=.8)
ax.set_title("Trait reliability (split-half r, dev era)")
fig.tight_layout(); fig.savefig(ch / "trait_reliability.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
hv = OUT["halves_dev"]["goals_events"]["share_1h"]
ax.barh(["goals_1h_share (dev, events 2024/2025 only)"], [hv]); ax.axvline(.5, color="k", lw=.8)
ax.set_xlim(0, 0.6); ax.set_title("1H share of goals — dev era (frozen halves constant)")
fig.tight_layout(); fig.savefig(ch / "halves_constants.png", dpi=110); plt.close(fig)
print("charts done")
