"""EDA computation for MX-ExpansionMX. Prints inventory + EDA JSON to stdout.

Reads rows through data/build_data.py (warehouse = main repo). No fitting.
Altitude map: static team-city altitudes (metres), descriptive only.
"""
import json, math, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "data"))
import build_data as bd

ALT = {  # home-city altitude (m), by canonical team name (accents as in corpus)
    # Atlante: the corpus's one populated stadium row says Zacatepec
    # (Estadio Coruco Diaz, ~1160 m) - the club's Expansion-era home,
    # NOT Mexico City. Dorados: Culiacan (one Tijuana row is a
    # relocated match; mapping is the club's home city).
    "Atlante": 1160, "Tlaxcala FC": 2400,
    "Mineros de Zacatecas": 2440, "Tepatitlán FC": 1820,
    "Atlético Morelia": 1920, "Alebrijes Oaxaca": 1550,
    "Alacranes de Durango": 1890, "Dorados": 60, "Cimarrones de Sonora": 210,
    "Venados FC": 10, "Celaya": 1760, "Correcaminos de la UAT": 320,
    "Leones Negros": 1560, "Tapatío": 1560, "Raya2 Expansion": 500,
    "Pumas Tabasco": 10, "Cancún FC": 10, "Atlético La Paz": 30,
    "Jaiba Brava del Tampico-Madero": 10,
    "Irapuato": 1720,
}
CARDS_ERA_START = "2022/2023 - Clausura"


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def split_half(pairs):
    """pairs: list of (team, half, value). Pearson r between half sums/means."""
    by = defaultdict(dict)
    for t, h, v in pairs:
        by[t][h] = v
    xs, ys = [], []
    for t, d in by.items():
        if 0 in d and 1 in d:
            xs.append(d[0]); ys.append(d[1])
    if len(xs) < 3:
        return {"n_teams": len(xs), "r": None}
    mx, my = mean(xs), mean(ys)
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs); vy = sum((y - my) ** 2 for y in ys)
    return {"n_teams": len(xs), "r": round(cov / math.sqrt(vx * vy), 3) if vx and vy else None}


