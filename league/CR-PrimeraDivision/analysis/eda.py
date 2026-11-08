"""EDA for Costa Rica Primera Division (scores + events only).

Reads league/CR-PrimeraDivision/data/cr_matches.csv and writes
analysis/eda_summary.json + analysis/inventory_summary.json.
Every number cited in EDA.md must come from these files.

Methods (J1 standard):
- Split-half reliability: career-pooled per team (>=24 matches), ratio-of-sums
  within halves, 60 random splits averaged + odd/even split.
- Halves variance decomposition: observed variance of the per-match 1H share
  minus the binomial noise floor mean(p(1-p)/total); true variance <= 0 means
  the per-match share is pure noise around the frozen constant.
- Regular season = stage == regular. Playoffs (final_stage, championship_final)
  are reported separately and excluded from fitting scope.

Usage: python3 league/CR-PrimeraDivision/analysis/eda.py
"""
import csv
import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "cr_matches.csv"
OUT_EDA = HERE / "eda_summary.json"
OUT_INV = HERE / "inventory_summary.json"

RELIABLE_CARDS_FROM = "2023/2024"  # diagnosed in this script; see card diagnostics
SEASONS = ["2021/2022", "2022/2023", "2023/2024", "2024/2025", "2025/2026", "2026/2027"]


def safe_write_text(path, text, tries=40):
    data = text.encode("utf-8")
    for _ in range(tries):
        try:
            tmp = str(path) + ".tmp%d" % os.getpid()
            with open(tmp, "wb") as f:
                f.write(data)
                f.flush()
                os.fsync(f.fileno())
            if os.path.getsize(tmp) != len(data):
                raise IOError("size mismatch")
            os.replace(tmp, path)
            if os.path.getsize(path) == len(data):
                return
        except (PermissionError, OSError):
            time.sleep(1.0)
    raise IOError("could not write %s" % path)


def load():
    rows = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "match_id": r["match_id"], "season": r["season"], "date": r["date_utc"],
                "tournament": r["tournament"], "stage": r["stage"], "round": r["round"],
                "hi": int(r["home_id"]), "home": r["home_name"],
                "ai": int(r["away_id"]), "away": r["away_name"],
                "yh": int(r["home_goals"]), "ya": int(r["away_goals"]),
                "ht_h": int(r["ht_home_goals"]) if r["ht_home_goals"] else None,
                "ht_a": int(r["ht_away_goals"]) if r["ht_away_goals"] else None,
                "g1h": int(r["goals_1h_total"]) if r["goals_1h_total"] else None,
                "g2h": int(r["goals_2h_total"]) if r["goals_2h_total"] else None,
                "yell_h": int(r["yellow_home"]), "yell_a": int(r["yellow_away"]),
                "yell": int(r["yellow_total"]),
                "red_h": int(r["red_home"]), "red_a": int(r["red_away"]),
                "y1h_h": int(r["yellow_1h_home"]) if r["yellow_1h_home"] else None,
                "y1h_a": int(r["yellow_1h_away"]) if r["yellow_1h_away"] else None,
                "c1h": int(r["cards_1h_total"]) if r["cards_1h_total"] else None,
                "c2h": int(r["cards_2h_total"]) if r["cards_2h_total"] else None,
                "referee": r["referee"] or None,
                "events": r["events_present"] == "True",
                "mismatch": r["goal_event_mismatch"] == "True",
            })
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    return rows


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def var(xs):
    if len(xs) < 2:
        return None
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / (len(xs) - 1)


