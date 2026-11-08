# MD-NationalDivision — STATUS

- Status: SELESAI — G FAIL (virgin legs i+ii), S/C/K/T not-buildable, virgin dibaca SEKALI, tidak ada yang ship (menunggu verifikasi Jarvis)
- Liga: MD-NationalDivision (Moldova National Division / Super Liga, tier 1, FotMob 231)
- Fase saat ini: SELESAI (Fase 7 deliver) — deliverable di outbox-muse2/MD-NationalDivision/ (main), RESULT.md ditulis; MENUNGGU verifikasi [Jarvis]
- Terakhir diperbarui: 2026-11-10 19:40 WIB oleh sub-agen Muse-2 (builder MD)
- Referensi commit pra-registrasi: 72b4199a9c0c104b96f1ea52214166c73b28cb10 (branch wip-md-nationaldivision, ter-push SEBELUM fitting apa pun)
- Hasil dev: results_dev.json md5 24702632b8419d0596f42d978e0be1a4 (re-run identik sebelum & sesudah virgin)
- Hasil virgin (2025/2026, n=114, dibaca SEKALI): Gate Zero 1X2 LL 0,840000 / OU 0,704782, kalibrasi HW −2,26pp (SE 3,96) / OU −11,69pp (SE 4,62); X2 0,809742 / 0,694756, OU kalibrasi −11,30pp; klimatologi OU 0,687981 → semua arm GAGAL leg (i) kaki OU + leg (ii) kalibrasi OU. Vonis G-MD FAIL; tidak ada yang ship; predictions/ tidak dibuat; 2026/2027 tidak pernah dibaca harness mana pun
- Pos jatah di papan: issue #1 komentar 6763121416 (Assignment 17; diproses setelah persetujuan user 2026-11-10 19:25 WIB); ACK MD 6767294131 oleh koordinator
- Data: release bundle-md-national; 556 JSON = index_231.csv (556 baris); musim 2021/2022–2026/2027 (112/86/86/86/114/72)

## Temuan kunci Fase 1–2

- Scores-only TERKONFIRMASI dari data: stats feed 0/556 semua musim, shotmap 0/556, splits 0/556, referee 0/556 → hanya G buildable; S/C/K/T not-buildable.
- Kartu: plain Yellow events = 0 di SEMUA musim (hanya YellowRed 25 + Red) → tidak ada target yellows sama sekali; K not-buildable bentuk terkuat.
- Format: 8 tim semua musim; 2021/2022 fase tunggal (112, nama "National Division"), 2022/2023+ dua fase (56 main + 30 championship, nama "Super Liga"); 2025/2026 main membesar (84+30=114). Fase = flag, tidak pernah difilter.
- Split beku (BRIEF): warm-up 2021/2022; dev scored 2022/2023–2024/2025 (n=258); virgin 2025/2026 (n=114); cadangan 2026/2027 tak disentuh.
- Reliability trait dev kuat: GF r 0,885 / GA r 0,877. Halves goals 1H share dev = 0,4388 (1.005 gol, 336 match berevents, awarded dikeluarkan).
- Level gol dev volatil: 3,063 / 2,128 / 2,953 / 2,965 — musim 2022/2023 anjlok dalam.
- Entrant: hanya 3 transisi dev (GF −0,363 tanda 3/3; GA +0,780 tanda 2/3) → X2 DIPERTAHANKAN sebagai arm berbasis aturan (offset clamp −0,223/+0,223), tapi secara numerik inert di jendela dev scored (aturan <3 transisi → offset 0; 2024/2025 tanpa entrant).
- Line beku: OU 2.5 (over-rate dev scored 0,4884; 1.5: 0,7481; 3.5: 0,2829). Home win dev scored 0,4574; draw 0,2403.
- Awarded 10 match (9 di 2021/2022, 1 di 2024/2025) — baris biasa berflag; skor header otoritatif; 0 mismatch skor-vs-events di seluruh korpus. Spot-check 3 JSON mentah lulus.

## Langkah berikutnya persis

1. SELESAI — tidak ada langkah berikutnya; menunggu verifikasi Jarvis di papan (pos done oleh koordinator). Bila Jarvis meminta perbaikan, kerjakan dari STATUS ini.

## Catatan pemulihan

- STATUS.md ini di folder workspace liga; salinan ikut di snapshot wip + deliverable outbox.
- Virgin (2025/2026) dibaca tepat SEKALI bila ada kandidat lolos dev; 2026/2027 tidak disentuh.
- Jangan pakai Codex. Jangan posting apa pun di papan GitHub sendiri; koordinator yang memposting.
- Snapshot WIP memakai clone ~/workspace/league-work/.snapshot-repo (dipakai paralel dengan builder liga lain — retry bila berbenturan, jangan force-push).
