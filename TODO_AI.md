# Improvement Backlog (autonomous loop)

Status legend: `[ ]` open · `[x]` done

## Current state (baseline)

- **Leakage control**: already enforced — walk-forward groups (`validation.walk_forward_groups`), strict `date < cutoff` in `run_wf`, state updated only post-match in `features.build_feature_rows`. Move on.
- **Proper metrics**: `validation.eval_1x2` reports Brier, log loss, per-class log loss, accuracy. Missing **F1** (draw class is heavily imbalanced).
- **Features**: `features.py` builds Elo / form / rolling-goal / rolling-xG / rest-day features, leak-free, but **not wired into any model** (experimental layer).
- **Dependencies**: numpy only. No scipy, no sklearn. Any new model must be numpy-only.
- **Freshness**: no guard for stale data/odds — pipeline silently runs on old snapshots.

## Prioritized backlog

- [x] **T1 — F1 scoring in validation.py.** Add per-class + macro F1 to `eval_1x2`; extend `test_core.py`. *Rationale: draws are the hard, imbalanced class; accuracy/LL alone hide it.* (validated: test_core.py hij, macro-F1==1.0 on perfect predictions)
- [x] **T2 — Data freshness guard.** In `pipeline_orchestrator.step_check_data`, warn loudly when `all_matches_clean.csv` or the latest fixture snapshot is older than N days. Non-fatal (warning) so runs still proceed, but surfaced. *Rationale: stale data => confidently-wrong picks.* (validated: step_check_data runs, `freshness_warnings` returned, 70,425 matches loaded)
- [x] **T3 — Numpy-only leak-free feature model.** New `model_features_1x2.py`: multinomial logistic regression over feature rows (`elo_diff`, form, rolling-goal/xG diff, rest days), trained walk-forward, evaluated against a constant-prior baseline on the same groups. Proves Elo/xG/form/rest carry signal. Does **not** change live betting outputs (kept gated). *Rationale: the one big unused asset is the feature layer.* (validated: selftest acc 1.000; walk-forward over 68,763 matches: brier 0.617 vs prior 0.651, log-loss 1.029 vs 1.076, macro-F1 0.354 vs 0.201)
- [x] **T4 — Syntax/lint gate.** `python -m py_compile` on every module; if `ruff` present, run it. Fix anything that fails. *Rationale: cheapest regression net before any change lands.* (validated: all modules compile clean; test_core green)
- [x] **T5 — Live shadow system (Phase 6).** `make_picks_live.py` + `live_shadow_ledger.csv` + `resolve_and_monitor.py` + `run_daily_shadow.py` built & committed. **PAUSED**: de-vigging shin di-fix (see EXPERIMENTS_LOG KOREKSI); pocket Phase 5 S1 +3.23% divalidasi (n=0). Filter sengaja menghasilkan 0 pick sampai strategi dengan edge benar divalidasi ulang.
- [ ] **T6 — Cari ulang edge bernilai dgn shin benar.** Setelah fix, tidak ada pocket ROI positif yang stabil (terbaik top5 2.6-3.5 +1.88% tapi noise temporal). Lever berikutnya: model lebih tajam sebelum ekstraksi edge (fitur/kalibrasi), bukan tuning threshold/de-vigging.
- [ ] **T7 — Data enrichment (Phase 11) selesai dibangun** (`data_enrichment/`, `all_matches_enriched.csv`). Blocker terbuka: (a) understat tidak andal → perlu API kunci/izin atau scrape stabil; (b) fixture Eropa asli (UCL/UEL/UECL) tidak ada → cari sumber jadwal kompetisi klub Eropa; (c) hanya 1 snapshot odds → cari closing/opening odds dua waktu untuk CLV sejati. Setelah (b)/(c) tersedia, build ulang fitur `midweek_fatigue_flag` & CLV dengan data nyata.
- [ ] **T8 — Validasi fitur enriched terhadap pipeline prediksi.** Integrasikan kolom baru `all_matches_enriched.csv` (ps_*, midweek_flag, rolling_xg_diff) ke `records_cache` / meta model via walk-forward, uji gerbang LL & yield mng protokol Phase 7/8.

## Notes

- The live DC/corner/value-bet path must keep producing identical outputs unless a task explicitly says a.
- Each task ends with a runnable validation (test or CLI run) and the TODO row flipped to `[x]`.
