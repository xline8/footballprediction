"""FI-Ykkonen EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection,
plus the Kakkonen/Ykkonen identity-break quantification.
Reads the built CSVs only. Virgin 2025 appears in inventory counts/
coverage only (its levels are inventory, NOT used to choose lines/arms
-- line selection uses the dev scored window 2022-2024 defined here).
2026 is inventory only.
Outputs: eda_summary.json + inventory_summary.json (+ charts via make_charts.py)
"""
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
M = pd.read_csv(HERE.parent / "data" / "fi_matches.csv", parse_dates=["date"])
TM = pd.read_csv(HERE.parent / "data" / "fi_team_matches.csv", parse_dates=["date"])
IDX = pd.read_csv("/home/hatch/league-remote/inbox-muse2/FI-Ykkonen/index_8969.csv")
LINEUP = {str(s): int(((IDX.season == int(s)) & (IDX.has_lineup == True)).sum())
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
        "referee": int(d.has_referee.sum()),
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
        "phases": {p: int(n) for p, n in d.phase.value_counts().items()},
    }

# ---- Per-phase levels (season x phase): Kakkonen groups + Ykkonen phases
OUT["phase_levels"] = {}
for (s, p), d in M.groupby(["season", "phase"]):
    OUT["phase_levels"][f"{s}:{p}"] = {
        "n": int(len(d)),
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "goals_pm": float(d.tot_goals.mean()),
        "home_win_rate": float((d.home_goals > d.away_goals).mean()),
        "over25_rate": float((d.tot_goals > 2.5).mean()),
    }

# ---- Era aggregates (dev only for analysis; virgin/reserve inventory only)
def era_stats(df, label):
    return {"label": label, "n": int(len(df)),
            "goals_pm": float(df.tot_goals.mean()),
            "home_win_rate": float((df.home_goals > df.away_goals).mean()),
            "draw_rate": float((df.home_goals == df.away_goals).mean()),
            "over25_rate": float((df.tot_goals > 2.5).mean()),
            "teams": int(len(set(df.home_team_id) | set(df.away_team_id)))}

kak = M[M.phase.str.startswith("kakkonen")]
ykk = M[M.phase.str.startswith("ykkonen")]
OUT["era_levels"] = {
    "kakkonen_2021_2023": era_stats(kak[kak.season <= 2023], "Kakkonen 2021-2023"),
    "ykkonen_2024": era_stats(ykk[ykk.season == 2024], "Ykkonen 2024"),
    "kakkonen_2023": era_stats(kak[kak.season == 2023], "Kakkonen 2023"),
    "kakkonen_2022_2023": era_stats(kak[kak.season >= 2022], "Kakkonen 2022-2023"),
}
# Per-group Kakkonen levels, dev era (regular groups only)
OUT["kakkonen_group_levels"] = {}
for g in ["kakkonen_a", "kakkonen_b", "kakkonen_c"]:
    d = kak[kak.phase == g]
    OUT["kakkonen_group_levels"][g] = era_stats(d, g)
    d23 = d[d.season >= 2022]
    OUT["kakkonen_group_levels"][g + "_2022_2023"] = era_stats(d23, g + " 2022-2023")

# ---- Cross-group identification (Kakkonen era)
# Regular-group membership per season: team -> group (a/b/c)
OUT["cross_group"] = {}
for s in [2021, 2022, 2023]:
    reg = M[(M.season == s) & (M.phase.isin(["kakkonen_a", "kakkonen_b", "kakkonen_c"]))]
    team_group = {}
    for _, r in reg.iterrows():
        team_group[int(r.home_team_id)] = r.phase[-1]
        team_group[int(r.away_team_id)] = r.phase[-1]
    promo = M[(M.season == s) & (M.phase.str.startswith("kakkonen_promo"))]
    cross = 0
    groups_in_promo = set()
    for _, r in promo.iterrows():
        gh, ga = team_group.get(int(r.home_team_id)), team_group.get(int(r.away_team_id))
        groups_in_promo.update([gh, ga])
        if gh is not None and ga is not None and gh != ga:
            cross += 1
    po = M[(M.season == s) & (M.phase.isin(["kakkonen_playoff", "kakkonen_promo_playoff"]))]
    cross_po = 0
    for _, r in po.iterrows():
        gh, ga = team_group.get(int(r.home_team_id)), team_group.get(int(r.away_team_id))
        if gh is not None and ga is not None and gh != ga:
            cross_po += 1
    OUT["cross_group"][str(s)] = {
        "regular_matches": int(len(reg)),
        "promo_matches": int(len(promo)),
        "promo_cross_group_matches": int(cross),
        "promo_groups_represented": sorted(g for g in groups_in_promo if g),
        "playoff_matches": int(len(po)),
        "playoff_cross_group_matches": int(cross_po),
        "regular_groups_teams": {g: int(sum(1 for t, gg in team_group.items() if gg == g))
                                 for g in ["a", "b", "c"]},
    }

