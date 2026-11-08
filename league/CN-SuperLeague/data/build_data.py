"""Build China Super League Phase-A tables from the FotMob warehouse.

This is an extraction step only: it does not fit models or create results.
"""
import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INDEX_NAME = "data_enrichment/fotmob_world_index.csv"
LEAGUE_ID = "120"
STAT_KEYS = ("total_shots", "ShotsOnTarget", "corners", "yellow_cards",
             "red_cards", "fouls", "touches_opp_box", "BallPossesion",
             "big_chance")
PERIODS = (("All", ""), ("FirstHalf", "fh_"), ("SecondHalf", "sh_"))


def number(value):
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split()[0].replace("%", ""))
    except (TypeError, ValueError):
        return None


def flat_stats(content):
    """Flatten Periods, retaining the last repeated value and conflict count."""
    out, seen, conflicts = {}, {}, 0
    periods = ((content or {}).get("stats") or {}).get("Periods") or {}
    for period, block in periods.items():
        for group in (block or {}).get("stats", []) or []:
            for stat in group.get("stats", []) or []:
                vals = stat.get("stats") or []
                pair = (number(vals[0]) if len(vals) else None,
                        number(vals[1]) if len(vals) > 1 else None)
                if pair == (None, None) or not stat.get("key"):
                    continue
                key = (period, stat["key"])
                if key in seen and seen[key] != pair:
                    conflicts += 1
                seen[key] = pair
                out[key] = pair
    return out, conflicts


def events(content):
    raw = ((content or {}).get("matchFacts") or {}).get("events") or {}
    return raw.get("events") or [] if isinstance(raw, dict) else []


def event_minute(event):
    value = event.get("time")
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).split("+")[0])
    except (TypeError, ValueError):
        return None


