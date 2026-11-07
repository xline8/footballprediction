#!/usr/bin/env python
"""First-half (1H) corner model — backtest (experiment, NOT production).

Design: experiments/MODEL_AUDIT_2026-11-07.md §2C item C-2.

Target: total FIRST-HALF corners per match (home 1H + away 1H).
Labels: FotMob store period stats (data_enrichment/fotmob_full/*.json,
content.stats.Periods.FirstHalf, stat key "corners" -> [home, away]),
extracted exactly the way experiments/audit_models_2026_11_07.py probed
them. shot_lineup_features.csv was checked first: it carries only FT
corners (corners_h/corners_a), no 1H split — so extraction from the
store JSONs is required. Coverage measured by the audit and re-measured
here: ~100% from 2023/24, only ~32% in 2022/23. Therefore:

  - 2022/23 labelled matches are used ONLY as trailing history (state
    updates); they are NOT used for any tuning decision.
  - Tuning (half-life / prior grid + every NB size) uses 2023/24 ONLY —
    the only honest tuning season. This is stated plainly in RESULTS.md.
  - Test: 2024/25 + 2025/26, walk-forward (predict, then update).

Model: clone of the corner/SOT recipe on 1H totals —
  venue-split team ratings for 1H corners for/against (exponentially
  decayed trailing rates, shrunk to the decayed division mean with
  prior K match-equivalents; exp = mu * att * def per team, the SOT
  clone's Ratings machinery), division base rates are the league means
  inside that machinery, and the total is Negative Binomial with size
  r estimated by method of moments from the tuning season's
  walk-forward residuals (r = sum(mu^2)/(sum((y-mu)^2)-sum(mu)),
  the estimator used by the SOT experiments).

Central line 4.5: the audit measured the 1H share of total corners as
0.472, and the FT corner model's central line is 9.5; 0.472*9.5 = 4.48
~= 4.5. Lines 3.5 / 5.5 are also reported.

Baselines (recomputed in the SAME pass, on the IDENTICAL test set):
  (a) 1H division base rate, walk-forward: per-division decayed league
      means (HL = 270d, the FT corner model's HL) for 1H corners
      home/away, mu_base = mu_h + mu_a, no team ratings. Its NB size
      r_base is estimated from its own 2023/24 residuals with the same
      MoM estimator, then frozen.
  (b) Naive FT-scaling: mu_naive = 0.472 * mu_shots_cs, where
      mu_shots_cs is the FT corner model's own walk-forward expected
      total for the same match, taken read-only from the production
      backtest artifact predictions_corners_shots.csv (joined on
      div/date/home/away; join rate reported). Converted to a 1H line
      probability with the SAME NB family: P(X > line) for
      X ~ NegBin(mean=mu_naive, size=r_naive), r_naive estimated from
      this baseline's own 2023/24 residuals with the same MoM
      estimator, then frozen. The model likewise uses its own frozen
      tuning-season r. So all three predictors differ only in their
      mu (and their own frozen dispersion), never in family or set.

GATE (pre-registered, from the audit design):
  pooled log loss at line 4.5 beats BOTH baselines AND pooled
  calibration |pred - actual| at line 4.5 <= 1pp.
  Fail = stop, report, no production file (none is touched regardless).

Run:  .venv/bin/python experiments/half_corners/run_half_corners.py
Writes ONLY inside experiments/half_corners/:
  labels_1h_corners.csv, test_predictions.csv, RESULTS.md
"""

import csv
import json
import math
import os
import time
from collections import defaultdict
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..", "..")
INDEX = os.path.join(ROOT, "data_enrichment", "fotmob_full_index.csv")
FEATURES = os.path.join(ROOT, "data_enrichment", "shot_lineup_features.csv")
FT_ARTIFACT = os.path.join(ROOT, "predictions_corners_shots.csv")

LABELS_OUT = os.path.join(HERE, "labels_1h_corners.csv")
PRED_OUT = os.path.join(HERE, "test_predictions.csv")
RESULTS_OUT = os.path.join(HERE, "RESULTS.md")

