"""QA-SecondDivision EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection.
Reads the built CSVs (league/QA-SecondDivision/data/qasd_*.csv) plus a
raw-JSON scan of the world warehouse for key coverage / splits checks.

Discipline (QA-QatarStars convention): fitting-relevant numbers are
computed on DEV-ERA data only -- G dev = 2024/2025 (warm-up rounds 1-7,
scored rounds 8-14), S/C/T/K dev = 2025/2026 (warm-up rounds 1-7, scored
rounds 8-14). The 2025/2026 season is the G VIRGIN: its goals levels
appear in the inventory table only and are NEVER used to choose G lines,
arms, or windows. The 2026/2027 season is the S/C/T/K virgin (partial,
TRANSITIONAL): its levels appear in inventory only. 2024/2025 stats-era
matches (rounds 6-14) are pre-scored-window history for S/C/T/K traits
and trailing features, never virgin data.

Outputs: eda_summary.json + inventory_summary.json (charts are made by
make_charts.py from eda_summary.json).
"""
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
MAIN = Path("/home/hatch/workspace/footballprediction")
WH = MAIN / "data_enrichment" / "fotmob_world" / "Qatar" / "Second Division"
M = pd.read_csv(HERE.parent / "data" / "qasd_matches.csv", parse_dates=["date"])
TM = pd.read_csv(HERE.parent / "data" / "qasd_team_matches.csv", parse_dates=["date"])
OUT = {"seasons": {}}

