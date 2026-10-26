# -*- coding: utf-8 -*-
"""build_appdata.py — perbarui array `upcoming` di app-data.js dari predictions_upcoming.csv.

Kontrak:
- HANYA bagian "upcoming" yang ditulis ulang; scorecard/opening_audit/ledger dibiarkan byte-demi-byte.
- Probabilitas = model v2: pakai *_bl bila ada (blend), kalau tidak *_dc. TIDAK mengubah angka model.
- odds/edge di upcoming diset null — harga 1X2 situs kini satu-satunya dari snapshot Nowgoal
  (odds-latest.js), bukan lagi B365 football-data. Tidak ada sumber ganda.
- Backup app-data lama -> assets/app-data.prev.js (satu salinan, ditimpa tiap run).
"""
import csv
import os
import re
import shutil

PROJ = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(PROJ, "predictions_upcoming.csv")
SITE = r"C:/Users/Arif Wicaksono/football-site/site/assets/app-data.js"


def pick(row, bl, dc):
    v = (row.get(bl) or "").strip()
    return round(float(v), 4) if v else round(float(row[dc]), 4)


def load_upcoming():
    from datetime import datetime, timedelta
    today = datetime.now().date()
    hi = (today + timedelta(days=11)).isoformat()  # jendela situs: 10 hari ke depan + hari ini (inklusif s.d. 27 Okt dulu)
    with open(DATA, encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    out = []
    for r in rows:
        if not r.get("home"):
            continue  # baris kosong sisa kanon FD
        if not (today.isoformat() <= r["date"] < hi):
            continue  # di luar jendela 10 hari — pipeline predict boleh memprediksi penuh,
                      # situs hanya menampilkan jendela jadwalnya
        out.append({
            "date": r["date"], "time": r["time"], "div": r["div"],
            "home": r["home"], "away": r["away"],
            "ph": pick(r, "ph_bl", "ph_dc"), "pd": pick(r, "pd_bl", "pd_dc"),
            "pa": pick(r, "pa_bl", "pa_dc"),
            "p_over": pick(r, "p_over_bl", "p_over_dc"),
            "p_btts": round(float(r["p_btts"]), 4) if r.get("p_btts") else None,
            "odds": None, "edge": None,
        })
    out.sort(key=lambda x: (x["date"], x["div"], x["time"], x["home"]))
    return out


def main():
    upcoming = load_upcoming()
    with open(SITE, encoding="utf-8") as f:
        src = f.read()
    m = re.search(r'"upcoming"\s*:\s*\[', src)
    if not m:
        raise SystemExit("kunci upcoming tidak ditemukan di app-data.js")
    i = m.start()
    j = src.index("],", i)
    old_chunk = src[i:j + 1]
    n_old = old_chunk.count('"date":')
    # catat probabilitas lama utk audit (anti-shifting diam-diam)
    old_vals = re.findall(r'"ph"\s*:\s*([\d.]+)', old_chunk)
    header = (
        '// Dihasilkan build_appdata.py (refresh fixture Understat; probabilitas model v2 '
        'TERKUNCI; odds/edge sengaja null = harga hanya dari snapshot Nowgoal via odds-latest.js)\n'
    )
    m2 = re.match(r"//.*\n", src)
    body = src[m2.end():] if m2 else src
    new_upcoming = '"upcoming": ' + json.dumps(upcoming, ensure_ascii=False, separators=(", ", ": ")) + ","
    body = re.sub(r'"upcoming"\s*:\s*\[.*?\],', new_upcoming, body, count=1, flags=re.S)
    shutil.copy2(SITE, SITE.replace("app-data.js", "app-data.prev.js"))
    tmp = SITE + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\r\n") as f:
        f.write(header + body)
    os.replace(tmp, SITE)
    print(f"upcoming: {n_old} -> {len(upcoming)} fixture")
    ph_new = [u["ph"] for u in upcoming]
    same_first = old_vals[:5] == [str(v) for v in ph_new[:5]] if old_vals else None
    print(f"5 prob pertama identik dgn lama: {same_first} | fixture 17-18 Okt: "
          f"{sum(1 for u in upcoming if u['date'] in ('2026-10-17', '2026-10-18'))}")
    print(f"rentang: {upcoming[0]['date']} .. {upcoming[-1]['date']} | tersimpan: {SITE}")


if __name__ == "__main__":
    import json
    main()
