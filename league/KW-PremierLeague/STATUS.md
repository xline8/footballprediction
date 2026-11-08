# KW-PremierLeague — STATUS

- Status: SELESAI — G FAIL (gerbang dev), S/C/K/T not-buildable; virgin TIDAK dibaca; deliverable siap di outbox, menunggu verifikasi Jarvis
- Liga: KW-PremierLeague (Kuwait Premier League, tier 1, FotMob 529)
- Fase saat ini: Fase 7 SELESAI — deliverable di outbox-muse2/KW-PremierLeague/ (repo papan, branch main), menunggu verifikasi Jarvis
- Terakhir diperbarui: 2026-11-10 oleh sub-agen Muse-2 (Fase 7)
- Referensi commit pra-registrasi: `c8988cf143b507f0f5c6d6e15f466d84e1f248e5` (branch wip-kw-premierleague, ter-push SEBELUM fitting apa pun)
- Pos jatah di papan: issue #1 komentar 6763121416 (Assignments 16–19; diproses setelah persetujuan user 2026-11-10 19:25 WIB). ACK KW 6767295066 (koordinator).
- Data: release bundle-kw-premier; 711 JSON terekstrak = index_529.csv (711 baris); yang dimainkan 642.

## Hasil akhir (vonis)

- G-KW: FAIL (gerbang dev, leg OU vs klimatologi saja) — Gate Zero pooled dev (n=422) 1X2 LL 0,9436 / RPS 0,1882 / OU2.5 LL 0,7293 vs klimatologi 1,0767 / 0,2357 / 0,6806 dan naive trailing-10 1,0108 / 0,2086 / 0,7405 (menang dari kedua baseline di 1X2 + RPS, menang OU vs naive, kalah OU vs klimatologi). SHRINK identik; X2 lebih buruk pooled (0,9496 / 0,1899 / 0,7371). Virgin 2025/2026 TIDAK PERNAH dibaca; 2026/2027 tidak disentuh. Re-run reproduksibel (md5 results_dev.json 67e9e6f0ea63509fb13b64cb0f0a8d2e).
- S-KW: NOT-BUILDABLE — stats feed 0/711, shotmap 0/711.
- C-KW: NOT-BUILDABLE — alasan sama (tidak ada target corners dari sumber mana pun).
- K-KW: NOT-BUILDABLE — tidak ada target yellows di musim mana pun: stats absen + event Yellow/YellowRed polos = 0 di SELURUH corpus (hanya 53 Red lurus); referee 0%.
- T-KW: NOT-BUILDABLE — alasan sama seperti S-KW.
- Tidak ada kandidat yang lolos; tidak ada yang dikirim (no shipping arm, no predictions, no results_virgin.json).

## Temuan kunci (Fase 0–2)

- **Label musim ganda TERSELESAI**: "2021" dan "2021/2022" adalah musim BERBEDA (0 match id sama, tanggal disjoint: Jan–Mei 2021 vs Nov 2021–Apr 2022; Kuwait beralih kalender → split). Keduanya dipertahankan verbatim sebagai musim terpisah; urutan kanonik 2021 < 2021/2022 < 2022/2023 < ... Tidak ada deduplikasi.
- **69 fixture index tidak pernah dimainkan** (finished=false, skor index placeholder "0-0"): 26/21/12/10 di empat musim pertama; dikeluarkan. Corpus dimainkan: 642 (64/69/120/122/111/111/45). "711 played" di BRIEF = jumlah baris index.
- **Scores-only absolut**: stats feed 0/711, shotmap 0, lineup 0, referee 0, xG tidak ada.
- **Events hanya dari 2024/2025** (0 di semua musim dev sebelumnya; 87/111 di 2024/2025; 0 mismatch skor di 237 match berevent). Konstanta halves gol 0,4411 dari 87 match itu saja (297 gol) — basis tertipis sejauh ini, dicatat.
- Split: warm-up 2021 (n=64), dev scored 2021/2022–2024/2025 (n=422), virgin 2025/2026 (n=111), cadangan 2026/2027 (45) tak disentuh.
- Reliabilitas trait kuat: split-half GF r 0,786 / GA r 0,922 (13 tim). X2 KEPT: 8 transisi entrant dev, GF diff −0,390 (7/8 negatif), GA diff +0,404 (5/8 positif), offset ter-clamp g_log −0,2231 / c_log +0,2231.
- Garis beku OU 2.5 (over-rate dev scored 0,5877); home win 0,4265; draw 0,2370; mean team goals 1,5640.
- Fase main/championship/relegation = baris biasa berflag; 1 match awarded (4067510, 2022/2023).

## Langkah berikutnya persis

1. SELESAI — tidak ada langkah berikutnya; menunggu verifikasi Jarvis di papan (pos done oleh KOORDINATOR). Bila Jarvis meminta perbaikan, kerjakan dari STATUS ini.

## Catatan pemulihan

- STATUS ini ada di folder workspace liga DAN di outbox liga; board-state.json di ~/league-remote/ jangan di-commit.
- Jangan pakai Codex (tidak login, jangan login ke akun ChatGPT user). Bekerja memakai sub-agen Muse sendiri.
- Jangan posting apa pun di papan GitHub sendiri; koordinator yang memposting.
- Jangan sentuh workspace liga lain (SG/MD/IN dibangun paralel).
