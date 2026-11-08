"""CH-ChallengeLeague EDA (steps 1-4): inventory, levels, era/coverage,
halves constants, trait reliability, entrant transitions, line selection.
Reads ONLY dev-era + structure data for fitting-relevant numbers; virgin
2025/2026 appears in inventory counts/coverage only (its levels are NOT
used to choose lines/arms -- line selection uses dev windows defined here).
2026/2027 is inventory only.
Outputs: eda_summary.json + charts/*.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
M = pd.read_csv(HERE.parent / "data" / "ch_matches.csv", parse_dates=["date"])
OUT = {"seasons": {}}

M["tot_goals"] = M.home_goals + M.away_goals
for k, cols in [("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                ("corners", ("corners_home", "corners_away")),
                ("shots", ("total_shots_home", "total_shots_away")),
                ("yell_stats", ("yellow_cards_home", "yellow_cards_away"))]:
    M[f"tot_{k}"] = M[cols[0]] + M[cols[1]]
M["tot_yell_ev"] = M.ev_yellow_home + M.ev_yellow_away + M.ev_yellowred_home + M.ev_yellowred_away
M.loc[~M.has_events, "tot_yell_ev"] = np.nan

for s, d in M.groupby("season"):
    OUT["seasons"][s] = {
        "n": int(len(d)), "stats": int(d.has_stats_all.sum()),
        "splits": int(d.has_stats_half.sum()), "events": int(d.has_events.sum()),
        "goals_pm": float(d.tot_goals.mean()),
        "sot_pm": float(d.tot_sot.mean()) if d.tot_sot.notna().any() else None,
        "corners_pm": float(d.tot_corners.mean()) if d.tot_corners.notna().any() else None,
        "shots_pm": float(d.tot_shots.mean()) if d.tot_shots.notna().any() else None,
        "yell_ev_pm": float(d.tot_yell_ev.mean()) if d.tot_yell_ev.notna().any() else None,
        "yell_stats_pm": float(d.tot_yell_stats.mean()) if d.tot_yell_stats.notna().any() else None,
        "teams": int(len(set(d.home_team_id) | set(d.away_team_id))),
        "xg_rows": int(d.expected_goals_home.notna().sum()),
        "score_mismatch": int(d.score_events_mismatch.sum()),
    }

# stats-vs-events yellows agreement (rich era, both present)
both = M[M.tot_yell_stats.notna() & M.tot_yell_ev.notna()]
OUT["yell_agreement"] = {
    "n": int(len(both)),
    "exact": float((both.tot_yell_stats == both.tot_yell_ev).mean()),
    "mean_stats_minus_events": float((both.tot_yell_stats - both.tot_yell_ev).mean()),
}
# empty-events matches in rich era have stats yellows > 0 -> events empty = missing, not zero
ee = M[(~M.has_events) & M.tot_yell_stats.notna()]
OUT["empty_events"] = {"n_total": int((~M.has_events).sum()),
                       "n_rich_with_stats_yellows": int(len(ee)),
                       "their_stats_yellows_mean": float(ee.tot_yell_stats.mean()) if len(ee) else None,
                       "all_scoreless": bool((ee.home_goals + ee.away_goals == 0).all()) if len(ee) else None}

# Halves constants — DEV ERA ONLY (<= 2024/2025)
dev = M[M.season_start <= 2024]
splits = dev[dev.has_stats_half]
def share(df, fh_cols, sh_cols):
    fh = df[fh_cols[0]] + df[fh_cols[1]]; sh = df[sh_cols[0]] + df[sh_cols[1]]
    tot = fh + sh
    ok = tot > 0
    return float(fh[ok].sum() / tot[ok].sum()), int(ok.sum())
OUT["halves_dev"] = {}
for name, fhc, shc in [("sot", ("fh_ShotsOnTarget_home", "fh_ShotsOnTarget_away"), ("sh_ShotsOnTarget_home", "sh_ShotsOnTarget_away")),
                       ("corners", ("fh_corners_home", "fh_corners_away"), ("sh_corners_home", "sh_corners_away")),
                       ("total_shots", ("fh_total_shots_home", "fh_total_shots_away"), ("sh_total_shots_home", "sh_total_shots_away")),
                       ("yellows_stats", ("fh_yellow_cards_home", "fh_yellow_cards_away"), ("sh_yellow_cards_home", "sh_yellow_cards_away"))]:
    v, n = share(splits, fhc, shc)
    OUT["halves_dev"][name] = {"share_1h": v, "n_matches_with_total_gt0": n}
# goals + yellows 1H share from EVENT TIMES (dev era, matches with events)
import json as _json
RAW = Path("~/workspace/league-work/CH-ChallengeLeague/raw/extracted/Switzerland/Challenge League").expanduser()
g1 = gtot = y1 = ytot = nm = 0
for _, r in dev[dev.has_events].iterrows():
    f = RAW / r.season.replace("/", "-") / f"{int(r.match_id)}.json"
    d = _json.load(open(f))
    evs = ((d.get("content") or {}).get("matchFacts") or {}).get("events", {}).get("events") or []
    gm = 0
    for e in evs:
        if e.get("type") == "Goal":
            gtot += 1; gm += 1
            if e["time"] <= 45: g1 += 1
        if e.get("type") == "Card" and e.get("card") in ("Yellow", "YellowRed"):
            ytot += 1
            if e["time"] <= 45: y1 += 1
    nm += 1
OUT["halves_dev"]["goals_events"] = {"share_1h": g1 / gtot if gtot else None, "n_goals": gtot, "n_matches": nm}
# NOTE: event-feed yellows are ~absent in CH dev era (see yell_agreement):
# no event-time yellows constant is derived; the stats-splits constant above is used.
OUT["event_yellows_dev_total"] = int(ytot)

# Trait reliability: split-half (odd/even chronological team matches) corr of team per-match means, dev era
tm = pd.read_csv(HERE.parent / "data" / "ch_team_matches.csv", parse_dates=["date"])
def reliability(col, df):
    df = df[df[col].notna()].sort_values(["team_id", "date", "match_id"])
    df = df.assign(idx=df.groupby("team_id").cumcount())
    a = df[df.idx % 2 == 0].groupby("team_id")[col].mean()
    b = df[df.idx % 2 == 1].groupby("team_id")[col].mean()
    j = pd.concat([a, b], axis=1, keys=["a", "b"]).dropna()
    return float(j.a.corr(j.b)), int(len(j))
dev_tm = tm[tm.season_start <= 2024]
OUT["trait_reliability_dev"] = {}
for name, col in [("goals_for", "goals_for"), ("sot_for", "sot_for"),
                  ("corners_for", "corners_for"), ("shots_for", "shots_for"),
                  ("yellow_for", "yellow_for"), ("possession", "possession")]:
    r, n = reliability(col, dev_tm.copy())
    OUT["trait_reliability_dev"][name] = {"split_half_r": r, "n_teams": n}

# Entrant transitions (dev era): team's first season in corpus after absence
seasons_sorted = sorted(M.season.unique())
prev_teams, transitions = set(), []
for s in seasons_sorted:
    cur = set(M[M.season == s].home_team_id) | set(M[M.season == s].away_team_id)
    entrants = cur - prev_teams if prev_teams else set()
    for tid in entrants:
        if s.startswith(("2025", "2026")):  # virgin/later: do not measure
            continue
        d = tm[(tm.team_id == tid) & (tm.season == s)]
        lg = tm[tm.season == s]
        transitions.append({"season": s, "team_id": int(tid),
                              "gf_diff": float(d.goals_for.mean() - lg.goals_for.mean()),
                              "ga_diff": float(d.goals_against.mean() - lg.goals_against.mean())})
    prev_teams = cur
OUT["entrant_transitions_dev"] = transitions

# Line selection on DEV windows only (over-rate closest to 0.5)
def pick_line(values, lines):
    v = pd.Series(values).dropna()
    rates = {L: float((v > L).mean()) for L in lines}
    best = min(lines, key=lambda L: abs(rates[L] - 0.5))
    return {"over_rates": {str(L): rates[L] for L in lines}, "primary": best, "n": int(len(v))}
gw = M[(M.season_start >= 2022) & (M.season_start <= 2024)]  # G/K dev scored window
sw = M[M.season_start == 2024]                                # stats dev scored window (2024/2025)
OUT["lines"] = {
    "goals_ou": pick_line(gw.tot_goals, [1.5, 2.5, 3.5]),
    "sot": pick_line(sw.tot_sot, [7.5, 8.5, 9.5, 10.5]),
    "corners": pick_line(sw.tot_corners, [8.5, 9.5, 10.5, 11.5]),
    "shots": pick_line(sw.tot_shots, [22.5, 24.5, 26.5, 28.5]),
    "yellows": pick_line(sw.tot_yell_stats, [3.5, 4.5, 5.5]),
}
OUT["home_win_rate_dev"] = float(((gw.home_goals > gw.away_goals)).mean())
OUT["draw_rate_dev"] = float(((gw.home_goals == gw.away_goals)).mean())

(HERE / "eda_summary.json").write_text(json.dumps(OUT, indent=1))
print(json.dumps(OUT, indent=1))

# Charts
ch = HERE / "charts"; ch.mkdir(exist_ok=True)
ss = pd.DataFrame(OUT["seasons"]).T
fig, ax = plt.subplots(figsize=(8, 4))
for col, lab in [("goals_pm", "goals"), ("sot_pm", "SOT"), ("corners_pm", "corners"), ("yell_pm", "yellows (events)")]:
    key = "yell_ev_pm" if col == "yell_pm" else col
    ax.plot(ss.index, ss[key], marker="o", label=lab)
ax.legend(); ax.set_title("CH-ChallengeLeague levels by season"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(ch / "levels_by_season.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(ss.index, ss.stats / ss.n, label="stats coverage")
ax.bar(ss.index, ss.events / ss.n, alpha=.6, label="events coverage")
ax.legend(); ax.set_title("Feed coverage by season"); ax.grid(alpha=.3)
fig.tight_layout(); fig.savefig(ch / "coverage_by_season.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
names = [k for k in OUT["halves_dev"]]
vals = [OUT["halves_dev"][k]["share_1h"] for k in names]
ax.barh(names, vals); ax.axvline(.5, color="k", lw=.8)
ax.set_title("1H share of totals — dev era (frozen halves constants)")
fig.tight_layout(); fig.savefig(ch / "halves_constants.png", dpi=110); plt.close(fig)
fig, ax = plt.subplots(figsize=(7, 4))
rn = list(OUT["trait_reliability_dev"])
ax.barh(rn, [OUT["trait_reliability_dev"][k]["split_half_r"] for k in rn])
ax.set_title("Trait reliability (split-half r, dev era)")
fig.tight_layout(); fig.savefig(ch / "trait_reliability.png", dpi=110); plt.close(fig)
print("charts done")
