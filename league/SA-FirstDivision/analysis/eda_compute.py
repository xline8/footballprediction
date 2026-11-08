"""EDA computations for SA-FirstDivision -> eda_numbers.json (for EDA.md).

VIRGIN DISCIPLINE: only DEV seasons are analysed.
- Goals: 2024/2025 regular played (n=306).
- SOT/corners/total-shots/yellows: 2025/2026 regular played (n=304).
2025/2026 goals levels and ALL 2026/2027 outcome levels are NEVER
computed here (goals virgin / count-markets virgin).
Regular played = phase=='regular' AND awarded=='0' throughout.

Methods copied from league/SA-ProLeague/analysis/eda_compute.py:
split-half odd/even per team (min 10), Pearson corr; half_share with
observed SD / binomial noise floor / true SD; dev over-rate ladders.
"""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROWS = [r for r in csv.DictReader(open(HERE.parent / "data" / "safd_matches.csv"))]
REG = [r for r in ROWS if r["phase"] == "regular" and r["awarded"] == "0"]
DEV_G = [r for r in REG if r["season"] == "2024/2025"]   # goals dev, n=306
DEV_C = [r for r in REG if r["season"] == "2025/2026"]   # count dev, n=304
assert len(DEV_G) == 306, len(DEV_G)
assert len(DEV_C) == 304, len(DEV_C)

def f(r, k):
    v = r.get(k)
    return None if v in (None, "", "None") else float(v)

def corr(xs, ys):
    if len(xs) < 5:
        return None
    mx, my = st.mean(xs), st.mean(ys)
    num = sum((a - mx) * (b - my) for a, b in zip(xs, ys))
    den = math.sqrt(sum((a - mx) ** 2 for a in xs) * sum((b - my) ** 2 for b in ys))
    return round(num / den, 3) if den else None

def split_half(vals_by_team, min_n=10):
    xs, ys = [], []
    for t, vs in vals_by_team.items():
        if len(vs) >= min_n:
            xs.append(st.mean(vs[0::2])); ys.append(st.mean(vs[1::2]))
    return corr(xs, ys), len(xs)

def team_series(key, rows):
    d = defaultdict(list)
    for r in rows:
        for side in ("home", "away"):
            v = f(r, f"{key}_{side}")
            if v is not None:
                d[r[f"{side}_team_id"]].append(v)
    return d

def goals_series(rows, against=False):
    d = defaultdict(list)
    for r in rows:
        d[r["home_team_id"]].append(int(r["away_goals"] if against else r["home_goals"]))
        d[r["away_team_id"]].append(int(r["home_goals"] if against else r["away_goals"]))
    return d

out = {"n_rows": len(ROWS), "n_regular_played": len(REG),
       "dev_goals_n": len(DEV_G), "dev_count_n": len(DEV_C)}

# ---- F1 levels: goals 2024/25 ----
g_tot = [int(r["home_goals"]) + int(r["away_goals"]) for r in DEV_G]
out["goals_dev_2024_25"] = {
    "n": len(DEV_G), "goals_per_match": round(st.mean(g_tot), 3),
    "home_goals": round(st.mean([int(r["home_goals"]) for r in DEV_G]), 3),
    "away_goals": round(st.mean([int(r["away_goals"]) for r in DEV_G]), 3),
    "home_edge": round(st.mean([int(r["home_goals"]) for r in DEV_G]) - st.mean([int(r["away_goals"]) for r in DEV_G]), 3),
    "home_win_pct": round(100 * st.mean([1 if int(r["home_goals"]) > int(r["away_goals"]) else 0 for r in DEV_G]), 1),
    "draw_pct": round(100 * st.mean([1 if int(r["home_goals"]) == int(r["away_goals"]) else 0 for r in DEV_G]), 1),
    "away_win_pct": round(100 * st.mean([1 if int(r["home_goals"]) < int(r["away_goals"]) else 0 for r in DEV_G]), 1),
    "ou15_pct": round(100 * st.mean([1 if t > 1.5 else 0 for t in g_tot]), 1),
    "ou25_pct": round(100 * st.mean([1 if t > 2.5 else 0 for t in g_tot]), 1),
    "ou35_pct": round(100 * st.mean([1 if t > 3.5 else 0 for t in g_tot]), 1),
    "btts_pct": round(100 * st.mean([1 if int(r["home_goals"]) > 0 and int(r["away_goals"]) > 0 else 0 for r in DEV_G]), 1),
}
gd = defaultdict(list)
for r in DEV_G:
    gd[r["home_team_id"]].append(int(r["home_goals"]) - int(r["away_goals"]))
    gd[r["away_team_id"]].append(int(r["away_goals"]) - int(r["home_goals"]))
