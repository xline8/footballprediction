"""Compute the Scotland Championship Phase-A EDA and inventory artefacts.

Only descriptive statistics are produced here.  No model fitting or tuning is
performed, and 2025/2026 and 2026/2027 are used only in coverage/descriptive
summaries, not in primary-line selection or other modelling choices.
"""
import csv
import json
import math
import statistics as stats
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "sco_championship_matches.csv"
ROWS = list(csv.DictReader(DATA.open()))
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
DEV_SEASONS = ("2022/2023", "2023/2024", "2024/2025")


def val(row, key):
    x = row.get(key)
    return None if x in (None, "", "None") else float(x)


def mean_or_none(xs, nd=4):
    return round(stats.mean(xs), nd) if xs else None


def pearson(xs, ys):
    if len(xs) < 5:
        return None
    mx, my = stats.mean(xs), stats.mean(ys)
    den = math.sqrt(sum((x - mx) ** 2 for x in xs) * sum((y - my) ** 2 for y in ys))
    return (sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / den) if den else None


def halves(rows):
    ordered = sorted(rows, key=lambda r: (r["date"], r["match_id"]))
    cut = (len(ordered) + 1) // 2
    return ordered[:cut], ordered[cut:]


def side_value(row, side, metric, against=False):
    other = "away" if side == "home" else "home"
    if metric == "goals":
        return float(row[f"{other if against else side}_goals"])
    if metric == "yellow_events":
        return float(row[f"ev_yellow_{other if against else side}"])
    return val(row, f"{metric}_{other if against else side}")


def season_reliability(rows, metric):
    first, second = halves(rows)
    a, b = defaultdict(list), defaultdict(list)
    for subset, dest in ((first, a), (second, b)):
        for row in subset:
            for side in ("home", "away"):
                tid = row[f"{side}_team_id"]
                v_for = side_value(row, side, metric)
                v_against = side_value(row, side, metric, True)
                if v_for is not None and v_against is not None:
                    dest[(tid, "for")].append(v_for)
                    dest[(tid, "against")].append(v_against)
    out = {}
    for direction in ("for", "against"):
        keys = sorted(set(k[0] for k in a if k[1] == direction) & set(k[0] for k in b if k[1] == direction))
        xs = [stats.mean(a[(k, direction)]) for k in keys if a[(k, direction)] and b[(k, direction)]]
        ys = [stats.mean(b[(k, direction)]) for k in keys if a[(k, direction)] and b[(k, direction)]]
        out[direction] = {"r": round(pearson(xs, ys), 4) if pearson(xs, ys) is not None else None,
                          "n_teams": len(xs)}
    return out


def event_share(rows, numerator):
    shares, expected = [], []
    total_num = total_den = 0
    for row in rows:
        if numerator == "goals":
            one = float(row["ht_home_goals"]) + float(row["ht_away_goals"])
            total = float(row["home_goals"]) + float(row["away_goals"])
        else:
            one = sum(1 for side in ("home", "away") for e in [])  # kept explicit below
            # Event-level timing is not retained in the CSV; the builder's
            # half counters cover goals, while cards need a compact re-scan.
            one = val(row, "fh_event_yellow_total") or 0.0
            total = float(row["ev_yellow_home"]) + float(row["ev_yellow_away"])
        if total > 0:
            shares.append(one / total)
            expected.append((one / total) * (1 - one / total) / total)
            total_num += one; total_den += total
    p = total_num / total_den if total_den else None
    observed = (stats.pvariance(shares) if shares else None)
    # The null uses the pooled league share as the fixed binomial p.
    binom = (stats.mean([p * (1 - p) / (1 / s if False else 1) for s in []])
             if False else None)
    totals = []
    for row in rows:
        total = (float(row["home_goals"]) + float(row["away_goals"])) if numerator == "goals" else (float(row["ev_yellow_home"]) + float(row["ev_yellow_away"]))
        if total > 0:
            totals.append(total)
    binom = stats.mean([p * (1 - p) / n for n in totals]) if p is not None and totals else None
    return {"share": round(p, 6) if p is not None else None,
            "n_matches": len(shares), "observed_variance": round(observed, 8) if observed is not None else None,
            "binomial_noise_expected_variance": round(binom, 8) if binom is not None else None,
            "true_variance_estimate": round(observed - binom, 8) if observed is not None and binom is not None else None}


