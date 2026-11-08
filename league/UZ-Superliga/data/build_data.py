"""Build the Uzbekistan Superliga scores-only match table from FotMob JSONs."""

import argparse
import csv
import json
import os
from collections import Counter
from pathlib import Path

LEAGUE_ID = "540"
EXPECTED_ROWS = 215
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
INDEX_NAME = "data_enrichment/fotmob_world_index.csv"


def find_warehouse():
    candidates = [REPO, Path(os.path.expanduser("~/workspace/footballprediction"))]
    for root in candidates:
        index = root / INDEX_NAME
        if not index.is_file():
            continue
        with index.open(newline="") as fh:
            rows = list(csv.DictReader(fh))
        if rows and (root / rows[0]["path"]).is_file():
            return root, index
    raise FileNotFoundError("FotMob warehouse not found (index plus payloads required)")


def index_rows(index_path):
    with index_path.open(newline="") as fh:
        return [r for r in csv.DictReader(fh) if r["league_id"] == LEAGUE_ID]


def halftime_score(payload, hg, ag):
    """HT score from the matchFacts Half event, or (None, None).

    The Half event at minute 45 carries homeScore/awayScore = the HT
    score. Validated per match: exactly one HT Half event, 0 <= HT <= FT
    on both sides, and the count of Goal events equals the FT goal total.
    Coverage is partial (99/215) and late-season only (rounds 10, 14-27);
    absence is recorded as blank, never imputed.
    """
    events = ((payload.get("content") or {}).get("matchFacts") or {}).get("events") or {}
    evs = events.get("events") or []
    if not evs:
        return None, None
    ht = [e for e in evs if e.get("type") == "Half" and e.get("halfStrShort") == "HT"]
    goals = [e for e in evs if e.get("type") == "Goal"]
    if len(ht) != 1 or len(goals) != hg + ag:
        return None, None
    hs, aws = ht[0].get("homeScore"), ht[0].get("awayScore")
    if not (isinstance(hs, int) and isinstance(aws, int)):
        return None, None
    if not (0 <= hs <= hg and 0 <= aws <= ag):
        return None, None
    return hs, aws


def payload_flags(payload):
    content = payload.get("content") or {}
    events = ((content.get("matchFacts") or {}).get("events") or {}).get("events") or []
    shotmap = (content.get("shotmap") or {}).get("shots") or []
    referee = ((content.get("matchFacts") or {}).get("infoBox") or {}).get("Referee") or {}
    periods = (content.get("stats") or {}).get("Periods") or {}
    return {
        "stats_null": content.get("stats") is None,
        "shotmap_empty": not shotmap,
        "events_empty": not events,
        "referee_blank": not any(referee.get(k) for k in ("text", "country", "countryCode")),
        "period_splits_present": bool(periods and any(p != "All" for p in periods)),
        "lineup_present": bool(content.get("lineup")),
    }


def read_matches(rows, warehouse):
    out = []
    payloads = []
    for index_row in rows:
        path = warehouse / index_row["path"]
        with path.open() as fh:
            payload = json.load(fh)
        payloads.append(payload)
        general = payload["general"]
        header = payload["header"]
        status = header["status"]
        assert status.get("finished") is True, f"unfinished match {index_row['match_id']}"
        teams = header["teams"]
        hg, ag = int(teams[0]["score"]), int(teams[1]["score"])
        assert f"{hg}-{ag}" == index_row["score"], f"score mismatch {index_row['match_id']}"
        round_no = int(general["matchRound"])
        result = "H" if hg > ag else "A" if hg < ag else "D"
        ht_hg, ht_ag = halftime_score(payload, hg, ag)
        out.append({
            "match_id": index_row["match_id"],
            "date": index_row["date"],
            "round": round_no,
            "home": general["homeTeam"]["name"],
            "away": general["awayTeam"]["name"],
            "home_goals": hg,
            "away_goals": ag,
            "total_goals": hg + ag,
            "result": result,
            "home_goals_ht": "" if ht_hg is None else ht_hg,
            "away_goals_ht": "" if ht_ag is None else ht_ag,
        })
    out.sort(key=lambda r: (r["date"], int(r["match_id"])))
    assert len(out) == EXPECTED_ROWS, f"UZ rows changed: {len(out)} != {EXPECTED_ROWS}"
    return out, payloads


def print_verify(rows, payloads):
    flags = [payload_flags(p) for p in payloads]
    print(f"payloads: {len(payloads)}")
    for key in flags[0]:
        print(f"{key}: {sum(f[key] for f in flags)}/{len(flags)}")
    print(f"halftime_score_derivable: {sum(1 for r in rows if r['home_goals_ht'] != '')}/{len(rows)}")
    print("round matches")
    for rnd, n in sorted(Counter(r["round"] for r in rows).items()):
        print(f"{rnd}: {n}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--verify", action="store_true", help="print payload coverage and round counts")
    args = parser.parse_args()
    warehouse, index_path = find_warehouse()
    rows = index_rows(index_path)
    assert len(rows) == EXPECTED_ROWS, f"index rows changed: {len(rows)} != {EXPECTED_ROWS}"
    matches, payloads = read_matches(rows, warehouse)
    out_path = HERE / "uz_superliga_matches.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(matches[0]))
        writer.writeheader()
        writer.writerows(matches)
    print(f"warehouse: {warehouse}")
    print(f"wrote {len(matches)} matches to {out_path}")
    if args.verify:
        print_verify(matches, payloads)


if __name__ == "__main__":
    main()
