"""Norway OBOS-ligaen data builder: FotMob world warehouse JSONs -> one
match-level CSV + one team-match long CSV under league/NO-Eliteserien/data/.

Source: data_enrichment/fotmob_world_index.csv filtered to league_id=59;
per-match JSONs at the index `path` column. Derivation rules are documented
in league/NO-Eliteserien/analysis/PREPROCESSING.md. Missing data stays
missing (NaN) with provenance flags -- targets are never imputed and absent
feeds are never read as zeros.
"""
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
# The world warehouse JSONs are gitignored and live in the main checkout;
# fall back to it when this worktree has no local copy.
WAREHOUSE_REPO = REPO if (REPO / "data_enrichment" / "fotmob_world" / "Norway").exists() else Path.home() / "workspace" / "footballprediction"
sys.path.insert(0, str(REPO / "league"))
from jleague_lib import events_of, flat_stats, goal_events, ht_from_events, load, shots_of

OUT = Path(__file__).parent
INDEX = WAREHOUSE_REPO / "data_enrichment" / "fotmob_world_index.csv"
LEAGUE_ID = "203"

HALF_KEYS = ["total_shots", "ShotsOnTarget", "corners", "yellow_cards",
             "red_cards", "expected_goals", "fouls"]
ALL_KEYS = ["expected_goals", "expected_goals_open_play",
            "expected_goals_set_play", "expected_goals_non_penalty",
            "total_shots", "ShotsOnTarget", "ShotsOffTarget", "blocked_shots",
            "shots_inside_box", "shots_outside_box", "big_chance",
            "touches_opp_box", "corners", "yellow_cards", "red_cards",
            "fouls", "Offsides", "keeper_saves", "BallPossesion"]


def phase_of(round_label):
    """Norwegian format: 16 teams, single double round-robin, rounds
    1-30, no split and no championship/relegation rounds in the league
    corpus (the end-of-season relegation play-off is a separate FotMob
    competition and is not in this league_id's index rows -- every
    indexed match is a round 1-30 regular-season match). Phase is
    therefore "regular" for every row; the column is kept for shape
    compatibility with the other league CSVs."""
    if round_label is None:
        return "unknown"
    try:
        int(round_label)
    except (TypeError, ValueError):
        return "unknown"
    return "regular"


