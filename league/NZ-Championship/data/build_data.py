"""Build the New Zealand Championship Phase A analysis tables."""
import csv
import json
from collections import Counter
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "8870"
EXPECTED_ET = {"2024", "2025"}


def payload_path(relative):
    p = Path(relative)
    return p if p.is_absolute() else MAIN_REPO / p


def events_from(content):
    return (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])


def score_pair(score):
    left, right = (x.strip() for x in score.split("-", 1))
    return int(left), int(right)


def main():
    with INDEX.open() as fh:
        index_rows = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    matches, event_mismatches, all_time_mismatches, extra_time = [], [], [], []
    for ir in index_rows:
        data = json.load(payload_path(ir["path"]).open())
        general = data.get("general") or {}
        status = (data.get("header") or {}).get("status") or {}
        if not status.get("finished") or status.get("cancelled"):
            continue
        home, away = general.get("homeTeam") or {}, general.get("awayTeam") or {}
        if not home or not away:
            raise ValueError(f"8870 payload missing team block: {ir['match_id']}")
        content = data.get("content") or {}
        events = events_from(content)
        goals = [e for e in events if e.get("type") == "Goal"]
        recorded = score_pair(status.get("scoreStr"))
        reg = tuple(sum(1 for e in goals if e.get("isHome") is side and e.get("time") is not None and e["time"] <= 90) for side in (True, False))
        all_time = tuple(sum(1 for e in goals if e.get("isHome") is side) for side in (True, False))
        shootout = any(e.get("type") == "PenaltyShootout" for e in events)
        et = any(e.get("time") is not None and e["time"] > 90 for e in goals) or shootout
        if events and reg != recorded:
            event_mismatches.append(ir["match_id"])
        if events and all_time != recorded:
            all_time_mismatches.append(ir["match_id"])
        if et:
            extra_time.append(ir["match_id"])
        ht_home = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome") is True)
        ht_away = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome") is False)
        reds = [e for e in events if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed")]
        r = {
            "match_id": ir["match_id"], "league": "NZ-Championship", "season": ir["season"], "date": ir["date"],
            "round": str(general.get("matchRound") or ""), "league_round_name": general.get("leagueRoundName") or "",
            "phase": "final" if (general.get("leagueRoundName") or "") == "final" else "regular",
            "league_name": general.get("leagueName") or "", "home_team_id": home.get("id"), "home_team": home.get("name") or "",
            "away_team_id": away.get("id"), "away_team": away.get("name") or "", "coverage_level": general.get("coverageLevel") or "",
            "home_goals": reg[0] if events else recorded[0],
            "away_goals": reg[1] if events else recorded[1],
            "ht_home_goals": ht_home if events else "", "ht_away_goals": ht_away if events else "",
            "ht_source": "events" if events else "none", "ev_red_home": sum(e.get("isHome") is True for e in reds),
            "ev_red_away": sum(e.get("isHome") is False for e in reds), "goals_1h_total": ht_home + ht_away if events else "",
            "referee": "", "has_stats_all": 0, "has_stats_half": 0, "has_extra_time": int(et), "has_events": int(bool(events)),
        }
        for side in ("home", "away"):
            for key in ("sm_shots", "sm_sot", "sm_xg", "sm_xgot", "sm_xgot_n", "sm_shots_fh"):
                r[f"{key}_{side}"] = 0
        matches.append(r)
    # The current warehouse index contains eight 2022 scheduled rows whose
    # payloads are still unfinished and have no scoreStr.  The frozen rule
    # keeps only finished, non-cancelled matches, so these are excluded.
    assert len(index_rows) == 229 and len(matches) == 221
    assert Counter(r["season"] for r in matches) == Counter({"2022": 38, "2023": 46, "2024": 46, "2025": 56, "2026": 35})
    assert len({r["match_id"] for r in matches}) == 221
    assert set(extra_time) == {r["match_id"] for r in matches if r["season"] in EXPECTED_ET and r["phase"] == "final"}
    assert {next(r["season"] for r in matches if r["match_id"] == mid) for mid in extra_time} == EXPECTED_ET
    # The two finals differ only for the 90-minute event-derived score;
    # their all-times event goal counts equal the recorded score including ET.
    assert set(event_mismatches) == set(extra_time) and all_time_mismatches == []
    fields = list(matches[0])
    with (OUT / "nz_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields); w.writeheader(); w.writerows(matches)
    team_rows = []
    for m in matches:
        for side, opp, venue in (("home", "away", "home"), ("away", "home", "away")):
            team_rows.append({"match_id": m["match_id"], "league": m["league"], "season": m["season"], "date": m["date"],
                              "phase": m["phase"], "team_id": m[f"{side}_team_id"], "team": m[f"{side}_team"], "venue": venue,
                              "goals_for": m[f"{side}_goals"], "goals_against": m[f"{opp}_goals"],
                              "ht_goals_for": m[f"ht_{side}_goals"], "ht_goals_against": m[f"ht_{opp}_goals"]})
    with (OUT / "nz_team_matches.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(team_rows[0])); w.writeheader(); w.writerows(team_rows)
    print("matches", len(matches), "team_rows", len(team_rows))
    print("season_counts", dict(Counter(r["season"] for r in matches)))
    print("phase_counts", dict(Counter(r["phase"] for r in matches)))
    print("eventless", sum(not r["has_events"] for r in matches), "event_mismatches", event_mismatches, "extra_time", extra_time)


if __name__ == "__main__":
    main()
