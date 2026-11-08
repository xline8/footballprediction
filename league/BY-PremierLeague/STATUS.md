# BY-PremierLeague — STATUS

- Status: SELESAI — Fase 7 deliver selesai, menunggu verifikasi [Jarvis] (Assignment 15, komentar papan 6761972198)
- Liga: BY-PremierLeague (Belarus Premier League, tier 1, FotMob 263)
- Fase saat ini: SELESAI — deliverable di outbox-muse2/BY-PremierLeague/ (main, commit 847aba9); pos done oleh koordinator
- Terakhir diperbarui: 2026-11-10 15:45 WIB oleh Muse-2
- Referensi commit pra-registrasi: 66cbfe459665943b113dd32946355410ddb7dada (branch wip-by-premierleague, SEBELUM fitting apa pun)
- Pos jatah di papan: issue #1 komentar 6761972198 (Assignment 15)
- Data: release bundle-by-premier (1.394 match, musim kalender 2021–2026; 240/musim 2021–2022, 210 di 2023, 240 di 2024–2025, 224 di 2026 masih berjalan), index_263.csv di bundle
- Split yang disarankan BRIEF: dev ≤ 2024, virgin = 2025 (n=240), 2026 cadangan konfirmasi (belum disentuh)
- Scores-only: stats feed 0% semua musim, shotmap 0%; hanya G buildable; S/C/K/T not-buildable (konfirmasi absen di EDA, jangan berburu stats feed yang tidak ada)

## Yang sudah selesai

- Fase 1 — SELESAI: league/BY-PremierLeague/data/build_data.py (adaptasi FR-Ligue3); by_matches.csv 1.394 baris + by_team_matches.csv 2.788 baris. Spot-check 3 JSON mentah lulus (3540809 1-0; 3540973 awarded 3-0 tanpa event; 4127429 awarded 3-0, event 2-2 dimainkan; 4432693 1-1). Temuan: 17 match awarded (15 di 2021 semua melibatkan Sputnik Rechitsa yang mundur tengah musim — sisa laga di-award 3-0/0-3 tanpa event; 3832254 Gomel 3-0 Neman 2022 tanpa event; 4127429 Naftan 3-0 Smorgon 2023, event 2-2); 1 mismatch non-awarded 3832371 (2022, Shakhtyor–Belshina: header 0-0, event 4-1 — hasil resmi 0-0, event mencerminkan skor lapangan; skor header yang dipakai); 23 team id, 0 varian ejaan nama; 16 tim/musim (15 di 2023); stats Periods kosong 1.394/1.394; shotmap 0; referee 0%; plain Yellow event 0 di semua musim.
- Fase 2 — SELESAI: dokumen langkah 1–6 (DATA_UNDERSTANDING.md, PREPROCESSING.md, EDA.md, FEATURES.md, MODEL_DESIGN.md) + eda.py + eda_summary.json + inventory_summary.json + 4 charts. Temuan kunci: goals/match 2,713/2,542/2,738/2,346 dev, 2,546 virgin (inventaris saja), 2,603 reserve; halves goals 1H share dev 0,4314 (2.348 gol, 845 match); reliabilitas trait GF r=0,855 / GA r=0,947 (n=20 tim) — SANGAT kuat, jauh di atas FR; entrant 8 transisi dev, mean GF −0,325 / GA +0,426, tanda konsisten (GF negatif 8/8, GA positif 7/8) → X2 KEEP, offset clamp g_log −0,223 / c_log +0,223 (keputusan sama seperti FI, berlawanan dengan CH/NO/FR); OU2.5 over-rate dev scored 0,4551 (n=690), garis beku OU2.5; S/C/K/T not-buildable (stats 0% semua musim, shotmap 0%, referee 0%, plain Yellow event 0 di SEMUA musim — K tanpa target sama sekali).

## Yang sudah selesai (lanjutan)

- Fase 3 — pra-registrasi SEBELUM fitting apa pun: PREREG_G_BY.md (Gate Zero + SHRINK + X2; X2 KEPT — EDA F4 8 transisi, mean GF −0,325 / GA +0,426, tanda konsisten; offset dihitung dari transisi selesai SEBELUM musim prediksi, clamp [0.8, 1.25], <3 transisi → 0; realisasi dev penuh g_log −0,223 / c_log +0,223) + PREREG_S/C/K/T_BY.md (not-buildable; K: plain Yellow 0 di SEMUA musim + referee 0%). Gate legs beku verbatim (dev: pooled 1X2 LL/RPS/OU2.5 LL kalahkan KEDUA baseline; virgin legs i–iii). Dev ≤ 2024 (warm-up 2021, scored 2022–2024 n=690), virgin 2025 n=240, 2026 cadangan. Virgin 2025 BELUM dibaca.

