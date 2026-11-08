"""IL-LigatHaAl EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection.
Reads ONLY dev-era (season_start <= 2024) data for every fitting-relevant
number. Virgin 2025/2026 appears in inventory counts/coverage/levels only
(its levels are NOT used to choose lines, arms, or windows); 2026/2027 is
inventory only. The stats feed exists only from 2025/2026, so every stats
trait, halves constant, and line for S/C/K/T is unmeasurable on dev --
that absence is itself the EDA finding (see EDA.md F-findings).
Outputs: eda_summary.json + inventory_summary.json (charts are made by
make_charts.py from eda_summary.json).
"""
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
WS = Path("~/workspace/league-work/IL-LigatHaAl").expanduser()
RAW = WS / "data_enrichment" / "fotmob_world" / "Israel" / "Ligat ha'Al"
M = pd.read_csv(HERE.parent / "data" / "il_matches.csv", parse_dates=["date"])
OUT = {"seasons": {}}

M["tot_goals"] = M.home_goals + M.away_goals
for k, cols in [("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                ("corners", ("corners_home", "corners_away")),
                ("shots", ("total_shots_home", "total_shots_away")),
                ("yell_stats", ("yellow_cards_home", "yellow_cards_away"))]:
    M[f"tot_{k}"] = M[cols[0]] + M[cols[1]]
M["tot_yell_ev"] = M.ev_yellow_home + M.ev_yellow_away + M.ev_yellowred_home + M.ev_yellowred_away
M.loc[~M.has_events, "tot_yell_ev"] = np.nan


def _lvl(series):
    v = series.dropna()
    return float(v.mean()) if len(v) >= 10 else None


for s, d in M.groupby("season"):
    OUT["seasons"][s] = {
        "n": int(len(d)), "stats": int(d.has_stats_all.sum()),
        "splits": int(d.has_stats_half.sum()), "events": int(d.has_events.sum()),
        "lineup": int(d.has_lineup.sum()),
        "referee": int(d.has_referee.sum()),
        "awarded": int(d.awarded.sum()),
        "goals_pm": float(d.tot_goals.mean()),
        "sot_pm": _lvl(d.tot_sot),
        "corners_pm": _lvl(d.tot_corners),
        "shots_pm": _lvl(d.tot_shots),
        "yell_ev_pm": _lvl(d.tot_yell_ev),
        "yell_stats_pm": _lvl(d.tot_yell_stats),
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
        "phases": {k: int(v) for k, v in d.phase.value_counts().items()},
    }
OUT["total_matches"] = int(len(M))
OUT["mismatch_match_ids"] = [int(x) for x in M.loc[M.score_events_mismatch, "match_id"]]
OUT["awarded_match_ids"] = [int(x) for x in M.loc[M.awarded, "match_id"]]

# ---- raw-JSON scan: stats keys per season, card-event kinds, referee
# names, lineup-object presence, splits All == FH+SH consistency ----
stats_keys, card_kinds, ref_names, lineup_any = {}, {}, {}, {}
splits_check = {"n": 0, "exact_shots": 0, "exact_corners": 0, "exact_sot": 0}
for sdir in sorted(RAW.iterdir()):
    y = sdir.name  # "2021-2022"
    kc, cc, rn, la = Counter(), Counter(), Counter(), 0
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
        if c.get("lineup"):
            la += 1
        if y == "2025-2026" and all(p in per for p in ("All", "FirstHalf", "SecondHalf")):
            def tot(period, key):
                for g in (per[period] or {}).get("stats", []) or []:
                    for st in g.get("stats", []) or []:
                        if st.get("key") == key:
                            v = st.get("stats") or [None, None]
                            return (float(v[0]) + float(v[1])) if v[0] is not None and v[1] is not None else None
                return None
            splits_check["n"] += 1
            for key, ck in (("total_shots", "exact_shots"), ("corners", "exact_corners"),
                            ("ShotsOnTarget", "exact_sot")):
                a, fh, sh = tot("All", key), tot("FirstHalf", key), tot("SecondHalf", key)
                if a is not None and fh is not None and sh is not None and abs(a - (fh + sh)) < 1e-9:
                    splits_check[ck] += 1
    stats_keys[y] = {f"{p}:{k}": v for (p, k), v in sorted(kc.items())}
    card_kinds[y] = dict(cc)
    ref_names[y] = {"distinct": len(rn), "top": rn.most_common(5)}
    lineup_any[y] = la
OUT["stats_keys_per_season"] = stats_keys
OUT["card_event_kinds_per_season"] = card_kinds
OUT["referees"] = ref_names
OUT["lineup_object_present_per_season"] = lineup_any
OUT["splits_consistency_2025_2026_descriptive"] = splits_check

# ---- stats-vs-events yellows agreement (2025/2026 only; both feeds
# exist there. Descriptive feed check only -- K has no dev window.) ----
both = M[M.tot_yell_stats.notna() & M.tot_yell_ev.notna()]
OUT["yell_agreement_2025_2026"] = {
    "n": int(len(both)),
    "exact": float((both.tot_yell_stats == both.tot_yell_ev).mean()) if len(both) else None,
    "mean_stats_minus_events": float((both.tot_yell_stats - both.tot_yell_ev).mean()) if len(both) else None,
}

# ---- empty-events matches ----
ee = M[~M.has_events]
OUT["empty_events"] = {
    "n_total": int(len(ee)),
    "by_season": {str(k): int(v) for k, v in ee.groupby("season").size().items()},
    "all_scoreless": bool((ee.home_goals + ee.away_goals == 0).all()) if len(ee) else None,
    "goals_total": int((ee.home_goals + ee.away_goals).sum()) if len(ee) else None,
    "goals_mean": float((ee.home_goals + ee.away_goals).mean()) if len(ee) else None,
    "n_with_stats_yellows": int(ee.tot_yell_stats.notna().sum()),
    "their_stats_yellows_mean": float(ee.tot_yell_stats.mean()) if ee.tot_yell_stats.notna().any() else None,
}

# ---- halves constants: DEV ERA ONLY (season_start <= 2024) ----
dev = M[M.season_start <= 2024]
splits_dev = dev[dev.has_stats_half]
OUT["halves_dev"] = {
    "note": "No stats period splits exist in the dev era (0 matches with "
            "FirstHalf/SecondHalf splits), so SOT/corners/total-shots/"
            "yellows 1H shares are NOT computable on dev. Only the goals "
            "share (event times) exists.",
    "splits_matches_dev": int(len(splits_dev)),
}
# goals 1H share from EVENT TIMES (dev era, matches with events,
# EXCLUDING awarded matches: their event goals do not sum to the
# awarded FT score, so their HT split is not the scored split).
g1 = gtot = nm = 0
for _, r in dev[(dev.has_events) & (~dev.awarded)].iterrows():
    f = RAW / r.season.replace("/", "-") / f"{int(r.match_id)}.json"
    d = json.load(open(f))
    evs = ((d.get("content") or {}).get("matchFacts") or {}).get("events", {}).get("events") or []
    for e in evs:
        if e.get("type") == "Goal":
            gtot += 1
            if e["time"] <= 45:
                g1 += 1
    nm += 1
OUT["halves_dev"]["goals_events"] = {"share_1h": g1 / gtot if gtot else None,
                                     "n_goals": int(gtot), "n_matches": int(nm),
                                     "note": "awarded matches excluded"}
# event-time yellow cards in dev are YellowRed only (second yellows);
# no 1H yellows constant is derived from them (wrong target).
OUT["event_yellows_dev_total_plain_yellow"] = int(
    dev[["ev_yellow_home", "ev_yellow_away"]].sum().sum())
OUT["event_yellowred_dev_total"] = int(
    dev[["ev_yellowred_home", "ev_yellowred_away"]].sum().sum())

# ---- trait reliability: split-half (odd/even chronological team
# matches) corr of team per-match means, DEV ERA ONLY ----
tm = pd.read_csv(HERE.parent / "data" / "il_team_matches.csv", parse_dates=["date"])


def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    if len(df) == 0:
        return None, 0
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return (float(j.a.corr(j.b)) if len(j) >= 3 else None), int(len(j))


dev_tm = tm[tm.season_start <= 2024]
OUT["trait_reliability_dev"] = {}
for name, col in [("goals_for", "goals_for"), ("sot_for", "sot_for"),
                  ("corners_for", "corners_for"), ("shots_for", "shots_for"),
                  ("yellow_for", "yellow_for"), ("possession", "possession")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {
        "split_half_r": r, "n_teams": n,
        "note": "not measurable on dev (target absent in dev era)" if n == 0 else None,
    }

# ---- entrant transitions (dev era): team's first season in corpus,
# or return after >=1 absent season ----
seasons_sorted = sorted(M.season.unique())
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if str(s).startswith(("2025", "2026")):
            continue
        d = tm[(tm.team_id == tid) & (tm.season == s)]
        lg = tm[tm.season == s]
        transitions.append({"season": str(s), "team_id": int(tid),
                            "gf_diff": float(d.goals_for.mean() - lg.goals_for.mean()),
                            "ga_diff": float(d.goals_against.mean() - lg.goals_against.mean())})
    prev_teams = cur
OUT["entrant_transitions_dev"] = transitions
OUT["entrant_summary_dev"] = {
    "n": len(transitions),
    "mean_gf_diff": float(np.mean([t["gf_diff"] for t in transitions])) if transitions else None,
    "mean_ga_diff": float(np.mean([t["ga_diff"] for t in transitions])) if transitions else None,
}

# ---- line selection on DEV windows only (over-rate closest to 0.5).
# Goals only: S/C/K/T have no dev scored window (no stats target in dev).
# ----
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}


gw = M[(M.season_start >= 2022) & (M.season_start <= 2024)]  # G dev scored window
OUT["lines"] = {
    "goals_ou": pick_line(gw.tot_goals, [1.5, 2.5, 3.5]),
    "sot": None, "corners": None, "shots": None, "yellows": None,
    "note": "S/C/K/T lines are null: no stats target exists in any dev "
            "season, so there is no dev window to select a line on.",
}
OUT["home_win_rate_dev"] = float((gw.home_goals > gw.away_goals).mean())
OUT["draw_rate_dev"] = float((gw.home_goals == gw.away_goals).mean())
OUT["dev_windows"] = {
    "goals": {"warm_up": ["2021/2022"], "scored": ["2022/2023", "2023/2024", "2024/2025"], "n_scored": int(len(gw))},
    "stats_markets": {"warm_up": [], "scored": [],
                      "note": "No stats season exists in dev (<=2024/2025); the stats era is 2025/2026+."},
}
# Scoring-level trend (descriptive; virgin level is NOT used to choose
# anything -- it is flagged here as a calibration risk for the gates).
OUT["goals_pm_by_season"] = {str(k): float(v) for k, v in M.groupby("season").tot_goals.mean().items()}
OUT["virgin_goals_pm_vs_dev_scored"] = {
    "virgin_2025_2026": float(M[M.season == "2025/2026"].tot_goals.mean()),
    "dev_scored_2022_2024": float(gw.tot_goals.mean()),
    "diff": float(M[M.season == "2025/2026"].tot_goals.mean() - gw.tot_goals.mean()),
}

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"seasons": OUT["seasons"], "total_matches": OUT["total_matches"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps({k: OUT[k] for k in ("seasons", "halves_dev", "trait_reliability_dev",
                                      "entrant_summary_dev", "lines", "yell_agreement_2025_2026",
                                      "empty_events", "dev_windows", "virgin_goals_pm_vs_dev_scored")}, indent=1))
print("card kinds:", OUT["card_event_kinds_per_season"])
print("referees:", OUT["referees"])
print("lineup object present:", OUT["lineup_object_present_per_season"])
print("splits consistency 2025/2026:", splits_check)