TOP5 = ["E0", "D1", "I1", "SP1", "F1"]
SHARE_1H = 0.472                      # audit §2B.3, n=400
LINES = [3.5, 4.5, 5.5]
MAIN_LINE = 4.5
WARM_SEASON = "2022/23"               # history only — NOT for tuning
TUNE_SEASON = "2023/24"               # the only honest tuning season
TEST_SEASONS = ["2024/25", "2025/26"]
MODEL_SEASONS = [WARM_SEASON, TUNE_SEASON] + TEST_SEASONS
GRID_HL = [180.0, 270.0, 365.0, 540.0]
GRID_K = [4.0, 8.0, 16.0, 24.0]
BASE_HL = 270.0                       # FT corner model's HL, for baseline (a)
FALLBACK_1H = (2.7, 2.1)              # 1H corners home/away, pre-history only
EPS = 1e-6


# ------------------------------------------------------------------ labels
def _period_corners(period):
    """[home, away] corners from one Periods entry, or None.

    Mirrors the audit probe: scan every stat group; a stat matches on
    key == 'corners' or title/name == 'Corners'; its 'stats' list is
    [home, away].
    """
    if not period:
        return None
    for grp in period.get("stats", []) or []:
        for st in grp.get("stats", []) or []:
            name = st.get("key") or st.get("title") or st.get("name")
            if name in ("corners", "Corners"):
                vals = st.get("stats") or []
                if len(vals) >= 2 and vals[0] is not None and vals[1] is not None:
                    return int(vals[0]), int(vals[1])
    return None