- Fase 4 — SELESAI: engine G dev-only (BY_DEV_ONLY=1). Gate Zero pooled dev (n=690): 1X2 LL 1,0679 / RPS 0,2223 / OU2.5 LL 0,7143 vs klimatologi 1,0886 / 0,2327 / 0,6934 dan vs naive trailing-10 1,0534 / 0,2181 / 0,7455 — GAGAL gerbang dev (kaki OU vs klimatologi di semua musim dev; kaki 1X2 + RPS vs naive pooled). SHRINK identik dengan Gate Zero. X2 lebih buruk pooled (1,0867 / 0,2257 / 0,7200): identik 2022 (offset 0, <3 transisi), lebih buruk 2023, jauh lebih buruk 2024 (1,1319 vs 1,0789). Fase 5 — DILEWATI: virgin 2025 TIDAK dibaca (Gate Zero gagal dev). Fase 6 — SELESAI: verdicts + config.yaml.
- Fase 7 — SELESAI: deliverable di outbox-muse2/BY-PremierLeague/ (main) + RESULT.md. Pos done di papan oleh KOORDINATOR (agen ini JANGAN posting).

## Hasil akhir

- G-BY: FAIL (gerbang dev, kaki OU2.5 vs klimatologi + kaki 1X2/RPS vs naive) — Gate Zero pooled dev (n=690) 1X2 LL 1,0679 / RPS 0,2223 / OU2.5 LL 0,7143 vs klimatologi 1,0886 / 0,2327 / 0,6934 dan naive 1,0534 / 0,2181 / 0,7455. SHRINK identik. X2 lebih buruk. Virgin 2025 TIDAK dibaca; 2026 tidak disentuh.
- S/C/K/T: NOT-BUILDABLE (stats feed 0% semua musim; shotmap 0%; K tambahan: plain Yellow event 0 di SEMUA musim + referee 0%).
- Tidak ada yang ship dari BY-PremierLeague.

## Langkah berikutnya persis

1. (tidak ada langkah berikutnya — liga selesai; menunggu verifikasi Jarvis)

1. Fase 0 — SELESAI: tarball diekstrak ke data_enrichment/fotmob_world/Belarus/Premier League/; 1.394 JSON cocok dengan index (0 hilang, 0 selisih skor vs index, 0 belum selesai).
2. Fase 1 — SELESAI (lihat di atas).
3. Fase 2 — SELESAI (lihat di atas).
4. Fase 3 — pra-registrasi SEBELUM fitting apa pun: PREREG_G_BY.md (Gate Zero + SHRINK; X1 goals-only; X2 hanya bila EDA mendukung; baselines klimatologi + naive trailing-10; gate legs beku verbatim; dev ≤ 2024 / virgin 2025 n=240 / 2026 cadangan) + PREREG_S/C/K/T_BY.md (not-buildable). Push ke branch wip-by-premierleague SEBELUM fitting; catat hash commit pra-registrasi di STATUS.md. Virgin 2025 TIDAK dibaca sebelum Fase 5.
5. Fase 4 — engine G dev-only (BY_DEV_ONLY=1), evaluasi dev saja. Fase 5 — virgin SEKALI (2025) hanya bila ada kandidat lolos gerbang dev; bila gagal dev, virgin TIDAK dibaca. Fase 6 — verdicts + config.yaml. Fase 7 — deliverable di outbox-muse2/BY-PremierLeague/ (main) + RESULT.md. Pos done di papan oleh KOORDINATOR (agen ini JANGAN posting).

## Catatan pemulihan

- PROGRESS.md (folder workspace liga) = log koordinator; board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025) dibaca tepat SEKALI bila ada kandidat lolos dev; 2026 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan sentuh workspace liga lain (FR-Ligue3, CN-LeagueOne, FI-Ykkonen — agen lain bekerja paralel).
- Di SETIAP perpindahan fase perbarui STATUS.md ini (kedua salinan: workspace + outbox), segarkan WORKER.lock, push snapshot WIP ke branch wip-by-premierleague via clone ~/workspace/league-work/.snapshot-repo.
