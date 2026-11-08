"""Compute descriptive Phase-A EDA for SCO League One; never fit a model."""
import csv, json, math, statistics as st
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data" / "sco_league_one_matches.csv"
ROWS = list(csv.DictReader(DATA.open()))
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
SEASONS = tuple(sorted({r["season"] for r in ROWS}))
COMPLETE = SEASONS[:-1]
DEV = ("2022/2023", "2023/2024", "2024/2025")


def f(row, key):
    x = row.get(key)
    return None if x in (None, "", "None") else float(x)


def mean(xs): return round(st.mean(xs), 6) if xs else None


def pearson(xs, ys):
    if len(xs) < 5: return None
    mx, my = st.mean(xs), st.mean(ys)
    den = math.sqrt(sum((x-mx)**2 for x in xs) * sum((y-my)**2 for y in ys))
    return sum((x-mx)*(y-my) for x, y in zip(xs, ys)) / den if den else None


def split(rows):
    rows = sorted(rows, key=lambda r: (r["date"], r["match_id"]))
    cut = (len(rows) + 1) // 2
    return rows[:cut], rows[cut:]


def reliability(metric, seasons=COMPLETE):
    pairs = {"for": [], "against": []}
    for season in seasons:
        first, second = split([r for r in ROWS if r["season"] == season])
        halves = []
        for subset in (first, second):
            d = defaultdict(list)
            for r in subset:
                for side in ("home", "away"):
                    other = "away" if side == "home" else "home"
                    tid = r[f"{side}_team_id"]
                    if metric == "goals":
                        own, opp = r[f"{side}_goals"], r[f"{other}_goals"]
                    else:
                        own, opp = r[f"{metric}_{side}"], r[f"{metric}_{other}"]
                    d[(tid, "for")].append(float(own))
                    d[(tid, "against")].append(float(opp))
            halves.append(d)
        for direction in ("for", "against"):
            ids = sorted({k[0] for k in halves[0] if k[1] == direction} & {k[0] for k in halves[1] if k[1] == direction})
            pairs[direction].extend((st.mean(halves[0][(i, direction)]), st.mean(halves[1][(i, direction)])) for i in ids)
    out = {"method": "within-season first-half vs second-half team rates, pooled across complete seasons 2021/2022–2025/2026",
           "seasons_used": list(COMPLETE)}
    for direction in ("for", "against"):
        x, y = zip(*pairs[direction]) if pairs[direction] else ([], [])
        r = pearson(x, y)
        out[direction] = {"r": round(r, 6) if r is not None else None, "n_teams": len(x), "n_team_seasons": len(x)}
    return out


def share(rows, num_key, den_fn):
    usable = []
    for r in rows:
        if num_key == "ht_goals": n = float(r["ht_home_goals"]) + float(r["ht_away_goals"])
        elif num_key == "ht_yellows": n = float(r["ht_yellow_home"]) + float(r["ht_yellow_away"])
        else: n = f(r, num_key)
        d = den_fn(r)
        if n is not None and d > 0: usable.append((n, d))
    p = sum(n for n, _ in usable) / sum(d for _, d in usable) if usable else None
    vals = [n/d for n, d in usable]
    observed = st.pvariance(vals) if vals else None
    expected = st.mean([p*(1-p)/d for _, d in usable]) if p is not None else None
    true = observed - expected if observed is not None and expected is not None else None
    # Frozen as a presentation constant when the true per-match share
    # variance is negligible: true variance <= 0.0001 means an implied
    # per-match SD of <= 1pp. (Championship precedent froze yellows at
    # +0.0063; this league's pooled yellow value, +0.00002, is far
    # smaller still.)
    return {"share": round(p, 6) if p is not None else None, "n_matches": len(usable),
            "observed_variance": round(observed, 8) if observed is not None else None,
            "binomial_noise_expected_variance": round(expected, 8) if expected is not None else None,
            "true_variance_estimate": round(true, 8) if true is not None else None,
            "frozen_constant": true is not None and true <= 0.0001}


def membership(league_id):
    result = defaultdict(dict)
    with INDEX.open() as fh:
        for ir in csv.DictReader(fh):
            if ir["league_id"] != str(league_id): continue
            p = json.loads((MAIN_REPO / ir["path"]).read_text())
            g = p.get("general") or {}
            for side in ("homeTeam", "awayTeam"):
                t = g.get(side) or {}
                result[ir["season"]][str(t.get("id"))] = t.get("name")
    return result