def levels(rows):
    n = len(rows)
    goals = [r["yh"] + r["ya"] for r in rows]
    return {
        "n": n,
        "goals_per_match": mean(goals),
        "home_goals_per_match": mean([r["yh"] for r in rows]),
        "away_goals_per_match": mean([r["ya"] for r in rows]),
        "home_advantage_goals": mean([r["yh"] - r["ya"] for r in rows]),
        "home_win_pct": sum(r["yh"] > r["ya"] for r in rows) / n,
        "draw_pct": sum(r["yh"] == r["ya"] for r in rows) / n,
        "away_win_pct": sum(r["yh"] < r["ya"] for r in rows) / n,
        "btts_pct": sum(r["yh"] > 0 and r["ya"] > 0 for r in rows) / n,
        "over_2_5_pct": sum(g > 2.5 for g in goals) / n,
        "goals_dispersion_var_mean": var(goals) / mean(goals),
        "yellows_per_match": mean([r["yell"] for r in rows]),
        "yellows_dispersion_var_mean": var([r["yell"] for r in rows]) / mean([r["yell"] for r in rows]),
        "reds_per_match": mean([r["red_h"] + r["red_a"] for r in rows]),
        "over_yellow_3_5_pct": sum(r["yell"] > 3.5 for r in rows) / n,
        "over_yellow_4_5_pct": sum(r["yell"] > 4.5 for r in rows) / n,
        "over_yellow_5_5_pct": sum(r["yell"] > 5.5 for r in rows) / n,
    }


def split_half(rows, for_key, against_key, min_matches=24, splits=60, seed=7):
    """Career-pooled split-half r for a per-team trait (ratio of sums).

    rows: list of dicts with hi/ai ids; for_key/against_key: functions
    row, team_is_home -> (numerator, denominator) for that team's trait.
    Returns dict with r_random (mean over splits), r_odd_even, n_teams.
    """
    by_team = defaultdict(list)
    for r in rows:
        by_team[r["hi"]].append((r, True))
        by_team[r["ai"]].append((r, False))
    teams = {t: v for t, v in by_team.items() if len(v) >= min_matches}
    if len(teams) < 3:
        return {"r_random": None, "r_odd_even": None, "n_teams": len(teams)}
    rng = random.Random(seed)

    def trait(pairs):
        num = den = 0.0
        for r, is_home in pairs:
            a, b = for_key(r, is_home), against_key(r, is_home)
            num += a
            den += b
        return num / den if den else None

    def corr(xs, ys):
        n = len(xs)
        mx, my = mean(xs), mean(ys)
        sx = sum((x - mx) ** 2 for x in xs)
        sy = sum((y - my) ** 2 for y in ys)
        if sx == 0 or sy == 0:
            return None
        return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / math.sqrt(sx * sy)

    rs = []
    for _ in range(splits):
        xs, ys = [], []
        for t, pairs in teams.items():
            idx = list(range(len(pairs)))
            rng.shuffle(idx)
            half = len(idx) // 2
            a = trait([pairs[i] for i in idx[:half]])
            b = trait([pairs[i] for i in idx[half:]])
            if a is not None and b is not None:
                xs.append(a)
                ys.append(b)
        c = corr(xs, ys)
        if c is not None:
            rs.append(c)
    xs, ys = [], []
    for t, pairs in teams.items():
        a = trait(pairs[0::2])
        b = trait(pairs[1::2])
        if a is not None and b is not None:
            xs.append(a)
            ys.append(b)
    return {"r_random": mean(rs), "r_odd_even": corr(xs, ys), "n_teams": len(teams)}


def halves_analysis(rows, total_key, first_key):
    """Pooled 1H share (ratio of sums) + variance decomposition + team split-half."""
    sub = [r for r in rows if r[first_key] is not None and r[total_key] is not None and r[total_key] > 0]
    tot = sum(r[total_key] for r in sub)
    fst = sum(r[first_key] for r in sub)
    p = fst / tot if tot else None
    shares = [r[first_key] / r[total_key] for r in sub]
    obs_var = var(shares)
    noise = mean([p * (1 - p) / r[total_key] for r in sub]) if p is not None else None
    true_var = (obs_var - noise) if (obs_var is not None and noise is not None) else None
    per_season = {}
    for s in SEASONS:
        ss = [r for r in sub if r["season"] == s]
        t2 = sum(r[total_key] for r in ss)
        f2 = sum(r[first_key] for r in ss)
        per_season[s] = {"n": len(ss), "share": (f2 / t2 if t2 else None)}
    return {
        "n": len(sub), "pooled_share": p,
        "observed_var": obs_var, "noise_floor": noise, "true_var": true_var,
        "per_season": per_season,
    }


