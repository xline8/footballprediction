# -*- coding: utf-8 -*-
"""fix_map_2026.py — extend meaping nama tim UG->FD utk tim baru musim 2026/27.

map_full.json hanya mencakup tim yang tampil 2016-2025. Tim promosi baru
(Coventry, Hull, dst.) wajib dipetakan sebelum diprediksi.
Output: xg_raw/map_ext.json ("div|ug" -> fd). TIDAK mengubah map_full.json.
"""
import csv
import difflib
import json
import os
from collections import defaultdict

PROJ = r"C:/Users/Arif Wicaksono/football-data"
SLUG = {"E0": "EPL", "SP1": "La_liga", "D1": "Bundesliga",
        "I1": "Serie_A", "F1": "Ligue_1"}

with open(os.path.join(PROJ, "xg_raw", "map_full.json"), encoding="utf-8") as f:
    NMAP = json.load(f)

# FD names per div (semua musim di all_matches_clean -> supaya balikan juga tim
# yang hanya turun-naik divisi; nama FD stabil lintas musim)
fd_names = defaultdict(set)
with open(os.path.join(PROJ, "all_matches_clean.csv"), encoding="utf-8", errors="replace") as f:
    for r in csv.DictReader(f):
        d = r.get("Div", "")
        if d in SLUG:
            if r.get("HomeTeam"):
                fd_names[d].add(r["HomeTeam"].strip())
            if r.get("AwayTeam"):
                fd_names[d].add(r["AwayTeam"].strip())

# UG names per div dari fixture mendatang
ug_names = defaultdict(set)
for div, slug in SLUG.items():
    p = os.path.join(PROJ, "xg_raw", f"{slug}_2026_fixtures.json")
    with open(p, encoding="utf-8") as f:
        data = json.load(f)
    for d in data:
        ug_names[div].add(d["h"]["title"])
        ug_names[div].add(d["a"]["title"])

ext, unparsed = {}, []
for div in SLUG:
    pool = sorted(fd_names[div])
    for ug in sorted(ug_names[div]):
        key = f"{div}|{ug}"
        if key in NMAP:
            continue
        if ug in pool:
            ext[key] = ug
            continue
        m = difflib.get_close_matches(ug, pool, n=1, cutoff=0.75)
        if m:
            ext[key] = m[0]
        else:
            unparsed.append((div, ug))

with open(os.path.join(PROJ, "xg_raw", "map_ext.json"), "w", encoding="utf-8") as f:
    json.dump(ext, f, ensure_ascii=False, indent=1)

print(f"dipetakan tambahan: {len(ext)}")
for k, v in sorted(ext.items()):
    if k.split("|")[1] != v:
        print("  ", k, "->", v)
if unparsed:
    print("BELUM TERPETAKAN (perlu manual):", unparsed)
else:
    print("semua nama fixture terpetakan; nama identik tidak dicetak")
