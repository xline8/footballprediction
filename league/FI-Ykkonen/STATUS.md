# FI-Ykkonen — STATUS

- Status: SELESAI — G FAIL (gerbang dev), S/C/K/T not-buildable; virgin TIDAK dibaca; deliverable siap di outbox, menunggu verifikasi Jarvis
- Liga: FI-Ykkonen (Finland Ykkönen, tier 2 per BRIEF — LIHAT TEMUAN STRUKTUR di bawah, tier 3 faktual)
- Fase saat ini: Fase 7 SELESAI — deliverable di outbox-muse2/FI-Ykkonen/ (repo papan, branch main), menunggu verifikasi Jarvis
- Terakhir diperbarui: 2026-11-10 14:30 WIB oleh sub-agen Muse-2 (Fase 7)
- Referensi commit pra-registrasi: `e5874b8d62f005abf9a79e8ee2b5641069cf1f2a` (branch wip-fi-ykkonen, "[Muse-2] WIP snapshot FI-Ykkonen fase 3", 2026-11-10 — SEBELUM fitting apa pun)
- Referensi commit deliverable: (dicatat di bawah setelah push ke main)
- Pos jatah di papan: issue #1 komentar 6761046100
- Keputusan split Jarvis: OPSI A, komentar papan 6761468990 (2026-11-10 07:17:39Z) — dev ≤ 2024 apa adanya, lanjut pra-registrasi pada split BRIEF; struktur Kakkonen/Ykkönen + efek komposisi dicatat di PREREG_G_FI.md; dev ≤ 2024 / virgin 2025 / 2026 cadangan dibekukan.
- Data: release bundle-fi-ykkonen, 1.730 JSON terverifikasi = index_8969.csv (396/438/410/162/162/162 per musim 2021–2026); stats 0%, shotmap 0%, lineup 0%, splits 0% di semua musim
- Split yang disarankan BRIEF: dev ≤ 2024, virgin = 2025 (n=162), 2026 cadangan konfirmasi (belum disentuh)
- Scores-only: stats feed 0% semua musim, shotmap 0%; hanya G buildable; S/C/K/T not-buildable (konfirmasi absen di EDA, jangan berburu stats feed yang tidak ada)

## TEMUAN STRUKTUR KRITIS (Fase 0, perlu keputusan Jarvis sebelum pra-registrasi)

FotMob league_id 8969 BERGANTI IDENTITAS di tengah korpus (dari `general.leagueName` di JSON mentah):
- 2021–2023 = **Kakkonen** (tier 3 lama, TIGA grup paralel Lohko A/B/C, 36–37 tim/musim; 396/438/410 match incl. promotion groups + playoff 2022–2023) — BUKAN Ykkönen.
- 2024–2026 = **Ykkönen** (tier 3 pasca-restrukturisasi, 12 tim, 132 reguler + 15 championship + 15 relegation = 162/musim).
- Kontinuitas tim TINGGI: 11/12 tim Ykkönen 2024 pernah main Kakkonen 2021–2023 (10/12 di Kakkonen 2023); 9/12 tim Ykkönen 2025 ada di 2024. Tier faktual sama (tier 3) di kedua era.
- Dampak: split BRIEF (dev ≤ 2024) berarti 3 dari 4 musim dev adalah kompetisi bernama lain; alternatif dev = 2024 saja (n=162, satu musim — gerbang dev multi-musim tidak jalan). Opsi split + bukti kuantitatif lengkap akan disajikan di akhir Fase 2; pra-registrasi (Fase 3) DITAHAN sampai Jarvis memutuskan. Jangan menebak melewati gerbang.

## Langkah berikutnya persis

1. Fase 1 — build data: SELESAI (lihat bawah).
2. Fase 2 — dokumen langkah 1–6 + EDA + charts: SELESAI 2026-11-10. Ringkasan hasil EDA kunci:
   - Halves constant goals dev **0,4463** (4.730 gol, 1.353 match ber-event, awarded excluded); stabil lintas era (Kakkonen 0,4445 vs Ykkönen 2024 0,4594).
   - Level gol dev scored 2022–2024: **3,401 gol/match**, OU2.5 0,650, home-win 0,471, draw 0,198 (n=1.010).
   - Reliabilitas GF/GA split-half dev: **0,612 / 0,632** (n=55 tim); antar-musim GF lemah (0,08–0,35), GA 0,18–0,43.
   - Break Kakkonen/Ykkönen: grup C ~0,35–0,60 gol/match di bawah grup B; hanya **22 match lintas grup** di seluruh dev era (semua 2023); level fase reguler identik 2023 vs 2024 (3,329 vs 3,326) — shift headline 2024 adalah efek komposisi fase split (championship/relegation 4,333, n=30); kontinuitas 11/12 tim.
   - X2: **22 transisi**, gf_diff −0,182 / ga_diff +0,235 → g_log −0,182, c_log +0,223 (ter-clamp); terukur dan konsisten tanda, didorong era Kakkonen (20/22).
   - Event-Yellow: **0 plain Yellow di seluruh korpus** (hanya YellowRed + Red); stats 0%, referee 0% — K not-buildable. S/C/K/T not-buildable; hanya G.
   - Rekomendasi Muse-2 (bukan keputusan): **Opsi A, dev ≤ 2024 apa adanya** — break adalah masalah format/identifikasi, bukan level; Opsi B (dev = 2024 saja) menghancurkan protokol gerbang. Keputusan tetap Jarvis. Detail di analysis/MODEL_DESIGN.md.
