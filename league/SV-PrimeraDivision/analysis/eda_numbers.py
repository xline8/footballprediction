"""Compute reproducible scores-only EDA from the built SV CSVs."""
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "data"
MATCHES = DATA / "sv_matches.csv"
TEAM_MATCHES = DATA / "sv_team_matches.csv"
PARTIAL = "2026/2027 - Apertura"


def mean(values):
    return sum(values) / len(values) if values else None


def pearson(pairs):
    if len(pairs) < 2:
        return None
    xs, ys = zip(*pairs)
    mx, my = mean(xs), mean(ys)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    denx = sum((x - mx) ** 2 for x in xs)
    deny = sum((y - my) ** 2 for y in ys)
    return num / math.sqrt(denx * deny) if denx and deny else None


def levels(rows):
    n = len(rows)
    hg = [int(r["home_goals"]) for r in rows]
    ag = [int(r["away_goals"]) for r in rows]
    total = [h + a for h, a in zip(hg, ag)]
    return {
        "n": n,
        "mean_goals_per_match": mean(total),
        "home_goals_per_match": mean(hg),
        "away_goals_per_match": mean(ag),
        "home_win_rate": sum(h > a for h, a in zip(hg, ag)) / n,
        "draw_rate": sum(h == a for h, a in zip(hg, ag)) / n,
        "away_win_rate": sum(h < a for h, a in zip(hg, ag)) / n,
        "over_2_5_rate": sum(x > 2 for x in total) / n,
        "btts_rate": sum(h > 0 and a > 0 for h, a in zip(hg, ag)) / n,
        "zero_zero_rate": sum(x == 0 for x in total) / n,
        "mean_ht_goals_where_available": mean([
            int(r["ht_home_goals"]) + int(r["ht_away_goals"])
            for r in rows if r["ht_source"] == "half_event"
        ]),
    }


def split_pairs(team_rows, value_fn):
    by_team = defaultdict(list)
    for r in team_rows:
        by_team[int(r["team_id"])].append(r)
    pairs = []
    for values in by_team.values():
        values.sort(key=lambda r: (r["date"], r["match_id"]))
        if len(values) < 10:
            continue
        cut = len(values) // 2
        if cut < 5 or len(values) - cut < 5:
            continue
        first, second = values[:cut], values[cut:]
        pairs.append((mean([value_fn(r) for r in first]), mean([value_fn(r) for r in second])))
    return pairs


def trait_record(team_rows):
    attack = split_pairs(team_rows, lambda r: int(r["goals_for"]))
    defence = split_pairs(team_rows, lambda r: int(r["goals_against"]))
    return {"n_teams": len(attack), "r_attack": pearson(attack), "r_defence": pearson(defence)}


def half_share_pairs(team_rows):
    by_team = defaultdict(list)
    for r in team_rows:
        by_team[int(r["team_id"])].append(r)
    pairs = []
    for values in by_team.values():
        values.sort(key=lambda r: (r["date"], r["match_id"]))
        if len(values) < 10:
            continue
        cut = len(values) // 2
        if cut < 5 or len(values) - cut < 5:
            continue
        halves = values[:cut], values[cut:]
        out = []
        for half in halves:
            ft = sum(int(r["goals_for"]) for r in half)
            ht = sum(int(r["ht_goals_for"]) for r in half)
            out.append(ht / ft if ft else None)
        if None not in out:
            pairs.append(tuple(out))
    return pairs