def score(value):
    parts = (value or "0 - 0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def tournament_info(content):
    box = (((content or {}).get("matchFacts") or {}).get("infoBox") or {})
    tournament = box.get("Tournament") or {}
    name = tournament.get("leagueName") or ""
    low = name.lower()
    if "grp. a" in low:
        phase = "group_a"
    elif "grp. b" in low:
        phase = "group_b"
    elif "championship" in low:
        phase = "championship"
    elif "relegation" in low:
        phase = "relegation"
    else:
        phase = "regular"
    return phase, name, tournament.get("id") or ""


def card_counts(ev, home):
    direct_yellow = sum(1 for e in ev if e.get("type") == "Card" and e.get("card") == "Yellow"
                        and bool(e.get("isHome")) == home)
    second_yellow = sum(1 for e in ev if e.get("type") == "Card" and e.get("card") == "YellowRed"
                        and bool(e.get("isHome")) == home)
    straight_red = sum(1 for e in ev if e.get("type") == "Card" and e.get("card") == "Red"
                       and bool(e.get("isHome")) == home)
    # Event target counts a second-yellow as both a yellow-card occurrence and a red dismissal.
    return direct_yellow + second_yellow, straight_red + second_yellow, direct_yellow, second_yellow


def build(index_row, warehouse_root):
    payload = json.loads((warehouse_root / index_row["path"]).read_text())
    header, content = payload.get("header") or {}, payload.get("content") or {}
    teams = header.get("teams") or []
    if len(teams) < 2:
        teams = [payload.get("general", {}).get(k) or {} for k in ("homeTeam", "awayTeam")]
    home, away = teams[0], teams[1]
    status = header.get("status") or {}
    hg, ag = score(status.get("scoreStr") or index_row.get("score"))
    stats, conflicts = flat_stats(content)
    ev = events(content)
    phase, tournament_name, tournament_id = tournament_info(content)
    info = (((content.get("matchFacts") or {}).get("infoBox") or {}))
    referee = (info.get("Referee") or {}).get("text") or ""
    row = {
        "match_id": index_row["match_id"], "season": index_row["season"], "date": index_row["date"],
        "home_id": home.get("id"), "away_id": away.get("id"),
        "home_name": home.get("name") or "", "away_name": away.get("name") or "",
        # TH-shape aliases so the copied league engines load this CSV
        # with only season/path changes; xG does not exist in this corpus.
        "league": "Super League",
        "home_team_id": home.get("id"), "away_team_id": away.get("id"),
        "home_team": home.get("name") or "", "away_team": away.get("name") or "",
        "expected_goals_home": "", "expected_goals_away": "",
        "expected_goals_set_play_home": "", "expected_goals_set_play_away": "",
        "home_goals": hg, "away_goals": ag, "phase": phase,
        "tournament_id": tournament_id, "tournament_name": tournament_name, "referee": referee,
        "has_stats": int(("All", "total_shots") in stats),
        "has_splits": int("FirstHalf" in ((content.get("stats") or {}).get("Periods") or {})
                         and "SecondHalf" in ((content.get("stats") or {}).get("Periods") or {})),
        "has_events": int(bool(ev)), "stats_conflicts": conflicts,
        "score_header": status.get("scoreStr") or index_row.get("score") or "",
    }
    goals = [e for e in ev if e.get("type") == "Goal" and not e.get("isPenaltyShootoutEvent")]
    row["goals_1h_home"] = sum(1 for e in goals if event_minute(e) is not None and event_minute(e) <= 45 and e.get("isHome"))
    row["goals_1h_away"] = sum(1 for e in goals if event_minute(e) is not None and event_minute(e) <= 45 and e.get("isHome") is False)
    row["goals_1h_source"] = "events" if ev else "none"
    for is_home in (True, False):
        side = "home" if is_home else "away"
        y, red, direct, second = card_counts(ev, is_home)
        row[f"ev_yellow_{side}"], row[f"ev_red_{side}"] = y, red
        row[f"ev_yellow_direct_{side}"], row[f"ev_yellowred_{side}"] = direct, second
        row[f"ev_yellow_1h_{side}"] = sum(1 for e in ev if e.get("type") == "Card"
                                            and e.get("card") in ("Yellow", "YellowRed")
                                            and event_minute(e) is not None and event_minute(e) <= 45
                                            and bool(e.get("isHome")) == is_home)
    for key in STAT_KEYS:
        for period, prefix in PERIODS:
            h, a = stats.get((period, key), (None, None))
            row[f"{prefix}{key}_home"], row[f"{prefix}{key}_away"] = h, a
    row["score_event_agreement"] = int((sum(1 for e in goals if e.get("isHome")) == hg)
                                       and (sum(1 for e in goals if e.get("isHome") is False) == ag))
    row["has_shotmap"] = int(bool(((content.get("shotmap") or {}).get("shots") or [])))
    return row


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]), extrasaction="ignore")
        writer.writeheader(); writer.writerows(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--warehouse-root", type=Path, default=REPO)
    args = ap.parse_args()
    index = args.warehouse_root / INDEX_NAME
    index_rows = [r for r in csv.DictReader(index.open()) if r["league_id"] == LEAGUE_ID]
    rows = [build(r, args.warehouse_root) for r in index_rows]
    rows.sort(key=lambda r: (r["date"], r["match_id"]))
    assert len(rows) == len(index_rows) == 1442, (len(rows), len(index_rows))
    assert len({r["match_id"] for r in rows}) == len(rows)
    expected = Counter(r["season"] for r in index_rows)
    actual = Counter(r["season"] for r in rows)
    assert expected == actual
    write_csv(HERE / "cn_matches.csv", rows)
    team_rows = []
    for r in rows:
        for side, other in (("home", "away"), ("away", "home")):
            item = {"match_id": r["match_id"], "season": r["season"], "date": r["date"],
                    "phase": r["phase"], "team_id": r[f"{side}_id"], "team": r[f"{side}_name"],
                    "venue": side, "goals_for": r[f"{side}_goals"], "goals_against": r[f"{other}_goals"],
                    "goals_1h_for": r[f"goals_1h_{side}"], "goals_1h_against": r[f"goals_1h_{other}"],
                    "referee": r["referee"]}
            for key in STAT_KEYS:
                item[f"{key}_for"], item[f"{key}_against"] = r[f"{key}_{side}"], r[f"{key}_{other}"]
                item[f"fh_{key}_for"], item[f"fh_{key}_against"] = r[f"fh_{key}_{side}"], r[f"fh_{key}_{other}"]
                item[f"sh_{key}_for"], item[f"sh_{key}_against"] = r[f"sh_{key}_{side}"], r[f"sh_{key}_{other}"]
            item["event_yellow_for"], item["event_yellow_against"] = r[f"ev_yellow_{side}"], r[f"ev_yellow_{other}"]
            item["event_red_for"], item["event_red_against"] = r[f"ev_red_{side}"], r[f"ev_red_{other}"]
            team_rows.append(item)
    write_csv(HERE / "cn_team_matches.csv", team_rows)
    for season in sorted(actual):
        print(f"{season}: matches={actual[season]} team_rows={actual[season]*2}")
    print(f"matches={len(rows)} team_rows={len(team_rows)}")


if __name__ == "__main__":
    main()
