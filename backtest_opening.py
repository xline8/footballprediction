# -*- coding: utf-8 -*-
"""backtest_opening.py — AUDIT HARGA OPENING untuk story jujur backtest.

Pertanyaan: kalau pool value-bet DIPILIH dan DIBAYAR di harga OPENING
(sebelum pasar hargakan info), apakah "edge" yang sama tetap terlihat —
dan berapa sisanya ketika bet yang sama disettle di harga CLOSING?

Metode (mirror backtest_value.py, sumber harga dibalik):
- Signal  : prob model MURNI (ph_dc/pd_dc/pa_dc, p_over_dc, p_ah_home).
- Pilih   : edge_open = p_model - 1/odds_open; bet saat edge_open > thr.
- Settle  : ret_open  = odds_open x kemenangan   (bet apa adanya)
            ret_close = odds_close x kemenangan (sama bet, ditahan s/d close)
- Odds opening 1X2: AvgH/D/A fallback B365H/D/A; OU: Avg>2.5 fallback B365>2.5;
  AH: AvgAHH di line AHh (closing pembanding PSC*, AvgC>2.5, AvgCAHH).
- Flat stake 1 unit; AH sisi home, push=refund, quarter-line didukung.

Output: value_bets_opening.csv + opening_audit.json (utk situs) + tabel stdout.
Skrip BARU — tidak menyentuh backtest_value.py / value_bets.csv.
"""
import csv
import json
import math
import time
from collections import Counter

PROJ = r"C:/Users/Arif Wicaksono/football-data"
PRED = PROJ + "/predictions_v2.csv"
RAW = PROJ + "/all_matches_clean.csv"
OUT_CSV = PROJ + "/value_bets_opening.csv"
OUT_JSON = PROJ + "/opening_audit.json"

T_GRID = [0.00, 0.01, 0.02, 0.03, 0.05, 0.08]
t0 = time.time()


def fnum(x):
    if x is None:
        return None
    x = str(x).strip()
    if not x:
        return None
    try:
        v = float(x)
    except ValueError:
        return None
    return v if math.isfinite(v) else None


with open(PRED, newline="", encoding="utf-8-sig") as fh:
    preds = list(csv.DictReader(fh))
keys = [(p["div"].strip(), p["date"].strip(), p["season"].strip(),
         p["home"].strip(), p["away"].strip()) for p in preds]
keyset = set(keys)

OPEN_COLS = ["AvgH", "AvgD", "AvgA", "B365H", "B365D", "B365A",
             "Avg>2.5", "B365>2.5", "AHh", "AvgAHH",
             "PSCH", "PSCD", "PSCA", "AvgC>2.5", "AvgCAHH"]
oddsmap = {}
with open(RAW, newline="", encoding="utf-8-sig") as fh:
    for row in csv.DictReader(fh):
        k = (str(row.get("Div", "")).strip(), str(row.get("Date", "")).strip(),
             str(row.get("Season", "")).strip(), str(row.get("HomeTeam", "")).strip(),
             str(row.get("AwayTeam", "")).strip())
        if k not in keyset:
            continue
        vals = {c: fnum(row.get(c)) for c in OPEN_COLS}
        if k not in oddsmap or sum(v is not None for v in vals.values()) > \
                sum(v is not None for v in oddsmap[k].values()):
            oddsmap[k] = vals

bets = []
miss = Counter()
for i, p in enumerate(preds):
    k = keys[i]
    od = oddsmap.get(k)
    ftr = (p.get("ftr") or "").strip().upper()
    yh, ya = fnum(p.get("yh")), fnum(p.get("ya"))

    def add(market, side, team, line, o_open, o_close, pm):
        if o_open is None or o_open <= 1.0:
            miss[market + "_no_open"] += 1
            return
        bets.append(dict(market=market, div=p["div"].strip(), date=p["date"].strip(),
                         season=p["season"].strip(), home=p["home"].strip(),
                         away=p["away"].strip(), mid=i, side=side, team=team, line=line,
                         odds_open=o_open, odds_close=o_close,
                         p_model=pm, edge=pm - 1.0 / o_open))

    # 1X2: edge dicek vs OPENING
    for side, pcol, ocols_o, ocols_c in (
            ("H", "ph_dc", ("AvgH", "B365H"), ("PSCH",)),
            ("D", "pd_dc", ("AvgD", "B365D"), ("PSCD",)),
            ("A", "pa_dc", ("AvgA", "B365A"), ("PSCA",))):
        pm = fnum(p.get(pcol))
        if pm is None:
            miss["1X2_model_prob_missing"] += 1
            continue
        o_open = next((od.get(c) if od else None for c in ocols_o
                       if od and od.get(c)), None) if od else None
        o_close = next((od.get(c) if od else None for c in ocols_c
                        if od and od.get(c)), None) if od else None
        team = p["home"].strip() if side == "H" else (p["away"].strip() if side == "A" else "Draw")
        add("1X2", side, team, None, o_open, o_close, pm)

    # O/U over 2.5
    pm = fnum(p.get("p_over_dc"))
    if pm is None:
        miss["OU_model_prob_missing"] += 1
    else:
        o_open = next((od.get(c) if od else None for c in ("Avg>2.5", "B365>2.5")
                       if od and od.get(c)), None) if od else None
        o_close = od.get("AvgC>2.5") if od else None
        add("OU", "Over", p["home"].strip() + " v " + p["away"].strip(), 2.5, o_open, o_close, pm)

    # AH home (line harus cocok dgn pred)
    pm = fnum(p.get("p_ah_home"))
    pline = fnum(p.get("ahh"))
    ahline = od.get("AHh") if od else None
    if pm is None:
        miss["AH_model_prob_missing"] += 1
    elif pline is None or ahline is None or abs(pline - ahline) > 1e-6:
        miss["AH_line_missing_or_mismatch"] += 1
    else:
        o_open = od.get("AvgAHH") if od else None
        o_close = od.get("AvgCAHH") if od else None
        add("AH", "AH_home", p["home"].strip(), ahline, o_open, o_close, pm)


