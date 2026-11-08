"""Measured Phase-A EDA for TR-1Lig; no model fitting and no virgin reads for reliabilities."""
import csv, json, math, random, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
ROWS = list(csv.DictReader(open(DATA / "tr1_matches.csv", encoding="utf-8")))
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]
DEV = {"2021/2022", "2022/2023", "2023/2024", "2024/2025"}
VIRGIN = {"2025/2026", "2026/2027"}

def f(r, key):
    v = r.get(key)
    return None if v in (None, "", "None") else float(v)

def corr(xs, ys):
    if len(xs) < 5: return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return None if not den else sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / den

def rel(series, min_n=20, reps=60, seed=42):
    series = {k: v for k, v in series.items() if len(v) >= min_n}
    rng, vals = random.Random(seed), []
    for _ in range(reps):
        xs, ys = [], []
        for vs in series.values():
            idx = list(range(len(vs))); rng.shuffle(idx); h = len(vs)//2
            xs.append(st.mean(vs[i] for i in idx[:h])); ys.append(st.mean(vs[i] for i in idx[h:]))
        c = corr(xs, ys)
        if c is not None: vals.append(c)
    return (round(st.mean(vals), 3) if vals else None, len(series))

def analysis_rows(seasons=None):
    return [r for r in ROWS if r["finished"] == "1" and r["awarded"] == "0" and r["phase"] == "regular" and (seasons is None or r["season"] in seasons)]

def total_mean(rs, key):
    vals = [f(r, f"{key}_home") + f(r, f"{key}_away") for r in rs if f(r, f"{key}_home") is not None and f(r, f"{key}_away") is not None]
    return round(st.mean(vals), 3) if vals else None

def coverage(rs, key):
    return round(100 * sum(f(r, key) is not None for r in rs) / len(rs), 1) if rs else None

