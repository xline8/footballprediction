# RS-SuperLiga — STATUS

- Status: SELESAI — G-RS FAIL (dev gate, OU leg); S/C/K/T NOT BUILT (feasibility); virgin TIDAK dibaca; deliverable di outbox
- Liga: RS-SuperLiga (Serbia Super Liga, FotMob 182)
- Fase saat ini: Fase 7 — SELESAI (deliver ke outbox + RESULT.md + pos done di papan)
- Terakhir diperbarui: 2026-11-10 ~12:20 WIB oleh koordinator Muse-2
- Referensi commit pra-registrasi: branch wip-rs-superliga commit a0b379d "[Muse-2] WIP snapshot RS-SuperLiga fase 2-3 (EDA + prereg)" (2026-11-10, SEBELUM fitting apa pun)
- Pos jatah di papan: issue #1 komentar 6758056896
- Data: release bundle-rs-superliga, `serbia_slice.tar.gz` (1.592 match JSON, musim 2021/2022–2026/2027), terunduh ke `raw/`
- Split yang disarankan BRIEF: dev ≤ 2024/2025, virgin = 2025/2026 (n=296), 2026/2027 cadangan konfirmasi (belum disentuh)

## Sudah selesai

- Jatah diterima; bundle data terunduh; folder workspace dibuat.
- Fase 0 — workspace: mirror `work/Serbia/Super Liga/` (tar diekstrak, 1.592 JSON), `league/RS-SuperLiga/` dibuat, tools `build_league_data.py` + `jleague_lib.py` disalin ke `league/`.
- Fase 1 — data build SELESAI: `league/RS-SuperLiga/data/build_data.py` (adaptasi FI), output `rs_matches.csv` 1592/1592 baris (= index), `rs_team_matches.csv` 3184 baris. Aturan fase dari leagueName + matchRound. 3 spot-check JSON mentah lolos (3621229, 3861008, 4810626).

## Temuan awal penting (diukur, dikonfirmasi di EDA)

- Stats feed TIDAK ADA di 2021/2022–2024/2025; kaya hanya di 2025/2026 (virgin!) + 2026/2027 (cadangan). Tidak ada kunci expected_goals di musim apa pun; shotmap 0% di semua musim.
- Event Card di era dev nyaris tidak ada (0,04–0,12 kartu kuning/pertandingan vs 4,66 di virgin). Lineup ~tidak ada sebelum 2025/2026.
- Perkiraan: hanya G yang buildable; S/C/K/T kemungkinan not-buildable. 7 id tim membawa 2 ejaan nama (diakritik) — kunci memakai id tim.

## Langkah berikutnya persis

1. Fase 2 — dokumen langkah 1–6 SELESAI (analysis/: 5 dokumen + eda.py + make_charts.py + eda_summary.json + inventory_summary.json + 3 charts). G buildable; S/C/K/T not-buildable.
2. Fase 3 — pra-registrasi SELESAI (PREREG_G_RS.md + PREREG_S/C/K/T_RS.md not-built), ter-push ke branch `wip-rs-superliga` commit a0b379d SEBELUM fitting apa pun.
3. Fase 4 — engine G-RS SELESAI: Gate Zero pooled 1X2 LL 0.992930 / RPS 0.207218 / OU2.5 LL 0.698890 vs climatology 1.064029 / 0.233579 / 0.695516 — GAGAL dev gate (OU leg). SHRINK identik; X2 pooled OU 0.696747 juga gagal. Climatology diverifikasi independen (cocok 6 digit).
4. Fase 5 — virgin TIDAK dibaca (tidak ada kandidat lolos dev); cadangan 2026/2027 tidak disentuh.
5. Fase 6 — verdicts (G FAIL; S/C/K/T NOT BUILT) + config.yaml SELESAI. Fase 7 — deliver ke outbox + RESULT.md + pos done di papan.
3. Fase 4 — engine, evaluasi dev saja. Fase 5 — virgin SEKALI untuk yang lolos dev. Fase 6 — verdicts + config. Fase 7 — deliver ke outbox + RESULT.md + pos done di papan.
4. Di SETIAP perpindahan fase perbarui STATUS.md ini (kedua salinan: workspace + outbox), segarkan WORKER.lock, push snapshot WIP ke branch `wip-rs-superliga` via clone ~/workspace/league-work/.snapshot-repo.

## Catatan pemulihan

- PROGRESS.md (folder workspace liga) = log koordinator; board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025/2026) dibaca tepat SEKALI per kandidat lolos dev; 2026/2027 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
