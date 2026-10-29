#!/usr/bin/env python3
"""make_picks_live.py — gun shadow signal engine (Phase 6).

Fitur upcoming depl terhadap strategi tervalidasi (Phase 5 S1):
  - Liga: Top-5 Eropa (E0/D1/I1/SP1/F1)
  - Odds kandang B365: 1.20 <= o_h <= 1.50
  - Model edge (meta prob home - shin fair home): 0.20 <= edge < 0.22

PERINGATAN (2026-10-26): pocket Phase 5 S1 (+3.23% flat) DIVALIDASI OLEH
FIX DE-VIGGING SHIN (sebelumnya sum prob != 1 -> sekarang sum = 1). Dengan formula
benar, filter ini menghasilkan n=0 pick (edge >= 0.20 pada favorit 1.2-1.5 hampir
tidak pernah terjadi). Filter sengaja dibiarkan seperti aslinya agar tidak mengirim
pick pada edge phantom; tidak ada pick yang dihasilkan sampai strategi dgn edge
benar tervalidasi ulang.

Model = meta-logistic (logit input) yang dilatih ulang pada seluruh riwayat
(records_cache), lalu diterapkan ke fixture upcoming. Rekomendasi stake:
flat 1u ( 0.25 fractional Kelly (cap 0.5).

Output: append ke live_shadow_ledger.csv (CSS, actual_outcome/pnl default kosong).
"""

import csv
import json
import os
from datetime import date, datetime, timezone

import numpy as np

import model_features_1x2 as mf
from backtest_picks import _fair_probs, load_records
from football_etl import TOP5

BASE = os.path.dirname(os.path.abspath(__file__))
RECORDS = os.path.join(BASE, "records_cache.jsonl")
PRED = os.path.join(BASE, "predictions_upcoming.csv")
LEDGER = os.path.join(BASE, "live_shadow_ledger.csv")

FIELDS = ["match_id", "date", "league", "home_team", "away_team",
          "odds_home", "odds_draw", "odds_away", "model_prob_home",
          "edge", "recommended_stake_flat", "recommended_stake_kelly",
          "actual_outcome", "pnl_flat", "pnl_kelly"]

# parameter strategi
EDGE_LO, EDGE_HI = 0.20, 0.22
ODDS_LO, ODDS_HI = 1.20, 1.50
KELLY = 0.25


def _logit_clip(p):
    return np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))


