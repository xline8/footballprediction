#!/usr/bin/env python3
"""model_features_1x2.py — model 1X2 berbasis fitur, numpy-only, anti-leakage.

Mengambil baris fitur dari features.build_feature_rows (Elo, form, rolling gol/xG,
hari istirahat). Melatih multinomial logistic regression (softmax) dengan L2 dan
mengevaluasinya walk-forward (expansion window) melawan baseline prior konstan.

Ini lapisan eksperimental: TIDAK mengubah output prediksi live. Melatih hanya
pada match yang tanggalnya < bulan uji, dan imputasi/standarisasi juga hanya dari
train — jadi tidak ada yang bocor dari masa depan.

Jalankan:  python model_features_1x2.py [--seasons 2024/25] [--selftest]
"""

import sys

import numpy as np

from features import build_feature_rows
from validation import eval_1x2

YIDX = {"H": 0, "D": 1, "A": 2}
CLASSES = ("H", "D", "A")

FEATURES = [
    "elo_diff",
    "form_pts_h", "form_pts_a",
    "goals_diff_h", "goals_diff_a",
    "xg_diff_h", "xg_diff_a",
    "rest_h", "rest_a",
    "n_played_h", "n_played_a",
]


def _rows_to_arrays(rows):
    """Ubah baris fitur -> (X mentah, y, dates, div). None -> NaN."""
    n = len(rows)
    X = np.full((n, len(FEATURES)), np.nan, dtype=np.float64)
    y = np.empty(n, dtype=np.int64)
    dates = [None] * n
    for i, r in enumerate(rows):
        for j, f in enumerate(FEATURES):
            v = r.get(f)
            if v is not None:
                X[i, j] = float(v)
        y[i] = YIDX[r["ftr"]]
        dates[i] = r["date"]
    return X, y, dates


