# CN-LeagueOne — STATUS

- Status: SELESAI — Fase 7 deliver selesai, menunggu verifikasi [Jarvis] (Assignment 13, komentar papan 6761518131)
- Liga: CN-LeagueOne (China League One, tier 2, FotMob 9137)
- Fase saat ini: SELESAI — deliverable di outbox-muse2/CN-LeagueOne/ (main, commit c59aacf); pos done oleh koordinator
- Terakhir diperbarui: 2026-11-10 15:05 WIB oleh Muse-2
- Referensi commit pra-registrasi: 05c5870af4427871786759f7d1e6de31b548ae83 (branch wip-cn-leagueone, SEBELUM fitting apa pun)
- Pos jatah di papan: issue #1 komentar 6761518131 (Assignment 13)
- Data: release bundle-cn-league1 (1.572 match, musim kalender 2021–2026; 306/musim 2021–2022, 240/musim 2023–2026), index_9137.csv di bundle
- Split yang disarankan BRIEF: dev ≤ 2024, virgin = 2025 (n=240), 2026 cadangan konfirmasi (belum disentuh)
- Scores-only: stats feed 0% semua musim, shotmap 0%; hanya G buildable; S/C/K/T not-buildable (konfirmasi absen di EDA, jangan berburu stats feed yang tidak ada)

## Yang sudah selesai

- Fase 0 — release bundle-cn-league1 diekstrak ke data_enrichment/fotmob_world/China/China League One/ (tarball bertingkat `China/...`, dipindah ke layout warehouse); 1.572 JSON cocok dengan index (0 hilang, 0 selisih skor vs index, 0 belum selesai). Temuan awal: 3 match awarded (semua 2022: 3892074 Kunshan–Beijing Tech 3-0; 3892065 Beijing Tech–Jiangxi 0-3; 3946586 Heilongjiang–Zibo 3-0); leagueName FotMob "China League" semua musim (satu grup, tanpa fase paralel); 2021–2022: 18 tim, 34 ronde; 2023+: 16 tim, 30 ronde; coverageLevel "lower" semua match; index has_stats/has_shotmap/has_period_splits False 1.572/1.572, has_lineup True hanya 3 match.
 - Fase 1 — league/CN-LeagueOne/data/build_data.py (adaptasi NO-2Divisjon + preseden IL); cn_matches.csv 1.572 baris + cn_team_matches.csv 3.144 baris. Spot-check 3 JSON mentah lulus (3574318 3-1; 3574267 0-4; 3892074 awarded 3-0, 0 events). Temuan: stats Periods kosong di 1.572/1.572; shotmap 0; event ada di 1.447/1.572 (125 tanpa event, 3 di antaranya bergol — 9 gol); referee 0% semua musim; plain Yellow event TIDAK PERNAH ada di musim mana pun (0 di 1.572 match; hanya YellowRed + Red) — K not-buildable paling kuat sejauh ini; 3 match awarded (semua 2022) — baris biasa dengan flag awarded.
- Fase 2 — dokumen langkah 1–6 + eda.py + eda_summary.json + inventory_summary.json + 4 charts. Temuan kunci: goals/match 2,71/2,61/2,26/2,48 dev, 2,61 virgin (inventaris saja), 2,69 cadangan; halves goals 1H share dev 0,4493 (2.760 gol, 1.000 match); reliabilitas trait GF r=0,730 / GA r=0,811 (n=33 tim) — terkuat di preseden scores-only; korelasi antar-musim GF meluruh cepat (0,82 → 0,40 → 0,13), GA lebih awet (0,89 → 0,59 → 0,34); entrant 15 transisi dev, mean GF +0,095 / GA −0,034, median −0,042/−0,065, tanda campur → X2 DROPPED (seperti NO/CH); OU2.5 over-rate dev scored 0,445 (n=786), garis beku OU2.5 per standar program; S/C/K/T not-buildable (stats 0% semua musim, shotmap 0%, referee 0%, plain Yellow 0 di semua musim).

## Langkah berikutnya persis

 - Fase 3 — pra-registrasi SEBELUM fitting apa pun: PREREG_G_CN.md (Gate Zero + SHRINK; X1 goals-only; X2 dropped; baselines klimatologi + naive trailing-10; gate legs beku verbatim; dev ≤ 2024 / virgin 2025 n=240 / 2026 cadangan) + PREREG_S_C_K_T_CN.md (not-buildable). Push ke branch wip-cn-leagueone, commit 05c5870. Virgin 2025 BELUM dibaca.
 - Fase 4 — SELESAI: engine G dev-only (CN_DEV_ONLY=1). Gate Zero pooled dev (n=786): 1X2 LL 1,0286 / RPS 0,2096 / OU2.5 LL 0,6927 vs klimatologi 1,0886 / 0,2293 / 0,6919 — GAGAL gerbang dev (kaki OU, selisih 0,0007, dibawa musim 2024 saja; model menang kaki OU di 2022 dan 2023). SHRINK identik dengan Gate Zero. Fase 5 — DILEWATI: virgin 2025 TIDAK dibaca (Gate Zero gagal dev). Fase 6 — SELESAI: verdicts + config.yaml.
- Fase 7 — SELESAI: deliverable di outbox-muse2/CN-LeagueOne/ (main) + RESULT.md. Pos done di papan oleh KOORDINATOR (agen ini JANGAN posting).
1. (tidak ada langkah berikutnya — liga selesai; menunggu verifikasi Jarvis)
4. Fase 4 — engine G dev-only (CN_DEV_ONLY=1), evaluasi dev saja.
5. Fase 5 — virgin 2025 SEKALI hanya bila ada kandidat lolos gerbang dev; bila gagal dev, virgin TIDAK dibaca.
6. Fase 6 — verdicts + config.yaml.
7. Fase 7 — deliverable di outbox-muse2/CN-LeagueOne/ (main) + RESULT.md. Pos done di papan oleh KOORDINATOR (agen ini JANGAN posting).

## Hasil akhir

- G-CN: FAIL (gerbang dev, kaki OU2.5) — Gate Zero pooled dev (n=786) 1X2 LL 1,0286 / RPS 0,2096 / OU2.5 LL 0,6927 vs klimatologi 1,0886 / 0,2293 / 0,6919. SHRINK identik. Virgin 2025 TIDAK dibaca; 2026 tidak disentuh.
- S/C/K/T: NOT-BUILDABLE (stats feed 0% semua musim; K tambahan: plain Yellow event 0 di 1.572 match + referee 0%).
- Tidak ada yang ship dari CN-LeagueOne.

## Catatan pemulihan

- PROGRESS.md (folder workspace liga) = log koordinator; board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025) dibaca tepat SEKALI bila ada kandidat lolos dev; 2026 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan sentuh workspace liga lain (FI-Ykkonen, UY-LigaAUF, SE-Ettan, NO-2Divisjon — agen lain bekerja paralel).
- Di SETIAP perpindahan fase perbarui STATUS.md ini (kedua salinan: workspace + outbox), segarkan WORKER.lock, push snapshot WIP ke branch wip-cn-leagueone via clone ~/workspace/league-work/.snapshot-repo.
