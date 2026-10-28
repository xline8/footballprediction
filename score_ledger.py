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

import paths
PROJ = paths.BASE
LEDGER = os.path.join(PROJ, "ledger")
PICKS = os.path.join(LEDGER, "picks.jsonl")
GRADES = os.path.join(LEDGER, "grades.jsonl")
SUMMARY = os.path.join(LEDGER, "ledger_summary.json")
SLUG = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
        "I1": "Serie_A", "F1": "Ligue_1"}
CLOSE_COLS = ("PSCH", "PSCD", "PSCA", "AvgC>2.5")

from football_etl import normalize_name

NMAP = {}
for _fn in ("map_full.json", "map_ext.json"):
    _p = os.path.join(PROJ, "xg_raw", _fn)
    if os.path.exists(_p):
        with open(_p, encoding="utf-8") as f:
            NMAP.update(json.load(f))
fd2ug = {}
for k, v in NMAP.items():
    div, ug = k.split("|", 1)
    fd2ug.setdefault(div, {})[normalize_name(v)] = ug

# hasil: {(div, date, home_ug, away_ug) -> (yh, ya)}
def _load_results(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        if not d.get("isResult") or d.get("goals", {}).get("h") is None:
            continue
        date = d["datetime"][:10]
        out[(date, d["h"]["title"], d["a"]["title"])] = \
            (int(d["goals"]["h"]), int(d["goals"]["a"]))
    return out


results = {}
for div, slug in SLUG.items():
    stem = os.path.join(PROJ, "xg_raw", f"{slug}_2026")
    merged = _load_results(stem + "_all.json")
    # _fixtures.json di-refresh harian dan lebih segar (sampai 10-25);
    # bila kunci sama, hasil fixtures menang.
    merged.update(_load_results(stem + "_fixtures.json"))
    for (date, h, a), g in merged.items():
        results[(div, date, h, a)] = g

# hasil piala dari ta/results.csv (FT): {(competition, date, home_norm, away_norm)}
CUP_COMP = {"England - EFL Cup": "EFL Cup", "Germany - Cup Germany": "DFB Pokal"}
cup_results = {}
_res_path = os.path.join(PROJ, "ta", "results.csv")
if os.path.exists(_res_path):
    with open(_res_path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("status") or "").upper() != "FT":
                continue
            comp = CUP_COMP.get(r.get("league", ""))
            if not comp:
                continue
            sh, sa = r.get("score_h"), r.get("score_a")
            if sh is None or sa is None:
                continue
            cup_results[(comp, r["date"][:10],
                         normalize_name(r["home"]), normalize_name(r["away"]))] = \
                (int(sh), int(sa))

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
unmapped = defaultdict(set)
for pk in picks:
    if pk["pick_id"] in graded_ids:
        continue
    comp = pk.get("competition") or ""
    if comp in ("EFL Cup", "DFB Pokal"):
        # pick piala: hasil dari ta/results.csv (samakan nama)
        res = cup_results.get((comp, pk["date"],
                               normalize_name(pk["home"]), normalize_name(pk["away"])))
        if res is None:
            unmapped[comp].add(f"{pk['home']} v {pk['away']}")
            continue
        yh, ya = res
        ret, won = settle(pk["market"], pk["side"], yh, ya, pk["odds_open"])
        new_grades.append({
            "pick_id": pk["pick_id"], "competition": comp,
            "graded_ts": datetime.now(timezone.utc).isoformat(),
            "result": "win" if won else "loss",
            "yh": yh, "ya": ya,
            "ret_open": round(ret, 4),
            "odds_close_1x2": None, "odds_close_o25": None,
        })
        continue
    home_ug = fd2ug.get(pk["div"], {}).get(pk["home"])
    away_ug = fd2ug.get(pk["div"], {}).get(pk["away"])
    if not home_ug:
        unmapped[pk["div"]].add(f"home={pk['home']}")
    if not away_ug:
        unmapped[pk["div"]].add(f"away={pk['away']}")
    res = results.get((pk["div"], pk["date"], home_ug, away_ug)) if home_ug and away_ug else None
    if res is None:
        continue  # belum main / belum keluar hasilnya
    yh, ya = res
    ret, won = settle(pk["market"], pk["side"], yh, ya, pk["odds_open"])
    cr = close_ref.get((pk["div"], pk["date"], pk["home"], pk["away"])) or {}
    new_grades.append({
        "pick_id": pk["pick_id"], "competition": "",
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
all_grades = []
if os.path.exists(GRADES):
    with open(GRADES, encoding="utf-8") as f:
        all_grades = [json.loads(l) for l in f if l.strip()]
gmap = {g["pick_id"]: g for g in all_grades}
agg = defaultdict(lambda: dict(n=0, prof=0.0))
for pk in picks:
    g = gmap.get(pk["pick_id"])
    if not g:
        continue
    comp = pk.get("competition") or g.get("competition") or "league"
    a = agg[(comp, pk["market"])]
    a["n"] += 1
    a["prof"] += g["ret_open"] - 1.0

competitions = {}
for (comp, market), a in agg.items():
    block = competitions.setdefault(comp, {})
    block[market] = {"n": a["n"], "profit": round(a["prof"], 2),
                     "roi": round(a["prof"] / a["n"], 4) if a["n"] else None}

# ringkasan: blok per kompetisi (liga gabungan + tiap piala)
comp_summary = {}
for comp in ("league", "EFL Cup", "DFB Pokal"):
    block = competitions.get(comp, {})
    n = sum(b["n"] for b in block.values())
    prof = sum(b["profit"] for b in block.values())
    comp_summary[comp] = {
        "n": n,
        "profit": round(prof, 2),
        "roi": round(prof / n, 4) if n else None,
        "markets": block,
    }
summary = {
    "graded_ts": datetime.now(timezone.utc).isoformat(),
    "n_picks": len(picks), "n_graded": len(all_grades), "n_pending": len(picks) - len(all_grades),
    "competitions": comp_summary,
    "note": "Settle di odds_open saat pick lahir (flat 1 unit; odds_close hanya pelaporan). "
            "Ringkasan per kompetisi: liga gabungan (kunci 'league') + tiap piala.",
}
with open(SUMMARY, "w", encoding="utf-8") as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)

print(f"graded baru: {len(new_grades)} | total graded: {len(all_grades)} | pending: {summary['n_pending']}")
if unmapped:
    print("!! tidak terpetakan:")
    for comp, names in sorted(unmapped.items()):
        print(f"   {comp}: {sorted(names)}")
for comp, c in summary["competitions"].items():
    print(f"  [{comp}] n={c['n']} profit={c['profit']}")
    for m, a in c["markets"].items():
        roi = a["roi"]
        print(f"     {m}: n={a['n']} ROI={roi*100 if roi is not None else 0:.2f}%")
for g in new_grades[:5]:
    print("  *", g["pick_id"], g.get("competition", ""), g["result"], "ret=", g["ret_open"])