def _records_meta():
    """Sidecar records_cache (.meta.json) sebagai dict, atau {}."""
    meta = os.path.splitext(RECORDS)[0] + ".meta.json"
    if os.path.exists(meta):
        try:
            with open(meta, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _records_mode():
    """Mode fit DC yang distamp pada records_cache (sidecar), atau None."""
    return _records_meta().get("dc_fit_mode")


def _data_stamp():
    """Stamp kesegaran all_matches_clean.csv (mtime_ns:ukuran)."""
    try:
        st = os.stat(os.path.join(BASE, "all_matches_clean.csv"))
        return f"{st.st_mtime_ns}:{st.st_size}"
    except OSError:
        return None


def _records_stale():
    """True bila cache dibangun dari mode DC lain ATAU dari data latih
    yang sudah di-refresh sejak cache dibuat."""
    m = _records_meta()
    from model_v2 import DC_FIT_MODE
    if m.get("dc_fit_mode") != DC_FIT_MODE:
        return True
    return m.get("data_stamp") != _data_stamp()


def _fit_meta():
    """Fit model meta (logit input) pada seluruh riwayat."""
    from model_v2 import DC_FIT_MODE
    if not os.path.exists(RECORDS):
        print("! records_cache.jsonl belum ada — membangun otomatis ...")
        from backtest_picks import cache_records
        n = cache_records(RECORDS)
        if not n or not os.path.exists(RECORDS):
            raise RuntimeError("gagal membangun records_cache.jsonl")
    elif _records_stale():
        print(f"! records_cache basi (mode {_records_mode()} vs aktif "
              f"{DC_FIT_MODE}, atau data latih sudah di-refresh) "
              f"— membangun ulang ...")
        from backtest_picks import cache_records
        n = cache_records(RECORDS)
        if not n or not os.path.exists(RECORDS):
            raise RuntimeError("gagal membangun records_cache.jsonl")
    records = load_records(RECORDS)
    n = len(records)
    X = np.full((n, 9), np.nan)
    y = np.empty(n, dtype=np.int64)
    for i, r in enumerate(records):
        X[i, 0] = _logit_clip(r["ph_dc"]); X[i, 1] = _logit_clip(r["pd_dc"])
        X[i, 2] = _logit_clip(r["pa_dc"])
        X[i, 3] = _logit_clip(r["ph_t3"]); X[i, 4] = _logit_clip(r["pd_t3"])
        X[i, 5] = _logit_clip(r["pa_t3"])
        o = r["o"]
        if o:
            for j in range(3):
                X[i, 6 + j] = _logit_clip(1.0 / o[j])
        y[i] = r["yi"]
    return mf._fit_params(X, y), records


def _meta_probs(params, ph_dc, pd_dc, pa_dc, ph_t3, pd_t3, pa_t3, o):
    med, mu, sd, W = params
    row = np.full((1, 9), np.nan)
    row[0, 0] = _logit_clip(ph_dc); row[0, 1] = _logit_clip(pd_dc)
    row[0, 2] = _logit_clip(pa_dc)
    row[0, 3] = _logit_clip(ph_t3); row[0, 4] = _logit_clip(pd_t3)
    row[0, 5] = _logit_clip(pa_t3)
    if o:
        for j in range(3):
            row[0, 6 + j] = _logit_clip(1.0 / o[j])
    return mf._softmax_scores(row, med, mu, sd, W)[0]


def _load_pending_ids():
    if not os.path.exists(LEDGER):
        return set()
    with open(LEDGER, newline="", encoding="utf-8") as f:
        return {r["match_id"] for r in csv.DictReader(f) if r.get("match_id")}


def _append(rows):
    write_header = not os.path.exists(LEDGER) or os.path.getsize(LEDGER) == 0
    with open(LEDGER, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        if write_header:
            w.writeheader()
        for r in rows:
            w.writerow(r)


def _pf(x):
    """float aman: None untuk sel kosong/rusak (bukan exception)."""
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    if not os.path.exists(PRED):
        # None = file hilang (rantai harus menandai gagal). Versi lama
        # mengembalikan 0 yang tak bisa dibedakan dari '0 pick baru
        # yang sah' oleh pemanggil (audit ronde 3).
        print("! predictions_upcoming.csv tidak ada. Jalankan predict_upcoming dulu.")
        return None
    params, records = _fit_meta()
    existing = _load_pending_ids()
    new = []
    with open(PRED, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            div = r.get("div", "")
            if div not in TOP5:
                continue
            # Tanggal file prediksi adalah UTC; membandingkannya ke
            # tanggal LOKAL bisa membuang laga yang belum kickoff pada
            # run manual dini hari (00:00-07:00 WIB).
            if (r.get("date") or "") < datetime.now(timezone.utc).date().isoformat():
                continue  # laga lampau (file prediksi basi) — jangan buat pick
            try:
                oh = float(r.get("b365h") or 0)
                od_ = float(r.get("b365d") or 0)
                oa = float(r.get("b365a") or 0)
            except (TypeError, ValueError):
                continue
            if not (ODDS_LO <= oh <= ODDS_HI):
                continue
            o = (oh, od_, oa)
            if min(o) <= 1.0:
                continue
            # Parsing aman: versi lama float(r["ph_dc"]) tanpa guard dan
            # pemeriksaan None tidak menangkap sel string kosong, jadi
            # satu sel "" meruntuhkan seluruh run sebelum pick apa pun
            # ditambahkan (audit ulang 2026-10-29).
            ph_dc = _pf(r.get("ph_dc")); pd_dc = _pf(r.get("pd_dc"))
            pa_dc = _pf(r.get("pa_dc"))
            ph_t3 = _pf(r.get("ph_t3")); pd_t3 = _pf(r.get("pd_t3"))
            pa_t3 = _pf(r.get("pa_t3"))
            if None in (ph_dc, pd_dc, pa_dc, ph_t3, pd_t3, pa_t3):
                continue
            pm = _meta_probs(params, ph_dc, pd_dc, pa_dc, ph_t3, pd_t3, pa_t3, o)
            fair = list(_fair_probs(o, "shin"))
            edge = pm[0] - fair[0]
            if not (EDGE_LO <= edge < EDGE_HI):
                continue
            mid = f"{div}|{r['date']}|{r['home']}|{r['away']}"
            import hashlib
            mid = hashlib.md5(mid.encode()).hexdigest()[:16]
            if mid in existing:
                continue
            stake_kelly = 0.0
            f_kelly = (pm[0] * oh - 1.0) / (oh - 1.0)
            if f_kelly > 0:
                stake_kelly = round(min(KELLY * f_kelly, 0.5), 4)
            new.append({
                "match_id": mid, "date": r["date"], "league": div,
                "home_team": r["home"], "away_team": r["away"],
                "odds_home": round(oh, 2), "odds_draw": round(od_, 2),
                "odds_away": round(oa, 2),
                "model_prob_home": round(pm[0], 4),
                "edge": round(edge, 4),
                "recommended_stake_flat": 1.0,
                "recommended_stake_kelly": stake_kelly,
                "actual_outcome": "", "pnl_flat": "", "pnl_kelly": "",
            })
            existing.add(mid)
    if new:
        _append(new)
    print(f"live shadow picks baru: {len(new)} (total ledger: {len(existing)})")
    for r in new[:8]:
        print("  +", r["date"], r["league"], f'{r["home_team"]} v {r["away_team"]}',
              "@", r["odds_home"], "edge=%.3f" % r["edge"],
              "kelly=%.2f" % r["recommended_stake_kelly"])
    if len(new) > 8:
        print("  ... +", len(new) - 8, "lagi")
    return len(new)


if __name__ == "__main__":
    main()
