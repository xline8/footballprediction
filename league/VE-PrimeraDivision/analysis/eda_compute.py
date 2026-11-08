"""Compute descriptive EDA for VE-PrimeraDivision; no models are fit."""
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
A = Path(__file__).resolve().parent
D = ROOT / "league" / "VE-PrimeraDivision" / "data"
d = pd.read_csv(D / "ve_matches.csv")
d["date"] = pd.to_datetime(d.date)
d["goals_total"] = d.home_goals + d.away_goals
d["round_num"] = pd.to_numeric(d["round"], errors="coerce")
r = d[d.phase == "regular"].copy()

def total(frame, key, suffix=""):
    return frame[f"{key}_home{suffix}"] + frame[f"{key}_away{suffix}"]

def summary(y):
    y = pd.Series(y).dropna()
    return {"n": int(len(y)), "mean": float(y.mean()) if len(y) else None, "sd": float(y.std(ddof=1)) if len(y) > 1 else None}

levels = {}
for season, g in d.groupby("season"):
    regular = g[g.phase == "regular"]
    z = {"n": int(len(g)), "regular_n": int(len(regular)), "playoff_n": int((g.phase == "playoff").sum()), "teams": int(len(set(g.home_team_id) | set(g.away_team_id))), "rounds": sorted(g["round"].astype(str).unique()), "home_advantage": {"home_goals": float(regular.home_goals.mean()), "away_goals": float(regular.away_goals.mean())}}
    for name, y in {"goals_total": regular.goals_total, "ShotsOnTarget": total(regular, "ShotsOnTarget"), "corners": total(regular, "corners"), "stats_yellows": total(regular, "stats_yellow"), "total_shots": total(regular, "total_shots")}.items():
        z[name] = summary(y)
    levels[str(season)] = z

tm = pd.read_csv(D / "ve_team_matches.csv")
tm["date"] = pd.to_datetime(tm.date)
tm = tm[tm.phase == "regular"].copy()
tm["on_target_rate"] = tm.sot_for / tm.total_shots_for
tm["on_target_rate_against"] = tm.sot_against / tm.total_shots_against
tm["era_sample"] = ((tm.season == 2025) & (tm.stage == "Clausura")) | (tm.season == 2026)
tm = tm[tm.era_sample].sort_values(["season", "team_id", "date", "match_id"])
traits = ["goals_for", "goals_against", "sot_for", "sot_against", "corners_for", "corners_against", "yellow_for", "yellow_against", "total_shots_for", "total_shots_against", "possession_for", "big_chances_for", "on_target_rate"]

def reliability(frame):
    out = {}
    for trait in traits:
        pairs = []
        for _, tg in frame.groupby(["season", "team_id"]):
            if len(tg) < 6:
                continue
            a, b = tg.iloc[::2], tg.iloc[1::2]
            if trait == "on_target_rate":
                av = a.sot_for.sum() / a.total_shots_for.sum() if a.total_shots_for.sum() else np.nan
                bv = b.sot_for.sum() / b.total_shots_for.sum() if b.total_shots_for.sum() else np.nan
            else:
                av, bv = a[trait].mean(), b[trait].mean()
            if pd.notna(av) and pd.notna(bv):
                pairs.append((av, bv))
        arr = np.asarray(pairs, dtype=float)
        rr = np.corrcoef(arr.T)[0, 1] if len(arr) >= 3 and arr[:, 0].std() and arr[:, 1].std() else None
        out[trait] = {"n_teams": int(len(pairs)), "r": float(rr) if rr is not None else None}
    return out

reliability_out = {str(s): reliability(g) for s, g in tm.groupby("season")}
reliability_out["pooled_stats_era"] = reliability(tm)

def half_record(frame, key=None, event=False):
    if event:
        h = frame.event_yellow_unified_home_1h + frame.event_yellow_unified_away_1h
        t = frame.event_yellow_unified_home + frame.event_yellow_unified_away
    elif key is None:
        h, t = frame.ht_home_goals + frame.ht_away_goals, frame.goals_total
    else:
        h, t = total(frame, key, "_1h"), total(frame, key)
    ok = h.notna() & t.notna() & (t > 0)
    shares = (h[ok] / t[ok]).astype(float)
    observed = float(shares.var(ddof=1)) if len(shares) > 1 else None
    # Binomial noise floor uses the POOLED share p: mean over matches of
    # p(1-p)/n_i. (Using each match's own share in the numerator is wrong:
    # with small denominators most per-match shares are 0 or 1, which
    # collapses the floor toward 0 and fabricates positive true variance.)
    p = float(h[ok].sum() / t[ok].sum()) if len(shares) else None
    noise = float(np.mean(p * (1 - p) / t[ok])) if len(shares) else None
    return {"share": float(h[ok].sum() / t[ok].sum()) if len(shares) else None, "n": int(len(shares)), "observed_variance": observed, "noise_floor": noise, "true_variance": observed - noise if observed is not None and noise is not None else None}

