"""Phase 2 builder: warehouse JSONs -> one match-level CSV per league plus
one team-match long CSV per league, under experiments/jleague_eda/data/.

Every derivation rule is documented in PREPROCESSING.md. Missing data stays
missing (NaN) with provenance flags -- targets are never imputed and absent
feeds are never read as zeros.
"""
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from jleague_lib import (LEAGUES, events_of, flat_stats, goal_events,
                         ht_from_events, iter_files, load, shots_of)

OUT = Path(__file__).parent / "data"

HALF_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards",
             "red_cards", "expected_goals", "fouls"]
ALL_KEYS = ["expected_goals", "expected_goals_open_play",
            "expected_goals_set_play", "expected_goals_non_penalty",
            "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
            "shots_inside_box", "shots_outside_box", "big_chance",
            "touches_opp_box", "corners", "yellow_cards", "red_cards",
            "fouls", "Offsides", "keeper_saves", "BallPossesion"]


def season_start_year(label):
    return int(label[:4])


def parse_match(lg, season, path):
    d = load(path)
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

    row = {
        "match_id": int(gen.get("matchId") or path.stem),
        "league": lg, "season": season,
        "season_start": season_start_year(season),
        "date": (gen.get("matchTimeUTCDate") or "")[:10],
        "kickoff_utc": gen.get("matchTimeUTCDate"),
        "round": gen.get("matchRound"),
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "coverage_level": gen.get("coverageLevel"),
        "awarded": bool(status.get("awarded")),
        "has_events": bool(events_of(content)),
        "has_lineup": False, "formation_home": None, "formation_away": None,
        "coach_home": None, "coach_away": None,
    }
    # events-derived scores
    ge = goal_events(content)
    row["ev_goals_home"] = sum(1 for e in ge if e.get("isHome"))
    row["ev_goals_away"] = sum(1 for e in ge if e.get("isHome") is False)
    row["score_events_mismatch"] = bool(
        row["has_events"] and hg is not None
        and (row["ev_goals_home"], row["ev_goals_away"]) != (hg, ag))
    ht = ht_from_events(content)
    row["ht_home_goals"], row["ht_away_goals"] = ht if ht else (None, None)
    row["ht_source"] = "events" if ht else "none"
    # event cards, by credited side (isHome = side of the booked player)
    cards = [e for e in events_of(content) if e.get("type") == "Card"]
    for kind, col in (("Yellow", "ev_yellow"), ("YellowRed", "ev_yellowred"),
                      ("Red", "ev_red")):
        row[f"{col}_home"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome"))
        row[f"{col}_away"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome") is False)
    # Feed-level fact established in Phase 1: the J1/J2 event feeds carry
    # yellow cards (season totals ~800-1,200 yellows); the J3 feed carries
    # ONLY red-family events (11-34 per season), so J3 yellows may come from
    # the stats feed alone and are otherwise missing -- never zero.
    row["ev_cards_complete"] = bool(row["has_events"]) and lg in ("J1", "J2")
    # stats: full-time
    for k in ALL_KEYS:
        row[f"{k}_home"] = st("All", k, 0)
        row[f"{k}_away"] = st("All", k, 1)
    row["has_stats_all"] = ("All", "total_shots") in fs or ("All", "corners") in fs
    # stats: halves
    for per, pre in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
        for k in HALF_KEYS:
            row[f"{pre}_{k}_home"] = st(per, k, 0)
            row[f"{pre}_{k}_away"] = st(per, k, 1)
    row["has_stats_half"] = ("FirstHalf", "corners") in fs
    # extra time present in stats periods?
    periods = ((content.get("stats") or {}).get("Periods") or {})
    row["has_extra_time"] = any("ExtraHalf" in p for p in periods)
    # shotmap aggregates -- regulation play only. The transitional J1 2026
    # league settled drawn matches by shootout, and those attempts sit in
    # the shotmap with period == 'PenaltyShootout' (xG 0.7884 each); the
    # stats feed excludes them, and so do we (they are not match shots).
    shots_all = shots_of(content)
    shots = [s for s in shots_all if s.get("period") != "PenaltyShootout"]
    row["n_shootout_shots"] = len(shots_all) - len(shots)
    row["has_shootout"] = row["n_shootout_shots"] > 0
    loser = status.get("whoLostOnPenalties")
    row["shootout_winner"] = None
    if row["has_shootout"] and loser:
        row["shootout_winner"] = ("away" if loser == home.get("name")
                                  else "home" if loser == away.get("name") else None)
    row["has_shotmap"] = bool(shots)
    hid = home.get("id")
    def credited_home(s):
        return (s.get("teamId") == hid) != bool(s.get("isOwnGoal"))
    for side, want in (("home", True), ("away", False)):
        mine = [s for s in shots if (s.get("teamId") == hid) == want]
        row[f"sm_shots_{side}"] = len(mine) if shots else None
        # Aligned SOT: FotMob's stats feed counts on-target EXCLUDING
        # blocked shots (verified: reproduces the stats value exactly in
        # 92.1% of team-matches, mean |diff| 0.20; the raw isOnTarget count,
        # which includes blocked attempts, is kept alongside).
        row[f"sm_sot_{side}"] = (sum(1 for s in mine if s.get("isOnTarget")
                                     and not s.get("isBlocked")) if shots else None)
        row[f"sm_sot_incl_blocked_{side}"] = (sum(1 for s in mine if s.get("isOnTarget"))
                                              if shots else None)
        row[f"sm_goals_{side}"] = (sum(1 for s in shots if s.get("eventType") == "Goal"
                                       and credited_home(s) == want) if shots else None)
        row[f"sm_xg_{side}"] = (round(sum(s.get("expectedGoals") or 0 for s in mine), 4)
                                if shots else None)
        xgot = [s.get("expectedGoalsOnTarget") for s in mine
                if s.get("expectedGoalsOnTarget") is not None]
        row[f"sm_xgot_{side}"] = round(sum(xgot), 4) if shots and xgot else None
        row[f"sm_xgot_n_{side}"] = len(xgot) if shots else None
        row[f"sm_pen_{side}"] = (sum(1 for s in mine if s.get("situation") == "Penalty")
                                 if shots else None)
        fh = [s for s in mine if s.get("period") == "FirstHalf"]
        row[f"sm_shots_fh_{side}"] = len(fh) if shots else None
        row[f"sm_sot_fh_{side}"] = (sum(1 for s in fh if s.get("isOnTarget")) if shots else None)
        row[f"sm_xg_fh_{side}"] = (round(sum(s.get("expectedGoals") or 0 for s in fh), 4)
                                   if shots else None)
    # lineup
    lu = content.get("lineup") or {}
    for side, gen_side in (("homeTeam", "home"), ("awayTeam", "away")):
        team = lu.get(side) or {}
        if len(team.get("starters") or []) == 11:
            row["has_lineup"] = True
            row[f"formation_{gen_side}"] = team.get("formation")
            coach = team.get("coach") or {}
            row[f"coach_{gen_side}"] = coach.get("name")
    row["has_player_stats"] = bool(content.get("playerStats"))
    # unified cards: stats feed preferred, event feed as fallback w/ source.
    # Documented exception (Phase 1/3 evidence): J1 2021's 'ratings'-era
    # stats feed undercounts yellows (1.24/match vs the event feed's 1.78;
    # exact agreement only 77% vs 91-96% in every later season, where the
    # two feeds track within 0.06/match). The event series is also the one
    # coherent with J2's 2021 level (1.72). So J1 2021 takes event counts.
    force_events = (lg == "J1" and season == "2021")
    for side in ("home", "away"):
        if row[f"yellow_cards_{side}"] is not None and not force_events:
            row[f"yellow_{side}"], row[f"cards_source"] = row[f"yellow_cards_{side}"], "stats"
        elif row["ev_cards_complete"]:
            row[f"yellow_{side}"], row[f"cards_source"] = row[f"ev_yellow_{side}"], "events"
        else:
            row[f"yellow_{side}"], row[f"cards_source"] = None, "none"
        if row[f"red_cards_{side}"] is not None and not force_events:
            row[f"red_{side}"] = row[f"red_cards_{side}"]
        elif row["has_events"]:
            row[f"red_{side}"] = row[f"ev_red_{side}"] + row[f"ev_yellowred_{side}"]
        else:
            row[f"red_{side}"] = None
    return row


def team_rows(m):
    out = []
    for venue, side, opp in (("H", "home", "away"), ("A", "away", "home")):
        gf, ga = m[f"{side}_goals"], m[f"{opp}_goals"]
        r = {
            "match_id": m["match_id"], "league": m["league"], "season": m["season"],
            "season_start": m["season_start"], "date": m["date"],
            "team_id": m[f"{side}_team_id"], "team": m[f"{side}_team"],
            "opponent_id": m[f"{opp}_team_id"], "opponent": m[f"{opp}_team"],
            "venue": venue,
            "goals_for": gf, "goals_against": ga,
            "ht_goals_for": m[f"ht_{side}_goals"], "ht_goals_against": m[f"ht_{opp}_goals"],
            "result": "W" if gf > ga else ("D" if gf == ga else "L"),
            "points": 3 if gf > ga else (1 if gf == ga else 0),
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
            "sm_xg_for": m[f"sm_xg_{side}"], "sm_sot_for": m[f"sm_sot_{side}"],
            "has_shootout": m["has_shootout"], "shootout_winner": m["shootout_winner"],
            "has_shotmap": m["has_shotmap"], "has_stats_all": m["has_stats_all"],
            "has_stats_half": m["has_stats_half"],
        }
        out.append(r)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    by_league = {lg: [] for lg in LEAGUES}
    seen = set()
    for lg, season, path in iter_files():
        row = parse_match(lg, season, path)
        assert row["match_id"] not in seen, f"duplicate match id {row['match_id']}"
        seen.add(row["match_id"])
        by_league[lg].append(row)
    total = 0
    for lg, rows in by_league.items():
        rows.sort(key=lambda r: (r["date"], r["match_id"]))
        total += len(rows)
        with open(OUT / f"{lg.lower()}_matches.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        trows = [tr for m in rows for tr in team_rows(m)]
        with open(OUT / f"{lg.lower()}_team_matches.csv", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
            w.writeheader(); w.writerows(trows)
        print(f"{lg}: {len(rows)} matches, {len(trows)} team rows")
    print(f"TOTAL {total} (warehouse: 6228)")
    assert total == 6228


if __name__ == "__main__":
    main()
