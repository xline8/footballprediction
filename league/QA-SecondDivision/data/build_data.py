"""QA-SecondDivision data builder: FotMob world-warehouse JSONs -> match-level
and team-match CSVs. Adapted from the QA-QatarStars builder (same country,
same payload shape; derivation rules unchanged unless QA-SD-forced and noted).

Usage: python3 build_data.py [INDEX_CSV] [WAREHOUSE_ROOT] [OUT_DIR]
INDEX defaults to the world warehouse index in the main footballprediction
checkout; WAREHOUSE_ROOT defaults to the warehouse root there (the JSONs
are gitignored and shared across worktrees -- see EE-Meistriliiga's
build_data.py, same MAIN_REPO convention).

QA-SD-forced differences from QA-QatarStars:
- The world-warehouse JSONs carry general/header as NULL (unlike the
  QA-QatarStars release bundle). Score, date, home/away team NAMES come
  from the INDEX (authoritative); team IDS come from
  content.lineup.homeTeam/awayTeam.id (verified: 13 ids, one name each);
  round + leagueName come from content.matchFacts.infoBox.Tournament;
  kickoff date is cross-checked against infoBox "Match Date".utcTime.
- 3 seasons only (2024/2025, 2025/2026, 2026/2027 in progress); 8 teams
  in the two complete seasons (double round robin, 14 rounds x 4 = 56),
  11 teams in 2026/2027 (5 matches/round, one bye per round; round 5
  short one match -- presumably postponed, not in the warehouse).
- Stats feed: 38/56 in 2024/2025 (rounds 6-14; rounds 1-5 essentially
  stat-less: 0,1,0,0,1 matches with stats), 56/56 in 2025/2026,
  29/29 in 2026/2027. NO expected_goals key in ANY season, NO shotmap
  in ANY season (0 shots in every shotmap payload), NO touches_opp_box.
  big_chance / shots_inside_box / shots_outside_box keys exist but are
  0/0 in every match (degenerate -- recorded, never used).
- Cards: the UNIFIED target is EVENT-derived (Yellow + YellowRed),
  following the SA-FirstDivision precedent: the stats feed undercounts
  the event feed one-directionally (2024/2025: 34 exact / 4 low / 0 high,
  mean -0.21; 2025/2026: 37 / 19 / 0, mean -0.52; pooled pre-virgin 71 /
  23 / 0, mean -0.40). Stats yellows are kept alongside as evidence.
- Referee: named in 0 matches in 2024/2025 and 2025/2026, 1 match in
  2026/2027 (Farhan Al Ruaili). No referee feature in dev.
- leagueName quirk: 10 matches in 2025/2026 (all Lusail SC, rounds 5-14)
  and 8 matches in 2026/2027 (rounds 5-6) carry leagueName
  "Second Division" instead of "Qatar Stars League 2". Same 8 teams,
  same round sequence, no phase split -- a naming quirk, not a format
  change. Phase is "regular" for every row.
- 1H goals / 1H event-yellows from event times (minute <= 45).
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
HALF_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards",
             "red_cards", "expected_goals", "fouls"]
ALL_KEYS = ["expected_goals", "expected_goals_open_play",
            "expected_goals_set_play", "expected_goals_non_penalty",
            "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
            "shots_inside_box", "shots_outside_box", "big_chance",
            "touches_opp_box", "corners", "yellow_cards", "red_cards",
            "fouls", "Offsides", "keeper_saves", "BallPossesion"]


def _num(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    if isinstance(v, str):
        head = v.split(" ")[0].replace("%", "")
        try:
            return float(head)
        except ValueError:
            return None
    return None


def flat_stats(content):
    out = {}
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for s in group.get("stats", []) or []:
                vals = s.get("stats") or [None, None]
                h, a = _num(vals[0]), _num(vals[1]) if len(vals) > 1 else None
                if h is None and a is None:
                    continue
                out[(period, s.get("key"))] = (h, a)
    return out


def events_of(content):
    ev = ((content or {}).get("matchFacts") or {}).get("events") or {}
    return ev.get("events") or []


def parse_match(idx_row, path):
    with open(path) as fh:
        d = json.load(fh)
    content = d.get("content") or {}
    mf = content.get("matchFacts") or {}
    ib = mf.get("infoBox") or {}
    tourn = ib.get("Tournament") or {}
    # Index is authoritative for identity/score/date/teams (world-warehouse
    # JSONs carry general/header as null).
    season_label = idx_row["season"]
    hg, ag = (int(x) for x in idx_row["score"].split("-"))
    date = idx_row["date"]
    # Cross-check: infoBox Match Date must agree with the index date.
    utc = ((ib.get("Match Date") or {}).get("utcTime") or "")[:10]
    date_mismatch = bool(utc) and utc != date
    fs = flat_stats(content)

    def st(period, key, side):
        v = fs.get((period, key))
        return None if v is None else v[side]

    evs = events_of(content)
    ge = [e for e in evs if e.get("type") == "Goal"]
    referee = ((ib.get("Referee") or {}).get("text") or "") or None
    if referee is not None and not referee.strip():
        referee = None
    lu = content.get("lineup") or {}
    home = lu.get("homeTeam") or {}
    away = lu.get("awayTeam") or {}
    row = {
        "match_id": int(idx_row["match_id"]),
        "league": "QA-SecondDivision",
        "season": season_label,
        "season_start": int(season_label[:4]),
        "date": date,
        "kickoff_utc": utc or None,
        "date_mismatch": date_mismatch,
        "round": tourn.get("roundName"),
        "league_name": tourn.get("leagueName"),
        "phase": "regular",
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "has_events": bool(evs),
        "has_lineup": False, "formation_home": None, "formation_away": None,
        "coach_home": None, "coach_away": None,
        "referee": referee,
        "has_referee": referee is not None,
        "ongoing": bool(d.get("ongoing")),
    }
    # Index team names must agree with the lineup names (same teams).
    row["name_mismatch"] = bool(
        (home.get("name") and home["name"] != idx_row["home"])
        or (away.get("name") and away["name"] != idx_row["away"]))
    row["ev_goals_home"] = sum(1 for e in ge if e.get("isHome"))
    row["ev_goals_away"] = sum(1 for e in ge if e.get("isHome") is False)
    row["score_events_mismatch"] = bool(
        row["has_events"]
        and (row["ev_goals_home"], row["ev_goals_away"]) != (hg, ag))
    ht = None
    if ge and all(e.get("time") is not None and e.get("isHome") is not None for e in ge):
        ht = (sum(1 for e in ge if e["time"] <= 45 and e.get("isHome")),
              sum(1 for e in ge if e["time"] <= 45 and e.get("isHome") is False))
    elif not ge and evs:
        ht = (0, 0)
    row["ht_home_goals"], row["ht_away_goals"] = ht if ht else (None, None)
    row["ht_source"] = "events" if ht else "none"
    row["goals_1h_total"] = (row["ht_home_goals"] + row["ht_away_goals"]) if ht else None
    cards = [e for e in evs if e.get("type") == "Card"]
    for kind, col in (("Yellow", "ev_yellow"), ("YellowRed", "ev_yellowred"),
                      ("Red", "ev_red")):
        row[f"{col}_home"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome"))
        row[f"{col}_away"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome") is False)
    yell_cards = [e for e in cards if e.get("card") in ("Yellow", "YellowRed")]
    htc = None
    if yell_cards and all(e.get("time") is not None and e.get("isHome") is not None for e in yell_cards):
        htc = (sum(1 for e in yell_cards if e["time"] <= 45 and e.get("isHome")),
               sum(1 for e in yell_cards if e["time"] <= 45 and e.get("isHome") is False))
    elif not yell_cards and evs:
        htc = (0, 0)
    row["ht_yellow_home"], row["ht_yellow_away"] = htc if htc else (None, None)
    row["ht_cards_source"] = "events" if htc else "none"
    row["ev_yellow_1h"] = (row["ht_yellow_home"] + row["ht_yellow_away"]) if htc else None
    row["ev_cards_complete"] = bool(row["has_events"])
    for k in ALL_KEYS:
        row[f"{k}_home"] = st("All", k, 0)
        row[f"{k}_away"] = st("All", k, 1)
    row["has_stats_all"] = ("All", "total_shots") in fs or ("All", "corners") in fs
    for per, pre in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
        for k in HALF_KEYS:
            row[f"{pre}_{k}_home"] = st(per, k, 0)
            row[f"{pre}_{k}_away"] = st(per, k, 1)
    row["has_stats_half"] = ("FirstHalf", "corners") in fs
    periods = ((content.get("stats") or {}).get("Periods") or {})
    row["has_extra_time"] = any("ExtraHalf" in p for p in periods)
    sm = (content.get("shotmap") or {}).get("shots") or []
    row["has_shotmap"] = bool(sm)
    row["shotmap_n"] = len(sm)
    sy_h, sy_a = st("All", "yellow_cards", 0), st("All", "yellow_cards", 1)
    sr_h, sr_a = st("All", "red_cards", 0), st("All", "red_cards", 1)
    row["stats_yellow_home"], row["stats_yellow_away"] = sy_h, sy_a
    row["stats_red_home"], row["stats_red_away"] = sr_h, sr_a
    for side, gen_side in (("homeTeam", "home"), ("awayTeam", "away")):
        team = lu.get(side) or {}
        if len(team.get("starters") or []) == 11:
            row["has_lineup"] = True
            row[f"formation_{gen_side}"] = team.get("formation")
            coach = team.get("coach") or {}
            row[f"coach_{gen_side}"] = coach.get("name")
    row["has_player_stats"] = bool(content.get("playerStats"))
    # Unified cards for QA-SD: EVENT-derived (Yellow + YellowRed; see
    # module docstring). Stats yellows are evidence columns only.
    for side in ("home", "away"):
        row[f"yellow_{side}"] = (row[f"ev_yellow_{side}"]
                                 + row[f"ev_yellowred_{side}"])
        row["cards_source"] = "events"
        row[f"red_{side}"] = row[f"ev_red_{side}"]
    return row


def team_rows(m):
    out = []
    for venue, side, opp in (("H", "home", "away"), ("A", "away", "home")):
        gf, ga = m[f"{side}_goals"], m[f"{opp}_goals"]
        r = {
            "match_id": m["match_id"], "league": m["league"], "season": m["season"],
            "season_start": m["season_start"], "date": m["date"],
            "phase": m["phase"], "round": m["round"],
            "team_id": m[f"{side}_team_id"], "team": m[f"{side}_team"],
            "opponent_id": m[f"{opp}_team_id"], "opponent": m[f"{opp}_team"],
            "venue": venue,
            "goals_for": gf, "goals_against": ga,
            "ht_goals_for": m[f"ht_{side}_goals"], "ht_goals_against": m[f"ht_{opp}_goals"],
            "ht_yellow_for": m[f"ht_yellow_{side}"],
            "result": "W" if gf is not None and ga is not None and gf > ga else ("D" if gf == ga else "L"),
            "points": 3 if gf is not None and ga is not None and gf > ga else (1 if gf == ga else 0),
            "xg_for": m[f"expected_goals_{side}"], "xg_against": m[f"expected_goals_{opp}"],
            "shots_for": m[f"total_shots_{side}"], "shots_against": m[f"total_shots_{opp}"],
            "sot_for": m[f"ShotsOnTarget_{side}"], "sot_against": m[f"ShotsOnTarget_{opp}"],
            "corners_for": m[f"corners_{side}"], "corners_against": m[f"corners_{opp}"],
            "yellow_for": m[f"yellow_{side}"], "red_for": m[f"red_{side}"],
            "yellow_stats_for": m[f"stats_yellow_{side}"],
            "fouls_for": m[f"fouls_{side}"],
            "possession": m[f"BallPossesion_{side}"],
            "fh_shots_for": m[f"fh_total_shots_{side}"], "sh_shots_for": m[f"sh_total_shots_{side}"],
            "fh_sot_for": m[f"fh_ShotsOnTarget_{side}"], "sh_sot_for": m[f"sh_ShotsOnTarget_{side}"],
            "fh_corners_for": m[f"fh_corners_{side}"], "sh_corners_for": m[f"sh_corners_{side}"],
            "fh_yellow_for": m[f"fh_yellow_cards_{side}"], "sh_yellow_for": m[f"sh_yellow_cards_{side}"],
            "fh_xg_for": m[f"fh_expected_goals_{side}"], "sh_xg_for": m[f"sh_expected_goals_{side}"],
            "has_stats_all": m["has_stats_all"], "has_stats_half": m["has_stats_half"],
        }
        out.append(r)
    return out


def main():
    index = Path(sys.argv[1]) if len(sys.argv) > 1 else MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
    wh = Path(sys.argv[2]) if len(sys.argv) > 2 else MAIN_REPO / "data_enrichment" / "fotmob_world"
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent
    idx_rows = [r for r in csv.DictReader(open(index)) if r["league_id"] == "11030"]
    rows, seen = [], set()
    id_names = {}
    for r in idx_rows:
        path = MAIN_REPO / r["path"]
        assert path.exists(), f"missing JSON {path}"
        row = parse_match(r, path)
        assert row["match_id"] == int(r["match_id"]), (row["match_id"], r["match_id"])
        assert row["match_id"] not in seen, f"duplicate {row['match_id']}"
        seen.add(row["match_id"])
        assert not row["ongoing"], f"ongoing match {row['match_id']}"
        assert not row["date_mismatch"], f"date mismatch {row['match_id']}"
        assert not row["name_mismatch"], f"name mismatch {row['match_id']}"
        for tid, tname in ((row["home_team_id"], row["home_team"]),
                           (row["away_team_id"], row["away_team"])):
            id_names.setdefault(tid, Counter())[tname] += 1
        rows.append(row)
    canonical = {tid: c.most_common(1)[0][0] for tid, c in id_names.items()}
    variants = {tid: dict(c) for tid, c in id_names.items() if len(c) > 1}
    for row in rows:
        row["home_team"] = canonical[row["home_team_id"]]
        row["away_team"] = canonical[row["away_team_id"]]
    if variants:
        print(f"team-name variants canonicalised: {variants}")
    else:
        print("team ids carry exactly one name each")
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "qasd_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    trows = [tr for m in rows for tr in team_rows(m)]
    with open(out_dir / "qasd_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
        w.writeheader(); w.writerows(trows)
    print(f"QA-SecondDivision: {len(rows)} matches (index {len(idx_rows)}), "
          f"{len(trows)} team rows, {len(id_names)} team ids")
    print(f"score/events mismatches: {sum(r['score_events_mismatch'] for r in rows)}; "
          f"shotmap shots total: {sum(r['shotmap_n'] for r in rows)}")


if __name__ == "__main__":
    main()
