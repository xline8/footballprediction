"""Ekspor riwayat bet (ta/best_bets.csv) ke data halaman situs.

Sumber:
  ta/best_bets.csv  -> bet yang dibuat model (harga pasar tipsterarea)
  hasil & skor      -> kolom score/result/profit yang diisi ta_model.py --grade
                       (skor diambil dari ta/results.csv hasil scrape tipsterarea)

Output:
  C:/Users/Arif Wicaksono/football-site/site/assets/bet-history.js
  ta/bet_history.csv   (salinan datar untuk diperiksa)

Skrip ini hanya membaca. Tidak menyentuh model, tidak menyentuh data situs lain.
"""
import csv
import json
import os
from datetime import datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
TA = os.path.join(HERE, "ta")
SITE = r"C:/Users/Arif Wicaksono/football-site/site"
WIB = timezone(timedelta(hours=7))

MARKET_LABEL = {
    "1X2": "Hasil akhir",
    "DC": "Peluang ganda",
    "DNB": "Seri = uang kembali",
    "OU": "Jumlah gol",
    "BTS": "Kedua tim mencetak gol",
    "Corners": "Jumlah tendangan pojok",
}
SEL_LABEL = {
    "1": "tuan rumah menang",
    "X": "seri",
    "2": "tamu menang",
    "1X": "tuan rumah atau seri",
    "12": "tidak seri",
    "X2": "seri atau tamu",
    "Dnb1": "tuan rumah (seri = uang kembali)",
    "Dnb2": "tamu (seri = uang kembali)",
    "Yes": "ya",
    "No": "tidak",
    "Over": "lebih dari",
    "Under": "kurang dari",
}


def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(x, default=0.0):
    try:
        return float(x)
    except (TypeError, ValueError):
        return default


def label(r):
    m, sel, line = r["market"], r["selection"], r.get("line", "")
    if m == "OU":
        arah = "lebih dari" if sel == "Over" else "kurang dari"
        return f"{arah} {line} gol"
    return SEL_LABEL.get(sel, sel) if m in ("1X2", "DC", "DNB", "BTS") else sel


def wib(stamp):
    try:
        dt = datetime.strptime(stamp[:16], "%Y-%m-%dT%H:%M")
    except ValueError:
        return stamp, ""
    dt = dt.replace(tzinfo=timezone.utc).astimezone(WIB)
    return dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M")


def main():
    bets = read_csv(os.path.join(TA, "best_bets.csv"))
    rows = []
    for r in bets:
        d, t = wib(r["kickoff_utc"])
        status = (r.get("status") or "OPEN").upper()
        result = (r.get("result") or "").lower()
        rows.append({
            "date": d,
            "time": t,
            "match": f'{r["home"]} v {r["away"]}',
            "jenis": MARKET_LABEL.get(r["market"], r["market"]),
            "pilihan": label(r),
            "book": r["bookmaker"],
            "price": round(num(r["price"]), 2),
            "p_model": round(num(r["p_model"]), 4),
            "p_market": round(num(r["p_market"]), 4),
            "edge_pp": round((num(r["p_model"]) - num(r["p_market"])) * 100, 1),
            "status": "selesai" if status == "SETTLED" else "menunggu",
            "hasil": result,
            "skor": r.get("score", "") or "",
            "profit": round(num(r.get("profit")), 3) if status == "SETTLED" else None,
        })

    rows.sort(key=lambda x: (x["status"] != "selesai", x["date"], x["time"]))
    done = [x for x in rows if x["status"] == "selesai"]
    win = sum(1 for x in done if x["hasil"] == "win")
    lose = sum(1 for x in done if x["hasil"] == "lose")
    push = sum(1 for x in done if x["hasil"] == "push")
    pnl = round(sum(x["profit"] or 0 for x in done), 3)

    payload = {
        "generated_at": datetime.now(WIB).strftime("%Y-%m-%d %H:%M"),
        "sumber": "tipsterarea (harga pasar) + skor akhir hasil scrape",
        "n_total": len(rows),
        "n_done": len(done),
        "n_open": len(rows) - len(done),
        "win": win,
        "lose": lose,
        "push": push,
        "pnl_per_1": pnl,
        "roi_pct": round(pnl / len(done) * 100, 1) if done else None,
        "rows": rows,
    }

    os.makedirs(os.path.join(SITE, "assets"), exist_ok=True)
    out_js = os.path.join(SITE, "assets", "bet-history.js")
    with open(out_js, "w", encoding="utf-8") as f:
        f.write("/* AUTO-GENERATED oleh ta_export.py — jangan edit manual. */\n")
        f.write("window.BET_HISTORY = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    flat = os.path.join(TA, "bet_history.csv")
    cols = ["date", "time", "match", "jenis", "pilihan", "book", "price",
            "p_model", "p_market", "edge_pp", "status", "hasil", "skor", "profit"]
    with open(flat, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)

    print(f"bet: {len(rows)} | selesai: {len(done)} (menang {win}, kalah {lose}, seri {push}) "
          f"| menunggu: {len(rows) - len(done)}")
    print(f"untung/rugi per Rp 1: {pnl:+.3f}")
    print(f"tulis: {out_js}")
    print(f"tulis: {flat}")


if __name__ == "__main__":
    main()