def movers():
    one, champ = membership(124), membership(123)
    out, pooled = {}, {"down_from_championship": [], "up_other": []}
    for season in ("2022/2023", "2023/2024", "2024/2025", "2025/2026"):
        prev = f"{int(season[:4])-1}/{int(season[:4])}"
        entrants = set(one[season]) - set(one[prev])
        down = sorted(entrants & set(champ[prev])); up = sorted(entrants - set(champ[prev]))
        rs = [r for r in ROWS if r["season"] == season]
        league_rate = st.mean(float(r[f"{side}_goals"]) for r in rs for side in ("home", "away"))
        def group(ids, label):
            tm = [(r, side) for r in rs for side in ("home", "away") if r[f"{side}_team_id"] in ids]
            gf = st.mean(float(r[f"{side}_goals"]) for r, side in tm) if tm else None
            ga = st.mean(float(r[f"{'away' if side == 'home' else 'home'}_goals"]) for r, side in tm) if tm else None
            item = {"team_ids": ids, "teams": [one[season].get(i, str(i)) for i in ids],
                    "n_clubs": len(ids), "n_team_matches": len(tm),
                    "gf_per_match": round(gf, 6) if gf is not None else None,
                    "ga_per_match": round(ga, 6) if ga is not None else None,
                    "gf_delta_vs_league": round(gf-league_rate, 6) if gf is not None else None,
                    "ga_delta_vs_league": round(ga-league_rate, 6) if ga is not None else None}
            if tm: pooled[label].append({"season": season, "n_clubs": len(ids), "n_team_matches": len(tm), "gf_sum": sum(float(r[f"{side}_goals"]) for r, side in tm), "ga_sum": sum(float(r[f"{'away' if side == 'home' else 'home'}_goals"]) for r, side in tm), "league_sum": league_rate * len(tm)})
            return item
        out[season] = {"league_gf_per_match": round(league_rate, 6), "league_ga_per_match": round(league_rate, 6),
                       "down_from_championship": group(down, "down_from_championship"),
                       "up_other": group(up, "up_other")}
    pooled_out = {}
    for label, groups in pooled.items():
        tm = sum(g["n_team_matches"] for g in groups)
        gf = sum(g["gf_sum"] for g in groups) / tm if tm else None
        ga = sum(g["ga_sum"] for g in groups) / tm if tm else None
        league = sum(g["league_sum"] for g in groups) / tm if tm else None
        pooled_out[label] = {"n_club_seasons": sum(g["n_clubs"] for g in groups), "n_team_matches": tm,
                             "gf_per_match": round(gf, 6) if gf is not None else None, "ga_per_match": round(ga, 6) if ga is not None else None,
                             "gf_delta": round(gf-league, 6) if gf is not None else None, "ga_delta": round(ga-league, 6) if ga is not None else None,
                             "per_season": [{"season": g["season"], "n_clubs": g["n_clubs"], "n_team_matches": g["n_team_matches"], "gf_delta": round(g["gf_sum"]/g["n_team_matches"] - g["league_sum"]/g["n_team_matches"], 6), "ga_delta": round(g["ga_sum"]/g["n_team_matches"] - g["league_sum"]/g["n_team_matches"], 6)} for g in groups]}
    return {"by_season": out, "pooled": pooled_out,
            "classification_notes": {"down_from_championship": "played Championship (FotMob 123) in the previous season",
                                      "up_other": "promoted from below, tier unverified"},
            "membership_source": "warehouse index league_ids 123 and 124 plus payload general team ids"}


def main():
    per = {}
    for season in SEASONS:
        rs = [r for r in ROWS if r["season"] == season]
        goals = [float(r["home_goals"])+float(r["away_goals"]) for r in rs]
        yell = [float(r["ev_yellow_home"])+float(r["ev_yellow_away"]) for r in rs]
        yell_plus = [y + float(r["ev_yellowred_home"])+float(r["ev_yellowred_away"]) for r, y in zip(rs, yell)]
        per[season] = {"n": len(rs), "goals_per_match": round(st.mean(goals), 6), "home_goal_share": round(sum(float(r["home_goals"]) for r in rs)/sum(goals), 6),
                       "event_yellows_per_match": round(st.mean(yell), 6), "event_yellows_plus_yellowred_per_match": round(st.mean(yell_plus), 6),
                       "red_events_per_match": round(st.mean(float(r["ev_red_home"])+float(r["ev_red_away"]) for r in rs), 6),
                       "ht_goal_share": share(rs, "ht_goals", lambda r: float(r["home_goals"])+float(r["away_goals"])),
                       "ht_yellow_share": share(rs, "ht_yellows", lambda r: float(r["ev_yellow_home"])+float(r["ev_yellow_away"])),
                       "ou2.5_over_rate": round(sum(x > 2.5 for x in goals)/len(goals), 6),
                       "event_yellows_3.5_over_rate": round(sum(x > 3.5 for x in yell)/len(yell), 6),
                       "stats_markets": "absent", "referee_n": 0}
    def pooled_line(metric, line):
        vals = []
        for r in ROWS:
            if r["season"] in DEV:
                vals.append((float(r[f"home_goals"])+float(r[f"away_goals"])) if metric == "goals" else float(r["ev_yellow_home"])+float(r["ev_yellow_away"]))
        return {"n": len(vals), "over_rate": round(sum(v > line for v in vals)/len(vals), 6)}
    halves = {"complete_seasons": list(COMPLETE), "goals": share([r for r in ROWS if r["season"] in COMPLETE], "ht_goals", lambda r: float(r["home_goals"])+float(r["away_goals"])),
              "event_yellows": share([r for r in ROWS if r["season"] in COMPLETE], "ht_yellows", lambda r: float(r["ev_yellow_home"])+float(r["ev_yellow_away"]))}
    summary = {"n": len(ROWS), "seasons": list(SEASONS), "dev_seasons": list(DEV), "per_season": per,
               "stats_markets": {"SOT": "absent", "corners": "absent", "total_shots": "absent", "reason": "0/969 payloads have stats Periods content"},
               "primary_lines": {"goals_ou_2.5": pooled_line("goals", 2.5), "event_yellows_3.5": pooled_line("yellow", 3.5)},
               "reliability": {"goals": reliability("goals"), "event_yellows": reliability("ev_yellow")}, "halves": halves,
               "referee": {"n_referees": 0, "coverage": "0/969 usable referee texts"}, "movers": movers(), "phase": "regular"}
    (HERE / "eda_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (HERE / "movers.json").write_text(json.dumps(summary["movers"], indent=2) + "\n")
    print(json.dumps({"n": len(ROWS), "primary_lines": summary["primary_lines"], "halves": halves, "mover_pooled": summary["movers"]["pooled"]}, indent=2))


if __name__ == "__main__": main()
