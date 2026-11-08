"""Build Mexico Liga de Expansión MX tables from the FotMob warehouse.

Extraction only: no fitting, imputation, or feature windows.

League-specific rules (see analysis/PREPROCESSING.md):
- Phase: `regular` when general.matchRound is a digit string (1..17);
  every other label ("1/8", "1/4", "1/2", "final",
  "Apertura - Quarter-finals", ...) is a liguilla play-off row and is
  excluded from every fit and score downstream.
- Tournament blocks: the warehouse season is the football year and
  contains both tournaments. Apertura = match date 15 Jun - 31 Dec of
  the first calendar year; Clausura = 1 Jan - 14 Jun of the second
  (Apertura 2022 began 25 Jun 2022; a month>=7 rule would misassign
  its first round to the previous Clausura).
- Played: all 1,508 index rows are finished (header.status.finished).
- Stats: content.stats is None in every payload before 2026/2027 and
  carries real values only in the in-progress 2026/2027 season
  (128 rows). has_stats_all is computed from parsed VALUES, never
  from the index flag.
- Cards target: unified yellows = event card='Yellow' plus
  card='YellowRed' (a second yellow is a yellow shown), per side.
  Plain 'Yellow' events are absent before 2022/2023 Clausura (the
  feed recorded only Red/YellowRed) - see DATA_UNDERSTANDING.md.
"""
import argparse, csv, json
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
LEAGUE_ID = "8976"
STAT_KEYS = ("BallPossesion", "expected_goals", "expected_goals_open_play",
             "expected_goals_set_play", "total_shots", "ShotsOnTarget",
             "ShotsOffTarget", "blocked_shots", "big_chance",
             "touches_opp_box", "corners", "yellow_cards", "red_cards",
             "fouls")

BLOCKS = ["2021/2022 - Apertura", "2021/2022 - Clausura",
          "2022/2023 - Apertura", "2022/2023 - Clausura",
          "2023/2024 - Apertura", "2023/2024 - Clausura",
          "2024/2025 - Apertura", "2024/2025 - Clausura",
          "2025/2026 - Apertura", "2025/2026 - Clausura",
          "2026/2027 - Apertura"]


def block_of(season, date_s):
    y, m, d = int(date_s[:4]), int(date_s[5:7]), int(date_s[8:10])
    if season == "2026/2027":
        return "2026/2027 - Apertura"
    first_year = int(season[:4])
    if y == first_year and (m > 6 or (m == 6 and d >= 15)):
        return f"{season} - Apertura"
    if y == first_year + 1 and (m < 6 or (m == 6 and d < 15)):
        return f"{season} - Clausura"
    raise ValueError(f"date {date_s} outside tournament windows for {season}")


