"""CH-ChallengeLeague data builder: FotMob warehouse JSONs -> match-level
and team-match CSVs. Adapted from the program's shared builder
(bundle tools/build_league_data.py + jleague_lib.py, J.League pattern);
derivation rules unchanged: missing stays missing (NaN) with provenance
flags, targets never imputed, absent feeds never read as zeros.

Usage: python3 build_data.py [RAW_ROOT] [OUT_DIR]
RAW_ROOT defaults to the extracted release layout
  .../Switzerland/Challenge League/<season-dir like 2021-2022>/*.json
Season label is written FotMob-style: 2021-2022 -> 2021/2022.
Differences from the J.League original, CH-forced:
- ev_cards_complete: kept as a column (= has_events) but NOT used for the
  CH card target: the CH event feed carries almost no card events in
  2021/2022-2025/2026 (measured in EDA), unlike J1/J2.
- Unified yellow target: STATS-derived (stats feed, 2023/2024 onward);
  before that yellows are missing, never zero (see PREPROCESSING.md).
"""
import csv
import json
import sys
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
    row = {
        "match_id": int(gen.get("matchId") or path.stem),
        "league": "CH-ChallengeLeague",
        "season": season_label,
        "season_start": int(season_label[:4]),
        "date": (gen.get("matchTimeUTCDate") or "")[:10],
        "kickoff_utc": gen.get("matchTimeUTCDate"),
        "round": gen.get("matchRound"),
        "home_team_id": home.get("id"), "home_team": home.get("name"),
        "away_team_id": away.get("id"), "away_team": away.get("name"),
        "home_goals": hg, "away_goals": ag,
        "coverage_level": gen.get("coverageLevel"),
        "awarded": bool(status.get("awarded")),
        "has_events": bool(evs),
        "has_lineup": False, "formation_home": None, "formation_away": None,
        "coach_home": None, "coach_away": None,
    }
    row["ev_goals_home"] = sum(1 for e in ge if e.get("isHome"))
    row["ev_goals_away"] = sum(1 for e in ge if e.get("isHome") is False)
    row["score_events_mismatch"] = bool(
        row["has_events"] and hg is not None
        and (row["ev_goals_home"], row["ev_goals_away"]) != (hg, ag))
    # HT from goal events: first half = time <= 45 (FotMob files 45+2' as 45)
    ht = None
    if ge and all(e.get("time") is not None and e.get("isHome") is not None for e in ge):
        ht = (sum(1 for e in ge if e["time"] <= 45 and e.get("isHome")),
              sum(1 for e in ge if e["time"] <= 45 and e.get("isHome") is False))
    elif not ge and evs:
        ht = (0, 0)
    row["ht_home_goals"], row["ht_away_goals"] = ht if ht else (None, None)
    row["ht_source"] = "events" if ht else "none"
    cards = [e for e in evs if e.get("type") == "Card"]
    for kind, col in (("Yellow", "ev_yellow"), ("YellowRed", "ev_yellowred"),
                      ("Red", "ev_red")):
        row[f"{col}_home"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome"))
        row[f"{col}_away"] = sum(1 for e in cards if e.get("card") == kind and e.get("isHome") is False)
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
    lu = content.get("lineup") or {}
    for side, gen_side in (("homeTeam", "home"), ("awayTeam", "away")):
        team = lu.get(side) or {}
        if len(team.get("starters") or []) == 11:
            row["has_lineup"] = True
            row[f"formation_{gen_side}"] = team.get("formation")
            coach = team.get("coach") or {}
            row[f"coach_{gen_side}"] = coach.get("name")
    row["has_player_stats"] = bool(content.get("playerStats"))
    # Unified cards for CH: STATS-derived. Measured in EDA: the CH event
    # feed carries almost no card events at all in 2021/2022-2025/2026
    # (0.01-0.16 event yellows/match vs 4.6-5.0 in the stats feed; the
    # event feed only starts carrying cards in 2026/2027). So the stats
    # feed is the ONLY card source, and yellows are missing (never zero)
    # before the stats era starts in 2023/2024.
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
            "has_stats_all": m["has_stats_all"], "has_stats_half": m["has_stats_half"],
        }
        out.append(r)
    return out


def main():
    raw = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(
        "~/workspace/league-work/CH-ChallengeLeague/raw/extracted/Switzerland/Challenge League").expanduser()
    out_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(__file__).parent
    rows, seen = [], set()
    for sdir in sorted(p for p in raw.iterdir() if p.is_dir()):
        label = sdir.name.replace("-", "/", 1)  # 2021-2022 -> 2021/2022
        for f in sorted(sdir.glob("*.json")):
            row = parse_match(label, f)
            assert row["match_id"] not in seen, f"duplicate {row['match_id']}"
            seen.add(row["match_id"])
            rows.append(row)
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    out_dir.mkdir(parents=True, exist_ok=True)
    with open(out_dir / "ch_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    trows = [tr for m in rows for tr in team_rows(m)]
    with open(out_dir / "ch_team_matches.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(trows[0].keys()))
        w.writeheader(); w.writerows(trows)
    print(f"CH-ChallengeLeague: {len(rows)} matches, {len(trows)} team rows")


if __name__ == "__main__":
    main()
