"""SE-Ettan EDA (steps 1-4): inventory, levels, era/coverage, halves
constants, trait reliability, entrant transitions, line selection.

Reads ONLY seasons <= 2025. The 2026 rows that exist in the built CSVs
(program precedent: reserve season built but never read) are filtered
out at load and never enter any number in this file -- no 2026 raw JSON
is opened either. Dev era is <= 2024; virgin 2025 appears in inventory
counts/coverage/levels ONLY (its levels are NOT used to choose any
line, arm, or window). The stats feed is 0% in every season, so every
stats trait, halves constant, and line for S/C/K/T is unmeasurable on
dev -- that absence is itself the EDA finding (see EDA.md F-findings).

Outputs: eda_summary.json + inventory_summary.json (charts are made by
make_charts.py from eda_summary.json).
"""
import csv
import json
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).parent
WS = Path("~/workspace/league-work/SE-Ettan").expanduser()
RAW = WS / "data_enrichment" / "Sweden" / "Ettan"
INDEX = Path("~/league-remote/inbox-muse2/SE-Ettan/index_169.csv").expanduser()

M = pd.read_csv(HERE.parent / "data" / "se_matches.csv", parse_dates=["date"])
# 2026 is the confirmatory reserve: never read, never counted.
assert set(M.season.unique()) <= {2021, 2022, 2023, 2024, 2025, 2026}
M = M[M.season <= 2025].copy()
TM = pd.read_csv(HERE.parent / "data" / "se_team_matches.csv", parse_dates=["date"])
TM = TM[TM.season <= 2025].copy()
OUT = {"seasons": {}, "note_2026": "Season 2026 rows exist in the built "
        "CSVs but were filtered out at load and never read in any "
        "analysis, fit, or gate (confirmatory reserve)."}

M["tot_goals"] = M.home_goals + M.away_goals
M["tot_yell_ev"] = (M.ev_yellow_home + M.ev_yellow_away
                    + M.ev_yellowred_home + M.ev_yellowred_away)
M.loc[~M.has_events, "tot_yell_ev"] = np.nan


def _lvl(series):
    v = series.dropna()
    return float(v.mean()) if len(v) >= 10 else None