def main():
    out = {"corpus": {"index_rows": len(ROWS), "seasons": SEASONS, "analysis_scope": "finished regular non-awarded", "dev_seasons": sorted(DEV), "virgin_seasons": sorted(VIRGIN)}}
    per = {}
    for s in SEASONS:
        all_s = [r for r in ROWS if r["season"] == s]
        rs = analysis_rows({s})
        per[s] = {
            "index_n": len(all_s), "analysis_n": len(rs), "goals": round(st.mean(int(r["home_goals"])+int(r["away_goals"]) for r in rs), 3),
            "home_goals": round(st.mean(int(r["home_goals"]) for r in rs), 3), "away_goals": round(st.mean(int(r["away_goals"]) for r in rs), 3),
            "phases_index": {p: sum(r["phase"] == p for r in all_s) for p in ("regular", "playoff")},
            "awarded_index": sum(r["awarded"] == "1" for r in all_s),
            "stats_cov_index_pct": round(100*sum(r["has_stats_all"] == "1" for r in all_s)/len(all_s), 1),
            "period_cov_index_pct": round(100*sum(r["has_stats_half"] == "1" for r in all_s)/len(all_s), 1),
            "events_cov_index_pct": round(100*sum(r["has_events"] == "1" for r in all_s)/len(all_s), 1),
            "shotmap_cov_index_pct": round(100*sum(r["has_shotmap"] == "1" for r in all_s)/len(all_s), 1),
            "referee_cov_index_pct": round(100*sum(bool(r["referee"]) for r in all_s)/len(all_s), 1),
            "stats": {k: total_mean(rs, k) for k in ("ShotsOnTarget", "corners", "total_shots", "yellow_cards", "expected_goals", "touches_opp_box", "big_chance")},
            "coverage_analysis": {k: coverage(rs, f"{k}_home") for k in ("ShotsOnTarget", "corners", "total_shots", "yellow_cards", "expected_goals", "touches_opp_box", "big_chance")},
            "event_yellows_per_match": round(st.mean(int(r["ev_yellow_home"])+int(r["ev_yellow_away"]) for r in rs), 3),
        }
    out["per_season"] = per
    dev = analysis_rows(DEV)
    out["dev_levels"] = {"n": len(dev), "home_goals": round(st.mean(int(r["home_goals"]) for r in dev), 3), "away_goals": round(st.mean(int(r["away_goals"]) for r in dev), 3),
                          "home_win_pct": round(100*sum(int(r["home_goals"]) > int(r["away_goals"]) for r in dev)/len(dev), 1),
                          "draw_pct": round(100*sum(int(r["home_goals"]) == int(r["away_goals"]) for r in dev)/len(dev), 1),
                          "away_win_pct": round(100*sum(int(r["home_goals"]) < int(r["away_goals"]) for r in dev)/len(dev), 1),
                          "over25_pct": round(100*sum(int(r["home_goals"])+int(r["away_goals"]) > 2 for r in dev)/len(dev), 1)}

    # Goals-only reliability evidence is dev-only and career-pooled by team id.
    series = defaultdict(lambda: defaultdict(list))
    for r in dev:
        for side, opp in (("home", "away"), ("away", "home")):
            tid = r[f"{side}_team_id"]
            series["goals_for"][tid].append(float(r[f"{side}_goals"]))
            series["goals_against"][tid].append(float(r[f"{opp}_goals"]))
    for key, col in (("yellow_for", "yellow"), ("sot_for", "ShotsOnTarget"), ("corners_for", "corners"), ("shots_for", "total_shots")):
        for r in dev:
            for side in ("home", "away"):
                v = f(r, f"{col}_{side}")
                if v is not None: series[key][r[f"{side}_team_id"]].append(v)
    out["reliability_dev"] = {k: {"r": rel(v)[0], "n_teams": rel(v)[1]} for k, v in series.items()}

    # Cards instrument check: overlap is the stats fragment + virgin complete season,
    # while pre-stats levels are reported season-by-season as an audit only.
    overlap = analysis_rows({"2024/2025", "2025/2026"})
    both = [r for r in overlap if f(r, "yellow_cards_home") is not None and f(r, "yellow_cards_away") is not None]
    diffs = [(f(r,"yellow_cards_home")+f(r,"yellow_cards_away"))-(int(r["ev_yellow_home"])+int(r["ev_yellow_away"])) for r in both]
    out["cards_check"] = {"n_overlap_with_stats": len(both), "exact_agreement_pct": round(100*sum(d == 0 for d in diffs)/len(diffs), 1), "mean_stats_minus_events": round(st.mean(diffs), 3), "stats_lower_pct": round(100*sum(d < 0 for d in diffs)/len(diffs), 1), "stats_higher_pct": round(100*sum(d > 0 for d in diffs)/len(diffs), 1)}
    out["pre_stats_event_levels"] = {s: {"n": len(analysis_rows({s})), "mean_event_yellows": per[s]["event_yellows_per_match"]} for s in ("2021/2022", "2022/2023", "2023/2024")}
    out["overlap_event_levels"] = {s: per[s]["event_yellows_per_match"] for s in ("2024/2025", "2025/2026")}

    # Goals HT source and noise floor; only dev seasons feed the frozen constant.
    hs = [r for r in dev if int(r["home_goals"])+int(r["away_goals"]) > 0 and r["ht_source"] == "events"]
    shares = [(int(r["ht_home_goals"])+int(r["ht_away_goals"]))/(int(r["home_goals"])+int(r["away_goals"])) for r in hs]
    weights = [int(r["home_goals"])+int(r["away_goals"]) for r in hs]
    m, obs = st.mean(shares), st.variance(shares)
    noise = st.mean(m*(1-m)/w for w in weights)
    out["goals_halves"] = {"n": len(hs), "share_ratio_of_sums": round(sum(int(r["ht_home_goals"])+int(r["ht_away_goals"]) for r in hs)/sum(weights), 4), "obs_var": round(obs, 5), "binomial_noise_var": round(noise, 5), "excess_var": round(obs-noise, 5)}

    # X2: same-id transitions between the real parent corpus and this league.
    parent = list(csv.DictReader(open("/home/hatch/workspace/footballprediction/league/TR-SuperLig/data/tr_matches.csv", encoding="utf-8")))
    def clean(rows, league): return [r for r in rows if r.get("phase", "regular").startswith("regular") and r.get("awarded", "0") != "1" and r["season"] != "2026/2027"]
    p = clean(parent, "parent"); q = clean(ROWS, "child")
    def season_year(s): return int(s[:4])
    def team_season(rows):
        d = defaultdict(lambda: defaultdict(lambda: [0, 0, 0]))
        for r in rows:
            for side, opp in (("home", "away"), ("away", "home")):
                z = d[r[f"{side}_team_id"]][r["season"]]; z[0] += 1; z[1] += int(r[f"{side}_goals"]); z[2] += int(r[f"{opp}_goals"])
        return d
    ps, qs = team_season(p), team_season(q); movers = []
    for tid in sorted(set(ps) & set(qs)):
        for s in sorted(qs[tid]):
            prior = f"{season_year(s)-1}/{season_year(s)}"
            if prior in ps[tid]:
                a, b = ps[tid][prior], qs[tid][s]
                movers.append({"team_id": tid, "direction": "SuperLig_to_1Lig", "from_season": prior, "to_season": s, "from_gf": round(a[1]/a[0],3), "to_gf": round(b[1]/b[0],3), "gf_shift": round(b[1]/b[0]-a[1]/a[0],3), "from_ga": round(a[2]/a[0],3), "to_ga": round(b[2]/b[0],3), "ga_shift": round(b[2]/b[0]-a[2]/a[0],3)})
        for s in sorted(ps[tid]):
            prior = f"{season_year(s)-1}/{season_year(s)}"
            if prior in qs[tid]:
                a, b = qs[tid][prior], ps[tid][s]
                movers.append({"team_id": tid, "direction": "1Lig_to_SuperLig", "from_season": prior, "to_season": s, "from_gf": round(a[1]/a[0],3), "to_gf": round(b[1]/b[0],3), "gf_shift": round(b[1]/b[0]-a[1]/a[0],3), "from_ga": round(a[2]/a[0],3), "to_ga": round(b[2]/b[0],3), "ga_shift": round(b[2]/b[0]-a[2]/a[0],3)})
    out["x2_movers"] = {"n": len(movers), "transitions": movers, "by_direction": {d: {"n": sum(x["direction"] == d for x in movers), "mean_gf_shift": round(st.mean(x["gf_shift"] for x in movers if x["direction"] == d),3), "mean_ga_shift": round(st.mean(x["ga_shift"] for x in movers if x["direction"] == d),3)} for d in ("SuperLig_to_1Lig", "1Lig_to_SuperLig")}}

    out["buildability"] = {"G-TR1": "BUILDABLE", "S-TR1": "NOT BUILDABLE", "C-TR1": "NOT BUILDABLE", "T-TR1": "NOT BUILDABLE", "K-TR1": "PENDING_ARTIFACT_CHECK"}
    with open(HERE / "eda_numbers.json", "w", encoding="utf-8") as fh: json.dump(out, fh, indent=2, ensure_ascii=False)
    print(json.dumps({"cards_check": out["cards_check"], "x2": out["x2_movers"]["by_direction"], "goals_halves": out["goals_halves"]}, indent=2))

if __name__ == "__main__": main()
