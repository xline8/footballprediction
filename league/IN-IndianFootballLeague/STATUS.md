# IN-IndianFootballLeague — STATUS

- Status: SELESAI — G FAIL (gerbang dev), S/C/K/T not-buildable; virgin TIDAK dibaca; deliverable siap di outbox, menunggu verifikasi Jarvis
- Liga: IN-IndianFootballLeague (India Indian Football League — I-League, tier 2, FotMob 8982; rebrand nama dari 2025/2026)
- Fase saat ini: Fase 7 SELESAI — deliverable di outbox-muse2/IN-IndianFootballLeague/ (repo papan, branch main), menunggu verifikasi Jarvis
- Terakhir diperbarui: 2026-11-10 19:52 WIB oleh Muse-2 (sub-agen builder IN)
- Referensi commit pra-registrasi: `83d1b1f590f459abc0417c895c55a3793068bec2` (branch wip-in-indianfootballleague, ter-push SEBELUM fitting apa pun)
- Pos jatah di papan: issue #1 komentar 6763121416 (Assignments 16–19; diproses setelah persetujuan user 2026-11-10 19:25 WIB)
- Data: release bundle-in-ifl; 608 JSON terverifikasi = index_8982.csv (114/132/154/132/66/10 per musim 2021/2022–2026/2027)
- Split yang disarankan BRIEF: dev ≤ 2024/2025, virgin = 2025/2026 (n=66, kecil — gerbang diterapkan apa adanya), 2026/2027 cadangan konfirmasi (belum disentuh)
- Scores-only: stats feed 0% semua musim, shotmap 0%; hanya G buildable; S/C/K/T not-buildable (K: plain Yellow event = 0 di semua musim dev DAN virgin; hanya YellowRed+Red)

## Yang sudah selesai

- Fase 0 — workspace + unduh data: SELESAI. Tar diekstrak ke data_enrichment/fotmob_world/India/Indian Football League/ (608 JSON = index), index disalin ke data_enrichment/fotmob_world_index.csv, tools build_league_data.py + jleague_lib.py disalin ke league/. Temuan struktur: leagueName 'I-League' 2021/2022–2024/2025 dengan grup Championship (21) / Relegation (15) di 2021/2022; 2025/2026 bernama 'Indian Football League' dengan grup Promotion (15) / Relegation (6); 2026/2027 campuran 'I League'/'Indian Football League'. Coverage 'lower' 608/608.
- Fase 1 — build data: SELESAI. league/IN-IndianFootballLeague/data/build_data.py → in_matches.csv (608 baris = index) + in_team_matches.csv (1.216 baris). Fase: main 551, championship 36, relegation 21, unknown 0. Stats 0/608, shotmap 0/608, events 574/608 (34 tanpa events), 4 awarded, 4 mismatch skor-vs-events. Wasit bernama 467/608 (dev 453/496; virgin hanya 4/66) — tapi K tetap not-buildable (tidak ada target yellows). 24 team id; 4 id dengan 2 ejaan nama (semua logika key by team id). Spot-check 3 JSON mentah LULUS: 3778932 (1-0), 5187191 (1-1), 1000022426 (3-2).

- Fase 2 — SELESAI: dokumen langkah 1–6 + eda.py + eda_summary.json + inventory_summary.json + 4 charts. Temuan kunci: stats 0%/shotmap 0%/splits 0% semua musim; level gol dev NAIK (2,579/2,727/3,331/3,182); halves goals 1H share dev 0,4387 (1.575 gol, 497 match); reliabilitas trait GF r=0,608 / GA r=0,462 (n=19, moderat); X2 DITOLAK (6 transisi entrant, GF −0,110 / GA +0,025, tanda campur — pola CH/NO/FR/SE); over-rate dev scored OU2.5 0,5718 (n=418), home win 0,4450, draw 0,2392; K not-buildable (plain Yellow 0 di dev DAN virgin; wasit dev 91,3% tapi virgin 4/66); virgin 2025/2026 LENGKAP (45 reguler + 15 promotion + 6 relegation; musim berikutnya sudah mulai).

## Langkah berikutnya persis

1. Fase 3 — SELESAI: prereg/ ditulis 2026-11-10 SEBELUM fitting apa pun (virgin 2025/2026 TIDAK dibaca — hanya n=66 yang sudah beku yang dituliskan): PREREG_G_IN.md (Gate Zero + SHRINK; X2 DITOLAK per EDA F4; baselines klimatologi + naive trailing-10; gate legs program beku verbatim) dan PREREG_S/C/K/T_IN.md (semua not-buildable). Angka beku: warm-up 2021/2022, dev scored 2022/2023–2024/2025 n=418, virgin 2025/2026 n=66 LENGKAP, 2026/2027 cadangan tak disentuh; OU2.5 over-rate dev scored 0,5718; home win 0,4450, draw 0,2392; goals_1h_share 0,4387.
3. Fase 4 — engine G (Dixon-Coles Gate Zero + SHRINK [+ X2 bila EDA mendukung]), evaluasi dev saja. Fase 5 — virgin SEKALI bila lolos dev. Fase 6 — verdicts + config. Fase 7 — deliver ke outbox + RESULT.md (pos done oleh KOORDINATOR, agen ini JANGAN posting).
4. Di SETIAP perpindahan fase perbarui STATUS.md ini, segarkan WORKER.lock, push snapshot WIP ke branch wip-in-indianfootballleague via clone ~/workspace/league-work/.snapshot-repo.

## Catatan pemulihan

- board-state.json di ~/league-remote/ jangan di-commit.
- Virgin (2025/2026) dibaca tepat SEKALI bila ada kandidat lolos dev; 2026/2027 tidak disentuh.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan sentuh workspace liga lain (SG/MD/KW bekerja paralel).
