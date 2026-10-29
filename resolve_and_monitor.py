#!/usr/bin/env python3
"""resolve_and_monitor.py — selesaikan & pantau live shadow ledger (Phase 6).

1. Baca live_shadow_ledger.csv; baris dgn actual_outcome kosong = pending.
2. Cocokkan dengan hasil pertandingan di all_matches_clean.csv (via load_matches).
3. Selesaikan outcome (H/D/A), hitung PnL flat & Kelly, update baris.
4. Tampilkan ringkasan CLI: Historical Backtest vs Live Shadow.
"""

import csv
import os

from football_etl import load_matches, normalize_name

BASE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(BASE, "live_shadow_ledger.csv")
FIELDS = ["match_id", "date", "league", "home_team", "away_team",
          "odds_home", "odds_draw", "odds_away", "model_prob_home",
          "edge", "recommended_stake_flat", "recommended_stake_kelly",
          "actual_outcome", "pnl_flat", "pnl_kelly"]

# Benchmark historis — META thr 0.02, de-vigging SHIN yang SUDAH DIFIX.
# Catatan: pocket +3.23% (Phase 5 S1) tidak bertahan setelah fix shin (n=0).
# Acuan jujur saat ini adalah yield global model meta yang masih negatif.
BENCH = {
    "flat": {"n": 17093, "win_rate": 0.3793, "yield": -0.0377},
    "kelly": {"n": 17093, "win_rate": 0.3793, "yield": -0.0377},
}


def _result_map():
    """(div, date_iso, home_norm, away_norm) -> ftr (H/D/A)."""
    out = {}
    for m in load_matches():
        if not m.get("ftr") or m["ftr"] not in ("H", "D", "A"):
            continue
        d = m.get("date")
        ds = str(d)[:10] if not isinstance(d, str) else d[:10]
        out[(m.get("div"), ds, m.get("home"), m.get("away"))] = m["ftr"]
    return out


def resolve(rows, rmap):
    resolved = 0
    for r in rows:
        if r["actual_outcome"]:
            continue
        home = normalize_name(r["home_team"]); away = normalize_name(r["away_team"])
        key = (r["league"], r["date"][:10], home, away)
        ftr = rmap.get(key)
        if not ftr:
            continue  # hasil belum ada -> biarkan pending
        r["actual_outcome"] = ftr
        oh = float(r["odds_home"])
        win = ftr == "H"
        r["pnl_flat"] = round(oh - 1.0, 4) if win else round(-1.0, 4)
        k = float(r["recommended_stake_kelly"] or 0.0)
        r["pnl_kelly"] = round(k * (oh - 1.0), 4) if win else round(-k, 4)
        resolved += 1
    return resolved


def _write(rows):
    with open(LEDGER, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def summary(rows):
    pending = [r for r in rows if not r["actual_outcome"]]
    done = [r for r in rows if r["actual_outcome"]]
    print("=" * 70)
    print("LIVE SHADOW — PERFORMANCE")
    print("=" * 70)
    print(f"total picks : {len(rows)} | pending: {len(pending)} | resolved: {len(done)}")
    if not done:
        print("Belum ada pick yang terselesaikan.")
        return
    # flat
    staked = float(len(done))
    profit = sum(float(r["pnl_flat"]) for r in done)
    wins = sum(1 for r in done if r["actual_outcome"] == "H")
    # kelly — dihitung HANYA dari baris ber-stake Kelly: win rate dari
    # baris yang sama, yield = profit Kelly / total stake Kelly. Versi
    # lama membagi wins semua baris dengan n Kelly (bisa > 1.0) dan
    # mencetak yield sebagai profit flat / profit Kelly.
    rows_k = [r for r in done if float(r["recommended_stake_kelly"] or 0) > 0]
    n_k = len(rows_k)
    k_staked = sum(float(r["recommended_stake_kelly"] or 0) for r in rows_k)
    k_profit = sum(float(r["pnl_kelly"]) for r in rows_k)
    k_wins = sum(1 for r in rows_k if r["actual_outcome"] == "H")
    print()
    print(f"{'metrik':14} {'Live flat':>12} {'Live kelly':>12} {'Hist flat':>10} {'Hist kelly':>10}")
    print(f"{'n':14} {len(done):>12} {n_k:>12} {BENCH['flat']['n']:>10} {BENCH['kelly']['n']:>10}")
    print(f"{'win rate':14} {wins/len(done):>12.3f} {k_wins/n_k if n_k else 0:>12.3f} "
          f"{BENCH['flat']['win_rate']:>10.3f} {BENCH['kelly']['win_rate']:>10.3f}")
    print(f"{'yield':14} {profit/staked:>12.4%} {k_profit/k_staked if k_staked else 0:>12.4%} "
          f"{BENCH['flat']['yield']:>10.4%} {BENCH['kelly']['yield']:>10.4%}")


def main():
    if not os.path.exists(LEDGER):
        print("! ledger belum ada. Jalankan make_picks_live.py dulu.")
        return
    with open(LEDGER, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    rmap = _result_map()
    n = resolve(rows, rmap)
    if n:
        _write(rows)
        print(f"resolved {n} picks -> ledger diupdate.")
    summary(rows)


if __name__ == "__main__":
    main()