def referee_reliability(rows):
    # The reliability split is an era split over the complete observed
    # corpus. Coverage is still reported season by season as requested.
    ordered = sorted(rows, key=lambda r: (r["date"], r["match_id"]))
    first, second = halves(ordered)
    by_half = []
    for subset in (first, second):
        d = defaultdict(list)
        for r in subset:
            if r.get("referee"):
                d[r["referee"]].append(float(r["ev_yellow_home"]) + float(r["ev_yellow_away"]))
        by_half.append(d)
    refs = sorted(set(by_half[0]) & set(by_half[1]))
    refs = [ref for ref in refs if len(by_half[0][ref]) >= 8 and len(by_half[1][ref]) >= 8]
    x = [stats.mean(by_half[0][ref]) for ref in refs]
    y = [stats.mean(by_half[1][ref]) for ref in refs]
    r = pearson(x, y)
    coverage = {}
    for season in sorted(set(z["season"] for z in rows)):
        rs = [z for z in rows if z["season"] == season]
        coverage[season] = round(100 * sum(bool(z.get("referee")) for z in rs) / len(rs), 1)
    return {"split": {"r": round(r, 4) if r is not None else None,
                       "n_referees": len(refs), "minimum_matches_per_half": 8},
            "coverage_pct_by_season": coverage}


def membership(league_id):
    rows = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == str(league_id)]
    result = defaultdict(dict)
    for r in rows:
        payload = json.loads((MAIN_REPO / r["path"]).read_text())
        g = payload.get("general") or {}
        result[r["season"]][g["homeTeam"]["id"]] = g["homeTeam"]["name"]
        result[r["season"]][g["awayTeam"]["id"]] = g["awayTeam"]["name"]
    return result


def x2_movers(rows):
    champs = membership(123); prem = membership(64); one = membership(124)
    seasons = ("2022/2023", "2023/2024", "2024/2025", "2025/2026")
    out = {}
    pooled = {"relegated_from_premiership": [], "promoted_from_league_one": []}
    for season in seasons:
        prev = f"{int(season[:4])-1}/{int(season[:4])}"
        current = set(champs.get(season, {})); prior = set(champs.get(prev, {}))
        relegated = sorted((set(prem.get(prev, {})) - prior) & current)
        promoted = sorted((set(one.get(prev, {})) - prior) & current)
        rs = [r for r in rows if r["season"] == season]
        league_gf = stats.mean(float(r["home_goals"]) + float(r["away_goals"]) for r in rs)
        # league mean per team-match (same as total goals/match for GF and GA).
        mean_gf = stats.mean([float(r[f"{side}_goals"]) for r in rs for side in ("home", "away")])
        def group(ids):
            tm = [(r, side) for r in rs for side in ("home", "away") if int(r[f"{side}_team_id"]) in ids]
            gf = stats.mean([float(r[f"{side}_goals"]) for r, side in tm]) if tm else None
            ga = stats.mean([float(r[f"{'away' if side=='home' else 'home'}_goals"]) for r, side in tm]) if tm else None
            return {"team_ids": ids, "teams": [champs[season].get(i, str(i)) for i in ids],
                    "n_team_matches": len(tm), "gf_per_match": round(gf, 4) if gf is not None else None,
                    "ga_per_match": round(ga, 4) if ga is not None else None,
                    "gf_delta_vs_league": round(gf - mean_gf, 4) if gf is not None else None,
                    "ga_delta_vs_league": round(ga - mean_gf, 4) if ga is not None else None}
        out[season] = {"league_gf_per_match": round(mean_gf, 4), "league_ga_per_match": round(mean_gf, 4),
                       "relegated_from_premiership": group(relegated),
                       "promoted_from_league_one": group(promoted)}
        for direction, ids in (("relegated_from_premiership", relegated), ("promoted_from_league_one", promoted)):
            tm = group(ids)
            if tm["gf_delta_vs_league"] is not None:
                pooled[direction].append(tm)
    pooled_out = {}
    for direction, groups in pooled.items():
        pooled_out[direction] = {"seasons": len(groups), "team_season_groups": groups,
                                 "mean_gf_delta": round(stats.mean([g["gf_delta_vs_league"] for g in groups]), 4) if groups else None,
                                 "mean_ga_delta": round(stats.mean([g["ga_delta_vs_league"] for g in groups]), 4) if groups else None}
    return {"by_season": out, "pooled": pooled_out}


