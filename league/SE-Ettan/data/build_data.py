"""SE-Ettan data builder: FotMob warehouse JSONs -> match-level and
team-match CSVs. Adapted from the QA-QatarStars builder (same program
pattern; derivation rules unchanged unless SE-forced and noted).

Usage: python3 build_data.py [INDEX_CSV] [RAW_ROOT] [OUT_DIR]
INDEX defaults to the bundle index
  /home/hatch/league-remote/inbox-muse2/SE-Ettan/index_169.csv
RAW_ROOT defaults to the extracted release layout
  ~/workspace/league-work/SE-Ettan/data_enrichment/Sweden/Ettan/<2021 ...>
Season label is the calendar year ("2021" .. "2026").

SE-forced differences from QA:
- Calendar seasons, 32 teams in TWO groups (Ettan Norra / Ettan Soedra,
  16 teams each, 240 matches/group/season). general.leagueName carries
  the group; phase = "norra" / "sodra" (both ordinary regular-season
  rows, no playoffs in this feed).
- INDEX OVERSTATES PLAYED MATCHES: the index lists 480 rows for 2021
  but only 262 were actually played. The other 218 are fixtures that
  were never started (header.status.finished false, no scoreStr) and
  the index carries a placeholder score of "0-0" for them. The raw JSON
  is ground truth: unplayed fixtures are EXCLUDED from the CSVs (2662
  played rows out of 2880 index rows), never counted as 0-0. This is a
  deliberate, documented deviation from the "CSV count == index count"
  check — the check is replaced by "CSV count == played count verified
  in raw JSONs" (262 + 480*4 + 480 = 2662). The 218 skipped match ids
  are listed in the build log.
- Stats feed is null in EVERY payload (content.stats is null, shotmap
  shots empty) in all six seasons: every stats column is None,
  has_stats_all/has_stats_half False, has_shotmap False. Scores-only
  league, confirmed in raw, not just in the index.
- Events: content.matchFacts.events carries Goal / Substitution /
  Card / Half / MissedPenalty. Present in 480/480 matches 2022-2026
  and in 0/480 matches in 2021 (no events payload at all that season).
  Card kinds include plain Yellow (6312 in 2022-2025), YellowRed,
  Red. Event-derived yellows are recorded as ev_* evidence columns;
  the unified cards target stays missing (no stats feed) — see
  analysis/EDA.md for the K verdict. Referee: infoBox Referee text is
  EMPTY in every played match (0/2662) — no referee feature possible.
- HT goals / HT cards from event times (minute <= 45) as in QA; HT is
  missing (not zero) wherever the events payload is absent (all 2021).
- One awarded match in 2024 (match 4398xxx — see build log); kept as
  a real result with awarded=True.
- 2026 rows are built into the CSVs (program precedent: CH/QA reserve
  seasons are built but never used in any analysis, fit, or gate).
  No analysis in this league reads 2026.
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

PHASE_BY_LEAGUE_NAME = {"Ettan Norra": "norra", "Ettan Södra": "sodra",
                        "Ettan Soedra": "sodra"}


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
        "league": "SE-Ettan",
        "season": season_label,
        "season_start": int(season_label[:4]),
        "date": (gen.get("matchTimeUTCDate") or "")[:10],
        "kickoff_utc": gen.get("matchTimeUTCDate"),
        "round": gen.get("matchRound"),
        "league_name": league_name,
        "phase": PHASE_BY_LEAGUE_NAME.get(league_name, "unknown"),
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
    # Unified cards target: no stats feed anywhere in SE, so the target
    # stays missing (never zero). Event counts are kept as ev_* evidence.
    for side in ("home", "away"):
        row[f"yellow_{side}"] = None
        row[f"red_{side}"] = None
    row["cards_source"] = "none"
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
        "/home/hatch/league-remote/inbox-muse2/SE-Ettan/index_169.csv")
    raw_root = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(
        "~/workspace/league-work/SE-Ettan/data_enrichment").expanduser()
    out_dir = Path(sys.argv[3]) if len(sys.argv) > 3 else Path(__file__).parent
    idx_rows = list(csv.DictReader(open(index)))
    rows, seen = [], set()
    skipped, awarded = [], []
    id_names = {}
    per_season = Counter()
    for r in idx_rows:
        rel = r["path"].replace("data_enrichment/fotmob_world/", "", 1)
        path = raw_root / rel
        assert path.exists(), f"missing JSON {path}"
        with open(path) as fh:
            probe = json.load(fh)
        st = (probe.get("header") or {}).get("status") or {}
        # Ground truth is the raw JSON: fixtures never started (no
        # scoreStr) are NOT played matches, whatever the index says.
        if not st.get("finished") or not st.get("scoreStr"):
            skipped.append((int(r["match_id"]), r["season"], r["score"]))
            continue
        row = parse_match(r["season"], path)
        assert row["match_id"] == int(r["match_id"]), (row["match_id"], r["match_id"])
        assert row["match_id"] not in seen, f"duplicate {row['match_id']}"
        seen.add(row["match_id"])
        assert row["finished"], f"unfinished match {row['match_id']}"
        assert row["home_goals"] is not None and row["away_goals"] is not None
        if row["awarded"]:
            awarded.append(row["match_id"])
        per_season[row["season"]] += 1
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
    with open(out_dir / "se_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    trows = [tr for m in rows for tr in team_rows(m)]
    with open(out_dir / "se_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
        w.writeheader(); w.writerows(trows)
    print(f"SE-Ettan: {len(rows)} played matches (index {len(idx_rows)}), "
          f"{len(trows)} team rows, {len(id_names)} team ids")
    print(f"played per season: {dict(sorted(per_season.items()))}")
    print(f"skipped unplayed fixtures: {len(skipped)} "
          f"(index placeholder scores, never started) — "
          f"by season: {dict(sorted(Counter(s for _, s, _ in skipped).items()))}")
    print(f"awarded matches kept (awarded=True): {awarded}")
    print(f"first 10 skipped match ids: {[m for m, _, _ in skipped[:10]]}")


if __name__ == "__main__":
    main()
