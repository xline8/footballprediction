#!/usr/bin/env python3
# snapshot_to_db.py — penerima snapshot Nowgoal (deterministic; dipakai cron odds-snapshot)
# Pakai: python snapshot_to_db.py raw/_latest_snapshot.json [--dry]
# Input : JSON {captured: "<ISO waktu lokal>", rows: [...]}  (hasil nowgoal_extract.js v2)
# Aksi  : (1) tulis raw/odds_nowgoal_<YYYYmmdd_HHMM>.csv (immutable, semua baris)
#         (2) append raw/odds_timeseries.csv (hanya baris div top-5)
#         (3) hitung edge vs model dari app-data.js situs (preview saja — TIDAK membuat pick)
# Aturan: tidak mengedit file lain; tidak menyentuh model/config; cocok nama gagal = SKIP (jangan menebak).
import json, sys, csv, os, re, difflib, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "raw")
COLS = ["captured","div","date","ko_wib","status","minute","home","away","score","ht",
        "x2_h","x2_d","x2_a","ah_h","ah_line","ah_a","raw"]
TS = os.path.join(RAW, "odds_timeseries.csv")
SITE_DATA = r"C:/Users/Arif Wicaksono/football-site/site/assets/app-data.js"

ALIAS = {  # ruang nama NORM nowgoal (nama panjang) -> ruang NORM model (nama pendek)
    "manchester city": "man city", "manchester united": "man united",
    "newcastle united": "newcastle", "nottingham forest": "nott m forest",
    "tottenham hotspur": "tottenham", "leeds united": "leeds",
    "west ham united": "west ham", "wolverhampton wanderers": "wolves",
    "eintracht frankfurt": "ein frankfurt", "rcd espanyol": "espanyol",
    "deportivo la coruna": "la coruna", "borussia dortmund": "dortmund",
    "atletico madrid": "ath madrid", "athletic bilbao": "ath bilbao",
    "borussia monchengladbach": "m gladbach", "celta vigo": "celta",
    "real sociedad": "sociedad", "racing santander": "santander",
    "rayo vallecano": "vallecano", "paris saint germain": "paris sg",
}

def norm(s):
    s = s.lower()
    s = re.sub(r"\b\d+\b", " ", s)      # buang token angka (menit/kartu/07)
    s = re.sub(r"[^a-z ]", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry = "--dry" in sys.argv
    src = args[0] if args else os.path.join(RAW, "_latest_snapshot.json")
    with open(src, encoding="utf-8") as f:
        d = json.load(f)
    cap = d.get("captured") or datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = d.get("rows", [])
    stamp = cap.replace("-", "").replace(":", "").replace(" ", "_")[:15]

    # (1) snapshot CSV immutable
    snap = os.path.join(RAW, f"odds_nowgoal_{stamp}.csv")
    if not dry:
        with open(snap, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS); w.writeheader()
            for x in rows:
                w.writerow({k: x.get(k, "") or "" for k in COLS})

    # (2) append timeseries (hanya div top-5)
    top = [x for x in rows if x.get("div")]
    if not dry:
        new = not os.path.exists(TS)
        with open(TS, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=COLS)
            if new: w.writeheader()
            for x in top:
                w.writerow({k: x.get(k, "") or "" for k in COLS})

    # (3) edge preview vs model
    with open(SITE_DATA, encoding="utf-8") as f:
        D = json.loads(re.search(r"window\.APP_DATA\s*=\s*(\{.*\});?\s*$", f.read(), re.S).group(1))
    up = D.get("upcoming", [])
    line = []
    for x in top:
        hn = ALIAS.get(norm(x["home"]), norm(x["home"]))
        an = ALIAS.get(norm(x["away"]), norm(x["away"]))
        best, sc = None, 0.0
        d0 = (x.get("date") or "")[:10]
        dt0 = datetime.date.fromisoformat(d0) if re.match(r"^\d{4}-\d{2}-\d{2}$", d0) else None
        for u in up:
            if dt0 and re.match(r"^\d{4}-\d{2}-\d{2}$", (u.get("date") or "")[:10]):
                try:
                    if abs((datetime.date.fromisoformat(u["date"][:10]) - dt0).days) > 1:
                        continue  # tanggal beda jauh = fixture lain, jangan cocokkan
                except ValueError:
                    pass
            r2 = (difflib.SequenceMatcher(None, hn, norm(u["home"])).ratio()
                  * difflib.SequenceMatcher(None, an, norm(u["away"])).ratio())
            if r2 > sc: sc, best = r2, u
        if sc < 0.55 or not best or not best.get("ph"):
            line.append(f"SKIP {x['home']} v {x['away']} (tanpa fixture model / pasangan rendah {sc:.2f})")
            continue
        ph, pd, pa = best["ph"], best["pd"], best["pa"]
        e = {"H": ph*float(x["x2_h"])-1, "D": pd*float(x["x2_d"])-1, "A": pa*float(x["x2_a"])-1}
        s2 = max(e, key=e.get)
        line.append(f"{x['status']:4} {best['home']} v {best['away']} [{x['ko_wib']}] "
                    f"1x2 {x['x2_h']}/{x['x2_d']}/{x['x2_a']} -> {s2} {e[s2]*100:+.2f}%"
                    + (f" | menit {x['minute']} skor {x['score']}" if x.get("status") != "pre" else ""))
        # disiplin: job ini TIDAK membuat pick; threshold hanya info tampilan
    print(f"captured={cap} top5={len(top)} snapshot_csv={'skip(dry)' if dry else os.path.basename(snap)}")
    for l in line: print("  " + l)

if __name__ == "__main__":
    main()
