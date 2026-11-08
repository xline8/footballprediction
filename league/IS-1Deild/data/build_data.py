"""Build the Iceland 1. Deild Phase A analysis tables.

This builder reads the shared FotMob index and payloads, keeps scoreStr as
the official full-time target, and derives only event-backed first-half and
red-family counts.  No stats or shotmap values are imputed or invented.
"""
import csv
import json
from collections import Counter
from pathlib import Path

MAIN_REPO = Path("/home/hatch/workspace/footballprediction")
INDEX = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
OUT = Path(__file__).resolve().parent
LEAGUE_ID = "216"


def payload_path(relative):
    p = Path(relative)
    return p if p.is_absolute() else MAIN_REPO / p


def event_list(content):
    return (((content.get("matchFacts") or {}).get("events") or {}).get("events") or [])


def phase(general):
    # Frozen Phase A rule: either explicit Promotion Playoff league name or
    # its FotMob round labels marks a playoff; all other rows are regular.
    lname = general.get("leagueName") or ""
    rname = general.get("leagueRoundName") or ""
    return "playoff" if "Promotion Playoff" in lname or rname in ("1/2", "final") else "regular"


def score_pair(score):
    try:
        left, right = (x.strip() for x in score.split("-", 1))
        return int(left), int(right)
    except (AttributeError, ValueError):
        raise ValueError(f"unparseable scoreStr: {score!r}")


def main():
    with INDEX.open() as fh:
        index_rows = [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]
    index_rows.sort(key=lambda r: (r["date"], r["match_id"]))
    matches = []
    mismatch_ids = []
    for ir in index_rows:
        with payload_path(ir["path"]).open() as fh:
            data = json.load(fh)
        general = data.get("general") or {}
        status = (data.get("header") or {}).get("status") or {}
        if not status.get("finished") or status.get("cancelled"):
            continue
        home = general.get("homeTeam") or {}
        away = general.get("awayTeam") or {}
        if not home or not away:
            raise ValueError(f"216 payload missing team block: {ir['match_id']}")
        content = data.get("content") or {}
        events = event_list(content)
        home_goals, away_goals = score_pair(status.get("scoreStr"))
        goals = [e for e in events if e.get("type") == "Goal"]
        ht_home = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome") is True)
        ht_away = sum(1 for e in goals if e.get("time") is not None and e["time"] <= 45 and e.get("isHome") is False)
        reds = [e for e in events if e.get("type") == "Card" and e.get("card") in ("Red", "YellowRed")]
        periods = ((content.get("stats") or {}).get("Periods") or {})
        rec = {
            "match_id": ir["match_id"], "league": "IS-1Deild", "season": ir["season"], "date": ir["date"],
            "round": str(general.get("matchRound") or ""), "league_round_name": general.get("leagueRoundName") or "",
            "phase": phase(general), "league_name": general.get("leagueName") or "",
            "home_team_id": home.get("id"), "home_team": home.get("name") or "",
            "away_team_id": away.get("id"), "away_team": away.get("name") or "",
            "coverage_level": general.get("coverageLevel") or "", "home_goals": home_goals, "away_goals": away_goals,
            "ht_home_goals": ht_home if events else "", "ht_away_goals": ht_away if events else "",
            "ht_source": "events" if events else "none",
            "ev_red_home": sum(1 for e in reds if e.get("isHome") is True),
            "ev_red_away": sum(1 for e in reds if e.get("isHome") is False),
            "goals_1h_total": ht_home + ht_away if events else "",
            "referee": (((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}).get("text") or "",
            "has_stats_all": 0, "has_stats_half": 0,
            "has_extra_time": int(any("Extra" in str(p) for p in periods)),
            "has_events": int(bool(events)),
        }
        for side in ("home", "away"):
            for key, default in (("sm_shots", 0), ("sm_sot", 0), ("sm_xg", 0),
                                 ("sm_xgot", 0), ("sm_xgot_n", 0), ("sm_shots_fh", 0)):
                rec[f"{key}_{side}"] = default
        event_goals = (sum(1 for e in goals if e.get("isHome") is True), sum(1 for e in goals if e.get("isHome") is False))
        if event_goals != (home_goals, away_goals):
            mismatch_ids.append(ir["match_id"])
        matches.append(rec)
    assert len(matches) == len(index_rows) == 812
    assert len({r["match_id"] for r in matches}) == 812
    assert mismatch_ids == ["3794991"]
    fields = list(matches[0])
    with (OUT / "is1_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields); writer.writeheader(); writer.writerows(matches)
    team_rows = []
    for m in matches:
        for side, opp, venue in (("home", "away", "home"), ("away", "home", "away")):
            team_rows.append({
                "match_id": m["match_id"], "league": m["league"], "season": m["season"], "date": m["date"],
                "phase": m["phase"], "team_id": m[f"{side}_team_id"], "team": m[f"{side}_team"], "venue": venue,
                "goals_for": m[f"{side}_goals"], "goals_against": m[f"{opp}_goals"],
                "ht_goals_for": m[f"ht_{side}_goals"], "ht_goals_against": m[f"ht_{opp}_goals"],
            })
    with (OUT / "is1_team_matches.csv").open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(team_rows[0])); writer.writeheader(); writer.writerows(team_rows)
    print("matches", len(matches), "team_rows", len(team_rows))
    print("season_counts", dict(Counter(r["season"] for r in matches)))
    print("phase_counts", dict(Counter(r["phase"] for r in matches)))
    print("eventless", sum(not r["has_events"] for r in matches), "mismatch", mismatch_ids)


if __name__ == "__main__":
    main()