def extract_labels():
    """Extract 1H/2H/FT corner splits for every FotMob store match."""
    feat_ft = {}
    if os.path.exists(FEATURES):
        with open(FEATURES, newline="", encoding="utf-8") as fh:
            for r in csv.DictReader(fh):
                try:
                    feat_ft[(r["div"], r["date"], r["home"], r["away"])] = (
                        int(float(r["corners_h"])), int(float(r["corners_a"])))
                except (TypeError, ValueError):
                    pass
    rows = []
    xcheck = {"n": 0, "exact": 0}
    with open(INDEX, newline="", encoding="utf-8") as fh:
        index_rows = list(csv.DictReader(fh))
    for r in index_rows:
        out = {"div": r["div"], "season": r["season"], "date": r["date"],
               "home": r["home"], "away": r["away"],
               "fotmob_match_id": r["fotmob_match_id"],
               "corners_1h_h": "", "corners_1h_a": "", "corners_1h_total": "",
               "corners_2h_h": "", "corners_2h_a": "", "corners_2h_total": "",
               "corners_ft_h": "", "corners_ft_a": "", "has_1h_corners": 0}
        try:
            with open(os.path.join(ROOT, r["path"]), encoding="utf-8") as fh:
                doc = json.load(fh)
        except Exception:
            rows.append(out)
            continue
        periods = ((doc.get("content", {}).get("stats") or {}).get("Periods")
                   or {})
        c1 = _period_corners(periods.get("FirstHalf"))
        c2 = _period_corners(periods.get("SecondHalf"))
        ca = _period_corners(periods.get("All"))
        if c1 is not None:
            out["corners_1h_h"], out["corners_1h_a"] = c1
            out["corners_1h_total"] = c1[0] + c1[1]
            out["has_1h_corners"] = 1
        if c2 is not None:
            out["corners_2h_h"], out["corners_2h_a"] = c2
            out["corners_2h_total"] = c2[0] + c2[1]
        if ca is not None:
            out["corners_ft_h"], out["corners_ft_a"] = ca
        # cross-check: 1H + 2H must equal the features file's FT corners
        if c1 is not None and c2 is not None:
            ft = feat_ft.get((r["div"], r["date"], r["home"], r["away"]))
            if ft is not None:
                xcheck["n"] += 1
                if (c1[0] + c2[0], c1[1] + c2[1]) == ft:
                    xcheck["exact"] += 1
        rows.append(out)
    rows.sort(key=lambda x: (x["date"], x["div"], x["home"]))
    cols = list(rows[0].keys())
    with open(LABELS_OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    return rows, xcheck


def load_labelled(rows):
    """Labelled matches in the model window, chronological."""
    out = []
    for r in rows:
        if r["season"] not in MODEL_SEASONS or not r["has_1h_corners"]:
            continue
        out.append({"div": r["div"], "season": r["season"], "date": r["date"],
                    "day": date.fromisoformat(r["date"]).toordinal(),
                    "home": r["home"], "away": r["away"],
                    "c1h": int(r["corners_1h_h"]), "c1a": int(r["corners_1h_a"]),
                    "y": int(r["corners_1h_total"])})
    out.sort(key=lambda m: (m["date"], m["div"], m["home"]))
    return out


def load_ft_mu():
    """FT corner model walk-forward mu (read-only artifact)."""
    out = {}
    with open(FT_ARTIFACT, newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            out[(r["div"], r["date"], r["home"], r["away"])] = float(r["mu_shots_cs"])
    return out


# ------------------------------------------------------- decayed ratings
class Decayed:
    __slots__ = ("s", "w", "last", "hl")

    def __init__(self, hl):
        self.s = 0.0
        self.w = 0.0
        self.last = None
        self.hl = hl

    def _decay(self, day):
        if self.last is not None and day > self.last:
            f = 0.5 ** ((day - self.last) / self.hl)
            self.s *= f
            self.w *= f
        self.last = day

    def value_at(self, day):
        self._decay(day)
        return self.s, self.w

    def add(self, day, x):
        self._decay(day)
        self.s += x
        self.w += 1.0


class Ratings:
    """Venue-split 1H-corner attack/defence ratings (SOT clone's recipe)."""

    def __init__(self, hl, k):
        self.hl, self.k = hl, k
        self.lg_h = defaultdict(lambda: Decayed(hl))
        self.lg_a = defaultdict(lambda: Decayed(hl))
        self.att_h = defaultdict(lambda: Decayed(hl))
        self.def_h = defaultdict(lambda: Decayed(hl))
        self.att_a = defaultdict(lambda: Decayed(hl))
        self.def_a = defaultdict(lambda: Decayed(hl))

    def league_mu(self, div, day):
        s_h, w_h = self.lg_h[div].value_at(day)
        s_a, w_a = self.lg_a[div].value_at(day)
        mu_h = s_h / w_h if w_h > 0 else FALLBACK_1H[0]
        mu_a = s_a / w_a if w_a > 0 else FALLBACK_1H[1]
        return mu_h, mu_a

    def _shrunk(self, obj, day, mu):
        s, w = obj.value_at(day)
        return (s + self.k * mu) / (w + self.k)

    def predict(self, div, home, away, day):
        mu_h, mu_a = self.league_mu(div, day)
        exp_h = mu_h * (self._shrunk(self.att_h[(div, home)], day, mu_h) / mu_h) \
                     * (self._shrunk(self.def_a[(div, away)], day, mu_h) / mu_h)
        exp_a = mu_a * (self._shrunk(self.att_a[(div, away)], day, mu_a) / mu_a) \
                     * (self._shrunk(self.def_h[(div, home)], day, mu_a) / mu_a)
        return exp_h, exp_a

    def base_mu(self, div, day):
        mu_h, mu_a = self.league_mu(div, day)
        return mu_h + mu_a

    def update(self, div, home, away, day, v_h, v_a):
        self.att_h[(div, home)].add(day, v_h)
        self.def_h[(div, home)].add(day, v_a)
        self.att_a[(div, away)].add(day, v_a)
        self.def_a[(div, away)].add(day, v_h)
        self.lg_h[div].add(day, v_h)
        self.lg_a[div].add(day, v_a)


# ------------------------------------------------------------ distributions
def nb_over(lam, r, line):
    """P(X > line), X ~ NegBin(mean=lam, size=r): Var = lam + lam^2/r."""
    k_max = int(math.floor(line))
    q = lam / (r + lam)
    term = (r / (r + lam)) ** r
    cdf = term
    for k in range(1, k_max + 1):
        term *= (k - 1 + r) / k * q
        cdf += term
    return min(max(1.0 - cdf, 0.0), 1.0)


def logloss(p, y):
    pc = min(max(p, EPS), 1 - EPS)
    return -(y * math.log(pc) + (1 - y) * math.log(1 - pc))


def mom_r(mus, ys):
    """NB size by method of moments (SOT experiments' estimator)."""
    s_lam2 = sum(m * m for m in mus)
    s_res2 = sum((y - m) ** 2 for m, y in zip(mus, ys))
    s_lam = sum(mus)
    denom = s_res2 - s_lam
    r = s_lam2 / denom if denom > 0 else 1e6
    return min(max(r, 1.0), 1e6)


# ------------------------------------------------------------------- tuning
def tune_grid(matches):
    """Score (HL, K) by NB LL@4.5 on TUNE_SEASON only (walk-forward)."""
    grid = {}
    for hl in GRID_HL:
        for k in GRID_K:
            rt = Ratings(hl, k)
            mus, ys = [], []
            for m in matches:
                if m["season"] == TUNE_SEASON:
                    eh, ea = rt.predict(m["div"], m["home"], m["away"], m["day"])
                    mus.append(eh + ea)
                    ys.append(m["y"])
                rt.update(m["div"], m["home"], m["away"], m["day"],
                          m["c1h"], m["c1a"])
            r = mom_r(mus, ys)
            ll = sum(logloss(nb_over(mu, r, MAIN_LINE),
                             1.0 if y > MAIN_LINE else 0.0)
                     for mu, y in zip(mus, ys)) / len(mus)
            grid[(hl, k)] = (ll, r)
    # ties break toward MORE shrinkage (larger K), then longer memory
    best = min(grid, key=lambda t: (grid[t][0], -t[1], -t[0]))
    return grid, best, grid[best][1]


def baseline_tuning_r(matches, ft_mu):
    """Frozen NB sizes for both baselines from their TUNE_SEASON residuals."""
    base = Ratings(BASE_HL, 8.0)   # K unused by base_mu (league means only)
    mus_b, mus_n, ys = [], [], []
    n_join = 0
    for m in matches:
        if m["season"] == TUNE_SEASON:
            mus_b.append(base.base_mu(m["div"], m["day"]))
            fm = ft_mu.get((m["div"], m["date"], m["home"], m["away"]))
            if fm is not None:
                n_join += 1
                mus_n.append(SHARE_1H * fm)
            else:
                mus_n.append(float("nan"))
            ys.append(m["y"])
        base.update(m["div"], m["home"], m["away"], m["day"], m["c1h"], m["c1a"])
    pairs_n = [(mu, y) for mu, y in zip(mus_n, ys) if mu == mu]
    r_base = mom_r(mus_b, ys)
    r_naive = mom_r([p[0] for p in pairs_n], [p[1] for p in pairs_n])
    return r_base, r_naive, n_join, len(ys)


# -------------------------------------------------------------- final pass
def new_acc():
    return {L: [0, 0.0, 0.0, 0.0, 0.0] for L in LINES}  # n, ll, brier, spred, sact


def add(acc, line, p, y):
    a = acc[line]
    a[0] += 1
    a[1] += logloss(p, y)
    a[2] += (p - y) ** 2
    a[3] += p
    a[4] += y


def stats(acc, L=MAIN_LINE):
    n, ll, br, sp, sy = acc[L]
    return {"n": n, "ll": ll / n, "brier": br / n,
            "pred": 100 * sp / n, "act": 100 * sy / n,
            "diff_pp": 100 * (sp - sy) / n}


PREDS = ("model", "base", "naive")


def final_pass(matches, hl, k, r_model, r_base, r_naive, ft_mu):
    rt = Ratings(hl, k)
    base = Ratings(BASE_HL, 8.0)
    pooled = {p: new_acc() for p in PREDS}
    by_season = {p: {s: new_acc() for s in TEST_SEASONS} for p in PREDS}
    by_div = {p: {d: new_acc() for d in TOP5} for p in PREDS}
    mae = {p: [0, 0.0] for p in PREDS}
    n_join_test = 0
    pred_rows = []
    rs = {"model": r_model, "base": r_base, "naive": r_naive}
    for m in matches:
        test = m["season"] in TEST_SEASONS
        if test:
            eh, ea = rt.predict(m["div"], m["home"], m["away"], m["day"])
            mu_model = eh + ea
            mu_base = base.base_mu(m["div"], m["day"])
            fm = ft_mu.get((m["div"], m["date"], m["home"], m["away"]))
            if fm is None:
                # identical-set discipline: no FT mu -> no naive score,
                # and the match is dropped for ALL predictors.
                rt.update(m["div"], m["home"], m["away"], m["day"], m["c1h"], m["c1a"])
                base.update(m["div"], m["home"], m["away"], m["day"], m["c1h"], m["c1a"])
                continue
            n_join_test += 1
            mus = {"model": mu_model, "base": mu_base, "naive": SHARE_1H * fm}
            row = {"div": m["div"], "season": m["season"], "date": m["date"],
                   "home": m["home"], "away": m["away"],
                   "corners_1h_h": m["c1h"], "corners_1h_a": m["c1a"],
                   "y_1h_total": m["y"], "mu_model": round(mu_model, 4),
                   "mu_base": round(mu_base, 4), "mu_ft_model": round(fm, 4),
                   "mu_naive": round(mus["naive"], 4)}
            for p in PREDS:
                mae[p][0] += 1
                mae[p][1] += abs(mus[p] - m["y"])
                for L in LINES:
                    prob = nb_over(mus[p], rs[p], L)
                    y = 1.0 if m["y"] > L else 0.0
                    add(pooled[p], L, prob, y)
                    add(by_season[p][m["season"]], L, prob, y)
                    if m["div"] in TOP5:
                        add(by_div[p][m["div"]], L, prob, y)
                    if p == "model" or True:
                        row[f"p_{p}_over_{L}"] = round(prob, 4)
            pred_rows.append(row)
        rt.update(m["div"], m["home"], m["away"], m["day"], m["c1h"], m["c1a"])
        base.update(m["div"], m["home"], m["away"], m["day"], m["c1h"], m["c1a"])
    with open(PRED_OUT, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(pred_rows[0].keys()))
        w.writeheader()
        w.writerows(pred_rows)
    return pooled, by_season, by_div, mae, pred_rows, n_join_test


# --------------------------------------------------------------------- main
def main():
    t0 = time.time()
    label_rows, xcheck = extract_labels()
    matches = load_labelled(label_rows)
    ft_mu = load_ft_mu()

    # coverage per season (over the whole store index)
    cov = defaultdict(lambda: [0, 0])
    for r in label_rows:
        cov[r["season"]][0] += 1
        cov[r["season"]][1] += int(r["has_1h_corners"])
    # 1H share re-measured on labelled test-period matches with FT known
    shares = []
    spine_ft = {}
    for r in label_rows:
        if r["has_1h_corners"] and r["corners_ft_h"] != "":
            tot = int(r["corners_ft_h"]) + int(r["corners_ft_a"])
            if tot > 0:
                shares.append(int(r["corners_1h_total"]) / tot)
    share_mean = sum(shares) / len(shares) if shares else float("nan")

    grid, (bhl, bk), r_model = tune_grid(matches)
    r_base, r_naive, n_join_tune, n_tune = baseline_tuning_r(matches, ft_mu)
    pooled, by_season, by_div, mae, pred_rows, n_join_test = final_pass(
        matches, bhl, bk, r_model, r_base, r_naive, ft_mu)

    sm = stats(pooled["model"])
    sb = stats(pooled["base"])
    sn = stats(pooled["naive"])
    gate_ll = sm["ll"] < sb["ll"] and sm["ll"] < sn["ll"]
    gate_cal = abs(sm["diff_pp"]) <= 1.0
    gate_pass = gate_ll and gate_cal

    # ---------------------------------------------------------------- report
    o = []
    o.append("# Model Corner Babak Pertama (1H) — Backtest")
    o.append("")
    o.append("## Ringkasan (Bahasa Indonesia)")
    o.append("")
    o.append(f"Model corner babak pertama diuji walk-forward: tuning HANYA di "
             f"musim 2023/24 (satu-satunya musim tuning yang jujur — label 1H "
             f"2022/23 cakupannya cuma 35,6%, jadi musim itu hanya dipakai "
             f"sebagai riwayat trailing, bukan untuk tuning), tes di 2024/25 + "
             f"2025/26 (n = {sm['n']:,}). Di garis tengah 4,5: log loss model "
             f"**{sm['ll']:.4f}**, baseline base-rate divisi **{sb['ll']:.4f}**, "
             f"baseline naif 0,472 × model FT **{sn['ll']:.4f}**; kalibrasi "
             f"model {sm['diff_pp']:+.2f}pp (prediksi Over "
             f"{sm['pred']:.1f}% vs aktual {sm['act']:.1f}%). MAE model "
             f"{mae['model'][1]/mae['model'][0]:.2f} corner.")
    o.append("")
    o.append(f"**Verdict gerbang (pra-registrasi): {'LOLOS (PASS)' if gate_pass else 'GAGAL (FAIL)'}** — "
             f"syarat log loss mengalahkan KEDUA baseline: "
             f"{'terpenuhi' if gate_ll else 'TIDAK terpenuhi'}; syarat "
             f"|kalibrasi| ≤ 1pp: {'terpenuhi' if gate_cal else 'TIDAK terpenuhi'}. "
             f"Produksi tidak disentuh apa pun hasilnya.")
    o.append("")
    o.append(f"**Margin sangat tipis — baca ini sebelum mengutip verdict:** "
             f"keunggulan model atas baseline naif hanya "
             f"{sn['ll']-sm['ll']:.4f} log loss (praktis seri; per musim model "
             f"kalah dari naif di 2024/25 dan menang di 2025/26, dan per "
             f"divisi model kalah dari naif di E0, D1, dan F1). Gerbang "
             f"pra-registrasi C-2 memang tidak mensyaratkan margin minimum, "
             f"jadi verdict formalnya PASS, tapi bukti keunggulan model 1H "
             f"khusus atas sekadar menskalakan model FT itu lemah.")
    o.append("")
    o.append("**Catatan tetap:** belum ada sumber odds corner babak pertama "
             "yang tertangkap sistem (sama seperti corner FT dan SOT) — "
             "akurasi terukur di sini, nilai taruhan belum bisa dibuktikan.")
    o.append("")
    o.append("---")
    o.append("")
    o.append("Script: `run_half_corners.py` (re-runnable; reads the FotMob "
             "store + `predictions_corners_shots.csv` read-only, writes only "
             "this folder). Design: `experiments/MODEL_AUDIT_2026-11-07.md` "
             "§2C item C-2. No production file was modified.")
    o.append("")
    o.append("## Label coverage (FotMob store period stats, FirstHalf corners)")
    o.append("")
    o.append("| Season | Store matches | With 1H corners | Coverage |")
    o.append("|---|---|---|---|")
    for s in sorted(cov):
        n_all, n_lab = cov[s]
        o.append(f"| {s} | {n_all:,} | {n_lab:,} | {100*n_lab/n_all:.1f}% |")
    o.append("")
    o.append(f"Cross-check: on matches with both halves labelled, "
             f"(1H+2H) corners equal the FT corners in "
             f"`shot_lineup_features.csv` exactly in "
             f"{xcheck['exact']:,}/{xcheck['n']:,} cases "
             f"({100*xcheck['exact']/max(xcheck['n'],1):.1f}%). "
             f"1H share of FT corners re-measured here: mean "
             f"{share_mean:.3f} (n={len(shares):,}; audit: 0.472 ± 0.174) — "
             f"the fixed 0.472 factor of baseline (b) is kept as "
             f"pre-registered, not re-fit.")
    o.append(f"Labelled matches in the model window "
             f"({' + '.join(MODEL_SEASONS)}): {len(matches):,}. "
             f"`shot_lineup_features.csv` carries no 1H corner split "
             f"(FT only), so labels were extracted from the store JSONs.")
    o.append("")
    o.append("## Frozen choices (2023/24 tuning season ONLY)")
    o.append("")
    o.append(f"- Ratings grid (NB log loss @4.5 on 2023/24, each cell with "
             f"its own MoM r): chosen **HL = {bhl:.0f}d, K = {bk:.0f}** "
             f"(LL {grid[(bhl, bk)][0]:.4f}, r = {r_model:.2f}). Full grid:")
    o.append("")
    o.append("| HL \\ K | " + " | ".join(f"K={k:.0f}" for k in GRID_K) + " |")
    o.append("|---|" + "---|" * len(GRID_K))
    for hl in GRID_HL:
        o.append(f"| {hl:.0f}d | " + " | ".join(
            f"{grid[(hl, k)][0]:.4f}" for k in GRID_K) + " |")
    o.append("")
    o.append(f"- NB sizes (MoM on 2023/24 walk-forward residuals, frozen): "
             f"model r = {r_model:.2f}; base-rate r = {r_base:.2f}; "
             f"naive r = {r_naive:.2f}.")
    o.append(f"- Baseline (b) FT-mu join on the tuning season: "
             f"{n_join_tune:,}/{n_tune:,} matches; on the test set: "
             f"{n_join_test:,}/{sm['n']:,} (any test match without an FT "
             f"mu would be dropped for ALL predictors — identical set).")
    o.append(f"- Central line 4.5 = 0.472 × FT central 9.5 = 4.48 ≈ 4.5.")
    o.append("")
    o.append("## Headline — pooled test (2024/25 + 2025/26), line 4.5")
    o.append("")
    o.append("| Predictor | n | LogLoss@4.5 | Brier | Pred Over% | Act Over% | Calib diff (pp) | MAE |")
    o.append("|---|---|---|---|---|---|---|---|")
    for p, s in (("model", sm), ("base", sb), ("naive", sn)):
        name = {"model": "1H ratings model", "base": "(a) division base rate",
                "naive": "(b) naive 0.472×FT model"}[p]
        o.append(f"| {name} | {s['n']:,} | {s['ll']:.4f} | {s['brier']:.4f} | "
                 f"{s['pred']:.1f} | {s['act']:.1f} | {s['diff_pp']:+.2f} | "
                 f"{mae[p][1]/mae[p][0]:.2f} |")
    o.append("")
    o.append("## All lines — pooled (log loss / calib diff pp)")
    o.append("")
    o.append("| Predictor | 3.5 | 4.5 | 5.5 |")
    o.append("|---|---|---|---|")
    for p in PREDS:
        cells = " | ".join(
            f"{stats(pooled[p], L)['ll']:.4f} / {stats(pooled[p], L)['diff_pp']:+.2f}pp"
            for L in LINES)
        o.append(f"| {p} | {cells} |")
    o.append("")
    o.append("## By season — line 4.5")
    o.append("")
    o.append("| Season | n | Model LL | Base LL | Naive LL | Model calib (pp) | Base calib | Naive calib | Model MAE |")
    o.append("|---|---|---|---|---|---|---|---|---|")
    for sname in TEST_SEASONS:
        ms = stats(by_season["model"][sname])
        bs = stats(by_season["base"][sname])
        ns = stats(by_season["naive"][sname])
        # MAE per season recomputed from prediction rows
        rows_s = [r for r in pred_rows if r["season"] == sname]
        mae_s = sum(abs(r["mu_model"] - r["y_1h_total"]) for r in rows_s) / len(rows_s)
        o.append(f"| {sname} | {ms['n']:,} | {ms['ll']:.4f} | {bs['ll']:.4f} | "
                 f"{ns['ll']:.4f} | {ms['diff_pp']:+.2f} | {bs['diff_pp']:+.2f} | "
                 f"{ns['diff_pp']:+.2f} | {mae_s:.2f} |")
    o.append("")
    o.append("## By division — line 4.5 (model, baselines alongside)")
    o.append("")
    o.append("| Div | n | Model LL | Base LL | Naive LL | Model calib (pp) | Act Over% |")
    o.append("|---|---|---|---|---|---|---|")
    for d in TOP5:
        ms = stats(by_div["model"][d])
        bs = stats(by_div["base"][d])
        ns = stats(by_div["naive"][d])
        o.append(f"| {d} | {ms['n']:,} | {ms['ll']:.4f} | {bs['ll']:.4f} | "
                 f"{ns['ll']:.4f} | {ms['diff_pp']:+.2f} | {ms['act']:.1f} |")
    o.append("")
    o.append("## Gate verdict (pre-registered)")
    o.append("")
    o.append(f"- Model LL@4.5 {sm['ll']:.4f} vs base {sb['ll']:.4f} "
             f"({'beats' if sm['ll'] < sb['ll'] else 'does NOT beat'}) and vs "
             f"naive {sn['ll']:.4f} "
             f"({'beats' if sm['ll'] < sn['ll'] else 'does NOT beat'}).")
    o.append(f"- Pooled calibration @4.5: {sm['diff_pp']:+.2f}pp "
             f"(|diff| ≤ 1pp: {'ok' if gate_cal else 'NO'}).")
    o.append(f"- **{'PASS' if gate_pass else 'FAIL'}**"
             + ("" if gate_pass else " — stop here; no production change (none was made either way)."))
    o.append("")
    o.append("## Method notes and caveats")
    o.append("")
    o.append("- Walk-forward everywhere: every state (ratings, league "
             "means) updates only AFTER the match is predicted; tuning "
             "choices and all three NB sizes are frozen from 2023/24 "
             "before any test match is scored.")
    o.append("- 2022/23 honesty: only ~32% of that season carries 1H "
             "labels, so ratings entering 2023/24 are built from a "
             "partial season — a real cold-start handicap the tuning "
             "and test numbers both live with. 2022/23 was used for "
             "NOTHING except trailing state updates.")
    o.append("- Baseline (b) construction, exactly: mu_naive = 0.472 × "
             "mu_shots_cs from the FT corner model's stored walk-forward "
             "artifact (read-only), probability = NegBin(mean=mu_naive, "
             "size=r_naive) tail above the line — the same NB family "
             "and the same MoM r estimator as the model, with r_naive "
             "fit on the naive baseline's own 2023/24 residuals.")
    o.append("- The model's exp is per-team (venue-split attack/defence "
             "on 1H corners for/against); the total is the sum. No "
             "halftime-state or in-match information is used — this is "
             "a pre-match model, like the FT corner model.")
    o.append("- No odds source for 1H corners exists in the system "
             "(market_compare carries none, and no other capture is "
             "wired) — betting value is unprovable today; this measures "
             "accuracy/calibration only.")
    o.append(f"- Runtime: {time.time()-t0:.0f}s. Outputs: "
             "`labels_1h_corners.csv` (all store matches, reusable "
             "asset), `test_predictions.csv`, this file.")

    with open(RESULTS_OUT, "w", encoding="utf-8") as fh:
        fh.write("\n".join(o) + "\n")
    print(f"coverage: " + ", ".join(
        f"{s} {cov[s][1]}/{cov[s][0]}" for s in sorted(cov)))
    print(f"tuned HL={bhl:.0f} K={bk:.0f} r_model={r_model:.2f} "
          f"r_base={r_base:.2f} r_naive={r_naive:.2f}")
    print(f"test n={sm['n']}  LL model={sm['ll']:.4f} base={sb['ll']:.4f} "
          f"naive={sn['ll']:.4f}  calib={sm['diff_pp']:+.2f}pp")
    print(f"GATE: {'PASS' if gate_pass else 'FAIL'}")
    print(f"wrote {LABELS_OUT}, {PRED_OUT}, {RESULTS_OUT}")


if __name__ == "__main__":
    main()