def main():
    seasons = sorted(set(r["season"] for r in ROWS))
    per = {}
    missing = {}
    for season in seasons:
        rs = [r for r in ROWS if r["season"] == season]
        def target_total(key):
            xs = [val(r, f"{key}_home") + val(r, f"{key}_away") for r in rs if val(r, f"{key}_home") is not None and val(r, f"{key}_away") is not None]
            return mean_or_none(xs, 3)
        per[season] = {"n": len(rs),
                       "goals_per_match": round(stats.mean(float(r["home_goals"]) + float(r["away_goals"]) for r in rs), 3),
                       "home_goal_share": round(sum(float(r["home_goals"]) for r in rs) / sum(float(r["home_goals"]) + float(r["away_goals"]) for r in rs), 4),
                       "sot_per_match": target_total("ShotsOnTarget"), "corners_per_match": target_total("corners"),
                       "total_shots_per_match": target_total("total_shots"),
                       "event_yellows_per_match": round(stats.mean(float(r["ev_yellow_home"]) + float(r["ev_yellow_away"]) for r in rs), 3),
                       "red_events_per_match": round(stats.mean(float(r["ev_red_home"]) + float(r["ev_red_away"]) for r in rs), 3),
                       "stats_all_n": sum(int(r["has_stats_all"]) for r in rs),
                       "referee_n": sum(bool(r.get("referee")) for r in rs)}
        missing[season] = [{k: r[k] for k in ("match_id", "date", "round", "home_team", "away_team", "has_stats_all")}
                           for r in rs if not int(r["has_stats_all"])]
    line_specs = {"goals_ou_2.5": ("goals", 2.5),
                  "sot_7.5": ("ShotsOnTarget", 7.5), "sot_8.5": ("ShotsOnTarget", 8.5), "sot_9.5": ("ShotsOnTarget", 9.5),
                  "corners_8.5": ("corners", 8.5), "corners_9.5": ("corners", 9.5), "corners_10.5": ("corners", 10.5),
                  "event_yellows_3.5": ("event_yellows", 3.5), "event_yellows_4.5": ("event_yellows", 4.5), "event_yellows_5.5": ("event_yellows", 5.5),
                  "total_shots_13.5": ("total_shots", 13.5), "total_shots_14.5": ("total_shots", 14.5), "total_shots_15.5": ("total_shots", 15.5), "total_shots_16.5": ("total_shots", 16.5)}
    over = {}
    for name, (metric, line) in line_specs.items():
        vals = []
        for r in ROWS:
            if r["season"] not in DEV_SEASONS: continue
            if metric == "goals": x = float(r["home_goals"]) + float(r["away_goals"])
            elif metric == "event_yellows": x = float(r["ev_yellow_home"]) + float(r["ev_yellow_away"])
            else:
                h, a = val(r, f"{metric}_home"), val(r, f"{metric}_away")
                if h is None or a is None: continue
                x = h + a
            vals.append(x > line)
        over[name] = {"n": len(vals), "over_rate": round(sum(vals) / len(vals), 6) if vals else None,
                      "distance_from_0.5": round(abs(sum(vals) / len(vals) - 0.5), 6) if vals else None}
    chosen = {}
    for market in ("goals", "sot", "corners", "event_yellows", "total_shots"):
        choices = {k: v for k, v in over.items() if k.startswith(market + "_") or (market == "goals" and k == "goals_ou_2.5")}
        chosen[market] = min(choices, key=lambda k: choices[k]["distance_from_0.5"])
    metrics = {"goals": "goals", "sot": "ShotsOnTarget", "corners": "corners", "total_shots": "total_shots", "event_yellows": "yellow_events", "possession": "BallPossesion"}
    reliabilities = {name: {season: season_reliability([r for r in ROWS if r["season"] == season], metric)
                            for season in seasons} for name, metric in metrics.items()}
    for name, vals in reliabilities.items():
        season_vals = {s: vals[s] for s in seasons}
        for direction in ("for", "against"):
            rs = [v[direction]["r"] for v in season_vals.values() if v[direction]["r"] is not None]
            vals[f"mean_{direction}_r"] = round(stats.mean(rs), 4) if rs else None
    halves_summary = {"goals": {"pooled": event_share(ROWS, "goals"),
                                "per_season": {s: event_share([r for r in ROWS if r["season"] == s], "goals") for s in seasons}},
                      "event_yellows": {"note": "First-half card counts were recomputed from source JSONs below.",
                                        "pooled": None, "per_season": {}}}
    # Re-scan source events for yellow half shares, without changing the CSV schema.
    yellow_rows = []
    for ir in csv.DictReader(INDEX.open()):
        if ir["league_id"] != "123": continue
        payload = json.loads((MAIN_REPO / ir["path"]).read_text()); es = (((payload.get("content") or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []
        one = sum(1 for e in es if e.get("type") == "Card" and e.get("card") == "Yellow" and e.get("time") is not None and e["time"] <= 45)
        total = sum(1 for e in es if e.get("type") == "Card" and e.get("card") == "Yellow")
        yellow_rows.append((ir["season"], one, total))
    def share_tuples(items):
        usable = [(a, b) for _, a, b in items if b > 0]; p = sum(a for a, _ in usable) / sum(b for _, b in usable) if usable else None
        shares = [a / b for a, b in usable]; observed = stats.pvariance(shares) if shares else None
        expected = stats.mean([p * (1 - p) / b for _, b in usable]) if p is not None else None
        return {"share": round(p, 6) if p is not None else None, "n_matches": len(usable), "observed_variance": round(observed, 8) if observed is not None else None,
                "binomial_noise_expected_variance": round(expected, 8) if expected is not None else None,
                "true_variance_estimate": round(observed - expected, 8) if observed is not None and expected is not None else None}
    halves_summary["event_yellows"]["pooled"] = share_tuples(yellow_rows)
    for s in seasons: halves_summary["event_yellows"]["per_season"][s] = share_tuples([x for x in yellow_rows if x[0] == s])
    rich = [r for r in ROWS if val(r, "yellow_cards_home") is not None and val(r, "yellow_cards_away") is not None]
    diffs = [val(r, "yellow_cards_home") + val(r, "yellow_cards_away") - float(r["ev_yellow_home"]) - float(r["ev_yellow_away"]) for r in rich]
    cards_artifact = {"n_rich_matches": len(rich), "exact_agree_n": sum(d == 0 for d in diffs),
                      "exact_agree_pct": round(100 * sum(d == 0 for d in diffs) / len(diffs), 2),
                      "mean_signed_diff_stats_minus_events": round(stats.mean(diffs), 4),
                      "mean_absolute_diff": round(stats.mean(abs(d) for d in diffs), 4)}
    summary = {"n": len(ROWS), "seasons": seasons, "dev_seasons": DEV_SEASONS, "per_season": per,
               "primary_lines": {"over_rates": over, "chosen": chosen}, "reliability": reliabilities,
               "halves": halves_summary, "referee_strictness": referee_reliability(ROWS),
               "cards_stats_vs_events": cards_artifact, "x2_movers": x2_movers(ROWS),
               "no_playoff_rows": True, "phase": "regular"}
    inventory = {"n": len(ROWS), "season_n": {s: sum(r["season"] == s for r in ROWS) for s in seasons},
                 "stats_all_n": {s: per[s]["stats_all_n"] for s in seasons}, "missing_stats_all": missing,
                 "rich_stats_yellow_n": len(rich), "event_n": sum(int(r["has_events"]) for r in ROWS),
                 "referee_n": {s: per[s]["referee_n"] for s in seasons},
                 "team_ids": sorted(set(r["home_team_id"] for r in ROWS) | set(r["away_team_id"] for r in ROWS)),
                 "has_shotmap_n": 0, "playoff_rows": 0}
    (HERE / "eda_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (HERE / "inventory_summary.json").write_text(json.dumps(inventory, indent=2) + "\n")
    print(json.dumps({"n": len(ROWS), "chosen": chosen, "cards": cards_artifact}, indent=2))


if __name__ == "__main__":
    main()
