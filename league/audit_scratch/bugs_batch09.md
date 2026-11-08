Batch 09 — clear code findings (read-only; no gates executed)

- NL-Eredivisie — league/NL-Eredivisie/engine/goals/run_g_nl.py:17 — The sealed metrics command uses passed or [gate_zero], evaluating sealed 2025/2026 when every dev arm fails; line 18 also permits virgin-predict without a dev guard (PREREG_G_NL requires dev pass; verdict acknowledges the burn).
- NL-Eredivisie — league/NL-Eredivisie/engine/cards/harness.py:61 — read_arms=list(arms or [gate_zero]) explicitly bypasses the dev gate and loads sealed 2025/2026 at line 62 after both arms fail (PREREG_K_NL forbids dead-arm reads; verdict acknowledges fallback burn).
- NL-Eredivisie — league/NL-Eredivisie/engine/corners/core.py:206 — league_base_rate returns count mean/r and harness.make_prediction converts it to NB probabilities, rather than PREREG_C_NL constant prior-season over-10.5 rate; gate_passes consequently tests the wrong baseline (verdict independently corrects outcome).
- NL-Eredivisie — league/NL-Eredivisie/engine/sot/harness.py:128 — choose(out,dev) never uses dev or leg (iii); X4/X6 remain read arms after line 88 drops the sign filter, so automatic selection can export a sign-failing quality arm, contrary to PREREG_S_NL and authoritative Gate Zero shipping verdict.
- NL-Eredivisie — league/NL-Eredivisie/engine/cards/harness.py:102 — best_base considers only base, omitting naive entirely, so virgin_ll_le_best_baseline at line 107 does not enforce the prereg best-of-two baseline leg.
- NO-Eliteserien — league/NO-Eliteserien/engine/cards/harness.py:101 — best_base considers only base, omitting naive, so the following virgin_ll_le_best_baseline check does not implement the prereg best-of-two comparison (current headline verdict unaffected).
- NO-OBOSLigaen — league/NO-OBOSLigaen/engine/cards/harness.py:60 — virgin_metrics filters arms independently and immediately loads 2026 without requiring Gate Zero pass; X8 is dev-passing while GZ is dead, so the exposed virgin-metrics command violates the explicit variants-moot/no-read rule in PREREG_K_NO_OBOS (authoritative verdict did not invoke it).
- PL-Ekstraklasa — league/PL-Ekstraklasa/engine/total_shots/run_t_pl.py:92 — Acc.add stores residual y-p (line 88), but out centers them on mean(p-y); line 93 therefore inflates SE by centering on the opposite mean and calibration_pp has the opposite sign to PREREG_T_PL actual-minus-predicted (verdict corrects the sign only).
- PL-Ekstraklasa — league/PL-Ekstraklasa/engine/cards/harness.py:50 — diff_3_5 is mean(p-y), contrary to config/prereg actual-minus-predicted; exported calibration sign is reversed (authoritative verdict independently uses the required sign).
- PL-Ekstraklasa — league/PL-Ekstraklasa/engine/sot/harness.py:126 — metric_probs reports baseline calibration as mean(p-y), while virgin_metrics uses y-p and PREREG_S_PL requires actual-minus-predicted everywhere; baseline diagnostic signs are inverted.

Findings describe current code paths, including dormant commands; candidate classifications retain authoritative verdict outcomes. No training/dev sealed-season load was identified in the skim. Reference docstrings alone and intentionally inherited reference constants were not classified as bugs.

Engine files actually opened/skimmed by source inspection (some inspected through targeted line extracts):

NL-Eredivisie:
- league/NL-Eredivisie/engine/cards/harness.py
- league/NL-Eredivisie/engine/cards/model.py
- league/NL-Eredivisie/engine/cards/run_k_nl.py
- league/NL-Eredivisie/engine/corners/core.py
- league/NL-Eredivisie/engine/corners/harness.py
- league/NL-Eredivisie/engine/corners/run_c_nl.py
- league/NL-Eredivisie/engine/goals/arms.py
- league/NL-Eredivisie/engine/goals/dc.py
- league/NL-Eredivisie/engine/goals/harness.py
- league/NL-Eredivisie/engine/goals/run_g_nl.py
- league/NL-Eredivisie/engine/sot/harness.py
- league/NL-Eredivisie/engine/sot/model.py
- league/NL-Eredivisie/engine/sot/run_s_nl.py
- league/NL-Eredivisie/engine/total_shots/model.py
- league/NL-Eredivisie/engine/total_shots/run_t_nl.py

NL-TweedeDivisie:
- league/NL-TweedeDivisie/engine/goals/arms.py
- league/NL-TweedeDivisie/engine/goals/dc.py
- league/NL-TweedeDivisie/engine/goals/harness.py
- league/NL-TweedeDivisie/engine/goals/run_g_nltd.py

NO-2Divisjon:
- league/NO-2Divisjon/engine/goals/arms.py
- league/NO-2Divisjon/engine/goals/dc.py
- league/NO-2Divisjon/engine/goals/harness.py
- league/NO-2Divisjon/engine/goals/run_g_no.py

NO-Eliteserien:
- league/NO-Eliteserien/engine/cards/harness.py
- league/NO-Eliteserien/engine/cards/model.py
- league/NO-Eliteserien/engine/cards/run_k_no.py
- league/NO-Eliteserien/engine/corners/core.py
- league/NO-Eliteserien/engine/corners/harness.py
- league/NO-Eliteserien/engine/corners/run_c_no.py
- league/NO-Eliteserien/engine/goals/arms.py
- league/NO-Eliteserien/engine/goals/dc.py
- league/NO-Eliteserien/engine/goals/harness.py
- league/NO-Eliteserien/engine/goals/run_g_no.py
- league/NO-Eliteserien/engine/sot/harness.py
- league/NO-Eliteserien/engine/sot/model.py
- league/NO-Eliteserien/engine/sot/run_s_no.py
- league/NO-Eliteserien/engine/total_shots/model.py
- league/NO-Eliteserien/engine/total_shots/run_t_no.py

