"""EDA computations for NO-Eliteserien (Phase 3). Reads the Phase-2 CSVs,
writes eda_summary.json. Split-half reliabilities: career-pooled per team,
30 seeded random splits averaged, teams with >=24 team-matches; ratio
traits are ratios of sums. Halves: variance decomposition of the per-match
1H share against the binomial noise floor, on the complete period-split
era (complete seasons 2023-2025)."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
m = pd.read_csv(DATA / "no_matches.csv", parse_dates=["date"], dtype={"season": str})
t = pd.read_csv(DATA / "no_team_matches.csv", parse_dates=["date"], dtype={"season": str})
rng = np.random.default_rng(20261109)
out = {}

for c in ["home_goals", "away_goals"]:
    m[c] = m[c].astype(float)
m["goals"] = m.home_goals + m.away_goals
for k, cols in [("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                ("corners", ("corners_home", "corners_away")),
                ("shots", ("total_shots_home", "total_shots_away")),
                ("yellow", ("yellow_home", "yellow_away")),
                ("red", ("red_home", "red_away")),
                ("xg", ("expected_goals_home", "expected_goals_away"))]:
    m[k] = m[cols[0]] + m[cols[1]]

seasons = {}
for s, g in m.groupby("season"):
    seasons[s] = dict(n=int(len(g)), goals=float(g.goals.mean()),
                      home_goals=float(g.home_goals.mean()), away_goals=float(g.away_goals.mean()),
                      hw=float((g.home_goals > g.away_goals).mean()), dr=float((g.home_goals == g.away_goals).mean()),
                      aw=float((g.home_goals < g.away_goals).mean()),
                      btts=float(((g.home_goals > 0) & (g.away_goals > 0)).mean()),
                      over25=float((g.goals > 2.5).mean()),
                      sot=float(g.sot.mean()), corners=float(g.corners.mean()),
                      shots=float(g.shots.mean()), yellow=float(g.yellow.mean()),
                      red=float(g.red.mean()), xg=float(g.xg.mean()),
                      xg_calib=float(g.goals.sum() / g.xg.sum()))
out["seasons"] = seasons
out["levels"] = dict(goals=float(m.goals.mean()), sot=float(m.sot.mean()),
                     corners=float(m.corners.mean()), shots=float(m.shots.mean()),
                     yellow=float(m.yellow.mean()), red=float(m.red.mean()), xg=float(m.xg.mean()),
                     home_adv=float(m.home_goals.mean() - m.away_goals.mean()))
out["dispersion"] = {k: float(m[k].var() / m[k].mean()) for k in ["goals", "sot", "corners", "shots", "yellow"]}
out["phase_counts"] = m.phase.value_counts().to_dict()
out["teams_per_season"] = {s: int(len(set(g.home_team_id) | set(g.away_team_id))) for s, g in m.groupby("season")}
out["coverage"] = {s: dict(n=int(len(g)), half=float(g.has_stats_half.mean()),
                           box=float(g.touches_opp_box_home.notna().mean()),
                           referee=float(g.referee.notna().mean()),
                           shotmap=float(g.has_shotmap.mean())) for s, g in m.groupby("season")}
out["score_events_mismatch"] = int(m.score_events_mismatch.sum())

def split_half(df, value_fn, min_matches=24, reps=30):
    rs = []
    teams = [tid for tid, g in df.groupby("team_id") if len(g) >= min_matches]
    for rep in range(reps):
        a, b = [], []
        for tid in teams:
            g = df[df.team_id == tid]
            idx = rng.permutation(len(g))
            h1, h2 = g.iloc[idx[: len(g) // 2]], g.iloc[idx[len(g) // 2:]]
            va, vb = value_fn(h1), value_fn(h2)
            if va is not None and vb is not None and np.isfinite(va) and np.isfinite(vb):
                a.append(va); b.append(vb)
        if len(a) >= 8:
            rs.append(np.corrcoef(a, b)[0, 1])
    return dict(r=float(np.mean(rs)), n_teams=len(teams)) if rs else None

def mean_of(col):
    return lambda g: g[col].mean()
def ratio_of(num, den):
    return lambda g: (g[num].sum() / g[den].sum()) if g[den].sum() > 0 else None

rel = {}
for name, fn in [("goals_for", mean_of("goals_for")), ("goals_against", mean_of("goals_against")),
                 ("shots_for", mean_of("shots_for")), ("sot_for", mean_of("sot_for")),
                 ("corners_for", mean_of("corners_for")), ("yellow_for", mean_of("yellow_for")),
                 ("xg_for", mean_of("xg_for")),
                 ("box_touches_for", lambda g: g.box_touches_for.mean() if g.box_touches_for.notna().sum() >= 12 else None),
                 ("box_touches_against", lambda g: g.box_touches_against.mean() if g.box_touches_against.notna().sum() >= 12 else None),
                 ("big_chance_for", mean_of("big_chance_for"))]:
    rel[name] = split_half(t, fn)
ratio_traits = {}
ratio_traits["setplay_xg_share"] = split_half(
    t.assign(sp_for=None) if False else t, lambda g: None)  # placeholder replaced below
# ratio traits need match-level xG split columns; compute from match table per team
tm = []
for _, r in m.iterrows():
    for side, opp in (("home", "away"), ("away", "home")):
        tm.append(dict(team_id=r[f"{side}_team_id"],
                       sp_xg=r[f"expected_goals_set_play_{side}"], tot_xg=r[f"expected_goals_{side}"],
                       sm_xg=r[f"sm_xg_{side}"], sm_shots=r[f"sm_shots_{side}"],
                       goals=r[f"{side}_goals"], sot=r[f"ShotsOnTarget_{side}"],
                       shots=r[f"total_shots_{side}"],
                       sm_xgot=r[f"sm_xgot_{side}"], sm_xgot_n=r[f"sm_xgot_n_{side}"],
                       date=r["date"], season=r["season"]))
tm = pd.DataFrame(tm)
ratio_traits["setplay_xg_share"] = split_half(tm, ratio_of("sp_xg", "tot_xg"))
ratio_traits["xg_per_shot"] = split_half(tm, ratio_of("sm_xg", "sm_shots"))
ratio_traits["finishing_goals_minus_xg"] = split_half(tm, lambda g: g.goals.mean() - g.tot_xg.mean())
ratio_traits["sot_rate"] = split_half(tm, ratio_of("sot", "shots"))
ratio_traits["goals_per_shot"] = split_half(tm, ratio_of("goals", "shots"))
era = tm[tm.date >= "2025-01-01"]
ratio_traits["xgot_per_shot_era2025"] = split_half(era, ratio_of("sm_xgot", "sm_xgot_n"), min_matches=20)
out["reliability"] = rel
out["ratio_traits"] = ratio_traits

# referee split-half: cards per match by referee (>=20 matches)
mm = m[m.referee.notna()].copy()
mm["cards"] = mm.yellow
def ref_split(reps=30):
    rs = []
    refs = [r for r, g in mm.groupby("referee") if len(g) >= 20]
    for rep in range(reps):
        a, b = [], []
        for r in refs:
            g = mm[mm.referee == r]
            idx = rng.permutation(len(g))
            a.append(g.iloc[idx[: len(g) // 2]].cards.mean()); b.append(g.iloc[idx[len(g) // 2:]].cards.mean())
        rs.append(np.corrcoef(a, b)[0, 1])
    return dict(r=float(np.mean(rs)), n_refs=len(refs), n_matches=int(len(mm)))
out["referees"] = ref_split()
out["referee_coverage"] = float(m.referee.notna().mean())

# territorial correlation with corners (team-match level, box era 2024+)
bt = t[t.box_touches_for.notna()]
out["corners_territorial"] = dict(
    corr_corners_boxtouches=float(bt[["corners_for", "box_touches_for"]].corr().iloc[0, 1]),
    corr_corners_possession=float(bt[["corners_for", "possession"]].corr().iloc[0, 1]), n=int(len(bt)))

# halves: period-split era, complete seasons only
era_m = m[m.season.isin(["2023", "2024", "2025"]) & m.has_stats_half].copy()
def half_share(fh_h, fh_a, ft_h, ft_a):
    g = era_m.dropna(subset=[fh_h, fh_a, ft_h, ft_a]).copy()
    g["ft"] = g[ft_h] + g[ft_a]; g["fh"] = g[fh_h] + g[fh_a]
    g = g[g.ft > 0]
    share = float(g.fh.sum() / g.ft.sum())
    p = g.fh / g.ft
    noise = float(np.mean(p * (1 - p) / g.ft)) if False else float(np.mean(share * (1 - share) / g.ft))
    return dict(share=share, true_var=float(p.var(ddof=1) - noise), n=int(len(g)))
out["halves"] = dict(
    goals=half_share("fh_expected_goals_home", "fh_expected_goals_away", "expected_goals_home", "expected_goals_away") if False else None,
    goals_events=None)
# goals halves from HT score (events) on same era
g = era_m.dropna(subset=["ht_home_goals", "ht_away_goals"]).copy()
g["ft"] = g.home_goals + g.away_goals; g["fh"] = g.ht_home_goals + g.ht_away_goals
g = g[g.ft > 0]; p = g.fh / g.ft; share = float(g.fh.sum() / g.ft.sum())
out["halves"]["goals"] = dict(share=share, true_var=float(p.var(ddof=1) - np.mean(share * (1 - share) / g.ft)), n=int(len(g)))
for name, fh, ft in [("sot", ("fh_ShotsOnTarget_home", "fh_ShotsOnTarget_away"), ("ShotsOnTarget_home", "ShotsOnTarget_away")),
                     ("corners", ("fh_corners_home", "fh_corners_away"), ("corners_home", "corners_away")),
                     ("shots", ("fh_total_shots_home", "fh_total_shots_away"), ("total_shots_home", "total_shots_away")),
                     # halves share for yellows is measured within the stats feed
                     # (the only period-split source); the FT cards TARGET is
                     # event-unified (PREPROCESSING rule 7) — within-feed ratio,
                     # presentation only.
                     ("yellow", ("fh_yellow_cards_home", "fh_yellow_cards_away"), ("yellow_cards_home", "yellow_cards_away"))]:
    out["halves"][name] = half_share(fh[0], fh[1], ft[0], ft[1])
# team-level 1H share split-half (goals)
def team_share_split(reps=30):
    rs = []
    gg = g.copy()
    rows = []
    for _, r in gg.iterrows():
        rows.append((r.home_team_id, r.fh, r.ft)); rows.append((r.away_team_id, r.ht_away_goals, r.away_goals))
    df = pd.DataFrame(rows, columns=["team_id", "fh", "ft"])
    teams = [tid for tid, x in df.groupby("team_id") if x.ft.sum() >= 20]
    for rep in range(reps):
        a, b = [], []
        for tid in teams:
            x = df[df.team_id == tid]; idx = rng.permutation(len(x))
            h1, h2 = x.iloc[idx[: len(x) // 2]], x.iloc[idx[len(x) // 2:]]
            if h1.ft.sum() > 0 and h2.ft.sum() > 0:
                a.append(h1.fh.sum() / h1.ft.sum()); b.append(h2.fh.sum() / h2.ft.sum())
        if len(a) >= 8: rs.append(np.corrcoef(a, b)[0, 1])
    return float(np.mean(rs)) if rs else None
out["halves"]["goals_team_share_r"] = team_share_split()

# primary lines: dev distribution (seasons 2021/2022-2024/2025)
dev = m[m.season.isin(["2021", "2022", "2023", "2024"])]
out["dev_levels"] = {k: float(dev[k].mean()) for k in ["goals", "sot", "corners", "shots", "yellow"]}
out["dev_over_rates"] = dict(ou25=float((dev.goals > 2.5).mean()), sot85=float((dev.sot > 8.5).mean()), sot95=float((dev.sot > 9.5).mean()),
                             corners95=float((dev.corners > 9.5).mean()), corners105=float((dev.corners > 10.5).mean()),
                             cards25=float((dev.yellow > 2.5).mean()), cards35=float((dev.yellow > 3.5).mean()),
                             shots255=float((dev.shots > 25.5).mean()), shots265=float((dev.shots > 26.5).mean()))
vir = m[m.season == "2025"]
out["virgin_levels"] = {k: float(vir[k].mean()) for k in ["goals", "sot", "corners", "shots", "yellow"]}
out["virgin_over_rates"] = dict(ou25=float((vir.goals > 2.5).mean()), sot85=float((vir.sot > 8.5).mean()),
                                corners105=float((vir.corners > 10.5).mean()), cards25=float((vir.yellow > 2.5).mean()),
                                shots265=float((vir.shots > 26.5).mean()))
(HERE / "eda_summary.json").write_text(json.dumps(out, indent=1, default=str))
print(json.dumps(out, indent=1, default=str))
