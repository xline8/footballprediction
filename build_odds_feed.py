#!/usr/bin/env python3
# build_odds_feed.py — sambungkan harga snapshot terakhir (odds_timeseries) ke data jadwal situs.
# Pakai: python build_odds_feed.py
# Output: C:/Users/Arif Wicaksono/football-site/site/assets/odds-latest.js
#   window.ODDS_LATEST = { "<HOME MODEL>|<AWAY MODEL>": {cap,h,d,a,edge,side}, ... }
# Aturan: hanya baris status "pre" (jadwal itu pre-match); harga = snapshot terbaru; tidak
#         menyentuh model/config; fixture tanpa harga tidak muncul (kolom tetap "belum dibuka").
import csv, os, re, json, difflib, datetime
from snapshot_to_db import norm, ALIAS

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, "raw", "odds_timeseries.csv")
SITE_DATA = r"C:/Users/Arif Wicaksono/football-site/site/assets/app-data.js"
OUT = r"C:/Users/Arif Wicaksono/football-site/site/assets/odds-latest.js"

def main():
    with open(SITE_DATA, encoding="utf-8") as f:
        D = json.loads(re.search(r"window\.APP_DATA\s*=\s*(\{.*\});?\s*$", f.read(), re.S).group(1))
    up = D.get("upcoming", [])

    rows = [r for r in csv.DictReader(open(TS, encoding="utf-8")) if r["status"] == "pre" and r.get("x2_h")]
    rows.sort(key=lambda r: r["captured"])          # terakhir menang
    feed, edge_rows = {}, []
    for r in rows:
        hn = ALIAS.get(norm(r["home"]), norm(r["home"]))
        an = ALIAS.get(norm(r["away"]), norm(r["away"]))
        d0 = (r.get("date") or "")[:10]
        dt0 = datetime.date.fromisoformat(d0) if re.match(r"^\d{4}-\d{2}-\d{2}$", d0) else None
        best, sc = None, 0.0
        for u in up:
            if dt0 and re.match(r"^\d{4}-\d{2}-\d{2}$", (u.get("date") or "")[:10]):
                try:
                    if abs((datetime.date.fromisoformat(u["date"][:10]) - dt0).days) > 1:
                        continue
                except ValueError:
                    pass
            r2 = (difflib.SequenceMatcher(None, hn, norm(u["home"])).ratio()
                  * difflib.SequenceMatcher(None, an, norm(u["away"])).ratio())
            if r2 > sc: sc, best = r2, u
        if sc < 0.55 or not best:
            continue
        e = {"H": best["ph"]*float(r["x2_h"])-1, "D": best["pd"]*float(r["x2_d"])-1, "A": best["pa"]*float(r["x2_a"])-1}
        side = max(e, key=e.get)
        feed[best["home"] + "|" + best["away"]] = {
            "cap": r["captured"][:16], "h": r["x2_h"], "d": r["x2_d"], "a": r["x2_a"],
            "edge": round(e[side], 4), "side": side,
        }
        edge_rows.append((e[side], side, best["home"], best["away"]))
    js = "/* AUTO-GENERATED oleh build_odds_feed.py — jangan edit manual. */\n" \
         "window.ODDS_LATEST = " + json.dumps(feed, ensure_ascii=False, sort_keys=True) + ";\n"
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(js)
    edge_rows.sort(reverse=True)
    print(f"odds-latest.js: {len(feed)} fixture berharga (dari {len(rows)} baris pre)")
    for e, s, h, a in edge_rows[:5]:
        print(f"  {s} {e*100:+.2f}%  {h} v {a}")

if __name__ == "__main__":
    main()