def half_stats(rows, pooled_share=None):
    trusted = [r for r in rows if r["ht_source"] == "half_event" and int(r["ht_suspect"]) == 0]
    ft_goals = sum(int(r["home_goals"]) + int(r["away_goals"]) for r in trusted)
    ht_goals = sum(int(r["ht_home_goals"]) + int(r["ht_away_goals"]) for r in trusted)
    share = ht_goals / ft_goals if ft_goals else None
    valid = [r for r in trusted if int(r["home_goals"]) + int(r["away_goals"]) > 0]
    if pooled_share is None:
        pooled_share = share
    observed = [
        (int(r["ht_home_goals"]) + int(r["ht_away_goals"]))
        / (int(r["home_goals"]) + int(r["away_goals"])) for r in valid
    ]
    floor = mean([
        pooled_share * (1 - pooled_share)
        / (int(r["home_goals"]) + int(r["away_goals"])) for r in valid
    ]) if valid and pooled_share is not None else None
    variance = mean([(x - mean(observed)) ** 2 for x in observed]) if observed else None
    return {
        "n_regular": len(rows), "n_ht_readable": len(trusted),
        "ht_coverage": len(trusted) / len(rows) if rows else None,
        "share": share, "sum_ht_goals": ht_goals, "sum_ft_goals": ft_goals,
        "observed_variance": variance, "binomial_noise_floor": floor,
        "excess_variance": variance - floor if variance is not None and floor is not None else None,
    }


