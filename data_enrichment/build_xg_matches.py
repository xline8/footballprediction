#!/usr/bin/env python3
"""build_xg_matches.py — regenerasi xg_raw/xg_matches.csv dari dump musim
Understat yang terversi (xg_raw/<League>_<year>.json).

- Tanpa jaringan, tanpa API-Football. Hanya hasil (isResult).
- Kolom sesuai ekspektasi `features._load_xg_map`: div,datetime,home,away,xgh,xga.
- Bila satu file musim hilang/rusak -> dilewati (tidak menggagalkan pipeline).
- Tidak mengubah model; hanya menyediakan data xG untuk mode fit "blend".
"""
from __future__ import annotations

import csv
import glob
import json
import os
import re
import sys
from datetime import date

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
XGRAW = os.path.join(BASE, "xg_raw")
OUT = os.path.join(XGRAW, "xg_matches.csv")

LEAGUES = {"EPL": "E0", "La_liga": "SP1", "Bundesliga": "D1",
           "Serie_A": "I1", "Ligue_1": "F1"}
COLS = ["div", "datetime", "home", "away", "xgh", "xga"]


def build(out_path=OUT):
    rows = []
    missing = []
    today_year = str(date.today().year)
    cur = {div: 0 for div in LEAGUES.values()}
    for league, div in LEAGUES.items():
        pattern = os.path.join(XGRAW, f"{league}_20*.json")
        for p in sorted(glob.glob(pattern)):
            y = re.search(r"_(\d{4})\.json$", p)
            if not y:
                continue  # bukan dump musim murni (mis. *_all.json / *_fixtures.json)
            try:
                with open(p, encoding="utf-8") as f:
                    data = json.load(f)
            except Exception as e:
                missing.append((os.path.basename(p), str(e)))
                continue
            for m in data:
                if not m.get("isResult") or not m.get("goals", {}).get("h"):
                    continue
                xg = m.get("xG") or {}
                xgh, xga = xg.get("h"), xg.get("a")
                if xgh is None or xga is None:
                    continue
                dt = m.get("datetime", "")
                rows.append({"div": div, "datetime": dt,
                             "home": m["h"]["title"], "away": m["a"]["title"],
                             "xgh": xgh, "xga": xga})
                if dt.startswith(today_year):
                    cur[div] += 1

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        w.writerows(rows)

    per_league = {d: sum(1 for r in rows if r["div"] == d) for d in LEAGUES.values()}
    print(f"build_xg_matches: {len(rows)} rows -> {out_path}")
    for div, n in per_league.items():
        print(f"   {div}: {n} rows | musim ini ({today_year}): {cur[div]}")
    if missing:
        print("   dilewati (file hilang/rusak):")
        for name, err in missing:
            print(f"     - {name}: {err}")
    return {"n_rows": len(rows), "per_league": per_league, "current": cur,
            "missing": missing}


if __name__ == "__main__":
    build()