for s, d in M.groupby("season"):
    OUT["seasons"][str(s)] = {
        "n": int(len(d)), "stats": int(d.has_stats_all.sum()),
        "splits": int(d.has_stats_half.sum()), "events": int(d.has_events.sum()),
        "lineup_11": int(d.has_lineup.sum()),
        "referee": int(d.has_referee.sum()),
        "goals_pm": float(d.tot_goals.mean()),
        "goals_pm_norra": float(d.loc[d.phase == "norra", "tot_goals"].mean()),
        "goals_pm_sodra": float(d.loc[d.phase == "sodra", "tot_goals"].mean()),
        "home_goals_pm": float(d.home_goals.mean()),
        "away_goals_pm": float(d.away_goals.mean()),
        "yell_ev_pm": _lvl(d.tot_yell_ev),
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "teams_norra": int(len(set(d.loc[d.phase == "norra", "home_team_id"])
                            | set(d.loc[d.phase == "norra", "away_team_id"]))),
        "teams_sodra": int(len(set(d.loc[d.phase == "sodra", "home_team_id"])
                            | set(d.loc[d.phase == "sodra", "away_team_id"]))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
        "phases": {k: int(v) for k, v in d.phase.value_counts().items()},
        "rounds": int(d["round"].nunique()),
    }
OUT["total_matches_le_2025"] = int(len(M))
OUT["mismatch_match_ids"] = [int(x) for x in M.loc[M.score_events_mismatch, "match_id"]]

# ---- raw-JSON scan (2021-2025 only; 2026 never opened): stats keys,
# event types, card-event kinds, referee names, lineup-object presence,
# shotmap, team-name spellings per id, and the 2021 played/unplayed
# verification against the index ----
stats_keys, card_kinds, event_kinds, ref_names = {}, {}, {}, {}
lineup_obj, shotmap_n, played_raw = {}, {}, {}
id_names, unplayed_2021 = {}, []
for sdir in sorted(RAW.iterdir()):
    yr = int(sdir.name)
    if yr > 2025:
        continue
    label = str(yr)
    kc, cc, ec, rn = Counter(), Counter(), Counter(), Counter()
    la, sm, played = 0, 0, 0
    for f in sorted(sdir.glob("*.json")):
        d = json.load(open(f))
        c = d.get("content") or {}
        gen, hdr = d.get("general") or {}, d.get("header") or {}
        st = hdr.get("status") or {}
        if st.get("finished") and st.get("scoreStr"):
            played += 1
        elif yr == 2021:
            unplayed_2021.append(int(gen.get("matchId") or f.stem))
        per = ((c.get("stats") or {}).get("Periods") or {})
        for period, block in per.items():
            for g in (block or {}).get("stats", []) or []:
                for stt in g.get("stats", []) or []:
                    kc[(period, stt.get("key"))] += 1
        evs = ((c.get("matchFacts") or {}).get("events") or {}).get("events") or []
        for e in evs:
            ec[e.get("type")] += 1
            if e.get("type") == "Card":
                cc[e.get("card")] += 1
        r = ((((c.get("matchFacts") or {}).get("infoBox") or {}).get("Referee")
              or {}).get("text") or "").strip()
        if r:
            rn[r] += 1
        if c.get("lineup"):
            la += 1
        if ((c.get("shotmap") or {}).get("shots")):
            sm += 1
        for side in ("homeTeam", "awayTeam"):
            t = gen.get(side) or {}
            if t.get("id") is not None:
                id_names.setdefault(int(t["id"]), Counter())[t.get("name")] += 1
    stats_keys[label] = {f"{p}:{k}": v for (p, k), v in sorted(kc.items())}
    card_kinds[label] = dict(cc)
    event_kinds[label] = dict(ec)
    ref_names[label] = {"distinct": len(rn), "top": rn.most_common(5)}
    lineup_obj[label] = la
    shotmap_n[label] = sm
    played_raw[label] = played
OUT["stats_keys_per_season"] = stats_keys
OUT["card_event_kinds_per_season"] = card_kinds
OUT["event_kinds_per_season"] = event_kinds
OUT["referees"] = ref_names
OUT["lineup_object_present_per_season"] = lineup_obj
OUT["shotmap_matches_per_season"] = shotmap_n
OUT["played_per_season_raw_json"] = played_raw
OUT["csv_vs_raw_played_match"] = {
    s: bool(OUT["seasons"][s]["n"] == played_raw[s]) for s in played_raw}
OUT["team_name_variants"] = {
    str(tid): dict(c) for tid, c in id_names.items() if len(c) > 1}
OUT["n_team_ids_le_2025"] = len(id_names)

# ---- 2021 anomaly: unplayed fixtures vs the index (raw JSON is ground
# truth; index carries a "0-0" placeholder score for every unplayed row)
# ----
idx_rows = list(csv.DictReader(open(INDEX)))
idx21 = {r["match_id"]: r for r in idx_rows if r["season"] == "2021"}
un_scores, bands = Counter(), Counter()
for mid in unplayed_2021:
    r = idx21[str(mid)]
    un_scores[r["score"]] += 1
    d = json.load(open(RAW / "2021" / f"{mid}.json"))
    ln = (d.get("general") or {}).get("leagueName") or ""
    rd = int((d.get("general") or {}).get("matchRound"))
    grp = "norra" if "Norra" in ln else "sodra"
    band = "rounds_1_12" if rd <= 12 else "rounds_13_30"
    bands[(grp, band)] += 1
pl = M[M.season == 2021]
for grp in ("norra", "sodra"):
    for band, lo, hi in (("rounds_1_12", 1, 12), ("rounds_13_30", 13, 30)):
        bands[(grp, band, "played")] = int(
            len(pl[(pl.phase == grp) & (pl["round"] >= lo) & (pl["round"] <= hi)]))
        bands[(grp, band, "unplayed")] = int(bands.get((grp, band), 0))
OUT["anomaly_2021"] = {
    "index_rows_2021": len(idx21),
    "played_csv": int(len(pl)),
    "unplayed_raw": len(unplayed_2021),
    "unplayed_index_scores": dict(un_scores),
    "played_by_group": {g: int((pl.phase == g).sum()) for g in ("norra", "sodra")},
    "unplayed_by_group": {
        "norra": int(bands[("norra", "rounds_1_12", "unplayed")]
                     + bands[("norra", "rounds_13_30", "unplayed")]),
        "sodra": int(bands[("sodra", "rounds_1_12", "unplayed")]
                     + bands[("sodra", "rounds_13_30", "unplayed")]),
    },
    "by_group_round_band": {
        f"{g}_{b}": {"played": int(bands[(g, b, "played")]),
                     "unplayed": int(bands[(g, b, "unplayed")])}
        for g in ("norra", "sodra") for b in ("rounds_1_12", "rounds_13_30")},
    "date_range_played": [str(pl.date.min().date()), str(pl.date.max().date())],
    "note": "Unplayed fixtures exist in EVERY round (1-30) of both "
            "groups; they are heaviest in rounds 1-12 (136 of 192 "
            "fixtures unplayed) and lighter in rounds 13-30 (82 of 288).",
}

# ---- halves constants: DEV ERA ONLY. Goals 1H share from EVENT TIMES
# (2022-2024: 2021 has no events at all, so no 1H share exists for it).
# The single mismatched match (awarded 4398485, corrupt event goals)
# is excluded from the goals share; its header score stays authoritative
# everywhere else. Yellows 1H share is descriptive evidence for K only.
# ----
dev = M[M.season <= 2024]
g = dev[(dev.has_events) & (~dev.score_events_mismatch)]
OUT["halves_dev"] = {
    "note": "No stats period splits exist in ANY season (0 matches), "
            "so SOT/corners/total-shots/yellows 1H shares from splits "
            "are NOT computable. Only event-time shares exist (goals, "
            "and yellows as descriptive evidence for K).",
    "splits_matches_dev": int(dev.has_stats_half.sum()),
    "goals_events": {
        "share_1h": float(g.goals_1h_total.sum() / g.tot_goals.sum()),
        "n_goals": int(g.tot_goals.sum()), "n_matches": int(len(g)),
        "excluded_mismatch_matches": int(dev.score_events_mismatch.sum()),
        "per_season": {
            str(s): {
                "share_1h": float(dd.goals_1h_total.sum() / dd.tot_goals.sum()),
                "n_goals": int(dd.tot_goals.sum()), "n_matches": int(len(dd)),
            } for s, dd in g.groupby("season")},
    },
    "yellows_events_descriptive": {
        "share_1h": float(g.ev_yellow_1h.sum() / g.tot_yell_ev.sum()),
        "n_yellows": int(g.tot_yell_ev.sum()), "n_matches": int(len(g)),
        "per_season": {
            str(s): {
                "share_1h": float(dd.ev_yellow_1h.sum() / dd.tot_yell_ev.sum()),
                "n_yellows": int(dd.tot_yell_ev.sum()),
            } for s, dd in g.groupby("season")},
    },
}
OUT["event_cards_dev_totals"] = {
    "plain_yellow": int(dev[["ev_yellow_home", "ev_yellow_away"]].sum().sum()),
    "yellowred": int(dev[["ev_yellowred_home", "ev_yellowred_away"]].sum().sum()),
    "red": int(dev[["ev_red_home", "ev_red_away"]].sum().sum()),
}

# ---- trait reliability: split-half (odd/even chronological team
# matches) corr of team per-match means, DEV ERA ONLY ----
def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    if len(df) == 0:
        return None, 0
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return (float(j.a.corr(j.b)) if len(j) >= 3 else None), int(len(j))


dev_tm = TM[TM.season <= 2024]
scored_tm = TM[(TM.season >= 2022) & (TM.season <= 2024)]
OUT["trait_reliability_dev"] = {}
for name, col in [("goals_for", "goals_for"), ("goals_against", "goals_against")]:
    r_all, n_all = reliability(col, dev_tm.copy())
    r_sc, n_sc = reliability(col, scored_tm.copy())
    OUT["trait_reliability_dev"][name] = {
        "split_half_r_dev_2021_2024": r_all, "n_teams_dev": n_all,
        "split_half_r_scored_2022_2024": r_sc, "n_teams_scored": n_sc,
    }
for name, col in [("sot_for", "sot_for"), ("corners_for", "corners_for"),
                  ("shots_for", "shots_for"), ("yellow_for", "yellow_for"),
                  ("possession", "possession")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {
        "split_half_r_dev_2021_2024": r, "n_teams_dev": n,
        "note": "not measurable on dev (target absent in dev era)" if n == 0 else None,
    }
# Event-derived yellows trait (descriptive evidence for K): build
# per-team-match event yellows from se_matches (team_matches yellow_for
# is the unified stats target, which is missing everywhere in SE).
yrows = []
for _, m in M.iterrows():
    if not m.has_events:
        continue
    yrows.append({"team_id": m.home_team_id, "date": m.date, "match_id": m.match_id,
                  "season": m.season,
                  "yell_ev": m.ev_yellow_home + m.ev_yellowred_home})
    yrows.append({"team_id": m.away_team_id, "date": m.date, "match_id": m.match_id,
                  "season": m.season,
                  "yell_ev": m.ev_yellow_away + m.ev_yellowred_away})
Y = pd.DataFrame(yrows)
r_y, n_y = reliability("yell_ev", Y[Y.season <= 2024].copy())
OUT["trait_reliability_dev"]["event_yellows_for"] = {
    "split_half_r_dev_2022_2024": r_y, "n_teams_dev": n_y,
    "note": "Descriptive only (K is not-buildable per BRIEF): event-"
            "derived yellows exist 2022-2024 but there is no stats "
            "feed to validate them against, and 2021 has no events.",
}
# Season-to-season correlation of team goals-for means (dev, overlapping teams)
OUT["season_to_season_gf_corr_dev"] = {}
for s1, s2 in [(2021, 2022), (2022, 2023), (2023, 2024)]:
    a = TM[TM.season == s1].groupby("team_id")["goals_for"].mean()
    b = TM[TM.season == s2].groupby("team_id")["goals_for"].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    OUT["season_to_season_gf_corr_dev"][f"{s1}_{s2}"] = {
        "r": float(j.a.corr(j.b)) if len(j) >= 3 else None,
        "n_teams": int(len(j)),
    }

# ---- entrant transitions (dev era): team's FIRST season in the corpus.
# 2021 is the baseline (all 32 teams are corpus entrants there, not
# transitions). 2022-2024 transitions only; 2025 is the virgin season.
# ----
seasons_sorted = sorted(M.season.unique())
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if int(s) >= 2025:
            continue
        d = TM[(TM.team_id == tid) & (TM.season == s)]
        lg = TM[TM.season == s]
        transitions.append({"season": str(s), "team_id": int(tid),
                            "team": str(d.team.iloc[0]),
                            "phase": str(d.phase.iloc[0]),
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
    "per_season": {
        str(s): {
            "n": int(sum(1 for t in transitions if t["season"] == str(s))),
            "mean_gf_diff": float(np.mean([t["gf_diff"] for t in transitions
                                           if t["season"] == str(s)])),
            "mean_ga_diff": float(np.mean([t["ga_diff"] for t in transitions
                                           if t["season"] == str(s)])),
        } for s in (2022, 2023, 2024)},
    "note": "Entrants mix relegated Superettan sides (strong) and "
            "promoted Division 2 sides (weak); no systematic tilt.",
}
# Group stability: any team switching norra<->sodra between seasons (<=2025)?
team_phase = {}
for s in seasons_sorted:
    for tid in set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id):
        ph = tuple(sorted(set(
            M[(M.season == s) & ((M.home_team_id == tid) | (M.away_team_id == tid))].phase)))
        team_phase.setdefault(int(tid), {})[int(s)] = ph
switches = []
for tid, mp in team_phase.items():
    ss = sorted(mp)
    for a, b in zip(ss, ss[1:]):
        if mp[a] != mp[b]:
            switches.append({"team_id": tid, "from_season": a, "to_season": b,
                             "from_phase": mp[a], "to_phase": mp[b]})
OUT["group_switches_le_2025"] = switches

# ---- line selection on DEV windows only (over-rate closest to 0.5).
# Goals only: S/C/K/T have no dev scored window (no stats target ever).
# ----
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}


gw = M[(M.season >= 2022) & (M.season <= 2024)]  # G dev scored window
gd = M[M.season <= 2024]  # all dev incl. partial 2021
OUT["lines"] = {
    "goals_ou_scored_2022_2024": pick_line(gw.tot_goals, [1.5, 2.5, 3.5]),
    "goals_ou_all_dev_incl_2021": pick_line(gd.tot_goals, [1.5, 2.5, 3.5]),
    "sot": None, "corners": None, "shots": None, "yellows": None,
    "note": "S/C/K/T lines are null: no stats target exists in any "
            "season, so there is no dev window to select a line on.",
}
OUT["home_win_rate_scored"] = float((gw.home_goals > gw.away_goals).mean())
OUT["draw_rate_scored"] = float((gw.home_goals == gw.away_goals).mean())
OUT["home_goals_mean_scored"] = float(gw.home_goals.mean())
OUT["away_goals_mean_scored"] = float(gw.away_goals.mean())
OUT["goals_distribution_scored"] = {
    str(k): int(v) for k, v in gw.tot_goals.value_counts().sort_index().items()}
OUT["ou25_by_group_scored"] = {
    g: float(((gw[gw.phase == g].home_goals + gw[gw.phase == g].away_goals) > 2.5).mean())
    for g in ("norra", "sodra")}
OUT["dev_windows"] = {
    "goals": {"warm_up": ["2021 (partial: 262 played of 480 fixtures; no events)"],
              "scored": ["2022", "2023", "2024"], "n_scored": int(len(gw)),
              "n_warm_up": int(len(pl))},
    "stats_markets": {"warm_up": [], "scored": [],
                      "note": "No stats season exists in any season "
                              "(stats feed 0% in 2021-2025); the stats "
                              "era never starts."},
}

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
inv = {"seasons": OUT["seasons"], "total_matches_le_2025": OUT["total_matches_le_2025"],
       "note_2026": OUT["note_2026"]}
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1))
print(json.dumps({k: OUT[k] for k in ("seasons", "halves_dev", "trait_reliability_dev",
                                      "entrant_summary_dev", "lines", "anomaly_2021",
                                      "dev_windows", "csv_vs_raw_played_match",
                                      "event_cards_dev_totals")}, indent=1))
print("card kinds:", OUT["card_event_kinds_per_season"])
print("event kinds:", OUT["event_kinds_per_season"])
print("referees:", OUT["referees"])
print("lineup objects:", OUT["lineup_object_present_per_season"])
print("team-name variants:", OUT["team_name_variants"])
print("group switches:", OUT["group_switches_le_2025"])