NO-OBOSLigaen:
- league/NO-OBOSLigaen/engine/cards/harness.py
- league/NO-OBOSLigaen/engine/cards/model.py
- league/NO-OBOSLigaen/engine/cards/run_k_obos.py
- league/NO-OBOSLigaen/engine/corners/core.py
- league/NO-OBOSLigaen/engine/corners/harness.py
- league/NO-OBOSLigaen/engine/corners/run_c_obos.py
- league/NO-OBOSLigaen/engine/goals/arms.py
- league/NO-OBOSLigaen/engine/goals/dc.py
- league/NO-OBOSLigaen/engine/goals/harness.py
- league/NO-OBOSLigaen/engine/goals/run_g_obos.py
- league/NO-OBOSLigaen/engine/sot/harness.py
- league/NO-OBOSLigaen/engine/sot/model.py
- league/NO-OBOSLigaen/engine/sot/run_s_obos.py
- league/NO-OBOSLigaen/engine/sot/virgin.py
- league/NO-OBOSLigaen/engine/sot/write_predictions.py
- league/NO-OBOSLigaen/engine/total_shots/model.py
- league/NO-OBOSLigaen/engine/total_shots/run_t_obos.py

NZ-Championship:
- league/NZ-Championship/engine/goals/arms.py
- league/NZ-Championship/engine/goals/dc.py
- league/NZ-Championship/engine/goals/harness.py
- league/NZ-Championship/engine/goals/run_g_nz.py

PA-LPF:
- league/PA-LPF/engine/goals/arms.py
- league/PA-LPF/engine/goals/dc.py
- league/PA-LPF/engine/goals/harness.py
- league/PA-LPF/engine/goals/run_g_pa_lpf.py

PE-Liga1:
- league/PE-Liga1/engine/cards/harness.py
- league/PE-Liga1/engine/cards/model.py
- league/PE-Liga1/engine/cards/run_k_pe.py
- league/PE-Liga1/engine/corners/core.py
- league/PE-Liga1/engine/corners/harness.py
- league/PE-Liga1/engine/corners/run_c_pe.py
- league/PE-Liga1/engine/goals/arms.py
- league/PE-Liga1/engine/goals/dc.py
- league/PE-Liga1/engine/goals/harness.py
- league/PE-Liga1/engine/goals/run_g_pe.py
- league/PE-Liga1/engine/sot/harness.py
- league/PE-Liga1/engine/sot/model.py
- league/PE-Liga1/engine/sot/run_s_pe.py
- league/PE-Liga1/engine/total_shots/model.py
- league/PE-Liga1/engine/total_shots/run_t_pe.py

PL-Ekstraklasa:
- league/PL-Ekstraklasa/engine/cards/harness.py
- league/PL-Ekstraklasa/engine/cards/model.py
- league/PL-Ekstraklasa/engine/cards/run_k_pl.py
- league/PL-Ekstraklasa/engine/corners/core.py
- league/PL-Ekstraklasa/engine/corners/harness.py
- league/PL-Ekstraklasa/engine/corners/run_c_pl.py
- league/PL-Ekstraklasa/engine/goals/arms.py
- league/PL-Ekstraklasa/engine/goals/dc.py
- league/PL-Ekstraklasa/engine/goals/harness.py
- league/PL-Ekstraklasa/engine/goals/run_g_pl.py
- league/PL-Ekstraklasa/engine/sot/harness.py
- league/PL-Ekstraklasa/engine/sot/model.py
- league/PL-Ekstraklasa/engine/sot/run_s_pl.py
- league/PL-Ekstraklasa/engine/total_shots/model.py
- league/PL-Ekstraklasa/engine/total_shots/run_t_pl.py

PL-IILiga:
- league/PL-IILiga/engine/goals/arms.py
- league/PL-IILiga/engine/goals/dc.py
- league/PL-IILiga/engine/goals/harness.py
- league/PL-IILiga/engine/goals/run_g_plii.py

PL-ILiga:
- league/PL-ILiga/engine/goals/arms.py
- league/PL-ILiga/engine/goals/dc.py
- league/PL-ILiga/engine/goals/harness.py
- league/PL-ILiga/engine/goals/run_g_pl_iliga.py

PT-Liga3:
- league/PT-Liga3/engine/goals/arms.py
- league/PT-Liga3/engine/goals/dc.py
- league/PT-Liga3/engine/goals/harness.py
- league/PT-Liga3/engine/goals/run_g_pt3.py

PT-LigaPortugal:
- league/PT-LigaPortugal/engine/cards/common.py
- league/PT-LigaPortugal/engine/cards/run_k_pt.py
- league/PT-LigaPortugal/engine/cards/virgin_k_pt.py
- league/PT-LigaPortugal/engine/corners/common.py
- league/PT-LigaPortugal/engine/corners/run_c_pt.py
- league/PT-LigaPortugal/engine/goals/run_g_pt.py
- league/PT-LigaPortugal/engine/goals/virgin_g_pt.py
- league/PT-LigaPortugal/engine/sot/common.py
- league/PT-LigaPortugal/engine/sot/run_s_pt.py
- league/PT-LigaPortugal/engine/sot/virgin_s_pt.py
- league/PT-LigaPortugal/engine/total_shots/common.py
- league/PT-LigaPortugal/engine/total_shots/run_t_pt.py
- league/PT-LigaPortugal/engine/total_shots/virgin_t_pt.py