gd_means = {t: round(st.mean(v), 3) for t, v in gd.items() if len(v) >= 20}
out["goals_dev_2024_25"]["gd_spread_sd"] = round(st.stdev(list(gd_means.values())), 3)
out["goals_dev_2024_25"]["gd_top"] = sorted(gd_means.items(), key=lambda kv: -kv[1])[:3]
out["goals_dev_2024_25"]["gd_bottom"] = sorted(gd_means.items(), key=lambda kv: kv[1])[:2]

# ---- F1 levels: count targets 2025/26 ----
def tot_mean(rows, key):
    vals = [f(r, f"{key}_home") + f(r, f"{key}_away") for r in rows
            if f(r, f"{key}_home") is not None]
    return round(st.mean(vals), 3) if vals else None

def home_away(rows, key):
    h = [f(r, f"{key}_home") for r in rows if f(r, f"{key}_home") is not None]
    a = [f(r, f"{key}_away") for r in rows if f(r, f"{key}_away") is not None]
    return round(st.mean(h), 3), round(st.mean(a), 3)

cnt = {}
for name, key in [("sot", "ShotsOnTarget"), ("corners", "corners"),
                  ("shots", "total_shots"), ("yellows_stats", "yellow_cards"),
                  ("touches", "touches_opp_box"), ("big_chance", "big_chance"),
                  ("fouls", "fouls")]:
    h, a = home_away(DEV_C, key)
    cnt[name] = {"mean": tot_mean(DEV_C, key), "home": h, "away": a}
cnt["yellows_events"] = {
    "mean": round(st.mean([f(r, "yellow_home") + f(r, "yellow_away") for r in DEV_C]), 3),
    "home": round(st.mean([f(r, "yellow_home") for r in DEV_C]), 3),
    "away": round(st.mean([f(r, "yellow_away") for r in DEV_C]), 3)}
cnt["red_cards"] = {"mean": tot_mean(DEV_C, "red_cards")}
out["count_levels_dev_2025_26"] = cnt

# ---- F2 reliabilities: split-half WITHIN each dev season ----
rel_g, rel_g_n = {}, {}
for name, series in [("goals_for", goals_series(DEV_G)),
                     ("goals_against", goals_series(DEV_G, against=True))]:
    r, n = split_half(series)
    rel_g[name] = r; rel_g_n[name] = n
out["reliability_goals_2024_25"] = rel_g
out["reliability_goals_n"] = rel_g_n

rel_c, rel_c_n = {}, {}
for name, key in [("sot_for", "ShotsOnTarget"), ("corners_for", "corners"),
                  ("shots_for", "total_shots"), ("yellows_events_for", "yellow"),
                  ("yellows_stats_for", "yellow_cards"),
                  ("touches_for", "touches_opp_box"), ("big_chance_for", "big_chance"),
                  ("possession", "BallPossesion"), ("fouls_for", "fouls")]:
    r, n = split_half(team_series(key, DEV_C))
    rel_c[name] = r; rel_c_n[name] = n
# against-series for the main targets
for name, key in [("sot_against", "ShotsOnTarget"), ("corners_against", "corners"),
                  ("shots_against", "total_shots"), ("touches_against", "touches_opp_box")]:
    d = defaultdict(list)
    for r in DEV_C:
        for side, oside in (("home", "away"), ("away", "home")):
            v = f(r, f"{key}_{oside}")
            if v is not None:
                d[r[f"{side}_team_id"]].append(v)
    r, n = split_half(d)
    rel_c[name] = r; rel_c_n[name] = n
out["reliability_count_2025_26"] = rel_c
out["reliability_count_n"] = rel_c_n

# per-match correlations 2025/26 (territory link)
def per_match_corr(k1, k2, rows=DEV_C):
    xs, ys = [], []
    for r in rows:
        for side in ("home", "away"):
            a, b = f(r, f"{k1}_{side}"), f(r, f"{k2}_{side}")
            if a is not None and b is not None:
                xs.append(a); ys.append(b)
    return corr(xs, ys), len(xs)
out["corr_touches_corners"], out["corr_touches_corners_n"] = per_match_corr("touches_opp_box", "corners")
out["corr_possession_corners"], _ = per_match_corr("BallPossesion", "corners")
out["corr_bigchance_corners"], _ = per_match_corr("big_chance", "corners")
out["corr_shots_sot"], _ = per_match_corr("total_shots", "ShotsOnTarget")

# R4: on-target-rate reliability (ratio of sums, split-half) 2025/26
def ratio_series(num, den, rows):
    per_team = defaultdict(list)
    for r in rows:
        for side in ("home", "away"):
            n_, d_ = f(r, f"{num}_{side}"), f(r, f"{den}_{side}")
            if n_ is not None and d_ is not None:
                per_team[r[f"{side}_team_id"]].append((n_, d_))
    xs, ys = [], []
    for t, ms in per_team.items():
        if len(ms) >= 10:
            for half, acc in ((ms[0::2], xs), (ms[1::2], ys)):
                sn = sum(a for a, b in half); sd = sum(b for a, b in half)
                acc.append(sn / sd if sd else 0)
    return corr(xs, ys), len(xs)
