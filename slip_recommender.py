#!/usr/bin/env python3
"""slip_recommender.py — rekomendasi harian deterministik dari odds 1xBet nyata.

Tiga produk, semua di-scope ke TANGGAL LAPORAN (keputusan user 2026-10-29;
perilaku lama yang mencari di seluruh jendela +4 hari dicabut):

  1. recommended_single.csv — single bet: leg tanggal itu dengan EV
     tertinggi (p_model * o_1xbet - 1) di antara yang lolos lantai
     p_model >= 0.45 dan o_1xbet >= 1.40; tie-break probabilitas, lalu odds.
     Bila tak ada yang lolos, lantai longgar (0.40 / 1.30) dipakai dan baris
     ditandai below_floor=true.
  2. recommended_slip.csv — slip odds ±2: 2-4 leg dari tanggal itu,
     p_model >= 0.50, o_1xbet >= 1.20, total odds di band 1.85-2.15, joint
     probability tertinggi (tie-break total EV). Tanpa in-band: kombinasi
     tanggal itu yang totalnya terdekat ke 2.0, in_band=false.
  3. recommended_slip10.csv — slip odds ±10: 3-6 leg, p_model >= 0.35,
     o_1xbet >= 1.30, total odds di band 9.0-11.0, joint tertinggi. Pool
     mulai dari tanggal laporan; bila band tak tercapai, pool diperluas
     hari demi hari (maks +4) — tiap leg membawa tanggalnya sendiri dan
     ringkasan mencatat pool_expanded_to. Tanpa in-band: terdekat ke 10.0,
     in_band=false.

Sumber leg: market_compare.csv (odds o_1xbet) di-join ke probabilitas model
(predictions_upcoming.csv / predictions_cups_upcoming.csv). Pasar: 1X2 / DC /
OU / BTS (tanpa corner — tidak ada odds-nya di market_compare). Satu leg per
pertandingan di semua produk. Ketiga file diarsipkan harian oleh
market_orchestration.archive_snapshots.

Run: python slip_recommender.py [--date YYYY-MM-DD]
"""
import csv
import math
import os
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
MARKET_COMPARE = os.path.join(HERE, "market_compare.csv")
PRED_LEAGUE = os.path.join(HERE, "predictions_upcoming.csv")
PRED_CUP = os.path.join(HERE, "predictions_cups_upcoming.csv")
OUT_SLIP = os.path.join(HERE, "recommended_slip.csv")
OUT_SINGLE = os.path.join(HERE, "recommended_single.csv")
OUT_SLIP10 = os.path.join(HERE, "recommended_slip10.csv")

MARKETS = ("1X2", "DC", "OU", "BTS")

# Single bet
SINGLE_MIN_PM, SINGLE_MIN_ODDS = 0.45, 1.40
SINGLE_LOOSE_PM, SINGLE_LOOSE_ODDS = 0.40, 1.30
# Slip odds ±2
S2_MIN_PM, S2_MIN_ODDS = 0.50, 1.20
S2_LO, S2_HI, S2_TARGET = 1.85, 2.15, 2.0
S2_MIN_LEGS, S2_MAX_LEGS = 2, 4
# Slip odds ±10
S10_MIN_PM, S10_MIN_ODDS = 0.35, 1.30
S10_LO, S10_HI, S10_TARGET = 9.0, 11.0, 10.0
S10_MIN_LEGS, S10_MAX_LEGS = 3, 6
S10_MAX_EXPAND_DAYS = 4

# Batas node DFS (audit K5): tanpa batas, pool besar (slate akhir pekan
# atau ekspansi slip10) bisa membuat pencarian berjalan sangat lama dan
# menggantung seluruh rantai harian yang memanggilnya in-process.
# Anggaran ini jauh di atas kebutuhan pool nyata saat ini; bila habis,
# pencarian berhenti dan mengembalikan kandidat terbaik yang sudah
# ditemukan (degradasi yang deterministik, bukan hang).
SEARCH_NODE_BUDGET = 200_000

SLIP_COLS = ["date", "home", "away", "competition", "market", "line",
             "selection", "o_1xbet", "p_model", "slip_total_odds",
             "slip_joint_prob", "slip_ev", "in_band"]
SINGLE_COLS = ["date", "home", "away", "competition", "market", "line",
               "selection", "o_1xbet", "p_model", "ev", "below_floor"]
SLIP10_COLS = SLIP_COLS + ["pool_expanded_to"]


