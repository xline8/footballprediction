# UY-LigaAUF — STATUS

- Status: SELESAI — Fase 7 (deliver; menunggu verifikasi Jarvis)
- Liga: UY-LigaAUF (Uruguay Liga AUF Uruguaya, tier 1, FotMob 161)
- Fase saat ini: Fase 7 SELESAI — deliverable di outbox-muse2/UY-LigaAUF/ (main), menunggu verifikasi Jarvis; koordinator memposting done di papan
- Terakhir diperbarui: 2026-11-10 14:30 WIB oleh sub-agen Muse-2
- Referensi commit pra-registrasi: 7d43257df3460bcfa1bf07c8c94d2ff4466f2074 (branch wip-uy-ligaauf, push SEBELUM fitting apa pun)
- Pos jatah di papan: issue #1 komentar 6761046100
- Data: release bundle-uy-liga (1.717 match, musim kalender 2021–2026; dev ≤2024 n=1136, virgin 2025 n=300, cadangan 2026 n=281 belum disentuh)
- Split yang disarankan BRIEF: dev ≤ 2024, virgin = 2025 (n=300), 2026 cadangan konfirmasi (belum disentuh)
- Scores-only: stats feed 0% semua musim, shotmap 0%; hanya G buildable; S/C/K/T not-buildable (konfirmasi absen di EDA, jangan berburu stats feed yang tidak ada)

## Yang sudah selesai

- Fase 0: release bundle-uy-liga diekstrak ke data_enrichment/fotmob_world/Uruguay/; 1.717 JSON cocok dengan index_161.csv (0 hilang); musim 2021:241, 2022:298, 2023:300, 2024:297, 2025:300, 2026:281.
- Fase 1: build_data.py (adaptasi QA) → data/uy_matches.csv (1.717 baris = index) + data/uy_team_matches.csv (3.434 baris), 26 team id, 16 tim/musim. Spot-check 3 JSON mentah lolos. 2 mismatch skor-vs-events (3834312 laga awarded 0-3, event 2-1; 4425121 scoreStr 5-0 vs 6 event gol — scoreStr otoritatif). 38 laga tanpa events (15+20+3 di 2021–2023). Variasi nama tim dikanonikalisasi (Progreso, Peñarol, Central Español). Stats feed 0/1717, shotmap 0/1717, referee 0/1717. Plain Yellow events HANYA dari 2023 (2021–2022: 0) → target yellows event-feed terputus di dalam dev (alasan K not-buildable).
- Snapshot WIP Fase 1 → branch wip-uy-ligaauf (commit dcc1cd6).
- Fase 4: engine G dijalankan dev-only (UY_DEV_ONLY=1): Gate Zero 1X2 LL 1.0705 / RPS 0.2228 / OU2.5 LL 0.6869 vs klimatologi 1.0939/0.2305/0.6806 dan naive 1.1465/0.2280/0.7296 — GAGAL gerbang dev di leg OU saja; ENTRANT 1.0753/0.2244/0.6858 juga gagal (leg iii 0/3). Vonis G-UY: FAIL (dev gate).
- Fase 5: DILEWATI — virgin 2025 TIDAK dibaca (tidak ada results_virgin.json / virgin_rows_* / fitted_params_virgin.json); 2026 tidak disentuh.
- Fase 6: verdicts (G FAIL dev gate; S/C/K/T not-buildable) + config.yaml (halves goals 0.4276; count-market null).
- Fase 7: RESULT.md ditulis; deliverable lengkap di outbox-muse2/UY-LigaAUF/ (commit main 4902428); snapshot final WIP → wip-uy-ligaauf (ef8946f). TIDAK ADA yang ship dari UY-LigaAUF.
- Fase 3: pra-registrasi lengkap — PREREG_G_UY.md (Gate Zero + ENTRANT, offset log attack −0.1178 / defence −0.1188, virgin 2025 n=300) + PREREG_S/C/K/T_UY.md (not-buildable, alasan beku). Push ke wip-uy-ligaauf SEBELUM fitting apa pun (commit menyusul di bawah).
- Fase 2: dokumen langkah 1–6 lengkap (DATA_UNDERSTANDING, PREPROCESSING, EDA, FEATURES, MODEL_DESIGN) + eda_summary.json + inventory_summary.json + 4 charts. Temuan kunci: stats 0%/shotmap 0%/referee 0% semua musim; goals 1H share dev 0.4276 (n=2664); split-half r GF 0.588 / GA 0.809; entrant 9 transisi (GF −0.128, GA +0.145; offset log attack −0.1178, defence −0.1188); line OU2.5 (over 0.4045 dev scored n=895); K not-buildable karena Yellow events hanya dari 2023 (definition break di dev).

## Langkah berikutnya persis

1. SELESAI — tidak ada langkah berikutnya; menunggu verifikasi Jarvis di papan (komentar koordinator). Bila Jarvis meminta perbaikan, kerjakan dari STATUS ini.
3. Fase 4 — engine G (Dixon-Coles Gate Zero + SHRINK; X1 blend goals-only, tanpa xG), evaluasi dev saja. Fase 5 — virgin SEKALI bila lolos dev. Fase 6 — verdicts + config. Fase 7 — deliver ke outbox + RESULT.md + lapor ke koordinator (koordinator yang memposting done di papan).
4. Di SETIAP perpindahan fase perbarui STATUS.md ini (kedua salinan: workspace + outbox), segarkan WORKER.lock, push snapshot WIP ke branch wip-uy-ligaauf via clone ~/workspace/league-work/.snapshot-repo.

## Catatan pemulihan

- PROGRESS.md (folder workspace liga) = log koordinator; board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025) dibaca tepat SEKALI bila ada kandidat lolos dev; 2026 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan sentuh workspace FI-Ykkonen (agen lain bekerja paralel).