def parse_match(idx_row):
    path = WAREHOUSE_REPO / idx_row["path"]
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

    season = idx_row["season"]
    rnd = gen.get("matchRound")
    info = ((content.get("matchFacts") or {}).get("infoBox") or {})
    ref = (info.get("Referee") or {}).get("text") or None
    row = {
        "match_id": int(gen.get("matchId") or path.stem),
        "league": "NO-OBOSLigaen", "season": season,
        "season_start": int(season[:4]),
        "date": (gen.get("matchTimeUTCDate") or "")[:10],
        "kickoff_utc": gen.get("matchTimeUTCDate"),
        "round": rnd, "phase": phase_of(rnd),
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "coverage_level": gen.get("coverageLevel"),
        "referee": ref,
        "awarded": bool(status.get("awarded")),
        "has_events": bool(events_of(content)),
    }
    ge = goal_events(content)
    row["ev_goals_home"] = sum(1 for e in ge if e.get("isHome"))
    row["ev_goals_away"] = sum(1 for e in ge if e.get("isHome") is False)
    row["score_events_mismatch"] = bool(
        row["has_events"] and hg is not None
        and (row["ev_goals_home"], row["ev_goals_away"]) != (hg, ag))
    ht = ht_from_events(content)
    row["ht_home_goals"], row["ht_away_goals"] = ht if ht else (None, None)
    row["ht_source"] = "events" if ht else "none"
    cards = [e for e in events_of(content) if e.get("type") == "Card"]
    for kind, col in (("Yellow", "ev_yellow"), ("YellowRed", "ev_yellowred"),
                      ("Red", "ev_red")):
        row[f"{col}_home"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome"))
        row[f"{col}_away"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome") is False)
        row[f"{col}_fh_home"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome") and e.get("time") is not None and e.get("time") <= 45)
        row[f"{col}_fh_away"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome") is False and e.get("time") is not None and e.get("time") <= 45)
    for k in ALL_KEYS:
        row[f"{k}_home"] = st("All", k, 0)
        row[f"{k}_away"] = st("All", k, 1)
    row["has_stats_all"] = all(("All", k) in fs for k in
                                ["BallPossesion", "ShotsOnTarget", "corners", "total_shots"])
    row["has_stats_block"] = bool((content.get("stats") or {}).get("Periods"))
    for per, pre in (("FirstHalf", "fh"), ("SecondHalf", "sh")):
        for k in HALF_KEYS:
            row[f"{pre}_{k}_home"] = st(per, k, 0)
            row[f"{pre}_{k}_away"] = st(per, k, 1)
    row["has_stats_half"] = ("FirstHalf", "corners") in fs
    periods = ((content.get("stats") or {}).get("Periods") or {})
    row["has_extra_time"] = any("ExtraHalf" in p for p in periods)
    shots_all = shots_of(content)
    shots = [s for s in shots_all if s.get("period") != "PenaltyShootout"]
    row["n_shootout_shots"] = len(shots_all) - len(shots)
    row["has_shootout"] = row["n_shootout_shots"] > 0
    row["has_shotmap"] = bool(shots)
    hid = home.get("id")

    def credited_home(s):
        return (s.get("teamId") == hid) != bool(s.get("isOwnGoal"))

    for side, want in (("home", True), ("away", False)):
        mine = [s for s in shots if (s.get("teamId") == hid) == want]
        row[f"sm_shots_{side}"] = len(mine) if shots else None
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
    lu = content.get("lineup") or {}
    row["has_lineup"] = False
    row["formation_home"] = row["formation_away"] = None
    row["coach_home"] = row["coach_away"] = None
    for side, gen_side in (("homeTeam", "home"), ("awayTeam", "away")):
        team = lu.get(side) or {}
        if len(team.get("starters") or []) == 11:
            row["has_lineup"] = True
            row[f"formation_{gen_side}"] = team.get("formation")
            row[f"coach_{gen_side}"] = (team.get("coach") or {}).get("name")
    row["has_player_stats"] = bool(content.get("playerStats"))
    # OBOS has no yellow_cards stats key. The only available, league-wide
    # target is event-unified yellows: Yellow + YellowRed; reds excluded.
    for side in ("home", "away"):
        row[f"yellow_{side}"] = row[f"ev_yellow_{side}"] + row[f"ev_yellowred_{side}"]
        row[f"red_{side}"] = row[f"red_cards_{side}"]
    row["cards_source"] = "events"
    return row


def team_rows(m):
    out = []
    for venue, side, opp in (("H", "home", "away"), ("A", "away", "home")):
        gf, ga = m[f"{side}_goals"], m[f"{opp}_goals"]
        r = {
            "match_id": m["match_id"], "league": m["league"], "season": m["season"],
            "season_start": m["season_start"], "date": m["date"], "phase": m["phase"],
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
            "yellow_for": m[f"yellow_{side}"], "yellow_against": m[f"yellow_{opp}"],
            "red_for": m[f"red_{side}"],
            "fouls_for": m[f"fouls_{side}"],
            "possession": m[f"BallPossesion_{side}"],
            "possession_against": m[f"BallPossesion_{opp}"],
            "box_touches_for": m[f"touches_opp_box_{side}"],
            "box_touches_against": m[f"touches_opp_box_{opp}"],
            "big_chance_for": m[f"big_chance_{side}"],
            "fh_shots_for": m[f"fh_total_shots_{side}"], "sh_shots_for": m[f"sh_total_shots_{side}"],
            "fh_sot_for": m[f"fh_ShotsOnTarget_{side}"], "sh_sot_for": m[f"sh_ShotsOnTarget_{side}"],
            "fh_corners_for": m[f"fh_corners_{side}"], "sh_corners_for": m[f"sh_corners_{side}"],
            "fh_xg_for": m[f"fh_expected_goals_{side}"], "sh_xg_for": m[f"sh_expected_goals_{side}"],
            "fh_yellow_for": m[f"fh_yellow_cards_{side}"],
            "sm_xg_for": m[f"sm_xg_{side}"], "sm_sot_for": m[f"sm_sot_{side}"],
            "sm_xgot_for": m[f"sm_xgot_{side}"], "sm_xgot_n_for": m[f"sm_xgot_n_{side}"],
            "has_shotmap": m["has_shotmap"], "has_stats_all": m["has_stats_all"],
            "has_stats_half": m["has_stats_half"],
        }
        out.append(r)
    return out


def main():
    with open(INDEX) as fh:
        idx = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    rows, seen = [], set()
    for r in idx:
        row = parse_match(r)
        assert row["match_id"] not in seen, f"duplicate match id {row['match_id']}"
        seen.add(row["match_id"])
        rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    with open(OUT / "no_obos_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    trows = [tr for m in rows for tr in team_rows(m)]
    with open(OUT / "no_obos_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
        w.writeheader(); w.writerows(trows)
    print(f"NO-OBOSLigaen: {len(rows)} matches, {len(trows)} team rows (index: {len(idx)})")
    assert len(rows) == len(idx)


if __name__ == "__main__":
    main()
