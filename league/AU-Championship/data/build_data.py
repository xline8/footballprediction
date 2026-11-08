"""Build the AU-Championship analysis CSV (scores only).

Scope (frozen from payloads, see analysis/DATA_UNDERSTANDING.md):
FotMob parent id 8938 is a CONTAINER of ten competitions. This builder
takes ONLY the true Australian Championship — payload
``general.leagueName`` starting with "Australian Championship"
(group stage Grp. A-D + Final Stage) — and drops the nine state
NPL leagues that share the parent id. No state-league row enters the
CSV: the state competitions are disjoint (no cross-state play), their
scores are ~50% unrecorded (finished=False, recorded 0-0), and they
are separate competitions, not this league.

Output: league/AU-Championship/data/au_championship_matches.csv
(one row per finished Championship match; gitignored by repo norm —
regenerate with this script).

Warehouse resolution: <repo-root>/data_enrichment/... first (the
normal layout once this league dir is merged into the main repo);
fallback to ~/workspace/footballprediction/data_enrichment/... so the
script also runs from a build worktree, which does not carry the
(untracked) warehouse.
"""

import csv
import json
import os
import sys

LEAGUE_ID = "8938"
CHAMP_PREFIX = "Australian Championship"


def find_warehouse():
    here = os.path.dirname(os.path.abspath(__file__))
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(here)))
    candidates = [
        repo_root,
        os.path.expanduser("~/workspace/footballprediction"),
    ]
    for cand in candidates:
        index = os.path.join(cand, "data_enrichment", "fotmob_world_index.csv")
        if not os.path.isfile(index):
            continue
        # The index CSV is tracked, but the 24 GB of payload JSONs are
        # untracked warehouse data: a candidate only counts if a payload
        # actually resolves under it (a bare worktree has the index
        # without the JSONs).
        with open(index, newline="") as f:
            first = next(csv.DictReader(f))
        if os.path.isfile(os.path.join(cand, first["path"])):
            return cand, index
    raise FileNotFoundError(
        "warehouse (index + payloads) not found under: "
        + ", ".join(candidates)
    )


def main():
    warehouse, index_path = find_warehouse()
    out_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "au_championship_matches.csv",
    )
    rows = []
    skipped_state = 0
    with open(index_path, newline="") as f:
        index = [r for r in csv.DictReader(f) if r["league_id"] == LEAGUE_ID]
    assert len(index) == 1333, f"parent 8938 rows changed: {len(index)} != 1333"
    for r in index:
        payload = json.load(open(os.path.join(warehouse, r["path"])))
        g = payload["general"]
        name = g.get("leagueName") or ""
        if not name.startswith(CHAMP_PREFIX):
            skipped_state += 1
            continue
        status = payload["header"]["status"]
        assert status.get("finished"), f"unfinished champ match {r['match_id']}"
        teams = payload["header"]["teams"]
        hg, ag = int(teams[0]["score"]), int(teams[1]["score"])
        assert f"{hg}-{ag}" == r["score"], f"score mismatch {r['match_id']}"
        phase = "final" if "Final Stage" in name else "group"
        group = "" if phase == "final" else name.rsplit("Grp. ", 1)[-1]
        halfs = status.get("halfs") or {}
        rows.append(
            {
                "match_id": r["match_id"],
                "season": r["season"],
                "date": r["date"],
                "phase": phase,
                "group": group,
                "round": g.get("leagueRoundName") or "",
                "home_team": g["homeTeam"]["name"],
                "away_team": g["awayTeam"]["name"],
                "home_goals": hg,
                "away_goals": ag,
                "total_goals": hg + ag,
                "home_win": int(hg > ag),
                "draw": int(hg == ag),
                "away_win": int(hg < ag),
                "over_2_5": int(hg + ag > 2.5),
                "extra_time": int(bool(halfs.get("firstExtraHalfStarted"))),
                # Shootout decided the match (whoLostOnPenalties set).
                # NOTE: this conflates two different things by design of
                # the competition — 2025: only the QF tie (after ET);
                # 2026: ALL 8 drawn group matches went to a shootout
                # with NO extra time (format change; the stored score
                # is still the drawn score, the shootout decides a
                # bonus point, not the 1X2 result). See EDA.md.
                "shootout": int(bool(status.get("whoLostOnPenalties"))),
            }
        )
    rows.sort(key=lambda x: (x["date"], x["match_id"]))
    assert len(rows) == 87, f"championship rows changed: {len(rows)} != 87"
    assert skipped_state == 1246, f"state rows changed: {skipped_state} != 1246"
    with open(out_path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n25 = sum(1 for x in rows if x["season"] == "2025")
    n26 = sum(1 for x in rows if x["season"] == "2026")
    print(f"warehouse: {warehouse}")
    print(f"parent 8938 rows: 1333; state rows skipped: {skipped_state}")
    print(f"championship rows written: {len(rows)} (2025: {n25}, 2026: {n26})")
    print(f"output: {out_path}")
    for season in ("2025", "2026"):
        sub = [x for x in rows if x["season"] == season]
        mg = sum(x["total_goals"] for x in sub) / len(sub)
        ov = sum(x["over_2_5"] for x in sub) / len(sub)
        print(f"  {season}: n={len(sub)} mean_goals={mg:.3f} over2.5={ov:.3f}")


if __name__ == "__main__":
    sys.exit(main())