def number(v):
    if v in (None, ""):
        return None
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).split()[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or []
                if len(vals) >= 2:
                    h, a = number(vals[0]), number(vals[1])
                    if h is not None or a is not None:
                        out[(period, stat.get("key"))] = (h, a)
    return out


def events(content):
    return (((content or {}).get("matchFacts") or {}).get("events") or {}).get("events") or []


def count_card(es, card, home):
    return sum(1 for e in es if e.get("type") == "Card" and e.get("card") == card
               and bool(e.get("isHome")) == home)


def score(s):
    p = (s or "0 - 0").split("-")
    return int(p[0].strip()), int(p[1].strip())


def build(index_row, warehouse_root):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    general, header = payload.get("general") or {}, payload.get("header") or {}
    status, content = header.get("status") or {}, payload.get("content") or {}
    stats, es = flat_stats(content), events(content)
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    teams = header.get("teams") or []
    ht, at = teams[0] if len(teams) > 0 else {}, teams[1] if len(teams) > 1 else {}
    rnd = str(general.get("matchRound") or "")
    phase = "regular" if rnd.isdigit() else "playoff"
    block = block_of(index_row["season"], index_row["date"])
    row = {"match_id": index_row["match_id"], "league": "MX-ExpansionMX",
           "season": index_row["season"], "block": block,
           "block_idx": BLOCKS.index(block),
           "date": index_row["date"], "round": rnd, "phase": phase,
           "finished": int(bool(status.get("finished"))),
           "kickoff_utc": general.get("matchTimeUTC") or "",
           "coverage_level": general.get("coverageLevel") or "",
           "home_team_id": ht.get("id"), "home_team": ht.get("name"),
           "away_team_id": at.get("id"), "away_team": at.get("name"),
           "home_goals": hg, "away_goals": ag}
    goals = [e for e in es if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["ht_home_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome"))
    row["ht_away_goals"] = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and not e.get("isHome"))
    row["n_goal_events"] = len(goals)
    row["goals_events_complete"] = int(len(goals) == hg + ag)
    row["ht_source"] = "events" if es else "none"
    for side in (True, False):
        p = "home" if side else "away"
        direct = count_card(es, "Yellow", side)
        second = count_card(es, "YellowRed", side)
        row[f"ev_yellow_direct_{p}"] = direct
        row[f"ev_yellowred_{p}"] = second
        row[f"yellow_{p}"] = direct + second
        row[f"yellow_1h_{p}"] = sum(1 for e in es if e.get("type") == "Card"
                                    and e.get("card") in ("Yellow", "YellowRed")
                                    and bool(e.get("isHome")) == side
                                    and e.get("time") is not None and e["time"] <= 45)
        row[f"red_{p}"] = count_card(es, "Red", side) + second
    row["cards_source"] = "events" if es else "none"
    facts = content.get("matchFacts") or {}
    info = facts.get("infoBox") or {}
    row["referee"] = ((info.get("Referee") or {}).get("text") or "")
    stadium = info.get("Stadium") or {}
    row["stadium"] = stadium.get("name") or ""
    row["stadium_city"] = stadium.get("city") or ""
    for key in STAT_KEYS:
        for period, prefix in (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_")):
            h, a = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"], row[f"{prefix}{key}_away"] = h, a
    row["has_stats_all"] = int(("All", "corners") in stats)
    row["has_stats_half"] = int(("FirstHalf", "corners") in stats and ("SecondHalf", "corners") in stats)
    row["has_events"] = int(bool(es))
    row["has_lineup"] = int(bool(content.get("lineup")))
    shots = ((content.get("shotmap") or {}).get("shots") or [])
    regular = [s for s in shots if s.get("period") != "PenaltyShootout"]
    row["has_shotmap"] = int(bool(regular))
    row["n_shootout_shots"] = len(shots) - len(regular)
    for side, tid in (("home", ht.get("id")), ("away", at.get("id"))):
        ss = [s for s in regular if s.get("teamId") == tid]
        row[f"sm_shots_{side}"] = len(ss) if regular else None
        row[f"sm_sot_{side}"] = sum(1 for s in ss if s.get("isOnTarget") and not s.get("isBlocked")) if regular else None
        row[f"sm_xg_{side}"] = round(sum(s.get("expectedGoals") or 0 for s in ss), 4) if regular else None
    return row


def load_rows(warehouse_root=None):
    root = Path(warehouse_root) if warehouse_root else MAIN_REPO
    idx = root / "data_enrichment" / "fotmob_world_index.csv"
    rows = [build(r, root) for r in csv.DictReader(idx.open()) if r["league_id"] == LEAGUE_ID]
    rows.sort(key=lambda r: (r["date"], int(r["match_id"])))
    assert len(rows) == 1508, len(rows)
    canon = {}
    for r in rows:
        canon[r["home_team_id"]] = r["home_team"]
        canon[r["away_team_id"]] = r["away_team"]
    for r in rows:
        r["home_team_raw"], r["away_team_raw"] = r["home_team"], r["away_team"]
        r["home_team"], r["away_team"] = canon[r["home_team_id"]], canon[r["away_team_id"]]
    return rows


def main():
    rows = load_rows()
    from collections import Counter
    per = Counter((r["block"], r["phase"]) for r in rows)
    print(json.dumps({"matches": len(rows),
                      "per_block_phase": {f"{b}|{p}": n for (b, p), n in sorted(per.items())}}, indent=1), flush=True)
    HERE.mkdir(parents=True, exist_ok=True)
    with (HERE / "mxe_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    team = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            x = {"match_id": r["match_id"], "season": r["season"], "block": r["block"],
                 "date": r["date"], "phase": r["phase"], "finished": r["finished"],
                 "team_id": r[f"{side}_team_id"], "team": r[f"{side}_team"], "venue": side,
                 "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
                 "yellow_for": r[f"yellow_{side}"], "yellow_against": r[f"yellow_{other}"]}
            for k in ("expected_goals", "total_shots", "ShotsOnTarget", "corners"):
                x[f"{k}_for"], x[f"{k}_against"] = r.get(f"{k}_{side}"), r.get(f"{k}_{other}")
            team.append(x)
    with (HERE / "mxe_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team[0]))
        w.writeheader()
        w.writerows(team)
    print(json.dumps({"team_rows": len(team), "csv_written": True}))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path)
    args = ap.parse_args()
    if args.warehouse_root is not None:
        MAIN_REPO = args.warehouse_root
        INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
    main()