def main():
    with MATCHES.open(newline="", encoding="utf-8") as fh:
        matches = list(csv.DictReader(fh))
    with TEAM_MATCHES.open(newline="", encoding="utf-8") as fh:
        team_matches = list(csv.DictReader(fh))
    assert len(matches) == 1448 and len(team_matches) == 2896
    match_by_id = {r["match_id"]: r for r in matches}
    for r in team_matches:
        m = match_by_id[r["match_id"]]
        r["ht_source"] = m["ht_source"]
        r["ht_suspect"] = m["ht_suspect"]
        if m["ht_source"] == "half_event" and int(m["ht_suspect"]) == 0:
            r["ht_goals_for"] = m["ht_home_goals"] if r["venue"] == "home" else m["ht_away_goals"]
        else:
            r["ht_goals_for"] = None
    regular = [r for r in matches if r["stage"] == "regular"]
    tournaments = []
    for r in matches:
        if r["season"] not in tournaments:
            tournaments.append(r["season"])
    regular_by = {s: [r for r in regular if r["season"] == s] for s in tournaments}
    team_regular_by = {
        s: [r for r in team_matches if r["season"] == s and r["stage"] == "regular"]
        for s in tournaments
    }

    by_tournament = {s: levels(regular_by[s]) for s in tournaments}
    completed = [r for r in regular if r["season"] != PARTIAL]
    by_tournament["pooled_regular"] = levels(completed)
    by_tournament["pooled_regular_incl_partial"] = levels(regular)
    by_tournament["playoffs"] = levels([r for r in matches if r["stage"] == "playoff"])

    trait_by = {s: trait_record(team_regular_by[s]) for s in tournaments}
    all_pairs_attack, all_pairs_defence = [], []
    for s in tournaments:
        rows = team_regular_by[s]
        all_pairs_attack += split_pairs(rows, lambda r: int(r["goals_for"]))
        all_pairs_defence += split_pairs(rows, lambda r: int(r["goals_against"]))
    season_year_rows = defaultdict(list)
    for r in team_matches:
        if r["stage"] == "regular":
            season_year_rows[r["season"].split("/", 1)[0]].append(r)
    season_year_attack, season_year_defence = [], []
    for rows in season_year_rows.values():
        season_year_attack += split_pairs(rows, lambda r: int(r["goals_for"]))
        season_year_defence += split_pairs(rows, lambda r: int(r["goals_against"]))
    trait_reliability = {
        "by_tournament": trait_by,
        "pooled": {"n_teams": len(all_pairs_attack), "r_attack": pearson(all_pairs_attack), "r_defence": pearson(all_pairs_defence)},
        "pooled_season_year": {"n_teams": len(season_year_attack), "r_attack": pearson(season_year_attack), "r_defence": pearson(season_year_defence)},
        "method": "Each team's regular-season matches sorted chronologically and split into two halves; teams require >=10 matches and >=5 per half.",
    }

    completed_share_rows = [r for r in completed if r["ht_source"] == "half_event" and int(r["ht_suspect"]) == 0]
    pooled_share = half_stats(completed, None)["share"]
    half_by = {s: half_stats(regular_by[s], pooled_share) for s in tournaments}
    half_pooled = half_stats(completed, pooled_share)
    half_all = half_stats(regular, pooled_share)
    half_pairs = []
    for s in tournaments:
        # ht_goals_for was joined from sv_matches.csv in the loop above;
        # keep only team rows whose match had a trusted HT marker.
        rows = [r for r in team_regular_by[s]
                if r["ht_source"] == "half_event" and r["ht_goals_for"] is not None]
        half_pairs += half_share_pairs(rows)
    halves = {
        "by_tournament": half_by,
        "pooled_completed": half_pooled,
        "pooled_incl_partial": half_all,
        "frozen_goals_1h_share": pooled_share,
        "team_tournament_split_half": {"n_pairs": len(half_pairs), "r": pearson(half_pairs)},
        "variance_formula": "Observed population variance of match HT-goals/FT-goals for FT-goals>0; noise floor is mean[p*(1-p)/FT-goals] with p equal to the pooled completed-tournament share.",
        "partial_label": PARTIAL,
    }

    turnover = {}
    previous = None
    for s in tournaments:
        ids = {int(r["team_id"]) for r in team_regular_by[s]}
        if previous is not None:
            turnover[s] = {
                "new_team_ids": sorted(ids - previous), "n_new": len(ids - previous),
                "left_team_ids": sorted(previous - ids), "n_left": len(previous - ids),
            }
        previous = ids

    inventory = {}
    for s in tournaments:
        rows = [r for r in matches if r["season"] == s]
        inventory[s] = {
            "n": len(rows), "stats_nonempty": sum(int(r["has_stats_all"]) for r in rows),
            "shotmap_nonempty": sum(int(r["has_shotmap"]) for r in rows),
            "events_nonempty": sum(int(r["has_events"]) for r in rows),
            "ht_readable": sum(r["ht_source"] == "half_event" for r in rows),
            "lineup_starters": sum(int(r["has_lineup"]) for r in rows),
            "playerstats_nonempty": sum(int(r["has_playerstats"]) for r in rows),
            "referee_nonempty": sum(bool(r["referee"]) for r in rows),
            "plain_yellow_events": sum(int(r["n_card_events"]) - int(r["n_red_events"]) for r in rows),
            "dismissal_events": sum(int(r["n_red_events"]) for r in rows),
            "event_ft_mismatch": sum(int(r["event_ft_mismatch"]) for r in rows),
            "lineup_blocks": sum(int(r["lineup_block"]) for r in rows),
        }
    assert sum(x["n"] for x in inventory.values()) == 1448
    assert sum(x["events_nonempty"] for x in inventory.values()) == 1334
    assert sum(x["ht_readable"] for x in inventory.values()) == 1334
    assert sum(x["dismissal_events"] for x in inventory.values()) == 593
    assert sum(x["event_ft_mismatch"] for x in inventory.values()) == 1

    (HERE / "eda_numbers.json").write_text(json.dumps({
        "by_tournament": by_tournament, "trait_reliability": trait_reliability,
        "halves": halves, "turnover": turnover,
    }, indent=2, sort_keys=False) + "\n", encoding="utf-8")
    (HERE / "inventory_summary.json").write_text(json.dumps({"by_tournament": inventory}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "regular_counts": {s: len(regular_by[s]) for s in tournaments},
        "pooled_regular_completed": len(completed),
        "pooled_trait_r": trait_reliability["pooled"],
        "frozen_goals_1h_share": pooled_share,
        "excess_variance": half_pooled["excess_variance"],
        "turnover_counts": {s: x["n_new"] for s, x in turnover.items()},
    }, indent=2))


if __name__ == "__main__":
    main()