# ---- Team continuity matrix (team-set overlap counts; inventory-level for 2025/2026)
seasons_sorted = sorted(M.season.unique())
team_sets = {}
for s in seasons_sorted:
    team_sets[int(s)] = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
OUT["team_continuity"] = {}
for i, s1 in enumerate(seasons_sorted):
    for s2 in seasons_sorted[i + 1:]:
        OUT["team_continuity"][f"{s1}-{s2}"] = {
            "n_common": int(len(team_sets[s1] & team_sets[s2])),
            "n_s1": int(len(team_sets[s1])), "n_s2": int(len(team_sets[s2])),
        }
# Ykkonen 2024 teams: how many played Kakkonen 2021-2023 / 2023
yk24 = team_sets[2024]
kak_all = team_sets[2021] | team_sets[2022] | team_sets[2023]
OUT["ykkonen_2024_continuity"] = {
    "n_2024": int(len(yk24)),
    "in_kakkonen_2021_2023": int(len(yk24 & kak_all)),
    "in_kakkonen_2023": int(len(yk24 & team_sets[2023])),
    "in_kakkonen_2022": int(len(yk24 & team_sets[2022])),
    "in_kakkonen_2021": int(len(yk24 & team_sets[2021])),
    "new_to_corpus_2024": int(len(yk24 - (team_sets[2021] | team_sets[2022] | team_sets[2023]))),
}

# ---- Event-feed cards by season
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

# ---- Empty-events matches: scoreless?
ee = M[~M.has_events.astype(bool)]
OUT["empty_events"] = {"n_total": int(len(ee)),
                       "n_with_goals": int(((ee.home_goals + ee.away_goals) > 0).sum()),
                       "goals_in_them": int((ee.home_goals + ee.away_goals).sum()),
                       "all_scoreless": bool(((ee.home_goals + ee.away_goals) == 0).all()),
                       "by_season": {str(s): int(n) for s, n in ee.groupby("season").size().items()}}

# ---- Awarded matches detail
aw = M[M.awarded.astype(bool)]
OUT["awarded_detail"] = [{"match_id": int(r.match_id), "season": int(r.season),
                          "date": str(r.date.date()), "phase": r.phase,
                          "home": r.home_team, "away": r.away_team,
                          "score": f"{int(r.home_goals)}-{int(r.away_goals)}",
                          "ev_goals": f"{int(r.ev_goals_home)}-{int(r.ev_goals_away)}"}
                         for _, r in aw.iterrows()]

# ---- Halves constants — DEV ERA ONLY (<= 2024), event times, awarded excluded
dev = M[(M.season <= 2024) & (~M.awarded.astype(bool))]
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
                       "note": "plain Yellows exist only from 2024; 2021-2023 event yellows are YellowRed only — NOT a frozen constant (no K market)"},
    "sot": None, "corners": None, "total_shots": None,
    "yellows_stats": None,
}
# Halves split by era (diagnostic for the break)
OUT["halves_by_era"] = {}
for label, dd in [("kakkonen_2021_2023", dev[dev.season <= 2023]),
                  ("ykkonen_2024", dev[dev.season == 2024])]:
    dde = dd[dd.has_events.astype(bool)]
    g1e = int((dde.ht_home_goals.fillna(0) + dde.ht_away_goals.fillna(0)).sum())
    gte = int((dde.home_goals + dde.away_goals).sum())
    OUT["halves_by_era"][label] = {"share_1h": g1e / gte if gte else None,
                                   "n_goals": gte, "n_matches": int(len(dde))}

# ---- Trait reliability: split-half (odd/even chronological team matches), dev era
def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return float(j.a.corr(j.b)), int(len(j))

dev_tm = TM[TM.season <= 2024]
OUT["trait_reliability_dev"] = {}
for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {"split_half_r": r, "n_teams": n}
# Per-era split-half (diagnostic)
OUT["trait_reliability_by_era"] = {}
for label, dd in [("kakkonen_2021_2023", TM[TM.season <= 2023]),
                  ("ykkonen_2024", TM[TM.season == 2024])]:
    OUT["trait_reliability_by_era"][label] = {}
    for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against")]:
        r, n = reliability(col, dd.copy())
        OUT["trait_reliability_by_era"][label][name] = {"split_half_r": r, "n_teams": n}