def _read(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _load_preds():
    """(date, home_norm, away_norm) -> pred row (liga/cup)."""
    d = {}
    for fn in (PRED_LEAGUE, PRED_CUP):
        for r in _read(fn):
            key = ((r.get("date") or ""), (r.get("home") or "").lower(),
                   (r.get("away") or "").lower())
            d.setdefault(key, []).append(r)
    return d


def _pm_for(market, line, sel, pr):
    """p_model dari baris prediksi untuk (market, line, selection)."""
    if market == "1X2":
        col = {"1": "ph_dc", "X": "pd_dc", "2": "pa_dc"}.get(sel)
        return _f(pr.get(col)) if col else None
    if market == "DC":
        col = {"1X": "p_dc_1x", "12": "p_dc_12", "X2": "p_dc_x2"}.get(sel)
        return _f(pr.get(col)) if col else None
    if market == "OU":
        col = {"1.5": "p_over15_dc", "2.5": "p_over_dc",
               "3.5": "p_over35_dc"}.get(str(line))
        ov = _f(pr.get(col)) if col else None
        if ov is None:
            return None
        return ov if sel == "Over" else 1.0 - ov
    if market == "BTS":
        b = _f(pr.get("p_btts"))
        if b is None:
            return None
        return b if sel == "Yes" else 1.0 - b
    return None


def _candidates(min_pm, min_odds):
    """Semua leg (dari market_compare + p_model) yang lolos lantai given."""
    preds = _load_preds()
    out = []
    for r in _read(MARKET_COMPARE):
        market = r.get("market")
        if market not in MARKETS:
            continue
        o = _f(r.get("o_1xbet"))
        if not o or o < min_odds:
            continue
        key = ((r.get("date") or ""), (r.get("home") or "").lower(),
               (r.get("away") or "").lower())
        prows = preds.get(key)
        if not prows:
            continue
        pm = _pm_for(market, r.get("line"), r.get("selection"), prows[0])
        if pm is None or pm < min_pm:
            continue
        out.append({
            "match": r.get("game_id") or key,
            "date": r.get("date") or "", "home": r.get("home") or "",
            "away": r.get("away") or "", "comp": r.get("competition") or "",
            "market": market, "line": r.get("line") or "",
            "sel": r.get("selection") or "", "o": o, "pm": pm,
        })
    return out


def _search(by_match, min_legs, max_legs, lo, hi, target, stats=None):
    """Cari kombinasi (<= 1 leg per laga) terbaik.

    Return (best_in_band, best_near), masing-masing (tot, jp, ev, legs) atau
    None. best_in_band: joint prob tertinggi dengan tot di [lo, hi]
    (tie-break total EV). best_near: |tot - target| terkecil di antara
    kombinasi valid (tie-break joint prob). Pencarian DFS dengan pruning
    produk odds: cabang berhenti bila produk melewati hi * 2.5.
    """
    keys = sorted(by_match, key=lambda k: (by_match[k][0]["date"],
                                           by_match[k][0]["home"],
                                           by_match[k][0]["away"]))
    pools = [sorted(by_match[k],
                    key=lambda l: (-l["pm"], -l["o"], l["market"],
                                   l["line"], l["sel"]))
             for k in keys]
    cap = hi * 2.5
    best_in = None
    best_near = None
    nodes = [0]
    truncated = [False]

    def consider(tot, jp, legs):
        nonlocal best_in, best_near
        if len(legs) < min_legs:
            return
        # EV gabungan slip: P(semua leg menang) * total odds - 1.
        # Versi lama menjumlahkan EV per leg, yang bukan EV slip dan
        # mengacaukan tie-break serta kolom slip_ev di output.
        ev = jp * tot - 1.0
        if lo <= tot <= hi:
            cur = (tot, jp, ev, list(legs))
            if (best_in is None or jp > best_in[1] + 1e-9
                    or (abs(jp - best_in[1]) <= 1e-9 and ev > best_in[2])):
                best_in = cur
        cur = (tot, jp, ev, list(legs))
        if (best_near is None
                or abs(tot - target) < abs(best_near[0] - target) - 1e-9
                or (abs(abs(tot - target) - abs(best_near[0] - target)) <= 1e-9
                    and jp > best_near[1])):
            best_near = cur

    def rec(i, tot, jp, legs):
        if truncated[0]:
            return
        nodes[0] += 1
        if nodes[0] > SEARCH_NODE_BUDGET:
            truncated[0] = True
            return
        if len(legs) >= min_legs:
            consider(tot, jp, legs)
        if i == len(pools) or len(legs) == max_legs:
            return
        rec(i + 1, tot, jp, legs)  # lewati laga ini
        for leg in pools[i]:
            if truncated[0]:
                return
            nt = tot * leg["o"]
            if nt > cap:
                continue
            legs.append(leg)
            rec(i + 1, nt, jp * leg["pm"], legs)
            legs.pop()

    nodes_pass1 = None
    trunc_budget = SEARCH_NODE_BUDGET
    rec(0, 1.0, 1.0, [])
    if best_near is None and not truncated[0]:
        # Semua kombinasi valid melewati cap produk (hi * 2.5), jadi
        # fallback terdekat ikut kosong — contoh nyata: dua laga @2.4
        # untuk slip2 (produk 5.76 > cap 5.375) menghasilkan file
        # kosong padahal kombinasi terdekat tersedia. Ulangi tanpa cap
        # dengan anggaran node kecil, khusus mencari best_near
        # (best_in tidak bisa muncul di sini: tot > cap > hi).
        nodes_pass1 = nodes[0]
        trunc_budget = 50_000
        nodes[0] = 0

        def rec2(i, tot, jp, legs):
            if truncated[0]:
                return
            nodes[0] += 1
            if nodes[0] > 50_000:
                truncated[0] = True
                return
            if len(legs) >= min_legs:
                consider(tot, jp, legs)
            if i == len(pools) or len(legs) == max_legs:
                return
            rec2(i + 1, tot, jp, legs)
            for leg in pools[i]:
                if truncated[0]:
                    return
                legs.append(leg)
                rec2(i + 1, tot * leg["o"], jp * leg["pm"], legs)
                legs.pop()

        rec2(0, 1.0, 1.0, [])
    if truncated[0]:
        # Anggaran yang benar-benar mengikat: pass 2 punya batas 50k
        # sendiri; mencetak SEARCH_NODE_BUDGET (batas pass 1) di sini
        # menyesatkan bila pass 2 yang terpotong.
        print(f"  ! slip search mencapai batas node {trunc_budget}; "
              f"memakai kandidat terbaik yang sudah ditemukan")
    if stats is not None:
        stats["nodes"] = nodes[0] + (nodes_pass1 or 0)
        stats["truncated"] = truncated[0]
    return best_in, best_near


def _by_match(cands, dates):
    by = defaultdict(list)
    for c in cands:
        if c["date"] in dates:
            by[c["match"]].append(c)
    return by


def _write_slip(path, cols, best, in_band, extra=None):
    rows = []
    if best is not None:
        tot, jp, ev, legs = best
        for l in legs:
            row = {"date": l["date"], "home": l["home"], "away": l["away"],
                   "competition": l["comp"], "market": l["market"],
                   "line": l["line"], "selection": l["sel"],
                   "o_1xbet": round(l["o"], 3), "p_model": round(l["pm"], 4),
                   "slip_total_odds": round(tot, 3),
                   "slip_joint_prob": round(jp, 4), "slip_ev": round(ev, 4),
                   "in_band": "true" if in_band else "false"}
            if extra:
                row.update(extra)
            rows.append(row)
    # Tulis atomik: file rekomendasi dibaca grader + arsip; penulisan
    # terpotong tidak boleh terbaca sebagai slip kosong.
    tmp = path + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, path)
    return rows