def main():
    rows = bd.load_rows()
    reg = [r for r in rows if r["phase"] == "regular" and r["finished"] == 1]
    blocks = bd.BLOCKS[:10]
    inv, eda = {}, {}
    for b in blocks + ["2026/2027 - Apertura"]:
        rs = [r for r in reg if r["block"] == b]
        inv[b] = {
            "n": len(rs),
            "teams": len({r["home_team_id"] for r in rs} | {r["away_team_id"] for r in rs}),
            "stats_all_pct": round(100 * mean([r["has_stats_all"] for r in rs]), 1) if rs else None,
            "stats_half_pct": round(100 * mean([r["has_stats_half"] for r in rs]), 1) if rs else None,
            "shotmap_pct": round(100 * mean([r["has_shotmap"] for r in rs]), 1) if rs else None,
            "events_pct": round(100 * mean([r["has_events"] for r in rs]), 1) if rs else None,
            "lineup_pct": round(100 * mean([r["has_lineup"] for r in rs]), 1) if rs else None,
            "referee_pct": round(100 * mean([1.0 if r["referee"] else 0.0 for r in rs]), 1) if rs else None,
            "goals_events_complete": sum(r["goals_events_complete"] for r in rs),
            "coverage": Counter(r["coverage_level"] for r in rs).most_common(1)[0][0] if rs else None,
        }
    mod = [r for r in reg if r["block"] in blocks]
    levels = {}
    for b in blocks:
        rs = [r for r in mod if r["block"] == b]
        lv = {"n": len(rs),
              "goals_per_match": round(mean([r["home_goals"] + r["away_goals"] for r in rs]), 3),
              "home_goals": round(mean([r["home_goals"] for r in rs]), 3),
              "away_goals": round(mean([r["away_goals"] for r in rs]), 3),
              "home_win_rate": round(mean([1.0 if r["home_goals"] > r["away_goals"] else 0.0 for r in rs]), 3),
              "draw_rate": round(mean([1.0 if r["home_goals"] == r["away_goals"] else 0.0 for r in rs]), 3),
              "over25_rate": round(mean([1.0 if r["home_goals"] + r["away_goals"] > 2.5 else 0.0 for r in rs]), 3)}
        if b >= CARDS_ERA_START:
            lv["yellows_per_match"] = round(mean([r["yellow_home"] + r["yellow_away"] for r in rs]), 3)
            lv["matches_with_yellow_pct"] = round(100 * mean([1.0 if r["yellow_home"] + r["yellow_away"] > 0 else 0.0 for r in rs]), 1)
            lv["zero_yellow_matches"] = sum(1 for r in rs if r["yellow_home"] + r["yellow_away"] == 0)
        levels[b] = lv
    eda["levels_by_block"] = levels
    eda["pooled_goals_per_match"] = round(mean([r["home_goals"] + r["away_goals"] for r in mod]), 3)
    eda["pooled_home_advantage"] = round(mean([r["home_goals"] - r["away_goals"] for r in mod]), 3)
    # halves constants: goals from event times (complete rows only), yellows cards-era
    comp = [r for r in mod if r["goals_events_complete"] == 1]
    tot_g = sum(r["home_goals"] + r["away_goals"] for r in comp)
    ht_g = sum(r["ht_home_goals"] + r["ht_away_goals"] for r in comp)
    eda["halves"] = {"goals_1h_share": round(ht_g / tot_g, 4), "goals_n": len(comp),
                     "incomplete_rows_excluded": len(mod) - len(comp),
                     "incomplete_match_ids": [r["match_id"] for r in mod if r["goals_events_complete"] == 0]}
    ce = [r for r in mod if r["block"] >= CARDS_ERA_START]
    tot_y = sum(r["yellow_home"] + r["yellow_away"] for r in ce)
    ht_y = sum(r["yellow_1h_home"] + r["yellow_1h_away"] for r in ce)
    eda["halves"]["yellow_1h_share_cards_era_incl_partial"] = round(ht_y / tot_y, 4)
    clean = [r for r in mod if r["block"] >= "2023/2024 - Apertura"]
    tot_yc = sum(r["yellow_home"] + r["yellow_away"] for r in clean)
    ht_yc = sum(r["yellow_1h_home"] + r["yellow_1h_away"] for r in clean)
    eda["halves"]["yellow_1h_share"] = round(ht_yc / tot_yc, 4)
    eda["halves"]["yellows_n"] = len(clean)
    # per-match 1H share variance vs binomial noise floor (goals)
    import statistics
    shares = [(r["ht_home_goals"] + r["ht_away_goals"]) / (r["home_goals"] + r["away_goals"])
              for r in comp if r["home_goals"] + r["away_goals"] > 0]
    p = ht_g / tot_g
    noise = mean([p * (1 - p) / (r["home_goals"] + r["away_goals"]) for r in comp if r["home_goals"] + r["away_goals"] > 0])
    eda["halves"]["goals_share_var_observed"] = round(statistics.pvariance(shares), 5)
    eda["halves"]["goals_share_var_noise_floor"] = round(noise, 5)
    eda["halves"]["goals_share_true_var"] = round(max(0.0, statistics.pvariance(shares) - noise), 5)
    # reliabilities: split-half by team across the modelling corpus (odd/even matches)
    def trait(key_for, key_against, pool):
        pf, pa = [], []
        cnt = Counter()
        aggf, agga = defaultdict(float), defaultdict(float)
        for r in pool:
            for tid, f, a in ((r["home_team_id"], key_for(r, "home"), key_against(r, "home")),
                              (r["away_team_id"], key_for(r, "away"), key_against(r, "away"))):
                h = cnt[tid] % 2
                cnt[tid] += 1
                aggf[(tid, h)] += f; agga[(tid, h)] += a
        teams = {t for t, _ in aggf}
        pf = [(t, h, aggf[(t, h)]) for t in teams for h in (0, 1) if (t, h) in aggf]
        pa = [(t, h, agga[(t, h)]) for t in teams for h in (0, 1) if (t, h) in agga]
        return {"for": split_half(pf), "against": split_half(pa)}
    eda["reliability_goals"] = trait(lambda r, s: r[f"{s}_goals"], lambda r, s: r["away_goals" if s == "home" else "home_goals"], mod)
    eda["reliability_yellows_cards_era"] = trait(lambda r, s: r[f"yellow_{s}"], lambda r, s: r["yellow_away" if s == "home" else "yellow_home"], ce)
    # cards capture check: 2022/2023 Clausura vs 2023/2024 blocks
    cap = {}
    for b in ["2022/2023 - Clausura", "2023/2024 - Apertura", "2023/2024 - Clausura"]:
        rs = [r for r in mod if r["block"] == b]
        dist = Counter(r["yellow_home"] + r["yellow_away"] for r in rs)
        cap[b] = {"n": len(rs), "yellows_per_match": round(mean([r["yellow_home"] + r["yellow_away"] for r in rs]), 3),
                  "zero_yellow": dist[0], "one_or_two": sum(v for k, v in dist.items() if k in (1, 2)),
                  "max": max(dist)}
    eda["cards_capture_check"] = cap
    # entrants per block + Liga MX overlap
    seen, entrants = set(), {}
    for b in blocks:
        rs = [r for r in mod if r["block"] == b]
        teams = {r["home_team_id"] for r in rs} | {r["away_team_id"] for r in rs}
        entrants[b] = len(teams - seen)
        seen |= teams
    eda["entrants_per_block"] = entrants
    mx_csv = Path.home() / "workspace" / "footballprediction" / "league" / "MX-LigaMX" / "data" / "mx_matches.csv"
    overlap = {}
    if mx_csv.exists():
        import csv as _csv
        mx_by_season = defaultdict(set)
        for r in _csv.DictReader(mx_csv.open()):
            mx_by_season[r["season"]].add(int(r["home_team_id"])); mx_by_season[r["season"]].add(int(r["away_team_id"]))
        for b in blocks:
            rs = [r for r in mod if r["block"] == b]
            teams = {r["home_team_id"] for r in rs} | {r["away_team_id"] for r in rs}
            prev = mx_by_season.get(b, set())
            overlap[b] = len(teams & prev)
    eda["liga_mx_same_block_team_overlap"] = overlap
    # altitude (descriptive)
    def alt_of(team):
        return ALT.get(team)
    hi, rest, hi_low, rest_low = [], [], [], []
    unknown = 0
    team_alt = {}
    for r in mod:
        a_h = alt_of(r["home_team"]); a_a = alt_of(r["away_team"])
        if a_h is None or a_a is None:
            unknown += 1
            continue
        team_alt[r["home_team"]] = a_h
        rec = (r["home_goals"] - r["away_goals"], 1.0 if r["home_goals"] > r["away_goals"] else 0.0)
        (hi if a_h >= 2000 else rest).append(rec)
        if a_a < 1000:
            (hi_low if a_h >= 2000 else rest_low).append(rec)
    def agg_alt(rs):
        return {"n": len(rs), "home_edge": round(mean([x[0] for x in rs]), 3) if rs else None,
                "home_win_rate": round(mean([x[1] for x in rs]), 3) if rs else None}
    eda["altitude"] = {"mapping": team_alt, "unknown_matches": unknown,
                       "high_ge2000": agg_alt(hi), "rest": agg_alt(rest),
                       "away_lt1000_high_home": agg_alt(hi_low), "away_lt1000_rest_home": agg_alt(rest_low),
                       "verdict": "DESCRIPTIVE / NOT ADOPTED: static home altitude is collinear with stable team identity (MX-LigaMX + PE precedent)."}
    # 2026/2027 stats-era levels (context only; excluded from modelling)
    era = [r for r in reg if r["block"] == "2026/2027 - Apertura"]
    if era:
        eda["stats_era_2026_2027"] = {
            "n": len(era),
            "sot_per_match": round(mean([(r["ShotsOnTarget_home"] or 0) + (r["ShotsOnTarget_away"] or 0) for r in era]), 3),
            "corners_per_match": round(mean([(r["corners_home"] or 0) + (r["corners_away"] or 0) for r in era]), 3),
            "total_shots_per_match": round(mean([(r["total_shots_home"] or 0) + (r["total_shots_away"] or 0) for r in era]), 3)}
    print(json.dumps({"inventory": inv, "eda": eda}, indent=1))


if __name__ == "__main__":
    main()
