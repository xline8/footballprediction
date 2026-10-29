"""Gabungkan & bersihkan semua CSV football-data -> all_matches.csv + laporan kualitas."""
import os
import csv
import re
from collections import Counter, defaultdict
from datetime import datetime

RAW = os.path.join(os.path.expanduser("~"), "football-data", "raw")
OUTD = os.path.join(os.path.expanduser("~"), "football-data")

FRONT = ["Div", "Season", "Date", "Time", "HomeTeam", "AwayTeam",
         "FTHG", "FTAG", "FTR", "HTHG", "HTAG", "HTR",
         "HS", "AS", "HST", "AST", "HC", "AC", "HF", "AF",
         "HY", "AY", "HR", "AR", "Referee"]

# padanan nama yang identik namun beda tulis (aman digabung)
CANON = {
    "spal": "Spal", "paris sg": "Paris SG", "paris s-g": "Paris SG",
    "nott'm forest": "Nottingham Forest", "nottm forest": "Nottingham Forest",
    "wolves": "Wolverhampton", "wolverhampton wanderers": "Wolverhampton",
    "man utd": "Man United", "man city": "Man City", "newcastle utd": "Newcastle",
    "st etienne": "St Etienne", "saint etienne": "St Etienne",
    "ath madrid": "Ath Madrid", "ath bilbao": "Ath Bilbao",
    "sporting cp": "Sporting CP", "sp,portugal": "Sporting CP",
}


def rows_of(path):
    raw = open(path, "rb").read()
    if raw[:3] == b"\xef\xbb\xbf":
        raw = raw[3:]
    try:
        text = raw.decode("utf-8")
        if "�" in text:
            raise UnicodeError
    except UnicodeError:
        text = raw.decode("latin-1", errors="replace")
    return list(csv.reader(text.splitlines()))


def prepare():
    """Bangun ulang all_matches.csv dari CSV raw. Return dict ringkasan."""
    files = sorted(f for f in os.listdir(RAW) if f.endswith(".csv"))
    seen_headers = Counter()
    row_count_in = 0
    name_groups = defaultdict(dict)                # div -> normalisasi-nama -> varian
    btts_cols = set()

    records = []
    for fn in files:
        m = re.match(r"([A-Z0-9]+)_(\d{4})\.csv$", fn)
        if not m:
            continue
        div, se = m.group(1), m.group(2)
        season = f"20{se[:2]}/{se[2:]}"
        rows = rows_of(os.path.join(RAW, fn))
        if not rows:
            continue
        hdr = [h.strip() for h in rows[0]]
        seen_headers[tuple(h for h in hdr if h)] += 1
        for h in hdr:
            if "BTTS" in h.upper() or "BTTS" in h:
                btts_cols.add(h)
        idx = {}
        for col in set(FRONT) | {"Div"}:
            if col in hdr:
                idx[col] = hdr.index(col)

        def col(row, name):
            i = idx.get(name)
            return row[i].strip() if i is not None and i < len(row) else ""

        for r in rows[1:]:
            if len(r) < 6 or not any(c.strip() for c in r[:5]):
                continue
            row_count_in += 1
            home, away, ftr = col(r, "HomeTeam"), col(r, "AwayTeam"), col(r, "FTR")
            if not home or not away or ftr not in ("H", "D", "A"):
                continue
            d_raw = col(r, "Date")
            d_iso = ""
            for fmt in ("%d/%m/%Y", "%d/%m/%y"):
                try:
                    d_iso = datetime.strptime(d_raw, fmt).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    pass
            # normalisasi nama tim
            pair = []
            for nm in (home, away):
                key = re.sub(r"[^a-z0-9]", "", nm.lower())
                fixed = CANON.get(key, nm)
                name_groups[div].setdefault(key, set()).add(fixed)
                pair.append(fixed)
            rec = {"Div": div, "Season": season, "Date": d_iso, "Time": col(r, "Time"),
                   "HomeTeam": pair[0], "AwayTeam": pair[1], "FTR": ftr}
            for c in FRONT[6:]:
                if c not in rec:
                    rec[c] = col(r, c)
            # seluruh kolom lain (odds dll) disimpan apa adanya
            for i, h in enumerate(hdr):
                if h and h not in rec:
                    rec[h] = r[i].strip() if i < len(r) else ""
            records.append(rec)

    # header master
    all_cols = Counter()
    for rec in records:
        for c in rec:
            all_cols[c] += 1
    n = len(records)
    rest = sorted(c for c in all_cols if c not in FRONT and all_cols[c] >= max(5, n // 1000))
    master_header = FRONT + rest

    # isi kolom yang hilang
    for rec in records:
        for c in master_header:
            rec.setdefault(c, "")

    # deteksi duplikat
    seen = set()
    dups = 0
    final = []
    for rec in records:
        key = (rec["Div"], rec["Date"], rec["HomeTeam"], rec["AwayTeam"], rec["Season"])
        if key in seen:
            dups += 1
            continue
        seen.add(key)
        final.append(rec)

    with open(os.path.join(OUTD, "all_matches.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=master_header, extrasaction="ignore")
        w.writeheader()
        w.writerows(final)

    # ===== laporan =====
    print(f"baris dibaca {row_count_in:,} | lolos {len(records):,} | duplikat dibuang {dups:,} | FINAL {len(final):,}")
    print(f"kolom master: {len(master_header)}")
    print(f"kolom BTTS ternyata ada? -> {btts_cols if btts_cols else 'TIDAK ADA (sesuai dugaan)'}")

    fill = []
    for c in ["HST", "HC", "Referee", "AHh", "AvgCH", "B365CH", "PSCH", "FTHG"]:
        k = sum(1 for r in final if r.get(c, "")) / max(len(final), 1)
        fill.append(f"{c} {k * 100:.0f}%")
    print("kelengkapan kolom kunci:", " | ".join(fill))

    print("\nVarian nama tim per divisi (kelompok >1 varian, top 12):")
    shown = 0
    for div in sorted(name_groups):
        for key, variants in name_groups[div].items():
            if len(variants) > 1 and shown < 12:
                print(f"  {div}: {sorted(variants)}")
                shown += 1
    if shown == 0:
        print("  (tidak ada kelompok multi-varian -> nama tim konsisten)")

    return {"read": row_count_in, "passed": len(records), "dups": dups,
            "final": len(final), "cols": len(master_header)}


if __name__ == "__main__":
    prepare()
