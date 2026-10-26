# -*- coding: utf-8 -*-
"""score_ledger.py — grade picks pending dgn hasil aktual; append grades.jsonl.

- Hasil dibaca dari xg_raw/{SLUG}_2026_all.json (Understat, hasil + fixture),
  nama tim dipetakan balik FD->UG via map_full.json.
- Settle memakai odds_open yang TERSIMPAN saat pick dibuat (jujur: harga yang
  memang bisa diambil ketika pick lahir) — bukan harga closing belakangan.
- odds_close (penanda tambahan) diambil dari raw/{div}_2627.csv bila sudah ada
  (kolom PSC*/AvgC>2.5) — hanya buat pelaporan, tidak mengubah settle.
- Append-only: pick_id yang sudah di-grade di-skip. Idempoten.
"""
import csv
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

PROJ = r"C:/Users/Arif Wicaksono/football-data"
LEDGER = os.path.join(PROJ, "ledger")
PICKS = os.path.join(LEDGER, "picks.jsonl")
GRADES = os.path.join(LEDGER, "grades.jsonl")
SUMMARY = os.path.join(LEDGER, "ledger_summary.json")
SLUG = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
        "I1": "Serie_A", "F1": "Ligue_1"}
CLOSE_COLS = ("PSCH", "PSCD", "PSCA", "AvgC>2.5")

with open(os.path.join(PROJ, "xg_raw", "map_full.json"), encoding="utf-8") as f:
    NMAP = json.load(f)
fd2ug = {}
for k, v in NMAP.items():
    div, ug = k.split("|", 1)
    fd2ug.setdefault(div, {})[v] = ug

# hasil: {(div, date, home_ug, away_ug) -> (yh, ya)}
results = {}
for div, slug in SLUG.items():
    p = os.path.join(PROJ, "xg_raw", f"{slug}_2026_all.json")
    if not os.path.exists(p):
        continue
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        if not d.get("isResult") or d.get("goals", {}).get("h") is None:
            continue
        date = d["datetime"][:10]
        results[(div, date, d["h"]["title"], d["a"]["title"])] = \
            (d["goals"]["h"], d["goals"]["a"])

# odds closing (ref): raw/{div}_2627.csv dd/mm/yyyy
close_ref = {}
for div in SLUG:
    p = os.path.join(PROJ, "raw", f"{div}_2627.csv")
    if not os.path.exists(p):
        continue
    with open(p, encoding="utf-8", errors="replace") as f:
        for r in csv.DictReader(f):
            try:
                dt = datetime.strptime((r.get("Date") or "").strip(), "%d/%m/%Y").date()
            except ValueError:
                continue
            k = (div, dt.isoformat(), (r.get("HomeTeam") or "").strip(),
                 (r.get("AwayTeam") or "").strip())
            close_ref[k] = {c: r.get(c) for c in CLOSE_COLS}

if not os.path.exists(PICKS):
    raise SystemExit("picks.jsonl belum ada")
with open(PICKS, encoding="utf-8") as f:
    picks = [json.loads(l) for l in f if l.strip()]
graded_ids = set()
if os.path.exists(GRADES):
    with open(GRADES, encoding="utf-8") as f:
        for l in f:
            if l.strip():
                graded_ids.add(json.loads(l)["pick_id"])


def settle(market, side, yh, ya, odds):
    if market == "1X2":
        wk = "H" if yh > ya else ("A" if ya > yh else "D")
        return (odds if side == wk else 0.0), (side == wk)
    over = (yh + ya) > 2.5
    return (odds if (side == "Over" and over) else
            0.0 if side == "Over" else odds if not over else 0.0), \
        (over if side == "Over" else not over)


new_grades = []
for pk in picks:
    if pk["pick_id"] in graded_ids:
        continue
    home_ug = fd2ug.get(pk["div"], {}).get(pk["home"])
    away_ug = fd2ug.get(pk["div"], {}).get(pk["away"])
    res = results.get((pk["div"], pk["date"], home_ug, away_ug)) if home_ug and away_ug else None
    if res is None:
        continue  # belum main / belum keluar hasilnya
    yh, ya = res
    ret, won = settle(pk["market"], pk["side"], yh, ya, pk["odds_open"])
    cr = close_ref.get((pk["div"], pk["date"], pk["home"], pk["away"])) or {}
    new_grades.append({
        "pick_id": pk["pick_id"],
        "graded_ts": datetime.now(timezone.utc).isoformat(),
        "result": "win" if won else "loss",
        "yh": yh, "ya": ya,
        "ret_open": round(ret, 4),
        "odds_close_1x2": [cr.get("PSCH"), cr.get("PSCD"), cr.get("PSCA")],
        "odds_close_o25": cr.get("AvgC>2.5"),
    })

if new_grades:
    with open(GRADES, "a", encoding="utf-8") as f:
        for g in new_grades:
            f.write(json.dumps(g, ensure_ascii=False) + "\n")

# ------- ringkasan
by_graded = {g["pick_id"]: g for g in new_grades}
with open(GRADES, encoding="utf-8") as f:
    all_grades = [json.loads(l) for l in f if l.strip()]
gmap = {g["pick_id"]: g for g in all_grades}
agg = defaultdict(lambda: dict(n=0, prof=0.0))
for pk in picks:
    g = gmap.get(pk["pick_id"])
    if not g:
        continue
    a = agg[pk["market"]]
    a["n"] += 1
    a["prof"] += g["ret_open"] - 1.0
summary = {
    "graded_ts": datetime.now(timezone.utc).isoformat(),
    "n_picks": len(picks), "n_graded": len(all_grades), "n_pending": len(picks) - len(all_grades),
    "markets": {m: {"n": a["n"], "profit": round(a["prof"], 2),
                    "roi": round(a["prof"] / a["n"], 4) if a["n"] else None}
                for m, a in agg.items()},
    "note": "Settle di odds_open saat pick lahir (flat 1 unit; odds_close hanya pelaporan).",
}
with open(SUMMARY, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"graded baru: {len(new_grades)} | total graded: {len(all_grades)} | pending: {summary['n_pending']}")
for m, a in summary["markets"].items():
    print(f"  {m}: n={a['n']} ROI={a['roi']*100 if a['roi'] is not None else 0:.2f}%" if a["roi"] is not None
          else f"  {m}: n={a['n']}")
for g in new_grades[:5]:
    print("  *", g["pick_id"], g["result"], "ret=", g["ret_open"])
