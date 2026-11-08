# EC-SerieA — STATUS

- Status: SELESAI — Fase 7 deliver (koordinator); semua verdict ditulis, tidak ada yang ship
- Liga: EC-SerieA (Ecuador Serie A, FotMob 246)
- Fase saat ini: Fase 7 selesai — deliverable di outbox-muse2/EC-SerieA/ + RESULT.md + pos done di papan
- Terakhir diperbarui: 2026-11-10 oleh sub-agen Muse-2 (fase 6)
- Referensi commit pra-registrasi: 1a2eb966f78fe43570c2f4a1177bf27b14ba2a6e (branch wip-ec-seriea, 2026-11-10 04:00:07 UTC / 11:00:07 WIB) — SEBELUM fitting apa pun
- Pos jatah di papan: issue #1 komentar 6758056896
- Data: release bundle-ec-seriea, `ecuador_slice.tar.gz` (1.565 match JSON, musim 2021–2026), terunduh ke `raw/`, terekstrak ke `data_enrichment/fotmob_world/Ecuador/Serie A/`
- Split yang dibekukan: dev ≤ 2024, virgin = 2025 (n=312), 2026 cadangan konfirmasi (belum disentuh)

## Sudah selesai

- Fase 0: workspace mirror lengkap; 1.565/1.565 JSON terverifikasi per musim (242×4 + 312 + 285); index disalin ke `data_enrichment/fotmob_world_index.csv`.
- Fase 1: `league/EC-SerieA/data/build_data.py` + `ec_matches.csv` (1.565 baris) + `ec_team_matches.csv` (3.130 baris); jumlah CSV == index; 3 spot-check lawan raw JSON lolos (3528006, 4412193, 4720459).
- Fase 2: `analysis/` lengkap — DATA_UNDERSTANDING.md, PREPROCESSING.md, EDA.md, FEATURES.md, MODEL_DESIGN.md, `eda.py`, `make_charts.py`, `charts/` (4 PNG), `eda_summary.json`, `inventory_summary.json`; `config.yaml` dibekukan (hanya goals_1h_share 0,4616; konstanta halves lain null).
- Temuan sentral: stats feed HANYA ada 2025+ (0% 2021–2023, 1 match 2024, 311/312 2025, 285/285 2026). Dev ≤2024 tidak punya target stats sama sekali → S/C/K/T NOT-BUILDABLE di bawah split beku. G-EC satu-satunya yang buildable (DC goals-only, warm-up 2021, scored 2022–2024 n=726, OU 2.5, arms Gate Zero + ENTRANT).

## Langkah berikutnya persis

1. Fase 3 — SELESAI: prereg G-EC (`prereg/PREREG_G_EC.md`: Gate Zero + ENTRANT, baselines climatology + naive trailing-10) + prereg not-buildable S/C/K/T; push ke branch `wip-ec-seriea` commit 1a2eb96 SEBELUM fitting apa pun.
2. Fase 4 — SELESAI: engine G-EC dievaluasi dev saja (n=726); dev gate FAIL (OU2.5 LL 0.7036 vs klimatologi 0.6941). Fase 5 — virgin TIDAK dibaca (tidak ada arm lolos dev; tidak ada results_virgin.json). Fase 6 — SELESAI: 5 verdict (G-EC FAIL; S/C/K/T not-buildable) + config.yaml lengkap. Fase 7 — deliver ke outbox + RESULT.md + pos done di papan (koordinator, bukan sub-agen ini).
3. Fase 7 — SELESAI: deliverable disalin ke outbox-muse2/EC-SerieA/ di main + RESULT.md + pos done di papan (koordinator).

## Catatan pemulihan

- PROGRESS.md (folder workspace liga) = log koordinator; board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025) dibaca tepat SEKALI per kandidat lolos dev (hanya G-EC); 2026 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan sentuh workspace RS-SuperLiga (agen lain bekerja paralel).