def recommend_single(day):
    """Produk 1: single bet tanggal `day` (ISO). Return ringkasan dict."""
    pool = [c for c in _candidates(SINGLE_MIN_PM, SINGLE_MIN_ODDS)
            if c["date"] == day]
    below = False
    if not pool:
        pool = [c for c in _candidates(SINGLE_LOOSE_PM, SINGLE_LOOSE_ODDS)
                if c["date"] == day]
        below = True
    rows = []
    best = None
    if pool:
        best = max(pool, key=lambda c: (c["pm"] * c["o"] - 1.0, c["pm"],
                                        c["o"]))
        rows = [{"date": best["date"], "home": best["home"],
                 "away": best["away"], "competition": best["comp"],
                 "market": best["market"], "line": best["line"],
                 "selection": best["sel"], "o_1xbet": round(best["o"], 3),
                 "p_model": round(best["pm"], 4),
                 "ev": round(best["pm"] * best["o"] - 1.0, 4),
                 "below_floor": "true" if below else "false"}]
    tmp = OUT_SINGLE + ".tmp"
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=SINGLE_COLS)
        w.writeheader()
        w.writerows(rows)
    os.replace(tmp, OUT_SINGLE)
    s = {"n_legs": len(rows),
         "pick": (f"{best['home']} vs {best['away']}: {best['market']} "
                  f"{best['line']} {best['sel']} @{best['o']:.2f}"
                  if best else None),
         "ev": rows[0]["ev"] if rows else None, "below_floor": below}
    print(f"single {day}: {s['pick']} EV={s['ev']} "
          f"below_floor={below} -> {OUT_SINGLE}")
    return s