M["tot_goals"] = M.home_goals + M.away_goals
for k, cols in [("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                ("corners", ("corners_home", "corners_away")),
                ("shots", ("total_shots_home", "total_shots_away")),
                ("yell_stats", ("yellow_cards_home", "yellow_cards_away"))]:
    M[f"tot_{k}"] = M[cols[0]] + M[cols[1]]
M["tot_yell_ev"] = M.ev_yellow_home + M.ev_yellow_away + M.ev_yellowred_home + M.ev_yellowred_away
M["tot_yell_ev_1h"] = M.ev_yellow_1h
M["round_int"] = M["round"].astype(int)


def _lvl(series):
    v = series.dropna()
    return float(v.mean()) if len(v) >= 10 else None


for s, d in M.groupby("season"):
    OUT["seasons"][s] = {
        "n": int(len(d)), "stats": int(d.has_stats_all.sum()),
        "splits": int(d.has_stats_half.sum()), "events": int(d.has_events.sum()),
        "lineup": int(d.has_lineup.sum()),
        "referee": int(d.has_referee.sum()),
        "goals_pm": float(d.tot_goals.mean()),
        "home_goals_pm": float(d.home_goals.mean()),
        "away_goals_pm": float(d.away_goals.mean()),
        "sot_pm": _lvl(d.tot_sot),
        "corners_pm": _lvl(d.tot_corners),
        "shots_pm": _lvl(d.tot_shots),
        "yell_ev_pm": _lvl(d.tot_yell_ev),
        "yell_stats_pm": _lvl(d.tot_yell_stats),
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "shotmap_shots": int(d.shotmap_n.sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
        "home_win_rate": float((d.home_goals > d.away_goals).mean()),
        "draw_rate": float((d.home_goals == d.away_goals).mean()),
        "over25_rate": float((d.tot_goals > 2.5).mean()),
        "phases": {k: int(v) for k, v in d.phase.value_counts().items()},
        "league_names": {k: int(v) for k, v in d.league_name.value_counts().items()},
        "stats_by_round": {str(int(k)): int(v) for k, v in
                           d.groupby("round_int").has_stats_all.sum().items()},
    }
OUT["total_matches"] = int(len(M))
OUT["mismatch_match_ids"] = [int(x) for x in M.loc[M.score_events_mismatch, "match_id"]]
OUT["date_mismatch_ids"] = [int(x) for x in M.loc[M.date_mismatch, "match_id"]]
OUT["name_mismatch_ids"] = [int(x) for x in M.loc[M.name_mismatch, "match_id"]]

# ---- raw-JSON scan: stats keys per season, card-event kinds, referee
# names, splits All == FH+SH consistency (all seasons) ----
stats_keys, card_kinds, ref_names = {}, {}, {}
splits_check = {}
for sdir in sorted(WH.iterdir()):
    label = sdir.name.replace("-", "/")
    kc, cc, rn = Counter(), Counter(), Counter()
    sc = {"n": 0, "exact_shots": 0, "exact_corners": 0, "exact_sot": 0, "exact_yellows": 0}
    for f in sorted(sdir.glob("*.json")):
        d = json.load(open(f))
        c = d.get("content") or {}
        per = ((c.get("stats") or {}).get("Periods") or {})
        for period, block in per.items():
            for g in (block or {}).get("stats", []) or []:
                for st in g.get("stats", []) or []:
                    kc[(period, st.get("key"))] += 1
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        for e in evs:
            if e.get("type") == "Card":
                cc[e.get("card")] += 1
        r = ((((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "").strip()
        if r:
            rn[r] += 1
        if all(p in per for p in ("All", "FirstHalf", "SecondHalf")):
            def tot(period, key):
                for g in (per[period] or {}).get("stats", []) or []:
                    for st in g.get("stats", []) or []:
                        if st.get("key") == key:
                            v = st.get("stats") or [None, None]
                            return (float(v[0]) + float(v[1])) if v[0] is not None and v[1] is not None else None
                return None
            sc["n"] += 1
            for key, ck in (("total_shots", "exact_shots"), ("corners", "exact_corners"),
                            ("ShotsOnTarget", "exact_sot"), ("yellow_cards", "exact_yellows")):
                a, fh, sh = tot("All", key), tot("FirstHalf", key), tot("SecondHalf", key)
                if a is not None and fh is not None and sh is not None and abs(a - (fh + sh)) < 1e-9:
                    sc[ck] += 1
    stats_keys[label] = {f"{p}:{k}": v for (p, k), v in sorted(kc.items())}
    card_kinds[label] = dict(cc)
    ref_names[label] = {"distinct": len(rn), "top": rn.most_common(5)}
    splits_check[label] = sc
OUT["stats_keys_per_season"] = stats_keys
OUT["card_event_kinds_per_season"] = card_kinds
OUT["referees"] = ref_names
OUT["splits_consistency"] = splits_check

# ---- stats-vs-events yellows agreement, per season (both feeds) ----
OUT["yell_agreement"] = {}
for s, d in M.groupby("season"):
    both = d[d.tot_yell_stats.notna() & d.tot_yell_ev.notna()]
    diff = (both.tot_yell_stats - both.tot_yell_ev) if len(both) else pd.Series([], dtype=float)
    OUT["yell_agreement"][str(s)] = {
        "n": int(len(both)),
        "exact": int((diff == 0).sum()) if len(both) else 0,
        "stats_low": int((diff < 0).sum()) if len(both) else 0,
        "stats_high": int((diff > 0).sum()) if len(both) else 0,
        "mean_stats_minus_events": float(diff.mean()) if len(both) else None,
    }

# ---- halves constants: DEV ERA ONLY, per candidate ----
# Goals: G dev season 2024/2025, event times, all matches (0 mismatches).
# SOT/corners/shots/yellows: S/C/T/K dev season 2025/2026, period splits
# (stats) for SOT/corners/shots, event times for unified yellows.
# True SD: observed var of per-match 1H shares minus mean binomial
# sampling var p(1-p)/tot_i (J1-style decomposition); floored at 0.
def half_share(df, fh_col, tot_col):
    d = df[df[tot_col].notna() & (df[tot_col] > 0)]
    p = float(d[fh_col].sum() / d[tot_col].sum())
    shares = (d[fh_col] / d[tot_col]).astype(float)
    obs_var = float(shares.var(ddof=1)) if len(shares) > 1 else 0.0
    samp_var = float((p * (1 - p) / d[tot_col]).mean())
    true_sd = math.sqrt(max(0.0, obs_var - samp_var))
    return {"share_1h": p, "n_matches": int(len(d)), "n_total": float(d[tot_col].sum()),
            "mean_of_ratios": float(shares.mean()), "sd_of_ratios": math.sqrt(obs_var),
            "true_sd": true_sd}


M["fh_goals_total"] = M.goals_1h_total
M["fh_sot_total"] = M.fh_ShotsOnTarget_home + M.fh_ShotsOnTarget_away
M["fh_corners_total"] = M.fh_corners_home + M.fh_corners_away
M["fh_shots_total"] = M.fh_total_shots_home + M.fh_total_shots_away
M["fh_yell_stats_total"] = M.fh_yellow_cards_home + M.fh_yellow_cards_away
g_dev = M[M.season == "2024/2025"]
s_dev = M[M.season == "2025/2026"]
OUT["halves_dev"] = {
    "goals_2024_2025_events": half_share(g_dev, "fh_goals_total", "tot_goals"),
    "sot_2025_2026_splits": half_share(s_dev, "fh_sot_total", "tot_sot"),
    "corners_2025_2026_splits": half_share(s_dev, "fh_corners_total", "tot_corners"),
    "shots_2025_2026_splits": half_share(s_dev, "fh_shots_total", "tot_shots"),
    "yell_stats_2025_2026_splits": half_share(s_dev, "fh_yell_stats_total", "tot_yell_stats"),
    "yell_events_2025_2026_times": half_share(s_dev, "tot_yell_ev_1h", "tot_yell_ev"),
}

# ---- trait reliability: split-half (odd/even chronological team
# matches) corr of team per-match means. G: 2024/2025 (dev season).
# S/C/T/K: pre-scored-window stats pool = 2024/2025 stats-era matches
# (rounds 6-14) + 2025/2026 rounds 1-7 (warm-up), i.e. every stats
# match strictly before the scored block. n=8-9 teams: SE ~ 1/sqrt(n)
# ~ 0.35, so these r's are reported with their noise, not as signals.
def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    if len(df) == 0:
        return None, 0
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return (float(j.a.corr(j.b)) if len(j) >= 3 else None), int(len(j))


OUT["trait_reliability"] = {}
g_tm = TM[TM.season == "2024/2025"]
for name, col in [("goals_for", "goals_for")]:
    r, n = reliability(col, g_tm.copy())
    OUT["trait_reliability"][f"g_dev_{name}"] = {"split_half_r": r, "n_teams": n}
s_pool = TM[((TM.season == "2024/2025") & (TM.has_stats_all))
            | ((TM.season == "2025/2026") & (TM["round"].astype(int) <= 7))]
for name, col in [("goals_for", "goals_for"), ("sot_for", "sot_for"),
                  ("corners_for", "corners_for"), ("shots_for", "shots_for"),
                  ("yellow_for", "yellow_for"), ("possession", "possession")]:
    r, n = reliability(col, s_pool.copy())
    OUT["trait_reliability"][f"stats_pool_{name}"] = {"split_half_r": r, "n_teams": n}
# per-season rechecks (instability witness)
for s in ("2024/2025", "2025/2026"):
    d = TM[(TM.season == s) & (TM.has_stats_all)]
    for name, col in [("sot_for", "sot_for"), ("corners_for", "corners_for")]:
        r, n = reliability(col, d.copy())
        OUT["trait_reliability"][f"{s}_{name}"] = {"split_half_r": r, "n_teams": n}
# Chronological split-half sensitivity (first vs second half of each
# team's season-ordered matches, pooled pre-scored-window stats pool):
# with 8-9 teams the two split methods disagree wildly (see EDA.md) --
# that disagreement IS the finding: no trait reliability is demonstrable.
def reliability_chrono(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    xs, ys = [], []
    for _, g in df.groupby("team_id"):
        g = g.reset_index(drop=True)
        h = len(g) // 2
        if h >= 3 and len(g) - h >= 3:
            xs.append(float(g[col].iloc[:h].mean()))
            ys.append(float(g[col].iloc[h:].mean()))
    if len(xs) < 4:
        return None, len(xs)
    return float(pd.Series(xs).corr(pd.Series(ys))), len(xs)


for name, col in [("goals_for", "goals_for"), ("sot_for", "sot_for"),
                  ("corners_for", "corners_for"), ("shots_for", "shots_for"),
                  ("yellow_for", "yellow_for")]:
    r, n = reliability_chrono(col, s_pool.copy())
    OUT["trait_reliability"][f"chrono_stats_pool_{name}"] = {"split_half_r": r, "n_teams": n}
r, n = reliability_chrono("goals_for", g_tm.copy())
OUT["trait_reliability"]["chrono_g_dev_goals_for"] = {"split_half_r": r, "n_teams": n}

# ---- entrant transitions: team's first season in corpus ----
# G: no pre-virgin transition exists (2024/2025 is the first warehouse
# season), so the X2 arm rests on the QA-QatarStars warehouse priors.
# S/C/T/K: the 2025/2026 entrant (Al-Khor, in from the Stars League)
# is pre-virgin for the stats markets and is recorded descriptively.
seasons_sorted = sorted(M.season.unique())
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        # 2026/2027 entrants are VIRGIN-season facts for every candidate
        # and are deliberately NOT recorded here (their performance must
        # not inform any design decision); only the 2025/2026 entrant,
        # pre-virgin for the stats markets, is listed.
        if int(str(s)[:4]) >= 2026:
            continue
        d = TM[(TM.team_id == tid) & (TM.season == s)]
        lg = TM[TM.season == s]
        transitions.append({"season": str(s), "team_id": int(tid),
                            "team": str(d.team.iloc[0]),
                            "gf_diff": float(d.goals_for.mean() - lg.goals_for.mean()),
                            "ga_diff": float(d.goals_against.mean() - lg.goals_against.mean()),
                            "n_matches": int(len(d))})
    prev_teams = cur
OUT["entrant_transitions"] = transitions

# ---- line selection on DEV windows only (over-rate closest to 0.5) ----
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}


OUT["lines"] = {
    "goals_ou_2024_2025": pick_line(g_dev.tot_goals, [1.5, 2.5, 3.5]),
    "sot_2025_2026": pick_line(s_dev.tot_sot, [7.5, 8.5, 9.5]),
    "corners_2025_2026": pick_line(s_dev.tot_corners, [8.5, 9.5, 10.5]),
    "shots_2025_2026": pick_line(s_dev.tot_shots, [22.5, 23.5, 24.5]),
    "yell_ev_2025_2026": pick_line(s_dev.tot_yell_ev, [3.5, 4.5, 5.5]),
    "yell_stats_2025_2026": pick_line(s_dev.tot_yell_stats, [3.5, 4.5, 5.5]),
}
OUT["dev_windows"] = {
    "goals": {"warm_up": "2024/2025 rounds 1-7 (28 matches, never scored)",
              "scored": "2024/2025 rounds 8-14 (28 matches)",
              "virgin": "2025/2026 complete (56)", "confirmatory": "2026/2027 (untouched)"},
    "stats_markets": {"warm_up": "2025/2026 rounds 1-7 (28 matches, never scored); "
                                 "fit history also 2024/2025 stats-era rounds 6-14 (38)",
                      "scored": "2025/2026 rounds 8-14 (28 matches)",
                      "virgin": "2026/2027 partial (29, TRANSITIONAL)",
                      "confirmatory": "2026/2027 season-end re-read"},
}
OUT["home_win_rate_g_dev"] = float((g_dev.home_goals > g_dev.away_goals).mean())
OUT["draw_rate_g_dev"] = float((g_dev.home_goals == g_dev.away_goals).mean())

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"seasons": OUT["seasons"], "total_matches": OUT["total_matches"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps({k: OUT[k] for k in ("seasons", "halves_dev", "trait_reliability",
                                      "entrant_transitions", "lines", "yell_agreement",
                                      "dev_windows", "splits_consistency")}, indent=1))
print("card kinds:", OUT["card_event_kinds_per_season"])
print("referees:", OUT["referees"])