def settle(market, line, o, yh, ya):
    """Return unit utk odds o (tidak pernah None saat dipanggil)."""
    if market == "1X2":
        return None  # settle terpisah dgn ftr
    if market == "OU":
        return o if (yh is not None and ya is not None and (yh + ya) > 2.5) else 0.0
    # AH
    if yh is None or ya is None:
        return None
    q = round(((yh - ya) + line) * 4)
    if q == 0:
        return 1.0
    if q > 0:
        return 1.0 + (o - 1.0) / 2.0 if q == 1 else o
    return 0.5 if q == -1 else 0.0


bets = [b for b in bets if b["odds_open"] is not None and b["odds_open"] > 1.0]
for b in bets:
    k = (b["div"], b["date"], b["season"], b["home"], b["away"])
    # hasil aktual: cari di preds (yh, ya ftr) by mid
    p = preds[b["mid"]]
    ftr = (p.get("ftr") or "").strip().upper()
    yh, ya = fnum(p.get("yh")), fnum(p.get("ya"))
    if b["market"] == "1X2":
        b["ret_open"] = b["odds_open"] if ftr == b["side"] else 0.0
        b["ret_close"] = (b["odds_close"] if ftr == b["side"] else 0.0) \
            if b["odds_close"] else None
    else:
        b["ret_open"] = settle(b["market"], b["line"], b["odds_open"], yh, ya)
        b["ret_close"] = settle(b["market"], b["line"], b["odds_close"], yh, ya) \
            if b["odds_close"] else None

agg = {}
for b in bets:
    for t in T_GRID:
        if b["edge"] > t:
            a = agg.setdefault((b["market"], t), dict(n=0, ro=0.0, rc=0.0, nc=0, npush=0))
            a["n"] += 1
            a["ro"] += b["ret_open"]
            if b["ret_close"] is not None:
                a["rc"] += b["ret_close"]
                a["nc"] += 1
            if b["market"] == "AH" and b["ret_open"] == 1.0:
                a["npush"] += 1

W = 88
print("=" * W)
print("AUDIT OPENING — bet dipilih dgn edge vs HARGA OPENING, disettle di open vs closing")
print("=" * W)
print(f"{'pasar':<6}{'thr':>6}{'n':>8}{'ROI_open%':>11}{'ROI_close%':>12}{'n_close':>9}{'push':>6}")
out_json = {}
for mkt in ("1X2", "OU", "AH"):
    out_json[mkt] = {}
    for t in T_GRID:
        a = agg.get((mkt, t))
        if not a:
            continue
        roi_o = (a["ro"] - a["n"]) / a["n"] * 100 if a["n"] else float("nan")
        roi_c = (a["rc"] - a["nc"]) / a["nc"] * 100 if a["nc"] else float("nan")
        print(f"{mkt:<6}{t:>6.2f}{a['n']:>8d}{roi_o:>10.2f}%{roi_c:>11.2f}%{a['nc']:>9d}{a['npush']:>6d}")
        out_json[mkt][f"{t:.2f}"] = {
            "n": a["n"],
            "roi_open": round(roi_o, 2),
            "roi_close": round(roi_c, 2) if a["nc"] else None,
            "n_close": a["nc"],
            "push": a["npush"],
        }
print(f"\npeluang gagal: {dict(miss)}")
print(f"Runtime: {time.time()-t0:.1f}s")

# opsional ringkas: pertahankan edge>0.02 sbg referensi utama situs
with open(OUT_CSV, "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh)
    w.writerow(["market", "league", "season", "date", "home", "away", "side", "team",
                "line", "odds_open", "odds_close", "p_model", "p_imp_open",
                "edge_open", "stake", "return_open", "return_close"])
    for b in sorted(bets, key=lambda x: (x["date"], x["mid"], x["market"])):
        if b["edge"] <= 0:
            continue
        w.writerow([b["market"], b["div"], b["season"], b["date"], b["home"], b["away"],
                    b["side"], b["team"], "" if b["line"] is None else b["line"],
                    repr(b["odds_open"]), "" if b["odds_close"] is None else repr(b["odds_close"]),
                    repr(b["p_model"]), repr(1.0 / b["odds_open"]), repr(b["edge"]),
                    1, repr(b["ret_open"]),
                    "" if b["ret_close"] is None else repr(b["ret_close"])])
with open(OUT_JSON, "w", encoding="utf-8") as fh:
    json.dump({
        "desc": "Bet dipilih dgn edge vs harga opening lalu disettle di open vs closing (flat 1u)",
        "note": "Opening = info pra-pasar; closing memuat informasi publik se kickoff. "
                "ROI_open yang bagus tapi ROI_close jelek = edge hanya ilusi informasi.",
        "grid": out_json,
    }, fh, ensure_ascii=False, indent=2)
print("tersimpan:", OUT_CSV, "+", OUT_JSON)