# Season-to-season correlation of team GF/GA per match (dev era, adjacent seasons)
season_means = {}
for s, d in dev_tm.groupby("season"):
    g = d.groupby("team_id").agg(gf=("goals_for", "mean"), ga=("goals_against", "mean"))
    season_means[int(s)] = g
OUT["season_to_season"] = {}
for s1, s2 in [(2021, 2022), (2022, 2023), (2023, 2024)]:
    j = season_means[s1].join(season_means[s2], lsuffix="_1", rsuffix="_2", how="inner")
    OUT["season_to_season"][f"{s1}-{s2}"] = {
        "n_teams_common": int(len(j)),
        "gf_corr": float(j.gf_1.corr(j.gf_2)) if len(j) > 2 else None,
        "ga_corr": float(j.ga_1.corr(j.ga_2)) if len(j) > 2 else None,
    }

# ---- Entrant transitions (dev era): team's first season in corpus after absence from previous season
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if int(s) >= 2025:  # virgin/later: do not measure
            continue
        d = TM[(TM.team_id == tid) & (TM.season == s)]
        lg = TM[TM.season == s]
        transitions.append({"season": str(s), "team_id": int(tid),
                            "team": str(d.team.iloc[0]) if len(d) else None,
                            "n_matches": int(len(d)),
                            "gf_diff": float(d.goals_for.mean() - lg.goals_for.mean()),
                            "ga_diff": float(d.goals_against.mean() - lg.goals_against.mean())})
    prev_teams = cur
OUT["entrant_transitions_dev"] = transitions
if len(transitions) >= 3:
    g = max(math.log(.8), min(math.log(1.25), sum(t["gf_diff"] for t in transitions) / len(transitions)))
    c = max(math.log(.8), min(math.log(1.25), sum(t["ga_diff"] for t in transitions) / len(transitions)))
    OUT["x2_offset_dev"] = {"n_transitions": len(transitions), "g_log": g, "c_log": c,
                            "gf_diff_mean": float(sum(t["gf_diff"] for t in transitions) / len(transitions)),
                            "ga_diff_mean": float(sum(t["ga_diff"] for t in transitions) / len(transitions))}
else:
    OUT["x2_offset_dev"] = {"n_transitions": len(transitions), "g_log": None, "c_log": None}
# Entrant transitions split by era (diagnostic: Kakkonen churn vs 2024 restructure)
OUT["entrant_transitions_by_era"] = {}
for label, ss in [("kakkonen_2022_2023", ["2022", "2023"]), ("ykkonen_2024", ["2024"])]:
    tt = [t for t in transitions if t["season"] in ss]
    OUT["entrant_transitions_by_era"][label] = {
        "n_transitions": len(tt),
        "gf_diff_mean": float(np.mean([t["gf_diff"] for t in tt])) if tt else None,
        "ga_diff_mean": float(np.mean([t["ga_diff"] for t in tt])) if tt else None,
    }

# ---- Line selection on DEV SCORED window only (2022-2024; warm-up 2021)
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}

gw = M[(M.season >= 2022) & (M.season <= 2024)]
OUT["lines"] = {"goals_ou": pick_line(gw.tot_goals, [1.5, 2.5, 3.5])}
OUT["lines_by_era"] = {
    "kakkonen_2022_2023": pick_line(M[(M.season >= 2022) & (M.season <= 2023)].tot_goals, [1.5, 2.5, 3.5]),
    "ykkonen_2024": pick_line(M[M.season == 2024].tot_goals, [1.5, 2.5, 3.5]),
}
OUT["lines_by_group_2022_2023"] = {}
for g in ["kakkonen_a", "kakkonen_b", "kakkonen_c"]:
    d = M[(M.season >= 2022) & (M.season <= 2023) & (M.phase == g)]
    OUT["lines_by_group_2022_2023"][g] = pick_line(d.tot_goals, [1.5, 2.5, 3.5])
OUT["home_win_rate_dev_scored"] = float((gw.home_goals > gw.away_goals).mean())
OUT["draw_rate_dev_scored"] = float((gw.home_goals == gw.away_goals).mean())
OUT["goals_pm_dev_scored"] = float(gw.tot_goals.mean())
OUT["dev_scored_n"] = int(len(gw))
OUT["dev_n"] = int(len(M[M.season <= 2024]))
OUT["virgin_n"] = int((M.season == 2025).sum())
OUT["reserve_n"] = int((M.season == 2026).sum())

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"league": "FI-Ykkonen", "fotmob_id": 8969, "matches_total": int(len(M)),
       "index_rows": int(len(IDX)), "csv_rows": int(len(M)), "team_rows": int(len(TM)),
       "seasons": OUT["seasons"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps(OUT, indent=1))
