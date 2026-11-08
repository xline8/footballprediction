"""QA-QatarStars data builder: FotMob warehouse JSONs -> match-level and
team-match CSVs. Adapted from the EC-SerieA builder (same program pattern;
derivation rules unchanged unless QA-forced and noted).

Usage: python3 build_data.py [INDEX_CSV] [RAW_ROOT] [OUT_DIR]
INDEX defaults to the bundle index
  /home/hatch/league-remote/inbox-muse2/QA-QatarStars/index_535.csv
RAW_ROOT defaults to the extracted release layout
  ~/workspace/league-work/QA-QatarStars/data_enrichment/Qatar/"Qatar Stars League"/<2021-2022 ...>
Season label is "2021/2022" style; season_start is the first year.

QA-forced differences from EC:
- Split seasons (2021/2022 .. 2026/2027), 12 teams, 132 matches/season
  (54 in 2026/2027, in progress). One phase only: general.leagueName is
  "Qatar Stars League" in all 714 JSONs -> phase "regular" for every row.
- Stats feed exists ONLY in 2025/2026 (132/132) and 2026/2027 (54/54);
  0 in 2021/2022-2023/2024 and 1 match in 2024/2025. Rich-era keys (42
  incl. duplicates) include total_shots, ShotsOnTarget, corners,
  touches_opp_box, big_chance, fouls, keeper_saves, yellow_cards,
  red_cards with FirstHalf/SecondHalf splits. NO expected_goals key in
  ANY season, NO shotmap in ANY season (0% per index, verified in raw).
- Cards: the event feed in 2021/2022-2025/2026 carries ONLY Red /
  YellowRed card events (no plain Yellow at all: 28-38 card events per
  season, all Red/YellowRed). Plain Yellow events appear only in
  2026/2027 (230). So event-derived yellows in the dev era would count
  second yellows only (~0.2/match vs 4.63/match stats era) and are NOT
  a yellow-card total. The unified QA target is therefore STATS-derived
  (EC precedent), source flag cards_source; before the stats era
  yellows are missing, never zero. Event card counts are kept in ev_*
  columns as evidence.
- Referee: content.matchFacts.infoBox.Referee.text, present
  (non-empty) only 9/132 in 2025/2026, 53/54 in 2026/2027, 0 in
  2021/2022-2024/2025. Kept as a column + has_referee flag; no
  referee feature in dev.
- 1H goals / 1H cards from event times (minute <= 45) alongside,
  per the PLAYBOOK.
"""
import csv
import json
import sys
from collections import Counter
from pathlib import Path

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


def parse_match(season_label, path):
    with open(path) as fh:
        d = json.load(fh)
    gen, hdr, content = d.get("general") or {}, d.get("header") or {}, d.get("content") or {}
    status = hdr.get("status") or {}
    home, away = gen.get("homeTeam") or {}, gen.get("awayTeam") or {}
    score = status.get("scoreStr") or ""
    hg = ag = None
    if " - " in score:
        try:
            hg, ag = (int(x) for x in score.split(" - "))
        except ValueError:
            pass
    fs = flat_stats(content)

    def st(period, key, side):
        v = fs.get((period, key))
        return None if v is None else v[side]

    evs = events_of(content)
    ge = [e for e in evs if e.get("type") == "Goal"]
    league_name = gen.get("leagueName")
    referee = ((((content.get("matchFacts") or {}).get("infoBox") or {})
                .get("Referee") or {}).get("text") or "") or None
    if referee is not None and not referee.strip():
        referee = None
    row = {
        "match_id": int(gen.get("matchId") or path.stem),
        "league": "QA-QatarStars",
        "season": season_label,
        "season_start": int(season_label[:4]),
        "date": (gen.get("matchTimeUTCDate") or "")[:10],
        "kickoff_utc": gen.get("matchTimeUTCDate"),
        "round": gen.get("matchRound"),
        "league_name": league_name,
        "phase": "regular",
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "coverage_level": gen.get("coverageLevel"),
        "awarded": bool(status.get("awarded")),
        "finished": bool(status.get("finished")),
        "has_events": bool(evs),
        "has_lineup": False, "formation_home": None, "formation_away": None,
        "coach_home": None, "coach_away": None,
        "referee": referee,
        "has_referee": referee is not None,
    }
    row["ev_goals_home"] = sum(1 for e in ge if e.get("isHome"))
    row["ev_goals_away"] = sum(1 for e in ge if e.get("isHome") is False)
    row["score_events_mismatch"] = bool(
        row["has_events"] and hg is not None
        and (row["ev_goals_home"], row["ev_goals_away"]) != (hg, ag))
    # HT goals + HT cards from event times: first half = time <= 45
    # (FotMob files 45+2' as 45). A match WITH an events payload and no
    # goal/card events gets HT 0-0; an empty events payload gets HT missing.
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
    row["has_shotmap"] = bool(((content or {}).get("shotmap") or {}).get("shots"))
    # stats-feed yellow/red kept alongside the unified target (evidence)
    sy_h, sy_a = st("All", "yellow_cards", 0), st("All", "yellow_cards", 1)
    sr_h, sr_a = st("All", "red_cards", 0), st("All", "red_cards", 1)
    row["stats_yellow_home"], row["stats_yellow_away"] = sy_h, sy_a
    row["stats_red_home"], row["stats_red_away"] = sr_h, sr_a
    lu = content.get("lineup") or {}
    for side, gen_side in (("homeTeam", "home"), ("awayTeam", "away")):
        team = lu.get(side) or {}
        if len(team.get("starters") or []) == 11:
            row["has_lineup"] = True
            row[f"formation_{gen_side}"] = team.get("formation")
            coach = team.get("coach") or {}
            row[f"coach_{gen_side}"] = coach.get("name")
    row["has_player_stats"] = bool(content.get("playerStats"))
    # Unified cards for QA: STATS-derived (see module docstring). The dev
    # era event feed carries no plain Yellow events at all, so an
    # event-derived dev target would count second yellows only.
    for side in ("home", "away"):
        if row[f"yellow_cards_{side}"] is not None:
            row[f"yellow_{side}"], row["cards_source"] = row[f"yellow_cards_{side}"], "stats"
            row[f"red_{side}"] = row[f"red_cards_{side}"]
        else:
            row[f"yellow_{side}"], row["cards_source"] = None, "none"
            row[f"red_{side}"] = None
    return row


