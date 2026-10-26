"""Cek terakhir sebelum pipeline: konsistensi nama tim ANTAR-divisi (per negara)
supaya Elo/fitur historis klub tidak putus saat promosi-degradasi."""
import os
import csv
import re
import difflib
from collections import defaultdict

DATA = os.path.join(os.path.expanduser("~"), "football-data", "all_matches_clean.csv")
COUNTRY = {
    "ENG": {"E0", "E1", "E2", "E3", "EC"},
    "SCO": {"SC0", "SC1", "SC2", "SC3"},
    "GER": {"D1", "D2"}, "ITA": {"I1", "I2"}, "ESP": {"SP1", "SP2"}, "FRA": {"F1", "F2"},
    "OTH": {"N1", "B1", "P1", "T1", "G1"},
}
DIV2C = {d: c for c, ds in COUNTRY.items() for d in ds}

teams = defaultdict(set)   # negara -> kumpulan nama persis
with open(DATA, encoding="utf-8", newline="") as f:
    for r in csv.DictReader(f):
        c = DIV2C[r["Div"]]
        teams[c].add(r["HomeTeam"])
        teams[c].add(r["AwayTeam"])

def nkey(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

issues_exact = 0
issues_fuzzy = 0
print("== nama multi-varian antar-divisi dalam satu negara ==")
for c, names in sorted(teams.items()):
    groups = defaultdict(set)
    for nm in names:
        groups[nkey(nm)].add(nm)
    for k, variants in sorted(groups.items()):
        if len(variants) > 1:
            issues_exact += 1
            print(f"  [{c}] {sorted(variants)}")
    # fuzzy: pasangan nama hampir identik (kemungkinan ejaan beda, bukan klub beda)
    lst = sorted(names)
    for i, a in enumerate(lst):
        for b in lst[i + 1:]:
            if nkey(a) == nkey(b):
                continue
            ratio = difflib.SequenceMatcher(None, nkey(a), nkey(b)).ratio()
            # ambang longgar + panjang mirip agar tak membanjiri
            if ratio >= 0.86 and abs(len(a) - len(b)) <= 3:
                issues_fuzzy += 1
                print(f"  [fuzzy {c}] '{a}' vs '{b}' (kemiripan {ratio:.2f})")

if issues_exact == 0 and issues_fuzzy == 0:
    print("  TIDAK ADA - nama klub konsisten lintas divisi & lintas musim")
print(f"\nTotal klub: {sum(len(v) for v in teams.values())} | "
      f"per negara: " + " ".join(f"{c}:{len(n)}" for c, n in sorted(teams.items())))
print(f"MASALAH: exact={issues_exact}, fuzzy={issues_fuzzy}")