def recommend_slip2(day):
    """Produk 2: slip odds ±2, hanya laga tanggal `day`."""
    by = _by_match(_candidates(S2_MIN_PM, S2_MIN_ODDS), {day})
    stats = {}
    best_in, best_near = _search(by, S2_MIN_LEGS, S2_MAX_LEGS,
                                 S2_LO, S2_HI, S2_TARGET, stats=stats)
    best, inb = (best_in, True) if best_in else (best_near, False)
    rows = _write_slip(OUT_SLIP, SLIP_COLS, best, inb)
    s = {"n_legs": len(rows),
         "total_odds": round(best[0], 3) if best else None,
         "joint_prob": round(best[1], 4) if best else None,
         "in_band": bool(best and inb),
         "search_truncated": bool(stats.get("truncated"))}
    print(f"slip2 {day}: {s['n_legs']} kaki | total={s['total_odds']} "
          f"joint={s['joint_prob']} in_band={s['in_band']} -> {OUT_SLIP}")
    return s


def recommend_slip10(day):
    """Produk 3: slip odds ±10; pool diperluas hari demi hari bila perlu."""
    cands = _candidates(S10_MIN_PM, S10_MIN_ODDS)
    base = date.fromisoformat(day)
    best = None
    inb = False
    expanded_to = day
    any_truncated = False
    for k in range(S10_MAX_EXPAND_DAYS + 1):
        upto = (base + timedelta(days=k)).isoformat()
        dates = {(base + timedelta(days=j)).isoformat()
                 for j in range(k + 1)}
        by = _by_match(cands, dates)
        stats = {}
        b_in, b_near = _search(by, S10_MIN_LEGS, S10_MAX_LEGS,
                               S10_LO, S10_HI, S10_TARGET, stats=stats)
        any_truncated = any_truncated or bool(stats.get("truncated"))
        expanded_to = upto
        if b_in is not None:
            best, inb = b_in, True
            break
        # Simpan kandidat terdekat sejauh ini. Tanpa pemotongan, pool
        # yang membesar tidak pernah menghasilkan near yang lebih buruk;
        # DENGAN pemotongan itu bisa terjadi, jadi tahap berikutnya hanya
        # menggantikan bila jaraknya ke target tidak lebih besar.
        if b_near is not None and (best is None or abs(b_near[0] - S10_TARGET)
                                   <= abs(best[0] - S10_TARGET)):
            best = b_near
    rows = _write_slip(OUT_SLIP10, SLIP10_COLS, best, inb,
                       extra={"pool_expanded_to": expanded_to})
    s = {"n_legs": len(rows),
         "total_odds": round(best[0], 3) if best else None,
         "joint_prob": round(best[1], 4) if best else None,
         "in_band": bool(best and inb), "pool_expanded_to": expanded_to,
         "search_truncated": any_truncated}
    print(f"slip10 {day}: {s['n_legs']} kaki | total={s['total_odds']} "
          f"joint={s['joint_prob']} in_band={s['in_band']} "
          f"pool_expanded_to={expanded_to} -> {OUT_SLIP10}")
    return s


def recommend(day=None):
    """Jalankan ketiga produk untuk `day` (default: hari ini, UTC —
    tanggal fixture di seluruh pipeline adalah UTC; audit ronde 7)."""
    day = day or datetime.now(timezone.utc).date().isoformat()
    out = {"date": day,
           "single": recommend_single(day),
           "slip2": recommend_slip2(day),
           "slip10": recommend_slip10(day)}
    # kunci kompatibilitas untuk pemanggil lama (run_daily_shadow):
    out.update({"n_legs": out["slip2"]["n_legs"],
                "total_odds": out["slip2"]["total_odds"],
                "in_band": out["slip2"]["in_band"]})
    return out


if __name__ == "__main__":
    _day = None
    if "--date" in sys.argv:
        _day = sys.argv[sys.argv.index("--date") + 1]
    _r = recommend(_day)
    sys.exit(0 if _r["slip2"]["n_legs"] or _r["single"]["n_legs"] else 1)
