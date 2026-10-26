#!/usr/bin/env python3
"""validation.py — proper scoring rules & evaluasi bersama untuk semua model.

Satu sumber untuk metrik yang dipakai pipeline prediksi (1X2/OU/AH/corner):
- Brier score (strictly proper)
- Log loss (strictly proper), termasuk per-kelas (draw sering paling sulit)
- Accuracy (hanya sebagai pendamping, bukan metrik utama)
- Tabel kalibrasi (reliability)
- Pembagi walk-forward (expansion-window, time-series) — bukan K-Fold acak

Penggunaan:
    from validation import eval_1x2, calibration_table, walk_forward_groups
"""

import math
from collections import defaultdict

YIDX = {"H": 0, "D": 1, "A": 2}
EPS = 1e-12


def brier3(p, yi):
    """Brier score untuk klasifikasi 3-kelas (0 = sempurna)."""
    return sum((p[k] - (1.0 if k == yi else 0.0)) ** 2 for k in range(3))


def logloss3(p, yi):
    """Log loss 3-kelas (strictly proper)."""
    return -math.log(max(p[yi], EPS))


def accuracy3(p, yi):
    """Accuracy (pendamping saja)."""
    return int(max(range(3), key=lambda k: p[k]) == yi)


def eval_1x2(pairs):
    """Evaluasi 1X2: Brier, log loss total & per-kelas, accuracy.

    Args:
        pairs: iterable dari ((ph, pd, pa), yi). yi dalam {0,1,2}.
    Returns:
        dict ringkasan.
    """
    n = 0
    brier = ll = acc = 0.0
    cls_ll = [0.0, 0.0, 0.0]
    cls_n = [0, 0, 0]
    cm = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]  # [true][pred]
    for p, yi in pairs:
        n += 1
        brier += brier3(p, yi)
        ll += logloss3(p, yi)
        acc += accuracy3(p, yi)
        cls_ll[yi] += logloss3(p, yi)
        cls_n[yi] += 1
        cm[yi][max(range(3), key=lambda k: p[k])] += 1
    if not n:
        return {"n": 0}

    # F1 per-kelas + macro (kelas draw biasanya sangat imbalanced).
    per_class_f1 = {}
    for i, k in enumerate(("H", "D", "A")):
        tp = cm[i][i]
        fp = sum(cm[j][i] for j in range(3)) - tp
        fn = sum(cm[i][j] for j in range(3)) - tp
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        per_class_f1[k] = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    macro_f1 = (sum(per_class_f1.values()) / 3.0
                if per_class_f1 else float("nan"))

    return {
        "n": n,
        "brier": brier / n,
        "log_loss": ll / n,
        "accuracy": acc / n,
        "brier_benchmark": 0.6667,  # prediksi konstan (1/3,1/3,1/3)
        "macro_f1": macro_f1,
        "per_class_f1": per_class_f1,
        "per_class_log_loss": {
            k: (cls_ll[i] / cls_n[i] if cls_n[i] else float("nan"))
            for i, k in enumerate(("H", "D", "A"))
        },
        "per_class_n": dict(zip(("H", "D", "A"), cls_n)),
    }


def calibration_table(entries, nbins=10):
    """Tabel reliabilitas untuk probabilitas biner.

    Args:
        entries: iterable dari (prob_predicted, label_biner) dengan label dalam {0,1}.
    Returns:
        list of (lo, hi, n, mean_pred, observed_freq).
    """
    bins = [[] for _ in range(nbins)]
    for p, y in entries:
        idx = min(int(p * nbins), nbins - 1)
        bins[idx].append((p, 1.0 if y else 0.0))
    out = []
    for i, sel in enumerate(bins):
        if not sel:
            continue
        lo, hi = i / nbins, (i + 1) / nbins
        mean_p = sum(x[0] for x in sel) / len(sel)
        freq = sum(x[1] for x in sel) / len(sel)
        out.append((lo, hi, len(sel), mean_p, freq))
    return out


def walk_forward_groups(matches, by_div, seasons, freq="m"):
    """Pembagi expansion-window untuk time-series CV (bukan K-Fold).

    Setiap grup = satu (divisi, periode) dari musim `seasons`. Model dilatih
    hanya pada match yang tanggalnya < tanggal match pertama dalam grup.
    freq: 'm' = bulanan, 'w' = mingguan, else = harian.
    Returns:
        dict: key -> list index match (di `matches`).
    """
    groups = defaultdict(list)
    for i, m in enumerate(matches):
        if m["season"] not in seasons:
            continue
        d = m["date"]
        if freq == "m":
            key = (m["div"], d.year, d.month)
        elif freq == "w":
            iso = d.isocalendar()
            key = (m["div"], iso[0], iso[1])
        else:
            key = (m["div"], d.year, d.month, d.day)
        groups[key].append(i)
    return dict(groups)
