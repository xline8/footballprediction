"""Stage A MLS EDA. 2026 is inventory-only and never enters model levels,
reliability, halves constants, dev gates, or virgin calculations."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).parent
DATA = HERE.parent / "data"
MODEL_SEASONS = ["2021", "2022", "2023", "2024", "2025"]
DEV_SEASONS = ["2022", "2023", "2024"]
rng = np.random.default_rng(20261109)
m = pd.read_csv(DATA / "us_matches.csv", parse_dates=["date"])
t = pd.read_csv(DATA / "us_team_matches.csv", parse_dates=["date"])
m["season"] = m.season.astype(str); t["season"] = t.season.astype(str)
for c in ["home_goals", "away_goals"]: m[c] = pd.to_numeric(m[c], errors="coerce")
m["goals"] = m.home_goals + m.away_goals
for k, cols in [("sot", ("ShotsOnTarget_home", "ShotsOnTarget_away")), ("corners", ("corners_home", "corners_away")),
                ("shots", ("total_shots_home", "total_shots_away")), ("yellow", ("yellow_home", "yellow_away")),
                ("red", ("red_home", "red_away")), ("xg", ("expected_goals_home", "expected_goals_away"))]:
    m[k] = pd.to_numeric(m[cols[0]], errors="coerce") + pd.to_numeric(m[cols[1]], errors="coerce")
model_m = m[m.season.isin(MODEL_SEASONS)].copy(); model_t = t[t.season.isin(MODEL_SEASONS)].copy()

def level(g):
    return dict(n=int(len(g)), goals=float(g.goals.mean()), home_goals=float(g.home_goals.mean()), away_goals=float(g.away_goals.mean()),
        home_win=float((g.home_goals > g.away_goals).mean()), draw=float((g.home_goals == g.away_goals).mean()), away_win=float((g.home_goals < g.away_goals).mean()),
        btts=float(((g.home_goals > 0) & (g.away_goals > 0)).mean()), over25=float((g.goals > 2.5).mean()), sot=float(g.sot.mean()), corners=float(g.corners.mean()),
        shots=float(g.shots.mean()), yellow=float(g.yellow.mean()), red=float(g.red.mean()), xg=float(g.xg.mean()), xg_calib=float(g.goals.sum() / g.xg.sum()))

out = {"seasons": {s: level(model_m[model_m.season == s]) for s in MODEL_SEASONS}, "reserved_inventory": {"2026": {"n": int((m.season == "2026").sum()), "phase_counts": m[m.season == "2026"].phase.value_counts().to_dict()}}}
out["levels"] = level(model_m); out["levels"]["home_adv"] = out["levels"]["home_goals"] - out["levels"]["away_goals"]
out["dispersion"] = {k: float(model_m[k].var() / model_m[k].mean()) for k in ["goals", "sot", "corners", "shots", "yellow"]}
out["phase_counts"] = model_m.phase.value_counts().to_dict(); out["phase_counts_all"] = m.phase.value_counts().to_dict()
out["phase_levels_goals"] = {p: level(model_m[model_m.phase == p])["goals"] for p in sorted(model_m.phase.dropna().unique())}
out["teams_per_season"] = {s: int(len(set(g.home_team_id) | set(g.away_team_id))) for s, g in m.groupby("season")}
out["coverage"] = {}
for s, g in m.groupby("season"):
    out["coverage"][s] = dict(n=int(len(g)), stats=float(g.has_stats_all.mean()), shotmap=float(g.has_shotmap.mean()), splits=float(g.has_stats_half.mean()), referee=float(g.referee.notna().mean()), xg=float(g.expected_goals_home.notna().mean()), yellow=float(g.yellow_home.notna().mean()), red=float(g.red_home.notna().mean()), box=float(g.touches_opp_box_home.notna().mean()))
out["score_events_mismatch"] = int(m.score_events_mismatch.sum()); out["extra_time_matches"] = int(m.has_extra_time.sum()); out["shootout_matches"] = int(m.has_shootout.sum()); out["shootout_shots"] = int(m.n_shootout_shots.sum())

def split_half(df, value_fn, min_matches=24, reps=30):
    rs = []; teams = [tid for tid, g in df.groupby("team_id") if len(g) >= min_matches]
    for _ in range(reps):
        a, b = [], []
        for tid in teams:
            g = df[df.team_id == tid]; ix = rng.permutation(len(g)); h1, h2 = g.iloc[ix[:len(g)//2]], g.iloc[ix[len(g)//2:]]
            va, vb = value_fn(h1), value_fn(h2)
            if va is not None and vb is not None and np.isfinite(va) and np.isfinite(vb): a.append(va); b.append(vb)
        if len(a) >= 8: rs.append(np.corrcoef(a, b)[0, 1])
    return dict(r=float(np.mean(rs)), n_teams=len(teams), reps=len(rs)) if rs else None
def mean_of(col): return lambda g: g[col].mean()
def ratio_of(num, den): return lambda g: (g[num].sum() / g[den].sum()) if g[num].notna().any() and g[den].sum() > 0 else None

rel = {}
for name, fn in [("goals_for", mean_of("goals_for")), ("goals_against", mean_of("goals_against")), ("shots_for", mean_of("shots_for")), ("sot_for", mean_of("sot_for")), ("corners_for", mean_of("corners_for")), ("yellow_for", mean_of("yellow_for")), ("xg_for", mean_of("xg_for")), ("box_touches_for", lambda g: g.box_touches_for.mean() if g.box_touches_for.notna().sum() >= 12 else None), ("box_touches_against", lambda g: g.box_touches_against.mean() if g.box_touches_against.notna().sum() >= 12 else None), ("big_chance_for", mean_of("big_chance_for"))]: rel[name] = split_half(model_t, fn)
tm = []
for _, r in model_m.iterrows():
    for side in ("home", "away"):
        tm.append(dict(team_id=r[f"{side}_team_id"], sp_xg=r[f"expected_goals_set_play_{side}"], tot_xg=r[f"expected_goals_{side}"], sm_xg=r[f"sm_xg_{side}"], sm_shots=r[f"sm_shots_{side}"], goals=r[f"{side}_goals"], sot=r[f"ShotsOnTarget_{side}"], shots=r[f"total_shots_{side}"], sm_xgot=r[f"sm_xgot_{side}"], sm_xgot_n=r[f"sm_xgot_n_{side}"], date=r.date))
tm = pd.DataFrame(tm)
ratio_traits = {"setplay_xg_share": split_half(tm, ratio_of("sp_xg", "tot_xg")), "xg_per_shot": split_half(tm, ratio_of("sm_xg", "sm_shots")), "finishing_goals_minus_xg": split_half(tm, lambda g: (g.goals - g.tot_xg).mean()), "sot_rate": split_half(tm, ratio_of("sot", "shots")), "goals_per_shot": split_half(tm, ratio_of("goals", "shots"))}
xgot_era = tm[tm.date >= "2024-01-01"]; ratio_traits["xgot_per_shot_era2024"] = split_half(xgot_era, ratio_of("sm_xgot", "sm_xgot_n"), min_matches=20)
out["reliability"], out["ratio_traits"] = rel, ratio_traits
mm = model_m[model_m.referee.notna()].copy(); mm["cards"] = mm.yellow
def ref_split():
    refs = [r for r, g in mm.groupby("referee") if len(g) >= 20]; rs = []
    for _ in range(30):
        a, b = [], []
        for ref in refs:
            g = mm[mm.referee == ref]; ix = rng.permutation(len(g)); a.append(g.iloc[ix[:len(g)//2]].cards.mean()); b.append(g.iloc[ix[len(g)//2:]].cards.mean())
        if len(a) >= 8: rs.append(np.corrcoef(a, b)[0, 1])
    return dict(r=float(np.mean(rs)), n_refs=len(refs), n_matches=int(len(mm)), reps=len(rs))
out["referees"] = ref_split(); out["referee_coverage"] = float(model_m.referee.notna().mean())
bt = model_t[model_t.box_touches_for.notna()]; out["corners_territorial"] = dict(corr_corners_boxtouches=float(bt[["corners_for", "box_touches_for"]].corr().iloc[0, 1]), corr_corners_possession=float(bt[["corners_for", "possession"]].corr().iloc[0, 1]), n=int(len(bt)))

era_m = model_m[model_m.season.isin(["2024", "2025"]) & model_m.has_stats_half].copy()
def half_share(fh_h, fh_a, ft_h, ft_a):
    g = era_m.dropna(subset=[fh_h, fh_a, ft_h, ft_a]).copy(); g["ft"] = g[ft_h] + g[ft_a]; g["fh"] = g[fh_h] + g[fh_a]; g = g[g.ft > 0]; share = float(g.fh.sum() / g.ft.sum()); p = g.fh / g.ft
    return dict(share=share, true_var=float(p.var(ddof=1) - np.mean(share * (1-share) / g.ft)), n=int(len(g)))
g = era_m.dropna(subset=["ht_home_goals", "ht_away_goals"]).copy(); g["ft"] = g.home_goals + g.away_goals; g["fh"] = g.ht_home_goals + g.ht_away_goals; g = g[g.ft > 0]; p = g.fh / g.ft; share = float(g.fh.sum() / g.ft.sum())
out["halves"] = {"goals": dict(share=share, true_var=float(p.var(ddof=1) - np.mean(share*(1-share)/g.ft)), n=int(len(g)))}
for name, fh, ft in [("sot", ("fh_ShotsOnTarget_home", "fh_ShotsOnTarget_away"), ("ShotsOnTarget_home", "ShotsOnTarget_away")), ("corners", ("fh_corners_home", "fh_corners_away"), ("corners_home", "corners_away")), ("shots", ("fh_total_shots_home", "fh_total_shots_away"), ("total_shots_home", "total_shots_away")), ("yellow", ("fh_yellow_cards_home", "fh_yellow_cards_away"), ("yellow_home", "yellow_away"))]: out["halves"][name] = half_share(fh[0], fh[1], ft[0], ft[1])

dev = model_m[model_m.season.isin(DEV_SEASONS)]; out["dev_levels"] = {k: float(dev[k].mean()) for k in ["goals", "sot", "corners", "shots", "yellow"]}
def primary_rate(col):
    rates = {str(v): float((dev[col] > v).mean()) for v in np.arange(0.5, 40.0, 1.0) if 0 < (dev[col] > v).sum() < len(dev)}; best = min(rates, key=lambda v: abs(rates[v] - 0.5)); return {"line": float(best), "over_rate": rates[best]}
out["primary_lines"] = {"goals": {"line": 2.5, "over_rate": float((dev.goals > 2.5).mean())}, "sot": primary_rate("sot"), "corners": primary_rate("corners"), "yellow": primary_rate("yellow"), "shots": primary_rate("shots")}
out["virgin_levels"] = {k: float(model_m[model_m.season == "2025"][k].mean()) for k in ["goals", "sot", "corners", "shots", "yellow"]}; out["virgin_n"] = int((m.season == "2025").sum())
out["expansion_levels"] = {}
for team in ["Charlotte FC", "St. Louis City", "San Diego FC"]:
    q_all = model_m[(model_m.home_team == team) | (model_m.away_team == team)]
    if len(q_all):
        entry = str(q_all.season.min())
        q = q_all[q_all.season == entry]  # FIRST season only
        out["expansion_levels"][team] = {"season": entry, "n": int(len(q)), "goals": float(q.goals.mean()), "xg": float(q.xg.mean())}
out["xgot_era"] = {"start": "2024-01-01", "population_matches": int((model_m[["sm_xgot_home", "sm_xgot_away"]].notna().any(axis=1) & (model_m.date >= "2024-01-01")).sum()), "team_matches": int(len(xgot_era))}
(HERE / "eda_summary.json").write_text(json.dumps(out, indent=1, allow_nan=True)); print(json.dumps(out, indent=1, default=str))
