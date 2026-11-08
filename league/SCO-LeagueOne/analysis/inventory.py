"""Inventory every Scotland League One (FotMob 124) warehouse payload.

Extraction only: no fitting, no imputation. The warehouse lives in the
main footballprediction checkout (gitignored payloads are absent from
worktrees); this script reads it read-only from there.

Outputs league/SCO-LeagueOne/analysis/inventory_summary.json.
"""
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
MAIN_REPO = Path.home() / "workspace" / "footballprediction"
LEAGUE_ID = "124"


def score(value):
    parts = (value or "0-0").split("-")
    return int(parts[0].strip()), int(parts[1].strip())


def main():
    index = MAIN_REPO / "data_enrichment" / "fotmob_world_index.csv"
    rows = [r for r in csv.DictReader(index.open()) if r["league_id"] == LEAGUE_ID]
    assert len(rows) == 969, len(rows)
    per_season = {}
    stat_keys_all = Counter()
    stat_keys_any = Counter()
    rounds = Counter()
    team_names = defaultdict(set)
    team_ids = set()
    score_mismatch = []
    missing_files = []
    shotmap_shots = Counter()
    detail = defaultdict(list)
    for r in rows:
        p = MAIN_REPO / r["path"]
        if not p.exists():
            missing_files.append(r["match_id"])
            continue
        d = json.loads(p.read_text())
        s = r["season"]
        b = per_season.setdefault(s, {
            "n": 0, "stats_all_n": 0, "stats_any_n": 0, "stats_half_n": 0,
            "events_n": 0, "referee_n": 0, "shotmap_n": 0, "shotmap_shots": 0,
            "lineup_n": 0, "goals": 0, "home_goals": 0,
        })
        b["n"] += 1
        content = d.get("content") or {}
        periods = ((content.get("stats") or {}).get("Periods") or {})
        keys_all = set()
        for period, block in periods.items():
            for group in (block or {}).get("stats", []) or []:
                for stat in group.get("stats", []) or []:
                    keys_all.add(stat.get("key"))
                    stat_keys_any[stat.get("key")] += 1
        if "All" in periods:
            b["stats_all_n"] += 1
            for group in (periods["All"] or {}).get("stats", []) or []:
                for stat in group.get("stats", []) or []:
                    keys_all.add(stat.get("key"))
                    stat_keys_all[stat.get("key")] += 1
        if periods:
            b["stats_any_n"] += 1
        if "FirstHalf" in periods and "SecondHalf" in periods:
            b["stats_half_n"] += 1
        mf = content.get("matchFacts") or {}
        ev = ((mf.get("events") or {}).get("events") or [])
        if ev:
            b["events_n"] += 1
        ref = (((mf.get("infoBox") or {}).get("Referee") or {}).get("text") or "")
        if ref:
            b["referee_n"] += 1
        sm = content.get("shotmap")
        shots = []
        if isinstance(sm, dict):
            shots = sm.get("shots") or []
        elif isinstance(sm, list):
            shots = sm
        if shots:
            b["shotmap_n"] += 1
            b["shotmap_shots"] += len(shots)
            shotmap_shots[s] += len(shots)
        if (content.get("lineup") or {}).get("homeTeam"):
            b["lineup_n"] += 1
        hg, ag = score(r.get("score"))
        b["goals"] += hg + ag
        b["home_goals"] += hg
        hdr = (d.get("header") or {}).get("status") or {}
        pscore = hdr.get("scoreStr")
        if pscore:
            ph, pa = score(pscore)
            if (ph, pa) != (hg, ag):
                score_mismatch.append(r["match_id"])
        gen = d.get("general") or {}
        rnd = str(gen.get("matchRound") or "")
        rounds[(s, rnd)] += 1
        for side in ("homeTeam", "awayTeam"):
            t = gen.get(side) or {}
            if t.get("id") is not None:
                team_ids.add(t["id"])
                team_names[t["id"]].add(t.get("name"))
        # record anomalies
        if not periods:
            detail[s].append(r["match_id"]) if False else None
    out = {
        "n": len(rows),
        "missing_files": missing_files,
        "score_mismatch": score_mismatch,
        "per_season": per_season,
        "stat_keys_all": dict(stat_keys_all),
        "stat_keys_any": dict(stat_keys_any),
        "rounds": {f"{s}|{rnd}": n for (s, rnd), n in sorted(rounds.items())},
        "n_team_ids": len(team_ids),
        "team_ids": sorted(team_ids),
        "team_name_aliases": {str(k): sorted(v) for k, v in sorted(team_names.items()) if len(v) > 1},
        "shotmap_shots_per_season": dict(shotmap_shots),
    }
    for s, b in per_season.items():
        b["goals_per_match"] = round(b["goals"] / b["n"], 4) if b["n"] else None
        b["home_goal_share"] = round(b["home_goals"] / b["goals"], 4) if b["goals"] else None
    (HERE / "inventory_summary.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out, indent=2)[:6000])
    print("missing_files:", len(missing_files), "score_mismatch:", len(score_mismatch))


if __name__ == "__main__":
    main()