out["on_target_rate_rel_2025_26"], out["on_target_rate_rel_n"] = ratio_series(
    "ShotsOnTarget", "total_shots", DEV_C)

# ---- F7 cards feed recheck, dev season regular played ----
rs = DEV_C
ex = sum(1 for r in rs if f(r, "yellow_cards_home") + f(r, "yellow_cards_away")
         == f(r, "yellow_home") + f(r, "yellow_away"))
low = sum(1 for r in rs if f(r, "yellow_cards_home") + f(r, "yellow_cards_away")
          < f(r, "yellow_home") + f(r, "yellow_away"))
high = sum(1 for r in rs if f(r, "yellow_cards_home") + f(r, "yellow_cards_away")
           > f(r, "yellow_home") + f(r, "yellow_away"))
out["cards_agreement_dev_2025_26"] = {
    "n": len(rs), "exact": ex, "stats_low": low, "stats_high": high,
    "mean_diff": round(st.mean([f(r, "yellow_cards_home") + f(r, "yellow_cards_away")
                                - f(r, "yellow_home") - f(r, "yellow_away") for r in rs]), 3)}

# ---- F4 movers / churn (team ids) ----
def team_ids(season):
    s = set()
    for r in ROWS:
        if r["season"] == season:
            s.add(r["home_team_id"]); s.add(r["away_team_id"])
    return s
t24, t25, t26 = team_ids("2024/2025"), team_ids("2025/2026"), team_ids("2026/2027")
out["churn"] = {"teams_24_25": len(t24), "teams_25_26": len(t25), "teams_26_27": len(t26),
                "new_in_25_26": len(t25 - t24), "left_after_24_25": len(t24 - t25),
                "new_in_26_27": len(t26 - t25), "left_after_25_26": len(t25 - t26),
                "ever_present_24_26": len(t24 & t25)}

# ---- F3 halves constants, 2025/2026 regular played only ----
def half_share(stat_key, rows=DEV_C, event=False):
    shares, weights = [], []
    for r in rows:
        if event:
            a1, a2 = f(r, "fh_ev_yellow_home"), f(r, "fh_ev_yellow_away")
            b1, b2 = f(r, "yellow_home"), f(r, "yellow_away")
        else:
            a1, a2 = f(r, f"fh_{stat_key}_home"), f(r, f"fh_{stat_key}_away")
            b1, b2 = f(r, f"{stat_key}_home"), f(r, f"{stat_key}_away")
        if None in (a1, a2, b1, b2) or (b1 + b2) == 0:
            continue
        shares.append((a1 + a2) / (b1 + b2)); weights.append(b1 + b2)
    m = st.mean(shares); obs = st.variance(shares)
    noise = st.mean([m * (1 - m) / w for w in weights])
    return {"n": len(shares), "share": round(m, 4),
            "obs_sd": round(math.sqrt(obs), 4),
            "noise_sd": round(math.sqrt(noise), 4),
            "true_sd": round(math.sqrt(max(obs - noise, 0.0)), 4)}
out["half_shares_2025_26"] = {
    "sot": half_share("ShotsOnTarget"),
    "corners": half_share("corners"),
    "shots": half_share("total_shots"),
    "yellows_events": half_share(None, event=True)}

# ---- Primary-line ladders ----
def over_rate(vals, line):
    return round(st.mean([1 if v > line else 0 for v in vals]), 3)

lines = {}
gvals = [int(r["home_goals"]) + int(r["away_goals"]) for r in DEV_G]
lines["goals"] = {"mean": round(st.mean(gvals), 3),
                  "ladder": {str(L): over_rate(gvals, L) for L in (1.5, 2.5, 3.5)}}
for name, fn in [("sot", lambda r: f(r, "ShotsOnTarget_home") + f(r, "ShotsOnTarget_away")),
                 ("corners", lambda r: f(r, "corners_home") + f(r, "corners_away")),
                 ("shots", lambda r: f(r, "total_shots_home") + f(r, "total_shots_away")),
                 ("yellows", lambda r: f(r, "yellow_home") + f(r, "yellow_away"))]:
    vals = [fn(r) for r in DEV_C]
    cands = [x + 0.5 for x in range(int(min(vals)), int(max(vals)))]
    best = min(cands, key=lambda L: abs(over_rate(vals, L) - 0.5))
    lines[name] = {"mean": round(st.mean(vals), 3), "primary_line": best,
                   "over_rate": over_rate(vals, best),
                   "ladder": {str(L): over_rate(vals, L) for L in (best - 1, best, best + 1)}}
out["dev_lines"] = lines

# NOTE (2026-11-10): do NOT write eda_numbers.json from this script.
# In this exec sandbox, child processes cannot write file content
# (open(O_CREAT) succeeds, write() raises EPERM; only the shell's own
# builtins can write). Print the JSON to stdout (pipe to the tool)
# and save it with the muse.write tool instead.
print(json.dumps(out, default=str))
