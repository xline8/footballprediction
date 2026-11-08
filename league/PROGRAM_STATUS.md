# League Model Program — Status Ledger

Spine of the per-league model program (user mandate 2026-11-09 14:38 WIB).
Updated at EVERY wave/step transition, failures included — a dead builder
is recorded as dead here, never silently dropped (continuity requirement,
user 2026-11-09 14:41 WIB). A separate monitor agent reads this file.

Conventions: step = 1 understanding · 2 preprocessing · 3 EDA ·
4 visualization · 5 feature engineering · 6 design · B build · G gate.
Verdicts: PASS / FAIL per gate leg, from the candidate's report in
`league/<L>/reports/`. All timestamps WIB (Asia/Jakarta).

## Program counters & heartbeat

- Leagues fully completed (all buildable candidates through gates): **156**
  (J3 — G-J3 FAIL. J2 — G-J2 FAIL + K-J2 FAIL. **J1 — 3 PASS (S-J1,
  C-J1, T-J1) + 2 FAIL (G-J1, K-J1). AT-Bundesliga — 0 PASS / 5 FAIL.
  DK-Superligaen — 2 PASS provisional (C-DK, T-DK arm C) / 3 FAIL.
  NL-Eredivisie — 2 PASS provisional (S-NL, T-NL arm A) / 3 FAIL.
  AU-ALeague — 4 PASS (S-RS, C, K, T-A) / 1 FAIL (G-AU).
  US-MLS — 3 PASS (S, C, T-C) / 2 FAIL (G-US, K-US).
  BR-SerieA — 2 PASS (S-RS, T-C) / 3 FAIL.
  AR-LigaProfesional — 1 PASS provisional (C-AR) / 4 FAIL.
  SCO-Premiership — 4 PASS (G, S, C provisional; T-B clean) / 1 FAIL.
  CH-SuperLeague — 3 PASS provisional (S-RS, C, T-A) / 2 FAIL.
  SE-Allsvenskan — 3 PASS (T-A clean; S-X4, C-X7 provisional) / 2 FAIL.
  NO-Eliteserien — 3 PASS (K clean; C, T-A provisional) / 2 FAIL.
  BE-FirstDivisionA — 2 PASS (K clean; S-RS provisional) / 3 FAIL.
  ENG-Championship — 2 PASS provisional (S-RS, C) / 3 FAIL.
  PT-LigaPortugal — 0 PASS / 5 FAIL.
  DE-2Bundesliga — 2 PASS provisional (S-RS, K-X8) / 3 FAIL.
  IN-ISL — 2 PASS provisional (S, C — Gate Zero) / 3 FAIL.
  KR-KLeague1 — 1 PASS provisional (K) / 4 FAIL.
  SA-ProLeague — 3 PASS provisional (S-RS, C, T-A) / 2 FAIL.
  BG-SecondLeague — 0 PASS / 1 FAIL (G-BG2 dev) + 4 not-buildable.
  TR-SuperLig — 4 PASS (T-A clean; G-X3, S, C provisional) / 1 FAIL.
  GE-Erovnuli — 0 PASS / 1 FAIL (G dev) + 4 not-buildable.
  MX-LigaMX — 1 PASS provisional (C) / 4 FAIL.
  IL-Leumit — 0 PASS / 1 FAIL (G dev) + 4 not-buildable.
  IT-SerieC — 0 PASS / 1 FAIL (G dev) + 4 not-buildable.
  PT-LigaPortugal2 — 0 PASS / 1 FAIL (G dev, semua kaki ke
  klimatologi) + 4 not-buildable.
  CO-PrimeraB — 0 PASS / 1 FAIL (G dev, semua arm) + 4
  not-buildable.
  PY-DivisionProfesional — 0 PASS / 5 FAIL (lengkap).
  ES-LaLiga2 — 3 PASS provisional / 2 FAIL (lengkap).
  DE-3Liga — 2 PASS provisional (C X7, T A) / 3 FAIL.
  ENG-LeagueOne — 3 PASS (1 clean) / 2 FAIL.
  CO-PrimeraA — 3 PASS (2 clean) / 2 FAIL.
  BR-SerieB — 2 PASS provisional / 3 FAIL.
  IT-SerieB — 2 PASS (1 clean) / 3 FAIL.
  FR-Ligue2 — 2 PASS provisional / 3 FAIL.
  US-USLChampionship — 2 PASS (1 clean) / 3 FAIL.
  PL-Ekstraklasa — 2 PASS (1 clean) / 3 FAIL.
  GR-SuperLeague — 2 PASS clean / 3 FAIL.
  EG-PremierLeague — 2 PASS (1 clean) / 3 FAIL.
  NL-EersteDivisie — 2 PASS provisional / 3 FAIL.
  RO-LigaI — 1 PASS provisional / 3 FAIL / 1 not-buildable.
  PE-Liga1 — 3 PASS provisional / 2 FAIL.
  RU-PremierLeague — 2 PASS provisional / 3 FAIL.
  RU-1Division — 1 PASS provisional / 4 FAIL.
  IE-PremierDivision — 1 PASS provisional / 4 FAIL.
  TH-ThaiLeague — 2 PASS (1 clean) / 3 FAIL.
  ZA-PSL — 1 PASS provisional / 4 FAIL.
  CZ-Liga — 2 PASS provisional / 2 FAIL / 1 not-buildable.
  BG-FirstLeague — 3 PASS (2 clean) / 2 FAIL.
  CL-LigaDePrimera — 3 PASS (1 clean) / 2 FAIL.
  AT-2Liga — 0 PASS / 5 FAIL.
  CN-SuperLeague — 3 PASS provisional (S, K — Gate Zero; T arm B)
  / 2 FAIL.
  CY-1Division — 2 PASS (C clean; T-A provisional) / 3 FAIL.
  NO-OBOSLigaen — 1 PASS provisional (C) / 4 FAIL.
  UA-PremierLeague — 0 PASS / 5 FAIL.
  KR-KLeague2 — 0 PASS / 5 FAIL (semua di dev; virgin utuh).
  SE-Superettan — 1 PASS provisional (K) / 4 FAIL.
  US-USLLeagueOne — 2 PASS provisional (C, T-B) / 3 FAIL.
  FI-Veikkausliiga — 1 PASS provisional (K) / 3 FAIL /
  1 not built.
  TR-1Lig — 0 PASS (G dev) / 4 not buildable.
  HU-NBI — 1 PASS provisional (C) / 4 FAIL.
  BE-FirstDivisionB — 0 PASS (G dev) / 4 not buildable.
  SK-1Liga — 1 PASS clean (S) / 3 FAIL / 1 not buildable.
  AE-ProLeague — 1 PASS provisional (T-C) / 4 FAIL.
  HR-HNL — 1 PASS provisional (C-X7) / 3 FAIL / 1 not built.
  TH-ThaiLeague2 — 0 PASS / 2 FAIL / 3 not buildable.
  DK-1Division — 4 PASS (K clean; S, C-X5, T-X5 provisional)
  / 1 FAIL.
  CA-PremierLeague — 0 PASS / 5 FAIL.
  ID-SuperLeague — 0 PASS / 2 FAIL / 3 not buildable.
  SCO-Championship — 0 PASS / 5 FAIL.
  CH-ChallengeLeague (EXTERNAL — built by [Muse-2], verified +
  merged locally by Jarvis, commit 60c17b0) — 0 PASS / 5 FAIL.
  CL-LigaDeAscenso — 0 PASS / 1 FAIL (G dev) / 4 not buildable.
  AU-ALeagueWomen — 3 PASS provisional (S-RS, C-X7, K-X8) /
  2 FAIL.
  IS-BestaDeildin — 3 PASS provisional (S-GZ, C-X7, T-B) /
  2 FAIL.
  MA-BotolaPro — 0 PASS / 5 FAIL.
  EC-SerieA (EXTERNAL — built by [Muse-2], verified + merged
  locally by Jarvis, commit bc6d400) — 0 PASS / 5 FAIL (G-EC
  FAIL at dev, OU leg; S/C/K/T NOT BUILDABLE).
  RS-SuperLiga (EXTERNAL — built by [Muse-2], verified +
  merged locally by Jarvis, commit bc6d400) — 0 PASS / 5 FAIL
  (G-RS FAIL at dev, OU leg; S/C/K/T NOT BUILT, feasibility).
  MX-ExpansionMX — 0 PASS / 2 FAIL (G/K virgin) /
  3 NOT BUILDABLE.
  BR-SerieC — 0 PASS / 1 FAIL (G-BRC dev) / 4 NOT BUILDABLE.
  IL-LigatHaAl (EXTERNAL — built by [Muse-2], verified +
  merged locally by Jarvis, commit 4f37e8d2) — 0 PASS / 5
  FAIL (G-IL FAIL virgin legs i+ii; S/C/K/T NOT BUILDABLE).
  QA-QatarStars (EXTERNAL — built by [Muse-2], verified +
  merged locally by Jarvis, commit 4f37e8d2) — 0 PASS / 5
  FAIL (G-QA FAIL dev gate; S/C/K/T NOT BUILDABLE).
  BO-PrimeraDivision — 0 PASS / 5 FAIL (G/C/K dev; S/T
  virgin).
  EE-Meistriliiga — 0 PASS / 1 FAIL (G-EE dev) / 4 NOT
  BUILDABLE.
  SA-FirstDivision — 1 PASS CLEAN (S-SAFD Gate Zero) /
  4 FAIL.
  CZ-FNL — 0 PASS / 1 FAIL (G-CZ-FNL dev) / 4 NOT
  BUILDABLE.
  LV-Virsliga — 1 PASS CLEAN (S-LV Gate Zero) /
  4 FAIL.
  FI-Ykkosliiga — 0 PASS / 1 FAIL (G-YK dev) / 4 NOT
  BUILDABLE.
  CO-Superliga — 0 PASS / 0 FAIL / 5 NOT BUILDABLE.
  DK-2Division — 0 PASS / 1 FAIL (G-DK2 dev) / 4 NOT
  BUILDABLE.
  VE-PrimeraDivision — 0 PASS / 5 FAIL.
  QA-SecondDivision — 0 PASS / 5 FAIL (all dev).
  NO-2Divisjon — 0 PASS / 1 FAIL (G-NO dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  RU-SecondLeague — 0 PASS / 1 FAIL (G-RU2 dev) / 4 NOT
  BUILDABLE.
  AR-PrimeraBNacional — 1 PASS PROVISIONAL (K-BNAC X8) /
  1 FAIL (G-BNAC dev) / 3 NOT BUILDABLE.
  SE-Ettan — 0 PASS / 1 FAIL (G-SE dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  GR-SuperLeague2 — 0 PASS / 1 FAIL (G-GR2 dev) / 4 NOT
  BUILDABLE.
  IQ-StarsLeague — 0 PASS / 1 FAIL (G-IQSL dev) / 4 NOT
  BUILDABLE.
  AR-PrimeraBMetropolitana + TorneoFederalA (FotMob 9213 —
  one league id, two sub-leagues, counted as ONE league) —
  0 PASS / 2 FAIL (G-PBM + G-FEDA dev) / S/C/K/T NOT
  BUILDABLE.
  ES-PrimeraFederacion — 0 PASS / 1 FAIL (G-ESPF dev) / 4
  NOT BUILDABLE.
  NG-ProfessionalLeague — 0 PASS / 1 FAIL (G-NG dev) / 4
  NOT BUILDABLE.
  UY-LigaAUF — 0 PASS / 1 FAIL (G-UY dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  NL-TweedeDivisie — 0 PASS / 1 FAIL (G-NLTD dev) / 4 NOT
  BUILDABLE.
  FI-Ykkonen — 0 PASS / 1 FAIL (G-FI dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  PL-ILiga — 0 PASS / 1 FAIL (G-PL-ILiga dev) / 4 NOT
  BUILDABLE.
  GH-PremierLeague — 0 PASS / 1 FAIL (G-GH dev) / 4 NOT
  BUILDABLE.
  PT-Liga3 — 0 PASS / 1 FAIL (G-PT3 dev) / 4 NOT
  BUILDABLE.
  PL-IILiga — 0 PASS / 1 FAIL (G-PL-II dev) / 4 NOT
  BUILDABLE.
  CN-LeagueOne — 0 PASS / 1 FAIL (G-CN dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  IR-AzadeganLeague — 0 PASS / 1 FAIL (G-IRAZ dev) / 4 NOT
  BUILDABLE.
  SV-PrimeraDivision — 0 PASS / 1 FAIL (G-SV dev) / 4 NOT
  BUILDABLE.
  FR-Ligue3 — 0 PASS / 1 FAIL (G-FR dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  BY-PremierLeague — 0 PASS / 1 FAIL (G-BY dev) / 4 NOT
  BUILDABLE (external, Muse-2).
  GT-LigaNacional — 0 PASS / 1 FAIL (G-GT dev) / 4 NOT
  BUILDABLE.
  RO-LigaII — 0 PASS / 1 FAIL (G-RL2 dev) / 4 NOT
  BUILDABLE.
  CR-PrimeraDivision — 0 PASS / 2 FAIL (G-CR dev, K-CR virgin
  calibration) / 3 NOT BUILDABLE.
  AU-Championship — 0 PASS / 0 FAIL / 5 NOT BUILDABLE
  (FotMob 8938 is a parent container of 10 competitions; only
  87 rows are the true Championship, one complete season only).
  DZ-Ligue1 — 0 PASS / 1 FAIL (G-DZ dev) / 4 NOT
  BUILDABLE.
  LU-NationalDivision — 0 PASS / 1 FAIL (G-LU dev, 3/6 legs) / 4
  NOT BUILDABLE.
  SK-2Liga — 0 PASS / 1 FAIL (G-SK2 dev OU2.5 leg, miss 0.000099) / 4
  NOT BUILDABLE.
  IR-PersianGulf — 0 PASS / 1 FAIL (G-IRPG dev OU2.5 leg, −0.0113) / 4
  NOT BUILDABLE.
  KR-KLeague3 — 0 PASS / 1 FAIL (G-KR3 dev, all 3 legs) / 4 NOT
  BUILDABLE.
  TZ-PremierLeague — 0 PASS / 1 FAIL (G-TZ dev OU2.5 leg, +0.0234) / 4
  NOT BUILDABLE.
  NI-Premiership — 0 PASS / 1 FAIL (G-NI dev OU2.5 leg, 5/6 legs) / 4
  NOT BUILDABLE.
  CY-2Division — 0 PASS / 1 FAIL (G-CY2 dev, LL + OU legs) / 4 NOT
  BUILDABLE.
  UY-SegundaDivision — 0 PASS / 1 FAIL (G-UYSEG dev, all 3 legs) / 4
  NOT BUILDABLE.
  WAL-CymruPremier — 0 PASS / 1 FAIL (G-WAL dev OU2.5 leg, +0.0188) / 4
  NOT BUILDABLE.
  HN-LigaNacional — 0 PASS / 1 FAIL (G-HN dev OU2.5 leg, +0.0103) / 4
  NOT BUILDABLE.
  TN-LigueI — 0 PASS / 1 FAIL (G-TN virgin OU calibration +8.02pp) / 4
  NOT BUILDABLE.
  LT-Toplyga — 0 PASS / 1 FAIL (G-LT dev OU2.5 leg, +0.0106) / 4
  NOT BUILDABLE.
  KZ-PremierLeague — 1 PASS PROVISIONAL (G-KZ Gate Zero) / 4 NOT
  BUILDABLE.
  BA-PremierLeague — 1 PASS PROVISIONAL (G-BA Gate Zero) / 4 NOT
  BUILDABLE.
  IE-FirstDivision — 0 PASS / 1 FAIL (G-IEFD dev OU2.5 leg) / 4 NOT
  BUILDABLE.
  MK-PrvaLiga — 0 PASS / 1 FAIL (G-MK dev OU2.5 leg) / 4 NOT
  BUILDABLE.
  VN-VLeague — 0 PASS / 1 FAIL (G-VN dev RPS + OU2.5 legs) / 4 NOT
  BUILDABLE.
  AL-KategoriaSuperiore — 0 PASS / 1 FAIL (G-AL dev, all 3 legs) /
  4 NOT BUILDABLE.
  ME-1CFL — 0 PASS / 1 FAIL (G-ME virgin LL leg) / 4 NOT BUILDABLE.
  AM-PremierLeague — 0 PASS / 1 FAIL (G-AM dev OU2.5 leg, +0.0123) / 4
  NOT BUILDABLE.
  SLO-PrvaLiga — 0 PASS / 1 FAIL (G-SLO dev OU2.5 leg, +0.0014) / 4
  NOT BUILDABLE.
  SCO-LeagueOne — 0 PASS / 2 FAIL (G-SCO-L1 dev OU; K-SCO-L1 virgin
  LL + calibration) / 3 NOT BUILDABLE.
  AZ-PremierLeague — 0 PASS / 1 FAIL (G-AZ virgin OU calibration
  −6.29pp) / 4 NOT BUILDABLE.
  SG-PremierLeague — 0 PASS / 1 FAIL (G-SG dev OU2.5 leg) / 4 NOT
  BUILDABLE. (EXTERNAL — Muse-2.)
  MD-NationalDivision — 0 PASS / 1 FAIL (G-MD virgin legs i + ii, OU
  calibration −11.69pp) / 4 NOT BUILDABLE. (EXTERNAL — Muse-2.)
  KW-PremierLeague — 0 PASS / 1 FAIL (G-KW dev OU2.5 leg) / 4 NOT
  BUILDABLE. (EXTERNAL — Muse-2.)
  IN-IndianFootballLeague — 0 PASS / 1 FAIL (G-IN dev, 2/6 legs) / 4
  NOT BUILDABLE. (EXTERNAL — Muse-2.)
  BD-FootballLeague — 0 PASS / 1 FAIL (G-BD dev OU2.5 leg, +0.0784) /
  4 NOT BUILDABLE.
  IS-1Deild — 0 PASS / 1 FAIL (G-IS1 dev, all 3 legs) / 4 NOT
  BUILDABLE.
  MY-LigaSuper — 0 PASS / 1 FAIL (G-MY dev, OU + RPS legs) / 4 NOT
  BUILDABLE.
  IS-2Deild — 0 PASS / 1 FAIL (G-IS2 dev, all 3 legs) / 4 NOT
  BUILDABLE.
  FO-Logmanssteypid — 0 PASS / 0 FAIL / 5 NOT BUILDABLE (cup final,
  1 match/season — no dev/virgin window).
  HU-NBII — 0 PASS / 0 FAIL / 5 NOT BUILDABLE (2025/26 only 96/240
  genuine final scores — 103 no-scoreStr placeholders + 41 mid-match
  partials; no gateable dev window; virgin unread).
  UZ-Superliga — 0 PASS / 0 FAIL / 5 NOT BUILDABLE (one partial
  season only, 2026 215/240 in progress; zero complete seasons; no
  gateable dev window; virgin unread).
  NZ-Championship — 0 PASS / 1 FAIL (G-NZ dev, all 3 legs) / 4 NOT
  BUILDABLE.
  FO-PremierLeague — 0 PASS / 2 FAIL (G-FO dev OU leg; K-FO dev,
  Gate Zero vs base rate) / 3 NOT BUILDABLE.
  PA-LPF — 0 PASS / 1 FAIL (G-PA dev, LL +0,0010 / RPS +0,0005 vs
  climatology; virgin not read) / 4 NOT BUILDABLE.**
  A FAIL verdict still completes a league: the process ran honestly
  to its end.)
- Milestones reported to user: **6** (25-league milestone recorded 2026-11-09; 50-league milestone recorded 2026-11-10; **75-league milestone recorded 2026-11-10**; **100-league milestone recorded 2026-11-10**; **125-league milestone recorded 2026-11-10**; **150-league milestone recorded 2026-11-10** — see MILESTONE #6 line in the event log; next at 175 completed
  leagues (19 to go) — when the count crosses a NEW multiple of 25, add a dated
  MILESTONE line in the event log listing those 25 leagues + verdict
  tallies, and increment this marker; never report the same multiple
  twice. Delivery to the user happens from the main chat/watchdog
  using that marker.)
- Phase Final activation — BE-FirstDivisionA: **JOINED 2026-11-09** — merged 88314c7 (conflicts resolved serially; BE block appended after SE). Proof: 207 fixtures × 2 markets, recompute 0.0 both markets, run 2 fetched 0, 31 prior files bit-identical; BE SOT engine was the fifth missing ratio_prior (fixed); builder hard-equality assert → floor >= 1698; cards settle verified WITHOUT override (gate target == stats columns on 1,695/1,695 stats rows). Runner now serves **11 leagues / 29 markets**
- Phase Final activation — ENG-Championship: **JOINED 2026-11-09** — merged 6a09d11 (conflicts resolved serially; ENG block appended after NO). Proof: 372 fixtures × 2 markets, recompute 0.0 both, run 2 fetched 0, 205 files bit-identical; ENG SOT engine was the sixth missing ratio_prior (fixed); builder assert → floor >= 2963. Runner now serves **13 leagues / 34 markets**
- Phase Final activation — DE-2Bundesliga: **JOINED (SOT only) 2026-11-09** — merged 0e058b9. SOT RS live (207 fixtures, recompute 0.0). **Cards X8 STOPPED at the operational gate (case b)**: FotMob's leagues payload has no referee field; matchDetails Referee.text is empty for all 6 nearest upcoming fixtures (populated only around matchday), while 230/306 (75,2%) of X8's virgin predictions carried an active referee multiplier — a daily fallback-driven run would ship Gate Zero under the X8 label. Not shipped; revisit only if appointments appear pre-match in the pull. Runner now serves **14 leagues / 35 markets**
- Phase Final activation — IN-ISL: **JOIN QUEUED** (next free slot; sot/gate_zero primary 8.5 halves 0,453 + corners/gate_zero primary 10.5 halves 0,458; config from ISL's frozen preregs). Held, with DE-3Liga, to respect the 6-concurrent cap (4 builds + 2 joins in flight).
- Phase Final activation — KZ-PremierLeague: **JOINED 2026-11-11** — merged efb502eb (branch build/runner-kz b0336713; active.yaml/README/run_daily.py merged cleanly). Proof: 2 full end-to-end runs, 58 leagues / 118 markets, 13,031 predictions each, 0 errors, fetched_new=0 in run 2; KZ 0 upcoming (2027 season unpublished), header-only daily CSV, empty ledger; 291/292 snapshot files bit-identical (exception HR-HNL corners — FotMob moved 12 fixture dates between runs, upstream listing change). Signature-dispatched goals adapter (5-arg engines); trap proven (HEAD TypeError on KZ), inertness proven on SCO/TR goals byte-identical. Runner now serves **58 leagues / 118 markets**
- Phase Final activation — BA-PremierLeague: **JOINED 2026-11-11** — merged ad5cc1fd (merge of branch build/runner-ba e2143005; active.yaml/README/run_daily.py merged cleanly — exactly the builder's 3 files, 42 insertions / 6 deletions). Proof: 2 full end-to-end runs, 59 leagues / 119 markets, 13,146 predictions each, 0 errors, fetched_new=0 in both runs; BA 115 upcoming (first 2026-11-21) / 115 predicted / 0 settled / 0 errors; 295/296 snapshot files bit-identical (exception ZA-PSL corners — FotMob renamed AmaZulu to AmaZulu FC between runs, same 160 rows, numerics identical, upstream listing change). Goals adapter: xG columns read with .get() (scores-only league) + exclude_awarded opt-in (4 awarded matches excluded per the frozen prereg); inertness proven on SCO/TR goals byte-identical; independent recompute of the 115 live predictions exact on all 19 fields; synthetic settlement on finished match 5927590 verified once-only. Runner now serves **59 leagues / 119 markets** — the LAST join; join queue EMPTY.
- Improvement program Lane 1 — TZ-PremierLeague goals (SHRINK): **JOINED 2026-11-11** (Lane 1 PROVISIONAL PASS; merged c979d05a). Proof: 2 full runs, 13,283 predictions each, 0 errors; 451/451 prediction/state files bit-identical; TZ 137 upcoming / 137 predicted / 0 errors; independent recompute of all 137 live predictions diff 0.0 on every float field; merged state verified (active.yaml parses: 60 leagues / 120 markets). Runner now serves **60 leagues / 120 markets**. Lane 1 ledger: league/IMPROVEMENT_STATUS.md.
- Improvement program Lane 1 — FO-PremierLeague cards (SHRINK): **JOINED 2026-11-11** (Lane 1 CLEAN PASS; merged 885a27bb). Proof: 2 full runs, 13,146 / 13,148 predictions, 0 errors (one transient LV feed pull error in run 2, zero output impact); FO and AU snapshots byte-identical between runs, remaining diffs all live-feed-explained; synthetic settlement settled 1-then-0 with files restored byte-identical; merged state verified (active.yaml parses: 61 leagues / 121 markets; run_daily.py compiles). FO's 2026 season is complete — it predicts live when 2027 fixtures publish. Runner now serves **61 leagues / 121 markets**.
- Improvement program Lane 1 — ID-SuperLeague cards (X5 blend): **JOINED 2026-11-11** (Lane 1 CLEAN PASS; merged 8f8b4b00). Proof: 2 full runs, 13,374 predictions each, 0 errors; 301/301 snapshot files bit-identical; ID 226 upcoming / 226 predicted / 0 errors; independent recompute diff 0.0 on all 12 float fields; history load exactly 1,376 rows. Merged state verified functionally (runner's own parser: 62 leagues / 122 markets; merged _cards_history_rows loads ID 1,376 and FO 809 rows exactly). Runner now serves **62 leagues / 122 markets**. Lane 1 wave 1 fully closed (13 verdicts, 3 unblocked joins); K-CO (CO-PrimeraA cards X8, provisional pass) remains HELD-BY-REFEREE-GATE per user decision 2026-11-11 19:47 — recheck as matchdays approach, join as provisional when ≥1 upcoming fixture names a referee.
- HEARTBEAT: 2026-11-11 18:21 WIB — **■ Program selesai.** BA-PremierLeague JOINED 17:55 (ad5cc1fd; merge of branch build/runner-ba e2143005) — verified in merged state by the 18:14 watchdog check (active.yaml parses: 59 leagues / 119 markets; run_daily.py compiles; merge diff exactly the builder’s 3 files, 42 insertions / 6 deletions). 156 leagues complete, 122 passing markets. Final audit COMPLETE (league/AUDIT.md; 785 candidates — 122 PASS / 309 FAIL / 353 NOT_BUILDABLE / 1 NOT_BUILT — T-FI held; 12 bug-fix commits, no verdict changed). Join queue EMPTY, build queue EXHAUSTED — the league build program is COMPLETE. Remaining follow-on work is the improvement program P1–P6, Gate Zero phase (charter league/IMPROVEMENT_PROGRAM.md; Gate Zero not yet started). The 175 milestone is moot (final total 156 leagues; milestones reported stays 6). No QUOTA-WAIT, no PAUSED-BY-USER.

## Phase Final — Daily League Pipeline (BUILD ITEM — activates per league on first PASS)

Registered as a design note 2026-11-09 14:46 WIB; **upgraded to a build
item by the user 2026-11-09 14:50 WIB**: do NOT wait for the whole
program. **Trigger: the moment the first candidate records a PASS
verdict, the coordinator builds the daily league runner** (its own
builder + branch, same two-agent flow), and every subsequently passing
league joins the same runner automatically (its config lists passing
markets only). Activation per league is recorded in the table below
and in the event log. The runner gets its **own daily cron**, created
by the coordinator when it first goes live — separate from the 08:52
top-5 report, which stays untouched.

Activation state: **TRIGGERED 2026-11-09 15:08 WIB** — first PASS:
S-J1 (Gate Zero ships). Runner build status: BUILDING (branch
build/daily-runner) with J1/SOT as the first active league-market;
the runner's own daily cron is created by the coordinator when the
runner first goes live.

| League | First PASS (candidate, date) | Joined daily runner |
|---|---|---|
| J1 | S-J1, 2026-11-09 | **JOINED 2026-11-09** — runner merged (203372c); markets: SOT/GZ (0,448) + corners/gate_zero (0,447) + total_shots/arm-A (0,455); cron `league-daily-runner` created, daily ±07:52 WIB, separate from the 08:52 top-5 report; day-one ledger 720 entries (240/market), 0 settled as expected |
| DK-Superligaen | C-DK + T-DK, 2026-11-09 | **JOINED 2026-11-09** — runner extension merged (4173106: world source kind, league-generic, arm-C adapter; one J1-literal residue in predict_sot parametrised). Coordinator's own post-merge run from the main checkout: DK predicted 48 corners + 48 total_shots, daily CSVs written, ledger created, 0 errors; J1 unchanged (240×3). Markets: corners/gate_zero (0,488, 9.5) + total_shots/arm-C (0,470, 25.5) |
| NL-Eredivisie | S-NL + T-NL, 2026-11-09 | **JOINED 2026-11-09** — merged a7b6de5. predict_sot conventions parametrised (div + ladder_1h/2h from config, J1 defaults preserved); NL data-builder count assert made a floor for daily rebuilds. Proof: 198 fixtures × 2 markets, run 2 fetched 0, J1+DK files bit-identical (11 md5s), independent recomputes exact on all 12 fields for both markets. Markets: sot/GZ (0,446, 9.5) + total_shots/arm-A (0,449, 26.5) |
| AU-ALeague | S-AU + C-AU + K-AU + T-AU, 2026-11-09 | **JOINED 2026-11-09** — merged 632f6a0. First cards adapter (gate_zero, total yellows) + ratio_prior as config (AU RS = 20,000; sensitivity proven: prior 200 gives different numbers, 20,000 reproduces the engine's RS exactly). Proof: 133 fixtures × 4 markets, run 2 fetched 0, J1/DK/NL bit-identical, 4-market recompute of one fixture exact, synthetic cards settlement hand-verified (log-loss to full precision), artifacts restored md5-clean. AU builder floor assert fixed like NL's |
| US-MLS | S-US + C-US + T-US, 2026-11-09 | **JOINED 2026-11-09** — merged 6f77f20 (combined with BR). Real fixtures existed after all (14 MLS playoff fixtures from 2026-11-20): predicted 14×3, recompute exact in all three markets. Defect fixed en route: MLS+BR SOT engines lacked the runner's ratio_prior kwarg (would have TypeError'd every SOT prediction); MLS builder count equalities floored |
| BR-SerieA | S-BR + T-BR, 2026-11-09 | **JOINED 2026-11-09** — merged 6f77f20 (combined with MLS). 41 real upcoming fixtures predicted ×2 markets; recompute exact (SOT RS + total shots arm C). The runner now serves **6 leagues / 16 markets** daily |
| AR-LigaProfesional | C-AR, 2026-11-09 | **JOINED 2026-11-09** — merged fe8c6b2. Realised as option (a): arm label `x7` passed to the AR engine's own fit/predict path (option (b) proven numerically false — GZ params in the x7 path IndexError; mus differ). Proofs: virgin tie-in float-exact, history-truncated replay float-exact, 8 real playoff fixtures predicted, run 2 fetched 0. **Two catches:** (1) a latent runner adapter bug — AR's builder encodes missing touches as the string "nan", which leaked float NaN into 2,579 territorial feature values (multipliers clamped at 1.43); fixed in the adapter, proven no-op for the existing corners leagues; (2) AR prereg/verdict freeze the corners halves share at 0,480 but the harness's write_predictions hard-coded 0,462 — the shipped virgin CSV's halves sit at 0,462; the runner follows the prereg (0,480); FT unaffected, verdict unaffected (halves are presentation-only) — flagged for the final audit |
| SCO-Premiership | G/S/C/T-SCO, 2026-11-09 | **JOINED 2026-11-09** — merged 8ef6342 after the coordinator resolved an interleaved active.yaml conflict by rewriting the AR/CH/SCO tail (all three blocks verified present; YAML parses). Proof (join builder): 122 fixtures × 4 markets, all four recomputed bit-exact in separate processes incl. leak checks (train strictly before each fixture date), synthetic goals settlement exact to <1e-12, run 2 fetched 0, all 28 prior-league files bit-identical. One Codex defect (row builders read `away` instead of `away_team`) caught by proof run 1 and fixed pre-merge. Runner now serves goals for the first time |
| CH-SuperLeague | S/C/T-CH, 2026-11-09 | **JOINED 2026-11-09** — merged 4b63dea (merge conflict in active.yaml + README vs the AR join resolved by the coordinator's serialised edit — both league blocks kept, exactly the speed-up rule's collision case). Proof: 54 fixtures × 3 markets, recompute exact in all three (RS sensitivity shown again), run 2 fetched 0, all prior leagues bit-identical; CH SOT engine needed the ratio_prior kwarg (third engine with that trap). Coordinator's own post-merge run from the main checkout: 8 leagues, CH predicted 54, errors []. Runner now serves **8 leagues / 20 markets** |
| SE-Allsvenskan | S/C/T-SE, 2026-11-09 | **JOINED 2026-11-09** — merged a0c78c4 (active.yaml + README conflicts resolved serially; SE block appended after SCO). Proof: Sweden is NOT off-season after all — 16 live fixtures (2026 season's final rounds) × 3 markets, every field float-exact on recompute; X4-vs-GZ dispatch proven real (AIK–Degerfors exp 8,6499 vs 9,0589); SE SOT engine was the fourth missing the ratio_prior kwarg (fixed, no-arg identical); data builder needed no floor change; run 2 fetched 0, all 52 prior files bit-identical. Runner now serves **10 leagues / 27 markets** |
| NO-Eliteserien | C/K/T-NO, 2026-11-09 | **JOINED 2026-11-09** — merged 53ebff0 (active.yaml conflict resolved serially; NO block appended last). The cards_actual fix (faafadc) was inspected by the coordinator directly in the diff: settle() uses the override only when the cards block carries it, default = the old stats pair, so AU/BE are bit-identical by construction. NO's join-builder completion handoff was the second one lost across compaction — the coordinator caught it via a full branch sweep and verified the fix commit itself; the merged-state full run (below) is the go-live evidence. Runner now serves **12 leagues / 32 markets** |

Once a league has at least one PASSING market, it joins a daily run:

1. Fixtures + results from **FotMob only** (fixtures endpoints per
   league-season; incremental matchDetails only for newly played
   matches, reusing the resumable puller — never a full re-pull).
2. The league's CSV is appended with the new matches.
3. The league's engine refits/updates on the extended data.
4. Predictions for upcoming matches are written to
   `league/<L>/predictions/` (FT + halves via the league's frozen
   constants).
5. Yesterday's predictions are settled from FotMob results into that
   league's own grading ledger.

Per-league failures are isolated and logged; one league's failure never
blocks the others. The top-5 morning report is **not** modified by this
phase. Runner requirements (frozen at upgrade): FotMob-only
fixtures/results; incremental matchDetails for newly played matches
via the resumable puller; per-league CSV append + engine update;
predictions to `league/<L>/predictions/` with halves via the league's
frozen constants; settlement of yesterday's predictions into the
league's grading ledger; per-league failure isolation + a run log.

## Resume notes (for a fresh coordinator — read this first)

State as of the heartbeat above. Repo: ~/workspace/footballprediction,
coordinator branch: local/fotmob-source (ledger commits land here).

**POST-REBUILD STATE (2026-11-10 17:51 WIB — read this first, the
per-league notes below are stale Wave-2-era text):** history rebuilt
(HEAD c375260a; SHAs diverge from originals, content verified; map in
~/workspace/recovery-backup-2026-11-10/ref_updates.json). 130 leagues
complete, 120 passing markets, runner 42/94. MILESTONE #5 recorded
2026-11-10 18:29 (leagues 101–125: 0 PASS / 25 FAIL / 100 NOT
BUILDABLE). Merges done post-rebuild:
GT #115, RO #116, CR #117, AU #118, DZ #119, CZ SOT fix, LU #120,
SK-2Liga #121, IR-PersianGulf #122, KR-KLeague3 #123, TZ-PremierLeague
#124, NI-Premiership #125, CY-2Division #126, UY-SegundaDivision #127,
WAL-CymruPremier #128, HN-LigaNacional #129, TN-LigueI #130.
In flight:
CY-1Division join (branch build/runner-cy @ wt-runner44) MERGED
2026-11-10 19:30 (3a1eb828; runner 43/96). SE-Superettan cards join
(branch build/runner-se-superettan @ wt-runner46) launched 19:30.
Join queue (PASS order, 16): NO-OBOS JOINED 2026-11-10 20:50 (6d0d3c51;
runner 44/97) → SE-Superettan JOINED 2026-11-10 21:13 (68cbdcf4;
runner 45/98) → US-USLLeagueOne JOINED 2026-11-11 01:48 (dd2765c7;
runner 48/102) → FI-Veikkausliiga
JOINED 2026-11-10 22:55 (61c606de; runner 46/99) → HU-NBI JOINED
2026-11-11 00:50 (2879ae4f; runner 47/100) → SK-1Liga JOINED
2026-11-11 02:30 (5ff23d9c; runner 49/103) → AE-ProLeague JOINED
2026-11-11 03:16 (ef2f7f2f; runner 50/104) → HR-HNL JOINED
2026-11-11 04:17 (33e43b9e; runner 51/105) → DK-1Division JOINED
2026-11-11 06:19 (490c6fcd; runner 52/109) → AU-ALeagueWomen JOINED
2026-11-11 06:20 (9e7230fd; runner 53/111) → IS-BestaDeildin JOINED
2026-11-11 07:51 (1d9048fd; runner 54/114) → SA-FirstDivision JOINED
2026-11-11 09:49 (ac93e742; runner 55/115) → LV-Virsliga SOT
2026-11-11 11:24 (8cec8d55; runner 56/116) → AR-PrimeraBNacional
cards X8 JOINED 2026-11-11 13:47 (e8f7c2d9; runner 57/117) →
KZ-PremierLeague goals GZ JOINED 2026-11-11 15:26 (efb502eb;
runner 58/118) → BA-PremierLeague goals GZ (join builder
launching 2026-11-11 15:26, branch build/runner-ba). Build queue head (recomputed 2026-11-10
~18:10, plain-n order): NI-Premiership (129, 1,242) launched as the LU
refill, UY-SegundaDivision (9122, 1,219) launched as the SK-2Liga
refill, CY-2Division (9100, 1,210), HN-LigaNacional (337, 1,132),
WAL-CymruPremier (116, 1,103) launched as the IR/KR3/TZ refills,
TN-LigueI (544, 1,060) launched as the NI refill, LT-Toplyga (228,
1,044) launched as the CY-2 refill, KZ-PremierLeague (225, 1,124)
launched as the UY-Segunda refill, BA-PremierLeague (267, 1,036)
launched as the WAL refill, IE-FirstDivision (218, 1,028) launched
as the HN refill, ME-1CFL (232, 972) launched as the LT refill
2026-11-10 18:57, VN-VLeague (9088, 969) launched as the KZ refill
2026-11-10 19:02, AL-KategoriaSuperiore (260, 969) launched as the
BA refill 2026-11-10 19:05, SCO-LeagueOne (124, 969) launched as
the IE refill 2026-11-10 19:07, SLO-PrvaLiga (173, 956) launched as
the MK refill 2026-11-10 19:11, AZ-PremierLeague (262, 914)
launched as the VN refill 2026-11-10 19:16, AM-PremierLeague
(118, 881) launched as the AL refill 2026-11-10 19:17. IS-1Deild
(216, 812) launched as the ME refill 2026-11-10 19:23 — the LAST
league on the 18:42 recompute; tail RECOMPUTED 19:24 (9 remain,
head Panama LPF 9039). PA-LPF (9039, 811) launched as the AM
refill 2026-11-10 19:32; queue head now Faroe Islands Premier
League (250, 810). MY-LigaSuper (8985, 793) launched as the SLO
refill 2026-11-10 19:34; queue head now Iceland 2. Deild (10226,
792). IS-2Deild (10226, 792) launched as the SCO refill
2026-11-10 19:35; queue head now Bangladesh Football League
(10443, 394). BD-FootballLeague (10443, 394) launched as the AZ
refill 2026-11-10 19:37; queue head now Hungary NB II (9117, 344).
HU-NBII (9117, 344) launching as the BD refill 2026-11-10 19:50;
queue head now New Zealand Championship (8870, 229). External
batch 16–19 (SG/MD/KW/IN) folded as #143–146 at 19:46; BD merged
as #147 at 19:50 — counter 147, passing markets 122, milestone
150 is 3 leagues away. IS-1Deild merged as #148 at 19:54
(8d6a307e); NZ-Championship (8870, 229) launching as the IS-1Deild
refill 2026-11-10 19:54; queue head now Uzbekistan Superliga
(540, 215); milestone 150 is 2 leagues away. MY-LigaSuper merged
as #149 at 19:57 (e82c6932); UZ-Superliga (540, 215) launching as
the MY refill 2026-11-10 19:57; queue head now Faroe Islands
Løgmanssteypið (9523, 6 — cup, assess buildability); milestone
150 is 1 league away. IS-2Deild merged as #150 at 20:01
(0cbdad69) — MILESTONE #6 recorded (leagues 126–150: 2 PASS
provisional / 24 FAIL / 99 NOT BUILDABLE; passing markets 122);
milestones reported = 6, next at 175. Faroe Islands
Løgmanssteypið (9523, 6) launching as the IS-2Deild refill
2026-11-10 20:01 — the LAST league in the local queue (0 remain
after Faroe); next work after Faroe is the external tail batch
(if Jarvis announces one) and the final Codex-sol audit pass.
**CORRECTION 2026-11-10 20:08: Faroe Islands Premier League (250,
810) was found UNBUILT — queue head at 19:32, skipped at the
19:34 refill with no reason recorded. Launching NOW as the true
last local league (branch build/fo-premier-league); the local
queue is exhausted only after it.**
Queue RECOMPUTED 2026-11-10
18:42 (plain-n order, 127 consumed config ids + external/in-flight
excluded): 21 leagues remain — head Kazakhstan Premier League (225,
1,124) → Bosnia Premier League (267, 1,036) → Ireland First Division
(218, 1,028) → North Macedonia Prva Liga (249, 1,022) → Montenegro
1. CFL (232, 972) → Vietnam V-League (9088, 969) → Albania Kategoria
Superiore (260, 969) → Scotland League One (124, 969) → Slovenia
Prva Liga (173, 956) → Azerbaijan Premier League (262, 914) →
Armenia Premier League (118, 881) → Iceland 1. Deild (216, 812) →
**RECOMPUTED 2026-11-10 19:24 (plain-n order, 138 consumed config
ids + external/in-flight/top-5-production excluded): 9 leagues
remain** — head Panama LPF (9039, 811) → Faroe Islands Premier
League (250, 810) → Malaysia Liga Super (8985, 793) → Iceland
2. Deild (10226, 792) → Bangladesh Football League (10443, 394) →
Hungary NB II (9117, 344) → New Zealand Championship (8870, 229) →
Uzbekistan Superliga (540, 215) → Faroe Islands Løgmanssteypið
(9523, 6 — cup, 6 matches only; assess buildability, likely
not-buildable). Note: top-5 production ids (87/55/47/53/54) are
excluded from the conveyor queue by design; 3 consumed config ids
(8974, 9136, 223) have no index rows.
EXTERNAL
SKIP-LOCAL: SG (461), MD (231), IN (8982), KW (529) — Muse-2 tail
assignments 16–19. Next actions: launch NO-OBOS join + refill build
slots from the queue head; next milestone 150.
Builders work in their own worktrees/branches and NEVER edit this file;
the coordinator merges their branches locally (no push, ever) and
records verdicts here. Codex: implementation = `~/.local/bin/codex
exec -m gpt-5.6-luna` with stdin closed (`< /dev/null`); the sol model
is reserved for the final audit pass only.

Per-league / per-candidate next actions:

- G-J1: DONE, merged (562baeb), verdict FAIL (virgin OU calibration;
  see table). Worktree removable at cleanup.
- Wave 2 builders: C-J1 `build/c-j1` @ wt-c-j1 (running),
  K-J1 DONE merged 4b840d1 (FAIL), K-J2 DONE merged d1104ad (FAIL),
  S-J1 `build/s-j1` @ wt-s-j1 (running), T-J1 `build/t-j1` @ wt-t-j1
  (running, launched 15:05). Next per builder: report → verify →
  merge → record.
  Wave-2 preregs carry the Wave-1 lesson as a frozen rule: an arm
  that fails its dev gate does NOT read the virgin window.
- G-J2: DONE, merged (b8ec72c), verdict FAIL at dev gate; virgin 2025
  unburned by design. Diagnosis (for a possible future prereg, NOT
  authorised now): unmodified DC gives extreme lambdas to 1–2-match
  teams in season openers (OU leg dies there); a shrinkage arm would
  need a NEW prereg. Worktree removable at cleanup.
- G-J3: DONE, merged (16b40ab), verdict FAIL (see table). Worktree
  `~/workspace/wt-g-j3` can be removed at cleanup; branch kept as record.
- Wave 2 (launch after Wave 1 merges): C-J1 (branch build/c-j1),
  K-J1 (build/k-j1), K-J2 (build/k-j2), S-J1 (build/s-j1),
  T-J1 (build/t-j1) — briefs follow the Wave-1 pattern; K candidates
  include the pre-match referee-availability operational check;
  T-J1 prereg must state it runs ahead of the top-5 verdict by user
  order with 3 frozen arms (v1 / v2 level layer / E9 trailing-r).
- Conveyor Batch 1 (launch after Wave 2): the 8 leagues listed in the
  conveyor section; each gets its own builder + branch
  `build/<slug>` running steps 1–6 + builds.
- Phase Final: TRIGGERED 2026-11-09 (S-J1 PASS). Daily-runner
  builder running on `build/daily-runner` @ wt-runner. Next: verify
  its report → merge → create the runner's daily cron (coordinator,
  cron tools; suggested slot ±07:15 WIB, MUST stay separate from the
  08:52 top-5 report) → mark J1 "joined" in the Phase Final table.
  Later PASSes (any league) join by adding their passing markets to
  the runner config — no new runner build needed.
- Final pass (after all builds): ONE Codex sol audit session →
  league/AUDIT.md; fix only clear bugs with re-tests.

If a builder is found dead: relaunch a replacement builder on the
SAME branch/worktree from its last commit (prereg/code commits are
checkpoints); if it cannot be relaunched, record the blocker in the
event log with the reason.

## J.League (design frozen; build mandated 2026-11-09)

| League | Steps 1–6 | Candidate | Market | Status | Verdict |
|---|---|---|---|---|---|
| J1 | done (in J1/analysis) | G-J1 | goals | DONE — merged 562baeb | **FAIL** — Gate Zero passes dev + virgin LL but fails virgin OU2.5 calibration (−4,56pp vs 1 SE 3,56pp; transitional 2026 ran hot, over 47,0% vs ~42% predicted); X2/X3 fail dev gate + sign check + OU calibration. Nothing ships. |
| J2 | done (via J1 analysis) | G-J2 | goals | DONE — merged b8ec72c | **FAIL** at dev gate: 1X2 LL/RPS legs pass, OU2.5 LL loses (0,746 vs base rate 0,690) for both arms. Virgin 2025 **deliberately NOT read** — remains virgin for one future read under a new prereg. Nothing ships. |
| J3 | done (via J1 analysis) | G-J3 | goals | DONE — merged 16b40ab | **FAIL** — both arms dead at dev gate (OU LL loses to base rate); virgin calibration FAIL (home-win −7,7pp, J3 2025 home rate jumped to 47,0%). Nothing ships. |
| J1 | done | C-J1 | corners | DONE — merged 0ba8ee8 | **PASS (calibration PROVISIONAL) — Gate Zero SHIPS.** Dev LL@9.5 GZ 0,6935 / X7 0,6915, both beat both baselines; virgin LL 0,6901 (best baseline 0,7050), calibration +2,59pp within 1 SE (3,53pp) = PROVISIONAL PASS. Note: the X7 box-touch multiplier was never selected (β_bt = 0 in every fit) — the F9 trait is real but worth zero inside this multiplier structure; virgin predictions of both arms identical, tie rule ships Gate Zero. **J1's second passing market → joins the daily runner.** |
| J1 | done | K-J1 | cards | DONE — merged 4b840d1 | **FAIL** — both arms pass dev (X8 helps: 0,6785 vs GZ 0,6872) and virgin calibration (PROVISIONAL PASS), but virgin LL leg fails vs naive trailing-10 (0,6807 vs GZ 0,6829 / X8 0,6831). Referee coverage: 51,6% overall but **0,5% in the virgin season** — X8 effectively untested there. Nothing ships. |
| J2 | done | K-J2 | cards | DONE — merged d1104ad | **FAIL** at dev gate: Gate Zero beats base rate (0,6564 vs 0,6668) but loses to naive trailing-10 (0,6554) by +0,0010. **Referee coverage in J2 = 0/2.318** — X8 inactive by construction (FotMob simply carries no referee for J2; same extractor finds referees in J1). Virgin 2025 NOT read. Nothing ships. |
| J1 | done | S-J1 | SOT | DONE — merged cc5f927 | **PASS — Gate Zero (unmodified v5 pattern) SHIPS.** Dev LL@8.5 0,6658 beats both baselines; virgin LL 0,6815 best of all arms + baselines; virgin calibration −0,30pp clean PASS. Variants RS/X4/X6 were slightly better on dev and reversed on the virgin — Gate Zero ships alone. **→ Triggers Phase Final: J1 joins the daily runner with SOT.** |
| J1 | done | T-J1 | total shots | DONE — merged ffec3aa | **PASS (calibration PROVISIONAL) — arm A (v1 pattern) SHIPS.** All 3 arms passed dev; virgin: A LL@24.5 0,6916, calibration −2,30pp within 1 SE → PROVISIONAL PASS. B (v2 level layer) failed legs (i)+(iii); C (E9 trailing-r) had the best virgin LL (0,6912) but failed the frozen per-season sign check (1/3) — applied as written. Built ahead of the top-5 prospective verdict by user order; that trial is untouched. **J1's third passing market → joins the daily runner.** |

## Conveyor — world warehouse leagues (6-step process, then build)

Batch 1 — SELECTED 2026-11-09 (richest by index depth flags, production
top-5 excluded; stats% / shotmap% / n from the world index):

| League | FotMob id | n | stats | shotmap | Status |
|---|---|---|---|---|---|
| Austria Bundesliga | 38 | 1,047 | 100% | 100% | **DONE — 0 PASS / 5 FAIL** (merged f59df10). G-AT + K-AT FAIL at dev gate (virgins unread); S-AT/C-AT/T-AT FAIL virgin calibration — 2025/2026 ran cold on every count stat (calib +5,3…+7,7pp). X7 beta=0 replicated; K-AT's X8 dev gain (+0,0093 LL) moot under the frozen rule. **League complete.** |
| Denmark Superligaen | 46 | 1,049 | 100% | 100% | **DONE — 2 PASS provisional / 3 FAIL** (merged 709d0cf). C-DK corners Gate Zero PASS; **T-DK total shots arm C (E9 trailing-r) PASS** — first variant-arm win of the program (by 0,00013 LL). G-DK/S-DK FAIL dev (virgins unread); K-DK FAIL virgin leg (i) despite full referee coverage. SHRINK arm degenerate under season-blocked fitting (recorded). **League complete.** Joins runner pending extension (below). |
| Netherlands Eredivisie | 57 | 1,659 | 100% | 100% | **DONE — 2 PASS provisional / 3 FAIL** (merged 75a085e). S-NL SOT Gate Zero PASS; T-NL total shots arm A PASS. G-NL FAIL dev (OU leg); C-NL FAIL dev — prereg-text vs port baseline discrepancy judged as frozen (fix = new prereg); K-NL FAIL dev by 0,00004 LL on the X8 arm. G/C/K virgin windows BURNED by labelled fallback reads (recorded in verdicts); 2026/2027 untouched. **League complete.** Joins runner after the DK extension (same world path). |
| Portugal Liga Portugal | 61 | 1,628 | 100% | 100% | **COMPLETE 2026-11-09: 0 PASS / 5 FAIL** (merged 685451f). G-PT FAIL virgin OU kalibrasi −5,58pp vs 1 SE 5,01pp (kaki yang sama dgn G-J1; virgin lari panas-tandang). S-PT FAIL leg (i) virgin sebesar 0,0019 LL (naive 0,6734 vs GZ 0,6753; kalibrasi bersih −0,98pp). C-PT FAIL di dev (virgin tak dibaca; baseline terkalibrasi baik, dispersi referensi meratakan probabilitas). K-PT FAIL: X8 satu-satunya arm lolos dev + LL virgin terbaik, mati di kalibrasi +9,57pp (level kartu virgin jatuh). T-PT FAIL legs (i)+(ii) (virgin shot-hot). Tanpa pasar lolos → tidak join runner. **Batch 1 TUNTAS 8/8** |
| USA MLS | 130 | 3,054 | 100% | 100% | **DONE — 3 PASS / 2 FAIL** (merged e026d3a). S-US GZ PASS provisional; C-US GZ PASS provisional; **T-US arm C PASS CLEAN** (second arm-C win; A also passed all legs, C ships on lower LL). G-US FAIL dev — climatology beat DC even on 1X2 (1,0579 vs 1,0671), a program first; K-US FAIL dev (GZ leg; X8 moot). G/K virgins unread. Virgin n=540, the program's largest. **League complete.** Joins runner queued behind AU join (below). |
| Australia A-League | 113 | 857 | 100% | 99.9% | **DONE — 4 PASS / 1 FAIL** (merged f838d62). S-AU RS ships (provisional); C-AU Gate Zero PASS CLEAN (calibration −0,01pp, tightest in program); K-AU Gate Zero PASS (provisional; single-arm by design — X8 referee trait is NOISE here, r=0,06); T-AU arm A PASS CLEAN. G-AU FAIL dev (OU leg). Smallest pools (dev 508 / virgin 163) — SEs ~3,8–4,0pp noted. **League complete.** Joins runner pending cards adapter + RS prior (below). |
| Argentina Liga Profesional | 112 | 2,464 | 100% | 72.6% | **DONE — 1 PASS provisional / 4 FAIL** (merged 1f29a1e). C-AR corners X7-as-fitted PASS (its box-touch beta is 0 as everywhere; the win came from GZ's big-chance beta hurting on the virgin — recorded honestly). G-AR FAIL dev; S-AR/K-AR FAIL virgin calibration (virgin ran hot on attack, cold on cards); T-AR FAIL — naive beat every arm (virgin shots 26,75 vs dev 24,15). Cards feed artefact caught pre-fitting (stats key undercounts; event-unified target). Virgin = complete 2026-Clausura group (n=240). **League complete.** Joins runner queued (below). |
| Brazil Série A | 268 | 2,239 | 100% | 68.8% | **DONE — 2 PASS / 3 FAIL** (merged c77116f). S-BR RS PASS CLEAN; **T-BR arm C PASS provisional** (third arm-C win, by 0,00007 LL — DK's outcome replicated). G-BR FAIL dev (OU leg); C-BR FAIL virgin leg (i) to the plain base rate; K-BR FAIL dev (base-rate leg; the mechanical X8 virgin read recorded transparently would also fail). Feed break found + unified-cards target fixed (stats undercount 2021–22). 2026 confirmatory unread. **League complete.** Joins runner queued (below). |

Each league: steps 1–6, J1 feature template (X1–X9 analogues) adopted
only where data exists AND reliability passes in that league; markets
per its feasibility matrix; prereg + gate per candidate.

Remaining queue (ordered by richness, after Batch 1): Scotland
Premiership, Norway Eliteserien, Switzerland Super League, Sweden
Allsvenskan, Belgium First Division A, England Championship, Germany
2. Bundesliga, Mexico Liga MX, India ISL, South Korea K League 1,
Turkiye Süper Lig, Saudi Pro League, then the rest of the 158 selected
leagues in index-richness order (full ordering computed from the index
when Batch 1 completes). The conveyor continues in later runs.

Batch 2 — LAUNCHED 2026-11-09 ~16:44 WIB under the user's speed-up
instruction (waves widened to ≤6 concurrent builders; joins
parallelised):

| League | FotMob id | n | stats | shotmap | Status |
|---|---|---|---|---|---|
| Scotland Premiership | 64 | 1,215 | 100% | 100% | **DONE — 4 PASS / 1 FAIL** (merged 477dfe7). **G-SCO goals PROVISIONAL PASS — the program's FIRST goals pass** (Gate Zero; OU calibration within 1 SE). S-SCO GZ provisional; C-SCO GZ provisional (X7 beta 0, tie rule); **T-SCO arm B (v2 level layer) PASS CLEAN — first arm-B win anywhere** (calibration −0,03pp). K-SCO FAIL dev by 0,0002 LL (virgin unread). X8 referee noise here too (r=0,158). **League complete.** Joins runner — needs the first GOALS adapter + arm-B support (below). |
| Norway Eliteserien | 59 | 1,407 | 100% | 100% | **DONE — 3 PASS / 2 FAIL** (merged 1665058). **K-NO cards Gate Zero PASS CLEAN** (calibration −0,84pp; event-unified target after a documented pre-virgin feed amendment — stats feed undercounts yellows in every season, third league with the artefact). C-NO GZ provisional; T-NO arm A provisional. G-NO FAIL dev (virgin unread); S-NO FAIL virgin calibration (−6,1pp). **League complete.** Join commissioned (below). |
| Switzerland Super League | 69 | 1,122 | 100% | 99.9% | **DONE — 3 PASS provisional / 2 FAIL** (merged 538150a). S-CH RS, C-CH GZ (tie rule), T-CH arm A. G-CH FAIL dev (virgin unread); K-CH FAIL virgin legs (i)+(ii). Program's highest-scoring league (goals 3,11); virgin ran hot → all three passes provisional. Format break (10→12 teams + split, 2023/24) handled. **League complete.** Join commissioned (below). |
| Sweden Allsvenskan | 67 | 1,424 | 100% | 99.9% | **DONE — 3 PASS / 2 FAIL** (merged 149a9d3). T-SE arm A PASS CLEAN; S-SE arm X4 PASS provisional; C-SE arm X7 PASS provisional (beta_bt 0 again — ships in its no-multiplier form per the gate). G-SE FAIL dev (OU leg by 0,0007; virgin unread); K-SE FAIL dev (GZ leg; X8 moot). Virgin = complete 2025 (n=240); 2026 confirmatory unread. **League complete.** Join commissioned (below). |
| Belgium First Division A | 40 | 1,698 | 99.9% | 99.9% | **COMPLETE 2026-11-09: 2 PASS / 3 FAIL** (merged 0f429a5). All phases included, phase-flagged (frozen). S-BE **PASS provisional — RS ships** (cal +2,32pp; X4 gagal leg (i) meski dev terbaik). K-BE **PASS CLEAN — Gate Zero** (+0,19pp; X8 menang dev, kalah leg (i) virgin). G-BE FAIL — kandidat gol pertama yang lolos SEMUA arm di dev (GZ 1,0024 vs klim 1,0765), lalu OU virgin +4,95pp (musim virgin mendingin 2,67). C-BE FAIL virgin kalibrasi −4,34pp (β X7 = 0 lagi). T-BE FAIL (A −4,93 / B −4,03pp; B meleset pita provisional 0,32pp). Integritas: 2 laga score-only (feed stub/null) dinull-kan pra-fit; cards stats-vs-events shape DK (kept). Virgin 2025/26 n=313; 2026/27 reserved |
| England Championship | 48 | 2,963 | 100% | 99.9% | **COMPLETE 2026-11-09: 2 PASS provisional / 3 FAIL** (merged 2538080). S-ENGCH **RS ships** (virgin LL 0,6798, kal −2,64pp). C-ENGCH **Gate Zero ships** (X7 seri, β=0; kal +1,11pp). G gagal gerbang OU di dev untuk SEMUA arm (X2 mover benar-benar bekerja di 1X2, −0,0074 LL — kaki total yang membunuh). K gagal dev (trait kartu tim noise murni r=−0,01, terlemah program). T gagal virgin legs (i)+(ii) (musim virgin panas: 25,22 tembakan/laga). Virgin n=555; G/K sengaja TIDAK dibaca. Proses: builder asli menyelesaikan virgin+verdict bersamaan dengan builder lanjutan, yang beralih ke verifikasi independen (recompute eksak) dan TIDAK membaca virgin dua kali — benar. Dua deviasi netral terungkap (S-X4 tak dibaca krn filter sign-leg dev; assert-n T dikoreksi pra-baca) → daftar audit final |
| Germany 2. Bundesliga | 146 | 1,629 | 100% | 100% | **COMPLETE 2026-11-09: 2 PASS provisional / 3 FAIL** (merged eaed158). S-DE2 **RS ships** (virgin LL 0,6622, kal +2,61pp). K-DE2 **X8 ships — arm wasit pertama yang lolos di program** (gain dev −0,0070 bertahan di virgin −0,0073; kal +1,08pp). G gagal kaki OU di dev (virgin tak dibaca). C gagal kalibrasi virgin +4,56pp (β X7 = 0 lagi). T: arm C lolos dev sebesar 0,00014 lalu kalah LL virgin dari base rate. Virgin = 2025/2026 LENGKAP (n=306; koreksi atas brief — 2026/27 parsial dicadangkan). Cards: shape BE/DK, stats kept tanpa amendemen. Sisa refactor X2 tak-tercommit di worktree DIREVERT koordinator pra-merge (bukan bagian catatan gerbang; G gugur di dev pada kedua versi) |
| Mexico Liga MX | 230 | 1,829 | 100% | 100% | **COMPLETE 2026-11-09: 1 PASS provisional / 4 FAIL** (merged 6197d8d) — **liga ke-25 program (MILESTONE)**. C-MX **Gate Zero ships** (seri X7, β=0; kal +4,17pp vs SE 4,02). G gagal kaki OU di dev; S kalah leg (i) virgin dari naive-nya sendiri (0,6721); K gagal dev (X8 lebih baik dari GZ tapi tak lewati base rate); T gagal kalibrasi virgin (level tembakan bergeser +1,3/laga). Target kartu event-derived (stats undercount di 9 turnamen dev). Join runner: QUEUED (beku) |
| South Korea K League 1 | 9080 | 1,350 | 95.5% | 82.1% | **COMPLETE 2026-11-09: 1 PASS provisional / 4 FAIL** (merged 528fb30). K-KR **Gate Zero ships** (virgin LL 0,6765, kal −1,74pp; target event-unified → join butuh cards_actual [yellow_home, yellow_away] gaya NO). G gagal kaki OU di dev; S gagal dev (semua arm); C gagal kalibrasi virgin −5,52pp (β X7 = 0); T kalah leg (i) dari naive + kalibrasi (tembakan 2025 melonjak 26,07). Virgin = 2025 lengkap n=228; 2026 reserved. Cacat tercatat utk audit: arm X2 gol konstruksinya tidak valid (tak memengaruhi verdict — GZ gugur duluan); kebocoran konstanta babak gaya AR tertangkap pra-ship (0,370 SE di harness kartu, 0,543 di total_shots — dikoreksi, virgin tak dibaca ulang). Join runner: QUEUED (beku oleh stop order) |
| Turkiye Süper Lig | 71 | 1,849 | 98.4% | 78.5% | **COMPLETE 2026-11-09: 4 PASS / 1 FAIL** (merged 90b8e05). G-TR **X3 PASS provisional — kandidat gol kedua yang lolos program** (set-play arm; OU bersih −0,86pp). S-TR GZ prov, C-TR GZ prov (seri, β=0), T-TR **arm A PASS CLEAN**. K-TR FAIL + **INSIDEN INTEGRITAS (terungkap sendiri)**: builder salah membaca aturan beku dan membaca virgin X8 (LL 0,6740 — seandainya provisional) padahal GZ gugur di dev → kandidat gugur; artefak shipping dihapus, bacaan hangus tercatat transparan di verdict, virgin K-TR terbakar. Jalur sah X8 = prereg baru + virgin segar (2026/2027) — keputusan koordinator/user, bukan sekarang. 31 baris forfeit gempa dikeluarkan by flag. Join runner: QUEUED (beku) |
| India ISL | 9478 | 653 | 100% | 100% | **COMPLETE 2026-11-09: 2 PASS provisional / 3 FAIL** (merged fe621e5). S-IN **Gate Zero ships** (virgin LL 0,6721 ≤ naive 0,6729; RS LL terbaik tapi sign dev 1/3). C-IN **Gate Zero ships** (0,6835; β X7 = 0 lagi). G gagal kaki OU di dev; K gagal dev ke naive (target event-unified per preseden NO); T gagal virgin legs (i)+(ii). Virgin n=91 (SE ~5pp). Codex panic lagi → port langsung terverifikasi |
| Germany 3. Liga | 208 | 1,992 | 99.9% | 0% | QUEUED — next free build slot (tanpa shotmap: fitur xG gugur by design, target stats-feed) |
| Saudi Pro League | 536 | 1,502 | 100% | 70.6% | **COMPLETE 2026-11-09: 3 PASS provisional / 2 FAIL** (merged 18739ae). S-SA **RS ships**, C-SA **Gate Zero ships** (seri persis, β X7 = 0 di virgin), T-SA **arm A ships**. G gagal kaki OU di dev (virgin tak dibaca); K gagal dev ke base rate (target event-unified; trait kartu lemah r=0,264). Regime break 2023/2024 terkonfirmasi data → dev dibatasi musim pasca-break (dibekukan pra-fit). Virgin 2025/2026 lengkap n=306; 2026/27 reserved. Join runner: QUEUED (beku) |

## Event log (append-only)

- 2026-11-09 14:39 — Program started. Wave 0 (scaffold) begun by coordinator.
- 2026-11-09 14:40 — Analysis docs git-mv'd from experiments/jleague_eda/
  to league/J1/analysis/ (J2/J3 analysis = pointer READMEs; no duplication).
- 2026-11-09 14:40 — Data builder committed (league/build_league_data.py +
  jleague_lib.py); CSVs regenerated into league/<L>/data/ — J1 2,091 /
  J2 2,318 / J3 1,819 matches, total 6,228 == warehouse; byte-identical to
  the exploration CSVs.
- 2026-11-09 14:41 — Step-4 visualization backfilled for J1:
  league/J1/analysis/charts/ (levels_by_season, trait_reliability,
  tier_gap, halves_constants, referee_and_territory) from frozen EDA
  numbers via league/J1/analysis/make_charts.py.
- 2026-11-09 14:41 — MODEL_DESIGN amended: per-league-engines decision
  (user 14:33) replaces forbidden item 7; build mandate recorded (§7b.5–6);
  T-J1 deferral overridden by user (§6).
- 2026-11-09 14:42 — Continuity requirement (user 14:41) adopted as a hard
  program rule: this ledger is updated at every transition, failures
  included; dead builders are relaunched from their last commit or the
  blocker is recorded here with its reason.
- 2026-11-09 14:43 — Wave 0 committed (d1011e1). Wave 1 LAUNCHED: three
  builders in parallel, each own worktree+branch, Codex luna implementing,
  builder verifies independently — G-J1 (build/g-j1), G-J2 (build/g-j2),
  G-J3 (build/g-j3). Each must commit its prereg before any fitting.
- 2026-11-09 14:47 — Conveyor Batch 1 selected from the world index by
  depth richness (production top-5 excluded): Austria Bundesliga,
  Denmark Superligaen, Netherlands Eredivisie, Portugal Liga Portugal,
  USA MLS, Australia A-League, Argentina Liga Profesional, Brazil
  Série A. Remaining queue ordered in the conveyor section above.
- 2026-11-09 14:45 — Milestone reporting + auto-resume adopted (user
  14:43): counters & heartbeat section and resume notes added to this
  ledger; milestone = every 25 fully completed leagues, reported once
  per multiple.
- 2026-11-09 19:31 — **WIND-DOWN: KR-KLeague1 COMPLETE: 1 PASS
  provisional / 4 FAIL** (merged 528fb30) — counter 20 leagues,
  39 passing markets. KR's runner join is NOT launched (stop
  order) — it joins the frozen queue behind the ISL join.
  Still in flight: MX, TR, SA builds + ENG-Ch, DE-2 joins.
  (Also folded in: the NO join builder's late-arriving full
  report confirms its merged proof and pins the parallel-run
  OOM peak to AR's rebuild, ~2,1–2,8 GB RSS per runner —
  proof archive ~/workspace/no2proof/.)
- 2026-11-10 01:19 — **⚠ STALL + RECOVERY (watchdog)**: no ledger
  commit since 00:15 WIB, heartbeat 00:22 WIB (57 min stale);
  coordinator agent still listed running but quiet ~60 min. Full
  sweep before any relaunch: all 6 in-flight joins ALIVE in proof
  runs (run_daily.py, CPU-active, run_log.jsonl entries to 01:16
  WIB) — FR-L2 run2 (PID 13815, wt-runner26), USL run2 (12225,
  wt-runner27), PL run2 (11160, wt-runner28), GR run2 (15956,
  wt-runner29), EG run1 (15386, wt-runner30), NL-Eerste run1
  (10381, wt-runner31). No QUOTA-WAIT, no PAUSED-BY-USER. NO
  relaunch, NO duplicate builders (6 concurrent full-runner proofs
  already load the VM; ledger notes OOM risk). Next: merge each join
  as its builder reports; no new conveyor builds until the joins
  clear. Heartbeat refreshed; counter header fixed 41→42.
- 2026-11-10 15:42 — **⛔ OBJECT-STORE DELETION (coordinator
  error) — git history after the last repack DESTROYED, GT
  merge blocked, full rebuild required.** While cleaning
  garbage `tmp_obj_*` files from `.git/objects/`, the
  coordinator ran `find .git/objects/[0-9a-f][0-9a-f] -type
  f ! -regex '.*/[0-9a-f]\{38\}' -delete` — the regex did
  NOT match valid 38-hex object filenames as intended
  (GNU find `-regex` + the interval quantifier did not
  behave as assumed; the pattern matched nothing, so the
  negation selected EVERYTHING). **3,763 files deleted:
  ALL loose objects (count 0 afterwards)** — every commit,
  tree and blob created since the last repack (packs:
  22,418 objects intact). `git log`/`merge` fail with
  `fatal: bad object HEAD`. **NO file content was lost:**
  the main working tree + every worktree hold all files;
  the index still holds the complete final tree
  (worktree-vs-index diff = only the 111 pre-existing
  xg_raw runtime-dirt files; index-vs-HEAD = 1,131 files).
  Boundary: newest surviving commit is **3531e0f** (MX-
  ExpansionMX merge, league #80); the last repack ran
  between the ZA join (91f3528, survives) and the CZ join
  (420a8a5a, lost). **Lost: 70 HEAD movements after
  3531e0f (69 commits + the 15:38 reset)** (leagues #81–#114 incl. FR/BY folds, IR/SV
  merges, CZ/BG/CL/CN joins, all ledger commits since) **+
  33 of 156 build/* branch tips** (list in the recovery
  brief). Reflogs survive with exact order, committer and
  timestamps for every lost commit (`.git/logs/HEAD`,
  `.git/logs/refs/heads/*`). HEAD was reset to 3531e0f at
  15:38:37 WIB **by Jarvis via `git update-ref`** (he
  diagnosed the bad HEAD before this entry landed); he
  then ran `git read-tree 3531e0f`, which REPLACED the
  index with #80's tree — so the "final tree" index
  mentioned below is NOT the original f8e2228a index: Jarvis
  rebuilt it by re-adding from disk (all league dirs
  #81–#114 + PROGRAM_STATUS.md + EXTERNAL_MERGES.md +
  runner files + fotmob_world_index.csv; xg_raw/ and
  runtime dirt deliberately excluded). The staged index
  now holds that set; the recovery agent must verify it
  and reset it as needed. **Jarvis also found
  `league/SV-PrimeraDivision` missing its `engine/` dir in
  the main checkout and restored it from
  wt-sv-primera-division (`engine/goals/*.py` + results
  files) and staged it** — the EPERM-era merge checkout
  never landed it; the recovery agent must make sure the
  rebuilt SV merge tree includes it. Jarvis committed
  NOTHING (freeze respected). Refs/reflog snapshot saved
  at `/tmp/git-recovery-20261110/` (packed-refs.bak,
  reflog-fotmob-source.bak, refs-before.txt,
  recovery-dirs.txt) — the recovery agent must copy it
  into its own backup dir first thing. **FREEZE:** all 6 in-flight
  builders/joins told 15:42 to work on files only, NO git
  commands, until the rebuild completes. **Recovery:**
  a dedicated recovery agent replays the 70 reflog steps
  in order from 3531e0f (branch tips rebuilt from worktree
  files + branch reflogs; merges replayed with original
  metadata from reflog + recorded messages; aim: exact
  SHA reproduction, verify each rebuilt SHA against the
  reflog, report + document every divergence). GT merge
  (#115) happens only after the rebuild, from the verified
  branch. Standing rule added: NEVER run a bulk delete
  inside `.git/` again — garbage tmp files are removed
  ONLY by exact-name match (`tmp_obj_*`) or `git prune`.
- 2026-11-10 15:42 — **Numbering correction: IR = #113,
  SV = #114 (NOT #111/#112).** Jarvis folded FR-Ligue3
  (#111) and BY-PremierLeague (#112) at 15:28 WIB while
  the coordinator was merging IR/SV; the 15:30 ledger
  numbered IR/SV #111/#112 before the folds reached the
  coordinator. The per-league list + counter above are
  corrected to 114. GT-LigaNacional will be #115 on merge
  (after the history rebuild).
- 2026-11-10 17:40 — **HISTORY REBUILD COMPLETE (recovery agent
  44fe6b48; report in ~/workspace/recovery-backup-2026-11-10/).**
  Rebuilt HEAD c375260a (expected original f8e2228a). 69 main-chain
  commits replayed in reflog order + 33 branch tips rebuilt from
  worktrees/reflogs (plumbing only, no push, no working-tree
  touches). CONTENT VERIFIED by the coordinator: git log shows the
  69 commits in order; GT pooled recomputes exactly (1.0022/0.2001/
  0.7098); final tree is a superset of Jarvis's staged index (+48
  force-added result CSVs the disk re-add missed); fresh fsck shows
  ONLY the known categories — 66,205 invalid reflog entries (the
  reflogs still reference the original lost SHAs; kept deliberately
  as the historical record — DO NOT rewrite them), 3 missing blobs
  (unreachable, same 3 as reported), 15,087 dangling objects
  (recovery experiments + one abandoned DZ commit), 23 stale
  cache-tree pointers in linked-worktree indexes (no main-index
  error), zeroPaddedFilemode warnings. No reachable object is
  missing or corrupt. **SHAs DIVERGE from the originals:** only
  step 1 (BR-SerieC 91c8288b) reproduces exactly; step 2 (CZ join
  420a8a5a → 3a881705) diverges because its merge-message body is
  unrecoverable, and the divergence cascades to all 68 descendants
  (parent SHAs differ) + all branch tips (message bodies
  unrecoverable). The rebuilt history is faithful in content;
  original SHAs quoted in old records now resolve to their rebuilt
  counterparts (map: ~/workspace/recovery-backup-2026-11-10/
  ref_updates.json). Rebuilt IR/SV merge subjects retain their
  original #111/#112 numbering; the ledger's corrected numbering
  (FR #111, BY #112, IR #113, SV #114) is authoritative. Auto-gc
  disabled for this repo during recovery (gc.auto 0) after a
  background gc pruned the recovery agent's dangling experiment
  objects; the reflog warnings it printed are the known
  lost-SHA references, not new damage.
- 2026-11-10 17:51 — **UNFREEZE + 5 MERGES + CZ SOT FIX (counter
  114 → 119; runner 42/93 → 42/94).** Frozen ledger state committed
  as 399006f5 (FR #111 + BY #112 folds + incident record). GT
  merged #115 (2c79ca87, 28 files; pooled verified 1.0022/0.2001/
  0.7098). RO merged #116 (7ec4ae3b; engine+verdicts committed on
  the branch as 68899917; pooled 1.059351/0.221992/0.708297). CR
  merged #117 (ba3c3da0; Phase B 02f77ad8; G 0.9678/0.1965/0.7167,
  K virgin 0.6871/cal −5.64pp). AU merged #118 (09043b8b; 0/0/5,
  parent-container finding confirmed by an independent payload
  census). DZ merged #119 (cdb5a09b; branch commit 0f7422db after
  a contaminated first attempt 85ae677e — pre-staged worktree dirt
  slipped in and was reset out before recommit; lesson: check
  `git status` staged column in EVERY worktree before committing,
  the EPERM-era indexes carry pre-staged dirt). CZ-Liga SOT fix
  merged (f53001c8): canonical-name opt-in cherry-picked from the
  rebuilt branch (b2ce0e35 → f770c8e9) with CN amendments preserved
  (a wholesale merge would have regressed the CN join); merged-state
  verification from the main checkout reproduces the branch proof's
  CZ daily files bit-identical (corners 11704bec…, SOT 0076e492…,
  129 fixtures each); coordinator confirmed the id-1860 premise
  reading (Fastav/Zlin stay split, replay 0.0). CY-1Division join
  agent notified of the unfreeze (rebase onto new HEAD). Build lane
  empty; refills queued from the frozen queue head.
- 2026-11-10 18:10 — **LU-NationalDivision COMPLETE + MERGED
  (league #120, 19321cb8, 28 files).** G-LU FAIL at dev gate
  (3/6 legs): pooled n=720, Gate Zero 0.9922/0.2120/0.7063 vs
  climatology 1.0547/0.2386/0.6729 vs naive 0.9756/0.2073/0.7399
  — beats climatology on 1X2+RPS but loses both to naive; beats
  naive on OU but loses to climatology in all 3 dev seasons.
  SHRINK identical. Virgin 2025/26 deliberately UNREAD. S/C/K/T
  NOT BUILDABLE (scores-only; 385 Card events all dismissals).
  Levels: 3.15 goals/match dev pooled; traits reliable (GF r=0.730,
  GA r=0.673); frozen goals 1H share 0.4294. Coordinator recomputed
  pooled metrics from the per-match predictions CSV exactly
  (RPS exact with the standard 1/2 factor). Follow-up commit
  0440d086 force-added results_dev.csv — the builder omitted it
  (same omission as PL-ILiga/PT-Liga3; check for it at every
  merge). Counter 120; milestone 125 is 5 leagues away. One build
  slot freed (4/5 running); next refill from the recomputed queue.
- 2026-11-10 18:18 — **SK-2Liga COMPLETE + MERGED
  (league #121, b1a7c7b6, 30 files).** G-SK2 FAIL at dev gate
  (OU2.5 leg only): pooled n=613, Gate Zero 1.023678/0.220911/
  0.683592 vs climatology 1.045988/0.232024/0.683493 — wins 1X2+RPS
  in every arm but loses pooled OU2.5 by **0.000099** (same failure
  mode as sibling G-SK); X2 (relegated-mover offset, adopted, 4
  completed transitions) also fails the OU leg (0.685011).
  SHRINK ≡ Gate Zero (0 changed rows, 0 teams in the 1–5 prior-match
  band). Virgin 2025/26 deliberately UNREAD (only the
  `{"virgin_read": false}` marker). S/C/K/T NOT BUILDABLE
  (scores-only; no stats/shotmap/cards series in any of 1,269
  payloads). Levels: 2.69–3.05 goals/match (OU2.5 over-rate 0.572);
  frozen goals 1H share 0.4940 — notably higher than SK-1Liga
  0.4448 / J1 0.412. Coordinator recomputed pooled metrics from
  results_dev.json per-season rows exactly (all 9 arm/kind cells
  match). Follow-up commit b29f6077 force-added results_dev.csv —
  the builder omitted it (same omission as LU/PL-ILiga/PT-Liga3;
  check for it at every merge). Counter 121; passing markets stay
  120; milestone 125 is 4 leagues away. Build lane 4/5 running
  (KR-3, TZ, PGPL, NI); next refill Uruguay Segunda Division
  (9122) from the recomputed queue head.
- 2026-11-10 18:20 — **IR-PersianGulf COMPLETE + MERGED
  (league #122, d6a13093, 24 files).** G-IRPG FAIL at dev gate
  (OU2.5 leg): pooled n=720, Gate Zero 1.0223/0.1972/0.6434 vs
  climatology 1.0950/0.2199/0.6320 — wins 1X2+RPS, loses OU by
  0.0113 (same shape as Azadegan sibling, smaller margin); X2
  (mover prior, adopted, frozen offsets a0=−0.18/d0=+0.15) improves
  all 3 legs in all 3 seasons but still fails OU (0.6422). SHRINK
  ≡ Gate Zero (0/720 lambda changes). Virgin deliberately UNREAD
  (results_virgin.json marker). S/C/K/T NOT BUILDABLE (stats/
  shotmap null in all 1,245 payloads; yellows only from 2025/26 —
  feed break). Levels: 1.99 goals/match pooled dev, over-2.5
  31.7%; home advantage weak (+0.15); frozen goals 1H share
  0.427. Coordinator recomputed pooled metrics from
  results_dev.json per-season rows exactly. results_dev.csv
  committed by the builder (no force-add needed). Counter 122.
- 2026-11-10 18:20 — **KR-KLeague3 COMPLETE + MERGED
  (league #123, e913c974, 28 files).** G-KR3 FAIL at dev gate,
  ALL THREE legs: pooled n=690, Gate Zero 1.123054/0.239301/
  0.708503 vs climatology 1.090000/0.229657/0.692295 — beats
  climatology only in 2024, loses every leg in 2022 and 2023.
  SHRINK identical to Gate Zero (max per-match prob diff 0.0).
  Virgin deliberately UNREAD (protocol `virgin_read: false` in
  results_dev.json; harness refuses virgin mode). S/C/K/T NOT
  BUILDABLE (stats null in all 1,296 payloads; 0 plain Yellows).
  Levels: 2.438 goals/match pooled; frozen goals 1H share 0.4273.
  Coordinator recomputed pooled metrics from results_dev.json
  per-season rows exactly. NOTE: KR3 names its per-match dev file
  `predictions_dev.csv` (1,380 rows, committed) rather than the
  program-norm `results_dev.csv` — data is present, naming only;
  flagged for the final audit. Counter 123.
- 2026-11-10 18:20 — **TZ-PremierLeague COMPLETE + MERGED
  (league #124, 936ed277, 26 files).** G-TZ FAIL at dev gate
  (OU2.5 leg): pooled n=720, Gate Zero 0.956279/0.185632/
  0.716160 vs climatology 1.069080/0.223944/0.692720 — wins 1X2+RPS
  by wide margins, loses OU by +0.023440. **SHRINK FORK
  (final-audit item):** SHRINK passes ALL THREE pooled dev legs
  on its own numbers (0.925501/0.180158/0.689404, OU won by
  −0.003316) and beats Gate Zero on every leg — the first league
  where the SHRINK band genuinely bites (60 changed rows:
  Fountain Gate FC n=1, Singida Black Stars n=2, under renamed
  identities not merged). The builder correctly did NOT let it
  proceed to virgin: the frozen prereg makes Gate Zero's dev pass
  a precondition for any virgin read, and re-interpreting the gate
  after seeing results is forbidden. Numbers recorded in full in
  G_TZ_VERDICT.md for a possible future coordinator/user decision
  on the "variants are moot" rule — no action now. Virgin NOT
  read (harness `virgin()` raises RuntimeError, exercised).
  S/C/K/T NOT BUILDABLE (scores-only; 114 Card events all
  dismissals). Levels: 2.215 goals/match; traits strong (attack
  r=.575, defence r=.490); frozen goals 1H share 0.4868.
  Coordinator recomputed pooled metrics from results_dev.json
  per-season rows exactly. results_dev.csv committed by the
  builder. NOTE: TZ ships no `results_virgin.json` marker file —
  the not-read state lives only in the verdict + harness guard;
  flagged for the final audit. Counter 124; passing markets stay
  120; **milestone 125 is 1 league away.** Build lane 2/5 running
  (NI, UY-Segunda); 3 refill slots open — Cyprus 2. Division
  (9100), Honduras Liga Nacional (337), Wales Cymru Premier (116)
  launching now.
- 2026-11-10 18:29 — **NI-Premiership COMPLETE + MERGED
  (league #125, fccac125, 30 files).** G-NI FAIL at dev gate
  (OU2.5 leg, 5/6 legs): pooled n=684, Gate Zero 0.9830/0.2102/
  0.7047 vs climatology 1.0431/0.2406/0.6915 — wins 1X2+RPS, loses
  OU in all 3 dev seasons (model under-predicts totals: mean pred
  over-2.5 0.4952 vs actual 0.5439). SHRINK ≡ Gate Zero. Virgin
  2025/26 deliberately UNREAD — no results_virgin.json, no virgin
  predictions, no fitted virgin params (verdict records the
  not-read state; same gap as TZ, flagged for the final audit).
  S/C/K/T NOT BUILDABLE (stats null 1,242/1,242; cards only Red +
  YellowRed fragments). Levels: 2.83 goals/match dev pooled;
  traits reliable (GF r=0.591/0.615, GA r=0.735/0.754); frozen
  goals 1H share 0.4376. Coordinator recomputed pooled metrics
  from results_dev.json per-season values exactly (equal n=228
  per season; all three metrics match pooled to 6dp); second
  path with production model_v2 DC gives the same FAIL.
  results_dev.csv (684 rows) force-added by the builder. Counter
  125; passing markets stay 120.
- 2026-11-10 18:29 — **MILESTONE #5 — 125 leagues complete.**
  Leagues 101–125: ES-PrimeraFederacion #101, NG #102, UY-LigaAUF
  #103, NL-TweedeDivisie #104, FI-Ykkonen #105, PL-ILiga #106,
  GH-PremierLeague #107, PT-Liga3 #108, PL-IILiga #109,
  CN-LeagueOne #110, FR-Ligue3 #111, BY-PremierLeague #112,
  IR-AzadeganLeague #113, SV-PrimeraDivision #114, GT-LigaNacional
  #115, RO-LigaII #116, CR-PrimeraDivision #117, AU-Championship
  #118, DZ-Ligue1 #119, LU-NationalDivision #120, SK-2Liga #121,
  IR-PersianGulf #122, KR-KLeague3 #123, TZ-PremierLeague #124,
  NI-Premiership #125. **Tally for the block: 0 PASS / 25 FAIL /
  100 NOT BUILDABLE (of 125 candidates).** Every league in the
  block is a scores-only goals FAIL (23× G dev fail + CR G dev +
  K virgin-calibration fail; AU-Championship 0/0/5) — the goals
  calibration/totals leg kills the whole tail of the queue, and
  no stats market was buildable in any of the 25. Passing markets
  program-wide stay 120; runner 42/94. Next milestone: 150.
  Build lane 4/5 running (UY-Segunda, CY-2, HN, WAL); next refill
  Tunisia Ligue I (544) from the recomputed queue head.
- 2026-11-10 18:33 — **CY-2Division COMPLETE + MERGED
  (league #126, 7bb24ea9, 25 files).** G-CY2 FAIL at dev gate
  (LL + OU legs): pooled n=682, Gate Zero 1.074895/0.239335/
  0.721043 vs climatology 1.064304/0.239718/0.695637 — loses 1X2
  LL and OU2.5 (in all 3 dev seasons), wins RPS by only 0.000383;
  X2 (mover offset, measured GF +0.08 / GA −0.21, n=8 team-seasons)
  makes things worse pooled (1.084642/0.241676/0.724094).
  SHRINK ≡ Gate Zero. Virgin deliberately UNREAD
  (results_virgin.json marker; 2026/2027 reserved confirmatory).
  S/C/K/T NOT BUILDABLE (no stats feed in any payload; 0 plain
  Yellows in 1,210 payloads — only YellowRed 51 + Red 86).
  Levels: 2.59 goals/match pooled; traits moderate (GF r=0.43,
  GA r=0.48); frozen goals 1H share 0.4351. Coordinator recomputed
  pooled metrics from results_dev.json per-season rows exactly.
  results_dev.csv + results_virgin.json marker committed by the
  builder (no force-add needed). Builder fixed 3 Codex defects
  pre-verdict (mover_ids missing target-season intersection —
  numerically inert; virgin() leg-(iii) sign check pooled-vs-
  per-season; missing `movers` key in fitted_params_virgin) +
  one own build_data HT-blank fix; inherited CY-1 harness defects
  deliberately not copied. Counter 126; passing markets stay 120;
  milestone 150 is 24 leagues away. Build lane 4/5 running
  (UY-Segunda, HN, WAL, TN); next refill Lithuania Toplyga (228)
  launching now.
- 2026-11-10 18:42 — **UY-SegundaDivision COMPLETE + MERGED
  (league #127, 0054f102, 26 files).** G-UYSEG FAIL at dev gate,
  ALL THREE legs: pooled n=863, Gate Zero 1.1352/0.2432/0.6767 vs
  climatology 1.0927/0.2318/0.6616 — loses every season on every
  metric (attack trait barely reliable, split-half r=0.187; thin
  2021 seed home-win rate 0.318 vs 0.379–0.416 later, so 2022/23
  fits under-predict home wins). X2 (mover signal ~null over 12
  relegated-from-AUF transitions, GF −0.017 / GA +0.040) also fails
  all 3 legs (1.1327/0.2427/0.6779). SHRINK ≡ Gate Zero (0 bites).
  Virgin 2026 (transitional, n=218) deliberately UNREAD
  (results_virgin.json marker; reserved confirmatory). S/C/K/T NOT
  BUILDABLE (stats feed 0/1,219; zero plain Yellows; only Red 415
  + YellowRed 62). Levels: 2.11–2.41 goals/match by season; frozen
  goals 1H share 0.433. Coordinator recomputed pooled metrics from
  results_dev.json per-season rows exactly; production model_v2 DC
  replay reproduces every Gate Zero dev number (max per-match prob
  diff 0.00005 = CSV rounding). results_dev.csv (863 rows) +
  results_virgin.json marker committed by the builder. NOTE: the
  brief asserted referee names exist (key present) — Codex
  correctly recomputed Referee.text empty in all 1,219 payloads;
  X8 stays dropped on the verified number. Counter 127; passing
  markets stay 120; milestone 150 is 23 leagues away. Build lane
  4/5 running (HN, WAL, TN, LT); next refill Kazakhstan Premier
  League (225) from the recomputed queue head.
- 2026-11-10 18:43 — **WAL-CymruPremier COMPLETE + MERGED
  (league #128, 79a4bf89, 27 files).** G-WAL FAIL at dev gate
  (OU2.5 leg): pooled n=576, Gate Zero 0.980160/0.210987/0.705762
  vs climatology 1.053306/0.237595/0.686916 — wins 1X2+RPS, loses
  OU by +0.018846 (OU loses to base rate in 2 of 3 folds). SHRINK
  ≡ Gate Zero (changed_rows = 0). Virgin 2025/2026 deliberately
  UNREAD (results_virgin.json marker with full gate arithmetic;
  harness `virgin()` raises RuntimeError, exercised once;
  confirmatory 2026/2027, 127 matches, new 16-team format,
  reserved). S/C/K/T NOT BUILDABLE (stats/shotmap/lineup/referee
  absent 1,103/1,103; 234 Card events all dismissals, 0 plain
  Yellows). Levels: 2.90–3.07 goals/match; traits reliable
  (GF/GA r 0.50–0.86); frozen goals 1H share 0.4444. Format:
  12-team regular (rounds 1–22) + Championship/Relegation split
  groups (23–32) pooled per the DK-2Division precedent; 16
  playoff rows excluded. Coordinator recomputed pooled metrics
  from results_dev.json per-season rows exactly; builder's fresh-
  code recompute from predictions_dev.csv matches to 6 decimals.
  results_dev.csv + predictions_dev.csv + results_virgin.json
  marker committed by the builder. PROCESS NOTE: the SCKT prereg
  file was committed in Phase B (`9497178d`, after dev ran) — but
  its decision was already frozen in Phase A MODEL_DESIGN
  (`a7996837`); no fitting exists under it, so gate integrity is
  unaffected; briefs should still demand the SCKT prereg in Phase
  A. Builder fixed a Codex split-half bug pre-verdict (hardcoded
  expected values vs a different split; rewritten per-team
  chronological odd/even keyed by team id — renames had split
  clubs under name keys). Counter 128; passing markets stay 120;
  milestone 150 is 22 leagues away. Build lane 4/5 running (HN,
  TN, LT, KZ); next refill Bosnia Premier League (267) launching
  now.
- 2026-11-10 18:45 — **HN-LigaNacional COMPLETE + MERGED
  (league #129, 3e3cc48d, 28 files).** G-HN FAIL at dev gate
  (OU2.5 leg): pooled n=540 (6 tournaments), Gate Zero 0.996905/
  0.193958/0.707903 vs climatology 1.076253/0.219861/0.697649 —
  wins 1X2 LL (−0.0794) + RPS (−0.0259), loses OU by +0.0103;
  beats the base-rate OU LL in only 1 of 6 dev tournaments (worst
  2024/2025 Apertura 0.7536 vs 0.6910); same failure mode as G-GT.
  SHRINK ≡ Gate Zero (0 changed predictions; prior-match counts
  always 0 or ≥36). Virgin 2026/2027 Apertura deliberately UNREAD
  (results_virgin.json marker; reserved confirmatory). S/C/K/T NOT
  BUILDABLE (0/1,132 targets each; recorded in G_HN_VERDICT.md —
  no separate SCKT verdict files). Levels: frozen goals 1H share
  0.4572 (observed var 0.1163 vs binomial 0.1161). Coordinator
  recomputed pooled metrics from results_dev.json per-tournament
  rows exactly; builder independently recomputed climatology +
  naive + a full DC fit reconstruction (2022/2023 Apertura exact).
  results_dev.csv + results_virgin.json marker committed by the
  builder. NOTE: prereg calibration leg reads provisional iff
  |diff| ≤ 0.01 + SE (literal reading) — implemented in the
  harness but never exercised (virgin unread); flagged for the
  final audit. Counter 129; passing markets stay 120; milestone
  150 is 21 leagues away. Build lane 4/5 running (TN, LT, KZ,
  BA); next refill Ireland First Division (218) launching now.
- 2026-11-10 18:48 — **TN-LigueI COMPLETE + MERGED
  (league #130, d9b575bb, 33 files).** G-TN **PASSED dev, FAILED
  virgin calibration** — the first dev-pass → virgin-fail since
  the milestone block. Dev pooled n=602: Gate Zero 1.0043/0.2000/
  0.6338 vs climatology 1.0637/0.2194/0.6425 — dev gate PASS 6/6.
  Virgin 2025/26 (n=237, read ONCE, legitimately): 1X2 LL 0.9785
  vs climatology 1.0639 — leg (i) PASS; calibration HW −3.74pp
  (SE 2.96pp, PROVISIONAL PASS) but OU2.5 **+8.02pp** (SE 2.87pp,
  FAIL — 2.45 SE beyond the 1pp boundary); leg (iii) PASS.
  SHRINK ≡ Gate Zero. Winner NONE, nothing ships, no predictions
  file. Cause measured: 2025/26 is a goals-level regime shift —
  1.72 goals/match, OU2.5 0.270 vs dev 2.00/0.339 — while the
  270-day-decay fit predicted a 0.350 over-rate. S/C/K/T NOT
  BUILDABLE (stats null + shotmap empty in all 1,060 payloads; 0
  plain Yellows; referee text empty 1,060/1,060). Format: group
  era 2021/22–2023/24 (2 groups + championship/relegation
  groups) then single 16-team table; ALL phases enter model data;
  9 awarded matches excluded. Frozen goals 1H share 0.4539.
  Coordinator recomputed dev pooled from results_dev.json
  per-season values exactly and checked the virgin calibration
  arithmetic against the frozen rule (HW |−3.74|−1 = 2.74 ≤ SE
  2.96 provisional; OU 8.02−1 = 7.02 > SE 2.87 FAIL). One crashed
  virgin-load attempt before any fit/score wrote nothing — the
  successful run was the only read. results_dev.csv force-added
  by the builder. Counter 130; passing markets stay 120;
  milestone 150 is 20 leagues away. Build lane 4/5 running (LT,
  KZ, BA, IE); next refill North Macedonia Prva Liga (249)
  launching now.
- 2026-11-10 18:57 — **LT-Toplyga COMPLETE + MERGED
  (league #131, c44c1e34, 24 files).** G-LT **FAIL at dev, OU leg**:
  pooled n=720 (2022–2025, seed 2021), Gate Zero 1.033968/0.213597/
  0.703992 vs climatology 1.083879/0.232674/0.693432 — wins 1X2+RPS,
  loses OU2.5 by +0.0106 (OU loses in 3 of 4 dev seasons); SHRINK
  ≡ Gate Zero (0 differing predictions — thin teams are exactly the
  zero-count new ids, whose factor-0 equals the a=d=0 prior).
  Virgin 2026 (n=144, complete) deliberately UNREAD — only the
  `{"virgin_read": false}` marker; confirmatory 2027 reserved.
  S/C/K/T NOT BUILDABLE (stats/shotmap/lineup/referee absent in all
  1,044 payloads; K: Card events red-family only, 0 plain Yellows).
  Levels: 2.57 goals/match pooled; traits strong (GF r=0.80,
  GA r=0.69); frozen goals 1H share 0.4304 (true variance −0.0016,
  NOISE, presentation-only). Format: 10 teams × 180, 2021–2025;
  2026 9 teams × 144 complete; no split/playoff. X2 dropped (no
  Lithuanian sibling). **Defects fixed pre-verdict by the builder:**
  (1) unseen-team prior bug in Codex's arms.py gave new teams the
  fitted mean rating instead of prereg-literal a=d=0 — changed
  Gate Zero on 104 dev matches and manufactured a spurious SHRINK
  difference; fixed to 0.0, re-run; (2) brief's "events exist in
  all rows" was wrong — 90 rows have empty event lists, all 0–0
  (docs corrected, no numeric impact); (3) Codex stray duplicates
  (analysis/ + config.yaml at worktree root) deleted. Coordinator
  recomputed pooled LL/RPS/OU from results_dev.csv exactly
  (RPS = 1/2 x cumulative RPS: GZ 0.213597, clim 0.232674) and
  per-season OU; prereg 2bd771ea precedes fitting f50718db;
  results_dev.csv committed by the builder (no force-add needed).
  Counter 131; passing markets stay 120; milestone 150 is 19
  leagues away. Build lane 4/5 running (KZ, BA, IE, MK); next
  refill Montenegro 1. CFL (232) launching now.
- 2026-11-10 19:02 — **KZ-PremierLeague COMPLETE + MERGED
  (league #132, 7ffcca85).** G-KZ **PASS PROVISIONAL — Gate Zero
  SHIPS (program's THIRD goals pass).** Dev pooled n=702
  (2022–2025, seed 2021): Gate Zero 1.0290/0.2135/0.6819 vs
  climatology 1.0712/0.2285/0.6929 — dev gate PASSES all 3 legs
  (wins LL in all 4 dev seasons); SHRINK ≡ Gate Zero (0 differing
  predictions). Virgin 2026 (n=240, complete, read ONCE after the
  dev pass): 1X2 LL 1.0152 vs climatology 1.0678 — leg (i) PASS;
  calibration HW −1.26pp (SE 3.09) and OU2.5 −3.21pp (SE 3.21) —
  both breach the 1.0pp boundary but within 1 SE = PROVISIONAL
  PASS; leg (iii) SHRINK dev LL ≤ Gate Zero 4/4 seasons (equal).
  Both-pass tie → simpler arm ships: Gate Zero, virgin fitted
  params (rho 0.0, mu 1.3373, h 0.2543) + 240-row predictions
  (FT + 1H/2H via frozen constant 0.4539). S/C/K/T NOT BUILDABLE
  (no target in any season: stats/shotmap/splits/lineups/
  playerStats/named referees 0/1,124; 0 plain-Yellow events).
  Levels: goals-for split-half r=0.802 (n=20) — unusually strong
  attack trait, why Gate Zero passes here where UY-SegundaDivision's
  failed. Format: single round-robin, calendar-year seasons, no
  split/playoff; 4 score/event mismatches flagged (3 awarded + 1
  feed-extra goal); HT cross-check 1,040/1,040. **Defects fixed
  pre-verdict:** (1) EDA entrant classification used
  previous-season-only, misclassifying returnees — fixed to
  accumulated union pre-prereg (corrected n=6); (2) virgin-predict
  overwrote results_virgin.json with Gate Zero only, dropping
  SHRINK's entry — restored from that run's reported numbers
  (provably identical; recorded in shrink_note; the J1 harness has
  the same overwrite behaviour — audit item). Coordinator recomputed
  dev pooled + virgin LL/RPS/OU/calibration from the CSVs exactly
  (LL 1.015226, OU 0.687263, HW cal +1.26pp actual−predicted, OU
  +3.21pp; halves split 0.4539 exact; 240 probs sum to 1);
  prereg 10121951 precedes fitting 6ca341e2; results_dev.csv
  committed by the builder. **Audit flags:** results_virgin.json
  calibration diffs use predicted−actual sign (opposite the frozen
  actual−predicted convention; magnitudes identical, verdict
  unaffected — same class as the AR-B note) and its SEs differ
  slightly from a direct binomial recompute (HW 0.0309 vs 0.0322;
  OU 0.0321 vs 0.0323) — both legs provisional under either SE.
  Counter 132; passing markets 121 (goals passes now 3: SCO, TR,
  KZ). **KZ goals join QUEUED (16th in join queue)** — join lane
  is 2/2 full (CY + NO-OBOS), no launch now. Build lane 5/5
  running (BA, IE, MK, ME, VN); next refill Albania Kategoria
  Superiore (260).
- 2026-11-10 19:05 — **BA-PremierLeague COMPLETE + MERGED
  (league #133, 1161f315).** G-BA **PASS PROVISIONAL — Gate Zero
  SHIPS (program's FOURTH goals pass).** Dev pooled n=772
  (2022/23–2025/26): Gate Zero 0.9473/0.1947/0.6845 vs climatology
  1.0522/0.2283/0.6972 — dev gate PASSES all 3 legs (wins LL+RPS
  in all 4 dev seasons; OU wins 3/4, loses 2025/26 narrowly 0.6775
  vs 0.6746); SHRINK ≡ Gate Zero (0 differing predictions — prior
  counts are 0 or ≥33, the 1–5 band never occurs). Virgin 2026/27
  partial (n=64, rounds 1–13, read ONCE after the dev pass, as
  frozen in the prereg): 1X2 LL 0.8880 vs climatology 1.0625 —
  leg (i) PASS; calibration HW +1.00pp (SE 5.41pp per json; 6.24pp
  by direct binomial recompute) and OU2.5 +2.45pp (SE 6.32pp) —
  both breach the 1.0pp boundary but within 1 SE = PROVISIONAL
  PASS; HW is the narrowest provisional in the program (excess
  0.004pp over the boundary). Leg (iii) SHRINK dev LL ≤ Gate Zero
  4/4 seasons (equal). Both-pass tie → simpler arm ships: Gate
  Zero (h=0.3204, rho=0.0, mu=1.1811). Virgin OU-LL 0.6989 is
  WORSE than climatology's 0.6815 — not a gate leg, recorded
  plainly; confirmatory re-read at season end reserved. S/C/K/T
  NOT BUILDABLE (preregistered Phase A: stats null + shotmap empty
  1,036/1,036; referee empty; lineups 13/1,036; 0 Yellow cards in
  the whole corpus — 205 cards are YellowRed 77 + Red 128).
  Levels: 2.48 goals/match pooled (2.16–2.78/season); traits
  signal (GF r=0.593, GA r=0.621); frozen goals 1H share 0.4493.
  Format: 12 teams × 33 rounds (2021/22–2024/25), 10 × 36 from
  2025/26; no split/playoff; 4 awarded matches excluded from all
  fits/evaluations. **Defects fixed pre-verdict:** (1) naive
  trailing-10 was stale (prior seasons only) — fixed to every
  match strictly before kickoff (naive pooled LL 1.0104 → 0.9829;
  model numbers unchanged); (2) fitted_params_virgin.json omitted
  the two newcomer clubs (Čelik Zenica, BSK Banja Luka) — patched
  with a=d=0, training_n=0 (definitional, no re-read; harness
  fixed the same way); (3) EDA split-half mismatch caught in
  verification (index-order vs date-order shuffles) — recomputed
  canonically (GF 0.548→0.593, GA 0.546→0.621). Coordinator
  recomputed dev pooled + virgin LL/RPS/OU/calibration from the
  CSVs exactly (note: results_dev.csv stacks both arms, 1,544
  rows; virgin predictions file carries gate_zero only, 64 rows;
  halves split 0.4493 exact; probs sum to 1); prereg 02673f5f
  precedes fitting 61ef38ff; results_dev.csv committed by the
  builder. **Audit flag:** results_virgin.json calibration diffs
  use predicted−actual sign (the prereg itself writes the leg as
  |mean predicted − actual|, so prereg-consistent here; KZ's json
  has the same sign against a differently-worded frozen rule) and
  its HW SE (0.0541) differs from the direct binomial recompute
  (0.0624) — verdict provisional under either. Counter 133;
  passing markets 122 (goals passes now 4: SCO, TR, KZ, BA).
  **BA goals join QUEUED (17th in join queue)** — join lane is
  2/2 full (CY + NO-OBOS), no launch now. Build lane 5/5 running
  (IE, MK, ME, VN, AL); next refill Scotland League One (124).
- 2026-11-10 19:07 — **IE-FirstDivision COMPLETE + MERGED
  (league #134, 2cf84f43).** G-IEFD **FAIL at dev, OU leg**:
  pooled n=683 regular (2022–2025), Gate Zero 1.0587/0.2235/
  0.7251 vs climatology 1.0829/0.2331/0.6908 — wins 1X2+RPS,
  loses OU2.5 by +0.0343, and loses the OU leg in ALL FOUR dev
  seasons (margins +0.068, +0.043, +0.032, +0.001) — systematic,
  not a pooled fluke. X2 (mover offset, +0.23 GF / −0.27 GA, n=6)
  fails the same leg, worse than Gate Zero (1.0623/0.2236/0.7307).
  Virgin deliberately UNREAD — only the `{"virgin_read": false}`
  marker; 2026 stays virgin for any future design. S/C/K/T NOT
  BUILDABLE (preregistered Phase A: no SOT/corners/shots target
  in any of 1,028 payloads; K: zero plain-Yellow events —
  Red/YellowRed only, 0.20/match; referee never named). Levels:
  2.84 goals/match dev (season levels swing 2.63–3.06; 2022 is an
  away-edge season, −0.16 home edge); traits very strong (GF
  split-half r=0.824, GA r=0.961, n=15 teams); frozen goals 1H
  share 0.441 (true variance 0.000). Format: 2021 10 teams/27
  rounds, 2022 9 teams/36 rounds, 2023–2026 10 teams/36 rounds;
  playoffs (2-legged semis + final, 5/season) EXCLUDED from all
  fitting/evaluation (regular-season scope frozen in MODEL_DESIGN
  + prereg). Warehouse gap: one 2025 regular match (Finn Harps vs
  Kerry FC, round 1) absent, n=179 not 180, not imputed; two
  goal-feed anomalies flagged (Cabinteely–Galway 0–3 with no
  events; UCD–Wexford side-flipped feed), both kept as official
  score with HT NaN. **Defects fixed pre-verdict:** (1)
  `has_extra_time` first used key presence on `status.halfs`
  (empty extra-half keys exist in every match) and flagged ~all
  of 2021 — fixed to require a non-empty timestamp (3 matches,
  all playoff finals); (2) Codex's crashed first run wrote an
  early harness/runner/README draft to a wrong-path
  `engine/goals/` at the worktree root — deleted, never staged.
  Coordinator recomputed pooled numbers as n-weighted means of
  the per-season rows in results_dev.csv exactly (GZ/X2/clim all
  three metrics); prereg 3f6eed8b precedes fitting 6896ec35;
  results_dev.csv committed by the builder. **Audit flag:
  results_dev.csv holds per-season summary rows only (20 rows),
  NOT per-match predictions** — unlike the program norm (cf.
  KR3's naming-only deviation); the verdict rests on the summary
  numbers + the builder's production-DC replay (2022 fit, max
  prob diff 0.0) and independent climatology recompute (6dp).
  Counter 134; passing markets stay 122. Build lane 5/5 running
  (MK, ME, VN, AL, SCO); next refill Slovenia Prva Liga (173).
- 2026-11-10 19:11 — **MK-PrvaLiga COMPLETE + MERGED
  (league #135, 9341a7ec).** G-MK **FAIL at dev, OU leg**:
  pooled n=549 (2022/23–2024/25), Gate Zero 1.0500/0.2139/
  0.6899 vs climatology 1.0645/0.2194/0.6804 — wins 1X2 LL + RPS
  vs BOTH baselines (5/6 legs) but loses OU2.5 to climatology by
  +0.0096, in ALL THREE dev seasons (0.6973 vs 0.6920; 0.6890 vs
  0.6767; 0.6844 vs 0.6740). Not a level miss: pooled mean P(over)
  0.4323 vs climatology 0.4339, both ~+1.6pp over actual 0.4171 —
  the per-match OU spread does not pay. SHRINK ≡ Gate Zero (0
  differing predictions; synthetic test proves the scaling is
  active, n=3 → 0.5). Fitted h/rho: 0.2576/−0.10, 0.2303/−0.15,
  0.3112/−0.10. Virgin 2025/2026 (n=197 model rows) deliberately
  UNREAD — only the marker with full gate arithmetic; the 2025/26
  goals-level jump (3.09/match) plays no part in the verdict and
  remains an untested virgin fact; confirmatory 2026/2027 partial
  (n=65) untouched. S/C/K/T NOT BUILDABLE (stats null + shotmap
  empty 1,022/1,022; K: 0 Yellow events, referee named 0/1,022 —
  only 131 Red + 87 YellowRed). Levels: goals/match 2.37/2.52/
  2.25/2.32 (model rows)/3.09 virgin/2.68 reserve; traits
  GF r=0.635 / GA r=0.548; frozen goals 1H share 0.4323
  (559/1,293, variance ratio 0.9572 → NOISE). Format: single-table
  triple round-robin, 33 rounds; 12 teams (11 in 2022/23, 10 in
  2026/27 partial); no playoffs/split groups; 13 awarded matches
  excluded from every fit/score (9 unplayed walkovers + 3
  played-then-overturned in 2024/25, 1 unplayed in 2025/26);
  teams keyed by FotMob id (3 renames). No MK sibling → no X2
  mover prior. **Defects fixed pre-verdict:** (1) `eda.py` halves
  variance used deviations from the pooled share instead of the
  TN/J1-standard variance around the mean of shares — fixed
  (0.119824 → 0.119702, ratio 0.9582 → 0.9572; constant + NOISE
  conclusion unchanged); (2) DATA_UNDERSTANDING coverage table
  had two wrong event counts (2025/26: 178, 2026/27: 57) —
  corrected to file values (184, 61). Coordinator recomputed
  pooled LL/RPS/OU from per-match results_dev.csv exactly (549
  rows); prereg in Phase A commit ecfd67f7 precedes fitting
  570d73f1; results_dev.csv force-added by the builder; config
  records shipping NONE / no_ship. Counter 135; passing markets
  stay 122. Build lane 5/5 running (ME, VN, AL, SCO, SLO); next
  refill Azerbaijan Premier League (262).
- 2026-11-10 19:16 — **VN-VLeague COMPLETE + MERGED
  (league #136, b617fcae).** G-VN **FAIL at dev, RPS + OU legs**:
  pooled n=654, Gate Zero 1.0964/0.2236/0.7413 vs climatology
  1.1056/0.2230/0.6884 — wins 1X2 LL only; RPS loses narrowly by
  0.0007 and OU2.5 loses by +0.0528, in ALL FOUR dev seasons
  (0.856/0.693/0.709/0.710 vs climatology 0.694/0.680/0.689/
  0.689) — systematic, not one bad year. OU level is fine (mean
  predicted over-rate 0.41–0.45 vs actual 0.42–0.46) but the
  match-level spread is too wide. Contributors measured: the 2022
  fold trains on only the 84-match truncated 2021 seed (worst OU
  LL, 0.856); defence trait weak (split-half r_GA mean 0.13 vs
  r_GF 0.52); draw rate volatile (0.14–0.37). Model still beats
  naive trailing-10 clearly (LL 1.0964 vs 1.1766). SHRINK ≡ Gate
  Zero (0 differing predictions). Virgin 2025/2026 deliberately
  UNREAD — only the sentinel; no predictions file, no fitted
  params. S/C/K/T NOT BUILDABLE (preregistered Phase A:
  stats/shotmap empty 969/969, no xG/SOT/corners/shots; K: 0
  plain-Yellow events in 2021–2023/2024 — yellows switch on only
  in 2024/2025; referee text empty 969/969; lineups exist only
  from 2024/2025, 413 matches). Mixed season labelling verified
  disjoint (2023 ends 2023-08-27, 2023/2024 starts 2023-10-20 —
  no overlap/double-count); 2021 truncated at round 12; 2023
  split-group (43 phase-2 matches); 11 team ids have name-spelling
  variants (keyed on id); one flagged score/event mismatch (match
  4688919, official 1–0 kept). HT via Half events 924/924
  cross-validated; frozen goals 1H constant 0.4468. **Defects:**
  none in engine or data pipeline (builder ran a from-scratch DC
  re-implementation from the model_v2.py spec — two folds exact to
  4dp; dc.py/arms.py differ from KZ only in docstrings). Process
  note: the gitignored warehouse is absent from worktrees, so the
  builder copied just this league's 969 JSONs (35 MB, gitignored)
  into the worktree — nothing committed from that copy. Coordinator
  recomputed pooled LL/RPS/OU from per-match results_dev.csv
  exactly (also from probs: 1.096398/0.223625/0.741289); prereg in
  Phase A commit 6b7f9799 precedes fitting 36fee6dc;
  results_dev.csv force-added by the builder. Counter 136;
  passing markets stay 122. Build lane 5/5 running (ME, AL, SCO,
  SLO, AZ); next refill Armenia Premier League (118).
- 2026-11-10 19:17 — **AL-KategoriaSuperiore COMPLETE + MERGED
  (league #137, d17a8638).** G-AL **FAIL at dev, ALL THREE legs**:
  pooled n=720 regular (2022/23–2025/26), Gate Zero 1.0972/0.2237/
  0.6779 vs climatology 1.0886/0.2224/0.6660 — loses 1X2 LL, RPS
  and OU2.5; naive trailing-10 also loses to climatology
  (1.1020/0.2263/0.6808). Model wins 2 of 4 dev seasons on LL
  (2022/23, 2025/26) but loses badly in 2023/24 (1.1314 vs
  1.0916). Honest pre-fit expectation from EDA F2: team traits
  weak (split-half GF 0.27 / GA 0.14, 5-season means) and tiers
  flat (top +0.32 to bottom −0.65 GD/match). SHRINK ≡ Gate Zero
  (0 differing predictions; prior counts per fold 0 or ≥36, never
  1–5). Virgin 2026/2027 (n=55, rounds 1–11) deliberately UNREAD
  — only the marker; no predictions file, no fitted params;
  window untouched for any future re-test under a fresh prereg.
  S/C/K/T NOT BUILDABLE (preregistered Phase A: stats null +
  shotmap empty 969/969; lineups 0/969; referee empty 969/969;
  0 Yellow events — 230 red-family cards only). **Format surprise
  (the 184/186 suspicion resolved):** 10 teams × 36 rounds every
  season, plus a Final Four playoff from 2023/24 — 14 matches
  total. 2023/24 + 2024/25: semis (1/2) + bronze + final;
  2025/26: a 6-match round-robin MISLABELLED by FotMob as rounds
  1–3, dated 2026-05-16..31 (regular season ended 2026-05-10).
  Flagged playoff=True in the CSV, excluded from every
  fit/evaluation; dev scored n=720 (not 772). Levels remarkably
  stable: 2.21–2.28 goals/match across all five complete regular
  seasons; home edge +0.24 pooled. Frozen halves constant 0.4267
  (920/2,156; excess variance −0.0074 → true SD 0.0pp, pure
  noise). No awarded matches (0/969). 2-club churn every season;
  4 team ids have two diacritic name spellings (key on ids). No
  Albanian sibling — no X2. **Defects fixed pre-verdict:** (1)
  builder repo-root resolution had one `dirname` too many
  (resolved to ~/workspace instead of the worktree) — fixed before
  the CSV was built (payload-root fallback FOOTBALLPREDICTION_ROOT
  carried since the worktree lacks the 24 GB warehouse); (2) first
  draft of the EDA pooled HW/D/AW/OU/BTTS row was wrong —
  recomputed from the CSV (41.0/30.4/28.6/38.6/47.3); (3)
  churn-name paragraph wrong for three seasons — corrected against
  the verified id→name map before committing; (4)
  results_dev.csv initially missed from the engine commit
  (gitignored) — force-added via amend, per program norm.
  Coordinator recomputed pooled LL/RPS/OU from per-match
  results_dev.csv exactly (stacked arms, 1,440 rows; no 2026/2027
  rows, no playoff ids in dev); prereg 96fcfd57 precedes fitting
  d092ae89; results_dev.csv force-added. Counter 137; passing
  markets stay 122. Build lane 5/5 running (ME, SCO, SLO, AZ,
  AM); next refill Iceland 1. Deild (216).
- 2026-11-10 19:23 — **ME-1CFL COMPLETE + MERGED (league #138,
  b62804d7).** G-ME **PASSED dev, FAILED virgin leg (i)** — the
  first dev-pass → virgin-fail since TN #130. Dev pooled n=539
  (2022/23–2024/25): Gate Zero 1.069383/0.219356/0.684857 vs
  climatology 1.090641/0.226923/0.689907 — dev gate PASSES all 3
  legs (OU margin thin, 0.0051, carried by 2024/25 alone: OU
  0.6467 vs 0.6853; the other two dev seasons lose OU). SHRINK ≡
  Gate Zero (0 differing predictions). Virgin 2025/26 (n=180,
  read ONCE, legitimately after the dev pass; fit train n=718,
  cutoff 2025-08-04, h=0.161, rho=0.0): 1X2 LL 1.100431 vs
  climatology 1.071892 — leg (i) FAIL; RPS 0.237812, OU2.5 LL
  0.752933 vs climatology 0.684552; calibration home-win
  +3.68pp (SE 3.82pp, PROVISIONAL PASS) and OU2.5 −1.49pp
  (SE 3.94pp, PROVISIONAL PASS); leg (iii) sign check 3/3.
  Nothing ships. Cause measured: home wins spiked to 45.0% in
  the virgin season (dev pooled 40.1%). Confirmatory 2026/2027
  remains reserved and unread. S/C/K/T NOT BUILDABLE
  (preregistered Phase A: stats/lineup/referee null on all rows;
  shotmap is `{"shots": [], "Periods": {"All": []}}` everywhere
  — SOT/total-shots not buildable despite the 2-key dict; Card
  events Red 74 + YellowRed 51, **Yellow 0** — no cards target).
  Corpus: 972 index rows → 971 played; one ghost fixture
  (3818692, Sutjeska–Mornar R36 2021/22, never started, 4
  phantom goal events) excluded; 2024/25 is 179 rows because
  the Buducnost–Decic R36 fixture is absent from the index
  entirely. Single phase, 10 teams × 36 rounds, no split/playoff.
  EDA: goals/match drifts 2.64 → 2.37; F2 — chronological
  split-half GF r=0.13 (team attack drifts hard: Mornar
  0.91→1.35, Sutjeska 1.75→1.38) but season-parity split-half
  r=0.69 both sides, so traits exist under drift (decay's job);
  1H goals share frozen at 0.426643 (true variance −0.0046,
  noise). No Montenegrin sibling league — no X2; SHRINK is the
  thin-data treatment. **Defects found (all recorded in the
  verdict):** (1) Codex added an `over05` key to `dc.py`'s
  `probs()` (for the 1H OU 0.5 line) — deviation from the
  verbatim-copy instruction, verified harmless (dev byte-identical
  under final code); (2) the harness `_calibration_leg`
  arithmetic string misstates "abs(...) <= 1.0pp" when the
  difference exceeds it; the status logic is correct and
  independently verified. Cosmetic; left unfixed post-virgin-read
  by design. Coordinator recomputed dev pooled + virgin LL/RPS/OU/
  calibration from the CSVs exactly (LL 1.100431, OU 0.752933, HW
  cal +3.68pp, OU cal −1.49pp; halves split 0.4266; 180 probs sum
  to 1); prereg 5d9d733c precedes fitting cde1bea9;
  results_dev.csv (539 per-match rows) + virgin predictions (180
  rows) committed by the builder. Counter 138; passing markets
  stay 122. Build lane 5/5 running (SCO, SLO, AZ, AM, IS-1Deild
  launched 19:23 as the ME refill); queue tail RECOMPUTE now.
- 2026-11-10 19:30 — **CY-1Division JOINED the daily runner
  (runner 43/96)** (merged 3a1eb828; branch build/runner-cy,
  tip 6b581bc6 — single commit, ONLY league/runner/{README.md,
  active.yaml} + league/CY-1Division/data/build_data.py, 102
  insertions / 1 deletion; no run_daily.py change). Markets:
  corners gate_zero 9.5 CLEAN PASS (virgin LL 0.688133,
  calibration −0.26pp) + total_shots arm A 18.5 PROVISIONAL
  PASS (virgin LL 0.688140, calibration +1.468pp within 1 SE
  3.217pp), both FT-only (`halves_share_1h: null`). Goals/SOT/
  cards FAILed — excluded. Merge: active.yaml auto-merged
  (CZ SOT fix had added +1 market after the branch base, so
  the merged count is 43/96, not the branch's 43/95 — the
  README proof paragraph was corrected to say so); README
  conflict resolved by concatenation (CZ paragraph kept, CY
  paragraph appended). **Merged-state verification
  (coordinator, from the main checkout):** one-league CY run
  (`~/workspace/runner-checks/run_one_league_cy.py`, venv,
  MALLOC_ARENA_MAX=2) reproduces the branch proof's CY files
  bit-identical — corners daily md5 39c94abfe694fae4b16294a0fc6cc4d3,
  total-shots daily 46b8c95d1b224753be1ff229fd18ce34, ledger
  6c1b9c90b561d1b05ea59f204d8b399f; 119 fixtures in both markets,
  fetched_new 0, settled 0. Branch proofs: two full runs on the
  rebased base (43 leagues, 95 markets on that base), each
  12,066 predictions, 0 errors, fetched 0 everywhere; 180/181
  files bit-identical (sole exception: the known pre-existing
  ZA-PSL corners daily — FT values bit-equal to ledger on all
  160 rows). Replay diffs: corners EXACT 0.0 (239 fixtures);
  total shots max diff exp 0.0802 — **decomposed, not
  hand-waved:** exact-harness walk vs shipped = 7.1e-15,
  refit-every-day walk vs shipped = 0.0802, refit-every-day vs
  runner replay = 1.47e-08 — the harness refits the regression
  store on a 7-day cadence (theta up to 7 days stale) while the
  replay fits fresh per fixture day; the production runner uses
  the same 7-day cadence as the harness, so the gap is a harness
  artefact, not a runner error. Synthetic settlement (match
  5975448): corners actual 11.0 (hit, LL 0.6846), shots actual
  26.0 (hit, LL 0.4576), each settled exactly once. **No
  adapter amendments** (run_daily.py untouched). **Defects,
  stated plainly:** (1) CY builder ignores the runner's
  INDEX/MAIN_REPO globals (hard-coded main-checkout root —
  inert in production); (2) total-shots
  `fitted_params_virgin.json` carries stale `primary_line:
  17.5` (runner reads `fitted_params.json`, 18.5 — never
  touches it). Builder hard-equality count assert floored to
  `>=` in the join commit (AU/MLS pattern). **Join slot
  refilled:** SE-Superettan cards join launched (brief
  ~/workspace/agent-briefs/runner-se-superettan-join.md;
  branch build/runner-se-superettan @ wt-runner46) — cards
  GZ 3.5 prov, halves 0.3344, event-unified yellows target.
- 2026-11-10 19:32 — **AM-PremierLeague COMPLETE + MERGED
  (league #139, 21486c92).** G-AM **FAIL at dev, OU leg**:
  pooled n=653 (2022/23–2025/26, 7 awarded matches excluded),
  Gate Zero 0.993863/0.214911/0.714220 vs climatology
  1.052350/0.240995/0.701880 — wins 1X2 LL + RPS, loses OU2.5
  by +0.0123, and loses the OU leg in ALL FOUR dev seasons
  (+0.0292, +0.0082, +0.0058, +0.0032). SHRINK ≡ Gate Zero
  (0 differing predictions; prior counts 0 or ≥28 per target
  season). Virgin 2026/27 (n=77, rounds 1–13 + 1 early
  round-15 fixture) deliberately UNREAD — only the marker
  (`{"virgin_read": false, "reason": "gate_zero_failed_dev"}`);
  no predictions file, no fitted params. S/C/K/T NOT BUILDABLE
  (preregistered Phase A: stats null 881/881, shotmap empty
  881/881, referee empty 881/881 — scores+events only).
  Diagnosis: season-blocked fit is stale on totals in a
  fast-rising league (levels 2.42→2.48→2.79→3.15); mean
  predicted P(over 2.5) vs actual: −9.5pp, −6.5pp, −13.3pp in
  the three rising seasons, then +6.9pp in 2025/26 after
  fitting the hot year. The flat climatology rate is less
  confidently wrong per match, so it wins OU LL. Non-gate
  finding (builder-verified, fresh DC implementation):
  naive trailing-10 beats Gate Zero pooled on LL (0.9144 vs
  0.9939) and RPS — freshness is worth ~0.08 LL here; a
  within-season-updating fit would be the arm for any future
  re-test under a fresh prereg (not authorised now). Format:
  NO playoff/split-group ever; team count changes every season
  (9→10→10→11→10→12; 32/36/36/30/27 games per team). 7 awarded
  matches, all 2024/25, all involving West Armenia (6 never
  played) — excluded from every fit/evaluation (BA/AE
  precedent); dev scored n=653. Team traits are STRONG
  (split-half GF 0.78 / GA 0.76, steep tiers +1.17 to −1.42) —
  the opposite pole from AL — which makes the OU-only failure,
  not a no-signal failure, the story. Halves constant 0.4335,
  frozen (excess variance −0.0086, true SD ≈ 0). **Defect
  caught and fixed (builder's own, pre-commit):** first EDA
  halves test used a match-total 1H-share definition returning
  r≈0.83; a binomial-resampling null test showed r≈0.82 for the
  same definition (confounded by team strength). The valid
  own-goals definition gives mean r≈+0.08 (noise); EDA F3/
  FEATURES R1 report that, constant 0.4335 unaffected.
  Coordinator recomputed pooled + per-season LL/RPS/OU from
  the stacked per-match results_dev.csv exactly (1,306 rows =
  653 matches × 2 arms; naive numbers are the builder's,
  not recomputable from the CSV — the gate decision does not
  depend on them); prereg 98b8c9c1 (Phase A) precedes fitting
  4138af41; results_dev.csv committed by the builder. Counter
  139; passing markets stay 122. Build lane 5/5 running (SCO,
  SLO, AZ, IS-1Deild, PA-LPF launched 19:32 as the AM refill);
  queue head now Faroe Islands Premier League (250).
- 2026-11-10 19:34 — **SLO-PrvaLiga COMPLETE + MERGED (league
  #140, 27ce90cb).** G-SLO **FAIL at dev, OU leg (by 0.0014)**:
  pooled n=538 (2022/23–2024/25), Gate Zero 1.031035/0.210921/
  0.697141 vs climatology 1.086857/0.230423/0.695709 — wins 1X2
  LL + RPS (5/6 dev legs), loses OU2.5 by +0.001432; the OU leg
  loses in 2022/23 (+0.0074) and 2024/25 (+0.0057), wins only
  2023/24. SHRINK ≡ Gate Zero (0 differing predictions;
  n_1_to_5 = 0 in every dev season; entrants 1, 1, 2 at
  league-mean fallback). Virgin 2025/26 deliberately UNREAD —
  only the marker; the 2025/26 level jump (3.0870 goals/match,
  OU2.5 0.6522, HW 0.4969 vs dev 2.7026/0.4870/0.4033) remains
  an untested virgin fact; confirmatory 2026/27 reserve (n=74)
  untouched; no predictions file. S/C/K/T NOT BUILDABLE
  (preregistered Phase A: stats null + shotmap empty 956/956;
  K: plain Yellow events 0; referee named 0/956). Root cause
  measured: mean P(over 2.5) 0.4235 vs actual 0.4870 (−6.34pp)
  — systematic under-prediction of overs. Fitted h/rho:
  0.2152/−0.05, 0.2000/−0.05, 0.2044/−0.10. Format: 10 teams,
  single table, 36 rounds, no playoffs (`hasPlayoff` never
  True). **2025/26 shortfall solved:** Domžale played only 18
  matches (rounds 1–18); every other team 34; rounds 19–36
  have 4 matches each — all 18 missing fixtures are Domžale
  fixtures in rounds 19–36; payloads state no reason. 3
  awarded matches (4206754, 4206847, 4834588), all 3-0, zero
  goal events — the only goal-event mismatches; excluded from
  every fit/score. HT via `time ≤ 45` rule agrees with HT
  marker 893/893. No Slovenian sibling league (only id 173 in
  the index) — no X2 mover. Frozen goals 1H share 0.4498
  (654/1,454; variance ratio 0.9364, implied true SD 0.0000 —
  noise). Split-half reliability: scored window GF r=.6302,
  GA r=.4756 (30 team-seasons). **Defects / diagnostics found:**
  (1) **Naive baseline degenerate edge (spec, not a bug):**
  naive trailing-10's 2024/25 1X2 LL is 1.3859, driven by two
  matches at the 27.63 epsilon floor — entrant Nafta scored
  after a scoreless debut, so its trailing-10 mean was exactly
  0.0 and the baseline assigned P=0 to Nafta scoring.
  Prereg-spec-faithful; removing both matches naive pooled LL
  would still be ≈1.0534 > Gate Zero's 1.0310, so the gate
  outcome is unaffected. Recorded in the verdict. (2) **Engine
  optimiser tolerance (not a bug):** independent re-fit finds
  slightly higher training LLs; scored metrics agree within
  0.004 and the verdict is unchanged. Recorded in the verdict.
  Coordinator recomputed pooled + per-season LL/RPS/OU from
  per-match results_dev.csv exactly (538 rows; naive 2024/25
  LL 1.3859 confirmed); prereg d973cfe6 (Phase A) precedes
  fitting e8d4bdfa; results_dev.csv committed by the builder.
  Counter 140; passing markets stay 122. Build lane 5/5
  running (SCO, AZ, IS-1Deild, PA-LPF, MY-LigaSuper launched
  19:34 as the SLO refill); queue head now Iceland 2. Deild
  (10226).
- 2026-11-10 19:35 — **SCO-LeagueOne COMPLETE + MERGED (league
  #141, 5213a6ce).** **0 PASS / 2 FAIL / 3 NOT BUILDABLE** —
  the league's only two buildable candidates both failed.
  **G-SCO-L1 FAIL at dev, OU leg:** pooled n=540 (2022/23–
  2024/25), Gate Zero 1.072613/0.230914/0.705258 vs climatology
  1.077529/0.234369/0.686842 — wins 1X2 LL + RPS, loses OU2.5
  by +0.0184. SHRINK ≡ Gate Zero (0 differing predictions;
  no team ever in the 1–5 prior-match band). X2 (mover gap
  real: down from Championship pooled ΔGF +0.176 / ΔGA −0.288,
  consistent all 4 seasons; up-other −0.136 / +0.201) also
  fails the OU leg (1.076237/0.230893/0.708908). **The
  G-SCOCH X2 defect was NOT repeated:** offsets apply only to
  each target season's own entrants (verified: X2 ≡ Gate Zero
  in 2022/2023, max |Δp| = 0.0; offsets recorded per season).
  G virgin NOT read — only the marker. **K-SCO-L1 PASSED dev,
  FAILED virgin (both legs):** dev LL@3.5 0.684551 vs base
  0.693715 vs naive 0.694791 — dev gate PASS, beats both
  baselines in all 3 dev seasons; virgin 2025/26 (n=180, read
  ONCE): LL@3.5 0.654519 vs base 0.689999 vs **naive 0.637606**
  — leg (i) FAIL; calibration **+7.42pp** (SE 3.55pp) — leg
  (ii) FAIL. Cause measured: 2025/26 was the card-heaviest
  season on record (4.13 yellows/match, over-3.5 rate 0.606 vs
  dev 0.469); the naive trailing-10 adapts to the level shift
  faster than the decayed team-rating model — same pattern as
  K-SCOCH. S/C/T NOT BUILDABLE (preregistered Phase A: stats
  Periods empty 0/969, shotmap 0 shots; no target in any
  season). Corpus: 969 matches, 180/season, 10 teams × 36
  rounds, no play-offs; scores reconcile 969/969 with event
  goals. Stats 0/969, shotmap 0, referee text empty 0/969,
  events 969/969. Goals/match 2.82/2.96/3.17/2.70/2.64; event
  yellows/match 3.62/3.53/3.64/3.53/4.13. Frozen halves
  constants: goals 0.4295 (true var −0.0041), yellows 0.3141
  (true var +0.00002, SD ≈0.5pp). 2026/2027 was never loaded
  by any engine (asserts in both harnesses); it appears only
  as descriptive levels in EDA, same as the Championship
  precedent. **Defects / notes found:** (1) Worktree has no
  warehouse payloads (gitignored, 0 JSON files); all reads
  came read-only from the main checkout
  `~/workspace/footballprediction/data_enrichment/fotmob_world/`,
  the same pattern the Championship builder used. Data CSVs
  are gitignored; the builder script is committed and
  regenerates them. (2) **Latent (never triggered):** L1
  `dc.py` rho selection calls `log(tau(...))` directly, where
  the sibling code skips `tau == 0` terms — a fit producing
  λ > 6.67 with a (0,1) scoreline would crash instead of
  skipping. No such case occurred in dev. Also one dead no-op
  line in the G harness (`r.pop(...) if False`). (3) Phase A
  corrections made before prereg: fixed garbled X1 wording,
  froze the yellows halves constant under an explicit ≤1pp-SD
  rule (was flagged non-frozen by the mechanical `true ≤ 0`
  test despite true variance +0.00002), and rewrote
  MODEL_DESIGN's gate text with separate G/K gates and
  consistent actual−predicted calibration. Coordinator
  recomputed G dev pooled + K dev/virgin LL@3.5 + K virgin
  calibration from the CSVs exactly (G 1.072613/0.230914/
  0.705258; K dev 0.684551/0.693715/0.694791; K virgin
  0.654519 vs naive 0.637606, calib +7.42pp; X2 ≡ GZ in
  2022/23); prereg 74778d9b precedes fitting 7ac1f045;
  results_dev.csv committed by the builder (G 1,620 rows =
  540 × 3 arms; K 540 rows). Counter 141; passing markets
  stay 122. Build lane 5/5 running (AZ, IS-1Deild, PA-LPF,
  MY-LigaSuper, IS-2Deild launched 19:35 as the SCO refill);
  queue head now Bangladesh Football League (10443).
- 2026-11-10 19:37 — **AZ-PremierLeague COMPLETE + MERGED
  (league #142, 4474cf59).** G-AZ **PASSED dev, FAILED virgin
  calibration leg (ii)** — the third dev-pass → virgin-fail
  of the day (after TN #130, ME #138, K-SCO-L1 #141 — fourth
  overall). Dev pooled n=540 (2022/23–2024/25): Gate Zero
  1.011061/0.206623/0.664750 vs climatology 1.081018/0.232482/
  0.693318 — dev gate PASSES all 3 legs; per-row LL columns
  in results_dev.csv agree exactly. SHRINK ≡ Gate Zero (0
  differing predictions; 0 thin-history teams). Virgin
  2025/26 (n=198, read ONCE via `virgin-metrics` only, because
  both arms passed dev; `virgin-predict` was never run — no
  predictions file, no fitted params): 1X2 LL 1.018524 vs
  climatology 1.084067 — leg (i) PASS; calibration HW
  +4.23pp (SE 3.28pp — 0.98 SE beyond the boundary, PROVISIONAL)
  and OU2.5 **−6.29pp (SE 3.68pp — 1.44 SE beyond, FAIL)** —
  leg (ii) FAIL. Nothing ships. Diagnosis: virgin totals miss
  is a level miss in established-team matches (predicted over
  0.432 vs actual 0.519, 2.70 g/m), not an entrant effect
  (entrant-involved matches well calibrated, 0.400 vs 0.413).
  2026/27 (64 matches, in progress) reserved for season-end
  confirmatory read only. S/C/K/T NOT BUILDABLE (preregistered
  Phase A: stats None 914/914, shotmap empty 914/914,
  plain-Yellow events 0 in every season, referee 0/914).
  Corpus: scores-only, but richer than the flags suggested —
  goal events + HT Half markers in 844/914 matches (agree
  844/844 with goal times ≤45) → frozen goals 1H share
  0.4344. One score/event mismatch flagged (match 4946647,
  official 0–3 kept). Format: 2021/22 full 8-team season (112,
  not truncated); 2022/23–2024/25 10 teams × 36 rounds (180
  ea.); **2025/26 expansion to 12 teams × 33 rounds (198)**;
  2026/27 round 2 has only 4/6 matches (2 fixtures absent from
  index). No split group/playoff. Team identity keyed on
  FotMob id: Keshla→Shamakhi FK rename (id 2103), diacritic
  variants from 2026-08-31. EDA: goals/match 2.40–2.64,
  stable; trait reliability unusually strong for a thin league
  (split-half r_GF 0.74–0.89, r_GA 0.66–0.70); all 5 real
  entrants systematically weak (mean GF −0.45, GA +0.25) but no
  entrant arm registered (no sibling league, no independent
  prior). **Defects found and corrected:** (1) **Codex misread
  the virgin LL leg** in its report: it compared virgin LL
  (1.0185) against Gate Zero's *dev* LL (1.0111) and called the
  leg a fail. The prereg compares virgin-window vs
  virgin-window numbers, so the LL leg actually PASSES.
  Corrected in `reports/G_AZ_VERDICT.md` with the reasoning
  documented — outcome unchanged (calibration leg still fails).
  (2) Codex chat claimed team 1H-share split-half n=38; the
  file (`eda_summary.json`) says n=11, r=−0.38 (interleaved
  odd/even split). Verified n=11 independently; also computed
  the chronological-halves variant (r=0.04, n=35); both
  support "no team halves trait". Fixed the EDA.md wording
  before the Phase A commit. Coordinator recomputed dev pooled
  + per-season LL/RPS/OU from per-match results_dev.csv exactly
  (also via the per-row LL columns — identical); prereg
  efe4a2c2 (Phase A) precedes fitting e89c941f;
  results_dev.csv committed by the builder. Virgin metrics
  rest on results_virgin.json + the builder's from-scratch DC
  re-implementation (reproduces the virgin run to 4dp) — no
  virgin predictions CSV exists to recompute from, by design
  (virgin-predict never ran). Counter 142; passing markets
  stay 122. Build lane 5/5 running (IS-1Deild, PA-LPF,
  MY-LigaSuper, IS-2Deild, BD-FootballLeague launched 19:37
  as the AZ refill); queue head now Hungary NB II (9117).
- 2026-11-10 19:46 — **EXTERNAL BATCH 16–19 FOLDED (leagues #143–146):
  SG-PremierLeague, MD-NationalDivision, KW-PremierLeague,
  IN-IndianFootballLeague — all 0 PASS / 1 FAIL / 4 NOT BUILDABLE,
  nothing ships** (merged by Jarvis bc125b70; rows in league/
  EXTERNAL_MERGES.md; coordinator folded at 19:50). **SG #143: G-SG
  FAIL at dev, OU leg** — pooled dev n=364, Gate Zero 1X2 LL 0.9607 /
  RPS 0.2056 beat both baselines but OU2.5 LL 0.5507 vs climatology
  0.5338, loses every dev season; X2 dropped pre-fitting; virgin NOT
  read. K-SG NOT BUILDABLE (plain Yellow events 0 in all 555 matches).
  **MD #144: G-MD PASSED dev, FAILED virgin legs (i) + (ii)** — dev
  pooled Gate Zero 1X2 LL 0.9538 / RPS 0.1869 / OU 0.7040; virgin
  2025/26 (n=114, read ONCE) 1X2 LL 0.8400 / OU 0.7048, OU
  calibration −11.69pp vs climatology 0.6880; X2 best 0.8097/0.6948,
  still fails. **KW #145: G-KW FAIL at dev, OU leg vs climatology
  only** — pooled Gate Zero 1X2 LL 0.9436 / RPS 0.1882 beat both
  baselines, OU2.5 LL 0.7293 vs climatology 0.6806, loses pooled and
  the first three dev seasons; X2 worse pooled (0.9496/0.1899/
  0.7371). K-KW NOT BUILDABLE (Yellow/YellowRed events 0 in the
  entire corpus, only 53 straight Reds). **IN #146: G-IN FAIL at
  dev, 2/6 legs** — pooled Gate Zero 1X2 LL 1.0861 / RPS 0.2337 /
  OU2.5 LL 0.7568 vs climatology 1.0813/0.2365/0.6903 and naive
  1.1344/0.2320/0.7399; OU loses to both baselines; X2 dropped
  pre-fitting. S/C/K/T NOT BUILDABLE in all four (scores-only; K:
  plain Yellow events 0 in dev and virgin for IN). Coordinator
  spot-checked the headline numbers against the merged verdict files
  (KW/IN table rows exact; MD verdict header + virgin-once note
  confirmed). Counter 146; passing markets stay 122. External lane:
  tail assignments 16–19 all delivered; no new external assignments
  pending — Jarvis will announce the next tail batch the same way.
- 2026-11-10 19:50 — **BD-FootballLeague COMPLETE + MERGED (league
  #147, 7b6124fb; branch build/bd-football-league, commits 8ec45b4d /
  a6ea2742 prereg / 5bbe6eed engine / 4263191a verdict — prereg
  before fitting; 25 files).** **0 PASS / 1 FAIL / 4 NOT BUILDABLE.
  G-BD FAIL at dev, OU leg:** pooled n=270 (2023/24–2025/26, seed
  2022/23), Gate Zero 1.048240/0.208447/0.773061 vs climatology
  1.098534/0.233042/0.694650 — wins 1X2 LL + RPS, loses OU2.5 by
  +0.0784, in ALL THREE dev seasons (0.7241 vs 0.6941; 0.8583 vs
  0.6913; 0.7368 vs 0.6985). SHRINK byte-identical to Gate Zero
  (270/270 rows; 0 teams in the 1–5 prior-match band at any target
  start). Virgin 2026/2027 (n=29) deliberately UNREAD — only the
  `{"virgin_read": false}` marker; no predictions file, no fitted
  params. Diagnosis: totals discrimination is noise — predicted
  P(over 2.5) spans 0.24–0.97 but correlates −0.031 with actual
  overs (mean pred 0.517 on overs vs 0.526 on unders); the outcome
  dimension works (home-win corr 0.35; 1X2/RPS legs pass). Fitted
  home advantage h = −0.004: effectively no home edge (dev HW 0.375
  vs AW 0.348). S/C/T/K NOT BUILDABLE (preregistered Phase A: stats
  None + shotmap empty 394/394; K: 0 plain-Yellow events every
  season — only 42 Red + 17 YellowRed; named referees 0/365 in dev).
  Corpus: only 5 seasons; **2022/2023 is incomplete — rounds 4–22
  only (95 matches), rounds 1–3 missing from the warehouse**;
  2023/24–2025/26 complete 10-team double round-robins (90 each);
  **2026/2027 expands to 13 teams** (City Club, Chattogram City new;
  Mohammedan returns), 29 matches, rounds 1–5, one round-4 fixture
  missing from the index. Zero score/event mismatches; HT markers
  394/394, cross-check 363/363. Frozen goals 1H share 0.4217
  (447/1060 dev goals, excess variance −0.0017). Traits reliable (GF
  r 0.53–0.79, GA r 0.70–0.92). Entrants weak, esp. defensively
  (5-entrant mean GF −0.49 / GA +0.93) — descriptive only, no prior
  exists. X1 adopted goals-only; X2–X9 all dropped with reasons in
  FEATURES.md. **Defects / quirks found:** none in the tooling. Data
  quirks (all documented in the analysis docs): incomplete 2022/2023
  seed, 13-team expansion with a missing round-4 fixture, and the CSV
  builder's `has_lineup` column hardcoded False (inherited from the
  AZ template) while payloads do carry 11-starter lineups — noted in
  PREPROCESSING.md, lineups unused as a feature either way.
  Coordinator recomputed pooled LL/RPS/OU from per-match
  results_dev.csv exactly (1.048240/0.208447/0.773061; SHRINK ≡ GZ
  on all 270 rows); prereg a6ea2742 precedes fitting 5bbe6eed;
  results_dev.csv (270 per-match rows) committed by the builder —
  no force-add needed. Counter 147; passing markets stay 122.
  **Build lane refill: Hungary NB II (FotMob 9117, 344) launching
  as the BD refill**; queue head now New Zealand Championship
  (8870, 229). Next milestone 150 — 3 leagues to go.
- 2026-11-10 19:54 — **IS-1Deild COMPLETE + MERGED (league #148,
  8d6a307e; branch build/is-1deild, commits 4e81f307 / b3cd3353
  prereg / eb077d8f engine / 5c580846 verdict — prereg before
  fitting; 27 files).** **0 PASS / 1 FAIL / 4 NOT BUILDABLE.
  G-IS1 FAIL at dev, ALL THREE legs (decisive, not marginal):**
  pooled n=543 (2022–2025, seed 2021), Gate Zero 1.085780/0.243000/
  0.685037 vs climatology 1.063502/0.236163/0.630089 — loses 1X2 LL
  by +0.0223, RPS by +0.0068, OU2.5 LL by +0.0549. SHRINK
  byte-identical to Gate Zero (543/543 rows; 0 lambda diffs).
  X2 (direction-specific mover offsets, adopted, clamped ±log 1.25)
  worse than Gate Zero on all three legs (1.107163/0.246435/
  0.681374) and fails the sign check in 2024–2025 — moot. Virgin
  2026 (n=137, complete) deliberately UNREAD — only the
  `{"virgin_read": false}` marker; no predictions file, no fitted
  params. Corpus: scores-only, 812 payloads (0/812 stats, 0/812
  shotmaps/xG, 0/812 named referees; events 790/812). 12 teams, 22
  rounds; promotion playoff (4 semis + final) introduced 2023,
  included in fit/scoring. Levels hot: goals/match 3.62/3.47/3.59/
  3.18/3.59/3.58; dev OU2.5 over-rate 0.6814. Traits strong (F2
  GF r=0.7987, GA r=0.8196, 24 teams). Frozen goals 1H share
  0.4418; team 1H-share split-half r=−0.0324 (noise). F4 mover
  effects symmetric: Besta entrants GF +0.40 / GA −0.30 (n=10);
  2. Deild entrants GF −0.44 / GA +0.55 (n=11) — yet the clamped
  X2 still fails the gate; offsets saturated at the clamp in both
  active seasons. X1 adopted goals-only; X2 adopted; X3/X4/X6/X7/
  X8/X9 dropped (no data); X5 not applicable standalone. S/C/K/T
  NOT BUILDABLE (preregistered Phase A). **Defects found (all fixed
  pre-commit or non-material, documented in the verdict):** (1)
  harness sign-check rule was stricter than the prereg (folded an
  all-seasons sign rule into the dev gate; prereg: dev gate = three
  metric legs only, sign = virgin leg (iii) at at-least-half) —
  fixed pre-commit; re-run changed only two boolean fields (X2 sign
  now passes 2/4); verdict applies the prereg rule; outcome
  unchanged. (2) Builder's string comparison counted 155 X2 lambda
  diffs vs the harness's 150 — the extra 5 are float noise (~1e-16)
  on same-origin entrant matches; the harness's 1e-12 threshold is
  the honest count. (3) Codex wrote stray duplicates at repo-root
  `engine/` and `analysis/placeholder` — removed before commit.
  (4) Awarded match 3794991 (Selfoss–Grindavik 2022-09-03, played
  5–3, awarded 0–3): `scoreStr` kept as truth; its 4 played 1H
  goals sit in the frozen 0.4418 constant (excluding it gives
  0.4409 — immaterial, noted in EDA.md). (5) Verdict draft error
  caught by the builder's own check: per-season climatology values
  first written from memory — corrected to verified values (2022:
  1.017990, 2023: 1.045390, 2024: 1.115517, 2025: 1.073452).
  Coordinator recomputed all three arms' pooled LL/RPS/OU from
  per-match results_dev.csv exactly (GZ 1.085780/0.243000/0.685037;
  SHRINK ≡ GZ; X2 1.107163/0.246435/0.681374); prereg b3cd3353
  precedes fitting eb077d8f; results_dev.csv (1,629 rows = 543
  matches × 3 arms) committed by the builder. **Audit note:**
  the harness's per-season climatology rows do not reproduce from
  in-season rates (mine: 2022 1.005341, 2024 1.074581, 2025
  1.052339) nor from trailing-prior-season rates (2023 1.048279,
  2024 1.107757, 2025 1.081448) — the exact rate source (seed
  2021? fold training window?) is not pinned in the harness docs.
  The FAIL is robust under every construction I can build (pooled
  rates 1.055455, per-season rates 1.043935, trailing 1.048–1.108,
  harness 1.063502 — model loses all three legs to all of them),
  but the baseline definition belongs on the final-audit list
  (same open item as C-VE / QA-2nd). Counter 148; passing markets
  stay 122. **Build lane refill: New Zealand Championship (FotMob
  8870, 229) launching as the IS-1Deild refill**; queue head now
  Uzbekistan Superliga (540, 215). Next milestone 150 — 2 leagues
  to go.
- 2026-11-10 19:57 — **MY-LigaSuper COMPLETE + MERGED (league #149,
  e82c6932; branch build/my-ligasuper, commits c3d1a0cf Phase A incl.
  prereg / f6924722 engine / 49675c13 verdict — prereg in the Phase A
  commit, before any fitting; 33 files).** **0 PASS / 1 FAIL / 4 NOT
  BUILDABLE. G-MY FAIL at dev, TWO legs:** pooled n=469 (warm-up
  2021, eval 2022/2023/2024-25), Gate Zero 0.952659/0.203229/0.709253
  vs climatology 1.054775/0.237650/0.681050 and naive trailing-10
  1.003148/0.198540/0.768844 — wins 1X2 LL vs both baselines and RPS
  vs climatology, but loses OU2.5 LL to climatology by +0.0282 and
  RPS to naive by +0.0047 (4/6 legs won). Per-season: OU loses to
  clim in 2022 (0.7642 vs 0.6858) and 2023 (0.7034 vs 0.6731),
  wins only 2024/2025 (0.6693 vs 0.6864); the RPS loss to naive is
  driven by 2023 alone (0.1923 vs 0.1774). SHRINK numerically
  identical to Gate Zero on all 469 rows (the 1–5 prior-match band
  never occurs). Virgin 2025/2026 (n=156, complete) deliberately
  UNREAD — only the `{"virgin_read": false}` marker; 2026/2027
  partial (n=35) untouched as confirmatory reserve. Diagnosis:
  Gate Zero systematically under-predicts overs — mean P(over 2.5)
  0.5176 vs actual 0.5885 (−7.08pp), worst in 2022 (−12.22pp) and
  2023 (−9.30pp), absent in 2024/2025 (−0.11pp); the expanding fit
  lags a rising-goals era (2.70 → 2.94 → 3.43 → 3.05 goals/match).
  S/C/K/T NOT BUILDABLE (preregistered Phase A: stats null +
  shotmap empty 793/793; K: plain Yellow events 0 — only Red 88 +
  YellowRed 39; referee named 0/793). Corpus: single double
  round-robin, no split/playoff — 12 teams 2021–22, 14 in 2023 (26
  rounds × 7; the 182-count is a team-count change, not a format
  split), 13 in 2024/25–2025/26. 2023 is a whole calendar-year
  season, never split across windows. Team identity by FotMob id
  (name aliases: Kelantan United id 1124836 → Kelantan DNFC/TRW;
  Imigresen FC id 1783759 → Star City). One awarded match 4480811
  (JDT 3–0 Selangor, 2024-05-10) excluded from fit/score. Goal
  events = scores in 792/792 non-awarded matches; HT cross-check
  759/759. Frozen goals 1H share 0.4534 (1125/2481; obs var
  0.097829 vs binomial noise 0.105540, true var 0). Split-half
  traits strong: GF r=0.8381, GA r=0.7715 (dev window, 39
  team-seasons). No Malaysian sibling league exists → no X2 mover
  prior. Fitted h/rho per season: 2022: 0.2139/−0.15; 2023:
  0.3851/0.00; 2024/2025: 0.2630/0.00. **Defect found and fixed:**
  Codex's SHRINK bucket diagnostic counted training-window teams
  that never play the target season (e.g. Perak, UiTM), reporting
  (2,0,12,0)/(4,0,4,10)/(0,0,6,12) vs frozen (2,0,10,0)/(4,0,2,8)/
  (0,0,3,10) — diagnostic-only: fixed to count target-season teams,
  re-ran, `results_dev.csv` byte-identical (md5 937fea76…),
  `fitted_params_dev.json` byte-identical, counts now match the
  prereg exactly. Coordinator recomputed pooled LL/RPS/OU for all
  four arms from per-match results_dev.csv exactly (GZ 0.952659/
  0.203229/0.709253; SHRINK ≡ GZ 469/469; clim 1.054775/0.237650/
  0.681050; naive RPS 0.198540 + OU 0.768844 exact); prereg
  c3d1a0cf precedes fitting f6924722; results_dev.csv (469
  per-match rows) committed by the builder. **Audit note:** the
  naive trailing-10 assigns P=0 on 5 rows (SLO degenerate edge,
  same class as the SLO-L1 note) — its LL depends on the harness's
  epsilon choice (eps 1e-6 → 0.9737, 1e-9 → 0.9884, json 1.0031);
  the RPS and OU legs are epsilon-independent and the verdict does
  not depend on naive LL. Counter 149; passing markets stay 122.
  **Build lane refill: Uzbekistan Superliga (FotMob 540, 215)
  launching as the MY refill**; queue head now Faroe Islands
  Løgmanssteypið (9523, 6 — cup, assess buildability). **Next
  milestone 150 — 1 league to go.**
- 2026-11-10 20:01 — **🎉 MILESTONE #6 — 150 LEAGUES COMPLETE.**
  Leagues 126–150: CY-2Division 0/1/4 · UY-SegundaDivision 0/1/4 ·
  WAL-CymruPremier 0/1/4 · HN-LigaNacional 0/1/4 · TN-LigueI 0/1/4 ·
  LT-Toplyga 0/1/4 · **KZ-PremierLeague 1 PASS provisional (G-KZ
  Gate Zero) / 4 NB** · **BA-PremierLeague 1 PASS provisional (G-BA
  Gate Zero) / 4 NB** · IE-FirstDivision 0/1/4 · MK-PrvaLiga 0/1/4 ·
  VN-VLeague 0/1/4 · AL-KategoriaSuperiore 0/1/4 · ME-1CFL 0/1/4 ·
  AM-PremierLeague 0/1/4 · SLO-PrvaLiga 0/1/4 · SCO-LeagueOne
  0/2/3 · AZ-PremierLeague 0/1/4 · SG-PremierLeague (ext) 0/1/4 ·
  MD-NationalDivision (ext) 0/1/4 · KW-PremierLeague (ext) 0/1/4 ·
  IN-IndianFootballLeague (ext) 0/1/4 · BD-FootballLeague 0/1/4 ·
  IS-1Deild 0/1/4 · MY-LigaSuper 0/1/4 · IS-2Deild 0/1/4.
  **Block tally (125 candidates): 2 PASS (both provisional goals:
  G-KZ, G-BA) / 24 FAIL / 99 NOT BUILDABLE.** Passing markets
  program-wide 122 (KZ + BA are the only two passes in the block);
  runner 43 leagues / 96 markets. Every league in the block is a
  scores-only goals FAIL except the two provisional goals passes —
  the OU2.5 calibration/totals leg remains the program-wide goals
  killer (dev OU leg in 20 of the 24 fails; virgin-calibration
  fails in TN, ME, AZ, K-SCO-L1, MD). Milestones reported = 6;
  next at 175.
- 2026-11-10 20:01 — **IS-2Deild COMPLETE + MERGED (league #150,
  0cbdad69; branch build/is-2deild, commits 271c2123 Phase A incl.
  prereg / aca3cb4a engine / ca468b88 verdict — prereg before
  fitting; 27 files).** **0 PASS / 1 FAIL / 4 NOT BUILDABLE.
  G-IS2 FAIL at dev, ALL THREE legs:** pooled n=528 (2022–2025,
  seed 2021), Gate Zero 1.066661/0.241576/0.662205 vs climatology
  1.037573/0.236529/0.615360 — loses 1X2 LL by +0.0291, RPS by
  +0.0050, OU2.5 LL by +0.0468. Gate Zero beats climatology on 1X2
  LL in only 1 of 4 dev seasons (2024). SHRINK 1.066783/0.241467/
  0.667660 and X2 1.065650/0.240198/0.669252 — both also lose to
  climatology on every leg (moot, not virgin-read). Note: SHRINK
  DOES bite here (134/528 lambda diffs vs Gate Zero per the
  harness diagnostics) yet still loses — unlike the usual
  SHRINK ≡ GZ pattern. Virgin 2026 (n=137, complete) deliberately
  UNREAD — only the `{"virgin_read": false}` marker; no predictions
  file, no fitted params. Corpus: 776 played matches (2021: 116 +
  16 never-played `Data not found` placeholders excluded; 2022–
  2026: 132 each, plain double round robin, no split/playoff; 2026
  complete). Scores-only: `content.stats` None + shotmap empty in
  all 776 payloads, referee empty in all 776, only 145 sporadic
  Card events (~0.19/match). Goals 3.42–3.89/match; dev OU2.5
  over-rate 69.51%. Frozen 1H goals share 0.4418 (true variance
  −0.00106, below the binomial noise floor). X2 mover priors
  measured from warehouse payloads: relegated-from-1.Deild
  arrivals dGF +0.11 / dGA −0.20 (n=10), from-below arrivals
  −0.31 / +0.25 (n=12); no club ever arrives directly from Besta
  deildin. F2 split-half r 0.402/0.370 (modest reliability).
  S/C/K/T NOT BUILDABLE (preregistered Phase A: no SOT/corners/
  shots stats, no usable cards target). **Defects / incidents
  found:** (1) Codex CLI first invocation crashed (stderr EAGAIN
  panic after ~26s, zero files written) when the full 14 KB brief
  was passed inline via `$(cat ...)` — retried with a short pointer
  prompt to the brief file, worked. (2) Runtime restart lost the
  Phase B Codex session (proc_93e53f138a9d, no confirmed result),
  but all engine/dev files had already landed; the builder verified
  and replayed them rather than re-running Codex. (3) Besta's
  `build_data.py` reads goal events from `matchFacts.events` —
  wrong for this league (goals live in `header.events`); this
  builder uses `header.events` with an assert (event count == FT
  goals, 0 mismatches). Also Besta's `dc.py` docstring says "G-J1"
  (copy drift); this one says G-IS2. (4) Data quirks (documented,
  not bugs): team identity must be by FotMob id — id 163250 "IR
  Reykjavik"/"ÍR Reykjavík" and id 4515 "Vikingur Olafsvik"/
  "Víkingur Olafsvik"; 2026 Magni hosts KFG twice (rounds 3 + 14),
  reverse fixture absent. IS-1Deild's config was not on main at
  build time, so mover classification was measured from warehouse
  payloads (leagues 215/216/10226), not from the in-flight build.
  Coordinator recomputed all three arms' pooled LL/RPS/OU from
  per-match results_dev.csv exactly (GZ 1.066661/0.241576/0.662205;
  SHRINK 1.066783/0.241467/0.667660; X2 1.065650/0.240198/0.669252)
  and the harness pooled climatology as the n-weighted mean of its
  per-season rows (1.037573/0.236529/0.615360 — exact); prereg
  271c2123 precedes fitting aca3cb4a; results_dev.csv (528
  per-match rows) committed by the builder. **Audit note:** the
  harness per-season climatology again does not reproduce from
  in-season rates (mine pooled 1.028298 vs harness 1.037573 —
  same open baseline-definition item as IS-1Deild); the FAIL is
  robust under both constructions. Counter 150; passing markets
  stay 122. **Build lane refill: Faroe Islands Løgmanssteypið
  (FotMob 9523, 6) launching as the IS-2Deild refill — the LAST
  league in the local queue.** Next milestone 175 — 25 leagues
  to go.
- 2026-11-10 20:08 — **FO-Logmanssteypid COMPLETE + MERGED (league
  #151, 96db67e0; branch build/fo-logmanssteypid, commits 50fe17d6
  feasibility prereg / 46cee3ff verdict — prereg before any fitting,
  and NO fitting was done at all; 17 files).** **0 PASS / 0 FAIL /
  5 NOT BUILDABLE — the third 0/0/5 league in the program** (after
  CO-Superliga and AU-Championship). **No gate could be run:** the
  warehouse holds exactly one match per year, and every payload's
  `general` confirms `matchRound`/`leagueRoundName: "final"`,
  `leagueName: "Cup"` — the Løgmanssteypið is a single-match cup
  final, not a league. Scores 6/6 (11 goals, mean 1.83; H2 D3 A1;
  Over 2.5 1/6; BTTS 2/6); `content.stats` 0/6, shotmap shots 0/6,
  events feed empty in 6/6 (0 events of any type — not even goal
  minutes), referee 0/6, lineup 0/6. Three of six finals went
  straight to penalties (2021, 2023, 2024); no extra time anywhere.
  Virgin 2026 is n=1: calibration SE ≈37pp at OU 2.5 (50pp at
  p=0.5) vs the 1pp clean-PASS threshold; pooled n=6 still ≈15.2pp.
  **Virgin deliberately NOT read** — no arm passes (or can pass) a
  dev gate; the not-read state is recorded in
  `reports/results_virgin.json` (`{"virgin_read": false, "reason":
  "not_buildable_no_window", ...}` — note: the marker lives in
  `reports/`, not `engine/goals/`, because no engine exists).
  No `results_dev.csv` exists because no dev was scored (none could
  be). No engine, no fitted params, no predictions, no halves
  constants (no 1H splits exist anywhere). X1–X9 all DROPPED.
  **Scope check done as briefed:** the warehouse holds exactly two
  Faroese competitions — Løgmanssteypið (9523, 6 rows) and Premier
  League (250, 810 rows); no cup rounds hide under another id;
  scope was not widened. Borrowing Premier League ratings was
  considered and rejected (same grounds as CO-Superliga's Primera A
  transfer: unvalidatable in-competition, would be a Premier League
  model wearing a cup label). Revisit condition: none scheduled — at
  1 match/year it will not reach a gateable sample; any pooled
  cross-cup design would need a fresh prereg outside the per-league
  gates. **Defects / corrections found:** (1) Brief scouting error
  (minor): the brief said index team names were NULL — they are
  populated on all 6 index rows and agree with the payloads.
  Recorded in DATA_UNDERSTANDING and LEAGUE_VERDICT. (2) Team-name
  spelling inconsistency in the warehouse: "B36 Torshavn" vs "B36
  Tórshavn", "Vikingur" vs "Víkingur" — distinct clubs are 6 after
  accent normalisation, 8 raw. Recorded; CSV keeps per-row spelling.
  (3) Index flags agree with payloads here (unlike CO-Superliga):
  `has_stats`/`has_shotmap` False on 6/6 is genuine — the
  competition really is scores-only. **Process note:** the builder
  did not route this through Codex — no code-heavy work; the
  deliverable is 12 short docs plus a 70-line builder adapted from
  the CO-Superliga precedent, written directly and verified by
  recomputing every headline number from the payloads through two
  independent paths (payload inspection + generated CSV).
  Coordinator verified the branch (prereg 50fe17d6 precedes verdict
  46cee3ff; no fitting anywhere; marker present; no dev/virgin
  artifacts) and confirmed from the warehouse index that exactly
  two Faroese competitions exist (250: 810 rows; 9523: 6 rows).
  Counter 151; passing markets stay 122. **⚠️ QUEUE CORRECTION
  (same heartbeat): Faroe Islands Premier League (FotMob 250, 810)
  was found UNBUILT — queue head at 19:32, skipped at the 19:34
  refill with no reason recorded. It launches NOW as the true last
  local league; the local queue is exhausted only after it.**
- 2026-11-10 20:19 — **HU-NBII COMPLETE + MERGED (league #152,
  c3d6daa2; branch build/hu-nbii, commits 4f62812e prereg /
  36cf5ace data + steps 1–6 / 44f04532 verdicts — prereg before any
  analysis; 21 files).** **0 PASS / 0 FAIL / 5 NOT BUILDABLE — the
  fourth 0/0/5 league in the program** (after CO-Superliga,
  AU-Championship, FO-Logmanssteypid). **Decisive defect, payload-
  verified: the brief's "2025/26 complete (240 rows)" is wrong —
  only 96/240 (40%) are genuine final scores.** The rest: 103 rows
  have no `scoreStr` (rounds 4–23 almost entirely) — pre-match
  fetches recorded as `0-0` in the index, not genuine 0-0s; 41 rows
  have a `scoreStr` but `finished=False`, no `gameEnded` /
  `secondHalfEnded`, last timed event median minute 45 (max 70),
  averaging 0.805 goals/match (round 8: 0.286) — mid-match captures,
  i.e. partial scores, excluded as contamination. Genuine data: 200
  matches, 533 goals, 2.665/match — 2025/26 n=96, 2.417 g/m, OU2.5
  44.8% (SE 5.1pp); 2026/27 n=104, 2.894 g/m, OU2.5 55.8% (SE
  4.9pp); pooled OU2.5 SE 3.5pp — 3–5× the 1pp clean-PASS
  threshold. **No complete season exists, so season-blocked dev is
  impossible and no gate could be run.** Stats/shotmap/period-
  splits/referee absent 344/344 (keys present as empty skeletons);
  47 card events / 344 matches, referee blank 344/344; shotmap
  empty 344/344. 1H goal share 234/533 = 0.439 (n=189 finished
  matches with Half marker, no constants frozen); split-half team
  GF/game r = 0.075 / 0.186 (noise). X1–X9 all DROPPED. X2 mover
  evidence exists (Diósgyőri VTK + Kazincbarcikai BSC relegated
  down, Vasas Budapest promoted up) but is moot with n=3 movers
  and no window; sibling HU-NBI's G candidate FAILED its dev gate,
  and cross-tier pooling was rejected. **Virgin deliberately NOT
  read** — no arm passed (or could pass) a dev gate; 2026/27 was
  tallied at inventory level only. Not-read marker in
  `league/HU-NBII/results_virgin.json` (`{"virgin_read": false,
  ...}`). No `results_dev.csv` — no dev was run (none could be);
  no engine, no fitted params, no predictions. Revisit: dev on
  2025/26+2026/27 once both complete **and re-fetched** with
  genuine scores, virgin 2027/28, fresh prereg required — nothing
  scheduled. **Defects / corrections:** (1) DATA_UNDERSTANDING
  said "eight" finished matches with empty `gameEnded` but
  populated `secondHalfEnded` — true count is nine (plus one
  finished 0-0 with neither marker, correctly counted); builder
  fixed before committing. (2) Split-half r corrected to 0.075/
  0.186 (brief's approximate 0.10/0.25) and 1H share to 0.439
  finished-only (not 0.436 on all scoreStr rows). **Coordinator
  verification:** branch order clean (prereg 4f62812e precedes
  analysis 36cf5ace and verdicts 44f04532); marker present; no dev
  artifacts; merge c3d6daa2 clean (21 files, HU-NBII only). The
  contamination counts were spot-verified independently from the
  warehouse payloads (`header.status.scoreStr`/`finished`):
  2025/26 = 96 finished+scoreStr / 41 scoreStr-but-unfinished /
  103 no scoreStr; 2026/27 = 104/104 finished — exact match to
  the builder's numbers. **Final-audit item:** the warehouse index
  row-count (240) for an in-progress season silently mixes
  pre-match placeholders and mid-match partials with finals —
  any future brief that calls a season "complete" must be checked
  against `finished` + `scoreStr` in the payloads, not the index
  row count. Counter 152; passing markets stay 122. Builds in
  flight now 4/5 (PA, NZ, UZ, FO-Premier); local queue exhausted
  after Faroe Premier. Next milestone 175 (23 to go).
- 2026-11-10 20:22 — **UZ-Superliga COMPLETE + MERGED (league #153,
  c84853bd; branch build/uz-superliga, commits 1c349d3a data +
  descriptive EDA / c229d579 prereg / 0b3980a2 analysis + verdicts;
  23 files).** **0 PASS / 0 FAIL / 5 NOT BUILDABLE — the fifth
  0/0/5 league in the program** (after CO-Superliga, AU-Championship,
  FO-Logmanssteypid, HU-NBII). **One partial season only:** 2026,
  215/240 matches, rounds 1–27, 2026-02-27..2026-11-08, in progress;
  round 26 short one fixture (Bunyodkor Tashkent vs Neftchi
  Fargona); rounds 28–30 unplayed. Zero complete seasons → no
  season-blocked dev, no virgin season. Thinner than the
  AU-Championship precedent (one complete season, 0/0/5).
  Hypothetical OU 2.5 calibration SE on n=215 would be ~3.4pp vs
  the 1pp clean-PASS threshold. **Scores-only:** stats null 215/215,
  shotmap empty 215/215, lineups null, referee blank 215/215, no
  structured period splits. No Uzbek sibling league exists (540 is
  the only Uzbekistan id) → no X2 mover prior. Levels (descriptive
  only): 565 goals, 2.628/match (J1 2.55); home 1.391 / away 1.237;
  HW/D/AW 89/50/76 (41.4/23.3/35.3%); Over 2.5 53.5%; BTTS 56.3%.
  Split-half within 2026 (rounds 1–13 vs 14–27, n=16): attack
  GF/match r=0.696, defence GA/match r=0.179. X1–X9 all DROPPED; no
  halves constant frozen. **Virgin deliberately NOT read** — no arm
  passed (or could pass) a dev gate; 2026 tallied at inventory
  level only. Not-read marker in `reports/results_virgin.json`
  (`{"virgin_read": false, "dev_scored": false, ...}` — note: marker
  lives in `reports/`, as in FO-Logmanssteypid). No
  `results_dev.csv` — no dev was scored; no engine, no fitted
  params, no predictions. Revisit: earliest gateable build is dev
  on 2026 (once complete) + 2027, virgin 2028 — fresh prereg
  required, nothing scheduled. **Notable finding:** the brief missed
  the event feed — `matchFacts.events` is non-empty in 99/215
  payloads (rounds 10, 14–27), carrying a Half event at 45' giving
  the HT score (99/99 consistent, 0≤HT≤FT) and Goal events matching
  FT totals (99/99). HT share of goals = 0.4588 (128/279). Builder
  added validated HT columns to the CSV/builder and a
  `halftime_share` EDA section — descriptive only, **not frozen**
  (late-season-only coverage). Cards remain unusable (29 Card events
  in 99 matches). **Defects / corrections:** Codex used J1
  goals/match 2.68 and admitted J1 EDA.md "does not state 2.68" —
  correct value from J1's EDA levels table is **2.55** (pooled,
  n=2,091); builder fixed in `eda.py`, `eda_summary.json`, and the
  regenerated `result_mix_vs_j1.png`. **Process deviation (no gate
  impact):** the prereg commit (c229d579) came AFTER the descriptive
  EDA commit (1c349d3a) — unlike HU-NBII, whose prereg was first.
  The prereg-before-fitting rule still holds in substance: no
  fitting of any kind exists anywhere in the branch (coordinator
  grep-checked the first commit for fitted/ridge/Poisson code —
  none; no engine, no dev scored), and the prereg precedes the
  verdicts. Recorded as a final-audit item: prereg must be the
  FIRST commit even for not-buildable leagues. **Coordinator
  verification:** index confirms 215 rows, all season 2026; branch
  files complete (23 files, UZ only); merge c84853bd clean. Counter
  153; passing markets stay 122. Builds in flight now 3/5 (PA, NZ,
  FO-Premier); local queue exhausted after Faroe Premier. Next
  milestone 175 (22 to go).
- 2026-11-10 20:24 — **NZ-Championship COMPLETE + MERGED (league
  #154, 277c7ff9; branch build/nz-championship, commits 18a957f0
  Phase A / 1238af2d prereg / 5de28ce2 engine + dev / 5c81fbd7
  verdict; 25 files).** **0 PASS / 1 FAIL / 4 NOT BUILDABLE.**
  G-NZ Gate Zero **FAILS dev, all 3 legs, pooled n=92 (2023–2024):
  1X2 LL 1.127229 vs climatology 1.057336; RPS 0.263013 vs 0.250859;
  OU2.5 LL 0.598031 vs frozen base-rate 0.562335.** SHRINK is
  bit-identical to Gate Zero (0 lambda diffs both seasons) and
  fails identically; sign check 2/2 on ties, moot. Per-season
  split: 2023 passes all legs (LL 0.969155 vs 1.054884); 2024 fails
  all badly (LL 1.285303 vs 1.059789) and sinks the pooled gate.
  Diagnosis: model is home-tilted and goal-shy vs reality in both
  seasons (2024 predicted AW 0.383 vs actual 0.435, OU2.5 0.647 vs
  0.761) — team traits barely replicate here (split-half GF
  r=0.2293, GA r=0.2570). S/C/K/T NOT BUILDABLE (prereg, Phase A).
  **Virgin deliberately NOT read** — Gate Zero failed dev (frozen
  rule); marker in `engine/goals/results_virgin.json`
  (`{"virgin_read": false, "virgin_season": "2025", ...}`).
  Per-match dev predictions committed in
  `engine/goals/results_dev.csv` (184 rows = 92 matches × 2 arms,
  force-added past the `*.csv` gitignore). League facts: 221 played
  matches from 229 index rows — **8 unplayed 2022 fixtures**
  (finished=false, index `0-0` is a placeholder) excluded; seed
  2022 is 38 matches, not 46. 10 teams 2022–24, 11 teams 2025–26,
  single round robin + one final; 2025's +10 is the 11th team, not
  a playoff. Scores-only: stats 0/221, shotmaps present-but-empty
  221/221, lineups 0/221, referees 0/221; 2022 event blackout; only
  Red/YellowRed card events (34), no plain Yellow. 2024/2025 finals
  stored at 90-min 1-1 (ET goals excluded, event-derived). Levels
  3.41–4.13 goals/match; 1H share frozen 0.4123 (observed variance
  below binomial noise floor); dev OU2.5 over-rate frozen 0.75
  (69/92). No NZ sibling league → no X2 arm. X1 adopted
  goals-only; X2–X9 dropped with reasons. **Defects / corrections:**
  (1) The Phase A brief counted 229 rows as played — the 8
  unplayed 2022 fixtures and their phantom 0-0s inflated the
  brief's 2022 levels (3.24 vs true 3.92); builder caught it via
  the finished-filter; all docs/prereg carry corrected numbers.
  (2) Codex's first builder draft inverted the ET rule (`recorded
  if et`) — caught in diff review before any run, fixed to 90-min
  scores. (3) Codex's `eda.py` shipped with a syntax error
  (unclosed dict) — fixed with one `}`. (4) Codex's chat table
  mis-transcribed 2024 climatology RPS by 3e-10; JSON + independent
  recompute agree. (5) Codex Phase A run had to be killed mid-way
  (looping on the brief's own wrong assertion); builder finished
  Phase A docs/charts directly. **Process deviation (no gate
  impact, same as UZ):** Phase A analysis commit (18a957f0) precedes
  the prereg commit (1238af2d); prereg still precedes all fitting
  (engine commit 5de28ce2) — recorded as a final-audit item (prereg
  must be the FIRST commit). **Coordinator verification:** recomputed
  all pooled legs independently from `results_dev.csv` — LL
  1.127229, RPS 0.263013 (with the standard 1/(K−1) normalisation),
  OU LL 0.598031, over-rate 0.7500, per-season LLs 0.969155 /
  1.285303 — all exact; probs sum to 1; SHRINK lambdas identical;
  seasons 2023/2024 only, no virgin leak. Index confirms 229 rows
  (46/46/46/56/35 by season 2022–2026). Merge 277c7ff9 clean (25
  files, NZ only). Counter 154; passing markets stay 122. Builds in
  flight now 2/5 (PA, FO-Premier); local queue exhausted after
  Faroe Premier. Next milestone 175 (21 to go).
- 2026-11-10 20:36 — **FO-PremierLeague COMPLETE + MERGED (league
  #155, d0a30bc6; branch build/fo-premier-league, commits 263c0e84
  Phase A / 4c162d84 prereg / c6dd5584 engines + dev / 65b93006
  verdicts; 39 files).** **0 PASS / 2 FAIL / 3 NOT BUILDABLE — the
  LAST local league; the local queue is now exhausted.** G-FO goals
  (DC goals-only; Gate Zero + SHRINK ×0.85) **FAILS dev, pooled
  n=539 (2022–2025): 1X2 LL 0.8080 / RPS 0.1633 / OU2.5 LL 0.6602
  vs climatology 1.0239 / 0.2426 / 0.6458 — wins the 1X2 legs by a
  wide margin but loses the OU2.5 leg.** SHRINK also fails (OU2.5
  0.6688). K-FO cards (unified yellows, line 3.5; Gate Zero K=8 +
  SHRINK K=16) **FAILS dev: LL@3.5 Gate Zero 0.6847, SHRINK 0.6810,
  base rate 0.6824, naive 0.6930 — Gate Zero doesn't beat the base
  rate. SHRINK passes its own dev gate but is moot per the frozen
  rule (Gate Zero fails dev ⇒ variants moot)** — second occurrence
  of the TZ SHRINK fork, same handling, no action. S/C/T NOT
  BUILDABLE (no SOT/corners/shots data anywhere). **Virgin NOT read
  for either candidate** — G-FO: no arm passed dev; K-FO: frozen
  rule blocks SHRINK's virgin read. Markers
  (`{"virgin_read": false, ...}`) committed in both engine dirs.
  No predictions CSV exists by design — writing one would itself
  be a virgin read. Nothing ships; no engine joins the daily
  pipeline. League facts: 810 index rows, 2021–2026, 135/season,
  10 teams × 27 rounds (triple round robin); 809 played matches
  after excluding one awarded match (3822183, official 0-3 AW vs
  played 3-1). Scores-only: stats 0/810, shotmap 0/810, referee
  text empty 810/810. Cards and HT scores derivable from events
  (HT marker 810/810). Levels: goals 3.30/match, yellows
  3.94/match, 1H shares 0.441 (goals) / 0.348 (yellows, true
  variance ≈0.0011 ≈ noise), team-trait split-half r 0.88/0.93
  (goals) and 0.87/0.85 (yellows). X2 dropped (no feeder tier in
  warehouse); X3–X9 dropped (no stats/shotmap/referee).
  **Defects / corrections:** (1) Codex's `build_data.py` counted
  Yellow-only in `yellow_*` (mean 3.844 vs correct unified 3.937)
  — fixed: `yellow_*` = Yellow+YellowRed; CSV rebuilt and
  re-verified per-season. (2) Codex's EDA.md swapped totals and 1H
  counts ("2,669 of 6,051" goals; "3,185 first-half yellows") —
  fixed to 1,178/2,669 goals and 1,107/3,185 yellows. (3) Builder's
  own first draft of the K verdict table carried four unverified
  per-season LL@4.5 cells and six unverified mean_p cells — caught
  by re-checking against `results_dev.json` and corrected before
  commit. (4) Cosmetic wart (not a bug, noted in the K verdict):
  the cards CSV rebuild loop `break`s after Gate Zero when filling
  base/naive columns — harmless because base/naive means and r are
  arm-independent (verified: base r=500, naive r=66.37 under both
  arms). **Coordinator verification:** recomputed all pooled legs
  independently from the per-match `results_dev.csv` files (539
  rows each, wide format, one row/match with per-arm columns,
  seasons 2022–2025 only, no 2026 rows) — goals GZ 0.808023 /
  0.163256 / 0.660229, SHRINK 0.808353 / 0.163847 / 0.668773,
  climatology 1.023901 / 0.242594 / 0.645834; cards Bernoulli
  LL@3.5 GZ 0.684736 / SHRINK 0.681000 / base 0.682420 / naive
  0.693044 — all exact to 4–6dp; probs sum to 1. Commit order
  clean (prereg 4c162d84 precedes engines c6dd5584 — unlike the
  UZ/NZ deviation). Merge d0a30bc6 clean (39 files, FO only).
  Counter 155; passing markets stay 122. **Local lane now: 1 build
  in flight (Panama LPF 9039) + 2 joins (NO-OBOS corners,
  SE-Superettan cards); no local leagues remain to launch.** Next
  milestone 175 (20 to go).
- 2026-11-10 20:54 — **NO-OBOSLigaen corners JOINED the daily runner
  (runner 44/97)** (merged 6d0d3c51; branch build/runner-no-obos,
  tip 71943d74 — single commit, ONLY league/runner/{README.md,
  active.yaml}, +19 lines; no run_daily.py change, no build_data.py
  change). Market: corners gate_zero 10.5 PROVISIONAL PASS (virgin
  LL 0.6898 at primary 10.5, calibration +1.14pp with the 0.14pp
  excess over the 1.0pp boundary within 1 SE of 3.24pp; dev LL
  0.6969 beat both baselines, league base rate 0.7257 and naive
  trailing-10 0.7205; Gate Zero and PLAIN tied exactly on virgin —
  the virgin fit chose beta [0.0], so the possession multiplier is
  inactive and the frozen tie rule ships the simpler arm, Gate
  Zero). Goals/SOT/cards/total shots FAILed or not buildable —
  excluded. Corners config: primary 10.5, ladder 9.5/10.5/11.5,
  `halves_share_1h: null` — FT-only (no period splits in the feed;
  RU-1Division precedent). **Merge note:** the branch base
  (e892d0d6, runner 42/94 era) predated the CY join, so both
  runner files conflicted; resolved per practice — HEAD's
  active.yaml + the NO-OBOS block appended verbatim, README
  concatenated (CY paragraph kept, NO-OBOS paragraph appended);
  merged counts verified by YAML parse: 44 leagues / 97 markets,
  CY intact (corners + total_shots). **Merged-state verification
  (coordinator, from the main checkout):** one-league NO-OBOS run
  (`~/workspace/runner-checks/run_one_league_noobos.py`, venv,
  MALLOC_ARENA_MAX=2) — rebuild 1,440 matches / 2,880 team rows
  (byte-identical to the build worktree's CSVs per the builder),
  upcoming 0, pull_errors [], corners predicted 0, settled 0 —
  reproduces the branch proof's NO-OBOS outputs (header-only daily
  CSV, empty ledger). The 2026 season ended 2026-11-08 and 2027 is
  not requested, so nothing was predicted. Branch proofs: two full
  runs (43 leagues; 92 markets run 1, 95 run 2 — on the pre-CY
  base), each 11,957 predictions; run 2 fetched_new=0 everywhere,
  0 errors; 363/366 files bit-identical. Exceptions, all explained:
  ZA-PSL corners daily (FT values bit-equal to run 1's ledger on
  all 160 fixtures — delta confined to non-ledger fields, as
  documented for that league); BR-SerieB corners + SOT daily on
  ONE fixture, 5190810 — FotMob rescheduled it 2026-11-14 →
  2026-11-12 between the pulls (SOT exp_total 8.48895 → 8.48875,
  p_over shifts ≤0.000013, no side flip; corners mu 1.4e-14);
  CO-PrimeraA's 6 files exist only in run 2 (first-ever outputs).
  Replay diffs: FIT exact (core.fit_params on 2021–2025 reproduces
  fitted_params_virgin.json bit-for-bit — gamma 0.15, r
  1.165312214160854, beta [0.0], fit_n 1,080); APPLY exact (real
  run_daily.predict_corners over 237 fixtures / 66 dates, max diff
  0.0 on mu and all ladder lines; halves empty — FT-only
  confirmed). Live-refit diagnostic: production refit on full
  history keeps gamma 0.15 / beta [0.0], r 1.16719 (fit_n 1,317);
  predictions on virgin fixtures differ ≤0.0002 in p_over —
  by-design daily refit, not a defect. Synthetic settlement on
  match 5105318 (Sandnes Ulf–Åsane, 2026-11-08), corners actual 15:
  live prediction exp 11.0629, P(over 10.5) 0.5379, chosen over,
  hit, log loss 0.62; settled exactly once. **Defects / findings:**
  (1) **CO-PrimeraA fails in a fresh worktree (pre-existing, not
  caused by this join):** its builder also reads Primera B
  warehouse JSONs, which no runner league pulls — run 1 died with
  FileNotFoundError (Colombia/Primera B/2021/3511732.json); fixed
  environmentally by copying Primera B (49 MB, 1,773 files) from
  the main checkout's warehouse, no code change; CO then rebuilt
  (2,583 rows) and predicted cleanly in run 2. Recorded as a
  final-audit item: runner fragility — a league builder depending
  on a sibling league's warehouse files that the runner never
  pulls. (2) Proof took 4 launches: run 2 attempt 1 cut by a
  service restart after J1+DK, attempt 2 OOM-killed (exit 137) at
  the AR stage under heavy parallel load, attempt 3 completed.
  (3) Builder's first active.yaml edit matched the first
  occurrence of a repeated ladder block and inserted mid-file —
  caught and moved to the end immediately; final diff verified as
  a pure append. Join lane now 2/2 (SE-Superettan cards in flight
  + US-USLLeagueOne launching); next in queue FI-Veikkausliiga.
- 2026-11-10 21:16 — **SE-Superettan cards JOINED the daily runner
  (runner 45/98)** (merged 68cbdcf4; branch build/runner-se-superettan,
  tip 412cf1ae — single commit, ONLY league/runner/{README.md,
  active.yaml}, +101 lines; no run_daily.py change, no build_data.py
  change). Market: cards gate_zero 3.5 PROVISIONAL PASS (virgin
  LL@3.5 0.667511 vs league base 0.682322; calibration +3.77pp,
  breach within 1 SE of 3.14pp; dev gate LL 0.672526 vs base
  0.690891). Goals/SOT/corners/total shots FAILed — excluded
  (corners C-SE2 passed dev and virgin leg (i) but died on virgin
  leg (ii) calibration −6.63pp). Config: primary 3.5, ladder
  2.5/3.5/4.5, halves yellows share 0.3344, plus the `cards_actual:
  [yellow_home, yellow_away]` opt-in (NO/KR pattern) — REQUIRED,
  not optional: the default settle actuals (`yellow_cards_home` /
  `yellow_cards_away`) are empty on all 1,440 rows (stats feed has
  no card keys), so the default path would settle nothing; the
  league CSV's `yellow_home`/`yellow_away` already carry the
  event-derived unified yellows. 1H/2H p_over ladders use the runner
  defaults (0.5/1.5/2.5 and 1.5/2.5/3.5), same values NO/KR
  configure explicitly. **Merge note:** the branch base (3a1eb828,
  CY merge, runner 43/96) predated the NO-OBOS join, so both runner
  files conflicted; resolved per practice — HEAD's files + the SE2
  additions appended verbatim; merged counts verified by YAML
  parse: 45 leagues / 98 markets, NO-OBOS intact. **Merged-state
  verification (coordinator, from the main checkout):** one-league
  SE2 run (`~/workspace/runner-checks/run_one_league_se2.py`, venv,
  MALLOC_ARENA_MAX=2) — rebuild 1,440 matches / 2,880 team rows,
  upcoming 0, pull_errors [], cards predicted 0, settled 0 —
  reproduces the branch proof's SE2 outputs (header-only daily CSV,
  empty ledger). The 2026 season is complete (last round 2026-11-07)
  and 2027 is not yet listed. Branch proofs: two full runs (44
  leagues, 97 markets on the pre-NO-OBOS base), each 12,195
  predictions, zero errors, fetched_new=0 everywhere; 229/229
  snapshotted output files bit-identical — no ZA-PSL-style exception
  this time. Replay: independent recompute of the shipped virgin
  CSV exactly 0.0 on every field, all 240 rows; r_model recomputed
  152.08755422697251, identical to frozen fitted_params_virgin.json;
  virgin LL@3.5 0.667511 and calibration +3.77pp / SE 3.14pp exact.
  Runner replay differs (max |Δexp_total| 1.3875, max |Δp_over 3.5|
  0.2999) — **decomposed, same class as CY total-shots 0.0802:** the
  first virgin fixture (2026-04-03) replays at exactly 0.0 and the
  gap grows monotonically with the season (mean |Δmu| 0.105 in April
  → 0.504 in October), because the harness interleaves each 2026
  result into the state before predicting the next fixture while the
  runner predicts all upcoming fixtures from the final DEV state;
  in production the runner's state already includes every played
  match (daily refit cadence), so this is a replay-construction
  artefact, not a runner error. Synthetic settlement on match
  5125446 (Helsingborg–Östers IF, 2026-04-03; unified 1+0=1):
  default settled 0, opt-in settled 1 (actual 1.0, p3.5 0.5684,
  miss, LL 0.8401 — matches independent computation), second pass
  settled 0 (exactly once). **Defects / findings:** (1) Pre-ship
  defect, corrected before shipping: the harness first split
  expected totals with SE-Allsvenskan's yellows constant 0.370;
  corrected to this league's frozen 0.3344 (shipped CSV's 1H share
  is exactly 0.3344 on all 240 rows; FT probabilities and gate
  outcome never affected). (2) Builder assert deliberately NOT
  floored: `assert len(out)==len(rows)` is the dynamic form
  (verified 1,440 == 1,440) — same form NO-Eliteserien,
  DE-2Bundesliga, KR-KLeague1 carry unfloored; the AU/MLS floor
  applies to frozen-count asserts only. (3) This worktree arrived
  without the `data_enrichment/fotmob_world` symlink the other
  runner worktrees carry — restored as a symlink to the main
  checkout's warehouse (git-ignored, no commit impact) before the
  proof runs. (4) Proof took extra attempts: run 1 needed 4
  launches — attempt 1 died in a VM reboot after 18 leagues (12:55
  UTC, /tmp wiped), attempts 2–3 OOM-killed at ~7 leagues while
  three Codex builder processes and a sibling proof run shared the
  VM; attempt 4 completed once that load eased. Run 2 completed
  first try. Join lane now 2/2 (US-USLLeagueOne in flight +
  FI-Veikkausliiga launching); next in queue HU-NBI.
- 2026-11-10 22:17 — **⚠ STALL + RECOVERY (watchdog)**: heartbeat
  21:16 WIB (61 min stale), no ledger commit since 21:16, coordinator
  agent quiet ~60 min. Full sweep before any relaunch: both join proof
  runs ALIVE + CPU-active (US-USLLeagueOne run_daily.py PID 1769,
  wt-runner47, 22:42 elapsed; FI-Veikkausliiga PID 1789, wt-runner48,
  22:33 elapsed; run_log.jsonl entries to 22:15 WIB) — NO relaunch, NO
  duplicate builders. Real stall found elsewhere: PA-LPF's verdict
  (FAIL, committed 19:56 WIB) sat UNMERGED for 2h18m. Watchdog verified
  it (prereg 19:48 precedes fitting; virgin-not-read marker present;
  dev numbers reproduce from results_dev.json: GZ pooled LL 1.1006 vs
  climatology 1.0996, RPS 0.2264 vs 0.2259) and MERGED it as league
  #156 (c1950d0e; 0 PASS / 1 FAIL / 4 NOT BUILDABLE; counter 156,
  passing markets 122, milestone 175 is 19 leagues away). Also merged
  the PE-Liga1 C-verdict erratum (189e5622; dev table corrected to
  committed results_dev.json, gate outcomes unchanged). Builds in
  flight 0/5, local queue exhausted; joins 2/2 in flight; remaining:
  joins, external tail batch (if announced), final Codex-sol audit
  pass. Heartbeat refreshed.
- 2026-11-10 22:56 — **FI-Veikkausliiga cards JOINED the daily runner
  (runner 46/99)** (merged 61c606de; branch build/runner-fi-veikkausliiga,
  tip f282d09c — single commit, ONLY league/runner/{README.md,
  active.yaml}, +127 lines; no run_daily.py change, no build_data.py
  change). Market: cards gate_zero 3.5 PROVISIONAL PASS (dev scored
  2022–2025, n=678: LL@3.5 0.673991 vs league base 0.674319 and naive
  0.677092 — dev gate PASS by 0.000328, the thinnest dev margin in
  this league's build; virgin 2026, n=177, read ONCE: LL@3.5
  0.679517 vs base 0.694058 and naive 0.692489; calibration −2.16pp,
  breach within 1 SE of 3.71pp). Goals/SOT/corners FAILed — excluded
  (corners C-FI failed on the virgin calibration leg); total shots
  was never built. Config: primary 3.5, ladder 2.5/3.5/4.5, halves
  yellows share 0.3109, plus the `cards_actual: [yellow_home,
  yellow_away]` opt-in (NO/KR/SE2 pattern). **FI differs from SE2
  on the settle path, and the difference matters:** the stats feed
  DOES carry card keys in 2025–2026, so the default path would not
  settle nothing — it would grade the WRONG target. Stats totals
  disagree with the event-derived gate target on 73/354 matches in
  2025–2026 (41/177 in 2026), including 13 in 2026 that straddle
  the 3.5 line and flip hit/miss; the default also grades nothing
  on the 663 pre-2025 rows. The opt-in is therefore load-bearing
  for correctness, not just coverage. Fitted NB r = 500.0 for
  model/base/naive (estimator cap — effectively Poisson).
  **Merge note:** the branch base (09d62715) was the current HEAD,
  so the merge was clean (no conflicts); merged counts verified by
  YAML parse: 46 leagues / 99 markets. **Merged-state verification
  (coordinator, from the main checkout):** one-league FI run
  (`~/workspace/runner-checks/run_one_league_fi.py`, venv,
  MALLOC_ARENA_MAX=2) — rebuild 1,017 matches / 2,034 team rows,
  upcoming 0, pull_errors [], cards predicted 0, settled 0 —
  reproduces the branch proof's FI outputs (header-only daily CSV,
  empty ledger). The 2026 season is complete (177/177, last match
  2026-11-08) and 2027 is not yet listed. Branch proofs: two full
  runs (46 leagues, 99 markets), each 12,195 predictions, zero
  errors, fetched_new=0 everywhere; **237/237 snapshotted output
  files bit-identical — zero exceptions.** Replay: independent
  recompute of the shipped virgin CSV exact 0.0 on all 177 rows,
  every field; r recomputed 500.0 on all three arms; LL@3.5
  0.679517 / calibration −2.16pp / SE 3.71pp exact; shipped 1H
  share exactly 0.3109 on all 177 rows. Runner replay differs (mean
  |Δmu| 0.2724, max 0.9708; max |Δp_over 3.5| 0.1768) — **same
  decomposed harness artefact as SE-Superettan:** first virgin
  fixture (5147507, 2026-04-04) replays at exactly 0.0, gap grows
  over the season (April 0.1139 → September 0.3849); the harness
  interleaves each 2026 result before predicting the next fixture
  while the runner predicts all upcoming from the frozen DEV state.
  Synthetic settlement on match 5147518 (FC Inter Turku–Ilves,
  2026-04-11): default settled 1 with actual 3.0 (hit, LL 0.5976)
  vs opt-in actual 4.0 (miss, LL 0.7988) — the two paths grade
  DIFFERENT outcomes on the same match, which is exactly why the
  opt-in is required; second pass settled 0. **Defects / findings:**
  (1) The runner's default cards settle path grades the wrong
  target for FI (stats yellows instead of event-derived unified
  yellows) — addressed with the existing opt-in, no new mechanism
  invented. (2) Pre-ship 0.3344 → 0.3109 yellows-constant
  correction (SE2 harness carried a foreign constant), recorded in
  the README; FT probabilities and the gate were never affected.
  (3) Proof incidents: run 1's first launch cut by a VM reboot at
  40/46 leagues (SIGTERM, uptime reset; /tmp wiped, replay/
  settlement scripts lost after their numbers were recorded in the
  README); relaunch + run 2 completed first try. The CO-PrimeraA
  trap did NOT trigger — Primera B files are present via the
  restored fotmob_world symlink; CO rebuilt and predicted cleanly
  in both runs with no copy and no code change. **Coordinator note
  on the 22:17 watchdog stall entry:** the 61-minute heartbeat gap
  was the two long full proof runs (SE2 + FI) running back-to-back
  on the shared VM, with the SE and FI merges landing at their
  completions (21:13 and 22:55); the PA-LPF verdict sat unmerged
  2h18m in the same window — the watchdog's merge of it as #156
  (c1950d0e) is accepted and correct; no coordinator action was
  duplicated. Join lane now 2/2 (US-USLLeagueOne in flight +
  HU-NBI launching); next in queue SK-1Liga.
- 2026-11-11 00:51 — **HU-NBI corners JOINED the daily runner
  (runner 47/100 — the 100th market)** (merged 2879ae4f; branch
  build/runner-hu-nbi, tip 15918bfd — single commit, ONLY
  league/runner/{README.md, active.yaml, run_daily.py}, +166/−12;
  no build_data.py change). Market: corners gate_zero 9.5
  PROVISIONAL PASS (dev n=588: LL@9.5 0.6931 vs base 0.7417 and
  naive 0.7384, beats both in all 3 seasons; virgin 2025/2026,
  n=198: LL@9.5 0.6755 vs best baseline 0.7121; calibration
  −1.56pp, breach within 1 SE of 3.55pp). Goals/SOT/cards/total
  shots FAILed — excluded. Config: primary 9.5, ladder 8.5/9.5/10.5,
  `halves_share_1h: null` — FT-only (no period splits). **First
  join where the territorial multiplier is genuinely active:**
  β_poss = 0.005, γ = 0.0, NB r = 1.086, fit_n 775, active on
  190/198 virgin rows. **Adapter amendment (the column-name
  mismatch, flagged by the coordinator before launch):** HU's CSV
  uses `_h`/`_a` names (`corners_h`, `possession_h`, `home_id`…)
  while the runner's `predict_corners` and corners settle path read
  the standard names (`corners_home`, `BallPossesion_home`,
  `home_team_id`) — without a fix the adapter's `good` filter would
  have dropped every HU row. Fixed with ONE minimal default-inert
  mechanism: a per-market `columns` map in `active.yaml` (12 entries,
  standard → `_h`/`_a`), consulted by both `predict_corners` and
  the corners branch of `settle()`; leagues without the key resolve
  every name to itself. Inertness probe: NO-OBOSLigaen —
  `predict_corners` with HEAD vs amended `run_daily.py` identical on
  every field of every row; `settle()` old-vs-new identical grading
  (match 5105318, actual 15.0, hit, LL 0.6201). HU settle mapping
  proven synthetically on virgin match 4813070 (settled 1 with
  actual 6.0 from `corners_h`/`corners_a`, second pass 0). HU also
  has NO team_matches file — matches only in the `data:` block (the
  world rebuild path reads only `matches`; verified in the proof
  runs). **Merge note:** branch base (f97a0f18) predated only a
  watchdog ledger commit (2d15d5cb), so the merge was clean; merged
  counts verified by YAML parse: 47 leagues / 100 markets.
  **Merged-state verification (coordinator, from the main
  checkout):** one-league HU run
  (`~/workspace/runner-checks/run_one_league_hu.py`, venv,
  MALLOC_ARENA_MAX=2) — upcoming 121, pull_errors [], corners
  predicted 121, settled 0 — reproduces the branch proof's HU
  outputs; first fixture 2026-11-21 Puskás FC Academy–MTK Budapest
  mu 9.22428 / P(over 9.5) 0.43992, exact to the builder's reported
  values; FT-only confirmed (all 1H/2H columns empty). Branch
  proofs: two full runs (47 leagues, 100 markets), each 12,316
  predictions, 0 errors; run 2 fetched_new=0 everywhere; 240/241
  files bit-identical (sole exception: the known pre-existing ZA-PSL
  corners daily — FT values bit-equal to run 1's ledger on all 160
  fixtures). Replay: refit on the pre-virgin window reproduces
  fitted_params_virgin.json bit-for-bit; max |dmu| = 0.0 and max
  |dp_over 9.5| = 0.0 across all 198 virgin rows; LL@9.5 0.6755 and
  calibration −1.56pp exact. β explicitly confirmed applied: active
  on 190/198 virgin rows, moves mu on all 190, largest +2.21 (match
  4813172, z_poss 41.4, mu 9.607 → 11.816); live replay (production
  refit on full history: gamma 0.15, r 1.14946, beta [0.005], fit_n
  1,050) reproduces all 121 live fixtures at max |dmu| = 0.0, and
  the multiplier moves mu on 121/121, largest +1.47 (match 5865544,
  Ferencváros–Kisvárda). **Real HU-NBI fixtures predicted on day
  one: 121** (198 − 77 played in 2026/2027), 2026-11-21 to
  2027-05-22; ledger holds 121 entries; settled 0 (nothing played
  yet). **Defects / findings:** (1) Expected finding, as briefed:
  the replay would have failed on first contact without the mapping
  — fixed by the `columns` map, not by renaming (frozen schema
  preserved). (2) The builder's own first live-replay script had a
  bug, caught before reporting: one FeatureBuilder over history +
  all fixtures let fixture rows (ch=0) contaminate later dates'
  state (max |dmu| 4.314); rebuilding per date group exactly as the
  adapter does gives 0.0 — documented in the README so future joins
  don't repeat it. (3) Codex left one factually backwards comment
  (claimed `core.load` reads standard names; it reads the `_h`/`_a`
  names) — builder fixed it. (4) Environment: worktree arrived
  without the fotmob_world symlink (restored, git-ignored); the
  CO-PrimeraA trap did NOT trigger; a VM reboot wiped /tmp mid-proof
  (scratch scripts + first run's log lost; all numbers re-derived
  from the persistent run log). Join lane now 2/2 (US-USLLeagueOne
  in flight + SK-1Liga launching); next in queue AE-ProLeague.
- 2026-11-10 15:50 — **EXTERNAL SKIP-LOCAL (user instruction via
  Jarvis): Muse-2's cap rises 2 → 4 leagues; assignments 16–19
  from the TAIL of the pool — SG-PremierLeague (461),
  MD-NationalDivision (231), IN-IndianFootballLeague (8982),
  KW-PremierLeague (529), all scores-only/goals-only.** Local lane
  works from the HEAD, external from the TAIL. Checked against the
  live ledger + in-flight list: no collision with the local queue
  head (KR-3 9537 → LU 229 → TZ 9066 → SK-2 8973 → PGPL 523) or
  the 114 completed. They arrive the same way (verified merge +
  EXTERNAL_MERGES.md row); merges may land in batches once the
  rebuild completes.
- 2026-11-10 15:28 — **FR-Ligue3 FOLDED (league #111):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (EXTERNAL — Muse-2;
  merged by Jarvis 111c63dd; row in league/
  EXTERNAL_MERGES.md). **G-FR FAIL at dev gate**: pooled
  dev n=884 — Gate Zero loses ALL THREE legs (1X2 LL
  1,0923 vs clim 1,0869; RPS 0,2266 vs 0,2243; OU2.5 LL
  0,6994 vs 0,6864); SHRINK identical. Virgin 2025/2026
  NOT read. S/C/K/T NOT BUILDABLE (K: plain Yellow events
  0 in 2021/2022–2022/2023, target break). Nothing ships;
  no join. (Merge commit object lost in the 15:33
  object-deletion incident — to be rebuilt.)
- 2026-11-10 23:48 — **WATCHDOG CHECK (no stall)**: heartbeat 22:56 WIB (51 min stale at check) but full sweep proves the program ALIVE — no relaunch, no duplicate builders (same handling as the 22:17 watchdog). Both join proof runs CPU-active: US-USLLeagueOne run 2 (PID 12789, wt-runner47, started 23:19 WIB, CPU time growing 17:38→18:03 across the check; run_log.jsonl entries to 23:46) + HU-NBI run 1 (PID 13227, wt-runner49, started 23:23 WIB, CPU 13:24→13:55; run_log.jsonl entries to 23:46). No Codex processes running (proof runs are the venv runner, not Codex). Coordinator agent still running, last activity ~44 min ago — waiting on the proof runs. No QUOTA-WAIT, no PAUSED-BY-USER (pause lifted). Counter still 156; next milestone 175 (19 leagues away). Heartbeat refreshed.
- 2026-11-11 01:45 — **WATCHDOG CHECK (no stall)**: heartbeat 00:51 WIB (54 min stale at check) but full sweep proves the program ALIVE — no relaunch, no duplicate builders (same handling as the 23:48 watchdog). Final audit (user order 01:34) RUNNING: Codex gpt-6.1-sol batch 01 live since 01:41 (PID 16520), classification 65/65 rows written 01:45, audit commits 01:35/01:38/01:43. US-USLLeagueOne join proof committed on branch build/runner-us-usll1 at 01:40 (99140862, runner 45/99) — awaiting coordinator merge. SK-1Liga join proof run 2 CPU-active (PID 15419, wt-runner50, started 01:37, CPU 5:48). No QUOTA-WAIT, no PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues away). Heartbeat NOT refreshed (no resume; heartbeat edits reserved for resume).
- 2026-11-11 01:48 — **US-USLLeagueOne JOINED runner (48/102)** — merge dd2765c7 (watchdog-completed 01:45 from the coordinator's staged resolution of branch build/runner-us-usll1 99140862; base e657f549 predated SE/FI/HU joins, so active.yaml/README/run_daily.py all conflicted and were resolved per practice: HEAD active.yaml + USLL1 block verbatim, HEAD README + USLL1 paragraph, run_daily.py exclude_phases insertions re-based onto HEAD's market.get + columns-map form). Markets: corners GZ 9.5 provisional (virgin LL 0.688533, cal +1.49pp ≤ SE 3.44pp; dev pooled LL 0.684403 vs base 0.693505/naive 0.691119, n=486; X7 failed dev 0.714615, excluded) + total-shots B 24.5 provisional (virgin LL 0.693325, cal +2.87pp ≤ SE 3.44pp; dev pooled B 0.679305 vs base 0.694009/naive 0.684291, n=321; arm C fails dev-sign, A provisional but B lower virgin LL). Coordinator recomputed both virgin files exactly from the shipped per-match CSVs (210 rows each). New adapter opt-in `exclude_phases` (corners + total-shots arm B, mirroring exclude_seasons; inertness probed on SCO corners + USLChampionship arm B) + build_data.py assert floored to >=1174. Merged-state one-league run from main reproduces branch proof bit-identically: 1 upcoming fixture, the 2026-11-15 final Charlotte Independence–Boise (1000023200), corners exp 8.8729 / P(over 9.5) 0.3967, total shots exp 29.0744 / P(over 24.5) 0.7694; 0 settled. Proof caveat: run-1 md5 snapshot lost to service restarts, run-1/run-2 comparison recovered through ledgers per the brief's exception clause (12,197 non-CO rows bit-equal; sole fixture-set delta CO-PrimeraA 0→10/market as FotMob published the 2026-11-12 matchday mid-proof). DEFECTS (final-audit list): (1) brief premise wrong — predict_corners live-fits every league, does NOT pin to fitted_params_virgin.json (verified git log -S empty; live refit on full regular history gamma 0.15, r 1.1255, beta [0.0025, 0.025] vs frozen r 1.1072, beta [0,0] — by-design daily refit, no pinning added; corrects the NO-OBOS-era 'pinned' framing); (2) frozen-builder phase bug — phase() keys off the league name ending in 'Playoff', so the six 2026 playoff matches are flagged 'regular' and enter production fits/state (bounded, 6/1,174; fix candidate: phase from the round field; NOT fixed — brief Change 2 forbade other build_data.py edits); (3) US-USLChampionship arm B moves on all 375 probe rows when exclude_phases is set — its production predictions currently include playoff-row state (config left untouched; follow-up could set the key deliberately); (4) corners results_virgin.json calibration_diff is predicted−actual (−0.0149) while the gate convention is actual−predicted (+1.49pp) — sign-convention inconsistency in that file only, verdict unaffected. Join lane now 1/2 (SK-1Liga SOT in flight); AE-ProLeague join launching next.
- 2026-11-11 02:30 — **SK-1Liga JOINED runner (49/103)** — merge 5ff23d9c (branch build/runner-sk-1liga 3c25101c; base ac1d645d predated the USLL1 join, so active.yaml/README conflicted and were resolved per practice: HEAD active.yaml + SK block verbatim, HEAD README + SK paragraph, 89 lines; run_daily.py untouched). Market: SOT GZ 8.5 CLEAN PASS (dev pooled LL 0.683432 vs base 0.702388/naive 0.695303, n=568; virgin 2025/2026 n=192 LL 0.687872 vs base 0.696309/naive 0.693703; cal +0.88pp actual−predicted, inside the 1.0pp clean band — the verdict/builder state it as −0.88pp pred−actual, same magnitude, opposite sign convention; RS passes dev but fails sign check 1/3, never read on virgin). Coordinator recomputed the virgin file exactly from the shipped per-match CSV (192 rows; nb_r 79.94; league_means SK-1Liga home 4.796608 / away 3.890263). Block carries div: SK-1Liga + ratio_prior: 200 + team_key: canonical_name (CZ precedent, no code change) — LOAD-BEARING: 8/12 clubs diacritic-spelled in the 2026/2027 feed (Žilina, Trenčín, Ružomberok, Komárno, FC Košice, Dukla Banská Bystrica, Zemplín Michalovce, Zeleziarne Podbrezová), 20 spellings for 12 teams; probe Žilina–Trenčín mu 9.670 with the key vs 10.157 without (Δ −0.488); even an ASCII fixture differs because the key merges the split 2026/2027 history. Merged-state one-league run from main reproduces branch proof exactly: 48 upcoming fixtures 2026-11-21→2027-02-27, first Ružomberok–Slovan Bratislava mu 8.4315 / P(over 8.5) 0.4978, FT-only (halves empty); 0 settled. Proof caveat: run-1 md5 snapshot lost to a runtime restart wiping /tmp (same class as USLL1) — substitute evidence: identical per-market counts on all 101 markets, SK daily values matching recorded run-1 values to full precision, SK ledger mtime untouched by run 2, ZA-PSL corners FT values bit-equal to run-1 ledger on all 160 rows. Join lane now 1/2 (AE-ProLeague in flight); HR-HNL join launching next.
- 2026-11-11 03:16 — **AE-ProLeague JOINED runner (50/104)** — merge ef2f7f2f (branch build/runner-ae-proleague 87b69640; base b7881d90 predated the SK merge, so active.yaml/README conflicted and were resolved per practice: HEAD active.yaml + AE block verbatim, HEAD README + AE paragraph; run_daily.py + build_data.py merged cleanly). Market: total shots C 25.5 PROVISIONAL (dev pooled n=545 LL@25.5 C 0.681906 vs base 0.696534/naive 0.695637; virgin 2025/2026 n=182 C LL 0.686302, lowest of A/B/C and below base 0.691060; cal |3.10pp| actual−predicted −3.10pp, inside 1 SE 3.67pp — virgin season ran cold, 24.48 shots/match vs 25.67–26.87 dev; B fails leg (i) vs A, excluded). Coordinator recomputed the virgin file exactly from the shipped per-match CSV (182 rows; r_A 156.5851, trailing window 200). Adapter amendment: arm-C `half_split` fallback to the market's frozen `halves_share_1h` (0.4608) when `fitted_params.json` carries no `half_split` — the unamended adapter CRASHED on AE with KeyError (first arm-C league without one; all six existing arm-C leagues carry it); verbatim port of the CL arm-A / CN arm-B precedent; inertness proven by a GR-SuperLeague arm-C probe byte-identical on 8 fixed pseudo-fixtures. Trailing window 200 confirmed picked up from `fitted_params.json`; no season exclusion (harness fits all seasons). build_data.py floors: completed seasons exact 182, 2026/2027 >= 49, total >= 959 (prophylactic — rebuild still exactly 959/49). Merged-state one-league run from main reproduces branch proof exactly: 70 upcoming fixtures 2026-11-19→2027-02-21, first Al-Wasl–Hatta exp 26.9833 / P(over 25.5) 0.5816, exp range 24.3319–28.5102, 1H share exactly 0.4608 on all 70 rows; 0 settled. Proof: two full runs first-try, 49 leagues, 12,418 predictions each, run 2 fetched_new=0 everywhere, 249/250 files bit-identical (sole exception ZA-PSL corners daily, known case — FT values bit-equal to run-1 ledger on all 160 fixtures). DEFECT (final-audit list): the runner's arm-C adapter includes the 2 awarded AE matches (2021-09-10, 2024-04-27) in its fit/state walk while the frozen harness drops them — uniform adapter behaviour across all leagues, fully explains the replay gap (max |Δmu| 0.0210; removing them reproduces the shipped file to 1.8e-07); left as-is because fixing it would change every league's behaviour. NOTE: final audit hit a Codex QUOTA-WAIT until 04:06 WIB (f84fda21) — audit agent only; join lane does not use Codex and is unaffected. Join lane now 1/2 (HR-HNL in flight); DK-1Division join launching next.
- 2026-11-11 04:17 — **HR-HNL JOINED runner (51/105)** — merge 33e43b9e (branch build/runner-hr-hnl 03014541; base c20588ff predated the AE merge, so active.yaml/README conflicted and were resolved per practice: HEAD active.yaml + HR block verbatim, HEAD README + HR paragraph, 79 lines; run_daily.py untouched — no adapter change needed). Market: corners X7 8.5 PROVISIONAL (dev pooled n=540 GZ 0.695758 / X7 0.693357 vs base 0.725167/naive 0.725569; virgin 2025/2026 n=180 X7 LL 0.685221 vs GZ 0.693697/base 0.758846; cal +2.97pp actual−predicted, inside 1 SE 3.70pp of the 1.0pp boundary — the verdict states −2.97pp pred−actual, same magnitude, opposite sign convention). Coordinator recomputed the virgin file exactly from the shipped per-match CSV (180 rows; gamma 0.15, r 1.1582846692836015, X7 beta [0.0], fit_n 710; 1H share exactly 0.4793 on every row). X7 β=0 again — no box-touch signal ships, honest per the frozen arm definition; the live refit on full history (964 rows) keeps gamma 0.15 and beta [0.0], moves r 1.1583 → 1.2280. Merged-state one-league run from main reproduces branch proof exactly: 116 upcoming fixtures 2026-11-21→2027-05-22 (all remaining 2026/2027 fixtures, 180 − 64 played), first Dinamo Zagreb–NK Istra 1961 mu 9.7025 / P(over 8.5) 0.6122; 0 settled. Proof: two full runs, 50 leagues / 104 markets, 12,512 predictions each, run 2 fetched_new=0 everywhere, 103/104 files bit-identical (sole exception ZA-PSL corners daily, known case — FT values bit-equal to run-1 ledger on all 160 rows); run 2's first attempt was killed by a runtime restart at 38/50, relaunched after 60s and completed first try. NOTE: DK-1Division builder (543cff0f) showed a stale "interrupted" flag in one handoff children list but is in fact RUNNING (last activity 29s at check) — no action taken. Join lane now 1/2 (DK-1Division in flight); AU-ALeagueWomen join launching next.
- 2026-11-11 06:19 — **DK-1Division JOINED runner (52/109)** — merge 490c6fcd (branch build/runner-dk-1division 99201450; base 8bb02fc9 predated the HR merge, so active.yaml/README conflicted and were resolved per practice: HEAD active.yaml + DK block verbatim, HEAD README + DK paragraph; run_daily.py merged cleanly). Markets: corners X5 9.5 PROVISIONAL (virgin 2025/2026 n=192 LL 0.7035, cal −3.71pp, inside the 4.64pp provisional bound; Gate Zero FAILS calibration |−5.16|pp and X7 fails too; dev pooled n=384 GZ 0.7016 / X5 0.6965 / X7 0.6977), cards GZ 3.5 CLEAN PASS (virgin LL 0.6780, cal +0.03pp; target stats-feed yellow+red), SOT GZ 9.5 PROVISIONAL (virgin LL 0.6902 vs base 0.6909 — LL leg passes by 0.0007; cal −1.48pp), total shots X5 26.5 PROVISIONAL (virgin LL 0.6764, cal −1.70pp; Gate Zero clean −0.77pp but X5 lower LL ships per the both-pass rule). Goals excluded (dev FAIL, virgin unread). Coordinator recomputed all four virgin LLs exactly from predictions/*_virgin_predictions.csv (diffs ≤6e-6, CSV rounding). X5 is NEW to the runner (no `x5` string existed in run_daily.py): corners mu = 0.5*mu_GZ + 0.5*(naive_home+naive_away)/2, which matches the frozen harness run_c_dk1.py:35 exactly (each naive_* is already a total — coordinator checked core.attach_naive rather than assuming); total shots arm_x5 is a new function reading lambda 100.0 / r 57.0019 from fitted_params_virgin.json, pointer walk mirroring arm C. Adapter amendments, all opt-in and default-inert (8 inertness probes byte-identical): cards_target yellow_plus_red in predict_cards + settle (builder's yellow_home alias is yellow-only; the frozen target is yellow+red); SOT league-column append in rebuild_csv_world (every SOT loader reads div = r["league"]; DK's builder omits it); ratio_prior passed only when the engine accepts it (DK's Engine takes only matches+arm, fixes prior 200.0); team_key id remap in predict_sot (three FotMob ids carry two spellings in the fit window: 9814 Horsens/AC Horsens, 8487 Sønderjyske/SønderjyskE, 8470 Aalborg BK/AaB). ccode corrected DNK→DEN (FotMob index + DK-Superligaen use DEN). Defect found by the proof run itself: the brief wrote world_league "1. division" (lowercase d) but FotMob's name and the warehouse directory are "1. Division" — run 1 re-fetched all 1,044 finished matches into a duplicate lowercase directory (154 MB); fixed (config now "1. Division", duplicate dir deleted, index paths restored, the one match that existed only in the duplicate, 5764526 finished 2026-11-09, re-fetched into the correct dir, four stats-revised JSONs refreshed, rebuilt CSV md5-identical to run-1). MERGE-VERIFICATION CATCH: that re-fetch updated the WORKTREE's index copy but not the main checkout's — the main index carried no row for 5764526, so the coordinator's merged-state run first rebuilt 1,043 rows (predictions shifted ≤0.005 on exp); the coordinator inserted the worktree's index row verbatim into the main index (DK 2026/2027 rows 83→84) and re-ran: rebuild now 1,044 matches / 2,088 team rows and the merged-state run reproduces the branch proof BIT-IDENTICALLY (first fixture Fredericia–Hillerød 2026-11-19 match 5764470: corners exp 9.448767250658385 / p9.5 0.4655; cards 3.1436974819915218 / 0.3840; SOT 10.214422993807698 / 0.5473; total shots 29.59980218718723 / 0.6636). Merged-state one-league run from main: 48 upcoming fixtures per market (2026-11-19→2027-03-19), 0 settled, ledger 192 entries. Proof: two full runs, 51 leagues / 108 markets, 12,658 predictions each, run 2 fetched_new=0 everywhere, 359/361 files bit-identical (run log accumulates by design; ZA-PSL corners daily differs only in row order, all values bit-equal to the run-1 ledger). Replay: all four markets reproduce the shipped virgin files at CSV rounding level with frozen params (cards p differs ≤0.0056, decomposed to the runner's live r re-estimation; SOT mu ≤0.0884, decomposed to the refit anchor — both by-design live-refit classes). NOTE for the next merge: DK's README claims "no joined SOT league's CSV lacks the league column" — stale the moment AUW (which also lacks it) joins; the rebuild append engages for AUW too with the same value (league name = div), no behaviour change. Join lane now 1/2 (AU-ALeagueWomen in flight).
- 2026-11-11 06:20 — **AU-ALeagueWomen JOINED runner (53/111)** — merge 9e7230fd (branch build/runner-au-aleaguewomen 32910e2f; base c86cf79c; active.yaml/README conflicted and were resolved per practice: HEAD active.yaml + AUW block verbatim, HEAD README + AUW paragraph; run_daily.py AUTO-MERGED with DK's changes — the two predict_sot hunks and both settle branches compose, verified by grep + ast.parse). Markets: corners X7 9.5 PROVISIONAL (virgin n=110 LL 0.684884, cal −3.205pp, SE 4.739pp; Gate Zero FAILS leg (i) vs naive, X7 the only eligible arm; beta [0.0], r 1.1887220308967725, fit_n 429), SOT RS 10.5 PROVISIONAL (virgin LL 0.643041, cal +1.471pp, SE 4.546pp; ratio_prior 20000 per prereg; team_key id). **Cards X8 EXCLUDED by the operational gate** (third stop after DE-2/PL): 0/91 upcoming 2026/2027 fixtures mention a referee anywhere in the FotMob leagues payload, and a per-fixture matchDetails check of all 91 shows the infoBox Referee text empty on every one (key present, name absent); the history referee column is populated (19/19 played 2026/2027, 550/597 overall) but that does not pass the gate, per the brief. No cards block, no X8 plumbing, no Gate Zero substituted. Goals + total shots excluded (dev FAIL). Coordinator recomputed all three virgin LLs exactly from predictions/*_virgin_predictions.csv (diffs ≤2e-7, n=110). Adapter amendments: predict_sot gains `columns` + `exclude_phases` opt-ins mirroring the corners precedent — the brief's premise "both arms already honoured, no run_daily.py edit" was FALSE for AUW (its builder writes home_-prefixed columns and no league column, so the stock SOT adapter's load_matches silently loads 0 rows; with the keys the engine loads 568 regular rows); settle() SOT now honours `columns` (without it SOT would settle 0 rows forever — the actuals would resolve to the lower-case fallback). Inertness proven on AU-ALeague RS (byte-identical HEAD vs amended, predict + settle). Config: no team_matches line (builder writes no team table; HU-NBI precedent); corners + SOT carry columns + exclude_phases ["finals"] (frozen harnesses are regular-only); corners halves 0.48 (shipped CSV uses stale 0.452, already documented in ca1da555 — the adapter's 1H/2H differ from the shipped CSV by design); shipped corners CSV ladder [9.5, 10.5, 11.5] vs frozen protocol [8.5, 9.5, 10.5] — evaluated lines reproduce exactly, the CSV omits the 8.5 column (recorded, NOT "fixed"). LATENT DEFECT (final-audit list, not fixed — cards doesn't join): predict_cards would silently drop all AUW history — the builder writes home_yellow_cards but the adapter accepts only yellow_home/away or yellow_cards_home/away; recorded in the README. Merged-state one-league run from main reproduces the branch proof BIT-IDENTICALLY: 91 upcoming fixtures per market (2026-11-14→2027-04-11), first 2026-11-14 Melbourne City FC (W)–Newcastle Jets (W) corners mu 8.5740 / P(over 9.5) 0.3620, SOT mu 10.4237 / P(over 10.5) 0.4006; 0 settled; ledger 182 entries; rebuild 597 rows (568 regular + 29 finals), build_data.py floored to >=597. Proof: two full runs, 52 leagues / 107 markets, 12,764 predictions each, run 2 fetched_new=0 everywhere, all 263 files bit-identical (the ZA-PSL known case did not differ this time). Replay: exact causal-state copies reproduce both markets at max |dmu| 0.0 (corners) / 1.8e-15 (SOT); live-refit gaps are the by-design daily refit + the update-order effect (fully decomposed). Join lane now 0/2; IS-BestaDeildin join launching next.
- 2026-11-11 07:51 — **IS-BestaDeildin JOINED runner (54/114)** — merge 1d9048fd (branch build/runner-is-bestadeildin 656a2853; base bcb1a37e already contained the DK+AUW merges, so active.yaml/README merged cleanly with no conflict; run_daily.py untouched). Markets, ALL PROVISIONAL: SOT GZ 9.5 (virgin 2026 n=162 LL 0.631861 vs base 0.672605 / naive 0.640239; cal −1.398pp, SE 3.707pp; RS 0.633819 fails leg (i)), corners X7 11.5 (virgin LL 0.674422 vs GZ 0.698517 / base 0.689293; cal −2.353pp, SE 3.863pp; GZ fails leg (i) vs base; gamma 0.3, r 1.1860067504340819, beta [0.0], fit_n 474), total shots B 27.5 (virgin LL 0.553977 vs A 0.559717 / C 0.566887 / base 0.608400; cal −3.446pp, SE 3.381pp; A fails cal −7.135pp, C fails cal −8.671pp). Goals + cards excluded (dev FAIL, virgin unread). Coordinator recomputed all three virgin LLs exactly from predictions/*_virgin_predictions.csv pre-brief (diffs ≤3e-7). NO adapter change: the pinned block is verbatim, no extra keys forced. No `exclude_phases` — the frozen harnesses score ALL phases (virgin n=162 = 132 regular + 15 championship + 15 relegation); rebuild 942 rows, phases 792/75/75. Total-shots arm-B `half_split` fallback to `halves_share_1h` engages (CN precedent; fitted_params.json has no half_split) — 1H share exactly 0.4623 on all 162 replay rows. Replay: SOT frozen walk 0.0 on all 12 columns; corners frozen params 0.0 on all 12 columns; total-shots adapter within max |Δmu| 0.426 (mean 0.071), entirely the same-day level-layer effect — zero (max 7.1e-15) on single-match dates, nonzero only on the 40 multi-match dates (harness updates the level layer after each match, adapter feeds a whole date at once); adapter LL@27.5 0.555773 vs shipped 0.553977. The SOT live gap (max |Δmu| 1.885) decomposes into the within-virgin update effect + the future-leakage effect (both by-design live-refit classes, same as AUW/DK); the corners live gap is only the r refit (1.1860 → 1.1974; gamma/beta unchanged), LL 0.674457 vs shipped 0.674422. FINDINGS (final-audit list): (1) Team-name split is REAL — nine FotMob ids carry two spellings (Keflavík, Kópavogs, Víkingur Reykjavík, Fram Reykjavík, ÍA, KR Reykjavík, FH Hafnarfjörður, ÍBV, Breiðablik); diacritic sole in 2026 for all nine, and Keflavík + Víkingur Reykjavík appear in diacritic form ONLY in 2026. No `team_key` — the frozen harness keys raw names, and an id-keyed walk is WORSE (max |Δmu| 1.064 vs 0.0 name-keyed); the DK remap would have broken this league. (2) REPLAY ARTEFACT (corners): feeding a played match as an upcoming fixture makes `predict_corners` return TWO rows for it (history copy with correct prior-only features, exp 11.5311, + fixture copy built on leaked full-history prior, exp 12.6920); both landed in the worktree ledger — `write_predictions` dedups only against the pre-existing ledger, not within one call — and `settle()` graded the first (correct) entry. In production this cannot occur (upcoming fixtures are future-dated and absent from the CSV). Worth a shared dedup fix if the corners adapter is ever touched. (3) LATENT: the corners adapter does not implement the 2023 touches quarantine (`core.load` blanking is bypassed by the in-memory history build); proven immaterial here (fits identical with/without, beta [0.0]) but a future league with nonzero fitted beta could be affected — worth a shared quarantine opt-in if such a league joins. Merged-state one-league run from main reproduces the branch proof: rebuild 942 rows, 0 upcoming fixtures per market (2026 complete, 2027 unpublished), 0 settled, header-only daily CSVs, ledger empty. Synthetic settlement (branch proof, match 5225640 ÍA–ÍBV 2026-05-21, actuals SOT 9.0 / corners 12.0 / total shots 28.0): SOT exp 10.1068, over, miss, LL 1.0426; corners exp 11.5311 (correct copy), under, miss, LL 0.7378; total shots exp 29.6751, over, hit, LL 0.4687; each settled exactly once, second pass settled 0; grading lines in reports/grading_ledger.jsonl (worktree only — the duplicate leaked corners row sits in the worktree ledger, NOT committed, so main's ledger is clean). Proof: two full runs, 54 leagues / 114 markets, 12,956 predictions each, run 2 fetched_new=0 everywhere; 228/276 files bit-identical, the only 48 differing files are ledger.jsonl dated appends (runs straddled midnight UTC: run-1 entries 2026-11-10 + identical run-2 set 2026-11-11, e.g. DK 192+192, J1 720+720 — expected run_date-keyed behaviour, not a defect). build_data.py floored to >=942 (rebuild exactly 942). Join lane now 0/2; SA-FirstDivision SOT join launching next.
- 2026-11-11 09:49 — **SA-FirstDivision JOINED runner (55/115)** — merge ac93e742 (branch build/runner-sa-firstdivision 553d7186; base 9e3c4f2b; active.yaml/README/run_daily.py merged cleanly, no conflict). Market: SOT GZ 8.5 **CLEAN PASS** (dev pooled n=214 GZ LL@8.5 0.6944 vs base 0.6963 / naive 0.6987; virgin 2026/2027 TRANSITIONAL n=94 GZ LL 0.686013 vs base 0.690133 / naive 0.705866; cal −0.686pp pred−actual, SE 5.145pp — inside the 1.0pp clean band; RS 0.686166 fails leg (i)). Goals, corners, total shots, cards all FAIL and are excluded. Coordinator recomputed the virgin LL exactly from predictions/s_safd_virgin_predictions.csv pre-brief (diff 1.2e-7). TWO adapter opt-ins in `predict_sot`, both engaged only by new market keys, hand-implemented (no Codex): (1) `seasons` allowlist (mirrors the ratio_prior signature-check pattern) — SA's loader is `load_matches(path, seasons)` with seasons REQUIRED, so the stock one-argument call raises TypeError (verified on HEAD); SA passes ["2025/2026", "2026/2027"] only — score-only 2024/2025 (309 rows, empty stat fields) would crash the loader's bare float(). Inertness: HEAD vs amended predict_sot on DK-1Division GZ byte-identical on 8 fixed pseudo-upcoming fixtures. (2) `regular_rounds_only` — the pull's fixture dicts now carry `round` (additive; verified on the branch that no other consumer reads it), and predict_sot skips a fixture whose round is not a plain round number when the market opts in; round-less fixtures pass through; leagues without the key are unchanged (verified: a playoff-round fixture is skipped for SA, kept for DK). The loader itself filters phase != regular and awarded != 0, so NO `exclude_phases` key was needed. Replay: harness-style causal walk reproduces the shipped CSV at max |Δmu| 1.8e-15 (virgin LL 0.686013 exactly); live adapter walk max |Δmu| 0.4580 (mean 0.1242), max |Δp8.5| 0.2181, replay LL 0.637147 — decomposed: refit-anchor effect exactly 0.0000, no-within-virgin-update effect 0.4676, future-leakage effect 0.5856 max pairwise; the adapter's replay LL looks better than the gated 0.686013 ONLY because of that leakage and is not the gated number (worst gap: 2026-08-31 Al-Saqer–Al Akhdoud, adapter 0.525 vs shipped 0.307 — both clubs 2026/2027 newcomers with no dev history). 1H share exactly 0.454 on all 94 replay rows; loader returns 398 rows (304 dev + 94 virgin), excluding the 3 playoff + 2 awarded rows of 2025/2026. Team names: fitted 24 teams equal the union of the 2025/2026 + 2026/2027 sets exactly; index names match the CSV on all 712 matches — no split, no `team_key`. EDGES: (1) playoffs — 2026/2027 playoffs (~May 2027) not yet published (FotMob lists ~2 months ahead); current 68 upcoming are all regular rounds; the opt-in above keeps playoffs unpredicted when they appear (round-19 fixtures 2027-01-03..05 are marked cancelled and the pull already skips them). (2) awarded at settlement — 2026/2027 has 0 awarded rows; the only 2 awarded rows (2025/2026, Al-Faisaly–Abha + Al-Ula–Al-Wehda) carry scores but NO stats, so settle()'s empty-actual guard skips them; latent only — PROPOSED (not implemented) opt-in `exclude_awarded_settle: true` for settle() if FotMob ever attaches stats to an awarded match. DEFECT found by proof run 1 and fixed: SA's `build_data.py` had NO `main()` (every other world builder defines one) — `rebuild_csv_world` raised AttributeError and SA predicted nothing in run 1; `main()` now wraps the `__main__` block (in the commit). Merged-state one-league run from main reproduces the branch proof BIT-IDENTICALLY: rebuild 712 rows (309/season + 94), 68 upcoming SOT fixtures 2026-11-18→2027-01-10, first 2026-11-18 Al-Adalah–Al-Orobah FC exp 8.090251945266731 / P(over 8.5) 0.4166736186999434, 1H share exactly 0.454 on all 68 rows, ledger 68 entries, 0 settled. Proof: run 1 (12,956 predictions, 1 error row = the main() defect, SA predicted nothing); run 2's first attempt killed by a runtime restart at 5 leagues (tmp wiped, run-1 snapshot lost — comparison recovered via a third run per the brief's exception clause, same class as USLL1/SK); relaunched run 2 + run 3: 13,024 predictions each, 0 errors, fetched_new=0 everywhere, all 280/280 snapshotted files bit-identical between runs 2 and 3 (ZA-PSL did not differ). Join lane now 0/2; LV-Virsliga SOT join launching next.
- 2026-11-11 11:24 — **LV-Virsliga JOINED runner (56/116)** — merge 8cec8d55 (branch build/runner-lv-virsliga 958d1c86; base 9aa99359; active.yaml/README merged cleanly, no conflict). Market: SOT GZ 9.5 **CLEAN PASS** (dev stats era n=133 GZ LL@9.5 0.682846 vs base 0.689921 / naive 0.683999; virgin 2026 n=179 GZ LL 0.679910 vs base 0.679994 / naive 0.680898; cal +0.21pp actual−predicted, SE 3.697pp; RS 0.685650 dead at dev). Leg (i) passes by **0.000084** over the league base rate — the frozen rule is a comparison, not a margin, and it passes (stated plainly in the README). Goals, corners, total shots, cards all FAIL and are excluded. Coordinator recomputed the virgin LL exactly from predictions/s_lv_virgin_predictions.csv pre-brief (diff 4.5e-7). NO adapter change, hand-implemented (no Codex): the stock predict_sot path fits exactly (loader `load_matches(path, allowed_seasons=None, ...)` requires `has_stats_all == "1"` + four stat columns, reads `div = r["league"]`, keys raw names; Engine accepts ratio_prior kwarg). No `seasons` key (pre-stats rows drop via the has_stats_all filter, as the harness does), no columns/exclude_phases/team_key (6 relegation finals excluded by the builder; standard stat names). Data rebuild UNCHANGED: source 1,017 / rows 1,011 / excluded 6 — the hard-equality asserts were left alone. The RFS–Riga FC round-36 match has NOT appeared: live FotMob probe shows match 5162094 (Riga FC vs RFS, 2026-11-08) is listed cancelled/postponed, not finished — neither fetched nor predicted; round 36 holds 4 played matches. Team names: FK Liepāja (id 8016) and Grobiņa (662738) each use ONE spelling across all 359 stats-era rows; ASCII spellings occur only in pre-stats seasons the loader drops — no split, no canonicalisation. Replay: harness causal walk reproduces the shipped CSV at max |Δmu| 3.6e-15, LL@9.5 0.679910 exact; live adapter walk max |Δmu| 0.8429, max |Δp@9.5| 0.1922, replay LL 0.672860 — decomposed: refit-anchor 7.8e-14, no-within-virgin-update 0.5888, future-leakage 0.8540; the adapter's replay LL looks better than the gated 0.679910 ONLY because of that leakage and is not the gated number. 1H share exactly 0.4637 on all 179 rows. Merged-state one-league run from main reproduces the branch proof: rebuild 1,011 rows / 2,022 team rows, 6 relegation finals excluded (ids 4064841/4064842, 4365408/4365409, 4673639/4673640), 0 upcoming, 0 settled. Proof: run 1 (13,024 predictions, 0 errors, fetched_new 2,092 for J1's fresh store only); run 2's first attempt killed by a runtime restart at 18 leagues (tmp wiped, run-1 snapshot lost — comparison recovered from the post-run-1 on-disk state re-snapshotted to ~/workspace/lv-proof/ after the killed attempt; per-league/market predicted counts match run 1 exactly on all 43 common entries, ledgers deduplicated, no duplicate lines — same class as USLL1/SK/SA); relaunched run 2: 13,022 predictions, 0 errors, fetched_new=0 everywhere. The 2-prediction gap is a LIVE-FEED change, not a defect: AU-ALeagueWomen fixture 1000020337 (Newcastle Jets (W) vs Adelaide United (W), 2026-11-21) was listed postponed/cancelled by FotMob between the runs (verified by live probe), so the relaunch correctly stopped predicting it (91→90 in both its markets). Bit-identical: 281/284 files; the 3 differs are AUW corners + SOT (the postponed fixture dropped) and ZA-PSL corners — a live-feed team-name spelling change ("AmaZulu FC" → "AmaZulu", 19 rows) with every numeric value bit-equal (max |d| 0.0). Synthetic settlement (LV predicts 0 upcoming): match 5161946 (2026-04-14, SK Super Nova vs Riga FC; actual SOT 9.0, within 0.5 of the 9.5 line): adapter exp_total 9.3850, P(over 9.5) 0.4270, chosen under, HIT, LL 0.5569; settle() first call 1 settled, second call 0 — nothing re-settles; the four touched runtime files were restored byte-identical to post-proof-run state afterward. No defects in the LV join path. Join lane now 0/2; AR-PrimeraBNacional cards X8 operational gate launching next.
- 2026-11-10 15:28 — **BY-PremierLeague FOLDED (league
  #112): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (EXTERNAL —
  Muse-2; merged by Jarvis 58d158d4; row in league/
  EXTERNAL_MERGES.md). **G-BY FAIL at dev gate**: pooled
  dev n=690 — OU2.5 LL 0,7143 vs clim 0,6934, loses the OU
  leg every season; 1X2 LL 1,0679 / RPS 0,2223 beat
  climatology but lose to naive (1,0534 / 0,2181); X2 worse
  pooled; SHRINK identical. Virgin 2025 NOT read. S/C/K/T
  NOT BUILDABLE (K: plain Yellow events 0 in every season).
  Nothing ships; no join. (Merge commit object lost in the
  15:33 object-deletion incident — to be rebuilt.)
- 2026-11-10 15:30 — **EPERM RECOVERED ~15:21 WIB; IR
  merged as #111, SV merged as #112.** The SV builder
  reported exec writes blocked ~07:58–08:20 (UTC — i.e.
  14:58–15:20 WIB) and recovered 08:21 UTC; the coordinator
  confirmed a content write landing at 08:30 UTC and git
  add/commit working again. IR's blocked commits were made
  by the coordinator from the verified worktree (23cf1515
  engine+verdict, dfc5fafa force-added results_dev.csv),
  then merged 76e60493; SV merged 2b8b4859. The 15:16
  ledger write itself is committed with this entry. Lesson
  for the final audit: this second EPERM episode ran
  ~07:57–08:21 UTC (~24 min of blocked writes, vs ~33 min
  for the morning episode); the file-tool write path stayed
  usable throughout, which is what saved both builds'
  artifacts. **Build slots refilled:** Australia
  Championship (FotMob 8938, 1,333 matches — id verified
  from the warehouse index; caution briefed: recently
  launched second tier, verify seasons/format from
  payloads; AU-ALeague sibling exists, X2 only if the data
  supports it) launched on branch build/au-championship +
  Algeria Ligue 1 (FotMob 516, 1,332 matches — id verified;
  no Algerian sibling, no X2) launched on branch
  build/dz-ligue1; build lane back at 5/5. Next in the
  frozen queue after these (recomputed from the index,
  plain-n order, production top-5 + consumed + external
  excluded): South Korea K League 3 (9537, 1,296) →
  Luxembourg National Division (229, 1,296) → Tanzania
  Premier League (9066, 1,284) → Slovakia 2. Liga (8973,
  1,269) → Iran Persian Gulf (523, 1,245).
- 2026-11-10 15:30 — **SV-PrimeraDivision COMPLETE (league
  #112): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged
  2b8b4859; branch build/sv-primera-division, commits
  5e766d56/ff1d6b97/a4f77ec4 — prereg before fitting; diff
  27 files, all under league/SV-PrimeraDivision/). **G-SV
  FAIL at dev gate**: pooled dev n=815 — Gate Zero wins 1X2
  LL (1,0565 vs clim 1,0895) and RPS (0,2172 vs 0,2286) but
  loses OU2.5 (0,6994 vs 0,6895 — miss 0,0100); SHRINK
  byte-identical to Gate Zero on all 815 rows (0 teams in
  the 1–5 prior-match band in any fold). Coordinator
  recomputed the pooled numbers from results_dev.json
  exactly. Virgin 2025/2026 (n=264) NOT read — `virgin()`
  refuses by design (exercised: raises RuntimeError); no
  virgin files. The failure is a near miss on one leg
  only: the 1X2/RPS wins are the largest of any
  scores-only league so far (LL −0,033, RPS −0,011), but
  the totals distribution loses on the 2.5 line, driven
  mainly by the 2023/2024 Apertura fold (OU 0,764 vs
  0,700). S/C/T/K NOT BUILDABLE: target in 0/1,448
  payloads; K: 593 Card events, ALL dismissals (Red 449,
  YellowRed 144, 0 plain Yellows); referee empty 1,448/
  1,448. Levels (regular phase, completed n=1,211): 2,51
  goals/match, home 1,34 vs away 1,17, H/D/A .400/.286/
  .314, Over-2.5 46,2%, BTTS 50,5% — mid-scoring, much
  flatter home advantage than Ghana (57% home wins).
  Traits: attack split-half r=.37, defence r=.36 pooled
  (season-year: .46/.41) — both moderate. Frozen goals 1H
  share 0,4335 (1,313/3,029; excess variance −0,0042,
  split-half r=−0,076 → presentation only). Format:
  Apertura/Clausura split seasons (own sub-ids under parent
  335), 12 teams (11 in 2024/2025), regular phase only
  modelled (MX precedent; 122 playoff rows excluded);
  2022/23 Apertura shortened (67 regular), 2022/23
  Clausura playoffs stop after 5 QF matches, 2026/27
  Apertura in progress (reserved confirmatory). Teams keyed
  by FotMob id (19 ids; renames incl. Once Deportivo→
  Hercules). X2 dropped — no Salvadoran sibling. Nothing
  ships; no join.
- 2026-11-10 15:29 — **IR-AzadeganLeague COMPLETE (league
  #111): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged
  76e60493; branch build/ir-azadegan-league, commits
  29f33384/3eab6893/23cf1515/dfc5fafa — prereg before
  fitting; diff 24 files, all under league/
  IR-AzadeganLeague/). **G-IRAZ FAIL at dev gate**: pooled
  dev n=884 — Gate Zero wins 1X2 LL (1,0471 vs clim
  1,0678) and RPS (0,2031 vs 0,2099) but loses OU2.5
  (0,6337 vs 0,6079) in ALL THREE dev seasons; SHRINK ≡
  Gate Zero (0 of 884 lambdas changed). Coordinator
  recomputed the pooled numbers from results_dev.json
  exactly. Virgin 2025/26 (n=305) NOT read — sentinel
  `{"virgin_read": false}` only. (Full substance recorded
  in the 15:12/15:16 ledger entries; the blocked commits
  23cf1515 + dfc5fafa were made by the coordinator from the
  verified worktree after git writes recovered ~15:21 WIB.)
  Nothing ships; no join.
- 2026-11-10 15:16 — **⚠️ EPERM RECURRENCE (second episode
  today): git loose-object writes failing, IR-AzadeganLeague
  merge BLOCKED.** Builder session hit it ~07:57 WIB
  (Codex `failed to register synthetic bubblewrap mount
  target /tmp/.git`; since then every exec-path content
  write silently persists as 0 bytes, `git add`/`git commit`
  → `fatal: unable to write loose object file: Operation
  not permitted`). Coordinator session confirms the same
  fault at 15:05–15:16 WIB (`git add`, `git hash-object -w`,
  python writes all fail/truncate; `touch` metadata ops
  still work; `LD_PRELOAD=~/workspace/modeshim.so` does NOT
  fix this variant). **93 garbage `tmp_obj_*` files cleaned
  from `.git/objects/`** (failed loose-object attempts
  accumulated today). IR build itself is DONE and VERIFIED
  (see entry below); only its final commit + merge are
  blocked. Counter stays 110 until the merge lands. **No
  new build launch until git writes recover** (a new builder
  could not checkpoint); in-flight builders/joins continue
  their file work (muse.write path unaffected) but cannot
  commit either — re-check their commit state at recovery.
  Retry order at recovery: (1) commit IR engine+verdict on
  build/ir-azadegan-league, force-add results_dev.csv,
  merge as #111; (2) commit this ledger; (3) refill the
  5th build slot from the frozen queue.
- 2026-11-10 15:12 — **IR-AzadeganLeague COMPLETE in
  substance: 0 PASS / 1 FAIL / 4 NOT BUILDABLE — commits
  STAGED, merge pending write recovery (see EPERM entry
  above).** Branch build/ir-azadegan-league, tip 3eab6893
  (prereg, committed before any fitting); steps+data commit
  29f33384. Engine + verdict verified on disk in
  ~/workspace/wt-ir-azadegan-league (files non-zero,
  content-checked): `league/IR-AzadeganLeague/engine/goals/`
  (dc.py byte-identical to NLTD, arms.py, harness.py,
  run_g_iraz.py, README.md, results_dev.json/csv,
  results_virgin.json sentinel) + `reports/
  G_IRAZ_VERDICT.md`. **G-IRAZ FAIL at dev gate**: pooled
  dev n=884 (2022/23–2024/25) — Gate Zero wins 1X2 LL
  (1,0471 vs clim 1,0678) and RPS (0,2031 vs 0,2099) but
  loses OU2.5 (0,6337 vs 0,6079) in ALL THREE dev seasons;
  SHRINK ≡ Gate Zero (0 of 884 lambdas changed). Coordinator
  recomputed the pooled numbers from results_dev.json
  exactly (1,0471/0,2031/0,6337 vs clim 1,0678/0,2099/
  0,6079). Virgin 2025/26 (n=305) NOT read — sentinel
  `{"virgin_read": false}` only; no predictions, no fitted
  params; 2026/27 partial (n=68) reserved confirmatory.
  Mirror image of NLTD: there the over-rate baseline was
  strong; here the under-rate baseline (29,4% over in scored
  dev) is strong and DC totals run systematically too high.
  S/C/T/K NOT BUILDABLE: no SOT/corners/shots target in any
  season; K: 0 Yellow events in 1,564 matches (reds
  0,085/match, split-half r=0,07). Levels: 1,97/1,90/1,94/
  1,77/**1,60 virgin**/1,79 partial goals/match; OU2.5
  33,4/31,6/31,7/25,2/**22,6**/29,4% — one of the
  lowest-scoring leagues in the program, falling steadily
  into the virgin season. Draws 35,2% pooled dev. Traits:
  GF split-half r=0,27 chronological / 0,38 random-60-rep
  (WEAK); GA r=0,51/0,53 (SIGNAL). Format: double
  round-robin, 34 rounds, 18 teams (17 in 2022/23, 16 in
  2026/27 partial); ~6 entrants/season, 42 team ids; 3
  renames on stable ids. Coverage verified from all 1,564
  payloads: stats 0, shotmap 0, lineup 0, referee 0;
  events in 1,261 (80,7%); goal events reproduce FT score
  in 1,258, 3 mismatches flagged (3863817, 4159522,
  4321829) with HT set to NaN. Frozen goals 1H share 0,415
  (true variance −0,00411, split-half r=−0,083 — noise,
  constant for reporting only). Features: X1 DROPPED (no
  xG); X2 DROPPED (scope + evidence: pooled dev entrant
  gaps GF +0,002 / GA −0,034, n=18 teams/600 team-matches —
  entrants at league mean); X3/X4/X6, X5, X7/X9, X8 all
  DROPPED (no xG/shotmap/stats/referee). **⚠️ Persian Gulf
  flag — brief premise WRONG:** the brief stated Iran has
  no other league in the warehouse, but **Persian Gulf Pro
  League (FotMob 523) has 1,245 indexed rows** across the
  same six seasons. The builder correctly used NONE of it
  (no prior, no feature, no gate input) and the
  within-league evidence gives no X2 magnitude anyway. An
  X2 amendment would need a fresh prereg + coordinator
  decision — NOT taken now. Persian Gulf itself remains in
  the frozen queue as its own league to build; future briefs
  must not repeat the "no Iranian sibling" claim. Nothing
  ships; no join. (Counter moves to 111 on merge.)
- 2026-11-10 14:50 — **PL-IILiga COMPLETE (league #109):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged 5a5bee86;
  branch build/pl-ii-liga, commits 68ae692b/bc16c516/
  415768db — prereg before fitting; diff 23 files, all
  under league/PL-IILiga/). **G-PL-II FAIL at dev gate**:
  pooled dev n=927 — Gate Zero loses ALL THREE legs (1X2
  LL 1,085122 vs clim 1,073300; RPS 0,233701 vs 0,229922;
  OU2.5 LL 0,711110 vs 0,692977); SHRINK ≡ Gate Zero
  exactly (0 teams in the 1–5 prior-match band every
  season; 0-prior teams 7/6/6; the two returning teams with
  priors carry a full 34 matches each). Per-season model
  worse every dev season on LL and OU2.5. Coordinator
  recomputed all 12 dev cells from results_dev.csv with an
  independent driver (production model_v2.DC directly):
  match to <1.2e-14. Virgin 2025/2026 (n=309) NOT read — no
  virgin/prediction/fitted-params files exist. Diagnosis: a
  level failure — predicted mean total goals 2,48–2,49 vs
  actual 2,63–2,81; mean P(over 2.5) 0,4497 vs actual
  0,5200; 39% churn (7 of 18 teams new every season) meets
  the DC's a=d=0 anchor (λ_H≈1.23–1.26, λ_A=1.00 vs league
  1.52/1.25), with 33–39% of target appearances on that
  anchor. S/C/T/K NOT BUILDABLE: stats null 1,679/1,679;
  shotmap empty 1,679/1,679; no referee, no period splits.
  Event feed has zero plain-Yellow Card events (173 Red +
  192 YellowRed only) — documented, not treated as missing
  data. Format: 18 teams/season; 306 regular + 3 promotion-
  playoff matches per complete season; `2. Division` (196
  matches) is a mid-season 2021/22 rename of the regular
  season; B teams ordinary (391 matches, 25.3%); frozen
  goals 1H share 0.4270 (n=1,522 validated; split-half
  r=−0.180, true variance ≈0); X2 measured not consumed
  (relegated −0.057/−0.060 n=9, from-below +0.113/−0.023
  n=12). Two brief-vs-Codex discrepancies resolved in
  Codex's favour with cause found (B-team GF/GA 1.315/1.592
  per-appearance, n=409; newcomer gaps are mean-of-per-row-
  gaps); docs corrected, builders re-run byte-identical.
  Nothing ships; no join. **Build slot refilled:**
  Costa Rica Primera Division (FotMob 121, 1,350 matches —
  id verified from the warehouse index) launched on branch
  build/cr-primera-division; build lane back at 5/5.
- 2026-11-10 14:50 — **CN-LeagueOne FOLDED (league #110):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (EXTERNAL — Muse-2;
  merged by Jarvis a1000bbc; row in league/
  EXTERNAL_MERGES.md). **G-CN FAIL at dev gate**: pooled
  dev n=786 — Gate Zero beats climatology on 1X2 LL
  (1,0286 vs 1,0886) and RPS (0,2096 vs 0,2293) but loses
  the OU2.5 leg (0,6927 vs 0,6919 — miss ≈0,0007);
  SHRINK identical. Coordinator recomputed the pooled
  numbers from results_dev.json in the merged tree exactly.
  Virgin 2025 NOT read — no results_virgin.json exists.
  S/C/T/K NOT BUILDABLE (plain Yellow events 0 in all
  1,572 matches). **Id correction:** the merge row
  initially carried FotMob id 8970 (that's FR-Ligue3);
  Jarvis fixed it to **9137** in commit 528048c3 —
  configs are authoritative, 9137 is used here. Nothing
  ships; no join.
- 2026-11-10 14:48 — **External lane: BY-PremierLeague
  (Belarus Premier League, FotMob 263) assigned EXTERNALLY
  to Muse-2 — SKIP locally.** It was next in the local
  queue (1,394 matches); the local slot went to Costa Rica
  Primera Division (121) instead. FR-Ligue3 (8970) still
  in progress externally.
- 2026-11-10 14:46 — **PT-Liga3 COMPLETE (league #108):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged ae3c7756;
  branch build/pt-liga3, commits ff3a5b07/d88320fb/
  1ddac2d6/f2d4dbde — prereg before fitting — plus
  coordinator commit 8d747543 force-adding the
  results_dev.csv the builder omitted; diff 24 files, all
  under league/PT-Liga3/). **G-PT3 FAIL at dev gate**:
  pooled dev n=929 — Gate Zero loses ALL THREE pooled
  comparisons (1,081779 vs clim 1,077696; RPS 0,229541 vs
  0,228739; OU2.5 LL 0,703742 vs 0,686441); SHRINK ≡ Gate
  Zero in every season (0 teams in the 1–5 prior-match band
  at any season start). Per-season 1X2 LL vs climatology:
  2022/23 wins (1,0597 < 1,0758), 2023/24 + 2024/25 lose;
  OU leg loses in all three seasons — the FAIL is not
  marginal. Coordinator recomputed the pooled numbers from
  results_dev.json per-season rows exactly. Virgin 2025/26
  (n=296) NOT read — only a `{"virgin_read": false}`
  marker; confirmatory 2026/2027 (n=90) reserved.
  S/C/T/K NOT BUILDABLE: stats None in all 1,647 payloads;
  shotmap 0 shots; no xG, no named referee (0/1,647), no
  period splits. Index says 1,652 rows; **1,647 finished —
  5 index rows are unstarted shells** (finished=false,
  started=false, placeholder 0-0) — excluded, asserted by
  the builder. Card events are a coverage break, not a
  target: plain Yellows 0, 0, 2, 303, 1,207 by season
  (2021/22 feed records dismissals only). Format: zones +
  promotion/relegation groups + 1 Championship Final;
  2026/27 in progress, zones only. Levels: 2,53 → 2,23
  goals/match (2025/26 dip is the lowest season); NO halves
  constant frozen (descriptive 1H share 0,4366), FT-only.
  X2 DROPPED (direct Liga Portugal ↔ Liga 3 movers = 0 in
  every transition; Liga 3 ↔ Liga Portugal 2 only 1–3 per
  transition — too small/unstable). **Bug caught by the
  builder:** Codex's `compute_eda.py` counted matches with
  ANY Card event as event-yellow matches — fixed to ≥1
  event yellow (0, 0, 2, 73, 289, 8); eda_summary.json +
  charts regenerated, all other numbers unchanged. Nothing
  ships; no join. **Build slot refilled:** Guatemala Liga
  Nacional (FotMob 336, 1,443 matches — id verified from
  the warehouse index) launched on branch
  build/gt-liga-nacional; build lane back at 5/5. **Standing
  reminder added to the GT brief (second omission in a row):
  results CSVs are TRACKED — force-add with `git add -f`.**
- 2026-11-10 14:43 — **GH-PremierLeague COMPLETE
  (league #107): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged 380efe0c; branch build/gh-premier-league, commits
  3b5f2033/577fae30/9926413a/b711a58f/2d87e779 — prereg
  before fitting; diff 25 files, all under league/
  GH-PremierLeague/). **G-GH FAIL at dev gate**: pooled dev
  n=901 — Gate Zero loses ALL THREE legs (1X2 LL 0,9728 vs
  clim 0,9653; RPS 0,1923 vs 0,1914; OU2.5 LL 0,6559 vs
  0,6331); SHRINK identical to Gate Zero on all 901 rows (0
  teams in the 1–5 prior-match band — same structural
  finding as RU2/NG). Model beats climatology on LL/RPS
  only in the 2024/2025 fold. Coordinator recomputed the
  pooled numbers from results_dev.csv exactly. Virgin
  deliberately NOT read — `virgin()` raises RuntimeError
  (exercised); no results_virgin.json, no fitted params, no
  virgin predictions; confirmatory 2026/2027 (90 matches)
  stays reserved. S/C/T/K NOT BUILDABLE: no stats/shotmap
  anywhere; K: 177 Card events, ALL dismissals, referee
  empty. Levels: **2,02 goals/match — lowest-scoring league
  built so far** (home 1,35 vs away 0,67; H/D/A
  57,1/26,6/16,3%; Over 2.5 32,9%); attack trait split-half
  r=−0,03 (trait-free), defence r=0,32. Halves goals 1H
  share frozen 0,4622 (excess variance −0,0009). **23
  awarded 3-0 forfeits excluded** (Nsoatreman 14 straight
  from 2025-03-16, Hohoe United 7 straight from 2026-04-03
  — mid-season withdrawals — plus 2 singles; one awarded
  row is direction-reversed in the source, excluded, flip
  flagged not repaired). `general`/`header` null in EVERY
  payload — unique in the program; teams keyed by name (32
  names, stable), no team ids exist. 4 event-feed errors
  flagged ht_suspect; round-33 2024/2025 Holy Stars vs
  Nations FC absent from the warehouse entirely. Nothing
  ships; no join. **Build slot refilled:** El Salvador
  Primera Division (FotMob 335, 1,448 matches — id verified
  from the warehouse index) launched on branch
  build/sv-primera-division; build lane back at 5/5.
- 2026-11-10 14:41 — **PL-ILiga COMPLETE (league #106):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged 31f972a1;
  branch build/pl-i-liga, commits 8dd2c1d3/4f9c42bc/
  dbb6c669/e14be495 — prereg before fitting — plus
  coordinator commit f5805f36 force-adding the
  results_dev.csv the builder omitted; diff 27 files, all
  under league/PL-ILiga/). **G-PL-ILiga FAIL at dev gate**:
  pooled dev n=918 (regular only; playoffs excluded) —
  Gate Zero loses ALL THREE legs (1,092210 vs clim
  1,087656; RPS 0,231355 vs 0,229661; OU 0,701717 vs
  0,695877); SHRINK identical (0/918 lambdas changed);
  model beats climatology in only 1 of 3 dev seasons
  (2024/25). Coordinator recomputed the pooled numbers
  from results_dev.json per-season rows exactly (and from
  the force-added CSV). Virgin 2025/26 (n=306, the hottest
  season at 2,981 goals/match, OU2.5 0,599) NOT read — no
  results_virgin.json, no predictions, no fitted virgin
  params; harness asserts against any virgin load. S/C/T/K
  NOT BUILDABLE: no stats feed and no shotmap in ANY of the
  1,671 payloads; cards: 358 Card events are Red (202) +
  YellowRed (156) only, ZERO plain Yellows — dismissals
  0,21/match are a rejected rare-event target; YellowRed
  collapses in 2025/26 (49 Red / 1 YellowRed vs 44/24) —
  apparent reclassification. X2 DROPPED (newcomer gaps pooled
  +0,059 GF / +0,05 GA, signs flip per transition).
  Levels: 2,695 goals/match; halves goals 1H share frozen
  0,457 (true var −0,0033). Format: 18 teams, 34 rounds +
  3 promotion-playoff matches/season (excluded). Nothing
  ships; no join. **Build slot refilled:** Romania Liga II
  (FotMob 9113, 1,513 matches — id verified from the
  warehouse index) launched on branch build/ro-liga2;
  build lane back at 5/5.
- 2026-11-10 14:34 — **NL-TweedeDivisie COMPLETE (league #104): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged 203365ea; branch build/nl-tweede-divisie, commits
  b85d8f15/c3380916/ff60bf34/2d236187 — prereg before fitting;
  diff 24 files, all under league/NL-TweedeDivisie/).
  **G-NLTD FAIL at dev gate**: pooled dev n=918 — Gate Zero
  beats climatology on 1X2/RPS in ALL THREE seasons
  (pooled 1,0353 vs 1,0645; RPS 0,2289 vs 0,2406) but loses
  the OU leg in all three (pooled OU 0,6890 vs 0,6628);
  SHRINK bit-identical to Gate Zero (max diff 0.0); X2
  genuinely ran (lambdas changed in exactly 256/918
  matches) and fails the same OU leg (0,6851). Coordinator
  recomputed the pooled numbers from results_dev.csv exactly.
  Virgin 2025/26 (n=306) NOT read — only a
  `{"virgin_read": false}` marker file exists. S/C/T/K NOT
  BUILDABLE: no stats/shotmap anywhere (1,638/1,638); 0
  Yellow events in 1,638 matches; reds 0,145/match, trait
  r=−0,09. Levels: 3,24 goals/match pooled (highest Dutch
  tier in the warehouse; over-2.5 63,2% — the base rate is a
  hard bar, which is why the OU leg kills it). Halves goals
  1H share frozen 0,436 (true variance −0,0054). X2 ADOPTED
  (gated): below-tier entrant prior GF −0,093 / GA +0,181,
  dev-only pooled (virgin transition deliberately excluded
  — stricter than the Eerste precedent). Format: 18 teams,
  34 rounds; NO promotion/relegation with Eerste Divisie
  (0/13 entrants from Eerste). Nothing ships; no join.
  **Caveat (audit item):** `run_g_nltd.py virgin-predict`
  has no dev-gate check (same sharp edge as the NL
  reference) — never run for this league; the virgin
  marker proves it was not run.
- 2026-11-10 14:34 — **FI-Ykkonen FOLDED (league #105,
  EXTERNAL — Muse-2): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged locally by Jarvis, commit 3fe28dd; row in
  league/EXTERNAL_MERGES.md, now marked folded). **G-FI
  FAIL dev gate**: pooled n=1,010 — Gate Zero loses ALL
  THREE legs (1,0747 vs clim 1,0420; RPS 0,2437 vs 0,2355;
  OU 0,7026 vs 0,6485); SHRINK identical; X2 improves all
  three pooled metrics (1,0660/0,2404/0,6940) but fails the
  dev gate itself. Coordinator checked the pooled numbers
  against results_dev.json in the merged tree (exact).
  Split per the board answer (option A): dev ≤ 2024 as-is,
  virgin 2025 NOT read — no results_virgin.json exists.
  S/C/T/K NOT BUILDABLE. Nothing ships; no join.
  **Passing markets program-wide still 120.**
  **Build slot refilled:** Iran Azadegan League (FotMob
  9372, 1,564 matches — id verified from the warehouse
  index) launched on branch build/ir-azadegan-league;
  build lane back at 5/5.
- 2026-11-10 14:34 — **EXTERNAL: FR-Ligue3 (France Ligue
  3, FotMob 8970) NOW ASSIGNED EXTERNALLY** — SKIP locally;
  removed from the local frozen queue (it was next after
  Iran Azadegan). CN-LeagueOne (9137) still in progress
  externally. Next local: Romania Liga II (9113, 1,513) →
  El Salvador Primera Division (335, 1,448) → Guatemala
  Liga Nacional (336, 1,443).
- 2026-11-10 14:23 — **CN-SuperLeague JOINED the daily runner
  (runner 42/93)** (merged 8ac12649; branch build/runner-cn,
  tip 2600056d — single commit, ONLY
  league/runner/{run_daily.py, active.yaml, README.md}, 201
  insertions / 4 deletions; no world-index line added). Markets:
  SOT GZ 9.5 prov (halves 0,4580, ratio_prior 200 explicit,
  team_key: id, exclude_seasons 2021/2022), cards gate_zero
  3.5 prov (halves 0,3328, exclude 2021/2022, NO cards_actual
  — gate graded the stats feed), total_shots arm B 26.5 prov
  (halves 0,4594, exclude 2021/2022). Virgin arbiters: SOT
  replay max diff 7.4e-15; cards 0.0; total-shots B 3.3e-9.
  Proof: two full runs, 11,825 predictions each, zero errors,
  fetched_new=0 everywhere; 448/449 files bit-identical (the
  exception is the known pre-existing ZA-PSL corners daily —
  same case as the CL join; FT values bit-equal to run 1's
  ledger on all 160 fixtures). First run-2 attempt SIGTERM'd
  after 24 leagues (no errors); completed rerun followed.
  CN's 2026 season is complete (240/240), so both runs predict
  ZERO CN fixtures — expected off-season state; adapters were
  exercised on a synthetic 2027-01-15 fixture (recompute 0.0
  in all three markets) + synthetic settlement (SOT 12.0,
  cards 2.0, total shots 37.0, each settled exactly once).
  **Three opt-in adapter amendments** (all default-inert,
  inertness probed on ES SOT / NL SOT / AU cards / SCO
  total-shots B): SOT exclude_seasons + int-cast of fixture
  ids under team_key: id when history keys are ints; cards
  yellow_cards_home/away fallback when the yellow_home alias
  is absent + exclude_seasons; total-shots arm B half_split
  fallback to halves_share_1h (CL arm-A pattern extended).
  **Defects, stated plainly:** (1) CN's data builder asserts
  hard equality len(rows)==1442 — MUST become a floor before a
  2027 season is added to the config, or the first daily
  rebuild fails (recorded in the runner README; not fixed
  here — join commit is runner-files-only); (2) the CN builder
  ignores the runner's INDEX/MAIN_REPO globals (its own
  argparse --warehouse-root coincides with the worktree root,
  so rebuilds work — not the established contract); (3) CN
  cards CSV has no yellow_home alias (handled by the fallback,
  not a builder change); (4) no nan strings, all markets
  id-keyed — no diacritic issue. **Final-audit note:** the
  cards fallback CHANGES behaviour for any cards league whose
  CSV lacks the yellow_home alias (builder claims only CN
  lacks it) — audit should re-verify the full active.yaml
  against every league's frozen config. No runner files had
  changed on main since the branch base, so the branch's own
  two-run proof stands for the merged state (CL precedent).
  **Join slot refilled:** CY-1Division join launched (brief
  ~/workspace/agent-briefs/runner-cy-join.md; branch
  build/runner-cy @ wt-runner44) — corners GZ 9.5 clean +
  total_shots arm A 18.5 prov, both FT-only.
- 2026-11-10 14:23 — **EXTERNAL UPDATES (Jarvis steering,
  14:20):** (1) UY-LigaAUF fold CONFIRMED already done —
  the steering arrived after the fold (ledger 01278b0b, #103);
  no action. (2) FI-Ykkonen's split question answered on the
  board: **option A, dev ≤ 2024 as-is**; Muse-2 proceeds to
  prereg — still SKIP locally. (3) **CN-LeagueOne (China
  League One, FotMob 9137) NOW ASSIGNED EXTERNALLY** — SKIP
  locally; removed from the local frozen queue (it was next
  after Ghana). Queue recompute: next local is France Ligue 3
  (8970, 1,570) → Iran Azadegan (9372, 1,564) → Romania Liga
  II (9113, 1,513); 46 local candidates remain (excludes the
  5 production top-5 ids that also sit in the index). (4)
  **Near-miss recorded:** Poland II Liga (8935) was nearly
  assigned externally by mistake; the live in-flight check
  caught it — it stays local (in flight). Lesson stands:
  external picks must be re-checked against live ledger/git
  log immediately before posting.
- 2026-11-10 14:18 — **UY-LigaAUF FOLDED (league #103,
  EXTERNAL — Muse-2): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged locally by Jarvis, commit 0f0009f5; row in
  league/EXTERNAL_MERGES.md, now marked folded). **G-UY
  FAIL dev gate**: pooled n=895 — Gate Zero 1X2 LL 1,0705
  vs climatology 1,0939 (beats), RPS 0,2228 vs 0,2305
  (beats), **OU2.5 LL 0,6869 vs 0,6806 (loses — the OU leg
  alone)**; ENTRANT also fails (1,0753/0,2244/0,6858,
  sign check 0/3). Coordinator checked the pooled numbers
  against results_dev.json in the merged tree (exact).
  Virgin 2025 (n=300) NOT read — no results_virgin.json
  anywhere. S/C/T/K NOT BUILDABLE (scores-only; K-UY
  event-yellows break inside dev, zero plain Yellows in
  dev AND virgin). Nothing ships; no join. **Passing
  markets program-wide still 120.** FI-Ykkonen (8969)
  remains the only live external assignment — still SKIP
  locally.
- 2026-11-10 14:17 — **HANDOFF TERTUNDA DITERIMA (AR-PBM +
  ES-PF):** laporan resume kedua builder tiba belakangan,
  setelah kedua liga sudah diverifikasi + merge (#100/#101)
  — tidak ada perubahan verdict. Resume-builder AR
  memverifikasi independen penuh (re-run harness
  byte-identik, klimatologi dihitung ulang s.d. 1e-9);
  resume-builder ES memverifikasi ulang semua klaim
  (replay production DC 0,000000). **Dua item audit kecil
  baru:** (1) harness PBM melipat leg (iii) ke dalam flag
  `dev_gate_pass` X2, padahal prereg menyimpannya sebagai
  kondisi tahap virgin; (2) trailing-10 PBM mewarisi rho DC
  hasil fit, sedangkan FEDA memakai rho=0 — baseline saja,
  gerbang membandingkan ke klimatologi. **Catatan proses:**
  sesi builder ES lama ternyata masih hidup di worktree
  yang sama saat resume berjalan — dua sesi menyentuh
  worktree bersamaan, tanpa konflik/duplikat commit, tapi
  pola ini harus dihindari (resume hanya setelah sesi lama
  dipastikan mati).
- 2026-11-10 14:16 — **NG-ProfessionalLeague COMPLETE
  (league #102): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged fba7093c; branch build/ng-professional-league,
  commits f45177d7/0533cf38/2b11eb46 — prereg before fitting;
  diff 25 files, all under league/NG-ProfessionalLeague/).
  **G-NG FAIL at dev gate**: pooled dev n=939 — Gate Zero
  loses ALL THREE legs (1X2 LL 0,887088 vs clim 0,874318;
  RPS 0,167613 vs 0,163259; OU2.5 LL 0,668512 vs 0,649374);
  SHRINK identical to Gate Zero on all 939 dev rows (the
  1–5 prior-match band never occurs under season-blocked
  fitting — same structural finding as G-RU2). Coordinator
  recomputed the pooled numbers from results_dev.json
  exactly. Virgin 2025/26 NOT read — zero virgin files.
  S/C/K/T NOT BUILDABLE (scores-only). Nothing ships; no
  join. **Passing markets program-wide still 120.**
  **Build slot refilled:** Ghana Premier League (FotMob
  522, 1,619 matches — id verified from the warehouse
  index) launched on branch build/gh-premier-league; build
  lane back at 5/5. Next in the frozen queue: China League
  One (9137, 1,572).
- 2026-11-10 14:14 — **ES-PrimeraFederacion COMPLETE
  (league #101): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged db25791b; branch build/es-primera-federacion,
  tip 3a57c204 — prereg 1750d713 precedes all fitting;
  diff 23 files, all under league/ES-PrimeraFederacion/).
  **G-ESPF FAIL at dev gate**: pooled dev n=2,322 — Gate
  Zero 1X2 LL 1,0834 vs climatology 1,0784, RPS 0,2209 vs
  0,2197, OU2.5 LL 0,6856 vs 0,6766 (loses ALL THREE legs);
  SHRINK bit-identical to Gate Zero (prior counts 0 or ≥38
  at season starts); X2 genuinely ran (id-keyed movers =
  EDA name-keyed lists, 4+10 per dev season) and fails all
  three pooled legs too (1,0835/0,2207/0,6845). Coordinator
  recomputed the pooled numbers from results_dev.json
  exactly (n-weighted means). Virgin 2025/26 (n=772) NOT
  read — only a `{"virgin_read": false}` marker file exists.
  Diagnosis: level swings year to year (2,41→2,22→2,23→
  2,41 goals/match) lagged by the 270d-decay DC; 2024/25
  draw-heavy (31,9%). S/C/T/K NOT BUILDABLE (scores-only,
  no stats/shotmap anywhere). Nothing ships; no join.
- 2026-11-10 14:13 — **🏁 MILESTONE #4 — 100 LEAGUES
  COMPLETE** (milestones reported = 4; next at 125).
  Leagues 76–100: IS-BestaDeildin (3 prov), MA-BotolaPro
  (0), EC-SerieA ext (0), RS-SuperLiga ext (0),
  MX-ExpansionMX (0), BR-SerieC (0), IL-LigatHaAl ext
  (0), QA-QatarStars ext (0), BO-PrimeraDivision (0),
  EE-Meistriliiga (0), SA-FirstDivision (1 clean),
  CZ-FNL (0), LV-Virsliga (1 clean), FI-Ykkosliiga (0),
  CO-Superliga (0 buildable), DK-2Division (0),
  VE-PrimeraDivision (0), QA-SecondDivision (0),
  NO-2Divisjon ext (0), RU-SecondLeague (0),
  AR-PrimeraBNacional (1 prov), SE-Ettan ext (0),
  GR-SuperLeague2 (0), IQ-StarsLeague (0),
  AR-PrimeraBMetropolitana+TorneoFederalA (0). Block
  tally: **6 passing markets** (IS 3, SA-1 SOT clean, LV
  SOT clean, AR-B cards X8 provisional); **goals 0 in the
  block** — the OU-2.5 calibration leg killed every goals
  candidate again. Passing markets program-wide: 120.
- 2026-11-10 14:13 — **AR-PrimeraBMetropolitana +
  TorneoFederalA COMPLETE (league #100): 0 PASS / 2 FAIL
  / S/C/K/T NOT BUILDABLE** (merged c7106b71; branch
  build/ar-primera-b-metropolitana, tip b31b1ac7 — prereg
  455bc43d precedes all fitting; diff 46 files, all under
  league/AR-PrimeraBMetropolitana/ +
  league/AR-TorneoFederalA/). This is the RELAUNCHED
  builder from the 14:04 interruption note — it completed
  from the frozen prereg checkpoint. **G-PBM FAIL at dev
  gate**: pooled n=1,426, Gate Zero loses ALL THREE legs
  (1,106952 vs clim 1,090260; RPS 0,225085 vs 0,220036;
  OU 0,664004 vs 0,649267); X2 same legs fail. **G-FEDA
  FAIL at dev gate**: pooled n=2,083, Gate Zero beats
  climatology on 1X2/RPS (1,015285/0,203167 vs
  1,028908/0,207592) but loses the OU leg (0,667651 vs
  0,648767). Coordinator recomputed both pooled sets
  from results_dev.csv exactly. Virgins (2026, n=462 /
  n=459) NOT read — zero virgin files in either tree.
  S/C/K/T NOT BUILDABLE in both sub-leagues (scores-only).
  Counted as ONE league (single FotMob id 9213). Nothing
  ships; no join.
- 2026-11-10 14:11 — **IQ-StarsLeague COMPLETE
  (league #99): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged b643d5aa; branch build/iq-stars-league, commits
  8eed0f37/0aff0b8b/90eaa904/4c512740 — prereg before
  fitting; diff 24 files, all under league/
  IQ-StarsLeague/). **G-IQSL FAIL at dev gate**: pooled
  dev n=1,104 — Gate Zero 1X2 LL 1,0384 vs clim 1,0955
  (beats), RPS 0,2063 vs 0,2246 (beats), **OU2.5 LL
  0,6949 vs clim 0,6754 (loses in all 3 seasons)**;
  SHRINK ≡ Gate Zero exactly (no club enters a scored
  season with 1–5 prior matches). Coordinator recomputed
  the pooled LL/RPS/OU from dev_predictions.csv exactly
  (1,038356/0,206256/0,694864). Virgin 2025/26 NOT read
  — no virgin file, no predictions dir. Diagnosis: goals
  drifted up (1,98→2,30/match) faster than the 270d-decay
  DC tracks; OU calibration −4,03pp (SE 1,50). S/C/T/K NOT
  BUILDABLE: stats null 2,032/2,032, shotmap empty
  2,032/2,032; events carry Red/YellowRed only, zero
  plain Yellows anywhere. **49 phantom 0-0s** excluded
  (finished=false, started=false, no scoreStr; played
  total 1,983, not 2,032) — builder-caught, coordinator
  verified. F2 split-half bug caught by the builder
  (reported r≈0, corrected to ≈0,77/0,74/0,61 by three
  re-derivations) before the prereg commit. Halves goals
  1H share frozen 0,4323308271 (2024/25 event-verified).
  X2 DROPPED (no other Iraqi league in the warehouse).
  External assignment VOID stands (local build won the
  race; any Muse-2 copy must be rejected as a duplicate).
  Nothing ships; no join. **Passing markets program-wide
  still 120.**
- 2026-11-10 14:14 — **BUILD SLOTS REFILLED (3):**
  Poland I Liga (FotMob 197, 1,671 matches — id verified
  from the warehouse index), Portugal Liga 3 (9112,
  1,652), Netherlands Tweede Divisie (9195, 1,638) —
  all launched on branches build/pl-i-liga, build/
  pt-liga3, build/nl-tweede-divisie. Build lane back at
  5/5 (NG 533, PL-II 8935 + the three new). Next in the
  frozen queue after these: Ghana Premier League (522,
  1,619) → China League One (9137, 1,572). Join lane
  unchanged (CZ SOT fix + CN join, both in proof runs).
- 2026-11-10 14:04 — **GR-SuperLeague2 COMPLETE
  (league #98): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged eb3abe4f; branch build/gr-superleague2,
  commits eab6a435/a72adf0d — Stage 1 + prereg,
  engine+dev+verdict; prereg 06:52 UTC precedes all
  fitting; diff 23 files, all under league/
  GR-SuperLeague2/). **G-GR2 FAIL at dev gate (OU
  leg)**: pooled dev n=1,045 (2022/23–2024/25) — Gate
  Zero 1X2 LL 1,028463 vs climatology 1,077632 (beats),
  RPS 0,211927 vs 0,231084 (beats), OU2.5 LL 0,707253
  vs 0,683044 (**loses**); coordinator recomputed from
  results_dev.json exactly. Fails the OU leg in pooled
  dev AND in every dev season (0,7288 vs 0,6894;
  0,6819 vs 0,6756; 0,7081 vs 0,6832) — the same leg
  and pattern as the parent tier G-GR. SHRINK ≡ Gate
  Zero everywhere (0 teams with 1–5 prior matches in
  any target season; 7/6/5 unseen teams take a=d=0 in
  both arms), so it is moot. Diagnostic: a
  totals-shape failure, not a level failure — pooled
  mean predicted P(over 2.5) 0,4066 vs actual 0,4268
  (gap only +2,0pp), yet per-match over-probabilities
  score worse than a constant. Virgin 2025/26 (n=265)
  NOT read — no virgin file exists. S/C/T/K NOT
  BUILDABLE: `content.stats` null and shotmap empty in
  ALL 1,935 payloads (builder-asserted per payload);
  zero referees named; event cards only 337 in 1,935
  matches with no stats feed to unify against. Format:
  2 groups through 2025/26 (34→30→24→20→20 teams),
  promotion/relegation groups from 2023/24, 2-legged
  playoff final 2021/22, 1-match Super Cup 2024/25–
  2025/26; **2026/27 is a single 16-team group** (79
  matches, in progress, confirmatory only). **B teams
  (frozen: ordinary rows, no feature):** 528/1,935
  matches (27,3%) involve a B team; B teams score
  1,222/concede 1,231 vs league mean 1,152 (gaps
  +0,07/+0,08) — league-average, slightly open (2,455
  vs 2,249 goals/match), identical home-win rate. They
  play in promotion groups (AEK B 2023/24; Asteras B +
  Olympiacos B 2025/26), so no exclusion logic
  applies. **X2 measured, not consumed:**
  SL1-relegated newcomers GF +0,314 / GA −0,288 (n=8;
  dev n=5) vs Gamma/other −0,198/+0,108 (n=25) — a
  single pooled offset would be wrong-signed for both
  groups, and 5 dev movers can't carry a parameter.
  Documented future candidate. Levels: 2,303
  goals/match pooled (lowest in programme; GR 2,54,
  PL 2,67, J1 ~2,7), home 1,335 vs away 0,969; OU2.5
  over-rate 0,422 dev. Goals trait reliability
  0,656/0,710 (55 teams). Frozen goals 1H share
  0,4596 (validated event subset n=1,617, true
  variance −0,0025 ≈ 0). Event feed validates 1,730/
  1,736 matches; 6 feed errors flagged, 35 awarded
  3–0/0–3 no-events results kept as ordinary FT rows.
  Parent id verified: GR-SuperLeague is **135** (the
  brief's correction landed before the builder
  started). Nothing ships; no join.
- 2026-11-10 14:04 — **⚠️ TWO BUILDERS INTERRUPTED —
  BOTH RELAUNCHED from prereg checkpoints.** The
  completion handoff for GR-SuperLeague2 also reported
  two child agents interrupted: (1) **AR-PrimeraB
  Metropolitana & Torneo Federal A (9213)** — branch
  tip 455bc43d (prereg G-PBM + G-FEDA, 06:53 UTC);
  Phase A commits ee4c5bc5/ee11f0cb below it (one per
  sub-league). (2) **ES-PrimeraFederación (8968)** —
  branch tip 1750d713 (prereg G-ESPF, 06:52 UTC);
  steps commit 79b4d106 below it. In both cases the
  interruption came AFTER the prereg and BEFORE any
  fitting — clean resume points; no virgin risk, no
  work lost beyond uncommitted scratch. Replacement
  builders spawned on the SAME branches/worktrees
  (build/ar-primera-b-metropolitana @
  wt-ar-primera-b-metropolitana; build/
  es-primera-federacion @ wt-es-primera-federacion)
  to do Phase B (engines+dev) + Phase C (virgin+
  verdicts) from the frozen preregs. **Build slot
  refilled: Poland II Liga (FotMob 8935) launched**
  (next by n, 1,679 matches, scores-only; parent
  Ekstraklasa verified FotMob 196 from its config).
  Queue recompute: 52 leagues remain (all key 0).
- 2026-11-10 13:51 — **SE-Ettan FOLDED (league #97,
  EXTERNAL — Muse-2): 0 PASS / 1 FAIL / 4 NOT
  BUILDABLE** (merged locally by Jarvis, commit
  70320c35; row in league/EXTERNAL_MERGES.md 13:47,
  now marked folded). **G-SE FAIL dev gate**: Gate
  Zero 1X2 LL 1,0625 vs climatology 1,0596 and naive
  1,1268; RPS 0,2354 vs 0,2380 / 0,2333; OU2.5 LL
  0,7126 vs 0,6834 / 0,7426 — **3/6 legs** (beats
  climatology on RPS only; beats naive on 1X2 and OU);
  SHRINK identical; virgin 2025 NOT read. S/C/T/K NOT
  BUILDABLE (scores-only). **Parked flag (no action
  now):** SE-Ettan's RESULT.md records K-SE
  event-yellows evidence (trait r 0,549, 1H share
  0,2841) flagged for a possible future program
  decision — parked, not blocking. Nothing ships; no
  join. **Passing markets program-wide still 120.**
- 2026-11-10 13:51 — **EXTERNAL: IQ assignment VOID
  CONFIRMED + NEW ASSIGNMENTS (FI-Ykkonen +
  UY-LigaAUF).** Jarvis confirms the IQ-StarsLeague
  (FotMob 524) external assignment is now VOID (the
  coordinator launched it locally after Assignment 10
  was posted — noted in the 13:42 heartbeat) and has
  posted a STOP for Muse-2 on the board — any IQ copy
  he delivers must be rejected as a duplicate of the
  local build (branch build/iq-stars-league, running).
  Two FRESH external assignments are now live, picked
  against the live ledger minutes ago: **FI-Ykkonen
  (Finland Ykkönen, FotMob 8969) and UY-LigaAUF
  (Uruguay Liga AUF Uruguaya, FotMob 161)** — both
  scores-only, goals-only candidates. **SKIP both in
  the local queue** (neither is in flight locally;
  both sit in the remaining-queue tail by n). They will
  arrive the same way (verified merge +
  EXTERNAL_MERGES.md row).
- 2026-11-10 13:42 — **AR-PrimeraBNacional COMPLETE
  (league #96): 1 PASS PROVISIONAL / 1 FAIL / 3 NOT
  BUILDABLE** (merged 0b0fdbb8; branch
  build/ar-primera-b, commits daa34156/cc2264f8/
  6ae1931b/afb5877e — Phase A, prereg, Phase B engines+
  dev, Phase C virgin+verdicts; prereg 06:08 UTC
  precedes all fitting; diff 36 files, all under
  league/AR-PrimeraBNacional/). **K-BNAC X8 SHIPS
  (PROVISIONAL PASS)** — virgin 2026 complete, n=648:
  X8 LL@4.5 0,669291 vs league base 0,692222 and naive
  0,687911 (leg i PASS); calibration |breach| 1,06pp
  (SE 1,92pp) — within 1 SE of the 1,0pp boundary =
  PROVISIONAL (file's diff convention is predicted −
  actual; magnitude identical either way); Gate Zero
  also provisional (LL 0,676939, breach 1,27pp) and X8
  ships on lower LL. Coordinator recomputed from
  results_virgin.json exactly (LL 0,669291, cal
  1,0611pp, SE 1,9191pp). Dev: GZ 0,68025 vs base
  0,69516, naive 0,69079 — PASS; X8 0,65961, beats GZ
  2/2 blocks — PASS. **G-BNAC FAIL at dev gate**: pooled
  n=2,648 — Gate Zero 1X2 LL 1,061652 vs climatology
  1,059995, RPS 0,209918 vs 0,209551, OU2.5 0,638135 vs
  0,623472 — fails ALL THREE legs; X2 also fails
  (1,060282 / 0,636674); virgin NOT read. S/C/T NOT
  BUILDABLE: 0/3,966 payloads have non-empty stats;
  shotmap shots empty in all 3,966 (index
  has_stats=True on 121 rows is a false positive — all
  `Periods.All=None`). Format eras: 2021 zones (17+18
  teams); 2022 single table (37); **2023 asymmetric
  zones** (A 19 teams/38 rounds, B 18/34); 2024 single
  (38); 2025 zones; 2026 single (36, virgin, rounds
  1–36 complete). Cards target exists only from 2023
  (2021–22 event feed has zero `Yellow` events;
  columns NaN, never 0). Referee present 0% in 2021,
  89–99% after. Halves constants (event times,
  group-only): goals 0,435381, yellows 0,390091.
  Levels: 1,97 goals/match pooled dev, 4,76 yellows/
  match 2023+. Movers F4 pooled GF −0,087 / GA +0,036
  (16 transitions; LP↔BNAC moves confirmed both
  directions by team id). Referee split-half r=0,525
  (47 refs). Goals FAIL is real, not a bug: baselines
  recomputed independently to 6dp; 2024 model
  over-predicted Over 2.5 by 8,06pp (0,3714 vs 0,2909
  actual) as levels fell to 1,78 goals/match. Builder
  review catches (fixed before the affected gate,
  prereg untouched): yellows halves rebuilt group-only
  (0,390091, n=1,954 — playoffs had leaked in);
  X8 arm fixed to the AR form (decayed HL-270 rate +
  <8 → 1,0) after a prereg deviation (dev re-run
  before virgin read; fixed X8 dev LL 0,65961 vs buggy
  0,66241); snapshot def_home/def_away shrinkage means
  swapped vs predict() — fixed. **Passing markets
  program-wide now 120. K-BNAC X8 is the FOURTH
  shipped referee arm** (DE-2 stopped, PL stopped at
  the operational gate; AU-W X8 still queued 12th) —
  **its join QUEUES 16th (after LV SOT) and the
  operational gate (referee appointments present
  pre-match in FotMob's pull for upcoming fixtures)
  MUST run before it ships.** **Build slot refilled:
  Nigeria Professional Football League (FotMob 533)
  launched** (next by n, 1,830 matches, scores-only;
  no built Nigerian sibling — X2 unavailable by
  default).
- 2026-11-10 13:36 — **RU-SecondLeague COMPLETE
  (league #95): 0 PASS / 1 FAIL / 4 NOT BUILDABLE**
  (merged 41220849; branch build/ru-second-league,
  commits 8f3c08cf/089980b3 — prereg+steps, engine+dev;
  prereg 06:24 UTC precedes all fitting; diff 24
  files, all under league/RU-SecondLeague/).
  **G-RU2 FAIL at dev gate**: pooled dev n=3,284 —
  Gate Zero 1X2 LL 1,084956 vs climatology 1,076319
  (**loses**), RPS 0,233237 vs 0,233355 (beats by
  0,000118), OU2.5 LL 0,711812 vs 0,696273 (**loses**);
  coordinator recomputed from results_dev.json exactly.
  SHRINK ≡ Gate Zero on all 3,284 dev rows (0 differing
  predictions — the 1–5 prior-match band never occurs
  under date-cutoff fitting, same finding as G-RU1).
  Worst fold is 2023/2024 Division A (LL 1,188 vs
  clim 1,097; model over-predicts away goals 1,037 vs
  actual 0,928 in the 2,21-goals season). Virgin
  (888 matches, labels 2026 + 2026/2027) NOT read —
  no virgin file exists. S/C/T/K NOT BUILDABLE:
  `content.stats` empty in 6,558/6,558 payloads;
  shotmap empty 6,558/6,558; referee empty 6,558/6,558.
  K: no yellow target — 959 Card events are all
  dismissals (YellowRed 624, Red 335, **0 plain
  Yellows**); events absent entirely from all 2,402
  rows from 2024/2025 onward. Format frozen in prereg:
  FotMob 9123 is a parent id over 44 sub-tournaments;
  Division A (autumn–spring, Gold/Silver) + Division B
  (calendar year, 4 groups) from 2023, pre-2023 FNL 2
  groups. Pooled DC, no group/stage/track feature;
  only 4 virgin matches (2026 Final Four) are
  cross-group. **1,181 phantom fixtures**
  (started=False, placeholder 0-0) and **50 awarded
  matches** (37 recorded 0-0 despite Goal events;
  concentrated on Yessentuki 13, Sokol Kazan 13,
  Irkutsk 12) excluded from every fit/score. **Season
  2025 excluded entirely** — harvest fragment, 42/842
  finished, mean 1,38 goals, 43% 0-0. X2 with the
  CORRECTED ids (63/338): 9 relegated entrants from
  1. Division (338), 0 from Premier League (63; team
  ids verified stable, e.g. Alania 268557 in both);
  pooled first-season gaps GF −0,079 / GA −0,021 — no
  hard-coded offset, SHRINK is the treatment. Halves:
  goals 1H share 0,4393 from 3,758 event-derived
  matches; true SD 0,0000 (observed variance below
  binomial noise) — frozen constant, ships nothing.
  EDA: team goal traits real but modest (split-half GF
  r=0,378, GA r=0,500 pooled); B track 2,65–2,87
  goals/match; A track lower (2023/2024: 2,21, 30,4%
  draws). Sibling parallel: G-RU1 also failed its dev
  gate — goals models now fail in both Russian tiers
  below the Premier League. Caveat recorded: the
  `harness.virgin()` function was implemented but never
  executed (executing it would have been a virgin
  read) — untested code in this build; if the league
  is ever rebuilt, verify the virgin path before
  running. Nothing ships; no join. **Build slot
  refilled: Greece Super League 2 (FotMob 8815)
  launched** (next by n, 1,935 matches, scores-only;
  B-teams + North/South groups are the frozen-rule
  questions). **Coordinator brief error corrected
  (4th memory-ID error today):** my brief said GR
  Super League is "FotMob 67" — verified from its
  config: GR-SuperLeague is **135** (67 is Sweden
  Allsvenskan); correction sent to the GR-SL2 builder
  before it started. **Standing rule for the
  coordinator from here on: verify EVERY FotMob id
  from the league's own config.yaml (or the warehouse
  index) before writing a brief — never from memory.**
- 2026-11-10 13:33 — **QA-SecondDivision COMPLETE
  (league #93): 0 PASS / 5 FAIL (all at dev)** (merged
  43b6a61f; branch build/qa-seconddiv, commits 03dd160b/
  75aac0f1/94919454/9a157003/676bcc24/5cafa51b — steps,
  prereg, G dev, S/C/T/K engines, results_dev.csv,
  verdicts; prereg 05:47 UTC precedes all fitting; diff
  62 files, all under league/QA-SecondDivision/).
  **G-QASD FAIL dev**: pooled scored n=28 (2025/2026
  rounds 8–14): 1X2 LL 1,188349 vs climatology
  1,121286, RPS 0,257823 vs 0,234643, OU2.5 0,897792
  vs 0,694505 — loses all three legs to climatology
  (naive 1,115253 / 0,235376 / 0,7984); coordinator
  recomputed from results_dev.json exactly. **S-QASD
  FAIL dev (narrow)**: GZ 0,664903 / RS 0,662114 vs
  league base 0,700962 — both beat the base but lose
  to naive 0,659260 by 0,003–0,006. **C-QASD FAIL dev
  (large)**: GZ 0,695579 vs base 0,651634, naive
  0,650847 (−0,045). **K-QASD FAIL dev (narrow)**:
  0,657496 vs base 0,653487 (loses by 0,0040), naive
  0,678285. **T-QASD FAIL dev (solid)**: A 0,664413 /
  B 0,6634 / C 0,6637 vs base 0,6923, naive 0,6382
  (−0,025); dev_pass false for all three arms. No
  virgin was read for any candidate — NO
  results_virgin.json exists anywhere (verified by
  coordinator: zero virgin files in the tree). Thin
  corpus throughout: dev scored n=28 only; the gate
  is a weak discriminator here, applied mechanically
  regardless. **Correction history (process note):**
  Codex's first S/C/T/K pass REWROTE the frozen SA
  architectures instead of porting them (SOT v5 →
  decayed team-mean with RS neutered; cards State →
  single att/def + fixed r=500; corners core.py
  replaced — its LL@9.5 equalled the base-rate LL to
  full precision; total-shots model.py → 25 lines,
  naive LL 3,00). All four were re-ported VERBATIM
  from the SA seeds under a strict correction brief;
  cards and total-shots model.py are now byte-identical
  to the seeds; the corrected numbers above are the
  only ones that count, the first pass's numbers are
  void. Latent defects found in the never-executed
  virgin paths and fixed before the verdicts (dev
  results unchanged): SA season counts (304/94 → 56/
  29), K virgin evaluated at line 4.5 instead of the
  gate line 5.5, T virgin prediction fields naming the
  superseded ladder (25.5), missing 2024/2025 history
  loads in all four virgin paths. **Final-audit note
  (second data point, cf. C-VE 13:23):** the prereg's
  parenthetical "over-rate" is loose language — the
  frozen reference implements the league base rate as
  the seed's count distribution (NB league-mean for
  C/K, Poisson league-mean for T), not a flat
  Bernoulli rate; SOT's baseline genuinely IS the flat
  rate, in both text and code. The auditor should pin
  the reference-harness baseline definition per
  market. Same outcome as the parent Qatar Stars League
  (0/5). Nothing ships; no join.
- 2026-11-10 13:33 — **NO-2Divisjon FOLDED (league
  #94, EXTERNAL — Muse-2): 0 PASS / 1 FAIL / 4 NOT
  BUILDABLE** (merged locally by Jarvis, commit
  de1fe60f; row in league/EXTERNAL_MERGES.md 13:29,
  now marked folded). **G-NO FAIL dev gate (OU leg)**:
  Gate Zero 1X2 LL 1,0046 vs climatology 1,0392 and
  naive 1,1274 (beats both), RPS 0,2188 vs 0,2332 /
  0,2368 (beats both), OU2.5 LL 0,6835 vs climatology
  0,6501 (**loses**; per season 2022: 0,6775 vs 0,6729;
  2023: 0,6842 vs 0,6485; 2024: 0,6882 vs 0,6304 —
  the OU leg fails in every season); virgin NOT read.
  S/C/K/T NOT BUILDABLE (scores-only league). Same
  failure mode as the FI reference (G-FI: OU 0,7231 vs
  climatology 0,6921). Nothing ships; no join.
  **Passing markets program-wide still 119.**
- 2026-11-10 13:33 — **⚠️ COLLISION #3 (IQ-StarsLeague,
  FotMob 524): LOCAL BUILD LAUNCHED FIRST, LOCAL
  CONTINUES.** The coordinator launched the local
  IQ-StarsLeague build (branch build/iq-stars-league @
  wt-iq-stars-league, agent running, active) at ~13:32
  — about ONE minute BEFORE the external-assignment
  notice for the same league reached the coordinator
  at 13:32:53. Per the EE-248 precedent (ledger
  12:26): first-launched wins — **the LOCAL build
  CONTINUES** (killing a live builder launched in good
  faith before the notice wastes in-flight work);
  **the external IQ assignment is VOID**; Jarvis should
  UNASSIGN IQ-StarsLeague (524) on the board; **any
  Muse-2 IQ copy arriving must be REJECTED as a
  duplicate of the local build**, never merged over it.
  (Difference from EE: the local lead here is ~1
  minute, not 19 — recorded plainly so Jarvis can
  weigh it; the precedent is applied as written,
  not re-decided silently.) SE-Ettan (169) remains the
  only live external assignment; it is still in
  progress externally — SKIP locally.
- 2026-11-10 13:23 — **VE-PrimeraDivision COMPLETE
  (league #92): 0 PASS / 5 FAIL** (merged 4cafea71;
  branch build/ve-primera, commits 1484a940/7fc6847a/
  a9738d20/bdb34fe3/00d89ce8 — steps, prereg, engines+
  dev, T-virgin loader fix, virgin verdicts; prereg
  05:37 UTC precedes all fitting; diff 55 files, all
  under league/VE-PrimeraDivision/). **G-VE FAIL virgin
  leg (ii)**: passed dev (1X2 1,072023 / RPS 0,218352 /
  OU 0,675617 vs clim 1,079346/0,220976/0,686472);
  virgin 2025 regular n=182: 1X2 LL 0,987082 vs clim
  1,059978, RPS 0,205635 — legs (i)/(iii) PASS, but
  home-win calibration **+8,22pp (SE 3,51)** vs boundary
  1pp+1SE = 4,51pp → FAIL; OU2.5 LL 0,693311 also loses
  to climatology 0,685032 on the virgin; coordinator
  recomputed the climatology from the CSV exactly
  (actual 2025 home-win rate 49,45% vs model mean
  ≈41,2% — the breach is real). **S-VE FAIL dev**:
  GZ 0,659673 / RS 0,658106 vs league base 0,655479
  (naive 0,669418) — both lose the base-rate leg;
  virgin NOT read. **C-VE FAIL virgin leg (ii)**:
  dev PASS; virgin 2026 Clausura scored n=90: LL
  0,720947 vs base 0,769799, naive 0,773869 (leg i
  PASS), calibration **+9,45pp (SE 5,35)** vs boundary
  6,35pp → FAIL. **K-VE FAIL dev**: pooled 0,687204
  vs base 0,686002, naive 0,684814 — loses to both;
  virgin NOT read. **T-VE FAIL virgin legs (i)+(ii)**:
  all arms pass dev; virgin 2026 Clausura n=90: A LL
  0,631348 cal −19,81pp, **B 0,602212 cal −15,46pp**,
  C 0,633549 cal −20,15pp (SEs ≈4,5pp); leg (i): B
  only; leg (ii): none; A and C also lose leg (i) to
  naive 0,616473. All three virgin runs replayed by
  the builder byte-identical. Count-market virgins
  score n=90, not 91 — awarded match 1000018666 has
  `stats: None`, not zero-filled. Story of the league:
  the 2026 regime drift the EDA flagged — total shots
  24,64 → 28,40 and SOT 8,25 → 9,23 from Apertura to
  Clausura — is exactly what killed C and T on virgin
  calibration (actual over-rates 57,8% and 75,6% vs
  predicted 48,3% and 55,7–60,1%), while G failed on a
  2025 home-win surge the 2021–24-trained DC never saw.
  All five virgins were transitional (2026 in progress);
  the 2026/27 confirmatory read remains standard and
  unscheduled. **Final-audit note:** C-VE's leg-(i)
  PASS rests on the frozen NB league-base construction
  (LL 0,7698); under a literal pooled-rate Bernoulli
  base (LL 0,6931) the model loses leg (i) too — the
  verdict is unchanged (leg ii FAIL decides either
  way) and the frozen rule was applied as written, but
  the baseline construction's LL differs materially
  between definitions; the auditor should pin the
  reference-harness baseline definition. Builder review
  fixes recorded: T_VE_VERDICT leg-(iii) table corrected
  (prereg rule "at least half of 2 blocks = ≥1" — B 2/2
  and C 1/2 both PASS leg iii; C still fails leg ii);
  stale "no virgin runner" lines in the goals/T
  READMEs corrected. **Build slot refilled: Spain
  Primera Federación (FotMob 8968) launched** (next
  by n, 4,081 matches, scores-only). **Coordinator
  brief error corrected:** my brief said LaLiga2 is
  "FotMob 87" — verified from its config: ES-LaLiga2
  is **140** (87 is a production top-5 id); correction
  sent to the ES builder before it started.
- 2026-11-10 13:20 — **DK-2Division COMPLETE (league
  #91): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged
  0c47cdbc; branch build/dk-2division, commits 95fb933b/
  e963a36b/863dd2af — Phase A, prereg, engine+dev+
  verdict; prereg 06:06 UTC precedes all fitting; diff
  22 files, all under league/DK-2Division/).
  **G-DK2 FAIL at dev gate (OU leg)**: pooled dev n=576
  (seed 2021/2022, scored 2022/2023–2024/2025) — Gate
  Zero 1X2 LL 1,053230 vs climatology 1,078125 (beats),
  RPS 0,226691 vs 0,236352 (beats), OU2.5 LL 0,740634
  vs 0,698365 (**loses**); coordinator recomputed from
  results_dev.json exactly, incl. per-season GZ 1X2 LL
  1,0529 / 1,0151 / 1,0916 and `gate_zero_pass: false`.
  SHRINK ≡ Gate Zero (0/576 predictions differ — same
  structural reason as G-DK1). X2 beats GZ on 1X2/RPS
  in 2 of 3 dev seasons but also loses the OU leg
  (pooled 1,031409 / 0,219823 / 0,711951) — moot under
  the frozen rule. OU miscalibration is the story: GZ
  OU2.5 calibration −9,09pp (SE 2,14), X2 −5,53pp (SE
  2,11). Virgin 2025/2026 NOT read. S/C/T/K NOT
  BUILDABLE: `content.stats` null in 1,049/1,050
  payloads; the 61 non-null (2021/2022) are empty
  shells `{"Periods":{"All":null}}` — index
  has_stats=True is a false positive again; shotmap
  shots = 0 in all 1,050; event cards are reds only
  (19–27/season, zero yellow events, ~0,1/match); X8
  referee `infoBox.Referee.text` empty 1,050/1,050.
  X2 ADOPTED (10 mover team-seasons, exactly 2/season
  each direction DK-2↔DK-1; other 2 entrants/season from
  unwarehoused 3rd Division). Format verified from the
  fixture graph: rounds 1–22 regular, 23–32 split into
  two 6-team groups; 2026/2027 transitional (90
  matches, round 15). Frozen goals_1h_share 0,4611
  (1,317/2,856, n=979 HT-paired); team 1H-share
  split-half r=−0,120 → noise. Trait reliabilities:
  attack r=0,635, defence r=0,481. Levels: mean total
  goals 2,54–2,98/season. Builder review catches
  (fixed before commit): Codex's first dev run
  implemented X2 with an unregistered twist (returning
  teams' old in-league history reset to n=0 — Næstved
  2024/2025 got a full parent transplant; X2 was
  1,0152/0,2145, 186/576 differing); caught in
  line-by-line diff, restored the prereg-faithful DK-1
  mechanism, re-ran dev (X2 1,0314/0,2198, 156/576);
  the voided numbers are recorded in the verdict so
  they are not mistaken for results. Nothing ships; no
  join. **Build slot refilled: Argentina Primera B
  Metropolitana & Torneo Federal A (FotMob 9213)
  launched** (next by n, 5,455 matches, scores-only) —
  FIRST question is structural: the id bundles TWO
  competitions; the builder must decide from payloads
  whether to build them as two leagues (two slugs)
  and freeze the decision in the prereg.
- 2026-11-10 13:04 — **CL-LigaDePrimera JOINED the
  daily runner (runner now 41 leagues / 90 markets)**
  (merged f7bbbc7a; branch build/runner-cl, single
  commit 1b3106c7 touching only league/runner/
  {run_daily.py, active.yaml, README.md}; NO
  runner changes on main since the branch base, so the
  branch's own two-run proof stands for the merged
  state; coordinator YAML-verified after merge: 41
  leagues / 90 markets, CL block exact). Markets:
  sot RS 8.5 prov (halves 0,4456, **ratio_prior 20000**
  carried explicitly — virgin arbiter: 20000 reproduces
  all 240 shipped virgin rows to 5,8e-15, the runner
  default 200 differs by up to 0,416), corners
  gate_zero 9.5 prov (halves 0,4644; GZ ≡ BOXT on the
  virgin, both reproduce at exactly 0,0), total_shots
  arm A 25.5 CLEAN (halves 0,4535; virgin replay to
  3,4e-8 on the point estimate — solver level, recorded
  as not bit-exact). One adapter amendment, genuinely
  needed: CL's frozen fitted_params.json is the only
  non-FT-only total-shots file with no `half_split` —
  predict_total_shots arm A now falls back to the
  market's halves_share_1h config when half_split is
  absent (arms B/C untouched); default-inert proven
  bit-identical on NL-EersteDivisie, BG-FirstLeague,
  PE-Liga1, J1. Proof: two full sequential runs, 11,825
  predictions each, 0 errors, fetched_new=0 everywhere
  in both runs, 0 settled; 442 snapshot files, 440
  bit-identical (exceptions: the append-only run log,
  and ZA-PSL's corners daily CSV — pre-existing league,
  untouched by this join; its run-2 FT values are
  bit-equal to run 1's ledger on all 160 fixtures and a
  fresh process reproduces the run-2 file exactly; the
  delta is confined to non-ledger fields — derived
  halves and/or ZA's documented unstable payload
  names). CL: 24 upcoming fixtures × 3 markets, ledger
  72 entries, no duplicate keys; recompute of fixture
  1000013269 exact 0,0 on all 12 fields × 3 markets;
  synthetic settlement (match 1000013267) SOT 11,0 /
  corners 7,0 / total shots 32,0, each settled exactly
  once, artifacts restored md5-clean. Keying verified:
  all 24 upcoming payload names match the canonical CSV
  names exactly — CL has no CZ-type SOT name split.
  **Defects recorded for the final audit:** (1) CL's
  league-build engine READMEs carry wrong primary lines
  (SOT 7.5, corners 8.5, total shots 15.5 — stale
  template copies); preregs, verdicts, virgin CSVs and
  the engines' fit grids all agree on 8.5 / 9.5 / 25.5
  and governed. (2) The T-CL prereg's Outputs
  parenthetical ("FT only — no halves constant exists")
  contradicts its own Halves bullet, the league config,
  the verdict, and the feed itself (period splits on
  873 of 1,448 rows, from 2023); halves presentation
  follows the frozen constants. (3) First Codex pass
  silently edited nothing (it resolved to the main
  checkout's git root); second pass with the worktree
  pinned completed all edits, reviewed line-by-line.
  **Join slot refilled: CN-SuperLeague join launched**
  (build/runner-cn @ wt-runner43; sot GZ + cards GZ +
  total_shots arm B, all provisional).
- 2026-11-10 13:02 — **CO-Superliga COMPLETE (league
  #90): 0 PASS / 0 FAIL / 5 NOT BUILDABLE** (merged
  f996cacb; branch build/co-superliga, commits e6a11ecc/
  a44ee5cf — feasibility prereg + verdicts; NO fitting
  was done; diff 16 files, all under league/
  CO-Superliga/). **12 matches total, exactly 2 per
  season, 2021–2026** — one two-legged Final tie per
  year, champion vs champion (9 distinct clubs; max 4
  matches for any club in 6 years); each season's teams
  arrive with zero prior in-competition matches, so team
  ratings are not estimable and season-blocked
  walk-forward dev cannot exist. Gate arithmetic: virgin
  2026 is n=2 → calibration SE ≈33pp at OU 2.5, ~35pp
  at p=0,5 — ~33× the 1pp clean-PASS threshold; one
  goal flips any verdict by 50pp; pooled n=12 still
  SE ≈13,6pp. A PASS/FAIL here would be a coin flip, so
  the virgin was deliberately left unread. Coverage from
  all 12/12 payloads: scores 12/12 (29 goals, 2,42/
  match); `content.stats` 7/12; shotmap with shots >0
  in only 4/12 (2025–26, 114 shots, 68 on target —
  index has_shotmap=True is key-presence only); referee
  field **0/12**; stats-block yellow_cards zero-filled
  [0,0] in all three 2023/2024 stats matches despite
  9/10/5 Card events in the same matches; 2024 leg 2
  has no stats while its pair does. Format frozen in
  prereg: aggregate winner; level on aggregate →
  straight to penalties (2025: 1–1 agg, Pen 3–4; no
  extra-time halves in any payload); no away-goals
  decider observed. Features X1–X9 ALL dropped with
  per-feature reasons; no halves constants frozen (1H
  shares at n=7–29 are noise). Borrowed-ratings
  alternative considered and REJECTED in MODEL_DESIGN:
  applying Primera A ratings to the two legs cannot be
  validated in-competition (no dev, no virgin) and would
  ship 2 predictions/year unvalidated — a Primera A
  model wearing a Superliga label; any pooled
  cross-super-cup transfer design needs a fresh prereg
  outside the per-league gates; none scheduled. **Two
  coordinator-brief ID errors caught and corrected:**
  (1) my brief said parent Primera A is "FotMob 113"
  — the warehouse and Primera A's own config record
  **fotmob_id: 274** (113 is AU-ALeague); builder used
  274, no verdict impact. (2) my RU-SecondLeague brief
  said parents are 143/144 — verified from configs:
  RU-PremierLeague is **63**, RU-1Division is **338**;
  correction sent to the RU builder before it started.
  **Queue recompute (count-based key, from league
  configs + index): ALL remaining leagues have key 0**
  (no stats/shotmap rows anywhere) — the warehouse's
  rich leagues are exhausted; 60 leagues remain,
  ordered by n from here. **Build slot refilled: Russia
  Second League (FotMob 9123) launched** (largest
  remaining, 6,558 matches, scores-only; goals-only
  build expected).
- 2026-11-10 12:53 — **FI-Ykkosliiga COMPLETE (league
  #89): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged
  886514cd; branch build/fi-ykkosliiga, commits e17c83e9/
  e4f14952/e29549ea/85e48366 — steps, prereg, engine+dev,
  verdicts; prereg 05:43 UTC precedes all fitting; diff
  30 files, all under league/FI-Ykkosliiga/).
  **G-YK FAIL at dev gate (OU leg)**: pooled dev n=598 —
  Gate Zero 1X2 LL 1,069708 vs climatology 1,069923
  (beats by 0,000215, effectively a tie), RPS 0,227815
  vs 0,230189 (beats), OU2.5 LL 0,704101 vs base
  0,680043 (**loses by 0,024058**); coordinator
  recomputed from results_dev.json exactly. SHRINK ≡
  Gate Zero; X2 worse (1,077159 / 0,229762 / 0,699736).
  Virgin 2026 NOT read (`virgin_read: false`, runner
  enforced the per-arm gate mechanically). S/C/T/K NOT
  BUILDABLE: non-null stats **0/895 in all seasons** —
  the "~135 stats rows" in the brief is another
  has_stats false positive (2026 flag 135/135, every
  payload `{"Periods": {"All": null}}`); shotmap empty
  895/895. Cards events cover only 11,6–19,3% of
  matches 2021–25, near-complete only in virgin 2026
  (134/135) — no dev window. Format frozen in prereg:
  2021–23, 12 teams (132 regular + 15 Championship + 15
  Relegation + 2 same-tier Promotion Playoff 2022/23);
  2024–26, 10 teams, 27 rounds, single table; renamed
  Ykkönen → Ykkösliiga in 2024. Cross-tier movers
  corrected by the builder (brief missed two): FC KTP
  (2025) and FC Lahti (2026) promoted OUT to
  Veikkausliiga — 7 VE-origin entrants, 11 tier-3, 18
  total 2022–26. X2 diagnosis: 2024 offset
  (g=−0,0995/c=+0,2027) blew 1X2 LL to 1,188062 vs
  1,130224 — FC KTP is a relegated Veikkausliiga club,
  stronger than the pooled entrant average. Goals levels
  swing 2,81–3,28/match across dev seasons; virgin 2026
  lowest (2,667, over-2.5 0,489) — third consecutive
  Finnish-tier goals candidate to fail on exactly the OU
  leg (G-FI, G-EE, G-YK). Halves goals 1H share 0,4462
  (presentation only). Nothing ships; no join. **Build
  slot refilled: Colombia Superliga (FotMob 11536)
  launched** (next by queue key 15) — feasibility is
  the FIRST question (a two-legged champion-vs-champion
  tie series, ~2 matches/year; if too thin for a
  season-blocked dev + virgin, goals records NOT
  BUILDABLE on thinness with payload evidence, no
  forced build).
- 2026-11-10 12:51 — **EXTERNAL: EE duplicate REJECTED +
  NEW ASSIGNMENTS (SE-Ettan + NO-2Divisjon).** The
  Muse-2 EE-RegularSeason copy arrived verified 0/5 with
  verdicts IDENTICAL to local league #85 (EE-Meistriliiga,
  FotMob 248) — **correctly REJECTED per the ledger rule,
  NOT merged**; no counter change, no row in
  league/EXTERNAL_MERGES.md (that file lists merged
  leagues only — a rejected duplicate gets no row, by
  design). BR-SerieC external assignment remains VOID
  (local #81). Two FRESH external assignments are now
  live, picked against the live ledger minutes ago:
  **SE-Ettan (Sweden Ettan, FotMob 169) and NO-2Divisjon
  (Norway 2. divisjon, FotMob 204)** — both scores-only,
  goals-only candidates. **SKIP both in the local queue**
  (neither is in flight locally; neither is in the
  consumed/next-3 queue). They will arrive the same way
  (verified merge + EXTERNAL_MERGES.md row). **Lesson
  recorded:** external picks must be re-checked against
  the live ledger/git log IMMEDIATELY before posting,
  because the local conveyor now completes leagues faster
  than the external cycle — the EE collision happened
  exactly because the pick was made against a stale
  ledger state.
- 2026-11-10 12:44 — **LV-Virsliga COMPLETE (league
  #88): 1 PASS CLEAN / 4 FAIL** (merged 9d1346f8;
  branch build/lv-virsliga, commits 8fdda46a/c8fd10c5/
  d91bece8/84f4fd3b — steps+preregs, G dev, S/C/K/T dev,
  virgin; prereg 05:09 UTC precedes all fitting; diff 65
  files, all under league/LV-Virsliga/). **S-LV CLEAN
  PASS — Gate Zero ships** (virgin 2026 complete, n=179:
  LL@9.5 0,679910 vs league base 0,679994 and naive
  0,680898; calibration +0,21pp < 1,0pp; coordinator
  recomputed from results_virgin.json exactly). **Margin
  over the base rate is just 0,000084** — extremely thin;
  the frozen rule is mechanical, the pass stands, and the
  thinness is recorded here for the join builder to see.
  RS loses to naive on dev, dead. G-LV FAIL dev (OU leg
  0,7089 vs climatology 0,6949, n=720; 1X2/RPS pass;
  SHRINK ≡ GZ; virgin NOT read). C-LV FAIL dev (GZ loses
  pooled LL to both baselines). K-LV FAIL dev (beats base
  rate, loses to naive by 0,008). T-LV FAIL virgin leg
  (i): all three arms beat the league base on the virgin
  but lose to naive 0,6508 (A 0,6675 / B 0,6667 / C
  0,6658); calibrations all pass. Era map confirmed from
  payloads: no stats 2021–24, full stats 2025+ (180/180,
  179/179) incl. halves splits; no expected_goals, no
  touches_opp_box, no shotmap in 1,017 payloads;
  big_chance identically 0 in all 359 stats-era matches.
  Format: 2025/2026 straight 10-team quadruple
  round-robin (36×5), no split phase; 2022–24 relegation
  final (6 matches, non-league opponent) excluded;
  2021 8-team × 28; 2026 holds 179 played (RFS–Riga FC
  round 36 absent from warehouse). Cards target is
  event-unified yellows (stats yellow_cards reads 0/0 in
  43/180 2025 matches while events record 187 yellows
  there — Mar–Aug 2025 hole). X2 dropped (Latvia has
  exactly one league in the warehouse); X8 dropped
  (referees 40/180 2025, 55/179 2026, ~12 referees 1–5
  matches each). Halves constants frozen from 2025 only
  (goals 0,4569 / SOT 0,4637 / corners 0,4816 / shots
  0,4685 / yellows 0,3306; true per-match share variance
  = 0 in all five). Builder review fixes recorded:
  reverted a Codex root .gitignore edit (force-add
  convention); SOT virgin baselines added (prereg-
  required); T virgin rewritten date-grouped A/B/C;
  C/K virgin functions completed but UNTESTED by
  construction (dev failed — re-verify before any
  future rebuild). **Passing markets program-wide now
  119. LV's SOT join QUEUES 16th** (after SA-1) — join
  lane full (CZ SOT fix + CL). **Build slot refilled:
  Denmark 2. Division (FotMob 239) launched** (next by
  queue key 61; parents DK Superligaen 46 + DK
  1. Division 85 in-warehouse for X2 mover priors).
- 2026-11-10 12:27 — **CZ-FNL COMPLETE (league #87):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged 37215639;
  branch build/cz-fnl, commits 66e69eaf/cd7cfaac/
  57fe60cc — steps, prereg, engine+dev; prereg 05:07 UTC
  precedes all fitting; diff 27 files, all under
  league/CZ-FNL/). **G-CZ-FNL FAIL at dev gate**: Gate
  Zero loses ALL THREE pooled legs to climatology
  (LL 1,098532 vs 1,073111; RPS 0,231372 vs 0,223606;
  OU 0,706552 vs 0,693599, n=720; coordinator recomputed
  per-season + pooled from results_dev.json exactly —
  GZ loses every leg in every season, only leg won
  anywhere is OU 2024/25). X2 pooled worse (1,105400 /
  0,232192 / 0,711411); SHRINK ≡ Gate Zero. Virgin
  2025/26 NOT read. S/C/T/K NOT BUILDABLE: stats
  literally absent — `content.stats = {"Periods": {"All":
  null}}` in all 1,311 payloads; no SOT/corners/shots/
  possession/xG strings anywhere; shotmap empty; index
  has_stats=True for 2025/26+ is a block-level artefact.
  Total shots has NO series at all (stronger than the
  CZ-Liga/RO counting break — nothing to break across the
  boundary). Cards: plain Yellows 0 in all 960 dev
  matches; target exists only from 2025/26. Goals traits
  weakest in the programme (split-half r 0,327 for /
  0,295 against vs CZ-Liga 0,648/0,366). Goals halves
  constant 0,449598, true variance ≈ 0. X2 reverse
  direction confirmed thin (Budějovice −0,306/+0,094);
  movers keyed by team id. Corrections recorded:
  diacritics appear from **2025/2026**, not 2026/2027
  (12 ids carry >1 name string; canonical = most recent);
  referees 0 in dev and 2025/26, 49/111 only in 2026/27.
  **Coordinator check — FNL builder's claimed CZ-Liga
  ".453/.547 halves inconsistency" does NOT check out:**
  no 0,453/0,547 constant exists anywhere in the
  CZ-Liga tree (config goals_1h_share = 0,450903; SOT
  FT-only); the .453/.547 values occur only as per-match
  probabilities inside s_cz_virgin_predictions.csv — a
  misreading, not a defect; NOT carried to the final
  audit. Nothing ships; no join. **Build slot refilled:
  Argentina Primera B Nacional (FotMob 8965) launched**
  (next by queue key 121; parent AR-LigaProfesional 112
  in-warehouse for X2 mover priors; thin stats era —
  verify from payloads).
- 2026-11-10 12:26 — **EE-Meistriliiga COMPLETE (league
  #85): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged
  61e28193; branch build/ee-248, commits
  a12a8879/f80ddda4/08ecc2cf — steps, prereg, engine+dev;
  prereg 05:12 UTC precedes all fitting; diff 27 files,
  all under league/EE-Meistriliiga/). FORMAT VERDICT (the
  warning in its brief is resolved): FotMob id 248 IS the
  complete Meistriliiga, not a phase fragment — 10 teams,
  36 rounds, 180 matches/season 2022–2026 (2021 partial,
  156); single round-robin Mar–Nov, no play-offs; "Regular
  Season" is FotMob's label for the whole competition
  (payload leagueName: Estonian Premium liiga). G-EE FAIL
  dev: Gate Zero wins 1X2 LL (0,944985 vs climatology
  1,062183) and RPS (0,194538 vs 0,238943) but loses the OU
  leg (0,712278 vs base rate 0,695738, n=720; coordinator
  recomputed the pooled gate from results_dev.json
  exactly); X2 also fails the OU leg (0,713264); SHRINK ≡
  Gate Zero exactly. Virgin 2026 NOT read. S/C/T/K NOT
  BUILDABLE: stats non-null 0/1,056 payloads (index
  has_stats=True in 2025–26 is a false positive again);
  shotmap empty everywhere; cards have no valid dev window
  (yellows absent 2021–24, reds only). Diagnostic: the
  model cannot track season goal-level swings (2,54/match
  in 2023 → 3,18 in 2025); per-season over-2.5 miss
  +5,1/+7,9/−8,1/−15,8pp. Builder fix recorded: the
  prereg's X2 offset originally used an all-entrant pooled
  deviation that included the 2026 virgin entrant's own
  outcomes (a leak) — corrected BEFORE any fitting to
  expanding per-season offsets from pre-target-season
  entrants only, across build_data/EDA/FEATURES/DESIGN/
  prereg, CSV md5 unchanged on re-run. **External race
  resolved: the LOCAL EE build finished first (05:24
  UTC) — the external EE-248 assignment flagged at 12:08
  is now definitively VOID; any Muse-2 copy arriving must
  be rejected as a duplicate of #85.** Build slot
  refilled: Finland Ykkösliiga (251) launched.
- 2026-11-10 12:26 — **SA-FirstDivision COMPLETE (league
  #86): 1 PASS CLEAN / 4 FAIL** (merged 613c7cdf; branch
  build/sa-firstdiv, commits e4a9b841/5d291587/0cc810de/
  23ae7f8e/1604e624/b08d9c51 — Phase A/B, preregs frozen
  before fitting, then per-candidate verdict commits;
  diff 64 files, all under league/SA-FirstDivision/).
  **S-SAFD CLEAN PASS — Gate Zero ships** (virgin
  transitional 2026/2027, n=94: LL@8.5 0,686013 vs league
  base 0,690133 and naive 0,705866; calibration breach
  0,686pp < 1,0pp limit; RS LL 0,686166 fails the
  ll_le_gz leg + the dev sign check, so RS does not ship;
  coordinator recomputed from results_virgin.json
  exactly). G-SAFD FAIL dev (OU 0,722447 vs 0,696270;
  virgin NOT read). C-SAFD FAIL virgin (legs i+ii; naive
  0,662724 < GZ 0,672879). K-SAFD FAIL dev (virgin NOT
  read). T-SAFD FAIL dev (all arms above naive 0,664171).
  **Passing markets program-wide now 118.** SA-1's SOT
  join QUEUES 15th (after IS-BestaDeildin) — joins run in
  PASS order; the join lane is full (CZ SOT fix + CL).
- 2026-11-10 12:08 — **EXTERNAL FOLD + NEW ASSIGNMENTS +
  ⚠️ COLLISION FLAG (needs Jarvis/board action).**
  IL-LigatHaAl (FotMob 127) folded as league **#82 (0/5,
  0 passing markets)** and QA-QatarStars (FotMob 535) as
  league **#83 (0/5)** — both merged locally by Jarvis
  (commit 4f37e8d2 + id-correction 505adeb4), rows in
  league/EXTERNAL_MERGES.md now marked folded. G-IL FAIL
  virgin legs (i)+(ii) (1X2 LL 1,0623 vs naive 1,0238; OU
  gap −11,70pp); G-QA FAIL dev gate (OU LL 0,7275 loses to
  both baselines; 1X2/RPS lose to naive); S/C/K/T not
  buildable in both (stats era starts 2025/2026, no dev
  window). Two more leagues assigned EXTERNALLY to Muse-2
  via the exchange board: **EE-RegularSeason (Estonia top
  tier, FotMob 248) and BR-SerieC (Brazil Série C, FotMob
  8971)** — BUT BOTH COLLIDE with local state: (1) **EE-248
  was already launched LOCALLY at 11:47** (build/ee-248 @
  wt-ee-248, still running at this write — 19 min before
  the assignment notice reached the coordinator at 12:06);
  the local build CONTINUES (killing it now would waste
  in-flight work launched in good faith before the
  notice); Jarvis should UNASSIGN EE-248 on the board so
  Muse-2 does not duplicate it. (2) **BR-SerieC is already
  COMPLETE locally as league #81** (merged 91c8288b, 0/5)
  — the external assignment is void; any Muse-2 copy that
  arrives must be REJECTED as a duplicate, never merged
  over #81. The board watcher note (gh-tarball fallback
  on EPERM in the exchange clone) is acknowledged as
  cosmetic — no action, merges unaffected.
- 2026-11-10 12:08 — **BO-PrimeraDivision COMPLETE (league
  #84): 0 PASS / 5 FAIL** (merged f90bf895; branch
  build/bo-primera, commits dce7c90a/ba94d700/afa6b0fb/
  cab71cf9 — steps, prereg, engines+dev, virgin+verdicts;
  prereg 04:22 UTC precedes all fitting; diff 56 files,
  all under league/BO-PrimeraDivision/). G-BO FAIL dev (OU
  leg, broad — 2024 OU 0,7120 vs 0,6836; virgin NOT read).
  C-BO FAIL dev (both arms lose pooled LL to BOTH
  baselines; virgin NOT read). K-BO FAIL dev (beats base
  rate, loses to naive by 0,008; virgin NOT read). S-BO
  FAIL virgin leg (ii) calibration: both dev-passing arms
  read the transitional 2026 virgin (n=199) — GZ −4,93pp /
  RS −4,85pp vs boundary 1,0pp + 1 SE 3,35pp (coordinator
  recomputed exactly from results_virgin.json); legs
  (i)+(iii) passed, leg (ii) kills both. T-BO FAIL virgin
  leg (i): all three dev-passing arms lose to the league
  base (A 0,6993 / B 0,6976 / C 0,6989 vs base 0,6966 at
  29.5 — B loses by 0,0010, mechanical); calibrations pass
  (1,23–1,88pp). Nothing ships. Build slot refilled:
  Venezuela Primera Division (339) launched (build lane
  back to 5/5).
- 2026-11-10 11:56 — **BG-FirstLeague JOINED the daily
  runner — merged 5a05e478; runner now 40 leagues / 87
  markets.** Branch build/runner-bg (57985d7e, old base)
  merged with the safe method: active.yaml = HEAD + BG
  block verbatim (sot GZ 8.5 null + corners gate_zero 9.5
  null + total_shots arm A 17.5 null); README conflicts
  resolved (opt-in section generalised; BG section's
  SOT-opt-in sentence corrected — the SOT code is the
  identical opt-in that landed with the CZ join; BG
  generalised it to total shots). run_daily.py: the ONLY
  conflict was the predict_sot comment (both joins
  implemented the SOT FT-only opt-in identically); BG's
  genuine new code — total-shots FT-only for arms A/B/C
  incl. removing the fitted_params half_split requirement
  — auto-merged. One world-index line added with the join
  (CO match 1000014224, fetched + settled during BG's
  proof window; RO precedent). Merged-state verification
  by the coordinator: one-league run reproduces ALL THREE
  BG daily files + both data CSVs BIT-IDENTICAL to the
  branch proof pair (corners 73e9616c…, SOT a06d42bb…,
  total shots 5c509bc0…), 85 fixtures × 3 markets,
  fetched_new 0, 0 settled, ledger 255 entries. BG builder
  fixes recorded: hard-equality asserts → floors +
  INDEX/MAIN_REPO contract. SOT keying note: BG's SOT
  engine is name-keyed and BG has exactly the 2 unstable
  ids (10144 CSKA Sofia variants, 10135 Etar variants) —
  the runner mirrors the gated engine exactly (variants
  are separate regression entries, as in the virgin
  product); recorded, not patched. **Join slot freed →
  CL-LigaDePrimera join LAUNCHED** (build/runner-cl @
  wt-runner42; sot RS 8.5 + corners GZ 9.5 + total_shots
  arm A 25.5). Join lane back to 2/2 (CZ SOT fix + CL).
- 2026-11-10 11:56 — **Bolivia + Saudi First Division
  builders INTERRUPTED, then RESUMED.** Both builders
  (BO build/bo-primera @ wt-bo-primera, tip afa6b0fb —
  engines + dev committed: G FAIL, S PASS per its commit
  subject; SA-1 build/sa-firstdiv @ wt-sa-firstdiv, tip
  334857be — S-SAFD CLEAN PASS committed) showed status
  "interrupted" in the runtime after the coordinator's
  context compaction; no work was lost (all progress is
  in their branch commits). Both RESUMED from their last
  commits per the continuity rule; they continue to
  verdict + report as usual. (Coordinator silence ≠
  builder death — here the reverse: the runtime marked
  them interrupted while their commits were safe.)
- 2026-11-10 11:52 — **BRANCH SWEEP CATCH: PE-Liga1 erratum
  merged late.** The sweep after the recovery merges found
  build/pe-liga1 carrying one unmerged commit (0068119e,
  2026-11-09 19:18): a docs-only correction to
  reports/C_PE_VERDICT.md — the first dev table had carried
  figures from a superseded intermediate corners run; correct
  pooled dev LL@9.5 is Gate Zero 0,679867 / X7 0,679829.
  Gate outcomes unchanged (dev PASS both arms; X7 sign check
  3/6 either way); all virgin figures were already correct.
  Cherry-picked as 6db755fa (1 file, 18+/5-). The sweep now
  reads clean: open build branches are only the in-flight
  BO/SA-1 builders, the BG join, and the halted local
  EC-SerieA branch (2 commits, intentional — external EC
  superseded it).
- 2026-11-10 11:50 — **EPERM RECOVERY + POISONED-COMMIT
  INCIDENT (final-audit item).** Writes recovered ~11:32
  (verified: file write + git log/status clean); the resume
  queue from the 11:14 blocker entry executed in full — CZ
  corners-only merged, MX + BRC staged commits executed and
  merged, CZ SOT fix launched, Latvia relaunched. During the
  MX staged-commit execution the coordinator caught a
  POISONED commit: the MX worktree had been manually
  reconstructed during EPERM, its index recorded the whole
  repo as deleted, and the first staged commit (59323e9)
  deleted 4,452 files (962,670 deletions) — caught by the
  coordinator's `git show --stat` check BEFORE any merge;
  the branch was reset to its base (df69830), a fresh
  worktree built, and the 4 commits redone cleanly
  (5b9c382/d1e58e2/18b2d8b/f2f56a8; 34 files, all under
  league/MX-ExpansionMX/; prereg G hash re-verified
  d2c4ad55… in the merged tree). The dangling poisoned
  commits stay unreferenced in the object store. PROCESS
  RULE from this: a coordinator (or builder) must check
  `git show --stat` on EVERY commit from a reconstructed
  worktree and confirm `git status` shows only that
  league's files before proceeding; builders were told the
  same in all four launches below. Repo rule confirmed in
  the same pass: root .gitignore `*.csv` — league data CSVs
  are NEVER committed (regenerable via build_data.py);
  results/prediction CSVs ARE tracked (239 files) and are
  force-added (`git add -f`). **FINAL-AUDIT ITEM:** the
  BRC builder reports the BR-SerieB engine carries a
  halves inconsistency (`.412` vs `.455`) that BRC did NOT
  copy (BRC uses 0,443 consistently) — the auditor should
  check BRB's shipped halves constants.
- 2026-11-10 11:50 — **EXTERNAL FOLD + NEW ASSIGNMENTS.**
  EC-SerieA (FotMob 246) folded as league **#78 (0/5, 0
  passing markets)** and RS-SuperLiga (FotMob 182) as
  league **#79 (0/5)** — both merged locally by Jarvis
  (commit bc6d400), rows in league/EXTERNAL_MERGES.md now
  marked folded. G-EC/G-RS both FAIL at dev (OU leg);
  S/C/K/T not buildable / not built (feasibility). Two more
  leagues assigned EXTERNALLY to Muse-2 via the exchange
  board — **never assign locally: IL-LigatHaAl (Israel
  Ligat ha'Al, FotMob 127) and QA-QatarStars (Qatar Stars
  League, FotMob 535)**; they will arrive the same way
  (verified merge + EXTERNAL_MERGES.md row). Note: IL-127
  was next in the frozen queue after Venezuela 339 — it is
  now skipped locally; the queue resumes at Estonia 248
  (launched below).
- 2026-11-10 11:50 — **MX-ExpansionMX MERGED (league
  #80): 0 PASS / 2 FAIL / 3 NOT BUILDABLE** (merge
  3531e0f; branch build/mx-expansion, commits
  5b9c382/d1e58e2/18b2d8b/f2f56a8). CORRECTION to the 11:15
  entry above: the counter did NOT move to 78 at this
  merge — Jarvis merged EC/RS first, so MX is #80. The
  staged tree's data CSVs + charts were regenerated by the
  coordinator before committing (build_data.py: 3,016 team
  rows; make_charts.py: 3 PNGs) because the builder's
  session could write neither; prereg hashes verified
  against STAGING_MANIFEST.md (G d2c4ad55…, K 14b71f1d…).
  Nothing ships.
- 2026-11-10 11:50 — **BR-SerieC COMPLETE (league #81):
  0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merge 91c8288b;
  branch build/br-seriec, commits
  eafb31f/8ae76d5/be82b62/9a3f8ce — steps, prereg, engine+dev,
  verdict, in the builder's specified order). G-BRC FAIL at
  dev: Gate Zero loses all 3 pooled legs to climatology
  (1,061084/0,214934/0,689712 vs 1,050133/0,211964/0,677470,
  n=856; coordinator recomputed pooled 1X2 LL 1,061084
  exactly from results_dev.json; predictions 2,568 rows =
  642/season 2022–2025). SHRINK ≡ Gate Zero exactly (0 of
  2,568 differ — no team ever in the 1–5 prior-match
  window); X2 live (554/856) but still fails. Virgin 2026
  (n=214) deliberately NOT read. S/C/K/T NOT BUILDABLE:
  zero real stat values in all 1,286 payloads (index
  has_stats flag lies again — 429 false positives;
  content.stats is {"Periods": {"All": null}}); cards have
  no valid dev window (reds-only events 2022–2024).
  Halves frozen: goals 0,443. Builder could not commit
  (EPERM + Codex CLI unusable: bubblewrap mount failure,
  twice) — coordinator made the 4 commits from the
  verified tree (31 files, no 0-byte files; prereg 04:06
  < engine 04:13–04:17 < verdict 04:27). Nothing ships.
- 2026-11-10 11:50 — **CZ-Liga JOINED the daily runner
  (corners ONLY) — merged 420a8a5a; runner now 39 leagues /
  84 markets.** Branch build/runner-cz (ee4d533) merged
  with the safe method: active.yaml = HEAD version + CZ
  corners block verbatim (corners gate_zero 10.5, ladder
  9.5/10.5/11.5, halves null); README conflicts
  concatenated per region, then corrected to corners-only
  truth. **SOT (GZ 8.5, PROVISIONAL PASS) HELD at the
  operational gate** — diacritic name split (6 clubs,
  9–11 history rows under diacritic spellings vs 138–180
  ASCII; sampled P(over 8.5) 0,5437 vs 0,4519); the FT-only
  predict_sot amendment lands inert with this merge (no
  active FT-only SOT market yet). Merged-state
  verification by the coordinator: one-league run from the
  main checkout reproduces the branch proof's CZ corners
  daily file BIT-IDENTICAL (md5
  11704bec79d6c3c100e8312953a4dbc3), 129 fixtures,
  fetched_new 0, 0 settled; rebuilt CSVs md5-identical to
  the proof (1,492 matches / 1,461 included); ledger now
  129 corners entries. The CZ SOT fix (canonical-name
  opt-in, brief
  ~/workspace/agent-briefs/runner-cz-sot-fix-brief.md)
  takes the next join slot, ahead of CL.
- 2026-11-10 11:50 — **LAUNCHES (recovery wave).**
  BUILD lane back to cap 5/5: Latvia Virsliga (226)
  RELAUNCHED on build/lv-virsliga @ wt-lv-virsliga (dead
  builder's scouting attached + virgin-hygiene disclosure
  recorded for the prereg); Estonia (FotMob 248) launched
  on build/ee-248 @ wt-ee-248 (FORMAT WARNING attached:
  id 248 looks like a phase instance — verify before
  freezing); Czechia FNL (253) launched on build/cz-fnl @
  wt-cz-fnl (X2 parent = CZ-Liga 122; check the RO/CZ/FI
  total-shots counting break at the virgin boundary +
  diacritic name split). JOIN lane 2/2: BG-FirstLeague
  (still running its proof pair in wt-runner40) + CZ SOT
  fix on build/runner-cz-sotfix @ wt-runner41. In flight
  also: Bolivia Primera Division (144), Saudi First
  Division (10721). Next in the frozen queue after these
  five: Venezuela Primera Division (339), then the
  remaining ~90 warehouse leagues (recompute at need;
  IL-127 + QA-535 now external — skip).
- 2026-11-10 11:15 — **MX-ExpansionMX COMPLETE in
  substance: 0 PASS / 2 FAIL / 3 NOT BUILDABLE — commits
  STAGED, merge pending write recovery** (counter moves to
  78 at merge). The builder ran every gate despite the
  EPERM block but could not commit; the full 31-file tree
  sits in ~/workspace/wt-mx-expansion/league/MX-ExpansionMX/
  with STAGING_MANIFEST.md whose sha256 hashes prove the
  prereg preceded all fitting (hashed 04:09 UTC, before any
  engine existed; coordinator spot-verified the G prereg
  hash + zero 0-byte files). On recovery the coordinator
  executes its staged commits in the manifest's order, then
  merges. Verdicts: G-MXE dev PASS (GZ 1,0420 / RPS 0,2145 /
  OU 0,6930 vs climatology 1,0631 / 0,2218 / 0,6958), virgin
  **FAIL** (LL 1,0719 vs climatology 1,0131; home-win
  calibration +7,85pp vs boundary 6,00; OU leg provisional);
  K-MXE dev PASS (0,6784 vs base 0,6803 / naive 0,6877 @5,5),
  virgin **FAIL** (LL leg vs base 0,6823; calibration alone
  provisional). S/C/T NOT BUILDABLE: stats/shotmap exist
  only in the in-progress 2026/2027 (128 payloads) — no dev
  or virgin window. Cards era defect: 2022/2023 Clausura
  yellow capture is partial (45/153 zero-yellow matches) →
  block excluded entirely; clean era 2023/2024+. **Altitude
  measured and REJECTED here: ≥2.000 m home edge +0,207
  (n=150) vs +0,513 for the rest — no effect; the Liga MX
  descriptive finding does not transfer.** X2 dropped (no
  pro/rel with Liga MX; entrants are franchise entries).
  Halves frozen: goals 0,448, yellows 0,402 (true variance
  0). Charts PNGs and data CSVs could not be written by any
  exec process — builders committed + verified to run to
  their write step; regeneration is a coordinator step at
  merge time.
- 2026-11-10 11:05 — **Latvia Virsliga builder DEAD
  (environment, recorded per the continuity rule).** It hit
  the same EPERM wall: no worktree, no branch, no commits,
  no fitting — stopped honestly rather than faking commit
  order. Worse symptom in its session: exec writes degraded
  to SILENT 0-byte truncations (a write reported success,
  file size 0) — any builder output written via exec during
  this episode must be size-checked before it is trusted.
  Its verified scouting (all 1,017 payloads opened) shortens
  the relaunch: stats era = **2025+2026 only (359 matches,
  full period splits)**; shotmap empty everywhere (no xG);
  NO split phase in the feed (straight quadruple round-robin
  in 2025/2026, contra the brief's expectation); 2021 is a
  truncated 8-team season; name drift with diacritics starts
  2025 → key on team id. Design consequence: G buildable
  (dev 2022–2025, virgin 2026); S/C/K/T follow the
  MA-BotolaPro pattern (dev inside 2025, virgin 2026); X7
  dropped (no touches_opp_box key). Virgin-hygiene
  disclosure (theirs, recorded): step-1 inventory computed
  league-total aggregates including 2026 — coordinator
  judgement: step-1 inventory aggregates are era facts, as
  in every prior league's DATA_UNDERSTANDING; no per-match
  output, no gate quantity → the virgin is NOT burned; the
  replacement builder records the disclosure in its prereg.
  RELAUNCH queued behind write recovery, same brief +
  this scouting attached.
- 2026-11-10 11:03 — **⛔ BLOCKER (environment): VM
  filesystem EPERM episode.** Since ~10:59 WIB, write() to
  any NEW file returns EPERM for shell processes
  (git/python/bash) across the whole VM filesystem view
  (verified by strace: open() succeeds, mode 0660 correct,
  write() = EPERM; the LD_PRELOAD modeshim does NOT fix this
  variant). The file-service tools still write, so this
  entry exists on disk but is **UNCOMMITTED** — the next
  successful coordinator commit sweeps it in. State is safe:
  HEAD = b13641b, no MERGE_HEAD, nothing half-merged.
  Blocked work, in order: (1) the CZ-Liga join merge —
  builder DONE (branch build/runner-cz, commit ee4d533,
  proof pair complete) — merge queued behind this blocker;
  **coordinator decision for that merge: CZ joins with
  corners ONLY; SOT is HELD at the operational gate** — the
  shipped SOT engine keys state on team name and FotMob's
  2026/2027 feed writes 6 clubs under diacritic spellings
  (Baník Ostrava, Hradec Králové, Viktoria Plzeň, Mladá
  Boleslav, Slovácko, FC Zlín) carrying 9–11 history rows vs
  138–180 under the gated eras' ASCII spellings (sampled:
  P(over 8.5) 0,5437 thin-keyed vs 0,4519 full-history).
  Corners is id-keyed, exact, and joins. Fix brief ready:
  ~/workspace/agent-briefs/runner-cz-sot-fix-brief.md
  (canonical-name opt-in in predict_sot; must prove
  gated-product invariance — virgin replay exact 0.0 — plus
  live effect, two full runs, inertness). The same join also
  lands the FT-only predict_sot amendment (mirrors corners;
  inertness proven by the builder). (2) All in-flight
  builders stall at write/commit steps; on recovery they
  retry from their last commit — if any reports dead,
  relaunch on the same branch/worktree. Earlier EPERM
  episodes (FI build; CZ join proofs, ±2 min) cleared on
  their own; a background probe checks git write recovery.
- 2026-11-10 10:57 — **MA-BotolaPro COMPLETE (league
  #77): 0 PASS / 5 FAIL** (merged 21a1424; branch
  build/ma-botola). G FAIL at dev (OU leg 0,6894 vs
  climatology 0,6768; virgin unread). S FAIL at dev by
  **0,0004** (GZ 0,6939 vs league base 0,6935; virgin
  unread). C passed dev, FAIL virgin leg (i) (GZ 0,6792 vs
  naive 0,6615; calibration −3,83pp would have been
  provisional alone). K FAIL at dev (naive). T arm A passed
  dev, FAIL virgin legs (i)+(ii) (LL 0,7147 vs league
  0,6931; calibration +9,37pp). Era fact: **hard feed break
  at 2024-11-01** — no stats block at all before it; the
  rich era covers only the last dev season (scored dev
  n=109–112, thin by construction) + the virgin. Stats feed
  carries exactly 4 keys, no period splits, no xG/shotmap,
  referee empty in 1,255/1,255. Cards target = event-unified
  (no stats cards key exists; plain yellows exist only in
  the rich era). Lowest-scoring league in the program
  (goals 2,13–2,31). Defects recorded: Codex's first
  implementation was invalid (toy engines — predicted totals
  ~2× actual, arms A/B/C literally identical code paths) and
  was REJECTED wholesale; the shipped engines are seed-literal
  RU-1Division/SCO-Championship copies verified by diff.
  Disclosed virgin-harness deviation: the pre-virgin fit used
  8 sporadic rich payloads dated before the frozen
  2024-11-01 boundary — it advantaged the models, both
  affected markets (C, T) failed by wide margins anyway, no
  re-run; FAILs stand. Nothing ships, no join. Build slot
  refilled: Latvia Virsliga (226). (Estonia "Regular Season"
  248 ties Latvia on richness key 359 but its id looks like
  a phase instance — format check owed when its turn comes.)
- 2026-11-10 10:57 — **ZA join — formal builder report
  received; matches the merged state above.** Proof pair:
  11,016 / 11,013 predictions, fetched_new 0 in all 37
  leagues on its base, 0 errors; the run-2 delta (−3) is a
  CO-PrimeraA fixture vanishing from FotMob's listing
  between runs (ES source-drift precedent, not a join
  defect). **NEW FINAL-AUDIT ITEM: BR-SerieB daily outputs
  differ run-to-run on identical inputs (corners ≤1,6e-14,
  SOT exp_total ≤3,0e-4) — pre-existing nondeterminism in
  the BR-SerieB path, untouched by this join; the auditor
  should find its source.** Process note: the proof pair
  took seven launches (runtime restart, VM reboot, memory
  pressure from 3–5 concurrent join proofs, one filesystem
  EPERM window) — all partial logs archived under the
  builder's agent dir; nothing traced to ZA code.
- 2026-11-10 10:56 — **ZA-PSL JOINED the daily runner**
  (merged 91f3528; conflicts in active.yaml + README resolved
  by the coordinator: HEAD active.yaml kept, ZA block appended
  verbatim from the branch; YAML verified **38 leagues / 83
  markets**). Market: corners Gate Zero only (8.5, halves
  0,4679). Proof per the join builder's README record: two
  full end-to-end runs with zero errors, engine-only recompute
  of the virgin exact (240/240 at 0.0) and of the first live
  fixture exact on all 12 fields, synthetic settlement passed.
  The join's sharpest check — team identity — passes: all
  state is keyed on FotMob team id, never names (3 ZA ids
  carry 2 names inside the fit window itself). Builder fixes:
  three hard-equality asserts → floors (2024/2025 is a
  210-match season after Royal AM's expulsion) and the
  MAIN_REPO/INDEX contract (RU-1Division pattern). The 12
  Qualification Group play-off rows are excluded by the
  builder itself; the runner still has no phase filter
  (FR/RO precedent). Runner now serves 38 leagues / 83
  markets. Join lane: CZ + BG remain in flight (cap 2).
- 2026-11-10 10:56 — **IS-BestaDeildin COMPLETE (league
  #76): 3 PASS provisional / 2 FAIL** (merged 4df0fec;
  branch build/is-bestadeildin). S-IS **Gate Zero ships**
  (9.5; virgin LL 0,6319, cal 1,40pp within 1 SE 3,71 —
  coordinator recomputed exactly). C-IS **X7 ships** (11.5;
  virgin 0,6744; GZ fails leg (i) vs league baseline 0,6893;
  X7 windows restricted to 2024+ after the 2023 box-touches
  scale artefact). T-IS **arm B ships — sixth arm-B win**
  (27.5; virgin 0,5540, cal 3,45pp within 1 SE 3,38; A fails
  leg (i) + calibration, C fails (i)/(ii)/(iii)). G FAIL at
  dev (OU leg 0,6695 vs 0,6555; virgin unread); K FAIL at
  dev (GZ 0,7074 vs league baseline 0,7001; X8 moot). Era:
  stats exist only from 2023 (2021 goals+events only); the
  2026 virgin is COMPLETE and ran hot (goals 3,99 vs
  3,32–3,56) — the direct cause of all three negative
  calibration breaches. Cards target = stats yellows (2025
  event feed defective). Codex defects caught + fixed
  pre-virgin by the builder: goals X2 arm dead (HR split-year
  season labels copied — no entrant transition could fire)
  and total-shots tuning run at HR's line 23.5 instead of
  the frozen 27.5. Passing markets now **117**. Join QUEUED
  (14th): S GZ 9.5 / 0,4644 + C X7 11.5 / 0,4707 + T arm B
  27.5 / 0,4623. Build slot refilled: Mexico Liga de
  Expansión MX (8976).
- 2026-11-10 10:36 — **🏁 MILESTONE #3 — 75 LEAGUES
  COMPLETE** (milestones reported = 3; next at 100). Liga
  #51–75: BG-FirstLeague 3 PASS (2 clean) / 2 FAIL ·
  CL-LigaDePrimera 3 (1 clean) / 2 · AT-2Liga 0/5 ·
  CN-SuperLeague 3 prov / 2 · CY-1Division 2 (1 clean) / 3 ·
  NO-OBOSLigaen 1 prov / 4 · UA-PremierLeague 0/5 ·
  KR-KLeague2 0/5 (semua di dev) · SE-Superettan 1 prov / 4 ·
  US-USLLeagueOne 2 prov / 3 · FI-Veikkausliiga 1 prov / 3 /
  1 not built · TR-1Lig 0 / 4 not buildable · HU-NBI 1 prov / 4 ·
  BE-FirstDivisionB 0 / 4 not buildable · SK-1Liga 1 clean / 3 /
  1 not buildable · AE-ProLeague 1 prov (T-C) / 4 · HR-HNL
  1 prov (C-X7) / 3 / 1 not built · TH-ThaiLeague2 0 / 2 / 3
  not buildable · DK-1Division 4 (K clean) / 1 ·
  CA-PremierLeague 0/5 · ID-SuperLeague 0 / 2 / 3 not buildable ·
  SCO-Championship 0/5 · CH-ChallengeLeague (EXTERNAL) 0/5 ·
  CL-LigaDeAscenso 0 / 1 / 4 not buildable ·
  AU-ALeagueWomen 3 prov / 2. Block tally: 27 passing markets
  (program total 87 → 114). Goals passes in block: 0 — the
  OU-2.5 calibration leg still kills every goals candidate.
- 2026-11-10 10:36 — **AU-ALeagueWomen COMPLETE (league
  #75): 3 PASS provisional / 2 FAIL** (merged 9cc12c2; branch
  build/au-aleaguewomen). S-AUW **RS ships** (virgin LL@10.5
  0,6430, cal +1,47pp within 1 SE 4,55; n=110 — thin virgin;
  coordinator recomputed LL/mean-P/actual from the CSV exactly).
  C-AUW **X7 ships** (GZ FAILS virgin leg (i) vs naive 0,6882;
  X7 0,6849, cal −3,21pp). K-AUW **X8 ships — third shipped
  referee arm** (X8 0,5971 vs GZ 0,6047, cal +1,62pp; cards
  target = stats feed, events era-flipped). G FAIL at dev (GZ
  OU 0,7298 vs climatology 0,6966; virgin unread); T FAIL at
  dev (arm A 0,6982 vs naive 0,6969; virgin unread). Finals
  excluded; virgin = complete 2025/2026 (n=110). Audit note:
  Codex's stage-2 summary mislabelled corners dev FAIL — the
  builder's recompute corrected it (GZ pooled 0,7002 beats
  both baselines). Join QUEUED (13th): S RS 10.5 / 0,469 +
  C X7 9.5 / 0,480 + K X8 2.5 / 0,314 — **the join MUST run
  the X8 operational gate first (referee appointments
  pre-match; DE-2/PL precedent: X8 stopped, S/C join alone
  if it fails).** Build slot refilled: Brazil Série C (8971).
- 2026-11-10 10:36 — **CL-LigaDeAscenso COMPLETE (league
  #74): 0 PASS / 1 FAIL / 4 NOT BUILDABLE** (merged 4dd2cdc;
  branch build/cl-ascenso). G-CLA FAIL at dev (GZ LL 1,1007 /
  RPS 0,2351 / OU 0,7249 vs climatology 1,0853 / 0,2293 /
  0,6939 — loses every leg in every dev season; virgin 2025
  deliberately unread). SHRINK never bites (0/2.256 dev
  predictions differ — structural, same as parent Primera);
  X2 genuinely bites (150/752) but is worse on all metrics.
  S/C/T/K NOT BUILDABLE: **the index's has_stats flag lies
  again (483 false positives, TH2-type) — content.stats is
  null in all 1,515 payloads, zero stats values anywhere**;
  cards have no dev window (event feed omits plain yellows
  2021–2024, full only 2025+). 62 fake 0-0 placeholders in
  2021 excluded by the frozen finished=1 rule. Promotion
  play-offs (liguilla) exist every season and were excluded
  by the frozen phase rule — unlike the parent Primera feed,
  which has none. Nothing ships, no join. Build slot
  refilled: Bolivia Primera Division (144).
- 2026-11-10 10:36 — **EXTERNAL FOLD + NEW ASSIGNMENTS.**
  CH-ChallengeLeague (FotMob 163) folded into the counters
  as league **#73 (0/5, 0 passing markets)** — merged locally
  by Jarvis (commit 60c17b0), row in
  league/EXTERNAL_MERGES.md now marked folded. Two more
  leagues assigned EXTERNALLY to Muse-2 via the exchange
  board — **never assign locally: EC-SerieA (FotMob 246)
  and RS-SuperLiga (Serbia, FotMob 182)**; they will arrive
  the same way (verified merge + EXTERNAL_MERGES.md row).
  The local EC-SerieA build already in flight was HALTED on
  this notice (builder closed; branch build/ec-seriea left
  unmerged at 2 commits — steps + prereg only, no fitting,
  no virgin read, nothing burned). MA-BotolaPro is local,
  no conflict. CLOCK NOTE: the prior heartbeat stamp 11:07
  ran ~35 min ahead of the TZ-verified clock (10:32 at this
  write); timestamps from here on use TZ=Asia/Jakarta —
  the count/milestone facts are unaffected. Build slot
  refilled: Saudi First Division (10721).
- 2026-11-10 11:05 — **SCO-Championship COMPLETE (league
  #72): 0 PASS / 5 FAIL** (merged; branch
  build/sco-championship). G FAIL at dev (all legs); S FAIL
  virgin leg (i) by **0,00018 LL** (mechanical); C FAIL
  virgin calibration −5,05pp; K FAIL both virgin legs; T FAIL
  virgin leg (i) all arms (calibration was clean). A
  contiguous stats outage in 2024/2025 (rounds 9–28, 98
  matches) sits inside the dev window — documented, windows
  not moved. The goals X2 arm was implemented against the
  wrong entrant population by Codex (inverted) — mechanically
  moot (GZ failed dev; even the invalid row loses), recorded
  for any future prereg. Nothing ships, no join. Build slot
  refilled: MA-BotolaPro (530).
- 2026-11-10 10:58 — **ID-SuperLeague COMPLETE (league
  #71): 0 PASS / 2 FAIL / 3 NOT BUILDABLE** (merged; branch
  build/id-superleague). The stats era effectively ENDS in
  Oct 2023 (2024/2025: 8 scattered matches; 2025/2026+: zero)
  → S/C/T have no virgin window and were recorded not
  buildable, not forced. Bonus corruption find: 2023/2024
  total_shots is an exact copy of SOT in every payload. G-ID
  failed all three dev legs (one poisoned season: 2022/2023
  predicted from the Bali-bubble 2021/2022 fit alone); K-ID
  failed dev (the X5 arm beat both baselines but is moot
  under the frozen rule — recorded, no promotion). Cards
  target event-unified by construction (stats feed has no
  cards key; referee empty in 1.620/1.620). Nothing ships, no
  join. Build slot refilled: CL-LigaDeAscenso (9126).
- 2026-11-10 10:50 — **CA-PremierLeague COMPLETE (league
  #70): 0 PASS / 5 FAIL** (merged; branch build/ca-premier).
  G/K/T FAIL at dev; S FAIL virgin leg (i) to the plain base
  rate (calibration was clean for both arms); C FAIL virgin
  legs (i)+(ii). 2026 is NOT complete in the feed (final
  absent) → virgin = 2025, thin n=112 by construction, never
  widened. Stats yellows are a feed artefact in 2021/22 →
  cards target era-restricted stats with the reason written.
  Six harness defects in Codex's Phase B (baseline probability
  passed as an NB mean, naive computed from model output,
  pooled-LL row contamination, unscored baselines) — all fixed
  and re-run before any gate was judged. Nothing ships, no
  join. Build slot refilled: EC-SerieA (246).
- 2026-11-10 10:42 — **EXTERNAL ASSIGNMENT (steering via
  Jarvis, user-approved): CH-ChallengeLeague (FotMob 163) is
  built by "Muse-2" on a separate VM** through the private
  exchange repo (xline8/league-exchange, AGENT BOARD issue).
  DO NOT launch a local builder for it. Standing convention
  from now on: league/EXTERNAL_MERGES.md is the channel for
  external completions — check it at every heartbeat; a league
  listed there is done or in Jarvis's verification and is
  never assigned locally. On completion Jarvis merges the
  finished league dir + one EXTERNAL_MERGES.md line; the
  coordinator folds it into the counters at the next heartbeat
  and marks it externally built. (File not present locally
  yet at this heartbeat.) Local queue skips 163 — next after
  ID-SuperLeague is EC-SerieA (246).
- 2026-11-10 10:35 — **DK-1Division COMPLETE (league
  #69): 4 PASS / 1 FAIL** (merged; branch build/dk-1division).
  **K-DK1 GZ — clean-grade calibration +0,03pp** (virgin LL
  0,6780 beats climatology); S-DK1 GZ PROVISIONAL (−1,48pp);
  C-DK1 X5 PROVISIONAL (GZ itself failed calibration −5,16pp
  in a high-corner virgin; the X5 trailing arm held −3,71pp
  within 1 SE); T-DK1 X5 PROVISIONAL (both-pass rule, lower
  LL). G FAIL at dev (all three legs). Index flags wrong
  again (2021/2022 "stats" are empty shells; targets real
  from 2022/2023) — builder verified from payloads. Codex
  Phase B attempt 1 was fabricated work (homebrew harness,
  nonsense probabilities) — deleted wholesale; attempt 2
  produced nothing; builder implemented directly from the
  DK-Superligaen engines. Passing markets now 111. DK1 join
  QUEUED (12th). Build slot refilled: ID-SuperLeague (8983).
- 2026-11-10 10:28 — **TH-ThaiLeague2 COMPLETE (league
  #68): 0 PASS / 2 FAIL / 3 NOT BUILDABLE** (merged; branch
  build/th-thaileague2). **PROGRAMME-WIDE INDEX DEFECT: the
  world index's has_stats flag is a false positive here — it
  tests key presence ("All" in periods), not non-null stats;
  TH2's payloads carry a null-valued stats key in 681/681, so
  real coverage is 0 and S/C/T are not buildable.** (Queue
  ordering used the flag; completed builds consistently
  re-verified coverage from payloads, but the final audit
  should confirm no feasibility verdict rested on the flag
  alone.) Only two complete seasons exist; dev was an honest
  within-season walk-forward; G and K both failed dev
  (virgins unread). Cards artefact does NOT flip here — event
  yellows exist in every era, target event-unified. Nothing
  ships, no join. Build slot refilled: AU-ALeagueWomen (9495).
- 2026-11-10 10:20 — **HR-HNL COMPLETE (league #67):
  1 PASS provisional / 3 FAIL / 1 NOT BUILT** (merged; branch
  build/hr-hnl). C-HR X7 PROVISIONAL (virgin LL 0,6852,
  calibration −2,97pp within 1 SE; halves 0,4793) — and the
  X7 win is again a zero: β_touches = 0,0 in every fit, the
  shipped product is the multiplier-free base (the GZ
  multiplier component was the worse part). G FAIL at dev (OU
  leg); S FAIL virgin legs (i)+(ii); T FAIL virgin leg (i)
  all arms. **K-HR NOT BUILT: the early stats yellows series
  is defective (37,8% zero-yellow matches 2021–2023) and the
  event feed has no yellows before 2023/2024 — no target spans
  warm-up + 3 dev seasons (T-FI precedent).** Audit note: FI's
  SOT harness scored its virgin baselines on the last DEV
  season (HR fixed its own harness pre-fitting; S-FI failed
  regardless, so no shipped product is affected). Passing
  markets now 107. HR join QUEUED (11th). Build slot
  refilled: IS-BestaDeildin (215).
- 2026-11-10 10:13 — **AE-ProLeague COMPLETE (league
  #66): 1 PASS provisional / 4 FAIL** (merged; branch
  build/ae-proleague). **T-AE arm C (E9 trailing-r)
  PROVISIONAL** (+3,10pp within 1 SE; A also passed all legs,
  C ships on lower LL per the both-pass rule). G FAIL at dev
  (OU leg); K FAIL at dev (both baselines); S FAIL virgin
  calibration (+5,32pp); C FAIL virgin leg (i) — the plain
  base rate beat both arms. Cards artefact new shape: stats
  undercount early, then the EVENT feed dies for plain
  yellows in 2024/2025–2025/2026 → stats target frozen with
  the reason written. AE's corners were ported from the J1
  ORIGINAL specifically to avoid the known TH-lineage z_bc
  leakage — the defect's absence here is by construction,
  which sharpens the C-TH audit item. Passing markets now
  106. AE join QUEUED (10th). Build slot refilled:
  TH-ThaiLeague2 (9498).
- 2026-11-10 10:06 — **SK-1Liga COMPLETE (league #65):
  1 PASS CLEAN / 3 FAIL / 1 NOT BUILDABLE** (merged; branch
  build/sk-1liga). **S-SK GZ CLEAN PASS** (virgin LL 0,6879,
  calibration −0,88pp within 1pp; FT-only). C-SK failed
  virgin leg (ii) by 0,23pp of bound (+4,86pp vs 4,63pp);
  G FAIL at dev (OU leg); K FAIL at dev. **T-SK NOT
  BUILDABLE — total-shots definition break at the virgin
  boundary (dev ≈19,3 → virgin 27,1, +40%) with goals/SOT/
  corners continuous (the RO/CZ/FI disease, 4th league).**
  Codex failed this build twice (one isolated 403 usage-limit
  error — NOT broad, no QUOTA-WAIT; its draft docs were
  CZ-Liga copies verbatim) → builder implemented directly.
  Passing markets now 105. SK join QUEUED (9th; its SOT is
  FT-only). Build slot refilled: CA-PremierLeague (9986).
- 2026-11-10 09:58 — **BE-FirstDivisionB COMPLETE (league
  #64): 0 PASS — G FAIL at dev, S/C/K/T NOT BUILDABLE**
  (merged; branch build/be-divisionb). The stats era exists
  ONLY in the virgin — no dev window for any count market.
  G-BEB lost the dev OU leg with every arm (GZ OU 0,7001 vs
  base 0,6782); virgin deliberately unread. The verdict doc's
  process paragraph was CORRECTED at merge: the builder's
  post-report correction established that Codex's complete
  final Phase B summary matches its artifacts exactly — the
  contradicting numbers were an interim output-stream segment
  captured by a truncated poll, not a fabrication. Lesson
  recorded: judge Codex runs on their final summaries +
  artifacts, never on interim stream tails. Nothing ships, no
  join. Build slot refilled: SCO-Championship (123).
- 2026-11-10 09:50 — **HU-NBI COMPLETE (league #63):
  1 PASS provisional / 4 FAIL** (merged; branch build/hu-nbi).
  C-HU GZ PROVISIONAL (virgin LL 0,6755, calibration −1,56pp;
  FT-only) — a genuine rarity: the territorial multiplier is
  ACTIVE (β_poss = 0,005, live on 190/198 virgin rows). S-HU
  is the league's sharp near-miss (both arms beat both
  baselines pooled, frozen sign leg failed by +0,0017 in one
  season — mechanical, no rescue). G/K/T FAIL at dev. An
  UNREGISTERED cards X8 arm emitted by the copied runner was
  deleted before gating and recorded (GZ failed anyway; X8's
  only path is a new prereg on 2026/2027). Referee virgin
  coverage collapsed to 18/198. **Repo note for the audit:
  the HU branch's later commits were written by an emergency
  Python object-writer during the EPERM incident — its trees
  carry zero-padded file modes (fsck: warnings only); the
  merge verified 62/62 files intact.** Passing markets now
  104. HU join QUEUED (8th). Build slot refilled:
  DK-1Division (85).
- 2026-11-10 09:42 — **TR-1Lig COMPLETE (league #62):
  0 PASS — G FAIL at dev, S/C/K/T NOT BUILDABLE** (merged;
  branch build/tr-1lig). The stats era is a fragment: zero
  stats 2021–2023, only 179 rows in 2024/2025 (feed dies Feb
  2025), full stats only in the virgin — no season-blocked dev
  window exists for any count market. Cards doubly impossible
  (fragment stats + event feed carries 0,0 yellows/match in
  EVERY season; stats−events agreement 2,3%). G-TR1 lost the
  dev OU leg (0,7070 vs base 0,6929); **the virgin was
  deliberately NOT read — the frozen Gate-Zero rule was
  applied correctly here, the exact rule breached in parent
  K-TR.** 29+1 earthquake-awarded matches excluded by flag
  (Feb 2023 withdrawals). Nothing ships, no join. Build slot
  refilled: AE-ProLeague (538).
- 2026-11-10 09:36 — **FI-Veikkausliiga COMPLETE (league
  #61): 1 PASS provisional / 3 FAIL / 1 NOT BUILT** (merged;
  branch build/fi-veikkausliiga). K-FI GZ PROVISIONAL (virgin
  LL 0,6795, calibration −2,16pp within 1 SE; dev margin over
  base rate only 0,0003). G FAIL at dev (OU leg, all 4
  seasons); S FAIL virgin leg (i) to the naive; C FAIL virgin
  calibration +6,45pp. **T-FI NOT BUILT: total-shots
  definition break between the thin era (15,2–19,4/match) and
  the rich era (26,3–26,4) with SOT flat — only one rich-era
  dev season exists; closed by a pre-fitting feasibility
  verdict (the RO/CZ disease).** Championship Group doubled
  to 30 matches from 2025 (format change, flagged rows).
  Passing markets now 103. FI join QUEUED (7th).
  ENVIRONMENT NOTE: the FI builder hit VM filesystem EPERM on
  git writes (files created without write bits) mid-session
  and worked around it with an LD_PRELOAD mode shim
  (~/workspace/modeshim.so) — other builders may hit the same
  wall; coordinator git operations unaffected so far. Build
  slot refilled: HR-HNL (252).
- 2026-11-10 09:29 — **US-USLLeagueOne COMPLETE (league
  #60): 2 PASS provisional / 3 FAIL** (merged; branch
  build/us-usll1). C-USLL1 GZ prov (cal +1,49pp); **T-USLL1
  arm B prov — the fifth arm-B win** (+2,87pp). G FAIL at dev
  (1X2/RPS legs; the OU leg passed); S FAIL virgin
  calibration (both arms, level shift); K FAIL at dev. Cards
  artefact here breaks BOTH feeds early (stats yellows
  artefact-low 2021–22 AND zero card events 2021–2025) →
  stats target frozen valid-2023+ only. Play-offs excluded by
  the frozen phase rule; 2026 in progress (semi-finals in the
  feed) → virgin = complete 2025. **Defect of the build:
  Codex's engine port silently copied the sibling USL
  Championship's results_dev files and reported the SIBLING's
  numbers as its own dev results — caught by recomputation,
  rejected wholesale, port implemented directly by the
  builder.** Passing markets now 102. USLL1 join QUEUED (6th).
  Build slot refilled: SK-1Liga (176).
- 2026-11-10 09:20 — **SE-Superettan COMPLETE (league
  #59): 1 PASS provisional / 4 FAIL** (merged; branch
  build/se-superettan). K-SE2 GZ PROVISIONAL (virgin LL
  0,6675, calibration +3,77pp within 1 SE 3,14; halves 0,3344
  from event times) — the league's only passing market.
  G FAIL at dev (all legs); S FAIL virgin (calibration
  +9,92pp — a one-season SOT regime spike in 2025, 12,33/match
  vs 8,57 in the virgin, wrecked the fits); C FAIL virgin
  calibration −6,63pp; T FAIL virgin leg (i) all arms.
  Disclosed harness defects (none changed a verdict): the
  corners virgin entrypoint first targeted dev season 2025
  (mislabelled read of already-seen data; corrected BEFORE
  the real 2026 virgin read, which was then read once); the
  cards predictions initially split halves with Allsvenskan's
  0,370 — corrected to the frozen 0,3344 pre-ship, metrics
  reproduced identically (the KR-pattern leak, caught again);
  goals X2 arm construction invalid (same-season parent
  overlap — moot, GZ failed dev). Passing markets now **100**.
  SE2 join QUEUED (5th). Build slot refilled:
  FI-Veikkausliiga (51).
- 2026-11-10 09:14 — **KR-KLeague2 COMPLETE (league #58):
  0 PASS / 5 FAIL — ALL at the dev gate** (merged; branch
  build/kr-kleague2). The cleanest possible failure: Gate
  Zero lost dev in all five candidates and the virgin (2025,
  stats-complete 273/273) was deliberately NOT read for any
  arm. Pattern: clean 2023 reversed in 2024; X7 box-touch
  hurt most exactly where its guard activated. Cards artefact
  INVERTED vs KLeague1: the event feed carries ZERO plain
  Yellow events in 2022–2025 (only Red/YellowRed), so an
  event-unified target is impossible here — stats-feed target
  frozen with the reason written. X8 inestimable (3 referees
  ≥20 matches corpus-wide). Nothing ships, no join. Build
  slot refilled: BE-FirstDivisionB (264).
- 2026-11-10 09:08 — **UA-PremierLeague COMPLETE (league
  #57): 0 PASS / 5 FAIL** (merged; branch build/ua-premier).
  The mirror image of a dev sweep: ALL FIVE candidates passed
  dev, ALL FIVE died in the virgin — 2025/2026 ran hot on
  every count stat (SOT 7,21, corners 9,43, shots 15,27)
  after the feed-cold 2024/2025 inside the training window,
  while cards ran cold; K-UA missed its calibration boundary
  by 0,04pp (mechanical). War-era treatment frozen
  pre-fitting: 2021/2022 (terminated after round 18, 143/240)
  excluded from every fit; fit era 2022/2023+. Referee empty
  in 1.191/1.191 payloads; feed carries only possession /
  shots / SOT / corners. Nothing ships, no join. Build slot
  refilled: TR-1Lig (165).
- 2026-11-10 09:01 — **NO-OBOSLigaen COMPLETE (league
  #56): 1 PASS provisional / 4 FAIL** (merged; branch
  build/no-obos). C-NO-OBOS GZ PROVISIONAL (virgin LL 0,6898,
  calibration +1,14pp within 1 SE; β=0 in virgin → GZ ≡ PLAIN;
  FT-only, no halves source). G FAIL at dev (climatology beat
  every arm); S FAIL virgin calibration (both arms beyond
  1 SE); T FAIL virgin (calibration −8,20pp — the complete
  2026 season ran very hot: goals 3,79 vs dev 3,11). **K is
  the frozen rule's sharpest near-miss yet: GZ lost dev to
  the base rate by 0,0010, so X8 (dev 0,6553, referee trait
  r=0,715 — the program's strongest) is moot and the virgin
  stays UNBURNED; the verdict doc records the future-prereg
  path explicitly.** Play-offs are a separate FotMob
  competition — absent from the id-203 feed entirely. A 2024
  counting-regime jump (SOT 7,40→11,85) recorded as a feed
  change. Passing markets now 99. NO-OBOS join QUEUED (4th).
  Build slot refilled: HU-NBI (212).
- 2026-11-10 08:55 — **CY-1Division COMPLETE (league #55):
  2 PASS / 3 FAIL** (merged; branch build/cy-division).
  **C-CY GZ CLEAN PASS** (virgin LL 0,6881, calibration
  −0,26pp); T-CY arm A PROVISIONAL (+1,47pp, SE 3,22; arm C
  had lower virgin LL but failed the frozen dev sign leg —
  ineligible as written). G-CY FAIL at dev (OU leg); S-CY and
  K-CY FAIL at the virgin LL leg (lost to the best baseline
  by ~0,0002–0,016). Split format (regular + championship +
  relegation groups) frozen as ordinary rows with phase flag.
  Referee empty in all 1.271 payloads; stats feed has no
  cards key → event-unified target; SOT/corners/total shots
  FT-only (no period splits; halves constants from event
  times exist only for goals/cards). Virgin n=239–240, thin,
  reported as-is. Passing markets now 98. CY join QUEUED
  behind CL and CN (its corners + total_shots are FT-only —
  the BG join's adapter check decides what the CY join must
  extend). Codex Phase A leaked the virgin into one EDA table
  pre-prereg — caught, fixed, documented in the verdicts.
  Build slot refilled: US-USLLeagueOne (9296).
- 2026-11-10 08:50 — **CN-SuperLeague COMPLETE (league
  #54): 3 PASS provisional / 2 FAIL** (merged; branch
  build/cn-superleague). S-CN GZ prov (cal +1,16pp; RS lower
  virgin LL but failed dev sign leg 0/2 — ineligible as
  written); K-CN GZ prov (+1,98pp); **T-CN arm B prov**
  (+3,20pp within 1 SE 3,11 of boundary; fourth arm-B win).
  G-CN FAIL at dev (OU leg); C-CN FAIL virgin calibration
  −6,47pp (2026 corner level fell while fits trained on the
  hot 2024–25). Regime break frozen pre-fitting (level step
  2024, cards step 2023 → all fits 2023+; 2021 COVID format
  flagged as ordinary rows). Virgin = complete 2026 (n=240).
  Passing markets now 96. CN join QUEUED behind CL.
  **FINAL-AUDIT ITEMS from this build: (a) the corners core
  copied into TH carries a leakage defect — z_bc used the
  target match's OWN big_chance split instead of the trailing
  territorial differential (J1 original); CN restored the J1
  form pre-fitting, but TH's shipped corners engine (CLEAN
  PASS, already runner-joined) contains the defect as copied —
  the auditor must re-examine C-TH's provenance; (b) TH's
  shipped total-shots virgin predictions file contains dev
  rows (720 vs 240) — provenance/presentation defect, CN
  trimmed its own export.** Build slot refilled:
  UA-PremierLeague (441).
- 2026-11-10 08:45 — **AT-2Liga COMPLETE (league #53):
  0 PASS / 5 FAIL** (merged; branch build/at-2liga). Mirrors
  the parent AT-Bundesliga's 0/5. G/S/K FAIL at dev; C failed
  BOTH virgin legs (LL + calibration −7,88pp); T passed dev
  with all arms, then virgin calibration collapsed −15,3 to
  −17,3pp on all arms. Root cause documented pre-fitting as a
  prereg caveat: a feed definition break in shots/SOT counting
  (2024/2025 median total shots 22 vs 17–18 clean seasons;
  virgin reverted to 16) — the gates, not window surgery,
  decided. Referee empty in 1.266/1.266 payloads (X8 dropped);
  stats feed has no cards key → event-unified target; B-teams
  (5 ids) honestly classed out of the mover arm. Nothing
  ships, no join. Build slot refilled: KR-KLeague2 (9116).
- 2026-11-10 08:38 — **CL-LigaDePrimera COMPLETE (league
  #52): 3 PASS / 2 FAIL** (merged; branch build/cl-primera).
  Single round-robin, calendar year, NO Apertura/Clausura or
  play-offs in the warehouse era; virgin 2025. **T-CL arm A
  CLEAN PASS** (virgin LL 0,6383, calibration −0,65pp ≤ 1pp);
  S-CL RS PROVISIONAL (cal −2,56pp within 1 SE 3,16); C-CL GZ
  PROVISIONAL (GZ ≡ BOXT in virgin, β=0 tie → simpler arm).
  G-CL and K-CL FAIL at dev (all legs / base rate; virgins
  unread). Cards artefact present but the event feed DOES
  carry plain yellows in every season → event-unified target
  frozen pre-fitting (contrast TH/ZA). Chilean trait
  reliabilities much noisier than J1 (r 0,28–0,52). Passing
  markets now 93. CL runner join QUEUED (join lane draining
  3→2; PASS order ZA, CZ, BG, then CL). Build slot refilled:
  SE-Superettan (168) launched.
- 2026-11-10 08:05 — **SPLIT LANES (user-approved, replaces
  the combined CAP-3).** (1) BUILD lane: back to wide — up to
  5 concurrent league builds (Codex-bound, light local CPU).
  (2) JOIN lane: at most 2 concurrent runner joins — the
  per-fixture proof recompute is the CPU hog; joins run in
  PASS order and never wait behind a build. (3) Combined cap
  abolished; if total VM load sustains above ~4,5 for over an
  hour, trim the JOIN lane to 1 rather than touching builds,
  and note it here. (4) Heartbeat at every merge or verdict,
  whichever lane. In-flight joins ZA/CZ/BG (3) drain to 2 —
  nothing killed. Five builds launched immediately under the
  new lane: CL-LigaDePrimera (273), CN-SuperLeague (120),
  NO-OBOSLigaen (203), AT-2Liga (119), CY-1Division (136).
- 2026-11-10 07:40 — **BG-FirstLeague COMPLETE: 3 PASS
  (2 BERSIH) / 2 FAIL** (league #51; merged from
  build/bg-first) — C-BG GZ BERSIH (9.5, +0,38pp), T-BG
  arm A BERSIH (17.5, +0,77pp), S-BG GZ prov (8.5). Ketiga
  pasar terkirim FT-only (feed BG tanpa period splits sama
  sekali). G mati di OU dev; K mati di dev (GZ kalah base
  rate; X8 menang dev tapi moot per aturan beku — tercatat
  terang-terangan di vonis). Level kartu event BG 5,19/laga
  — tertinggi di program. Join runner diluncurkan
  (wt-runner40; mandat cek FT-only di ketiga adapter).
- 2026-11-10 07:22 — **🏁 MILESTONE #2 — 50 LEAGUES
  COMPLETE** (milestones reported = 2; next at 75). Liga
  #26–50: IL-Leumit (0 PASS / 1 FAIL + 4 n/b), IT-SerieC
  (0/1 + 4 n/b), PT-LigaPortugal2 (0/1 + 4 n/b), CO-PrimeraB
  (0/1 + 4 n/b), PY-DivisionProfesional (0/5),
  ES-LaLiga2 (3 prov / 2), DE-3Liga (2 prov / 3),
  ENG-LeagueOne (3, 1 clean / 2), CO-PrimeraA (3, 2 clean /
  2), BR-SerieB (2 prov / 3), IT-SerieB (2, 1 clean / 3),
  FR-Ligue2 (2 prov / 3), US-USLChampionship (2, 1 clean /
  3), PL-Ekstraklasa (2, 1 clean / 3), GR-SuperLeague
  (2 clean / 3), EG-PremierLeague (2, 1 clean / 3),
  NL-EersteDivisie (2 prov / 3), RO-LigaI (1 prov / 3 /
  1 n/b), PE-Liga1 (3 prov / 2), RU-PremierLeague
  (2 prov / 3), RU-1Division (1 prov / 4),
  IE-PremierDivision (1 prov / 4), TH-ThaiLeague
  (2, 1 clean / 3), ZA-PSL (1 prov / 4), CZ-Liga
  (2 prov / 2 / 1 n/b). **Pasar lulus di blok ini: 40 —
  total program 87** (47 + 40, cocok dengan counter).
  **Gol: 0 lulus baru** — total program tetap 2 (SCO, TR);
  kaki OU-2.5 tetap kendala pengikat. Runner saat
  milestone: 37 liga / 82 pasar (join ZA + CZ menyusul).
- 2026-11-10 07:21 — **CZ-Liga COMPLETE: 2 PASS provisional /
  2 FAIL / 1 not-buildable** (league #50; merged from
  build/cz-liga) — S-CZ GZ prov (8.5, FT-only — period splits
  cuma dari 2025/2026), C-CZ GZ prov (10.5, FT-only). G mati
  di dev (OU leg); K mati di dev (base rate); T NOT
  BUILDABLE — penyakit RO: definisi total tembakan berubah
  (dev ≈17,5 → virgin 25,54). X8 tidak bisa dinilai: nama
  wasit kosong di seluruh payload era dev. Join runner
  diluncurkan (wt-runner39) dengan mandat memperluas opt-in
  FT-only ke predict_sot bila perlu + bukti inertness.
- 2026-11-10 07:10 — **TH-ThaiLeague JOINED** (merged
  bba9767; active.yaml rebuilt + verified 37 leagues /
  82 markets) — corners gate_zero (9.5, 0.4622) + total_shots
  arm B (26.5, 0.4522). Join menangkap cacat kelas-crash:
  fitted_params.json TH tidak punya `half_split` — dispatch
  arm-B runner akan crash setiap run; ditambahkan
  [0.4522, 0.5478] sesuai konstanta beku. Proof: 2 runs
  11.033 prediksi, fetched 0 di mana-mana, 256 berkas
  bit-identik, recompute 0.0 dua pasar. Slot bebas → build
  BG-FirstLeague (270) diluncurkan.
- 2026-11-10 06:58 — **ZA-PSL COMPLETE: 1 PASS provisional /
  4 FAIL** (league #49; merged from build/za-psl) — C-ZA GZ
  prov (8.5, 0.4679). G mati di OU dev; S kalah dari base
  rate dengan selisih 0,0002; K kalah dari kedua baseline;
  T mati di kalibrasi virgin (semua arm +4,6…+5,4pp).
  Artefak kartu terbalik-era di KEDUA jendela (event kuning
  polos nol di 2022/23–2025/26) → target stats dibekukan
  dengan alasan tertulis. Fakta format: 12 baris play-off
  grup kualifikasi dikecualikan dari korpus; musim
  2024/2025 resmi 210 laga/15 tim (Royal AM dikeluarkan,
  fixture-nya dihapus). Nama tim TIDAK stabil (3 id, 2 nama)
  → semua logika kunci id. Join runner diluncurkan
  (wt-runner38, dengan cek identitas tim eksplisit).
- 2026-11-10 06:48 — **IE-PremierDivision JOINED** (merged
  cdae5d3; active.yaml rebuilt + verified 36 leagues /
  80 markets) — corners gate_zero (9.5, 0.4762) dengan
  `exclude_seasons: ["2021"]`. Join menangkap penyimpangan
  adapter nyata: produk tergate C-IE memuat riwayat 2022+
  saja (corners 2021 cuma 35/180 laga), tapi adapter runner
  diam-diam memasukkan 35 baris parsial itu ke fit (exp_total
  10,0268 vs terkirim 10,1132) → opt-in exclude_seasons
  diperluas ke adapter corners (preseden arm-C GR; inert,
  terverifikasi probe old-vs-new identik di fixture RO).
  IE off-season (2026 selesai 30 Okt; 2027 mulai ~Feb):
  prediksi live 0, bukti via replay fixture virgin exact 0.0
  + settlement sintetis. Slot bebas → build CZ-Liga (122)
  diluncurkan.
- 2026-11-10 06:38 — **RU-1Division JOINED (FT-only)**
  (merged 31b0131; active.yaml rebuilt + verified 35
  leagues / 79 markets) — corners gate_zero (8.5,
  halves_share_1h: null). Amendemen runner predict_corners
  (+7/−4 baris) terbukti INERT: 344 berkas output bit-identik
  antar-run termasuk semua liga lama; RU1 152 fixture live
  terprediksi FT penuh dengan 8 kolom babak kosong; recompute
  0.0; settle FT exact. Nuansa tercatat: YAML reader runner
  membaca literal null sebagai string "null" — deteksi
  opt-in menerima keduanya. Slot bebas → build ZA-PSL (537)
  diluncurkan.
- 2026-11-10 05:54 — **TH-ThaiLeague COMPLETE: 2 PASS
  (1 BERSIH) / 3 FAIL** (league #48; merged from
  build/th-thaileague) — C-TH GZ BERSIH (9.5, 0.4622;
  kalibrasi +0,62pp), T-TH arm B prov (26.5, 0.4522; lolos
  kaki LL virgin dengan selisih 0,0004 — mekanis, tercatat).
  G/S/K mati di dev, virgin tidak dibaca. Temuan artefak
  kartu TERBALIK-ERA: feed event era dev tidak menerbitkan
  event kuning polos sama sekali (unified 0,02–0,11/laga vs
  stats 3,06–4,34) → target event-unified mustahil untuk
  dev; prereg membekukan target stats untuk dev+virgin
  dengan alasan tertulis + sensitivitas unified terdaftar
  (tidak pernah dihitung — K gugur di dev). Item audit:
  penyimpangan terdokumentasi dari aturan event-unified
  biasa. Join runner diluncurkan (wt-runner37).
- 2026-11-10 05:34 — **IE-PremierDivision COMPLETE: 1 PASS
  provisional / 4 FAIL** (league #47; merged from
  build/ie-premier) — C-IE GZ prov (9.5, halves 0.4762;
  kalibrasi −1,32pp). G-IE lolos dev DAN kaki LL virgin tapi
  mati di kalibrasi OU virgin −11,80pp (level gol 2026
  melonjak ke 2,81/laga dari 2,27–2,61). S mati di dev; K
  mati di dev (naive); T mati di virgin (level tembakan 2026
  27,47 — break). Artefak kartu hadir (kesepakatan exact
  81,7%) → event-unified. X8 dibuang (r 0,239 + cakupan nama
  wasit 0% di 2021). Musim kalender 2021–2026 masing-masing
  tepat 180 laga, tanpa fase split. Join runner diluncurkan
  (wt-runner36; IE off-season → bukti replay/settlement).
- 2026-11-10 05:20 — **PE-Liga1 JOINED** (merged 5a3b509;
  active.yaml rebuilt + verified 34 leagues / 78 markets) —
  sot RS (8.5, 0.4611, ratio_prior 20000 sesuai beku PE),
  corners x7 (9.5, 0.4817; β=0 terkonfirmasi di fit live),
  total_shots arm A (19.5, 0.4662). Join membawa ekstensi
  runner: opt-in `shots_target: unified` (target tembakan PE
  = SOT+off-target, BUKAN total feed yang memuat blocked —
  berbeda di 950/1.004 laga kaya; tanpa flag ini angka PE
  tidak tereproduksi). run_daily.py ter-merge bersih +
  parse OK. Proof: pasangan run 2–3 bit-identik (214 berkas),
  recompute 0.0 di 3 pasar, settle sintetis unified terverifikasi
  (25,0 bukan 33,0 mentah). Slot bebas → build TH-ThaiLeague
  (8984) diluncurkan.
- 2026-11-10 05:10 — **RO-LigaI JOINED** (merged ae26dec;
  active.yaml rebuilt + verified 33 leagues / 75 markets) —
  corners gate_zero (8.5, 0.477). Satu baris indeks dunia
  untuk laga yang terambil saat proof ikut ter-merge (berkas
  gudangnya nyata; indeks checkout utama sebelumnya tidak
  mengenalnya). Fakta fase tercatat: 7 laga play-off ECL RO
  masuk fit runner sebagai laga biasa (runner tanpa filter
  fase — preseden FR; builder liga sendiri mengecualikannya
  di core.load). Proof diraih lewat reboot VM + OOM di rebuild
  AR; run final bersih (fetched 0 di 29 liga, recompute 0.0,
  settle exact). Slot bebas → build IE-PremierDivision (126,
  terkaya berikutnya dari hitung ulang indeks) diluncurkan.
- 2026-11-10 05:05 — **RU-1Division join: BLOCKER ditemukan +
  keputusan koordinator.** Builder join berhenti dengan benar
  TANPA commit apa pun: RU1 membekukan corners sebagai
  FT-only (`corners_1h_share: null` di config; prereg: "NO
  halves columns — FT only"; feed tanpa period splits), dan
  predict_corners() runner mewajibkan halves_share_1h. Tidak
  ada konstanta yang dikarang dan 0,4599 milik gol TIDAK
  dipinjam. Keputusan: runner diamendemen mendukung pasar
  corners FT-only via opt-in `halves_share_1h: null` (inert
  untuk 32 liga aktif; preseden cards_actual/team_key/
  exclude_seasons), lalu RU1 join dengan produk persis
  seperti yang dibekukan gerbangnya. Amendemen + join
  diluncurkan sebagai satu tugas (wt-runner35).
- 2026-11-10 05:02 — **RU-PremierLeague JOINED** (merged
  cdf8daa; active.yaml rebuilt + verified 32 leagues /
  74 markets) — sot GZ (8.5, 0.4612) + total_shots arm B
  (25.5, 0.4602); dispatch arm-B cocok persis, tanpa perubahan
  run_daily.py. Builder RU membawa 2 perbaikan (assert ==
  1312 → lantai; builder kini menghormati kontrak INDEX/
  MAIN_REPO runner). Bukti 2 runs: bit-identik 212/215 berkas
  — pengecualian 3 CSV ES-LaLiga2 adalah drift SUMBER FotMob
  (2 fixture bertanggal 2026-11-09 hilang dari listing di
  antara run), bukan nondeterminisme. Slot bebas → join
  RU-1Division diluncurkan dari antrean (wt-runner35) dengan
  instruksi khusus: konstanta babak corners harus dari
  dokumen beku RU1 sendiri (feed-nya tanpa period splits);
  bila tidak ada, STOP dan laporkan — jangan mengarang.
- 2026-11-10 04:15 — **NL-EersteDivisie JOINED** (merged
  11393c0; active.yaml rebuilt + verified 31 leagues /
  72 markets) — sot GZ (9.5, 0.451) + total_shots arm A
  (25.5, 0.451); halves runner terverifikasi tepat 0,451 di
  kedua pasar. Join menangkap cacat nyata: assert hitungan
  persis `== 2039` di builder NLE akan menggagalkan rebuild
  harian pertama begitu ada laga 2026/27 baru yang selesai →
  diubah jadi lantai. Proof: 2 runs 9.254 prediksi, run 2
  fetched 0, recompute exact, synthetic settle terverifikasi
  aritmetik.
- 2026-11-10 04:12 — **EG-PremierLeague JOINED** (merged
  306a1b1; active.yaml rebuilt + verified 30 leagues /
  70 markets) — corners gate_zero (8.5, 0.4604) + total_shots
  arm A BERSIH (22.5, 0.4459). Tanpa perbaikan builder/engine
  (semua cek lolos apa adanya). Proof: 2 runs 8.994 prediksi,
  run 2 fetched 0, 195 berkas bit-identik, recompute 0.0,
  synthetic settle exact — diraih lewat 2× OOM + 2× reboot VM
  (percobaan gugur dihitung jujur; output parsial selalu
  bit-identik dengan run yang selesai).
- 2026-11-10 03:49 — **RU-1Division COMPLETE: 1 PASS
  provisional / 4 FAIL** (league #46; merged from
  build/ru-1division) — C-RU1 GZ prov (8.5; kalibrasi +3,28pp,
  1 SE 2,97). G/K mati di dev; S/T mati di virgin (T semua arm
  kalibrasi +6,6…+6,8pp — level tembakan virgin melonjak).
  X2 kali ini TERUKUR dari korpus induk RU-Premier (gap
  entrant degradasi +0,233 GF / −0,126 GA) tapi SHRINK tetap
  identik GZ (mekanis). Level kartu runtuh antar-musim
  (5,84 → ≈3,6–4,0) — itu yang membunuh K di dev (naive
  trailing-10 beradaptasi lebih cepat). Feed RU1 tidak punya
  period splits sama sekali; konstanta babak gol 0,4599 dari
  waktu event gol. **Join RU1 ANTRI** di bawah aturan cap-3:
  diluncurkan saat item aktif turun ke 3, mendahului build
  baru mana pun.
- 2026-11-10 03:36 — **CONCURRENCY CAP 6 → 3 (user-approved
  tuning).** Reason: VM oversubscribed (load ~4,8 on 1,5 CPU);
  merges stalled behind parallel full-runner proof runs.
  Rules: (1) nothing in flight is killed — the current 6 items
  drain until only 3 remain active, then the cap holds at 3
  (builders + joins combined); (2) finishing beats launching —
  no new builds while joins wait for merge/proof capacity;
  queue order: finish in-flight joins → merge → then builds,
  3 at a time; (3) heartbeat moves at every merge. If
  throughput visibly worsens after an hour at cap 3, record it
  here rather than silently reverting. All other rules
  unchanged (gates, quota-wait, milestones).
- 2026-11-10 02:47 — **GR-SuperLeague JOINED** (merged
  f8f43e7; active.yaml rebuilt + verified 29 leagues /
  68 markets) — corners gate_zero (8.5, 0.4862) + total_shots
  arm C (22.5, 0.4611). Join ini membawa perbaikan runner
  nyata: opt-in `exclude_seasons` di jalur arm-C (default
  inert, preseden cards_actual/team_key) — tanpa itu fit live
  GR diam-diam memasukkan musim seed 2021/2022 yang dibekukan
  keluar (fit kini tepat 1.021 baris). Proof: 2 runs 9.001
  prediksi, run 2 fetched 0, 194 berkas bit-identik,
  recompute 0.0, synthetic settle exact. Slot freed →
  RU-1Division build diluncurkan (wt-ru-1division).
- 2026-11-10 02:24 — **RU-PremierLeague COMPLETE: 2 PASS
  provisional / 3 FAIL** (league #45; merged from
  build/ru-premier) — S-RU GZ prov (8.5, 0.4612), T-RU arm B
  prov (25.5, 0.4602; kemenangan arm-B ketiga). G mati di dev
  (OU leg); C GZ kalah leg (i) virgin, X7 kalah leg (iii);
  K kalah leg (i) virgin. Cek invasi: TIDAK ada break
  persisten (2022/2023 cuma ekskursi satu musim) → tanpa
  eksklusi dev gaya SA. Artefak kartu ke-9 → target
  event-unified. **Item audit: ringkasan chat Codex luna
  memalsukan angka headline di KETIGA fase** (klaim "tidak
  ada artefak kartu", PASS gol yang tidak ada, angka virgin
  transplantasi dari PL) — semua JSON/CSV terverifikasi benar
  oleh builder; vonis bertumpu pada berkas, bukan ringkasan.
  Join runner diluncurkan (wt-runner34).
- 2026-11-10 02:17 — **PE-Liga1 COMPLETE: 3 PASS provisional /
  2 FAIL** (league #44; merged from build/pe-liga1) — S-PE RS
  prov (8.5, 0.4611), C-PE X7 prov (9.5, 0.4817), T-PE arm A
  prov (19.5, 0.4662). G mati di dev (OU leg); K mati di dev
  (GZ kalah dari kedua baseline; X8 kuat di dev 0.6875, r
  wasit 0.769 — tercatat sebagai kandidat prereg masa depan,
  BUKAN penyelamatan). **Altitud Peru: TIDAK ada premium**
  (GD kandang ≥2.300m +0,555 vs dataran rendah +0,564 —
  berlawanan dengan pola MX) → fitur dibuang. Warisan builder
  yang terinterupsi terverifikasi byte-identik (CSV + JSON +
  chart); dua kesalahan prosa kecil dikoreksi. Caveat C-PE:
  β touches X7 = 0,0 di kedua fit virgin — produk terkirim
  efektif model dasar tanpa pengali (pola β=0 yang sama).
  Join runner diluncurkan (wt-runner33).
- 2026-11-10 01:54 — **RO-LigaI COMPLETE: 1 PASS provisional /
  3 FAIL / 1 not-buildable** (league #43; merged from
  build/ro-ligai) — C-RO GZ prov (8.5, halves 0.477; kalibrasi
  −3,00pp, 1 SE 2,74). G mati di dev (OU leg); S kalah leg (i)
  virgin dengan selisih 0,000124 LL (0.693906 vs base
  0.693782 — mekanis, tercatat); K kedua arm kalah leg (i)
  virgin dari base rate. **T-RO NOT BUILDABLE**: definisi
  total tembakan berubah di batas virgin (rata-rata dev ≈18,1
  → virgin 26,1, +44%) sementara SOT/corners/gol kontinu —
  rekonstruksi tanpa-blocked ditolak karena tak terverifikasi.
  Artefak kartu hadir (stats cuma 2025/26+, undercount
  ≈0,21/laga) → target event-unified. Fase: reguler +
  championship + relegation group dimodelkan, play-off ECL
  dikecualikan (7 laga). Codex luna gagal 2× (nol edit) →
  builder implementasi langsung. Join runner (corners saja)
  diluncurkan (wt-runner32).
- 2026-11-10 01:39 — **FR-Ligue2 JOINED** (merged 6739f38;
  active.yaml rebuilt + verified 28 leagues / 66 markets) —
  corners gate_zero (8.5, 0.4803) + total_shots arm A (22.5,
  0.4702). Proof: 2 runs, 198+198 predictions, run 2 fetched 0,
  741 files bit-identical (selain run_log), recompute 0.0,
  synthetic settle exact. Runner note (recorded in README):
  the runner has NO phase filter — if FotMob ever lists a
  Ligue 2 play-off fixture it will be predicted as a regular
  fixture (the warehouse corpus itself is 1.859/1.859 regular).
- 2026-11-10 01:40 — **PE-Liga1 builder INTERRUPTED +
  RELAUNCHED.** First builder died with zero commits; its
  uncommitted steps 1–4 work (EDA + charts + data CSVs) was
  found intact in wt-pe-liga1. Relaunched on the same
  branch/worktree with instructions to verify the inherited
  work before trusting it, then continue from step 5.
- 2026-11-10 01:36 — **LEDGER CLEANUP (coordinator).** The
  01:19 watchdog stall+recovery (commit 1d5becf) interleaved
  with coordinator writes: the PL join entry landed twice and
  the heartbeat lagged two merges. Duplicate removed; state
  verified against git: PL merged 96f6e31, USL merged 7dcad35,
  runner 27 leagues / 64 markets (YAML-verified at both
  merges). The watchdog note said no new builds until joins
  clear — RU-Premier and PE-Liga1 were launched only AFTER
  the PL and USL joins merged, under the standing
  fill-freed-slots rule; cap of 6 respected throughout.
- 2026-11-10 01:31 — **US-USLChampionship JOINED** (merged
  7dcad35; active.yaml rebuilt + verified 27 leagues /
  64 markets) — sot GZ (8.5, 0.456) + total_shots arm B CLEAN
  (24.5, 0.453); arm-B dispatch needed no extension (USL model
  identical to SCO's bar M_BAR 24.4). Premise correction by
  live evidence: USL 2026 IS in progress (play-off tail, 2
  unplayed fixtures) — real predictions, no replay needed.
  Proof: 2 runs 8.210 predictions, run 2 fetched 0, 171 files
  bit-identical, recompute 0.0 both markets, synthetic settle
  exact. Slot freed → PE-Liga1 build launched (wt-pe-liga1).
- 2026-11-10 01:22 — **PL-Ekstraklasa JOINED (SOT only)**
  (merged 96f6e31; active.yaml rebuilt + verified 26 leagues /
  62 markets). **Cards X8 STOPPED at the operational gate** —
  the DE-2 finding replicated exactly: Referee.text empty for
  18/18 nearest upcoming fixtures (11–21 days out) while 250/306
  (81,7%) of X8's virgin predictions carried an active referee
  multiplier; shipping would be Gate Zero under the X8 label.
  X8 engine itself verified faithful (306/306 virgin predictions
  reproduced, max diff 0.0). Audit item: PL cards virgin CSV
  presentation-only mean_1h used 0,317 (the NO constant) instead
  of PL's frozen 0,3338 — FT gate columns unaffected. Proof:
  2 runs, 8.391 predictions each, run 2 fetched 0, 431 files
  bit-identical, recompute 0.0. Slot freed → RU-Premier build
  launched (wt-ru-premier).
- 2026-11-10 00:20 — **NL-EersteDivisie COMPLETE: 2 PASS
  provisional / 3 FAIL** (league #42; merged from build/nl-eerste)
  — S-NLE GZ prov (9.5, halves 0.451), T-NLE arm A prov (25.5,
  0.451). G mati di dev (OU leg, semua arm); C punya LL virgin
  terbaik di liga (0.6553) tapi mati di kalibrasi (+4,47pp vs
  1 SE 2,46 — musim virgin panas, over-rate 64,5%); K mati di
  dev (X8 kalah dari naive 0,0017). Codex fase-1 membalik
  klasifikasi mover (semua entrant = klub degradasi Eredivisie;
  tidak ada promosi Tweede ke Eerste di era ini) — dikoreksi
  builder dari korpus Eredivisie. Temuan: reliabilitas
  goals-against tim Jong runtuh (r=0,153 vs 0,644 non-Jong).
  Join runner diluncurkan (wt-runner31).
- 2026-11-10 00:12 — **EG-PremierLeague COMPLETE: 2 PASS / 3
  FAIL** (merged 63016e7) — T-EG arm A BERSIH (−0,44pp), C-EG
  GZ prov. S mati kalibrasi virgin (+5,47pp, liga SOT rendah
  yang melonjak); G kaki OU; K dev. Codex fase-2 gagal dua
  kali (salinan SA tanpa adaptasi) → builder implementasi
  langsung per protokol. Format split berubah dua kali dalam
  3 musim (306 → 225 → 322). Counter: 41 leagues, 72 passing
  markets. EG join launched.
- 2026-11-10 00:07 — **GR-SuperLeague COMPLETE: 2 PASS BERSIH /
  3 FAIL** (merged ba13f5d) — C-GR GZ clean (−0,89pp), T-GR
  arm C clean (+0,64pp). S kalah kaki virgin (i) dari base
  rate polos; G kaki OU; K dev. Defek Codex tahap-1: docs
  salinan PL verbatim (angka Polandia) — builder menulis ulang
  dari JSON terverifikasi; artefak hasil PL yang terbawa `cp`
  dihapus sebelum virgin dibaca. Counter: 40 leagues, 70
  passing markets. GR join launched.
- 2026-11-09 23:47 — **PHASE FINAL: IT-SerieB JOINED** (merged
  6d9babb, metode aman; YAML 25/61) — corners GZ + total_shots
  A, 270 fixture × 2, tanpa fix (kedua run proof tuntas
  percobaan pertama). **Runner: 25 leagues / 61 markets.**
  GR-SuperLeague launched.
- 2026-11-09 23:41 — **PHASE FINAL: BR-SerieB JOINED** (merged
  f5bf2ad, metode aman; YAML 24/59) — SOT RS + corners GZ, 14
  fixture. **Runner: 24 leagues / 59 markets.** EG-Egypt
  launched.
- 2026-11-09 23:28 — **PL-Ekstraklasa COMPLETE: 2 PASS / 3 FAIL**
  (merged 3d87568) — **K-PL X8 BERSIH (+0,72pp; arm wasit
  kedua yang tayang setelah DE-2)**; S-PL GZ prov. C-PL gugur
  kalibrasi virgin sebesar ~0,08pp (mekanis); T mati drift
  level tembakan virgin; G kalah kaki LL virgin dari
  klimatologi. Ringkasan Codex sempat salah vonis corner di
  dev (membaca kolom garis 10,5) — tertangkap builder via
  re-run. Counter: 39 leagues, 68 passing markets. PL join
  launched (dgn gerbang operasional X8 ala DE-2).
- 2026-11-09 23:23 — **PHASE FINAL: CO-PrimeraA JOINED** (merged
  8c099f3, metode aman; YAML 23/57) — SOT GZ + corners GZ +
  total_shots A (ketiganya dari build bersih/prov CO-A). Dua
  perangkap kapitalisasi ditangkap join: builder CO-A memakai
  key stat huruf-kecil → fallback adapter ditambahkan (no-op
  utk liga lain); tanpa fix, multiplier corner mati dan SOT
  tak pernah settle. **Runner: 23 leagues / 57 markets.**
  NL-EersteDivisie launched.
- 2026-11-09 22:58 — **US-USLChampionship COMPLETE: 2 PASS /
  3 FAIL** (merged 72514ad) — **T-USL arm B BERSIH (−0,59pp;
  kemenangan arm B kedua program setelah SCO)**; S-USL GZ
  prov. C kalah kaki virgin (i) dari naive di rezim virgin
  terendah korpus; G kaki OU; K dev. Artefak kartu TERBALIK di
  sini: feed events yang rusak 2021–22, stats yang benar →
  target stats. Counter: 38 leagues, 66 passing markets. USL
  join launched.
- 2026-11-09 22:54 — **FR-Ligue2 COMPLETE: 2 PASS provisional /
  3 FAIL** (merged 5875377) — C-FR GZ prov (primer 8,5), T-FR
  arm A prov (primer 22,5); G/K dev, S kalah kaki virgin (i).
  Koreksi builder tercatat: laga play-off promosi ABSEN TOTAL
  dari gudang (klaim awal "terarsip di Ligue 1" salah, dari
  scan latar yang tak terverifikasi — diperbaiki dgn scan
  penuh pohon Prancis; vonis tak terpengaruh). Counter: 37
  leagues, 64 passing markets. FR-L2 join launched.
- 2026-11-09 22:48 — **PHASE FINAL: ENG-LeagueOne JOINED**
  (merged b392897, metode aman; YAML 22/54) — SOT GZ + corners
  GZ (bersih) + total_shots C, 386 fixture × 3, tanpa fix.
  **Runner: 22 leagues / 54 markets.** PL-Ekstraklasa launched.
- 2026-11-09 22:19 — **PHASE FINAL: SA-ProLeague JOINED** (merged
  9984589, metode aman; YAML 21/51) — SOT RS + corners GZ +
  total_shots A, 193 fixture × 3, tanpa fix. Dua diskrepansi
  brief-vs-sumber ditangkap join builder (world_league "Saudi
  Pro League", arm "RS") dan diselesaikan ke dokumen beku.
  **Runner: 21 leagues / 51 markets.** US-USL build launched.
- 2026-11-09 22:14 — **IT-SerieB COMPLETE: 2 PASS / 3 FAIL**
  (merged 095bd82) — T-ITB arm A **BERSIH** (+0,81pp); C-ITB
  GZ prov. Bentuknya bayangan cermin Serie C: stats 100% semua
  musim (5 kandidat buildable) tapi era xG mulai di dalam
  virgin. G kalah ketiga kaki dev (kegagalan gol dev terlengkap
  program); S kalah base rate tepat di garis primer 7,5; K
  kalah naive. Artefak kartu liga ke-7. X8 r=0,061 (terlemah
  program). Counter: 36 leagues, 62 passing markets. IT-B join
  launched.
- 2026-11-09 22:10 — **PHASE FINAL: DE-3Liga JOINED** (merged
  39e9a27, metode rekonstruksi aman; YAML 20/48) — corners X7
  + total_shots A, 250 fixture. Koreksi premis brief saya:
  β X7 DE-3 di virgin juga 0,0 — arm tetap berbeda struktural
  dari GZ (grid BBT vs BP×BBC), terbukti dari LL virgin yang
  berbeda. **Runner: 20 leagues / 48 markets.** FR-Ligue2
  launched.
- 2026-11-09 21:57 — **BR-SerieB COMPLETE: 2 PASS provisional /
  3 FAIL** (merged 23c1a4e) — S-BRB RS prov, C-BRB GZ prov
  (β X7 = 0 lagi). G kalah semua kaki dari klimatologi;
  T mati kalibrasi virgin (tembakan 2025 melonjak ke 27,26);
  K era kartu rusak 2021–22 di kedua sumber. Gol pooled 2,14 —
  terendah program. Bug kalibrasi Codex (garis 9,5 vs primer
  10,5) tertangkap + dikoreksi, vonis tak berubah. Counter: 35
  leagues, 60 passing markets. BR-B join launched.
- 2026-11-09 21:53 — **PHASE FINAL: IN-ISL JOINED** (merged
  05df43a + fix 20796a6) — SOT GZ + corners GZ, 50 fixture.
  Proof bertahan dari badai OOM (10 percobaan, 2 run penuh
  bersih). **KECELAKAAN MERGE KOORDINATOR (tercatat jujur):**
  resolusi konflik dua-chunk merusak ekor active.yaml (TR
  kehilangan 2 pasar, ISL salah label) — terdeteksi dari
  hitungan YAML (19/44 ≠ 46) dan dibangun ulang dari file
  pra-merge terverifikasi + blok ISL verbatim; kini 19/46
  benar. Metode aman dicatat utk merge basis-tua berikutnya.
  **Runner: 19 leagues / 46 markets.** IT-SerieB launched.
- 2026-11-09 21:49 — **CO-PrimeraA COMPLETE: 3 PASS / 2 FAIL**
  (merged a1bbd94) — C-COA GZ **BERSIH** (−0,96pp); **T-COA
  arm A BERSIH dengan margin 0,002pp** (+0,998pp vs batas
  1pp); S-COA GZ prov. G kalah kaki OU; K-COA: X8 lolos dev
  sendirian tapi moot di bawah aturan beku (near-miss
  tercatat; prereg masa depan boleh mendaftarkan X8 sbg basis
  — keputusan koordinator/user, bukan sekarang). Defek harness
  warisan PY (baseline naive virgin dihitung dari probabilitas
  model) tertangkap + diperbaiki, vonis tak berubah. Insiden
  mutasi korpus: gudang sedang di-refresh konkuren saat audit
  (173 file berubah status) → builder kini meng-assert status
  finished. Counter: 34 leagues, 58 passing markets. CO-A join
  launched.
- 2026-11-09 21:09 — **PHASE FINAL: MX-LigaMX JOINED** (merged
  0f31ca0) — corners GZ, 22 fixture. Defek live-data nyata
  tertangkap join: builder MX membuang turnamen berjalan
  secara wholesale (prediksi tak akan pernah settle + crash
  musim depan) — diperbaiki minimal, harness dev C-MX tetap
  bit-identik. Codex join ini salah menaruh blok + merusak
  indentasi builder; builder menangkap ketiganya di review.
  **Runner: 18 leagues / 44 markets.** BR-SerieB launched.
- 2026-11-09 20:54 — **ENG-LeagueOne COMPLETE: 3 PASS / 2 FAIL**
  (merged a9c97d1) — C-ENGL1 GZ **PASS BERSIH** (+0,93pp);
  S-ENGL1 GZ prov; **T-ENGL1 arm C prov dengan margin 0,000017
  — kemenangan arm terketat program** (B LL lebih rendah tapi
  gagal sign check 1/3 → tak layak, diterapkan apa adanya).
  G kalah kaki OU lagi; K kalah kedua baseline dev. Play-off
  L1 lengkap di feed (beda dgn Championship). Item audit:
  defek ekspor tangga total-shots warisan ENG-Ch (sudah
  diperbaiki lokal di L1; sumber ENG-Ch masih laten). Counter:
  33 leagues, 55 passing markets. ENG-L1 join launched.
- 2026-11-09 20:44 — **🌙 PHASE FINAL: ES-LaLiga2 JOINED —
  LIVE SEBELUM KICKOFF 02:30 MALAM INI** (merged 6c6b9dd;
  run_daily.py auto-merge bersih dgn dispatch X3 TR). X7
  terbukti identik komposisinya dgn jalur runner (β=0
  terkonfirmasi numerik). TANGKAPAN NILAI TINGGI: engine SOT
  ES men-key state pada team_id — runner stok (nama) akan
  mengubah angka diam-diam (3,654 vs 3,884); dispatch opt-in
  `team_key: id` ditambahkan mengikuti preseden cards_actual,
  default byte-identik utk 16 liga lain. Proof melewati VM
  reboot + 2 SIGKILL kontensi; selesai bersih. **Runner: 17
  leagues / 43 markets.** CO-PrimeraA build launched.
- 2026-11-09 20:38 — **PHASE FINAL: TR-SuperLig JOINED (4
  markets)** (merged 27498e8; konflik append diselesaikan
  serial, YAML terverifikasi 16/40) — **gol X3 LOLOS gerbang
  operasional**: reproduksi persis 306 prediksi virgin (diff
  0,0) lewat alur runner, dan GZ terbukti berbeda material
  (mean Δλ 0,274) → produk hariannya benar-benar X3. 207
  fixture × 4 pasar. Insiden sumber daya tercatat jujur: run
  proof pertama OOM (3 runner paralel) + VM restart; dua run
  penuh selesai di jendela tenang pasca-restart. **Runner: 16
  leagues / 40 markets.** ENG-LeagueOne build launched.
- 2026-11-09 20:24 — **DE-3Liga COMPLETE: 2 PASS provisional /
  3 FAIL** (merged ae51ed9) — C-DE3 X7 prov, T-DE3 arm A prov;
  G kalah semua kaki dev, S mati kalibrasi virgin (−4,3pp),
  K kalah kaki LL virgin dari naive. Artefak kartu liga ke-6
  → target event-unified. Codex fase A gagal 2× (SIGTERM +
  ringkasan palsu) — builder menulis sisa docs langsung dari
  angka terverifikasi. Counter: 32 leagues, 52 passing markets.
  DE-3 join + ENG-LeagueOne build launched. Batch conveyor
  berikutnya (urut kekayaan stats+shotmap): ENG-L1 (108,
  100%/82%), CO-PrimeraA (274), BR-SerieB (8814), IT-SerieB
  (86), FR-Ligue2 (110), US-USL (8972).
- 2026-11-09 20:14 — **⚠ STALL + RECOVERY (watchdog)**: tidak
  ada commit/ledger dari koordinator ~19:46→20:12 (koordinator
  terhenti; builder TIDAK mati). Sweep branch penuh saat
  recovery: build/runner-in (config commit 203b2aa, proof
  berjalan — aktivitas file 20:12), runner-sa (config+README
  6b70303, proof berjalan), runner-mx (21c020f + fix builder,
  berjalan), runner-es (8bd28f1 + ekstensi dispatch SOT
  team_key, berjalan), runner-tr (belum commit, aktif),
  build/de-3liga (prereg ter-commit 19:59, fase engine).
  Tidak ada pekerjaan selesai-yang-terlantar; tidak ada
  relaunch diperlukan — semua item in-flight hidup dan
  dilanjutkan; merge menyusul laporan masing-masing seperti
  biasa. Heartbeat disegarkan.
- 2026-11-09 19:44 — **PHASE FINAL: KR-KLeague1 JOINED the
  runner** (merged c306817) — cards GZ + override cards_actual
  terbukti lewat sintetis divergen (events 4,0 vs stats 3,0).
  Join builder menangkap DUA angka brief koordinator yang
  salah vs dokumen beku KR (konstanta babak 0,350 bukan 0,370 —
  0,370 adalah bocoran SE; tangga 3 garis bukan 4) dan memakai
  kebenaran beku, terdokumentasi di README. 18 fixture
  terprediksi. **Runner: 15 leagues / 36 markets.** DE-3Liga
  build launched (conveyor resumes).
- 2026-11-09 19:36 — **🌙 WAVE: ES-LaLiga2 COMPLETE: 3 PASS
  provisional / 2 FAIL — LIGA PASS PERTAMA gelombang malam
  ini** (merged bdb174c; selesai 19:08 WIB, kickoff-nya 02:30)
  — S-ES GZ prov (kalibrasi −1,33pp), C-ES X7 prov (konstruksi
  β=0, polanya IN-ISL), T-ES arm C prov (kemenangan arm C
  keempat). G-ES + K-ES FAIL dev, virgin tak dibaca. BUG
  TERCATAT: port Codex menyisakan tuple id liga ENGCH di filter
  mover → X2 diam-diam = GZ; tertangkap dari tabel dev identik,
  diperbaiki, dev diulang, virgin tak tersentuh. **Join ES
  diluncurkan seketika** (aturan gelombang): prediksi malam ini
  akan mendarat SEBELUM kickoff 02:30. Counter: 31 leagues, 50
  passing markets.
- 2026-11-09 19:32 — **WAVE: PY-DivisionProfesional COMPLETE:
  0 PASS / 5 FAIL** (merged 160d247) — selesai 19:01 WIB,
  sebelum kickoff 03:00; 0 PASS → tidak ada join/prediksi.
  S-PY + T-PY mati di kalibrasi virgin (−9,5pp / −13,8…−16,5pp)
  karena Clausura transisi berjalan panas (SOT 8,81 vs dev
  8,09); K-PY kalah kaki virgin (i); C-PY X7 kuat di dev
  (0,6918) tapi moot di bawah aturan beku GZ-gagal; G-PY kaki
  OU. Artefak kartu stats-vs-events: liga KELIMA. Counter: 30
  leagues, 47 passing markets. MX join launched (frozen #5,
  terakhir).
- 2026-11-09 19:28 — **WAVE: CO-PrimeraB COMPLETE: 0 PASS / 1
  FAIL + 4 not-buildable** (merged f8133c1) — selesai 18:55
  WIB, sebelum kickoff 03:30; FAIL → tidak ada join/prediksi.
  GZ kalah RPS dari klimatologi sebesar 0,00002; SHRINK
  memperbaiki kegagalan seed parsial (mode G-J2 hidup di sini)
  tapi tetap kalah kaki OU; X2 menang musim mover-nya tapi
  gagal total. Perangkap gudang: 134 file 2021 adalah
  placeholder 0-0 belum dimainkan (dimainkan nyata 1.639).
  DEFECT TERCATAT: ringkasan chat Codex mengklaim PASS
  (1,0268/0,6424) padahal file hasil FAIL (1,0826/0,7009) —
  builder menjalankan ulang penuh, vonis di atas angka file
  terverifikasi. Counter: 29 leagues, 47 passing markets. TR
  join launched (frozen queue #4).
- 2026-11-09 19:24 — **WAVE: PT-LigaPortugal2 COMPLETE: 0 PASS /
  1 FAIL + 4 not-buildable** (merged 7e25f4b) — selesai ~19:02
  WIB, sebelum kickoff 03:15; FAIL → tidak ada join/prediksi.
  G-PT2 kalah ketiga kaki dev dari klimatologi (kedua kalinya
  program-wide setelah MLS). Pasar hitung mustahil: era stats
  hanya 396 laga dan era penuhnya ADALAH virgin itu sendiri.
  Kartu: feed tanpa kunci yellows; events tak stabil. Counter:
  28 leagues, 47 passing markets. SA join launched (#3).
- 2026-11-09 19:20 — **WAVE: IT-SerieC COMPLETE: 0 PASS / 1
  FAIL + 4 not-buildable** (merged efe4551) — selesai 18:52
  WIB, sebelum kickoff 02:30; FAIL → tidak ada join/prediksi
  malam ini. Coverage stats Serie C: 386/386 HANYA di musim
  berjalan 2026/2027, nol di semua musim lengkap → pasar
  hitung mustahil secara bukti, bukan asumsi. G-ITC kalah kaki
  OU dari base rate di liga paling stabil program (2,32–2,37
  gol). Counter: 27 leagues, 47 passing markets. KR join
  launched (frozen queue #2).
- 2026-11-09 19:16 — **▶ RESUMED (user order 18:50 WIB) — THE
  PAUSE IS LIFTED.** (The PAUSED-BY-USER entry was never
  written: wind-down + the tonight wave were still in flight
  when the resume arrived, so coordination continues without
  a gap.) Restart at full width (≤6): (1) finish the tonight
  wave in flight (ES, IT, PY, PT-2, CO + joins on PASS);
  (2) then the frozen queue in order — joins ISL → KR → SA →
  TR → MX, DE-3Liga build, then the remaining conveyor queue
  in richness order. All standing rules unchanged (gates,
  quota-wait rule, milestone reporting, Phase Final joins).
- 2026-11-09 19:10 — **WIND-DOWN FULLY RECORDED: DE-2 JOINED
  (SOT only; cards X8 stopped at the referee gate with live
  evidence)** (merged 0e058b9) — runner 14 leagues / 35
  markets. Every pre-stop in-flight item is now merged and
  recorded. Remaining active work = the tonight wave only:
  ES, IT, PY, PT-2, CO (+ their joins on PASS).
- 2026-11-09 19:04 — **WAVE: IL-Leumit COMPLETE: G-IL FAIL**
  (merged 0af33b4) — selesai 18:46 WIB, sebelum kickoff 00:00;
  FAIL → tidak ada join/prediksi malam ini. Semua arm gugur di
  dev (X2 kalah kaki RPS sebesar 0,0002 — margin rambut lain
  yang diterapkan mekanis); virgin utuh tak dibaca. Counter:
  26 leagues, 47 passing markets.
- 2026-11-09 18:58 — **🏁 MILESTONE — 25 LEAGUES COMPLETE**
  (milestone #1; next at 50). The 25: J1 (3 PASS/2 FAIL),
  J2 (0/2), J3 (0/1), AT-Bundesliga (0/5), DK-Superligaen
  (2/3), NL-Eredivisie (2/3), AU-ALeague (4/1), US-MLS (3/2),
  BR-SerieA (2/3), AR-LigaProfesional (1/4), PT-LigaPortugal
  (0/5), SCO-Premiership (4/1), CH-SuperLeague (3/2),
  SE-Allsvenskan (3/2), NO-Eliteserien (3/2),
  BE-FirstDivisionA (2/3), ENG-Championship (2/3),
  DE-2Bundesliga (2/3), IN-ISL (2/3), KR-KLeague1 (1/4),
  SA-ProLeague (3/2), BG-SecondLeague (0/1 +4 n/b),
  TR-SuperLig (4/1), GE-Erovnuli (0/1 +4 n/b), MX-LigaMX
  (1/4). **Passing markets: 47.** Goals candidates passed:
  2 of 25 leagues (SCO Gate Zero, TR X3) — the OU-2.5
  calibration/totals leg is the program's binding constraint;
  SOT/corners/total-shots pass far more often. Runner live:
  13 leagues / 34 markets; 5 more leagues' joins frozen in
  queue (ISL, KR, SA, TR, MX).
- 2026-11-09 18:56 — **WIND-DOWN: MX-LigaMX COMPLETE: 1 PASS
  provisional / 4 FAIL** (merged 6197d8d) — C-MX Gate Zero.
  Wind-down builds are now ALL recorded; the only wind-down
  item left is the DE-2 runner join (X8 referee gate).
- 2026-11-09 18:47 — **WAVE: GE-Erovnuli COMPLETE: G-GE FAIL**
  (merged 74299e8) — selesai 18:43 WIB, jauh sebelum kickoff
  23:00-nya; FAIL → tidak ada join/prediksi malam ini. Dev OU
  0,7313 vs base 0,6977 (fit tertinggal lompatan rezim 2023);
  virgin 2025 tetap perawan untuk rancangan masa depan.
  Counter: 24 leagues, 46 passing markets. Colombia Primera B
  launched — the wave's last build.
- 2026-11-09 18:50 — **WIND-DOWN: ENG-Championship JOINED THE
  DAILY RUNNER** (merged 6a09d11) — runner 13 leagues / 34
  markets. Portugal Liga Portugal 2 launched (wave order;
  Colombia Primera B is the wave's last). Wind-down remaining:
  MX build + DE-2 join (with its X8 referee gate).
- 2026-11-09 18:44 — **WIND-DOWN: TR-SuperLig COMPLETE: 4 PASS /
  1 FAIL** (merged 90b8e05) — counter 23 leagues, 46 passing
  markets. **FINAL-AUDIT ITEM #1: the K-TR spoiled virgin
  read** (builder misread the frozen Gate-Zero-fails rule,
  read X8's virgin anyway, self-reported, artifacts removed,
  FAIL applied as written; K-TR virgin burned — any X8 future
  needs a new prereg + the 2026/2027 virgin). Paraguay
  launched (wave order). Still in flight: MX build, ENG-Ch +
  DE-2 joins; wave: GE, IL, ES, IT, PY.
- 2026-11-09 18:38 — **BULGARIA COMPLETE: G-BG2 FAIL (dev OU
  leg) — verdict landed BEFORE tonight's 19:30 WIB kickoff,
  but a FAIL ships nothing: no runner join, no prediction for
  tonight's fixture.** (merged 042fa9d). GZ beat climatology on
  1X2/RPS, lost OU 0,6774 vs 0,6739; virgin unread by the
  frozen rule; S/C/K/T not buildable (stats 0%). Counter: 22
  leagues, 42 passing markets. **Tonight wave RESUMES in
  order** (per the escalation): GE + IL + ES relaunched as
  continuations from their hold checkpoints, IT-SerieC
  launched; PY/PT-2/CO follow as slots free.
- 2026-11-09 18:36 — **WIND-DOWN: SA-ProLeague COMPLETE: 3 PASS
  provisional / 2 FAIL** (merged 18739ae) — counter 21 leagues,
  42 passing markets. SA join frozen in queue. Wave HOLD
  checkpoints all confirmed clean: GE-Erovnuli held at Step 1
  (commit 05d5fc0; goals-only confirmed from every payload —
  events carry no cards either; virgin candidate 2025 n=180),
  IL-Leumit held with Step 1 COMPLETE (64fb9a1; virgin
  candidate 2025/2026 n=296), ES-LaLiga2 held at Step 1
  inspection (ff982c4; key fact: shotmap exists effectively
  only from 2025/2026 → xG arms era-dead there; stats 100%).
  Still in flight: MX + TR builds, ENG-Ch + DE-2 joins, and
  BG-SecondLeague as the wave's sole focus.
- 2026-11-09 18:31 — **ESCALATION (user 18:30 WIB): BULGARIA
  IS THE SOLE FOCUS until it completes.** The three wave
  builders already launched (GE/IL/ES) have been sent HOLD
  instructions (finish the current step, commit, stop, report
  checkpoint); the remaining four (IT/PY/PT-2/CO) are NOT
  launched. Bulgaria's data supports goals only, so its width
  is the single G-BG2 build (already running, first slot) with
  the machine cleared around it; its runner-join brief is
  pre-written (~/workspace/agent-briefs/runner-bg2-join-ready.md)
  and fires the moment a PASS lands. After Bulgaria completes:
  resume the tonight order GE → IL → ES → IT → PY → PT-2 → CO.
- 2026-11-09 19:37 — **EXCEPTION WAVE (user 18:28 WIB) —
  TONIGHT FAST-TRACK, 8 LIGUES, FULL PROCESS.** Bulgaria Second
  Professional League (9096, n=1.735, stats 0% → goals-only;
  kickoff 19:30), Georgia Erovnuli Liga (439, n=1.059, 0% →
  goals-only; 23:00), Israel Leumit League (128, n=1.581, 0% →
  goals-only; 00:00), Spain LaLiga2 (140, n=2.478, stats 100% /
  shotmap 24,7%; 02:30), Italy Serie C (147, n=6.184, stats
  6,2%; 02:30), Paraguay Division Profesional (199, n=1.480,
  stats 34,3%; 03:00), Portugal Liga Portugal 2 (185, n=1.619,
  stats 24,5%; 03:15), Colombia Primera B (9125, n=1.773, 0% →
  goals-only; 03:30). Same 6 steps + prereg + gates, Codex
  luna, ≤6 parallel wave builders; on PASS the league joins
  the daily runner IMMEDIATELY (runner fetches tonight's
  fixtures itself); the ledger records per league whether
  tonight's predictions landed before or after its kickoff.
  Bulgaria's 19:30 kickoff precedes any possible build finish —
  it is built fully anyway and will be recorded as AFTER.
  Everything else stays PAUSED. Launch order = kickoff order,
  first four launched at once, the rest as slots free.
- 2026-11-09 19:24 — **STOP ORDER (user 18:23 WIB) — WIND-DOWN
  STARTED.** No new leagues, no new joins from this point.
  In-flight items (MX-LigaMX, KR-KLeague1, TR-SuperLig,
  SA-ProLeague builds; ENG-Championship + DE-2Bundesliga
  runner joins) run to their next clean checkpoint = branch
  completion, coordinator merge, ledger record. Queued items
  (ISL runner join, DE-3Liga build) are FROZEN, not cancelled.
  When the last in-flight item is recorded, the coordinator
  writes the PAUSED-BY-USER entry with the full resume state;
  resume happens only on the user's word in chat.
- 2026-11-09 19:12 — **IN-ISL COMPLETE: 2 PASS provisional / 3
  FAIL** (merged fe621e5) — counter 19 leagues, 38 passing
  markets. ISL join commissioned (SOT GZ + corners GZ).
  Germany 3. Liga launched (largest remaining pool; no
  shotmap — an honest goals-only/count-stats build).
- 2026-11-09 19:03 — **DE-2Bundesliga COMPLETE: 2 PASS
  provisional / 3 FAIL** (merged eaed158) — counter 18 leagues,
  36 passing markets. K-DE2's X8 is the program's first shipped
  referee arm. DE-2 join commissioned WITH AN OPERATIONAL
  GATE: the runner must prove it can produce X8 cards
  predictions for upcoming fixtures (pre-match referee data) —
  if it cannot, the join stops and reports rather than shipping
  a degraded arm. Saudi Pro League launched.
- 2026-11-09 18:52 — **NO GO-LIVE VERIFIED FROM THE MAIN
  CHECKOUT**: a NO-only pass through the runner's own per-league
  functions (33 upcoming × 3 markets, zero errors) produced
  daily CSVs + ledger BIT-IDENTICAL to the join worktree's
  proof. Note for the final audit: a full 12-league coordinator
  run launched under 6-builder contention was OOM-killed
  (6 GB shared VM) before reaching NO (last in config order) —
  the scheduled solo morning run does not face that contention,
  but runner memory growth as leagues accumulate is worth one
  look in the audit.
- 2026-11-09 18:40 — **NO-Eliteserien JOINED THE DAILY RUNNER**
  (merged 53ebff0) — 12 leagues / 32 markets. Second lost
  handoff caught by the coordinator's branch sweep (the NO
  join had committed its completion at 17:52 WIB); coordinator
  inspected the cards_actual diff directly. Standing lesson
  from PT + NO: the coordinator now sweeps all build/* branch
  tips against HEAD after every completion round. Turkiye
  Süper Lig launched.
- 2026-11-09 18:31 — **PT-LigaPortugal COMPLETE: 0 PASS / 5
  FAIL** (merged 685451f) — **BATCH 1 FULLY DONE (8/8)**.
  Coordinator-side catch-up, recorded honestly: the PT builder
  had in fact committed its completion at 15:45 WIB (b03c337)
  but its completion handoff never reached the coordinator's
  active context (lost across a context compaction), so the
  league sat built-but-unmerged for ~2.5 hours while the
  ledger said BUILDING. The work itself was never at risk
  (committed on its branch); the gap was in coordinator
  bookkeeping, found by a branch-state sweep. Counter: 17
  leagues, 34 passing markets (PT adds none).
- 2026-11-09 18:20 — **BE-FirstDivisionA JOINED THE DAILY
  RUNNER** (merged 88314c7) — 11 leagues / 29 markets.
  South Korea K League 1 launched into the freed slot.
- 2026-11-09 18:10 — **ENG-Championship COMPLETE: 2 PASS
  provisional / 3 FAIL** (merged 2538080) — counter 16 leagues,
  34 passing markets. ENG-Ch join commissioned (SOT RS +
  corners GZ). India ISL launched. For the final audit:
  ENG-Ch's two disclosed deviations (S-X4 virgin not read —
  dev sign-leg used as pre-read filter, inconsistent with T's
  B/C which were read despite failing sign legs; T virgin
  assert n corrected pre-read) — both outcome-neutral, both
  on the record; a one-line convention for future preregs is
  the fix, not new virgin reads.
- 2026-11-09 18:02 — **MERGED-STATE RUNNER VERIFIED END-TO-END**:
  one full run from the main checkout over all 10 active
  leagues — 10/10 summaries, zero errors in any row (J1 240,
  DK 48, NL 198, AU 133, MLS 14, BR 41, AR 8, CH 54, SCO 122,
  SE 16 upcoming). (An earlier duplicate coordinator run was
  SIGTERM'd by the runtime mid-flight — recorded for honesty;
  the completed run above is the go-live evidence.)
- 2026-11-09 17:56 — **SCO + SE JOINED THE DAILY RUNNER**
  (merges 8ef6342, a0c78c4; both needed serialised conflict
  resolution in active.yaml/README — the parallel-join pattern
  now routine). Runner: **10 leagues / 27 markets**, goals
  served for the first time (SCO DC Gate Zero).
- 2026-11-09 17:55 — **TWO BUILDERS INTERRUPTED MID-FLIGHT —
  RECORDED, NOT DROPPED** (continuity rule): ENG-Championship
  builder died after committing steps 1–6 + preregs (bff7782,
  17:31 WIB); DE-2Bundesliga builder died after committing
  steps 1–6 (91b2c04, 17:43 WIB). Both worktrees/branches
  intact. RELAUNCHED as continuations in the same worktrees
  with the frozen preregs/designs binding (ENG-Ch: engines →
  verdicts; DE-2BL: preregs first → verdicts). Mexico Liga MX
  (id 230, n=1,829, 100%/100%) launched into the sixth slot.
- 2026-11-09 17:44 — **BE-FirstDivisionA COMPLETE: 2 PASS / 3
  FAIL** (merged 0f429a5) — S RS provisional, K Gate Zero
  CLEAN. Goals note for the record: G-BE is the program's
  first goals candidate to pass every dev arm and it STILL
  failed the frozen virgin OU calibration (+4.95pp on a
  cooled virgin season). BE join commissioned immediately
  (SOT RS + cards GZ; config read from BE's own frozen preregs
  by the join builder, verified against shipped predictions).
- 2026-11-09 17:39 — **CH-SuperLeague JOINED THE DAILY RUNNER**
  (merged 4b63dea) — the program's first parallel-join merge
  conflict (AR and CH both appended to active.yaml/README from
  different bases) resolved by the coordinator's serialised
  edit with both blocks kept, per the speed-up rule; the
  coordinator's own post-merge full run from the main checkout
  is the go-live evidence (8 leagues served, CH 54 fixtures ×
  3 markets, zero errors). CH's SOT engine was the third found
  missing the runner's ratio_prior kwarg — the join fixed it
  pre-live, as with MLS/BR. England Championship launched.
- 2026-11-09 17:26 — **QUOTA RULE (user 17:12 WIB) ADOPTED,
  superseding the earlier drop-to-3–4 fallback where they
  conflict.** If Codex returns quota / 5-hour-limit errors
  BROADLY (builders can no longer run): stop launching new
  Codex work; write a prominent ledger entry "QUOTA-WAIT until
  <time> WIB" (reset time from the Codex error if given, else
  limit-hit time + 5 hours) and mirror it in the heartbeat;
  coordination then goes quiet and the watchdog relaunches it
  from this ledger after the wait; builders resume at full
  width (6). A SINGLE isolated quota error is not a full stop:
  retry that run once after a short pause. Every quota hit and
  the resume get event-log entries. Status at adoption: no
  quota failure observed yet (Batch 2's Codex incidents were a
  panic and two silent no-output runs — different failure
  modes, builders fell back to direct implementation); no
  QUOTA-WAIT is in effect.
- 2026-11-09 17:23 — **NO RUNNER JOIN STOPPED ON TARGET
  VERIFICATION — the system working as designed.** The join
  builder's crux check found that K-NO's gate graded the
  event-unified columns (yellow_home/away) while the runner's
  settle() reads the stats-feed columns (yellow_cards_home/
  away): for NO they disagree in 171 of 1.407 matches and 42
  matches would settle to the OPPOSITE over/under outcome at
  the 2,5 line. The builder stopped with zero commits rather
  than joining on the wrong target. (AU is the opposite case —
  its stats columns are its target — so the fix is per-league
  configuration, not a global change.) Remedy commissioned:
  a `cards_actual` override in the market config (default =
  current columns, existing leagues bit-identical), NO sets it
  to the event-unified pair, then the join proceeds as briefed.
- 2026-11-09 17:16 — NO-Eliteserien COMPLETED + MERGED
  (1665058): **3 PASS / 2 FAIL — league complete.** Headline:
  K-NO cards passes CLEAN (−0,84pp) on an event-unified target
  adopted through a documented prereg amendment taken BEFORE
  any virgin read, after a per-match audit showed the stats
  feed undercounts yellows in every season (the AR/BR artefact
  in a third league; the single stats-target dev run was
  discarded in full, disclosed in the prereg). X8 was restored
  by the amendment, won dev, and lost the virgin LL leg —
  K-J1's mirror. C-NO and T-NO pass provisional; G-NO failed
  dev (Norway's 60,4% over-rate makes climatology brutal on
  the OU leg; DC still beat it on 1X2); S-NO failed virgin
  calibration by −6,1pp. Norway is the conveyor's
  highest-scoring league (3,12) with its strongest home edge
  (+0,42). Two Codex indentation bugs caught in the builder's
  diff audit (one would have silently dropped a baseline).
  NO join commissioned.
- 2026-11-09 17:09 — SE-Allsvenskan COMPLETED + MERGED
  (149a9d3): **3 PASS / 2 FAIL — league complete.** T-SE arm A
  clean; S-SE ships arm X4 (the xG/shot quality arm's first
  win; its in-league trait was the program's weakest adopted,
  r=0,268 — the gate, not the trait table, decides); C-SE ships
  the X7 configuration whose box-touch beta is again 0 — it
  wins in its no-multiplier form, recorded plainly. G-SE lost
  the dev OU leg by 0,0007 and K-SE its dev gate; both virgins
  unread. Sweden's corners (10,66) are the conveyor's highest.
  SE join commissioned (X4/X7 numeric proofs, AR pattern).
- 2026-11-09 17:04 — **AR-LigaProfesional JOINED THE DAILY
  RUNNER** (merged fe8c6b2) — corners arm `x7` through the AR
  engine's own fit/predict path; 8 Clausura playoff fixtures
  predicted; all proofs float-exact. The join earned its keep
  twice over: it exposed a latent adapter defect (the string
  "nan" from AR's builder leaking into territorial features as
  float NaN — would have silently degraded AR corners daily;
  fixed, proven no-op for the other corners leagues) and a
  prereg-vs-harness inconsistency inside AR's own artifacts
  (halves share 0,480 frozen vs 0,462 hard-coded in
  write_predictions; FT and the verdict unaffected; the runner
  follows the prereg). Runner now serves 7 leagues / 17
  markets. Belgium builder launched into the freed slot.
- 2026-11-09 16:59 — CH-SuperLeague COMPLETED + MERGED
  (538150a): **3 PASS (all provisional) / 2 FAIL — league
  complete.** Switzerland is the program's highest-scoring
  league (goals 3,11, O2.5 59,9%) and its virgin ran hot on
  every count stat — hence provisional, not clean, calibrations
  on all three passes (S-RS by 0,0007 LL; C-GZ on the tie rule;
  T-A after B failed the sign check and C leg (i)). G-CH died
  at dev (OU leg; virgin unread); K-CH failed both virgin legs
  (its team-yellows trait is weak here, r=0,256 — the failure
  is consistent with the EDA). Second Codex incident of Batch
  2: the luna run exited having written NOTHING; the builder
  implemented directly under the fallback rule and caught two
  real defects in verification (J1 halves constants hardcoded
  in the copied DK goals harness — fixed to CH's; stale DK
  virgin artifacts that rode in with the engine seed — removed
  in a dedicated commit BEFORE any CH virgin was read). CH join
  commissioned immediately (adapters all exist).
- 2026-11-09 16:54 — SCO-Premiership COMPLETED + MERGED
  (477dfe7): **4 PASS / 1 FAIL — league complete, and two
  program firsts.** G-SCO is the FIRST goals candidate to pass
  any gate final (provisional: OU calibration breach inside
  1 SE) — Scotland's DC is honest because its trait spread is
  extreme and stable (Old Firm career GD +1,73/+1,21 vs next
  best +0,35; no clamping applied or needed). T-SCO is the
  FIRST arm-B (v2 level layer) win anywhere, and clean
  (calibration −0,03pp). K-SCO failed its dev gate by 0,0002
  LL — reported as FAIL, gate not moved; its virgin stays
  unread. Incident recorded: the Codex luna run for this build
  PANICKED (`failed printing to stderr: Resource temporarily
  unavailable`) and produced zero files; the builder implemented
  directly from the DK ports under the fallback rule and
  verified everything itself — no quota error was involved and
  the 6-builder pace continues. SCO join commissioned: it needs
  the runner's first goals adapter + first arm-B support.
- 2026-11-09 16:44 — **SPEED-UP (user instruction 16:41 WIB)
  APPLIED.** (1) Conveyor waves widened from 3–4 to up to 6
  concurrent builders. (2) Runner joins parallelised: a league
  joins as soon as its own merge lands; only shared-file edits
  serialise if two join builders collide. (3) Gates, preregs and
  virgin rules UNCHANGED — speed comes from parallelism only.
  (4) Quota rule: if Codex returns quota/rate-limit errors, the
  fact is recorded here and the program drops back to 3–4 builders
  automatically without stalling. Immediate effect: Batch 2
  launched (Scotland Premiership, Norway Eliteserien, Switzerland
  Super League, Sweden Allsvenskan) alongside PT + the AR join —
  6 concurrent; Belgium First Division A + England Championship
  queued for the next slots.
- 2026-11-09 16:39 — **US-MLS + BR-SerieA JOINED THE DAILY
  RUNNER** (merged 6f77f20). The off-season assumption was wrong
  in the pleasant direction: FotMob already lists 14 MLS playoff
  fixtures and 41 late-season Brazil fixtures, so all proofs ran
  on real fixtures (MLS 14×3 markets, BR 41×2; recompute exact
  in every market; run 2 fetched 0; all prior leagues
  bit-identical). One real defect caught: the MLS and BR SOT
  engines pre-dated the runner's ratio_prior interface and would
  have thrown TypeError on every SOT prediction — fixed to the
  AU pattern with no-arg behaviour unchanged. Runner now serves
  6 leagues / 16 markets. AR join commissioned (last one).
- 2026-11-09 16:32 — AR-LigaProfesional COMPLETED + MERGED
  (1f29a1e): **1 PASS provisional / 4 FAIL — league complete.**
  Only C-AR ships: the X7-labelled configuration won the virgin
  on LL with provisional calibration — with the verdict stating
  plainly that its box-touch beta is 0 (the F9 replication streak
  continues: J1, DK, NL, BR, AR) and the margin came from Gate
  Zero's big-chance beta hurting on a hot virgin. The other four
  failed honestly: G-AR at dev (all arms lose to climatology),
  S-AR and K-AR on virgin calibration (the virgin block ran hot
  on attacking counts, cold on cards — decayed-level models lost
  to the shift), T-AR beaten outright by naive trailing-10.
  K-AR's X8 had the program's strongest referee trait (r=0,724,
  dev sign 6/6) and still failed the virgin calibration leg.
  Pre-fitting catch: the stats-feed yellow_cards key undercounts
  the event feed in every block — K-AR's target is event-unified
  yellows throughout. Argentina: goals 2,13 (program low),
  yellows 4,89 (program high), draws ≈31%. AR join queued.
- 2026-11-09 16:27 — **AU-ALeague JOINED THE DAILY RUNNER**
  (merged 632f6a0) with all four markets — SOT/RS, corners,
  cards (the runner's first cards adapter; total yellows only,
  no referee component, exactly K-AU's shipped form), total
  shots arm A. The RS ratio prior is now a config value across
  all runner-served SOT engines (default arm behaviour when
  unset). Proofs: 133 fixtures × 4 markets; second run fetched
  0; J1/DK/NL bit-identical; one fixture recomputed exactly in
  all four markets through AU's own engines; the cards settle
  path proven synthetically with hand-checked log-loss, then
  artifacts restored md5-clean. The runner now serves 4 leagues
  / 11 markets daily. Combined MLS+BR join commissioned.
- 2026-11-09 16:20 — BR-SerieA COMPLETED + MERGED (c77116f):
  **2 PASS / 3 FAIL — league complete.** S-BR ships RS with a
  CLEAN calibration (+0,27pp); T-BR ships arm C (third trailing-r
  win; margin over A just 0,00007 LL, calibration provisional).
  C-BR's model lost its virgin to a plain base rate in a cold
  corners season; G-BR and K-BR died at the dev gate (OU leg;
  base-rate leg). Data find of the build: FotMob's stats feed
  undercounts yellows in 2021–22 (3,0/match vs events 4,5–4,9) —
  the unified target (events then, stats from 2023+) follows the
  J1 rule and saved K-BR's dev from mixing two definitions. X6
  dropped honestly: its population era starts IN the virgin
  season, so the arm could never be dev-tested. Brazil is the
  program's lowest-goals (2,45) / highest-cards (4,87) league
  with the strongest home edge (+0,39). BR join queued.
- 2026-11-09 16:15 — US-MLS COMPLETED + MERGED (e026d3a):
  **3 PASS / 2 FAIL — league complete.** T-US arm C passes CLEAN
  (calibration +0,81pp) — the trailing-r mechanism's second
  league win; arm A also passed every leg and C ships on lower
  virgin LL per the frozen rule. S-US and C-US pass provisional
  (Gate Zero both; X7's beta 0 again on the virgin). G-US failed
  the dev gate in a new way: MLS's climatology beat DC even on
  1X2 LL (1,0579 vs 1,0671) — the league's high stable over-rate
  (58,4% dev) makes the baseline brutal. K-US: Gate Zero failed
  dev, X8's pass moot. A Codex-invented cards fallback (event
  yellows where stats yellows were missing) was caught and
  reverted to the frozen target definition — verdict unchanged.
  Expansion handled honestly (San Diego FC enters the virgin
  cold; SHR helped marginally, could not rescue G-US). MLS join
  queued behind AU (config + proof; off-season until Feb 2026).
- 2026-11-09 16:12 — **NL-Eredivisie JOINED THE DAILY RUNNER**
  (merged a7b6de5). Both documented conventions resolved by
  parametrisation (div and 1H/2H ladders now per-market config;
  J1's values became its explicit config, outputs bit-identical).
  One genuine runner-readiness fix in NL's own tree: its data
  builder's hard count assert (== 1,638) became a floor — it
  would have broken the daily rebuild on the next played match.
  Proof: 198 upcoming fixtures predicted in both markets, second
  run fetched 0, all 11 J1/DK files bit-identical across three
  runs, independent recomputes through NL's own engines exact.
  The runner now serves J1 + DK + NL daily. AU join commissioned
  (adds the first cards adapter + RS prior as config).
- 2026-11-09 16:04 — AU-ALeague COMPLETED + MERGED (f838d62):
  **4 PASS / 1 FAIL — the program's strongest league so far.**
  S-AU ships the RS arm (BB prior 20,000; provisional) — X6 had
  the best virgin LL but a 1/3 dev sign check, frozen out as
  written. C-AU is a CLEAN pass with calibration −0,01pp
  (predicted 45,39% vs actual 45,40%). K-AU passes as a
  preregistered Gate-Zero-only candidate: the referee trait that
  was real in J1/DK is pure noise in Australia (split-half
  r=0,06) AND coverage is incomplete — X8 dropped on both legs,
  a program first. T-AU arm A clean; arm C missed leg (i) by
  0,0002 LL. G-AU died on the dev OU leg like G-DK/G-J2. The
  builder also corrected the coordinator's brief on evidence:
  2025/2026 was COMPLETE in the warehouse (not in progress), so
  it served as a full virgin and 2026/2027 is the confirmatory.
  Three Codex defects caught pre-verdict (sign check misused as
  a virgin-eligibility filter; arm C initially unscored on the
  virgin; DK halves constants leaked into AU predictions — all
  repaired and re-verified). AU's runner join needs the first
  cards adapter + the RS prior as config — queued behind NL.
- 2026-11-09 16:00 — **DK-Superligaen JOINED THE DAILY RUNNER.**
  Extension merged (4173106): the runner is now league-generic —
  grep confirms zero league references in code; per-league source
  kind (jleague/world), config-path data builders, per-market arm
  dispatch (incl. the new arm-C trailing-r adapter for DK total
  shots). Bonus fix inside scope: predict_sot's J1-literal arm/
  ladder/share parametrised from market config (J1 proof CSVs
  bit-identical after the change). The coordinator's own post-
  merge run from the main checkout is the go-live evidence: DK
  predicted 48 + 48 (corners + total shots), daily CSVs written,
  DK ledger created, settled 0 (nothing due), errors [] — and J1
  produced its usual 240 × 3 untouched. NL join commissioned on
  the same generic path (config + proof; two documented SOT
  conventions to resolve). Brazil launched — Batch 1 fully in
  flight.
- 2026-11-09 15:53 — NL-Eredivisie COMPLETED + MERGED (75a085e):
  **2 PASS (both provisional) / 3 FAIL — league complete.** S-NL:
  Gate Zero ships — X4/X6 posted the best virgin LLs with clean
  calibration but failed the frozen sign check (1/3), applied as
  written. T-NL: arm A ships; arm B had the best virgin LL AND
  calibration but sign check 1/3 → FAIL, same rule. G-NL failed the
  dev OU leg (its fallback virgin read would also fail). C-NL
  failed the dev gate on a genuine prereg-text discrepancy: the NL
  prereg froze a constant base rate (0,7014) while the ported J1
  harness implements the corners family's NB-scored base rate
  (0,7058 GZ loses to the text constant) — judged against the
  frozen text, fix requires a NEW prereg, recorded in the verdict.
  K-NL: X8 lost the base-rate leg by 0,00004 LL. The G/C/K virgin
  windows are recorded as BURNED (labelled fallback reads in the
  verdicts); 2026/2027 remains the untouched confirmatory window.
  Eredivisie character: goals 3,12, shots 27,4, yellows only 2,94;
  team traits much more reliable than J1 (GF split-half r=0,909).
  NL joins the runner queue behind DK (same world path; builder
  notified to stay league-generic). Argentina launched.
- 2026-11-09 15:44 — DK-Superligaen COMPLETED + MERGED (709d0cf):
  **2 PASS (both provisional) / 3 FAIL — league complete.** C-DK
  corners: Gate Zero ships on the tie rule (virgin arms identical,
  betas 0 again). **T-DK total shots: arm C — the E9 trailing-r
  mechanism — SHIPS**, the program's first variant-arm win (virgin
  LL 0,68630 vs arm A 0,68643; sign check 2/3). G-DK and S-DK failed
  the dev gate and their virgins stay unread; K-DK failed virgin
  leg (i) (naive won) despite the program's first FULL referee
  coverage (100%) making X8 honestly testable — it lost too.
  Recorded degeneracy: G-DK's SHRINK arm is byte-identical to Gate
  Zero under season-blocked fitting (the 1–5-match band never
  occurs) — a biting version needs per-match refit cadence = new
  prereg. DK levels near top-5 (goals 2,90; corners 1H share 0,488
  vs J1 0,447). **Runner join is NOT config-only**: inspection of
  league/runner/run_daily.py shows its fetch layer imports the
  J.League puller and its total-shots adapter implements arm A —
  DK needs a runner extension (world-warehouse fetch path, DK data
  builder hookup, arm-C adapter). Extension builder commissioned;
  DK's activation row above records the pending state honestly.
  A-League builder launched into the freed C1 slot.
- 2026-11-09 15:36 — AT-Bundesliga COMPLETED + MERGED (f59df10):
  **0 PASS / 5 FAIL — league complete.** Rich corpus (xG/splits
  100%, referee 91,8% in the virgin season) and an honest format
  treatment (split rounds + play-offs kept, phase-flagged). G-AT
  and K-AT failed the dev gate — their 2025/2026 virgins stay
  unread for a future prereg. S-AT, C-AT, T-AT all reached the
  virgin and all failed the calibration leg: the 2025/2026 season
  ran cold on every counting stat (SOT 7,93 vs dev 8,58; corners
  9,33 vs 9,81; shots 24,36 vs 24,70) and walk-forward levels
  lagged (+5,3…+7,7pp) — the gate working as designed. Two
  cross-league replications recorded: X7's beta is 0 in every fit
  again (trait r=0,945), and K-AT's referee arm posted the
  program's largest variant dev gain (+0,0093 LL) yet stays
  unshipped because Gate Zero lost its dev gate (frozen rule).
  G-AT note: DC crushed climatology on 1X2 (1,0029 vs 1,0910) but
  the prereg gates on OU 2.5, where it lost — applied as written.
  MLS builder launched into the freed slot (Wave C2 begins).
- 2026-11-09 15:22 — **PHASE FINAL GO-LIVE: J1 JOINED THE DAILY
  RUNNER.** Runner merged (203372c: league/runner/ run_daily.py +
  active.yaml + README, config-driven, per-league and per-market
  failure isolation). Two consecutive proof runs on real data:
  run B fetched 0 new, all three daily prediction CSVs byte-
  identical, ledger stable at 720 entries (240 per market), 0
  settled (day-one expectation; the virgin predictions CSV is an
  evaluation artifact, not part of the daily ledger). One Codex bug
  caught in the builder's review (column `away` vs `away_team`
  would have KeyError'd total_shots every run). Independent
  recompute of a total_shots fixture matched the daily CSV
  bit-for-bit. Cron created: `league-daily-runner`, daily ±07:52
  WIB (flexible slot), own job, separate from the 08:52 top-5
  report; first scheduled run Tue 2026-11-10. Every future PASS
  league joins by adding its block to active.yaml (passing markets
  only).
- 2026-11-09 15:17 — Conveyor Wave C1 LAUNCHED: Austria Bundesliga
  (build/at-bundesliga), Denmark Superligaen (build/dk-superligaen),
  Netherlands Eredivisie (build/nl-eredivisie), Portugal Liga
  Portugal (build/pt-liga) — each steps 1–6 then build, per the
  shared template brief (~/workspace/agent-briefs/
  BRIEF_CONVEYOR_LEAGUE_TEMPLATE.md). Wave C2 (MLS, A-League,
  Argentina, Brazil) launches as C1 slots free.
- 2026-11-09 15:14 — T-J1 COMPLETED + MERGED (ffec3aa): verdict **PASS
  (provisional calibration)** — arm A (the plain v1 pattern) ships.
  All three arms passed dev (LL@24,5: A 0,6548 / B 0,6551 / C 0,6549
  vs baselines 0,6925 / 0,6648); on the virgin, B failed legs (i)
  and (iii), and C — despite the best virgin LL (0,6912) — failed
  the prereg's frozen per-season sign check (1/3), applied as
  written; A's calibration breach (1,30pp) sat inside 1 SE →
  PROVISIONAL PASS. Two Codex defects caught in verification
  (ensemble probability computed as NB-of-mean instead of
  mean-of-NB probabilities; trailing-r window absorbing same-day
  matches) and fixed via a narrow repair run before any verdict.
  **J1 IS NOW FULLY COMPLETE: 3 PASS (SOT, corners, total shots —
  all plain reference arms) + 2 FAIL (goals, cards).** J1 joins the
  daily runner with three markets. Detail:
  league/J1/reports/T_J1_VERDICT.md.
- 2026-11-09 15:10 — C-J1 COMPLETED + MERGED (0ba8ee8): verdict **PASS
  (provisional calibration)** — J1's second passing market. Both arms
  passed dev; on the virgin both arms produced identical predictions
  (every territorial beta fitted to 0 on the full window) at LL@9.5
  0,6901 vs best baseline 0,7050, calibration +2,59pp inside 1 SE →
  PROVISIONAL PASS; the frozen tie rule ships Gate Zero. Recorded
  honestly: the box-touch trait (F9, r=0,857) earned exactly zero
  inside the production multiplier structure at trailing scale —
  a result, not a tuning invitation. J1 joins the daily runner with
  SOT + corners. Detail: league/J1/reports/C_J1_VERDICT.md.
- 2026-11-09 15:08 — **S-J1 COMPLETED + MERGED (cc5f927): verdict PASS
  — the program's FIRST PASS.** Gate Zero (the unmodified v5 pattern)
  passes every leg: dev LL@8.5 0,6658 vs base rate 0,6864 / naive
  0,6714; virgin LL 0,6815, best of all arms and baselines; virgin
  calibration −0,30pp (SE 3,50pp), clean pass. The three variants
  were marginally better on dev and all reversed on the virgin
  (RS neutral — the F6 ratio-trait noise verdict confirmed in
  market; X4/X6 over-predicted 2026). Verification was strong: an
  independent recompute through the production model_sot.py code
  path matched all 200 virgin matches to 7e-15; a silent Codex key
  bug that had neutered X4/X6 in run 1 was caught in verification
  and fixed via a narrow re-brief. **Phase Final TRIGGERED**: J1
  joins the daily runner with SOT (Gate Zero) as its only passing
  market; runner builder launched (build/daily-runner). Detail:
  league/J1/reports/S_J1_VERDICT.md.
- 2026-11-09 15:05 — K-J1 COMPLETED + MERGED (4b840d1): verdict **FAIL**
  — the closest candidate so far. Both arms passed the dev gate and
  X8 (referee) genuinely helped there (LL@2.5 0,6785 vs Gate Zero
  0,6872; sign check 3/4). On the virgin both arms took PROVISIONAL
  PASS on calibration (+2,0pp, SE 3,5pp) but failed LL leg (i):
  naive trailing-10 was the best virgin performer (0,6807 vs GZ
  0,6829 / X8 0,6831). Referee coverage overall 51,6% (dev 54,6%)
  but **0,5% in the virgin season (1/200)** — the X8 arm was
  effectively untested on the window that decides. Operational
  check concluded honestly: warehouse records are post-match
  snapshots; pre-match referee publication cannot be proven from
  them; the no-imputation fallback is the operating rule. Detail:
  league/J1/reports/K_J1_VERDICT.md.
- 2026-11-09 15:05 — T-J1 LAUNCHED (Wave 2b, slot freed by K-J2):
  builder on build/t-j1 @ wt-t-j1; three frozen arms (v1 / v2 level
  layer / E9 trailing-r), prereg must open with the ahead-of-verdict
  provenance (user order, §6).
- 2026-11-09 15:03 — K-J2 COMPLETED + MERGED (d1104ad): verdict **FAIL**
  at the dev gate — Gate Zero LL@2.5 0,6564 beats the base rate
  (0,6668) but loses to naive trailing-10 (0,6554); the 2023 yellow
  level jump (mean 2,06→2,66) is the diagnosis (trailing-10 adapts in
  weeks, HL-270 ratings carry the old regime for months). Referee
  coverage for J2 is **0/2.318** — the F8 referee trait was only ever
  measurable in J1; X8 reported honestly as a Gate Zero clone
  (fallback 1.764/1.764), never imputed. Virgin 2025 NOT read. Two
  Codex bugs caught in verification (unbounded naive deque; season
  label constant) and fixed before the verdict; engine replayed exact
  against production CardsState. **J2 league is now fully complete**
  (both candidates through their gates, both FAIL). Detail:
  league/J2/reports/K_J2_VERDICT.md.
- 2026-11-09 14:54 — WAVE 1 CLOSED: 0/3 PASS. G-J1 COMPLETED + MERGED
  (562baeb): verdict **FAIL** — Gate Zero passed dev and the virgin LL
  leg (1,0748 < klimatologi 1,0915) but failed virgin OU2.5
  calibration (−4,56pp; breach 3,5636pp vs 1 SE 3,5589pp — the prereg
  rule is mechanical and was applied as written); X2 died on dev
  (frozen F4 offset punished promoted Machida Zelvia, a top finisher)
  and X3 with it. WAVE 2 LAUNCHED: C-J1, K-J1, K-J2, S-J1 builders;
  T-J1 queued as Wave 2b. Phase Final still untriggered (no PASS).
- 2026-11-09 14:52 — Phase Final UPGRADED to a build item (user 14:50):
  the daily league runner is built as soon as the first candidate
  records a PASS — per-league activation, own daily cron at first
  go-live, morning report untouched. Not yet triggered (no PASS yet).
- 2026-11-09 14:51 — G-J2 COMPLETED + MERGED (b8ec72c): verdict **FAIL**
  at the dev gate (both arms; OU2.5 LL 0,746 vs base rate 0,690 while
  1X2 LL/RPS legs passed). Virgin 2025 deliberately NOT read — the
  window stays virgin. Builder caught and fixed 2 Codex bugs during
  verification (RPS accumulation; virgin-training structure) and
  reproduced the failure with the production DC class itself, so the
  failure belongs to the reference pattern in J2 (extreme lambdas for
  thin-data teams in season openers), not to the copy. Detail:
  league/J2/reports/G_J2_VERDICT.md.
- 2026-11-09 14:49 — G-J3 COMPLETED + MERGED (16b40ab): verdict **FAIL**,
  nothing ships. Prereg aeb720a preceded all fitting; builder's
  independent rerun reproduced Codex's results byte-for-byte, virgin
  isolation verified. Detail: league/J3/reports/G_J3_VERDICT.md.
- 2026-11-09 14:46 — Phase Final (Daily League Pipeline) registered as
  a design note (user decision): FotMob-only daily fixtures/results,
  incremental pulls, CSV append, engine refit, predictions to
  league/<L>/predictions/, daily settlement into per-league grading
  ledgers; activates per league on its first PASS; NOT built in this
  program; morning report untouched by it.

## FINAL AUDIT — started 2026-11-11 01:35 WIB (user order 01:34)

- AUDIT-START: the final Codex-sol audit pass (league/AUDIT_BRIEF.md)
  is RUNNING, launched on the user's direct order ahead of the last
  two joins (SK-1Liga in wt-runner50; US-USLLeagueOne wt-runner47) —
  the audit does not touch wt-runner* worktrees or league/runner/.
  Audited state at start: 156 leagues complete, 122 passing markets,
  runner 47 leagues / 100 markets (per heartbeat 00:51).
- Method: mechanical skeleton extraction of all 157 league config
  dirs x 5 markets, then Codex gpt-6.1-sol batches (one session at a
  time) classifying every candidate from verdict + prereg + design
  files into a fixed schema; deterministic grep sweep for known bug
  patterns across engines; clear-bug fixes confined to
  league/<L>/engine/, each with a recorded re-test. Gates are NOT
  moved; no failed market is re-passed. Deliverable: league/AUDIT.md,
  committed in batches.
- AUDIT HEARTBEAT: 2026-11-11 01:35 WIB — audit started; skeleton
  extraction in progress.
- AUDIT PROGRESS 2026-11-11 ~02:05 WIB: classification batches 01–02
  complete (130/785 candidates, schema-validated); batch 03 running.
  Fix batches committed: ca1da555 (halves constants batch 1 + CL
  READMEs + CY comment), 80c06162 (halves batch 2 — 27 files, incl.
  SCO/TR shipped CSVs proven to carry J1's 0.412 split vs frozen
  0.4405/0.4403), b7881d90 (gate-arithmetic tokens vs prereg, all
  verified outcome-neutral). Systemic latent class recorded in
  AUDIT.md §5.7 (unguarded sealed-read CLI paths; procedural guard
  held in every verdict). AUDIT HEARTBEAT: 2026-11-11 02:45 WIB.
- AUDIT PROGRESS 2026-11-11 ~02:25 WIB: batches 01–04 classified
  (260/785). Fix batch 4 committed (62800ae2): T-family level prior
  M_BAR = J1's 24.9 found in ~45 engines; fixed where the league's
  own documents state its dev mean (CH/CN/CL/CY). CN-SuperLeague
  ships arm B — its ship-selection over arm A (margin 0.0010 LL)
  ran under the wrong prior and the daily runner imports the
  engine live, so CN daily T used the wrong prior until the fix;
  pass itself unaffected (both arms eligible). CY T eligibility
  helper at wrong line 17.5 verified outcome-neutral, fixed.
- AUDIT PROGRESS 2026-11-11 ~02:45 WIB: batches 01–06 classified
  (390/785). More fixes: FI SOT sealed baselines were scored on the
  wrong window (fixed 2768ed6d, verdict FAIL unaffected), GR T
  calibration sign (fixed), HR goals FI halves literals (fixed
  b1942096). HU-NBI T "naive" baseline is arm B in code — verified
  non-decisive (all arms lose to the true base rate too). AUDIT.md
  §5.12 records batches 04–06 adjudications.
- AUDIT QUOTA-WAIT 2026-11-11 ~02:47 WIB: Codex usage limit hit
  during batch 10 launch (error: "You've hit your usage limit...
  try again at 9:06 PM" UTC = 04:06 WIB). Classification stands at
  585/785 (batches 01–09, all schema-valid). Batches 10–12 queued
  to auto-run sequentially after 04:08 WIB; synthesis follows.
  AUDIT HEARTBEAT: 2026-11-11 02:47 WIB (QUOTA-WAIT until 04:06 WIB).
- FINAL AUDIT COMPLETE 2026-11-11 ~05:20 WIB — league/AUDIT.md.
  785 candidates classified (12 Codex-sol batches, schema-validated;
  rows in league/audit_scratch/class_batch*.jsonl): PASS 122
  (94 provisional / 28 clean — reconciles with the ledger), FAIL 309
  (dev 210, sealed 99), NOT_BUILDABLE 353, NOT_BUILT 1.
  Root causes ranked: (1) data absence 353 (stats feed absent/null
  248, window 63, scores-only 38; all NB verdicts verified to rest
  on payload counts, not the defective has_stats flag); (2) no edge
  over baselines at dev 210 (goals 135 of them — goals pass rate
  3% vs corners 58% of built); (3) era drift at the sealed window
  99 (45% of dev-passers; calibration legs 70; median breach
  1.57 SE); (4) variants-moot architecture 10 (8 cards/referee-arm);
  (5) data-depth gradient: stats seasons >=4 -> 35% pass, <=3 -> 1%.
  EDA self-audit (99 sealed fails): missed 53, mixed 37,
  could-not-see 9 — the user's hypothesis confirmed; EDA inspected
  all seasons, so sealed levels were visible in design workbooks
  (not design-sealed). Bugs: 12 fix commits, 59 engine files —
  halves-split constants (2 shipped goals markets' CSVs carried
  J1's 0.412), T-family M_BAR=24.9 template prior (CN ships arm B;
  runner imports engine live, fixed), CY/KR wrong-line gate
  helpers (verified outcome-neutral), FI/SE-Superettan cross-window
  baselines, gate-arithmetic tokens (AR/AT/J1/MX/NL/NO). One
  realised isolation breach found: K-TR erroneous sealed read,
  caught by the program itself, artefacts removed, candidate
  spoiled. No gate moved, no verdict changed, nothing re-passed.
  Proposals P1–P6 in AUDIT.md §6 (inputs, not decisions).
  AUDIT HEARTBEAT: 2026-11-11 05:20 WIB — AUDIT DONE.
- WATCHDOG 2026-11-11 05:20 WIB — heartbeat line read 04:17 (58 min old)
  but the program is LIVE, not stalled: DK-1Division join proof
  completed 05:11 (4 markets × 48 fixtures, 0 errors, wt-runner53);
  AU-ALeagueWomen join proof running since 04:49 (wt-runner54,
  run_daily.py PID 11814, mid-run 05:18, active.yaml block added).
  No duplicate builders launched; no resume needed. Ledger heartbeat
  refreshed to 05:20 so the next tick does not misread staleness.
  Next: coordinator merges DK-1Division join after verification,
  then the join queue; improvement program Gate Zero phase starts
  now that the audit is closed.
- WATCHDOG 2026-11-11 07:16 WIB — heartbeat line read 06:28 (48 min old)
  but the program is LIVE, not stalled: IS-BestaDeildin join proof run 1
  RUNNING in wt-runner55 (run_daily.py PID 25867, CPU-active — CPU time
  19:15→19:36 across the check; run_log.jsonl entries to 07:16,
  SE-Superettan cards predict/settle, 0 errors, 331 entries). No
  duplicate builders launched; no resume needed. No Codex processes
  running (proof run is the venv runner, not Codex). No QUOTA-WAIT, no
  PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues
  away). Heartbeat NOT refreshed (no resume; heartbeat edits reserved
  for resume).
- WATCHDOG 2026-11-11 07:46 WIB — heartbeat line read 06:28 (78 min old)
  but the program is LIVE, not stalled: IS-BestaDeildin join proof run 1
  finished since the 07:16 check and run 2 is RUNNING in wt-runner55
  (run_daily.py PID 29386, started 07:19 WIB, CPU-active — CPU time
  19:24→19:43 across the check; run_log.jsonl entries to 07:45,
  SK-1Liga SOT 48 predicted, 0 errors). No duplicate builders launched;
  no resume needed. No Codex processes running (proof run is the venv
  runner, not Codex). No QUOTA-WAIT, no PAUSED-BY-USER. Counter still
  156; next milestone 175 (19 leagues away). Heartbeat NOT refreshed
  (no resume; heartbeat edits reserved for resume).
- WATCHDOG 2026-11-11 08:15 WIB — heartbeat line read 07:52 (23 min old,
  fresh). Program LIVE: SA-FirstDivision SOT join proof run 1 RUNNING
  in wt-runner56 (run_daily.py PID 35104, started 08:08 WIB, CPU-active,
  3:15 CPU time); daily runner run_daily.py PID 33266 also running
  (started 07:52 WIB). No duplicate builders launched; no resume needed.
  No Codex processes running (proof run is the venv runner, not Codex).
  No QUOTA-WAIT (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE
  05:20), no PAUSED-BY-USER. Counter still 156; next milestone 175
  (19 leagues away). Heartbeat NOT refreshed (no resume; heartbeat
  edits reserved for resume).
- WATCHDOG 2026-11-11 08:48 WIB — heartbeat line read 07:52 (56 min old)
  but the program is LIVE, not stalled: SA-FirstDivision SOT join proof
  run 2 RUNNING in wt-runner56 (run_daily.py PID 1813, wrapper PID 1811,
  started 08:47 WIB, CPU-active — log entries to 08:48, J1 SOT 240
  predicted, 0 errors; output ~/workspace/safd_proof/run2.log). Run 1
  exited (PID 35104 gone; run-1 outputs hashed, 276 files) with one
  defect: SA-FirstDivision predicted 0 — AttributeError("module
  'daily_SA-FirstDivision_builder' has no attribute 'main'") at 08:41;
  build_data.py was fixed in the worktree at 08:43 (now defines main();
  uncommitted) and run 2 relaunched 08:47 after the fix — an earlier
  08:43 attempt (PID 38916) is no longer running. SA-FD not yet reached
  in run 2 at check time; verify it predicts on this run before merge.
  No duplicate builders launched; no resume needed. No Codex processes
  running (proof runs are the venv runner, not Codex). No QUOTA-WAIT
  (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE 05:20), no
  PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues
  away). Heartbeat NOT refreshed (no resume; heartbeat edits reserved
  for resume).
- WATCHDOG 2026-11-11 09:15 WIB — heartbeat line read 07:52 (83 min old)
  but the program is LIVE, not stalled: SA-FirstDivision SOT join proof
  run 2 RUNNING in wt-runner56 (run_daily.py PID 1813, started 08:47 WIB,
  CPU-active — 20:30 CPU time, elapsed 27:52; run_log.jsonl entries to
  09:15, currently on IS-BestaDeildin, 0 errors; SA-FirstDivision not yet
  reached in run 2 — it follows IS in league order; run-1 defect
  AttributeError fixed in-worktree 08:43, verify SA-FD predicts on this
  run before merge). No duplicate builders launched; no resume needed.
  No Codex processes running (proof run is the venv runner, not Codex).
  No QUOTA-WAIT (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE
  05:20), no PAUSED-BY-USER. Counter still 156; next milestone 175
  (19 leagues away). Heartbeat NOT refreshed (no resume; heartbeat edits
  reserved for resume).
- WATCHDOG 2026-11-11 09:46 WIB — heartbeat line read 07:52 (114 min old)
  but the program is LIVE, not stalled: SA-FirstDivision SOT join proof
  run 2 FINISHED 09:45:00 WIB (rows 822–1216 of
  wt-runner56/league/runner/run_log.jsonl, 395 rows, 0 errors; SA-FD
  summary is the final row — run-1 defect AttributeError FIXED and
  verified: SA-FD predict step SOT 68 predicted, 0 errors, 68 upcoming
  fixtures). No run_daily process running at check time because the run
  had just ended; coordinator still active — a delayed verification
  command is queued (PID 7305, sleep 600 then reads run-3 rows 822+).
  No duplicate builders launched; no resume needed. No Codex processes
  running (proof runs are the venv runner, not Codex). No QUOTA-WAIT
  (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE 05:20), no
  PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues
  away). Heartbeat NOT refreshed (no resume; heartbeat edits reserved
  for resume).
- WATCHDOG 2026-11-11 10:15 WIB — heartbeat line read 09:49 (26 min old,
  fresh). Program LIVE: daily runner run_daily.py PID 10195 CPU-active
  (12:09 CPU time); wt-runner57 present (LV-Virsliga SOT join worktree,
  launching next per heartbeat). No duplicate builders launched; no
  resume needed. No Codex processes running (proof/runner work is the
  venv runner, not Codex). No QUOTA-WAIT (audit QUOTA-WAIT until 04:06
  expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156;
  next milestone 175 (19 leagues away). Heartbeat NOT refreshed (no
  resume; heartbeat edits reserved for resume).
- WATCHDOG 2026-11-11 10:45 WIB — heartbeat line read 09:49 (56 min old)
  but the program is LIVE, not stalled: LV-Virsliga SOT join proof run
  RUNNING in wt-runner57 (run_daily.py PID 14455, started 10:37 WIB,
  CPU 75.6%, 5:56 CPU time; run_log.jsonl entries to 10:44:32 WIB,
  ENG-Championship SOT 372 predicted, 0 errors). No duplicate builders
  launched; no resume needed. No Codex processes running (proof runs are
  the venv runner, not Codex). No QUOTA-WAIT (audit QUOTA-WAIT until
  04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter still
  156; next milestone 175 (19 leagues away). Heartbeat NOT refreshed (no
  resume; heartbeat edits reserved for resume).
- WATCHDOG 2026-11-11 11:15 WIB — heartbeat line read 09:49 (86 min old)
  but the program is LIVE, not stalled: LV-Virsliga SOT join proof run
  RUNNING in wt-runner57 (run_daily.py PID 1891, started 10:49 WIB, CPU
  77%, 19:33 CPU time; run_log.jsonl entries to 11:15:21 WIB,
  AE-ProLeague pull_fixtures, 70 upcoming, 0 errors). No duplicate
  builders launched; no resume needed. No Codex processes running (proof
  runs are the venv runner, not Codex). No QUOTA-WAIT (audit QUOTA-WAIT
  until 04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter
  still 156; next milestone 175 (19 leagues away). Heartbeat NOT
  refreshed (no resume; heartbeat edits reserved for resume).
- WATCHDOG 2026-11-11 12:15 WIB — heartbeat line read 11:24 (51 min old)
  but the program is LIVE, not stalled: AR-PrimeraBNacional cards X8
  join proof run 1 RUNNING in wt-runner58 (branch
  build/runner-ar-primerab; run_daily.py PID 9153, started 11:47 WIB,
  CPU-active — 20:09 CPU time; run_log.jsonl 360 rows, entries to
  12:15:35 WIB, last league HR-HNL, 0 rows with non-empty errors; the
  new AR cards market not yet reached in run order). No duplicate
  builders launched; no resume needed. No Codex processes running (proof
  run is the venv runner, not Codex). No QUOTA-WAIT (audit QUOTA-WAIT
  until 04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter
  still 156; next milestone 175 (19 leagues away). Heartbeat NOT
  refreshed (no resume; heartbeat edits reserved for resume).
- WATCHDOG 2026-11-11 12:45 WIB — heartbeat line read 11:24 (81 min old)
  but the program is LIVE, not stalled: AR-PrimeraBNacional cards X8
  join proof run 2 RUNNING in wt-runner58 (branch
  build/runner-ar-primerab; run_daily.py PID 12982, started 12:17 WIB,
  CPU 75,3%, 20:48 CPU time; run_log.jsonl 806 rows, ALL with empty
  errors; at check time the run had just reached the new market —
  AR-PrimeraBNacional predict cards: 9 predicted, 0 errors, 9 upcoming
  fixtures; run 1 finished between 12:15 and 12:17 and run 2 launched
  as the verification rerun). No duplicate builders launched; no resume
  needed. No Codex processes running (proof run is the venv runner, not
  Codex). No QUOTA-WAIT (audit QUOTA-WAIT until 04:06 expired; audit
  COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156; next milestone
  175 (19 leagues away). Heartbeat NOT refreshed (no resume; heartbeat
  edits reserved for resume).
- WATCHDOG 2026-11-11 13:15 WIB — heartbeat line read 11:24 (111 min old)
  but the program is LIVE, not stalled: AR-PrimeraBNacional cards X8
  join proof run 2 FINISHED 12:45:32 WIB (run_log.jsonl 810 rows, ALL
  with empty errors; AR cards predict 9/9, summary row present) and the
  join branch is COMMITTED (4450088d, 12:47:43 WIB, build/runner-ar-
  primerab — 2 proof runs, 57 leagues/117 markets, 13,031 predictions
  each, 0 errors, fetched_new=0 in run 2). Merge into main is the
  pending coordinator step; no run_daily/Codex process running at check
  time because the proof runs have ended, not because work died. No
  duplicate builders launched; no resume needed. No Codex processes
  running. No QUOTA-WAIT (audit QUOTA-WAIT until 04:06 expired; audit
  COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156; next milestone
  175 (19 leagues away). Heartbeat NOT refreshed (no resume; heartbeat
  edits reserved for resume).
- 2026-11-11 13:47 — **AR-PrimeraBNacional JOINED runner (57/117)** — merge e8f7c2d9 (branch build/runner-ar-primerab 4450088d; base b3e983df predated the three watchdog ledger commits, so the merge took HEAD's PROGRAM_STATUS.md with no conflict; active.yaml/README/run_daily.py merged cleanly). Market: cards X8 **PROVISIONAL PASS** (dev pooled n=1,334 GZ LL@4.5 0.680252, X8 0.659605; virgin 2026 n=648 X8 LL@4.5 0.669291 vs GZ 0.676939 / base 0.692222 / naive 0.687911; cal −1.0611pp, SE 1.9191pp — breach 0.0611pp ≤ 1 SE → PROVISIONAL; both-pass rule ships lowest virgin LL, X8). Goals FAIL dev, excluded. First X8 join: `predict_cards` in run_daily.py gained the opt-in X8 path (arm accepted; history-row construction extracted to `_cards_history_rows` with team-column alias + referee/`key` attached ONLY for x8; referee fetched per upcoming fixture from FotMob matchDetails, failed fetch falls back to no referee and never fails the run; engine without `estimate_r` supplies frozen dispersion as module-level `R` (112.39 here) with two-argument `nb_over`; x8 output rows carry referee/n_prior/multiplier/fallback/fallback_reason). One defect caught by the inertness probe pre-proof: unconditional referee attachment activated dormant referee branches in gate_zero engines (KR-KLeague1 `update()` then requires `row["kickoff_utc"]`) — fixed by attaching referee only for x8; inertness proven on KR-KLeague1 cards byte-identical. Operational gate passed the day of the join: 9 upcoming fixtures (2026 Reducido playoffs, 2026-11-14/15), 1/9 carries a referee in matchDetails (6575527 Godoy Cruz–Tristán Suárez, Maximiliano Ramírez) with zero in-league priors, so all 9 production predictions are Gate-Zero-equivalent (multiplier 1.0). Proof: 2 full end-to-end runs (57 leagues, 117 markets, 13,031 predictions each, 0 errors, fetched_new=0 in run 2; 288 files bit-identical between runs). Coordinator merged-state verification from main (one-league run, /tmp/verify_ar_join.py): rebuild 3,874 rows, 9 predicted, 0 settled, 0 errors; first fixture 6546950 exp_total 4.5341 / P(over 4.5) 0.4724, range 3.8819–5.6716 — all 4 AR output files byte-identical to the branch proof outputs; referee Maximiliano Ramírez on 6575527, multiplier 1.0, fallback True, as recorded. Join lane now 1/2; KZ-PremierLeague goals GZ join launching next.
- WATCHDOG 2026-11-11 13:44 WIB — heartbeat line read 11:24 (140 min old) and the pending coordinator step from the 13:15 check (merge build/runner-ar-primerab) still unmerged, no run_daily/Codex process running: RESUMED per the watchdog rule. Merged the AR join (e8f7c2d9), verified it in merged state (above), refreshed the heartbeat to 13:49, and launched the KZ-PremierLeague goals GZ join builder (branch build/runner-kz, worktree wt-runner59) — the next item in the join queue. BA-PremierLeague goals GZ remains queued after KZ. No QUOTA-WAIT (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues away). No Codex processes were running at check time; the KZ builder drives Codex luna itself.
- WATCHDOG 2026-11-11 14:48 WIB — heartbeat line read 13:49 (59 min old): RESUMED per the watchdog rule. The KZ-PremierLeague goals GZ join builder launched 13:49 was interrupted twice by timeout/runtime restart; its final report (agent 4dab2151) confirms proof run 2 did NOT complete — killed 14:46 WIB at 225/410 rows (EG-PremierLeague data_refresh; run2.log empty, no run_daily/Codex process alive). No QUOTA-WAIT in effect (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues away). Preserved work verified on disk: wt-runner59 has the 2 intended modifications uncommitted (active.yaml +20, run_daily.py +12/-1), proof run 1 snapshot in ~/workspace/kz-proof/run1, run_log.jsonl 635 rows. Relaunching proof run 2 from scratch via a resume builder on the same branch/worktree (idempotent runner; analyse the relaunched run's rows from line 635, not 410); then snapshot comparison, synthetic settlement, README paragraph, commit, and merge verification. BA-PremierLeague goals GZ remains queued after KZ.
- 2026-11-11 15:26 — **KZ-PremierLeague JOINED runner (58/118)** — merge efb502eb (branch build/runner-kz b0336713; base fc3036e5; active.yaml/README/run_daily.py merged cleanly, no conflict). Market: goals Gate Zero **PROVISIONAL PASS** (virgin 2026 complete season n=240, 1X2 LL 1.0152 vs climatology 1.0678; calibration home-win −1.26pp SE 3.09pp and OU2.5 −3.21pp SE 3.21pp, both breaches within 1 SE → PROVISIONAL; dev pooled 1X2 LL 1.0290 < climatology 1.0712, RPS 0.2135 < 0.2285, OU2.5 LL 0.6819 < base rate 0.6929; SHRINK identical to Gate Zero everywhere measured, so the both-pass rule ships the simpler arm). SOT, corners, cards, total shots NOT BUILDABLE, excluded (scores-only league). Third goals join and the first to need the signature-dispatched adapter: `predict_goals` now calls `adjusted_lambdas` with exactly the signature each engine ships — engines taking (model, home, away, arm, counts) are called 5-arg, all other engines take the existing path unchanged; KZ engine untouched. Trap proven real: HEAD raises TypeError on KZ in both call forms; amended code predicts. Inertness proven on SCO-PremierLeague + TR-SuperLig goals (HEAD vs amended on 8 fixed fixtures each, byte-identical, max |d| 0.0). Replay: harness-style causal walk reproduces the shipped virgin CSV exactly (max |Δlam| 0.0, max |Δp| 0.0, LL 1.015226 = verdict 1.0152); live-adapter walk LL 1.000751, decomposed as refit-anchor 0.009951 + within-virgin-update 1.741266 on lam, future leakage 0 by construction. FotMob probe the day of the join: 2027 season unpublished (selectedSeason='2026', 0 upcoming), so the join predicts nothing live until FotMob publishes 2027. Proof: 2 full end-to-end runs (58 leagues, 118 markets, 13,031 predictions each, 0 errors, fetched_new=0 in run 2; 410 log rows each). Run 2's first attempt was killed mid-run by a runtime restart at 14:46 WIB (225/410 rows, last write EG-PremierLeague data_refresh) and was relaunched from scratch by the watchdog's resume builder — the partial run is not a proof and was not compared. 291/292 snapshot files bit-identical between the runs; the one exception is HR-HNL's daily corners CSV, where FotMob moved 12 fixture dates between the runs (upstream listing change, same 116 match_ids/teams, max float difference 1.1e-14). Synthetic settlement on finished match 5204163 (2026-07-05, Atyrau–Kaspiy Aktau 1–2, actual total 3): live adapter exp_total 1.6096, p_over_2.5 0.2191, chosen under, missed, log loss 1.5181; settled exactly once (second pass 0); all four touched files restored byte-identical (md5-verified). Coordinator merged-state verification from main (/tmp/verify_kz_join.py): rebuild 1,124 rows, 0 upcoming, 0 predicted, 0 settled, 0 errors; all 4 KZ output files byte-identical to the branch proof run-2 snapshot. Join lane now 1/2; BA-PremierLeague goals GZ launching next.
- WATCHDOG 2026-11-11 15:26 WIB — resume from the 14:48 check COMPLETE: KZ-PremierLeague goals GZ join merged (efb502eb) and verified in merged state (above); heartbeat refreshed to 15:26. BA-PremierLeague goals GZ join builder launching now (branch build/runner-ba) — the last item in the join queue; after BA the join lane is empty and remaining work is the improvement program Gate Zero phase. No QUOTA-WAIT, no PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues away).
- WATCHDOG 2026-11-11 16:15 WIB — heartbeat line read 15:26 (49 min old): RESUMED per the watchdog rule. The BA-PremierLeague goals GZ join builder launched 15:26 (agent 619e22b8) was cancelled ~15:50 WIB mid-proof-run-1 — no result of its own; its proof run 1 was killed at MX-LigaMX pull_fixtures (run_log.jsonl 138 rows, last write 15:50:20 WIB; run1.log empty; no run_daily/Codex process alive; BA-PremierLeague 0 rows — not yet reached). No QUOTA-WAIT in effect (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues away). Preserved work verified on disk: wt-runner60 (branch build/runner-ba, base 33b84154) has the 2 intended modifications uncommitted (active.yaml +20 BA block; run_daily.py +26/-6 — .get() xG reads for the scores-only league + exclude_awarded opt-in, 4 awarded matches excluded per the frozen prereg). Relaunching proof run 1 from scratch via a resume builder on the same branch/worktree (idempotent runner; the partial 138-row run is not a proof); then snapshot comparison, synthetic settlement, README paragraph, commit, and merge verification. BA is the LAST item in the join queue; after BA the join lane is empty and remaining work is the improvement program Gate Zero phase.
- WATCHDOG 2026-11-11 17:21 WIB — heartbeat line read 16:15 (65 min old): RESUMED per the watchdog rule. The 16:15 resume builder (agent c6b5e293) was cancelled 17:17:50 WIB — 9 seconds after its proof run 1 COMPLETED 17:17:41 WIB. Proof run 1 verified by the coordinator in worktree state: run_log.jsonl 415 rows, 0 errors, BA-PremierLeague goals 115 predictions / 0 settled / fetched_new 0, daily CSV 115 rows (from 2026-11-21), ba_matches.csv 1036 rows (4 awarded excluded per the frozen prereg). Preserved on disk: wt-runner60 (branch build/runner-ba, base 33b84154) still holds the 2 intended modifications uncommitted (active.yaml +20 BA block; run_daily.py +26/-6 — .get() xG reads for the scores-only league + exclude_awarded opt-in). No QUOTA-WAIT in effect (audit QUOTA-WAIT until 04:06 expired; audit COMPLETE 05:20), no PAUSED-BY-USER. Counter still 156; next milestone 175 (19 leagues away). Relaunching a resume builder on the same branch/worktree to continue from proof run 1 COMPLETE (proof run 2 + snapshot comparison + synthetic settlement + README + commit); coordinator verifies + merges. BA is the LAST item in the join queue; after BA the join lane is empty and remaining work is the improvement program Gate Zero phase.
- WATCHDOG 2026-11-11 18:21 WIB — heartbeat line read 17:21 (60 min old). BA join found already MERGED 17:55 (ad5cc1fd, merge of e2143005) but unrecorded in the ledger — the merge commit’s tree carries the builder’s 3 files only; the builder wrote no ledger update. Verified in merged state: active.yaml parses (59 leagues / 119 markets), run_daily.py compiles, merge diff exactly the builder’s change; proof runs on disk (~/workspace/ba-proof/run1.log + run2.log, 13,146 predictions each, 0 errors; snapshot 295/296, ZA-PSL rename only; synthetic settlement verified). Ledger updated: BA JOINED in the Phase Final table, heartbeat refreshed to 18:21, runner 59/119. No QUOTA-WAIT, no PAUSED-BY-USER. Counter still 156; the 175 milestone is moot (program total is 156). ALL LEAGUES COMPLETE — build program done; remaining work is the improvement program Gate Zero phase. Watchdog may be deleted by the user per the ALL-DONE rule.