def main():
    rows = load()
    reg = [r for r in rows if r["stage"] == "regular"]
    rel = [r for r in reg if r["season"] >= RELIABLE_CARDS_FROM]
    eda = {"scope": {"all_matches": len(rows), "regular_only": len(reg),
                      "reliable_cards_era": RELIABLE_CARDS_FROM,
                      "reliable_cards_regular_n": len(rel)},
           "levels_all": {}, "levels_regular": {}, "levels_pooled": {}}
    for s in SEASONS:
        eda["levels_all"][s] = levels([r for r in rows if r["season"] == s])
        eda["levels_regular"][s] = levels([r for r in reg if r["season"] == s])
    eda["levels_pooled"]["all"] = levels(rows)
    eda["levels_pooled"]["regular"] = levels(reg)
    eda["levels_pooled"]["regular_reliable_cards"] = levels(rel)

    # trait reliabilities (regular season only)
    gf = lambda r, h: (r["yh"] if h else r["ya"])
    ga = lambda r, h: (r["ya"] if h else r["yh"])
    one = lambda r, h: 1
    eda["reliability"] = {
        "goals_for": split_half(reg, gf, one),
        "goals_against": split_half(reg, ga, one),
        "yellows_for": split_half(rel, lambda r, h: (r["yell_h"] if h else r["yell_a"]), one),
        "yellows_against": split_half(rel, lambda r, h: (r["yell_a"] if h else r["yell_h"]), one),
    }
    # halves (match-total 1H shares + variance decomposition + team split-half)
    for r in reg:
        r["yh_ya_total"] = r["yh"] + r["ya"]
    eda["halves"] = {
        "goals": halves_analysis(reg, "yh_ya_total", "g1h"),
        "yellows_reliable": halves_analysis(rel, "yell", "c1h"),
    }
    # team split-half of the 1H share: trait = team's 1H goals (or yellows)
    # divided by the team's total goals (or yellows), ratio of sums.
    eda["halves"]["goals"]["team_split_half"] = split_half(
        [r for r in reg if r["g1h"] is not None],
        lambda r, h: (r["ht_h"] if h else r["ht_a"]),
        lambda r, h: (r["yh"] if h else r["ya"]),
    )
    eda["halves"]["yellows_reliable"]["team_split_half"] = split_half(
        [r for r in rel if r["c1h"] is not None],
        lambda r, h: (r["y1h_h"] if h else r["y1h_a"]),
        lambda r, h: (r["yell_h"] if h else r["yell_a"]),
    )

    # card-feed diagnostics: per season-month mean yellows + zero-card rate
    diag = {}
    by_sm = defaultdict(list)
    for r in rows:
        by_sm[(r["season"], r["date"][:7])].append(r)
    for k in sorted(by_sm):
        rs = by_sm[k]
        diag["%s %s" % k] = {
            "n": len(rs),
            "mean_yellows": mean([r["yell"] for r in rs]),
            "zero_card_rate": sum(r["yell"] == 0 for r in rs) / len(rs),
            "matches_with_yellow_event": sum(r["yell_h"] + r["yell_a"] > 0 for r in rs),
        }
    eda["card_feed_diagnostics"] = diag
    eda["card_feed_by_season"] = {
        s: {"n": sum(1 for r in rows if r["season"] == s),
            "mean_yellows": mean([r["yell"] for r in rows if r["season"] == s]),
            "zero_card_matches": sum(1 for r in rows if r["season"] == s and r["yell"] == 0),
            "matches_with_yellow_event": sum(
                1 for r in rows if r["season"] == s and r["yell_h"] + r["yell_a"] > 0),
            "referee_known": sum(1 for r in rows if r["season"] == s and r["referee"])}
        for s in SEASONS
    }
    # thin-history check: prior regular-season matches per team at each target-season cutoff
    thin = {}
    for target in ("2022/2023", "2023/2024", "2024/2025"):
        prior = [r for r in reg if r["season"] < target]
        counts = Counter()
        for r in prior:
            counts[r["hi"]] += 1
            counts[r["ai"]] += 1
        teams_target = {r["hi"] for r in reg if r["season"] == target} | \
                       {r["ai"] for r in reg if r["season"] == target}
        ns = {t: counts.get(t, 0) for t in teams_target}
        thin[target] = {"min_prior_matches": min(ns.values()), "n_teams": len(ns),
                        "teams_with_lt_10": sorted(t for t, n in ns.items() if n < 10),
                        "teams_with_zero": sorted(t for t, n in ns.items() if n == 0)}
    eda["thin_history"] = thin
    # cards distribution (reliable era, regular)
    eda["cards_distribution_reliable"] = {
        "mean": mean([r["yell"] for r in rel]),
        "p_over_3_5": sum(r["yell"] > 3.5 for r in rel) / len(rel),
        "p_over_4_5": sum(r["yell"] > 4.5 for r in rel) / len(rel),
        "p_over_5_5": sum(r["yell"] > 5.5 for r in rel) / len(rel),
    }
    safe_write_text(OUT_EDA, json.dumps(eda, indent=2) + "\n")

    # inventory
    inv = {"per_tournament_season_round": {}, "team_churn": {}, "mismatch_ids": [],
           "no_events_ids": [], "referee_coverage": {}, "format_notes": []}
    c = Counter()
    for r in rows:
        c[(r["tournament"], r["season"], r["stage"], r["round"])] += 1
    for k in sorted(c, key=lambda x: (x[1], x[0], x[2], str(x[3]))):
        inv["per_tournament_season_round"][" | ".join(str(x) for x in k)] = c[k]
    for s in SEASONS:
        teams = {r["hi"] for r in rows if r["season"] == s} | {r["ai"] for r in rows if r["season"] == s}
        prev = {r["hi"] for r in rows if r["season"] < s} | {r["ai"] for r in rows if r["season"] < s} \
            if s != SEASONS[0] else set()
        prev_season = SEASONS[SEASONS.index(s) - 1] if s != SEASONS[0] else None
        prev_s_teams = ({r["hi"] for r in rows if r["season"] == prev_season} |
                        {r["ai"] for r in rows if r["season"] == prev_season}) if prev_season else set()
        inv["team_churn"][s] = {
            "n_teams": len(teams),
            "entered_vs_prev_season": sorted(teams - prev_s_teams),
            "left_vs_prev_season": sorted(prev_s_teams - teams),
            "new_to_warehouse": sorted(teams - prev),
        }
    inv["mismatch_ids"] = [r["match_id"] for r in rows if r["mismatch"]]
    inv["no_events_ids"] = [r["match_id"] for r in rows if not r["events"]]
    inv["no_half_event_ids"] = [r["match_id"] for r in rows if r["ht_h"] is None]
    for s in SEASONS:
        rs = [r for r in rows if r["season"] == s]
        inv["referee_coverage"][s] = {"known": sum(1 for r in rs if r["referee"]), "n": len(rs)}
    # team id -> canonical name map for the churn ids
    names = {}
    for r in rows:
        names[r["hi"]] = r["home"]
        names[r["ai"]] = r["away"]
    inv["team_names"] = {str(k): v for k, v in sorted(names.items())}
    safe_write_text(OUT_INV, json.dumps(inv, indent=2) + "\n")
    print("goals pooled (regular): %.4f" % eda["levels_pooled"]["regular"]["goals_per_match"])
    print("yellows pooled (regular, reliable era): %.4f"
          % eda["levels_pooled"]["regular_reliable_cards"]["yellows_per_match"])
    print("goals 1H share pooled: %.4f" % eda["halves"]["goals"]["pooled_share"])
    print("yellows 1H share pooled (reliable): %.4f"
          % eda["halves"]["yellows_reliable"]["pooled_share"])
    print("reliability goals_for r_random: %.3f" % (eda["reliability"]["goals_for"]["r_random"] or -9))
    print("wrote", OUT_EDA, "and", OUT_INV)


if __name__ == "__main__":
    main()
