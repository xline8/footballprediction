"""Pembersihan final: sel mustahil -> kosong (missing), TANPA buang baris/outlier asli.
Output: all_matches_clean.csv + verifikasi ulang."""
import os
import csv
from collections import defaultdict

# Direktori dari paths (sumber kebenaran tunggal), pola yang sama
# dengan download.py: hardcode ~/football-data hanya sama dengan
# lokasi proyek berkat symlink deployment (audit ronde 9).
try:
    from paths import BASE, DATA_CLEAN as DST, DATA_RAW as SRC
except Exception:
    BASE = os.path.join(os.path.expanduser("~"), "football-data")
    SRC = os.path.join(BASE, "all_matches.csv")
    DST = os.path.join(BASE, "all_matches_clean.csv")

def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None

# rentang sah per kolom; None = kolom odds (harus >1.0)
RANGES = {
    "HS": (0, 50), "AS": (0, 50), "HST": (0, 40), "AST": (0, 40),
    "HC": (0, 30), "AC": (0, 30), "HF": (0, 45), "AF": (0, 45),
    "HY": (0, 12), "AY": (0, 12), "HR": (0, 6), "AR": (0, 6),
}


def clean():
    """Bangun ulang all_matches_clean.csv dari all_matches.csv. Return dict."""
    with open(SRC, encoding="utf-8", newline="") as f:
        header = next(csv.reader(f))

    # kolom odds: diakhiri H/D/A (huruf besar) atau mengandung >/< — kolom UKURAN handicap dikecualikan
    ODDS_COLS = sorted(
        c for c in header
        if (c.endswith(("H", "D", "A")) or ">" in c or "<" in c)
        and not c.endswith(("AH", "AHh")) and c != "AHh"
        and c not in RANGES and c not in ("Div", "Season", "Date", "Time",
                                          "HomeTeam", "AwayTeam", "FTHG", "FTAG", "FTR")
    )

    fixes = defaultdict(int)
    rows = []
    with open(SRC, encoding="utf-8", newline="") as f:
        rdr = csv.DictReader(f)
        fieldnames = rdr.fieldnames
        for r in rdr:
            # 1) statistik mustahil -> kosongkan pasangannya
            for tot, tgt in (("HS", "HST"), ("AS", "AST")):
                v_t, v_g = num(r[tot]), num(r[tgt])
                if v_t is not None and v_g is not None and v_g > v_t:
                    r[tot] = ""; r[tgt] = ""; fixes[f"{tgt}>{tot}"] += 1
            # 2) rentang tidak sah
            for c, (lo, hi) in RANGES.items():
                v = num(r[c])
                if v is not None and not (lo <= v <= hi):
                    r[c] = ""; fixes[f"{c} luar rentang"] += 1
            # 3) odds: decimal odds harus >1.0; AHh (ukuran handicap) tidak disentuh
            for c in ODDS_COLS:
                v = num(r[c])
                if v is not None and not (1.0 < v < 101):
                    r[c] = ""; fixes[f"odds {c}"] += 1
            rows.append(r)

    with open(DST, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"diperbaiki/jadikan missing: {sum(fixes.values())} sel")
    for k, v in sorted(fixes.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")
    print(f"baris: {len(rows):,} (tidak ada baris dibuang)")

    # ===== verifikasi ulang aturan pada file bersih =====
    viol = 0
    for r in rows:
        hs, hst = num(r["HS"]), num(r["HST"])
        if hs is not None and hst is not None and hst > hs: viol += 1
        aso, ast = num(r["AS"]), num(r["AST"])
        if aso is not None and ast is not None and ast > aso: viol += 1
        for c, (lo, hi) in RANGES.items():
            v = num(r[c])
            if v is not None and not (lo <= v <= hi): viol += 1
        for c in ODDS_COLS:
            v = num(r[c])
            if v is not None and not (1.0 < v < 101): viol += 1
        h, a = num(r["FTHG"]), num(r["FTAG"])
        if h is None or a is None: viol += 1
    print(f"\nVERIFIKASI: baris {len(rows):,} | pelanggaran sisa: {viol}")

    # cek baris penting tidak hilang
    venlo = [r for r in rows if r["HomeTeam"] == "VVV Venlo" and r["AwayTeam"] == "Ajax"
             and r["Date"] == "2020-10-24"]
    if venlo:
        r = venlo[0]
        print(f"cek outlier asli dipertahankan: {r['HomeTeam']} {r['FTHG']}-{r['FTAG']} {r['AwayTeam']} OK")
    print(f"\nfile bersih: {DST} ({os.path.getsize(DST)/1e6:.1f} MB)")

    return {"rows": len(rows), "violations": viol}


if __name__ == "__main__":
    clean()
