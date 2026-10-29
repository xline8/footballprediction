#!/usr/bin/env python3
"""experiment_eval_corners.py — kalibrasi corner liga (walk-forward per musim).

Mengevaluasi model corner produksi (model_corners_v3, gamma=0.15, r=1.1868)
terhadap HC/AC di all_matches_clean.csv, per musim, per divisi, dan pooled:

  - bias & MAE (mu prediksi vs total corner aktual)
  - ladder kalibrasi: garis 6.5-11.5, mean p_gt vs frekuensi empiris
  - Brier & log-loss pada garis 9.5

Gate koreksi: hanya usulkan ubah model jika bias sistematis konsisten
lintas musim — |bias| > 0.5 corner di >=3 dari 5 divisi searah yang sama,
ATAU deviasi kalibrasi > 5pp di garis tengah (9.5). Jika gate TIDAK
terpenuhi, model TIDAK diubah — cukup lapor.

Run: python experiment_eval_corners.py
"""
import math
import sys
from collections import defaultdict

from model_corners_v3 import (run_wf, mu_cs, pmf_k, k_of, TOP5, LINES,
                              GRID)

GAMMA = 0.15   # parameter produksi (ta/corner_params.json)
R_STAR = 1.186807949137477
SEASONS = ["2019/20", "2020/21", "2021/22", "2022/23", "2023/24",
           "2024/25", "2025/26"]
GATE_DIV = 0.5   # |bias| corner > 0.5
GATE_DIV_N = 3   # di >=3 dari 5 divisi
GATE_CAL_PP = 0.05  # deviasi kalibrasi > 5pp di garis tengah


def p_gt(mu, line):
    return sum(pmf_k(mu, k_of(R_STAR, mu))[int(line) + 1:])


def main():
    print(f"kalibrasi corner | gamma={GAMMA} r={R_STAR:.4f} | seasons={SEASONS}")
    print(f"data: all_matches_clean.csv | divisi: {TOP5}\n")

    # rows per musim: [ {div, y, mu, p9} ... ]  (mu = corner shots CS)
    per_season = {}
    for s in SEASONS:
        rows = run_wf({s})
        rec = []
        for r0 in rows:
            mu = mu_cs(r0, GAMMA)
            rec.append({"div": r0["div"], "y": r0["y"], "mu": mu,
                        "p9": p_gt(mu, 9.5)})
        per_season[s] = rec

    # ---- per musim x divisi: bias/MAE ----
    print("=== bias & MAE per musim x divisi (corner) ===")
    hdr = f"{'div':5s} " + " ".join(f"{s[-7:]:>8s}" for s in SEASONS) + "  pooled"
    print("  " + hdr)
    pool_div = defaultdict(lambda: [0, 0.0, 0.0])
    for d in TOP5:
        line = []
        pooled = pool_div[d]
        for s in SEASONS:
            sub = [r for r in per_season[s] if r["div"] == d]
            n = len(sub)
            bias = sum(r["mu"] - r["y"] for r in sub) / n if n else 0.0
            mae = sum(abs(r["mu"] - r["y"]) for r in sub) / n if n else 0.0
            pooled[0] += n
            pooled[1] += sum(r["mu"] - r["y"] for r in sub)
            pooled[2] += sum(abs(r["mu"] - r["y"]) for r in sub)
            line.append(f"{bias:7.2f}/{mae:7.2f}")
        print(f"  {d:5s} " + " ".join(f"{x:>8s}" for x in line)
              + f"  {pooled[1]/pooled[0]:7.2f}/{pooled[2]/pooled[0]:7.2f}")

    # ---- pooled per musim ----
    print("\n=== pool per musim ===")
    print(f"  {'season':8s} {'n':>6s} {'muCS':>6s} {'akt':>6s} "
          f"{'bias':>6s} {'MAE':>6s}")
    for s in SEASONS:
        rec = per_season[s]
        n = len(rec)
        mu = sum(r["mu"] for r in rec) / n
        y = sum(r["y"] for r in rec) / n
        bias = sum(r["mu"] - r["y"] for r in rec) / n
        mae = sum(abs(r["mu"] - r["y"]) for r in rec) / n
        print(f"  {s:8s} {n:6,d} {mu:6.2f} {y:6.2f} {bias:6.2f} {mae:6.2f}")

    # ---- ladder kalibrasi (pooled semua musim) ----
    print("\n=== ladder kalibrasi (pooled) ===")
    allrec = [r for s in SEASONS for r in per_season[s]]
    print(f"  {'line':>6s} {'n':>8s} {'p_pred':>7s} {'freq':>7s} {'dev':>7s}")
    cal_dev_mid = None
    for ln in LINES:
        preds = [p_gt(r["mu"], ln) for r in allrec]
        p_pred = sum(preds) / len(preds)
        freq = sum(1 for r in allrec if r["y"] > ln) / len(allrec)
        dev = p_pred - freq
        if ln == 9.5:
            cal_dev_mid = dev
        print(f"  {ln:6.1f} {len(allrec):8,d} {p_pred:7.4f} {freq:7.4f} "
              f"{dev:7.4f}")

    # ---- Brier & log-loss di 9.5 ----
    n = len(allrec)
    brier = sum((r["p9"] - (1 if r["y"] > 9.5 else 0)) ** 2 for r in allrec) / n
    logloss = sum(
        -(math.log(max(r["p9"], 1e-12)) if r["y"] > 9.5
          else math.log(max(1 - r["p9"], 1e-12)))
        for r in allrec) / n
    freq95 = sum(1 for r in allrec if r["y"] > 9.5) / n
    print(f"\n=== Brier / log-loss @9.5 === (freq aktual={freq95:.4f})")
    print(f"  Brier={brier:.4f}  log-loss={logloss:.4f}")

    # ---- gate koreksi ----
    print("\n=== gate koreksi ===")
    div_bias = []
    for d in TOP5:
        sub = [r for r in allrec if r["div"] == d]
        bias = sum(r["mu"] - r["y"] for r in sub) / len(sub) if sub else 0.0
        div_bias.append((d, bias))
    same_dir = sum(1 for _, b in div_bias if b > GATE_DIV) - sum(
        1 for _, b in div_bias if b < -GATE_DIV)
    n_strong = max(sum(1 for _, b in div_bias if b > GATE_DIV),
                   sum(1 for _, b in div_bias if b < -GATE_DIV))
    for d, b in div_bias:
        flag = "  <-- over" if b > GATE_DIV else (" <-- under" if b < -GATE_DIV else "")
        print(f"  {d}: bias={b:+.3f}{flag}")
    print(f"  divisi dgn |bias|>{GATE_DIV}: {n_strong}/5 "
          f"(net {same_dir:+d} searah)")
    gate1 = n_strong >= GATE_DIV_N and abs(same_dir) == n_strong
    gate2 = cal_dev_mid is not None and abs(cal_dev_mid) > GATE_CAL_PP
    print(f"  gate A (bias >{GATE_DIV} di >={GATE_DIV_N} divisi searah): "
          f"{'LULUS' if gate1 else 'TIDAK'}")
    print(f"  gate B (deviasi kalibrasi @9.5 >{GATE_CAL_PP*100:.0f}pp): "
          f"{'LULUS' if gate2 else 'TIDAK'} ({cal_dev_mid:+.4f})")
    if gate1 or gate2:
        print("  -> GATE TERPENUHI: periksa usulan koreksi (belum diterapkan).")
    else:
        print("  -> model TIDAK diubah; hanya laporan.")

    return {"gate_a": gate1, "gate_b": gate2, "cal_dev_95": cal_dev_mid}


if __name__ == "__main__":
    sys.exit(main())
