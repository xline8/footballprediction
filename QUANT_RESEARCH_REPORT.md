# QUANT RESEARCH REPORT — Football 1X2 / Derivative Market Efficiency

**Audience:** executive / senior quant review. **Project:** pre-match football
outcome prediction & value-betting engine on 70k+ historical matches
(2000s–2025, B365 opening odds baseline).

---

## 1. Executive Summary

We built a leak-free, walk-forward 1X2 match-outcome model and tested whether
any exploitable value remains in the B365/Pinnacle pre-match markets.

**Final verdict: the 1X2 market is effectively efficient.** Our best model
reaches log loss 1.0013 and Brier 0.5986, at the information ceiling set by
the market. But no betting rule we tested (edge thresholds, de-vigging
variants, Kelly staking, contextual/psychological overlays, sharp-book
deviation signals) produces a statistically significant positive ROI. Every
"profitable pocket" discovered along the way dissolved on scrutiny; the worst
was a de-vigging bug that inflated edges into a false +3.23% strategy. The
derived Over/Under 2.5 market shows the same efficiency (hit rate ≈ 50%,
yield ≈ −6% ≈ margin).

**Conclusion:** the calibrated model is useful for ranking, risk, and future
market-scanning, but this dataset cannot support a live value-betting
strategy. Live shadow stays gated at 0 picks by design.

---

## 2. Modeling Milestones

| Phase | Milestone | Result |
|---|---|---|
| Core | Dixon-Coles (DC) bivariate Poisson baseline | log loss 1.0311 |
| Core | T3 feature model (Elo/form/xG/rest) | log loss 1.0287 |
| P4 | Meta-logistic (DC + T3 + market-implied) | log loss 1.0017, Brier 0.5988 |
| P7–8 | Deep feature science (fatigue, xG, motivation) | all fail LL gate → market-info ceiling |
| P9–10 | Decoupled betting policy + contextual overlays | best +6.7% but N=553, bootstrap p=0.216 → not significant |
| P11 | Exogenous enrichment (Pinnacle PS, midweek, rolling xG) | 70k rows joined |
| P12 | Enriched meta (9 → 17 features: dev, ps_fair, midweek) | log loss 1.0013, Brier 0.5986 |

---

## 3. Key Learnings

1. **Shin de-vigging inversion bug.** A reversed bisection made fair
   probabilities sum to ~0.52, producing phantom edges and a false
   +3.23% "profitable pocket" (Phase 5 S1). Fixing it nullified the pocket.
   Lesson: verify calibrated outputs sum to 1.0 before trusting any edge.
2. **The N=553 trap (small-sample P-hacking).** A dynamic-Kelly policy showed
   +6.7% yield and 3/5 positive years, but bootstrap gave p=0.216 on N=553.
   Positive ROI on a few hundred bets is noise; no gate was relaxed on
   statistical grounds.
3. **Soft vs sharp books confirm efficiency.** Pinnacle-vs-B365 deviation
   (B365/PS) carries *no* exploitable signal for 1X2: soft books track sharp
   lines; the deviation filter only thinned the sample toward negative-yield
   subsets. We confirmed the market auto-copies the sharp line.
4. **Context features move edge selection, not calibration.** Fatigue/
   motivation/xG never lowered global log loss but did shift decisions to
   better subsets. That points to post-model overlays, which failed on
   sample-size/significance gates.

---

## 4. Architecture

- **Probability Engine (locked):** DC model outputs λ_home/λ_away/ρ; the meta
  model stacks logits of DC, T3, B365-implied, plus sharp signals (deviation
  B365/PS, Pinnacle shin-fair, midweek flags) via walk-forward multinomial
  logistic. Strict `date < cutoff` grouping prevents leakage.
- **Scoreline Matrix & Derivative Pricing:** `matrix_pricer.py` builds the
  bivariate Poisson matrix and meta-calibrates regions so summed 1X2 marginals
  equal the meta model exactly; Over/Under 2.5 and BTTS probabilities are
  derived from the calibrated matrix.
- **Decoupled Policy Engine:** betting decisions are filtered *after* the model
  (edge thresholds, overlays, staking) so calibration stays intact. Every
  candidate policy must clear dual gates (log-loss safety; fixed-threshold yield
  + bootstrap p<0.05 + minimum N) before going live.
- **Live Shadow:** `run_daily_shadow.py` → `make_picks_live.py` →
  `resolve_and_monitor.py` runs as a daily cron-safe chain (each step isolated
  by try/except). It is deliberately strict: with no validated edge, it emits
  0 picks and records nothing to the ledger.
