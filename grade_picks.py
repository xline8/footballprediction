#!/usr/bin/env python3
# grade_picks.py — menilai pick pending dari skor FT hasil snapshot (append-only, idempoten).
# Pakai: python grade_picks.py
# Sumber: ledger/picks.csv (pending) + raw/odds_timeseries.csv (baris status=ft dengan skor).
# Output: ledger/graded.csv (per pick: status win/loss + ret + skor) — picks.csv TIDAK disentuh.
# Cocok nama pakai ALIAS+jendela tanggal yang sama dengan snapshot_to_db; tak ketemu = masih pending.
# Grade dihitung dari skor FT: H menang bila gol tuan > gol tamu, dst. ret = (odds-1) saat menang, -1 saat kalah.
import csv, os, re, difflib, datetime
from snapshot_to_db import norm, ALIAS

HERE = os.path.dirname(os.path.abspath(__file__))
TS = os.path.join(HERE, "raw", "odds_timeseries.csv")
PICKS = os.path.join(HERE, "ledger", "picks.csv")
GRADED = os.path.join(HERE, "ledger", "graded.csv")
GRADE_COLS = ["ts_grade","date","home","away","market","side","status","score","ret"]

def side_win(side, score):
    m = re.match(r"^\s*(\d+)\s*[-:]\s*(\d+)\s*$", score or "")
    if not m: return None
    gh, ga = int(m.group(1)), int(m.group(2))
    if side == "H": return "win" if gh > ga else "loss"
    if side == "A": return "win" if ga > gh else "loss"
    return "win" if ga == gh else "loss"          # D

def main():
    if not os.path.exists(PICKS):
        print("graded: picks.csv belum ada"); return
    picks = [r for r in csv.DictReader(open(PICKS, encoding="utf-8")) if r["status"] == "pending"]
    have = set()
    if os.path.exists(GRADED):
        for r in csv.DictReader(open(GRADED, encoding="utf-8")):
            have.add((r["date"], r["home"], r["away"], r["market"], r["side"]))
    ft = [r for r in csv.DictReader(open(TS, encoding="utf-8")) if r["status"] == "ft" and r.get("score")]

    graded = []
    for p in picks:
        key = (p["date"], p["home"], p["away"], p["market"], p["side"])
        if key in have: continue
        pn = ALIAS.get(norm(p["home"]), norm(p["home"]))
        an = ALIAS.get(norm(p["away"]), norm(p["away"]))
        best, sc = None, 0.0
        for r in ft:
            d0 = (p["date"] or "")[:10]
            if re.match(r"^\d{4}-\d{2}-\d{2}$", d0) and re.match(r"^\d{4}-\d{2}-\d{2}$", (r.get("date") or "")[:10]):
                try:
                    if abs((datetime.date.fromisoformat(r["date"][:10]) - datetime.date.fromisoformat(d0)).days) > 1:
                        continue
                except ValueError:
                    pass
            r2 = (difflib.SequenceMatcher(None, pn, norm(r["home"])).ratio()
                  * difflib.SequenceMatcher(None, an, norm(r["away"])).ratio())
            if r2 > sc: sc, best = r2, r
        if sc < 0.55 or not best:
            continue
        st = side_win(p["side"], best["score"])
        if not st: continue
        graded.append({
            "ts_grade": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": p["date"], "home": p["home"], "away": p["away"], "market": p["market"], "side": p["side"],
            "status": st, "score": best["score"],
            "ret": f"{(float(p['odds_open']) - 1) if st == 'win' else -1:.2f}",
        })
    if graded:
        new = not os.path.exists(GRADED)
        with open(GRADED, "a", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=GRADE_COLS)
            if new: w.writeheader()
            for g in graded: w.writerow(g)
        for g in graded:
            print(f"GRADE  {g['home']} v {g['away']}  1x2 {g['side']}  {g['score']} -> {g['status']} (ret {g['ret']})")
    print(f"graded: {len(graded)} baru; total baris graded: "
          f"{sum(1 for _ in open(GRADED, encoding='utf-8')) - 1 if os.path.exists(GRADED) else 0}")

if __name__ == "__main__":
    main()
