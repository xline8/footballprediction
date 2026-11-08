"""K-CO referee-gate recheck (watchdog resume 2026-11-12 ~12:58 WIB).

Mirrors league/runner/run_daily.py::_cards_referees exactly:
upcoming CO-PrimeraA fixtures from the FotMob leagues endpoint
(season "2026 - Clausura", fotmob_id 274), referee first from the
fixture payload, else matchDetails infoBox "Referee".

Gate rule (user decision 2026-11-11 19:47): when >=1 upcoming
fixture carries a named referee, run the standard join proof and
join K-CO cards X8 as PROVISIONAL. Otherwise K-CO stays
HELD-BY-REFEREE-GATE.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "data_enrichment"))
sys.path.insert(0, str(ROOT / "league"))

import httpx  # noqa: E402
import pull_fotmob_world as world_pull  # noqa: E402
from stealth import proxy_url  # noqa: E402

LEAGUE_ID = 274
CCODE = "COL"
SEASON = "2026 - Clausura"


def main():
    out = {"checked_at_wib": "2026-11-12 ~12:58", "season": SEASON,
           "league_id": LEAGUE_ID, "fixtures": []}
    with httpx.Client(headers=world_pull.HEADERS, timeout=60,
                      follow_redirects=True, proxy=proxy_url()) as client:
        payload = world_pull.get(client, "leagues",
                                 {"id": LEAGUE_ID, "ccode3": CCODE,
                                  "season": SEASON}, 0.0)
        fixtures = ((payload.get("fixtures") or {}).get("allMatches") or [])
        upcoming = []
        for f in fixtures:
            s = f.get("status") or {}
            if not s.get("finished") and not s.get("cancelled"):
                upcoming.append(f)
        out["n_upcoming"] = len(upcoming)
        for f in upcoming:
            mid = int(f["id"])
            ref = str(f.get("referee") or "").strip()
            source = "fixture"
            if not ref:
                try:
                    p = world_pull.get(client, "matchDetails",
                                       {"matchId": mid}, 0.0)
                    box = (((p.get("content") or {}).get("matchFacts") or {})
                           .get("infoBox") or {})
                    ref = str((box.get("Referee") or {}).get("text") or "").strip()
                    source = "matchDetails"
                except Exception as exc:  # noqa: BLE001
                    ref, source = "", f"error: {exc!r}"
            out["fixtures"].append({
                "match_id": mid,
                "date": str((f.get("status") or {}).get("utcTime") or "")[:10],
                "home": (f.get("home") or {}).get("name") or "",
                "away": (f.get("away") or {}).get("name") or "",
                "round": f.get("round"),
                "referee": ref, "source": source})
    named = [x for x in out["fixtures"] if x["referee"]]
    out["n_named_referee"] = len(named)
    out["gate_pass"] = len(named) >= 1
    dest = Path(__file__).with_name("recheck_2026-11-12_1258.json")
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                    encoding="utf-8")
    print(f"upcoming={out['n_upcoming']} named_referee={len(named)} "
          f"gate_pass={out['gate_pass']}")
    for x in out["fixtures"]:
        print(f"  {x['date']} {x['match_id']} {x['home']} vs {x['away']} "
              f"round={x['round']} referee={x['referee']!r} ({x['source']})")


if __name__ == "__main__":
    main()