def _fit_params(Xtr, ytr, l2=1e-3, epochs=120, lr0=0.5):
    """Fit multinomial logistic regression. Mengembalikan par. not model."""
    # imputasi + standarisasi HANYA dari train
    med = np.nanmedian(Xtr, axis=0)
    med = np.where(np.isnan(med), 0.0, med)
    Xtr = np.where(np.isnan(Xtr), med, Xtr)

    mu = Xtr.mean(axis=0)
    sd = Xtr.std(axis=0)
    sd = np.where(sd < 1e-9, 1.0, sd)
    Xtr = (Xtr - mu) / sd
    Xtr = np.column_stack([np.ones(Xtr.shape[0]), Xtr])  # intercept

    d = Xtr.shape[1]
    K = 3
    W = np.zeros((d, K))
    tr = Xtr.shape[0]
    for it in range(epochs):
        scores = Xtr @ W
        scores -= scores.max(axis=1, keepdims=True)
        exp = np.exp(scores)
        sm = exp / exp.sum(axis=1, keepdims=True)
        onehot = np.zeros((tr, K))
        onehot[np.arange(tr), ytr] = 1.0
        grad = Xtr.T @ (sm - onehot) / tr
        grad[1:, :] += 2.0 * l2 * W[1:, :]  # L2 non-intercept
        lr = lr0 * (0.8 ** (it // 30))
        W -= lr * grad
    return med, mu, sd, W


def _softmax_scores(X, med, mu, sd, W):
    """Terapkan model (med,mu,sd,W) pada baris baru; imputasi ts standarisasi dari train."""
    X = np.where(np.isnan(X), med, X)
    X = (X - mu) / sd
    X = np.column_stack([np.ones(X.shape[0]), X])
    s = X @ W
    s -= s.max(axis=1, keepdims=True)
    e = np.exp(s)
    return e / e.sum(axis=1, keepdims=True)


def _fit_multinomial(Xtr, ytr, Xte, l2=1e-3, epochs=120, lr0=0.5):
    """Multi-class logistic regression via gradient descent. numpy-only."""
    med, mu, sd, W = _fit_params(Xtr, ytr, l2, epochs, lr0)
    return _softmax_scores(Xte, med, mu, sd, W)


class FitModel:
    """Predictor siap-pakai, dilatih pada seluruh riwayat (untuk prediksi live).

    Tidak ada kebocoran dalam penggunaan produksi: seluruh data hingga hari ini
    adalah masa lalu. Evaluasi yang membuktikan sinyal tetap memakai walk-forward.
    """

    def __init__(self, Xtr, ytr, l2=1e-3, epochs=120, lr0=0.5):
        self.med, self.mu, self.sd, self.W = _fit_params(
            Xtr, ytr, l2, epochs, lr0)

    def predict(self, Xte) -> np.ndarray:
        return _softmax_scores(Xte, self.med, self.mu, self.sd, self.W)

    def predict_vector(self, vec: dict) -> tuple:
        """vec: dict {nama_fitur: nilai} -> (ph, pd, pa)."""
        row = np.full((1, len(FEATURES)), np.nan)
        for j, f in enumerate(FEATURES):
            v = vec.get(f)
            if v is not None:
                row[0, j] = float(v)
        return tuple(self.predict(row)[0])


def _month_key(date_iso):
    return date_iso[:7]  # YYYY-MM


def evaluate(seasons=None):
    rows = build_feature_rows(limit=None)
    X, y, dates = _rows_to_arrays(rows)

    if seasons:
        keep = [i for i, r in enumerate(rows) if r.get("season") in seasons]
        X, y, dates = X[keep], y[keep], [dates[i] for i in keep]
        rows = [rows[i] for i in keep]

    # bulan uji (terurut)
    months = sorted({_month_key(d) for d in dates})
    # baseline prior = proporsi kelas dari seluruh data (sebagai pembanding)
    prior = np.bincount(y, minlength=3).astype(float)
    prior /= prior.sum()

    pairs_model, pairs_prior = [], []
    for i, m in enumerate(months):
        train_mask = np.array([d < m + "-01" for d in dates])
        test_mask = np.array([_month_key(d) == m for d in dates])
        if train_mask.sum() < 1500 or test_mask.sum() == 0:
            continue
        Xtr, ytr = X[train_mask], y[train_mask]
        Xte, yte = X[test_mask], y[test_mask]
        p_model = _fit_multinomial(Xtr, ytr, Xte)
        for p, yi in zip(p_model, yte):
            pairs_model.append((tuple(p), int(yi)))
        for yi in yte:
            pairs_prior.append((tuple(prior), int(yi)))

    em = eval_1x2(pairs_model)
    ep = eval_1x2(pairs_prior)
    return em, ep


def selftest():
    """Sintetis: dua cluster terpisah -> LR harus belajar, loss turun."""
    rng = np.random.default_rng(0)
    Xtr = np.vstack([rng.normal(-2, 0.5, (200, 3)),
                     rng.normal(0, 0.5, (200, 3)),
                     rng.normal(2, 0.5, (200, 3))])
    ytr = np.repeat([0, 1, 2], 200)
    Xte = np.vstack([rng.normal(-2, 0.5, (50, 3)),
                     rng.normal(0, 0.5, (50, 3)),
                     rng.normal(2, 0.5, (50, 3))])
    yte = np.repeat([0, 1, 2], 50)
    p = _fit_multinomial(Xtr, ytr, Xte)
    acc = float((p.argmax(axis=1) == yte).mean())
    assert acc > 0.8, f"selftest acc {acc} terlalu rendah"
    print(f"  ok selftest: akurasi sintetis {acc:.3f} (diharapkan >0.8)")


def main():
    seasons = None
    if "--seasons" in sys.argv:
        i = sys.argv.index("--seasons")
        seasons = set(sys.argv[i + 1].split(","))
    em, ep = evaluate(seasons)
    print(f"n uji         : {em['n']}")
    print(f"{'metrik':12} {'fitur-model':>10} {'prior':>10}")
    for k, label in (("brier", "brier"), ("log_loss", "log_loss"),
                     ("macro_f1", "macro_f1"), ("accuracy", "accuracy")):
        print(f"{label:12} {em[k]:>10.4f} {ep[k]:>10.4f}")
    print("per-class log-loss (model):", em["per_class_log_loss"])
    print("per-class F1     (model):", em["per_class_f1"])


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        sys.exit(0)
    main()