half_frame_goals = r[(r.season <= 2025) & ~r.awarded.astype(bool)]
split_regular = r[r.period_splits_present == 1]
halves = {"goals": half_record(half_frame_goals)}
for output_key, source_key in [("ShotsOnTarget", "ShotsOnTarget"), ("corners", "corners"), ("total_shots", "total_shots"), ("stats_yellow", "yellow_cards")]:
    halves[output_key] = half_record(split_regular, source_key)
halves["cards_events_2026_audit"] = half_record(r[r.season == 2026], event=True)
halves["cards_stats_2025_26_audit"] = half_record(split_regular, "yellow_cards")

def window_summary(frame, keys):
    out = {"n": int(len(frame))}
    for label, key in keys.items():
        y = frame[key] if key == "goals_total" else total(frame, key)
        line = float(np.floor(y.mean()) + 0.5)
        out[label] = {"mean": float(y.mean()), "sd": float(y.std(ddof=1)), "line": line, "over_rate": float((y > line).mean())}
    return out

dev_goals = r[r.season.isin([2023, 2024])]
goals_dev = {"n": int(len(dev_goals)), "mean": float(dev_goals.goals_total.mean()), "ou2_5_over_rate": float((dev_goals.goals_total > 2.5).mean()), "home_win_rate": float((dev_goals.home_goals > dev_goals.away_goals).mean())}
count_keys = {"S": "ShotsOnTarget", "C": "corners", "K": "stats_yellow", "T": "total_shots"}
windows = {"counts_dev_2026_apertura": window_summary(r[(r.season == 2026) & (r.stage == "Apertura")], count_keys), "counts_seed_2025_clausura": window_summary(r[(r.season == 2025) & (r.stage == "Clausura")], count_keys), "counts_virgin_2026_clausura": window_summary(r[(r.season == 2026) & (r.stage == "Clausura")], count_keys)}

stats_era = d[d.stats_present == 1]
zero_filled = {}
for key in ["shots_inside_box", "shots_outside_box", "accurate_passes", "accurate_crosses", "accurate_long_balls", "interceptions", "blocked_shots", "blocks", "clearances", "duel_won", "duels_won", "dribbles_succeeded", "successful_dribbles", "touches_opp_box"]:
    if f"{key}_home" in stats_era:
        nonzero = int((total(stats_era, key) > 0).sum())
        zero_filled[key] = {"present": True, "nonzero_matches": nonzero, "stats_era_matches": int(len(stats_era))}
    else:
        zero_filled[key] = {"present": False, "nonzero_matches": 0, "stats_era_matches": int(len(stats_era))}
agreement = d[(d.season.isin([2025, 2026])) & (d.stats_present == 1)].copy()
sy, ey = total(agreement, "stats_yellow"), total(agreement, "event_yellow_unified")
diff = (ey - sy).value_counts().sort_index()
agreement_by_season = {}
for season, g in agreement.groupby("season"):
    a, b = total(g, "stats_yellow"), total(g, "event_yellow_unified")
    agreement_by_season[str(season)] = {"matches": int(len(g)), "stats_total": int(a.sum()), "events_unified_total": int(b.sum()), "exact_agreement_matches": int((a == b).sum()), "diff_distribution_events_minus_stats": {str(k): int(v) for k, v in (b - a).value_counts().sort_index().items()}}
artifacts = {"stats_vs_events_yellows": {"matches": int(len(agreement)), "stats_total": int(sy.sum()), "events_unified_total": int(ey.sum()), "exact_agreement_matches": int((sy == ey).sum()), "diff_distribution_events_minus_stats": {str(k): int(v) for k, v in diff.items()}, "by_season": agreement_by_season}, "event_card_coverage_by_season": {str(s): int(((g.event_yellow_home + g.event_yellow_away + g.event_red_home + g.event_red_away) > 0).sum()) for s, g in d.groupby("season")}, "referee_named_by_season": {str(s): int((g.referee.fillna("") != "").sum()) for s, g in d.groupby("season")}, "zero_filled_stat_keys": zero_filled, "shotmap_nonempty": int((d.shotmap_n > 0).sum()), "expected_goals_keys": 0}
out = {"levels": levels, "reliability": reliability_out, "halves": halves, "dev_goals": goals_dev, "count_windows": windows, "artifacts": artifacts}
(A / "eda_numbers.json").write_text(json.dumps(out, indent=2))
print(json.dumps(out, indent=2))