3. STOP sebelum Fase 3 — laporkan bloker split ke koordinator untuk keputusan Jarvis (opsi: dev ≤ 2024 apa adanya / dev = 2024 saja / re-scope / batal).
   → TERJAWAB 2026-11-10: Jarvis memilih OPSI A (komentar papan 6761468990, 07:17:39Z) — dev ≤ 2024 apa adanya, pra-registrasi pada split BRIEF; struktur + efek komposisi dicatat di prereg; dev ≤ 2024 / virgin 2025 / 2026 cadangan dibekukan.
4. Fase 3 — pra-registrasi SEBELUM fitting apa pun; push ke branch wip-fi-ykkonen. SELESAI 2026-11-10: `league/FI-Ykkonen/prereg/PREREG_G_FI.md` (Gate Zero + SHRINK + X2; g_log −0,182, c_log +0,223 ter-clamp; gerbang verbatim; struktur Kakkonen/Ykkönen + efek komposisi fase split dicatat) dan `prereg/PREREG_S_C_K_T_FI.md` (semua not-buildable; stats 0%, shotmap 0%, K: 0 plain Yellow di seluruh korpus + referee 0%). Commit pra-registrasi ke wip-fi-ykkonen SEBELUM fitting apa pun — hash dicatat di baris "Referensi commit pra-registrasi" di atas.
5. Fase 4 — engine G (Dixon-Coles Gate Zero + SHRINK; X1 blend goals-only, tanpa xG), evaluasi dev saja. SELESAI 2026-11-10: engine port template NO (dc.py/arms.py referensi FI verbatim; harness + run_g_fi.py; FI_DEV_ONLY=1). Dev pooled (n=1.010): Gate Zero 1X2 LL 1,0747 / RPS 0,2437 / OU2.5 LL 0,7026 vs klimatologi 1,0420 / 0,2355 / 0,6485 — KALAH di ketiganya vs klimatologi; vs naive menang 1X2 + OU tapi kalah RPS. SHRINK identik dengan Gate Zero. X2 membaik di ketiganya (1,0660 / 0,2404 / 0,6940) tapi tetap gagal gerbang dev. **GATE ZERO GAGAL GERBANG DEV → varian moot, vonis FAIL.**
   Fase 5 — virgin SEKALI bila lolos dev. TIDAK DILAKUKAN: virgin 2025 TIDAK dibaca (Gate Zero gagal dev); tidak ada results_virgin.json / fitted_params_virgin.json / virgin_rows_*.csv. 2026 tidak disentuh.
   Fase 6 — verdicts + config. SELESAI 2026-11-10: reports/G_FI_VERDICT.md (FAIL gerbang dev), S/C/K/T_FI_VERDICT.md (not-buildable), config.yaml.
   Fase 7 — deliver ke outbox + RESULT.md. SELESAI 2026-11-10: outbox-muse2/FI-Ykkonen/ di repo papan (branch main) + RESULT.md; STATUS.md kedua salinan diperbarui; snapshot akhir ke wip-fi-ykkonen. TIDAK posting di papan — koordinator yang memposting done.
6. Di SETIAP perpindahan fase perbarui STATUS.md ini (kedua salinan: workspace + outbox), segarkan WORKER.lock, push snapshot WIP ke branch wip-fi-ykkonen via clone ~/workspace/league-work/.snapshot-repo.

## Yang sudah selesai

- Fase 0 — workspace + unduh data: SELESAI. Tar diekstrak ke data_enrichment/fotmob_world/Finland/Ykkonen/ (1.730 JSON = index), index disalin ke data_enrichment/fotmob_world_index.csv, tools build_league_data.py + jleague_lib.py disalin ke league/. Temuan struktur Kakkonen/Ykkönen di atas.
- Fase 1 — build data: SELESAI. league/FI-Ykkonen/data/build_data.py → fi_matches.csv (1.730 baris = index, 0 fase unknown, 0 duplikat) + fi_team_matches.csv (3.460 baris). Stats 0/1730, shotmap 0/1730, referee 0/1730, events 1675/1730. 7 match awarded (skor awarded 0-3/3-0 ≠ gol event) — dipertahankan sebagai baris biasa berflag, preseden NO. Team id 112425 dua ejaan (GrIFK Grankulla / GrIFK); semua logika key by team id. Spot-check 3 JSON mentah LULUS: 4422555 (2-0, HT 1-0, 0 kartu), 4422585 awarded (0-3), 3537968 tanpa event (0-0, ht_source none).

## Catatan pemulihan

- PROGRESS.md (folder workspace liga) = log koordinator; board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025) dibaca tepat SEKALI bila ada kandidat lolos dev; 2026 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan sentuh workspace UY-LigaAUF (agen lain bekerja paralel).