def team_rows(m):
    out = []
    for venue, side, opp in (("H", "home", "away"), ("A", "away", "home")):
        gf, ga = m[f"{side}_goals"], m[f"{opp}_goals"]
        r = {
            "match_id": m["match_id"], "league": m["league"], "season": m["season"],
            "season_start": m["season_start"], "date": m["date"],
            "phase": m["phase"],
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
            "fouls_for": m[f"fouls_{side}"],
            "possession": m[f"BallPossesion_{side}"],
            "fh_shots_for": m[f"fh_total_shots_{side}"], "sh_shots_for": m[f"sh_total_shots_{side}"],
            "fh_sot_for": m[f"fh_ShotsOnTarget_{side}"], "sh_sot_for": m[f"sh_ShotsOnTarget_{side}"],
            "fh_corners_for": m[f"fh_corners_{side}"], "sh_corners_for": m[f"sh_corners_{side}"],
            "fh_xg_for": m[f"fh_expected_goals_{side}"], "sh_xg_for": m[f"sh_expected_goals_{side}"],
            "has_stats_all": m["has_stats_all"], "has_stats_half": m["has_stats_half"],
        }
        out.append(r)
    return out


def main():
    index = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "/home/hatch/league-remote/inbox-muse2/QA-QatarStars/index_535.csv")
    raw_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
        "~/workspace/league-work/QA-QatarStars/data_enrichment").expanduser()
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent
    idx_rows = list(csv.DictReader(open(index)))
    rows, seen = [], set()
    id_names = {}
    for r in idx_rows:
        # index paths are warehouse-relative ("data_enrichment/fotmob_world/...");
        # the release tar stores them under data_enrichment/Qatar/...
        rel = r["path"].replace("data_enrichment/fotmob_world/", "", 1)
        path = raw_root / rel
        assert path.exists(), f"missing JSON {path}"
        row = parse_match(r["season"], path)
        assert row["match_id"] == int(r["match_id"]), (row["match_id"], r["match_id"])
        assert row["match_id"] not in seen, f"duplicate {row['match_id']}"
        seen.add(row["match_id"])
        assert row["finished"], f"unfinished match {row['match_id']}"
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
    with open(out_dir / "qa_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    trows = [tr for m in rows for tr in team_rows(m)]
    with open(out_dir / "qa_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
        w.writeheader(); w.writerows(trows)
    print(f"QA-QatarStars: {len(rows)} matches (index {len(idx_rows)}), "
          f"{len(trows)} team rows, {len(id_names)} team ids")


if __name__ == "__main__":
    main()
