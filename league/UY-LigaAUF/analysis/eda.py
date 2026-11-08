"""UY-LigaAUF EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection.
Reads ONLY dev-era (season_start <= 2024) data for every fitting-relevant
number. Virgin 2025 appears in inventory counts/coverage/levels only
(its levels are NOT used to choose lines, arms, or windows); 2026 is
inventory only. The stats feed is absent in EVERY season, so every stats
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
WS = Path("~/workspace/league-work/UY-LigaAUF").expanduser()
RAW = WS / "data_enrichment" / "fotmob_world" / "Uruguay" / "Liga AUF Uruguaya"
M = pd.read_csv(HERE.parent / "data" / "uy_matches.csv", parse_dates=["date"])
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
        "goals_pm": float(d.tot_goals.mean()),
        "sot_pm": _lvl(d.tot_sot),
        "corners_pm": _lvl(d.tot_corners),
        "shots_pm": _lvl(d.tot_shots),
        "yell_ev_pm": _lvl(d.tot_yell_ev),
        "yell_stats_pm": _lvl(d.tot_yell_stats),
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
        "awarded": int(d.awarded.sum()),
        "phases": {k: int(v) for k, v in d.phase.value_counts().items()},
        "home_win_rate": float((d.home_goals > d.away_goals).mean()),
        "draw_rate": float((d.home_goals == d.away_goals).mean()),
        "away_win_rate": float((d.home_goals < d.away_goals).mean()),
        "ou25_over_rate": float((d.tot_goals > 2.5).mean()),
    }
OUT["total_matches"] = int(len(M))
OUT["mismatch_match_ids"] = [int(x) for x in M.loc[M.score_events_mismatch, "match_id"]]
OUT["awarded_match_ids"] = [int(x) for x in M.loc[M.awarded, "match_id"]]

# ---- raw-JSON scan: stats keys per season, card-event kinds, referee
# names, lineup-object presence ----
stats_keys, card_kinds, ref_names, lineup_any, shotmap_any = {}, {}, {}, {}, {}
for sdir in sorted(RAW.iterdir()):
    label = sdir.name  # calendar year "2021" .. "2026"
    kc, cc, rn, la, sm = Counter(), Counter(), Counter(), 0, 0
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
        if ((c.get("shotmap") or {}).get("shots")):
            sm += 1
    stats_keys[label] = {f"{p}:{k}": v for (p, k), v in sorted(kc.items())}
    card_kinds[label] = dict(cc)
    ref_names[label] = {"distinct": len(rn), "top": rn.most_common(5)}
    lineup_any[label] = la
    shotmap_any[label] = sm
OUT["stats_keys_per_season"] = stats_keys
OUT["card_event_kinds_per_season"] = card_kinds
OUT["referees"] = ref_names
OUT["lineup_object_present_per_season"] = lineup_any
OUT["shotmap_present_per_season"] = shotmap_any

# ---- empty-events matches ----
ee = M[~M.has_events]
OUT["empty_events"] = {
    "n_total": int(len(ee)),
    "by_season": {str(k): int(v) for k, v in ee.groupby("season").size().items()},
    "all_scoreless": bool((ee.home_goals + ee.away_goals == 0).all()) if len(ee) else None,
    "goals_total": int((ee.home_goals + ee.away_goals).sum()) if len(ee) else None,
    "goals_mean": float((ee.home_goals + ee.away_goals).mean()) if len(ee) else None,
}

# ---- halves constants: DEV ERA ONLY (season_start <= 2024) ----
dev = M[M.season_start <= 2024]
splits_dev = dev[dev.has_stats_half]
OUT["halves_dev"] = {
    "note": "No stats period splits exist in ANY season (0 matches with "
            "FirstHalf/SecondHalf splits in the whole warehouse), so "
            "SOT/corners/total-shots/yellows 1H shares are NOT computable "
            "on dev. Only the goals share (event times) exists.",
    "splits_matches_dev": int(len(splits_dev)),
}
g = dev[(dev.has_events) & (~dev.score_events_mismatch)]
OUT["halves_dev"]["goals_events"] = {
    "share_1h": float(g.goals_1h_total.sum() / g.tot_goals.sum()),
    "n_goals": int(g.tot_goals.sum()), "n_matches": int(len(g)),
    "excluded_mismatch_matches": int(dev.score_events_mismatch.sum()),
}
# 1H share per dev season (stability check, not a separate constant)
OUT["halves_dev"]["goals_events_by_season"] = {
    str(s): {"share_1h": float(d.goals_1h_total.sum() / d.tot_goals.sum()),
             "n_goals": int(d.tot_goals.sum())}
    for s, d in g.groupby("season")
}
OUT["event_yellows_dev_total_plain_yellow"] = int(
    dev[["ev_yellow_home", "ev_yellow_away"]].sum().sum())
OUT["event_yellowred_dev_total"] = int(
    dev[["ev_yellowred_home", "ev_yellowred_away"]].sum().sum())
OUT["event_red_dev_total"] = int(
    dev[["ev_red_home", "ev_red_away"]].sum().sum())

# ---- trait reliability: split-half (odd/even chronological team
# matches) corr of team per-match means, DEV ERA ONLY ----
tm = pd.read_csv(HERE.parent / "data" / "uy_team_matches.csv", parse_dates=["date"])


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
for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against"),
                  ("sot_for", "sot_for"), ("corners_for", "corners_for"),
                  ("shots_for", "shots_for"), ("yellow_for", "yellow_for"),
                  ("possession", "possession")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {
        "split_half_r": r, "n_teams": n,
        "note": "not measurable on dev (target absent in dev era)" if n == 0 else None,
    }

# ---- season-to-season reliability of team attack/defence (dev era):
# per-season team GF/GA means, corr across consecutive seasons ----
def season_team_means(col):
    return (dev_tm.groupby(["season", "team_id"])[col].mean()
            .unstack(0))
for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against")]:
    piv = season_team_means(col)
    pairs = []
    yrs = sorted(piv.columns)
    for a, b in zip(yrs, yrs[1:]):
        j = piv[[a, b]].dropna()
        pairs.append({"seasons": f"{a}-{b}", "r": float(j[a].corr(j[b])) if len(j) >= 3 else None,
                      "n_teams": int(len(j))})
    OUT.setdefault("season_to_season_dev", {})[name] = pairs

# ---- entrant transitions (dev era): team absent in the immediately
# preceding season (first corpus season 2021 yields no entrants) ----
seasons_sorted = sorted(M.season.unique())
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if int(str(s)[:4]) >= 2025:
            continue
        d = tm[(tm.team_id == tid) & (tm.season == s)]
        lg = tm[tm.season == s]
        transitions.append({"season": str(s), "team_id": int(tid),
                            "team": str(d.team.iloc[0]),
                            "gf_diff": float(d.goals_for.mean() - lg.goals_for.mean()),
                            "ga_diff": float(d.goals_against.mean() - lg.goals_against.mean())})
    prev_teams = cur
OUT["entrant_transitions_dev"] = transitions
OUT["entrant_summary_dev"] = {
    "n": len(transitions),
    "mean_gf_diff": float(np.mean([t["gf_diff"] for t in transitions])) if transitions else None,
    "mean_ga_diff": float(np.mean([t["ga_diff"] for t in transitions])) if transitions else None,
    "gf_negative_count": int(sum(1 for t in transitions if t["gf_diff"] < 0)) if transitions else None,
    "ga_positive_count": int(sum(1 for t in transitions if t["ga_diff"] > 0)) if transitions else None,
}
# dev scored mean team goals (needed for the frozen entrant log offsets)
gw_dev = dev_tm[dev_tm.season_start >= 2022]
OUT["entrant_summary_dev"]["dev_scored_mean_team_goals"] = float(gw_dev.goals_for.mean())
OUT["entrant_summary_dev"]["dev_scored_n_matches"] = int(len(dev[dev.season_start >= 2022]))

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
OUT["away_win_rate_dev"] = float((gw.home_goals < gw.away_goals).mean())
OUT["dev_windows"] = {
    "goals": {"warm_up": ["2021"], "scored": ["2022", "2023", "2024"], "n_scored": int(len(gw))},
    "stats_markets": {"warm_up": [], "scored": [],
                      "note": "No stats season exists in dev (<=2024) or "
                              "anywhere else; the stats feed is 0% in "
                              "2021-2026."},
}

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"seasons": OUT["seasons"], "total_matches": OUT["total_matches"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps({k: OUT[k] for k in ("seasons", "halves_dev", "trait_reliability_dev",
                                      "season_to_season_dev", "entrant_summary_dev",
                                      "lines", "empty_events", "dev_windows")}, indent=1))
print("card kinds:", OUT["card_event_kinds_per_season"])
print("referees:", OUT["referees"])
print("shotmap:", OUT["shotmap_present_per_season"])
print("stats keys:", {k: len(v) for k, v in OUT["stats_keys_per_season"].items()})
