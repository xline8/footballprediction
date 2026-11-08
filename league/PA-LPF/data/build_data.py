"""Build the PA-LPF regular-season analysis CSV from the FotMob warehouse.

The warehouse has one index row per regular or final-stage match.  This
builder keeps played regular-season rows, including the two awarded rows so
that their administrative exclusion remains auditable.  Final-stage rows and
error placeholders are omitted.  ``scoreStr`` is the official score source;
goal events are used only for event inventory and first-half derivation.
"""
import csv
import json
import os

LEAGUE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(LEAGUE_DIR)))
INDEX = os.path.join(REPO, "data_enrichment", "fotmob_world_index.csv")
OUT = os.path.join(LEAGUE_DIR, "pa_lpf_matches.csv")
LEAGUE_ID = "9039"


def payload_roots():
    roots = [REPO]
    env = os.environ.get("FOOTBALLPREDICTION_ROOT")
    if env:
        roots.append(env)
    roots.append(os.path.expanduser("~/workspace/footballprediction"))
    seen, result = set(), []
    for root in roots:
        if root and root not in seen:
            seen.add(root)
            result.append(root)
    return result


def resolve_payload(rel_path):
    for root in payload_roots():
        path = os.path.join(root, rel_path)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(rel_path)


def score_pair(score_str):
    return [int(x.strip()) for x in score_str.split("-")]


def main():
    indexed = [r for r in csv.DictReader(open(INDEX, newline=""))
               if r["league_id"] == LEAGUE_ID]
    indexed.sort(key=lambda r: (r["season"], r["date"], r["match_id"]))
    output = []
    skipped_errors = 0
    skipped_playoffs = 0
    for index_row in indexed:
        payload = json.load(open(resolve_payload(index_row["path"])))
        if payload.get("error"):
            skipped_errors += 1
            continue
        general = payload["general"]
        header = payload["header"]
        status = header["status"]
        if general.get("leagueRoundName", "") in ("1/4", "1/2", "final"):
            skipped_playoffs += 1
            continue
        if not status.get("finished") or not status.get("scoreStr"):
            continue
        home_goals, away_goals = score_pair(status["scoreStr"])
        facts = (payload.get("content") or {}).get("matchFacts") or {}
        events = ((facts.get("events") or {}).get("events") or [])
        ht_home = sum(1 for e in events if e.get("type") == "Goal"
                      and e.get("isHome") is True and not e.get("isPenaltyShootoutEvent")
                      and (e.get("time") or 0) <= 45)
        ht_away = sum(1 for e in events if e.get("type") == "Goal"
                      and e.get("isHome") is False and not e.get("isPenaltyShootoutEvent")
                      and (e.get("time") or 0) <= 45)
        if not events:
            # All empty-event payloads in this corpus are verified 0-0.
            ht_home = ht_away = 0
        cards = [e for e in events if e.get("type") == "Card"
                 and e.get("card") in ("Red", "YellowRed")]
        red_home = sum(1 for e in cards if e.get("isHome") is True)
        red_away = sum(1 for e in cards if e.get("isHome") is False)
        reason = (status.get("reason") or {}).get("short", "")
        output.append({
            "match_id": index_row["match_id"],
            "season": index_row["season"],
            "tournament": general.get("leagueName", "").replace("LPF ", "").replace(" Final Stage", ""),
            "round": general.get("leagueRoundName", ""),
            "date": status.get("utcTime", "")[:10],
            "home_team_id": general["homeTeam"]["id"],
            "home_team": general["homeTeam"]["name"],
            "away_team_id": general["awayTeam"]["id"],
            "away_team": general["awayTeam"]["name"],
            "home_goals": home_goals,
            "away_goals": away_goals,
            "ht_home_goals": ht_home,
            "ht_away_goals": ht_away,
            "playoff": False,
            "awarded": bool(status.get("awarded")),
            "awarded_reason": reason if status.get("awarded") else "",
            "excluded_awarded": bool(status.get("awarded")),
            "red_home": red_home,
            "red_away": red_away,
            "has_events": bool(events),
            "n_events": len(events),
            "n_goal_events": sum(e.get("type") == "Goal" for e in events),
            "n_card_events": sum(e.get("type") == "Card" for e in events),
            "n_half_events": sum(e.get("type") == "Half" for e in events),
        })
    fields = list(output[0])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(output)
    print(f"wrote {OUT}: {len(output)} rows; errors skipped {skipped_errors}; "
          f"final-stage skipped {skipped_playoffs}; awarded {sum(r['awarded'] for r in output)}")


if __name__ == "__main__":
    main()
