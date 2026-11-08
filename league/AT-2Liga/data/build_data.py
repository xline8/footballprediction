"""Build Austria 2. Liga Phase-2 tables from the FotMob world warehouse.

Extraction only: no fitting, no imputation, no feature windows.
Source: data_enrichment/fotmob_world_index.csv filtered to league_id=119;
per-match JSONs at the index `path` column (warehouse lives in the main
checkout; this worktree falls back to it).

Feed facts this builder encodes (measured, Phase 1):
- The stats feed carries ONLY BallPossesion, ShotsOnTarget, corners and
  total_shots (Periods.All only -- no FirstHalf/SecondHalf block exists
  in any payload). There is no xG, no shotmap, no yellow_cards key.
- Cards therefore come from the match events feed (event-unified
  yellows: Yellow + YellowRed per team), with cards_source recorded
  per row. Matches without an events feed keep NaN -- never zero.
- HT goals and the yellows 1H share come from event times (time <= 45),
  the only halves source in this league.
"""
import csv
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
WAREHOUSE_REPO = REPO if (REPO / "data_enrichment" / "fotmob_world" / "Austria").exists() \
    else Path.home() / "workspace" / "footballprediction"
sys.path.insert(0, str(REPO / "league"))
from jleague_lib import events_of, flat_stats, goal_events, ht_from_events, load  # noqa: E402

INDEX = WAREHOUSE_REPO / "data_enrichment" / "fotmob_world_index.csv"
LEAGUE_ID = "119"

STAT_KEYS = ("BallPossesion", "total_shots", "ShotsOnTarget", "ShotsOffTarget",
             "blocked_shots", "corners", "yellow_cards", "red_cards",
             "expected_goals", "expected_goals_set_play", "big_chance",
             "touches_opp_box", "fouls")


def count_card(es, card, home):
    return sum(1 for e in es if e.get("type") == "Card" and e.get("card") == card
               and bool(e.get("isHome")) == home)


def parse_match(idx_row):
    path = WAREHOUSE_REPO / idx_row["path"]
    d = load(path)
    gen, hdr, content = d.get("general") or {}, d.get("header") or {}, d.get("content") or {}
    status = hdr.get("status") or {}
    home, away = gen.get("homeTeam") or {}, gen.get("awayTeam") or {}
    score = status.get("scoreStr") or idx_row.get("score") or ""
    hg = ag = None
    if " - " in score:
        try:
            hg, ag = (int(x) for x in score.split(" - "))
        except ValueError:
            pass
    fs = flat_stats(content)
    es = events_of(content)

    def st(period, key, side):
        v = fs.get((period, key))
        return None if v is None else v[side]

    season = idx_row["season"]
    ref = (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or ""
    row = {
        "match_id": int(gen.get("matchId") or path.stem),
        "league": "AT-2Liga", "season": season,
        "season_start": int(season[:4]),
        "date": (gen.get("matchTimeUTCDate") or idx_row["date"] or "")[:10],
        "kickoff_utc": gen.get("matchTimeUTCDate"),
        "round": gen.get("matchRound"), "phase": "regular",
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "referee": ref if ref.strip() else None,
        "has_events": bool(es),
    }
    ge = goal_events(content)
    row["ev_goals_home"] = sum(1 for e in ge if e.get("isHome"))
    row["ev_goals_away"] = sum(1 for e in ge if e.get("isHome") is False)
    row["score_events_mismatch"] = bool(
        es and hg is not None and (row["ev_goals_home"], row["ev_goals_away"]) != (hg, ag))
    ht = ht_from_events(content)
    row["ht_home_goals"], row["ht_away_goals"] = ht if ht else (None, None)
    row["ht_source"] = "events" if ht else "none"
    # Cards: events are the only source (stats feed has no cards key).
    for side, p in ((True, "home"), (False, "away")):
        direct = count_card(es, "Yellow", side)
        second = count_card(es, "YellowRed", side)
        row[f"ev_yellow_direct_{p}"] = direct if es else None
        row[f"ev_yellowred_{p}"] = second if es else None
        row[f"ev_yellow_{p}"] = (direct + second) if es else None
        row[f"ev_red_{p}"] = (count_card(es, "Red", side) + second) if es else None
        row[f"ev_yellow_1h_{p}"] = (sum(1 for e in es if e.get("type") == "Card"
                                       and e.get("card") in ("Yellow", "YellowRed")
                                       and bool(e.get("isHome")) == side
                                       and e.get("time") is not None and e["time"] <= 45)
                                   if es else None)
    stats_yellow = st("All", "yellow_cards", 0)
    if stats_yellow is not None:
        row["yellow_home"], row["yellow_away"] = st("All", "yellow_cards", 0), st("All", "yellow_cards", 1)
        row["cards_source"] = "stats"
    elif es:
        row["yellow_home"], row["yellow_away"] = float(row["ev_yellow_home"]), float(row["ev_yellow_away"])
        row["cards_source"] = "events"
    else:
        row["yellow_home"], row["yellow_away"] = None, None
        row["cards_source"] = "none"
    row["red_home"] = st("All", "red_cards", 0) if st("All", "red_cards", 0) is not None else row["ev_red_home"]
    row["red_away"] = st("All", "red_cards", 1) if st("All", "red_cards", 1) is not None else row["ev_red_away"]
    for k in STAT_KEYS:
        row[f"{k}_home"] = st("All", k, 0)
        row[f"{k}_away"] = st("All", k, 1)
        row[f"fh_{k}_home"] = st("FirstHalf", k, 0)
        row[f"fh_{k}_away"] = st("FirstHalf", k, 1)
        row[f"sh_{k}_home"] = st("SecondHalf", k, 0)
        row[f"sh_{k}_away"] = st("SecondHalf", k, 1)
    row["has_stats_all"] = ("All", "total_shots") in fs or ("All", "corners") in fs
    row["has_stats_half"] = ("FirstHalf", "corners") in fs
    row["has_shotmap"] = bool(((content.get("shotmap") or {}).get("shots") or []))
    return row


def main():
    idx = [r for r in csv.DictReader(INDEX.open()) if r["league_id"] == LEAGUE_ID]
    rows = [parse_match(r) for r in idx]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == len(idx) == 1266, (len(rows), len(idx))
    assert len({r["match_id"] for r in rows}) == len(rows)
    with (HERE / "at2_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    team = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                 "phase": r["phase"], "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"],
                 "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"]}
            for k in ("total_shots", "ShotsOnTarget", "corners", "BallPossesion"):
                x[f"{k}_for"], x[f"{k}_against"] = r.get(f"{k}_{side}"), r.get(f"{k}_{other}")
            x["yellow_for"] = r[f"yellow_{side}"]
            x["yellow_against"] = r[f"yellow_{other}"]
            x["yellow_events_for"], x["yellow_events_against"] = r[f"ev_yellow_{side}"], r[f"ev_yellow_{other}"]
            team.append(x)
    with (HERE / "at2_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team[0]))
        w.writeheader(); w.writerows(team)
    print(f"matches={len(rows)} team_rows={len(team)}")


if __name__ == "__main__":
    main()
