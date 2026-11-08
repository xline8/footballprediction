"""EDA computations for PE-Liga1 (steps 1+3). Reads the built CSV only.
Outputs analysis/eda_summary.json + inventory_summary.json and prints
the headline numbers used in DATA_UNDERSTANDING.md / EDA.md."""
import json, math
from collections import Counter, defaultdict
from pathlib import Path
import pandas as pd
import numpy as np

HERE = Path(__file__).resolve().parent
df = pd.read_csv(HERE.parent / "data" / "pe_liga1_matches.csv", dtype={"match_id": str})
df["date"] = pd.to_datetime(df["date"])
reg = df[(df.phase == "regular") & (df.awarded == 0)].copy()
dev = reg[reg.season <= 2024]
vir = reg[reg.season == 2025]

def corr(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 5: return None, int(m.sum())
    return float(np.corrcoef(a[m], b[m])[0, 1]), int(m.sum())

inv = {"n_total": int(len(df)), "by_season": {str(k): int(v) for k, v in df.season.value_counts().sort_index().items()},
       "by_block": {k: int(v) for k, v in df.block.value_counts().sort_index().items()},
       "playoff_n": int((df.phase == "playoff").sum()), "awarded_n": int((df.awarded == 1).sum()),
       "awarded_list": df[df.awarded == 1][["season", "date", "home_team", "away_team", "home_goals", "away_goals"]].astype(str).values.tolist(),
       "coverage": {}}
for s, sub in df.groupby("season"):
    inv["coverage"][str(s)] = {"n": int(len(sub)), "has_stats": int(sub.has_stats.sum()),
        "has_rich_stats": int(sub.has_rich_stats.sum()), "has_period_splits": int(sub.has_period_splits.sum()),
        "has_xg": int(sub.has_xg.sum()), "shotmap_rows": int((sub.n_shotmap > 0).sum()),
        "referee_named": int((sub.referee.fillna("") != "").sum()),
        "ht_source": {k: int(v) for k, v in sub.ht_source.value_counts().items()},
        "events_exact": int(sub.events_exact.sum())}
inv["modelling_corpus"] = {"regular_nonawarded": int(len(reg)),
    "dev_2021_2024": int(len(dev)), "virgin_2025": int(len(vir)),
    "reserved_2026": int(len(reg[reg.season == 2026]))}

# Levels per block (modelling corpus)
levels = {}
for b, sub in reg.groupby("block"):
    st = sub[sub.has_stats == 1]
    rich = sub[sub.has_rich_stats == 1]
    levels[b] = {"n": int(len(sub)),
        "goals": float((sub.home_goals + sub.away_goals).mean()), "home_goals": float(sub.home_goals.mean()),
        "away_goals": float(sub.away_goals.mean()), "home_win_rate": float((sub.home_goals > sub.away_goals).mean()),
        "over25_rate": float(((sub.home_goals + sub.away_goals) > 2.5).mean()),
        "sot": float((st.shotsontarget_home + st.shotsontarget_away).mean()),
        "corners": float((st.corners_home + st.corners_away).mean()),
        "total_shots": float((st.total_shots_home + st.total_shots_away).mean()),
        "ev_yellow_inc2nd": float((sub.ev_yellow_inc2nd_home + sub.ev_yellow_inc2nd_away).mean()),
        "ev_yellow_plain": float((sub.ev_yellow_home + sub.ev_yellow_away).mean()),
        "stats_yellow_rich": float((rich.yellow_cards_home + rich.yellow_cards_away).mean()) if len(rich) else None,
        "rich_n": int(len(rich)), "stats_n": int(len(st))}

# Dev pooled totals + primary-line candidates
devst = dev[dev.has_stats == 1]
dev_tot = {"goals": float((dev.home_goals + dev.away_goals).mean()),
    "sot": float((devst.shotsontarget_home + devst.shotsontarget_away).mean()),
    "corners": float((devst.corners_home + devst.corners_away).mean()),
    "total_shots": float((devst.total_shots_home + devst.total_shots_away).mean()),
    "ev_yellow_inc2nd": float((dev.ev_yellow_inc2nd_home + dev.ev_yellow_inc2nd_away).mean()),
    "sot_median": float((devst.shotsontarget_home + devst.shotsontarget_away).median()),
    "corners_median": float((devst.corners_home + devst.corners_away).median()),
    "shots_median": float((devst.total_shots_home + devst.total_shots_away).median()),
    "cards_median": float((dev.ev_yellow_inc2nd_home + dev.ev_yellow_inc2nd_away).median()),
    "dev_n": int(len(dev)), "dev_stats_n": int(len(devst))}

# Cards artefact (dev era, rich matches only): stats-feed vs events
rich_dev = dev[dev.has_rich_stats == 1]
art = {}
for nm, cols in (("plain", ("ev_yellow_home", "ev_yellow_away")), ("inc2nd", ("ev_yellow_inc2nd_home", "ev_yellow_inc2nd_away"))):
    ev = rich_dev[cols[0]] + rich_dev[cols[1]]; stt = rich_dev.yellow_cards_home + rich_dev.yellow_cards_away
    art[nm] = {"exact_pct": float((ev == stt).mean() * 100), "mean_ev": float(ev.mean()), "mean_stats": float(stt.mean()),
               "mean_diff_ev_minus_stats": float((ev - stt).mean()), "n": int(len(rich_dev))}
art["by_season"] = {}
for s, sub in rich_dev.groupby("season"):
    ev = sub.ev_yellow_inc2nd_home + sub.ev_yellow_inc2nd_away; stt = sub.yellow_cards_home + sub.yellow_cards_away
    art["by_season"][str(s)] = {"n": int(len(sub)), "exact_inc2nd_pct": float((ev == stt).mean() * 100),
                               "mean_diff_inc2nd": float((ev - stt).mean())}

# Split-half team trait reliability (career-pooled, odd/even match index per team)
tm_rows = []
for _, r in reg.sort_values("date").iterrows():
    for side, opp in (("home", "away"), ("away", "home")):
        tm_rows.append({"team_id": r[f"{side}_team_id"], "goals_for": r[f"{side}_goals"], "goals_against": r[f"{opp}_goals"],
            "sot_for": r[f"shotsontarget_{side}"], "sot_against": r[f"shotsontarget_{opp}"],
            "corners_for": r[f"corners_{side}"], "corners_against": r[f"corners_{opp}"],
            "shots_for": r[f"total_shots_{side}"], "shots_against": r[f"total_shots_{opp}"],
            "evyel_for": r[f"ev_yellow_inc2nd_{side}"], "evyel_against": r[f"ev_yellow_inc2nd_{opp}"],
            "touches_for": r[f"touches_opp_box_{side}"], "touches_against": r[f"touches_opp_box_{opp}"],
            "poss_for": r[f"ballpossesion_{side}"], "bigchance_for": r[f"big_chance_{side}"],
            "xgshot_num": np.nan, "has_stats": r["has_stats"], "has_rich": r["has_rich_stats"]})
tm = pd.DataFrame(tm_rows)
traits = {}
for col, sub_filter, min_n in [("goals_for", None, 20), ("goals_against", None, 20),
        ("sot_for", "stats", 20), ("sot_against", "stats", 20), ("corners_for", "stats", 20),
        ("corners_against", "stats", 20), ("shots_for", "stats", 20), ("shots_against", "stats", 20),
        ("evyel_for", None, 20), ("evyel_against", None, 20), ("touches_for", "rich", 16),
        ("touches_against", "rich", 16), ("poss_for", "stats", 20), ("bigchance_for", "rich", 16)]:
    sub = tm if sub_filter is None else (tm[tm.has_stats == 1] if sub_filter == "stats" else tm[tm.has_rich == 1])
    sub = sub.dropna(subset=[col])
    h1, h2 = {}, {}
    for tid, g in sub.groupby("team_id"):
        if len(g) < min_n: continue
        vals = g[col].values
        h1[tid] = vals[0::2].mean(); h2[tid] = vals[1::2].mean()
    ids = sorted(set(h1) & set(h2))
    r_, n_ = corr([h1[i] for i in ids], [h2[i] for i in ids])
    traits[col] = {"r": r_, "n_teams": n_}
# corner corr with touches / possession per match (team-match level, rich+stats)
sub = tm[(tm.has_rich == 1)].dropna(subset=["corners_for", "touches_for", "poss_for"])
traits["corr_corners_touches"], _ = corr(sub.corners_for, sub.touches_for)
traits["corr_corners_poss"], _ = corr(sub.corners_for, sub.poss_for)

# Referee trait (dev era, named referees, unified event yellows)
dref = dev[dev.referee.fillna("") != ""].copy()
dref["tot_yellow"] = dref.ev_yellow_inc2nd_home + dref.ev_yellow_inc2nd_away
h1, h2 = {}, {}
for ref, g in dref.groupby("referee"):
    if len(g) < 16: continue
    v = g.tot_yellow.values; h1[ref] = v[0::2].mean(); h2[ref] = v[1::2].mean()
ids = sorted(set(h1) & set(h2))
rr, rn = corr([h1[i] for i in ids], [h2[i] for i in ids])
ref_trait = {"r": rr, "n_refs": rn, "dev_coverage": float((dev.referee.fillna("") != "").mean()),
             "virgin_coverage": float((vir.referee.fillna("") != "").mean())}

# Halves
def share_stats(num, den):
    m = den > 0
    pooled = float(num[m].sum() / den[m].sum())
    s = (num[m] / den[m])
    noise = float((s * (1 - s) / den[m]).mean()); obs = float(s.var(ddof=1))
    return {"pooled_share": pooled, "n_matches": int(m.sum()), "obs_var": obs,
            "noise_var": noise, "true_var": max(obs - noise, 0.0), "true_sd": math.sqrt(max(obs - noise, 0.0))}
halves = {}
h = reg.dropna(subset=["ht_home_goals"])
halves["goals"] = share_stats(h.ht_home_goals + h.ht_away_goals, h.home_goals + h.away_goals)
sp = reg[reg.has_period_splits == 1]  # 2025+2026 only era carrying splits
for nm, k1, kt in (("sot", "shotsontarget", "shotsontarget"), ("corners", "corners", "corners"), ("total_shots", "total_shots", "total_shots")):
    halves[nm] = share_stats(sp[f"{k1}_home_1h"] + sp[f"{k1}_away_1h"], sp[f"{kt}_home"] + sp[f"{kt}_away"])
halves["cards_events"] = share_stats(reg.fh_ev_yellow_inc2nd_home + reg.fh_ev_yellow_inc2nd_away,
                                     reg.ev_yellow_inc2nd_home + reg.ev_yellow_inc2nd_away)
halves["splits_era_n"] = int(len(sp))

# Altitude: modal home city per team -> elevation (m, standard geographic values)
ALT = {"Cusco": 3400, "Juliaca": 3825, "Huancayo": 3259, "Tarma": 3053, "Andahuaylas": 2926,
       "Ayacucho": 2761, "Cajamarca": 2750, "Cutervo": 2649, "Cajabamba": 2654, "Arequipa": 2335,
       "Huánuco": 1880, "Moquegua": 1410, "Jaén": 729, "Tarapoto": 356, "Lima": 150, "Callao": 10,
       "Trujillo": 34, "Sullana": 65, "Piura": 29, "Chongoyape": 209, "Humay": 430, "Huacho": 30,
       "Lambayeque": 18, "Olmos": 175, "Moyobamba": 860, "Talavera": 2820, "La Matanza": 60}
modal_city = reg.groupby("home_team_id").stadium_city.agg(lambda s: s.value_counts().idxmax())
alt_rows = []
for cls, lo, hi in (("high>=2300", 2300, 9999), ("mid 700-2299", 700, 2299), ("low<700", 0, 699)):
    mask = reg.home_team_id.map(lambda t: ALT.get(modal_city.get(t, ""), -1) >= lo and ALT.get(modal_city.get(t, ""), -1) <= hi)
    sub = reg[mask]
    alt_rows.append({"class": cls, "n": int(len(sub)), "home_goals": float(sub.home_goals.mean()),
        "away_goals": float(sub.away_goals.mean()), "home_win_rate": float((sub.home_goals > sub.away_goals).mean()),
        "home_edge_gd": float((sub.home_goals - sub.away_goals).mean()),
        "teams": sorted(set(sub.home_team.unique()))})
# Per-team home vs away GD for the high-altitude clubs
alt_teams = {}
for tid, city in modal_city.items():
    a = ALT.get(city, -1)
    if a < 2300: continue
    home = reg[reg.home_team_id == tid]; away = reg[reg.away_team_id == tid]
    nm = home.home_team.iloc[0] if len(home) else away.away_team.iloc[0]
    alt_teams[nm] = {"city": city, "alt_m": a, "home_n": int(len(home)),
        "home_gd": float((home.home_goals - home.away_goals).mean()),
        "away_gd": float((away.away_goals - away.home_goals).mean()) if len(away) else None}

# Entrants (absent previous calendar year): first-year performance vs league mean
entrants = {}
for year in (2022, 2023, 2024, 2025):
    sub = reg[reg.season == year]
    ent_ids = sorted(set(sub[sub.home_absent_prev == 1].home_team_id) | set(sub[sub.away_absent_prev == 1].away_team_id))
    rows_e = []
    for tid in ent_ids:
        t = tm[(tm.team_id == tid)]
        # restrict to that year's matches via match dates
        mm = reg[reg.season == year]
        sel = mm[(mm.home_team_id == tid) | (mm.away_team_id == tid)]
        gf = float(pd.concat([sel[sel.home_team_id == tid].home_goals, sel[sel.away_team_id == tid].away_goals]).mean())
        ga = float(pd.concat([sel[sel.home_team_id == tid].away_goals, sel[sel.away_team_id == tid].home_goals]).mean())
        canon = df.drop_duplicates("home_team_id").set_index("home_team_id").home_team.to_dict()
        canon.update(df.drop_duplicates("away_team_id").set_index("away_team_id").away_team.to_dict())
        rows_e.append({"team": canon[tid], "n": int(len(sel)), "gf": gf, "ga": ga})
    league_gf = float((sub.home_goals.sum() + sub.away_goals.sum()) / (2 * len(sub)))
    entrants[str(year)] = {"teams": rows_e, "league_gf_per_team_match": league_gf,
        "entrant_gf": float(np.mean([x["gf"] for x in rows_e])) if rows_e else None,
        "entrant_ga": float(np.mean([x["ga"] for x in rows_e])) if rows_e else None}
dev_ent = [x for y in ("2022", "2023", "2024") for x in entrants[y]["teams"]]
ent_dev_pooled = {"n_teams": len(dev_ent),
    "gf_delta_vs_league": float(np.mean([x["gf"] for x in dev_ent]) - np.mean([entrants[y]["league_gf_per_team_match"] for y in ("2022", "2023", "2024")])),
    "ga_delta_vs_league": float(np.mean([x["ga"] for x in dev_ent]) - np.mean([entrants[y]["league_gf_per_team_match"] for y in ("2022", "2023", "2024")]))}

# --- Addendum: era-restricted cards (events valid 2023+ only) + unified shots ---
cards_era = reg[reg.season >= 2023]
tm_ce = []
for _, r in cards_era.sort_values("date").iterrows():
    for side, opp in (("home", "away"), ("away", "home")):
        tm_ce.append({"team_id": r[f"{side}_team_id"], "evyel_for": r[f"ev_yellow_inc2nd_{side}"],
                      "evyel_against": r[f"ev_yellow_inc2nd_{opp}"]})
tm_ce = pd.DataFrame(tm_ce)
cards_traits = {}
for col in ("evyel_for", "evyel_against"):
    h1, h2 = {}, {}
    for tid, g in tm_ce.groupby("team_id"):
        if len(g) < 16: continue
        v = g[col].values; h1[tid] = v[0::2].mean(); h2[tid] = v[1::2].mean()
    ids = sorted(set(h1) & set(h2)); r_, n_ = corr([h1[i] for i in ids], [h2[i] for i in ids])
    cards_traits[col] = {"r": r_, "n_teams": n_}
dref2 = cards_era[(cards_era.season <= 2024) & (cards_era.referee.fillna("") != "")].copy()
dref2["tot_yellow"] = dref2.ev_yellow_inc2nd_home + dref2.ev_yellow_inc2nd_away
h1, h2 = {}, {}
for ref, g in dref2.groupby("referee"):
    if len(g) < 12: continue
    v = g.tot_yellow.values; h1[ref] = v[0::2].mean(); h2[ref] = v[1::2].mean()
ids = sorted(set(h1) & set(h2)); rr2, rn2 = corr([h1[i] for i in ids], [h2[i] for i in ids])
ref_trait_2324 = {"r": rr2, "n_refs": rn2, "coverage_2023": float((cards_era[cards_era.season == 2023].referee.fillna("") != "").mean()),
                  "coverage_2024": float((cards_era[cards_era.season == 2024].referee.fillna("") != "").mean())}
cards_dev = {"seed_2023_n": int(len(cards_era[cards_era.season == 2023])),
             "eval_2024_n": int(len(cards_era[cards_era.season == 2024])),
             "mean_2023_2024": float((cards_era[cards_era.season <= 2024].ev_yellow_inc2nd_home + cards_era[cards_era.season <= 2024].ev_yellow_inc2nd_away).mean()),
             "median_2023_2024": float((cards_era[cards_era.season <= 2024].ev_yellow_inc2nd_home + cards_era[cards_era.season <= 2024].ev_yellow_inc2nd_away).median())}
halves["cards_events_2023plus"] = share_stats(cards_era.fh_ev_yellow_inc2nd_home + cards_era.fh_ev_yellow_inc2nd_away,
                                              cards_era.ev_yellow_inc2nd_home + cards_era.ev_yellow_inc2nd_away)
# Unified total shots: rich = SOT+OffTarget (blocked excluded, matches the
# rich-era identity total = SOT+Off+Blocked exactly); sparse = total_shots key.
reg["shots_unified_home"] = np.where(reg.has_rich_stats == 1,
    reg.shotsontarget_home + reg.shotsofftarget_home, reg.total_shots_home)
reg["shots_unified_away"] = np.where(reg.has_rich_stats == 1,
    reg.shotsontarget_away + reg.shotsofftarget_away, reg.total_shots_away)
devu = dev.merge(reg[["match_id", "shots_unified_home", "shots_unified_away"]], on="match_id")
shots_unified = {"dev_mean": float((devu.shots_unified_home + devu.shots_unified_away).mean()),
                 "dev_median": float((devu.shots_unified_home + devu.shots_unified_away).median()),
                 "virgin_mean": float((vir.merge(reg[["match_id", "shots_unified_home", "shots_unified_away"]], on="match_id").pipe(lambda x: x.shots_unified_home + x.shots_unified_away)).mean())}
# Team 1H-goal-share split-half cross-check (frozen-constant question)
h = reg.dropna(subset=["ht_home_goals"]).copy()
h["share_home"] = np.where(h.home_goals > 0, h.ht_home_goals / h.home_goals, np.nan)
h1s, h2s = {}, {}
for tid, g in h.groupby("home_team_id"):
    v = g.share_home.dropna().values
    if len(v) < 20: continue
    h1s[tid] = v[0::2].mean(); h2s[tid] = v[1::2].mean()
ids = sorted(set(h1s) & set(h2s)); rsh, nsh = corr([h1s[i] for i in ids], [h2s[i] for i in ids])
halves["goals_team_share_splithalf"] = {"r": rsh, "n_teams": nsh}

out = {"inventory": inv, "levels_by_block": levels, "dev_totals": dev_tot,
       "cards_traits_2023plus": cards_traits, "referee_trait_2023_2024": ref_trait_2324,
       "cards_dev": cards_dev, "shots_unified": shots_unified,
       "cards_artefact": art, "traits": traits, "referee_trait": ref_trait,
       "halves": halves, "altitude": {"by_class": alt_rows, "high_teams": alt_teams},
       "entrants": entrants, "entrant_dev_pooled": ent_dev_pooled}
(HERE / "eda_summary.json").write_text(json.dumps(out, indent=1, ensure_ascii=False))
(HERE / "inventory_summary.json").write_text(json.dumps(inv, indent=1, ensure_ascii=False))
print(json.dumps(out, indent=1, ensure_ascii=False))
