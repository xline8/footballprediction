# Lane 1 Inventory — Unread Sealed Windows

Generated 2026-11-11 from `league/audit_scratch/class_batch*.jsonl` (final audit §1).
Scope: every candidate with outcome FAIL at the DEV gate — its sealed (virgin)
window was never read (gate order was dev first; dev fail = no sealed read).
Each candidate re-enters only as a NEW candidate under a fresh preregistration
committed BEFORE its window is read (charter, Lane 1). One read, verdict final.

**Total: 210 candidates.** Goals 135 · SOT 13 · Cards 49 · Corners 7 · Total shots 6

## Goals (135)

| League | Candidate | Sealed window (from prereg) | Virgin n | Dev n | Failed dev legs | Mechanisms |
|---|---|---|---|---|---|---|
| AE-ProLeague | G-AE | 2025/2026 | 182 | 545 | OU_LL | level_misspec,baseline_too_strong |
| AL-KategoriaSuperiore | G-AL | ? | 55 | 720 | 1X2_LL,RPS,OU_LL | feature_failure,baseline_too_strong |
| AM-PremierLeague | G-AM | ? | 77 | 653 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| AR-LigaProfesional | G-AR | ? | 240 | 1854 | 1X2_LL,RPS,OU_LL | data_absence,thin_data,feature_failure,baseline_too_strong |
| AR-PrimeraBMetropolitana | G-PBM | ? | 462 | 1426 | 1X2_LL,RPS,OU_LL | thin_data,mover_churn,feature_failure,baseline_too_strong |
| AR-PrimeraBNacional | G-BNAC | ? | 648 | 2648 | 1X2_LL,RPS,OU_LL | era_drift,level_misspec,baseline_too_strong |
| AR-TorneoFederalA | G-FEDA | ? | 459 | 2083 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| AT-2Liga | G-AT2 | 2025/2026 | 210 | 720 | 1X2_LL,OU_LL | baseline_too_strong |
| AT-Bundesliga | G-AT | ? | 195 | 585 | OU_LL | feature_failure,baseline_too_strong |
| AU-ALeague | G-AU | 2025/2026 | 163 | 508 | OU_LL | feature_failure,baseline_too_strong |
| AU-ALeagueWomen | G-AUW | ? | 110 | 369 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| BD-FootballLeague | G-BD | ? | 29 | 270 | OU_LL | feature_failure,thin_data,baseline_too_strong |
| BE-FirstDivisionB | G-BEB | 2025/2026 | 278 | 654 | OU_LL | baseline_too_strong,feature_failure |
| BG-FirstLeague | G-BG | 2025/2026 | 293 | 859 | OU_LL | baseline_too_strong |
| BG-SecondLeague | G-BG2 | 2025/2026 | 272 | 992 | OU_LL | baseline_too_strong |
| BO-PrimeraDivision | G-BO | 2025 | 240 | 896 | OU_LL | baseline_too_strong |
| BR-SerieA | G-BR | 2025 | 380 | 1140 | OU_LL | level_misspec,feature_failure,baseline_too_strong |
| BR-SerieB | G-BRB | 2025 | 380 | 1140 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| BR-SerieC | G-BRC | 2026 | 214 | 856 | 1X2_LL,RPS,OU_LL | thin_data,era_drift,mover_churn,baseline_too_strong |
| BY-PremierLeague | G-BY | 2025 | 240 | 690 | 1X2_LL,RPS,OU_LL | level_misspec,feature_failure,baseline_too_strong |
| CA-PremierLeague | G-CA | 2025 | 112 | 336 | 1X2_LL,OU_LL | thin_data,baseline_too_strong |
| CH-ChallengeLeague | G-CH | 2025/2026 | 181 | 540 | 1X2_LL,RPS,OU_LL | mover_churn,era_drift,baseline_too_strong |
| CH-SuperLeague | G-CH | 2025/2026 | 228 | 636 | OU_LL | baseline_too_strong,feature_failure |
| CL-LigaDeAscenso | G-CLA | 2025 | 240 | 752 | 1X2_LL,RPS,OU_LL | baseline_too_strong,feature_failure |
| CL-LigaDePrimera | G-CL | 2025 | 240 | 720 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| CN-LeagueOne | G-CN | 2025 | 240 | 786 | OU_LL | level_misspec,era_drift,baseline_too_strong |
| CN-SuperLeague | G-CN | 2026 | 240 | 480 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| CO-PrimeraA | G-COA | ? | 204 | 1788 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| CO-PrimeraB | G-CO | ? | 308 | 909 | 1X2_LL,RPS,OU_LL | thin_data,opener_extremes,era_drift,level_misspec,baseline_too_strong |
| CR-PrimeraDivision | G-CR | ? | 262 | 492 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| CY-1Division | G-CY | ? | 240 | 776 | OU_LL | baseline_too_strong |
| CY-2Division | G-CY2 | ? | 232 | 682 | 1X2_LL,OU_LL | mover_churn,thin_data,baseline_too_strong,feature_failure |
| CZ-FNL | G-CZ-FNL | ? | 240 | 720 | 1X2_LL,RPS,OU_LL | mover_churn,thin_data,baseline_too_strong,feature_failure |
| CZ-Liga | G-CZ | 2025/2026 | 270 | 810 | OU_LL | thin_data,baseline_too_strong |
| DE-2Bundesliga | G-DE2 | 2025/2026 | 306 | 918 | OU_LL | level_misspec,feature_failure,baseline_too_strong |
| DE-3Liga | G-DE3 | ? | 380 | 1140 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| DK-1Division | G-DK1 | ? | 192 | 576 | 1X2_LL,RPS,OU_LL | feature_failure,baseline_too_strong |
| DK-2Division | G-DK2 | ? | 192 | 576 | OU_LL | level_misspec,baseline_too_strong |
| DK-Superligaen | G-DK | 2025/2026 | 193 | 579 | OU_LL | level_misspec,feature_failure,baseline_too_strong |
| DZ-Ligue1 | G-DZ | ? | 240 | 719 | OU_LL | level_misspec,baseline_too_strong |
| EC-SerieA | G-EC | 2025 | 312 | 726 | OU_LL | baseline_too_strong,feature_failure |
| EE-Meistriliiga | G-EE | ? | 180 | 720 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| EG-PremierLeague | G-EG | 2025/2026 | 322 | 837 | OU_LL | level_misspec,baseline_too_strong |
| ENG-Championship | G-ENGCH | 2025/2026 | 555 | 1671 | OU_LL | level_misspec,baseline_too_strong |
| ENG-LeagueOne | G-ENGL1 | 2025/2026 | 557 | 1671 | OU_LL | level_misspec,baseline_too_strong |
| ES-LaLiga2 | G-ES | 2025/2026 | 468 | 1404 | OU_LL | level_misspec,baseline_too_strong |
| ES-PrimeraFederacion | G-ESPF | 2025/2026 | 772 | 2322 | 1X2_LL,RPS,OU_LL | era_drift,level_misspec,baseline_too_strong |
| FI-Veikkausliiga | G-FI | 2026 | 177 | 678 | OU_LL | baseline_too_strong |
| FI-Ykkonen | G-FI | 2025 | 162 | 1010 | 1X2_LL,RPS,OU_LL | level_misspec,mover_churn,baseline_too_strong |
| FI-Ykkosliiga | G-YK | 2026 | 135 | 598 | 1X2_LL,OU_LL | mover_churn,baseline_too_strong |
| FO-PremierLeague | G-FO | ? | 135 | 539 | OU_LL | baseline_too_strong |
| FR-Ligue2 | G-FR | 2025/2026 | 306 | 1065 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| FR-Ligue3 | G-FR | 2025/2026 | 272 | 884 | 1X2_LL,RPS,OU_LL | feature_failure,mover_churn,baseline_too_strong |
| GE-Erovnuli | G-GE | ? | 180 | 540 | OU_LL | level_misspec,era_drift,baseline_too_strong |
| GH-PremierLeague | G-GH | ? | 299 | 901 | 1X2_LL,RPS,OU_LL | feature_failure,baseline_too_strong |
| GR-SuperLeague | G-GR | 2025/2026 | 236 | 716 | OU_LL | baseline_too_strong |
| GR-SuperLeague2 | G-GR2 | 2025/2026 | 265 | 1045 | OU_LL | baseline_too_strong |
| GT-LigaNacional | G-GT | ? | 292 | 746 | OU_LL | baseline_too_strong |
| HN-LigaNacional | G-HN | ? | 220 | 540 | OU_LL | baseline_too_strong |
| HR-HNL | G-HR | 2025/2026 | 180 | 540 | OU_LL | baseline_too_strong,level_misspec |
| HU-NBI | G-HU-NBI | ? | 198 | 594 | OU_LL,SIGN_CHECK | baseline_too_strong |
| ID-SuperLeague | G-ID | ? | 306 | 918 | 1X2_LL,RPS,OU_LL | baseline_too_strong,level_misspec |
| IE-FirstDivision | G-IEFD | ? | 180 | 683 | OU_LL | level_misspec,baseline_too_strong,feature_failure |
| IL-Leumit | G-IL | ? | 296 | 888 | 1X2_LL,RPS,OU_LL | level_misspec,baseline_too_strong,feature_failure |
| IN-ISL | G-IN | 2025/2026 | 91 | 419 | OU_LL | baseline_too_strong,feature_failure |
| IN-IndianFootballLeague | G-IN | 2025/2026 | 66 | 418 | 1X2_LL,RPS,OU_LL | level_misspec,mover_churn,baseline_too_strong |
| IQ-StarsLeague | G-IQSL | ? | 379 | 1104 | OU_LL | level_misspec,baseline_too_strong |
| IR-AzadeganLeague | G-IRAZ | ? | 305 | 884 | OU_LL | level_misspec,mover_churn,baseline_too_strong |
| IR-PersianGulf | G-IRPG | ? | 178 | 720 | OU_LL | level_misspec,baseline_too_strong |
| IS-1Deild | G-IS1 | ? | 137 | 543 | 1X2_LL,RPS,OU_LL | era_drift,feature_failure,baseline_too_strong |
| IS-2Deild | G-IS2 | ? | 132 | 528 | 1X2_LL,RPS,OU_LL | thin_data,feature_failure,baseline_too_strong |
| IS-BestaDeildin | G-IS | ? | 162 | 648 | OU_LL | baseline_too_strong,feature_failure |
| IT-SerieB | G-ITB | 2025/2026 | 390 | 1169 | 1X2_LL,RPS,OU_LL | era_drift,feature_failure,baseline_too_strong |
| IT-SerieC | G-ITC | 2025/2026 | 1102 | 3346 | OU_LL | baseline_too_strong |
| J2 | G-J2 | ? | 383 | 1764 | OU_LL | thin_data,opener_extremes,mover_churn,feature_failure,baseline_too_strong |
| J3 | G-J3 | ? | 383 | 1066 | OU_LL,SIGN_CHECK | era_drift,feature_failure,baseline_too_strong |
| KR-KLeague1 | G-KR | ? | 228 | 684 | OU_LL | baseline_too_strong,feature_failure |
| KR-KLeague2 | G-KR2 | ? | 273 | 688 | OU_LL | baseline_too_strong,feature_failure |
| KR-KLeague3 | G-KR3 | ? | 210 | 690 | 1X2_LL,RPS,OU_LL | thin_data,baseline_too_strong |
| KW-PremierLeague | G-KW | 2025/2026 | 111 | 422 | OU_LL | thin_data,level_misspec,feature_failure,baseline_too_strong |
| LT-Toplyga | G-LT | ? | 144 | 720 | OU_LL | baseline_too_strong |
| LU-NationalDivision | G-LU | 2025 | 240 | 720 | 1X2_LL,RPS,OU_LL | baseline_too_strong,level_misspec,era_drift |
| LV-Virsliga | G-LV | 2026 | 179 | 720 | OU_LL | baseline_too_strong |
| MA-BotolaPro | G-MA | 2025/2026 | 240 | 720 | OU_LL | baseline_too_strong,level_misspec |
| MK-PrvaLiga | G-MK | ? | 197 | 549 | OU_LL | baseline_too_strong,feature_failure |
| MX-LigaMX | G-MX | ? | 153 | 1224 | OU_LL | era_drift,level_misspec,baseline_too_strong,feature_failure |
| MY-LigaSuper | G-MY | ? | 156 | 469 | RPS,OU_LL | era_drift,level_misspec,baseline_too_strong |
| NG-ProfessionalLeague | G-NG | ? | 379 | 939 | 1X2_LL,RPS,OU_LL | feature_failure,baseline_too_strong |
| NI-Premiership | G-NI | 2025 | 228 | 684 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| NL-EersteDivisie | G-NLE | ? | 380 | 1140 | OU_LL | baseline_too_strong,feature_failure |
| NL-Eredivisie | G-NL | ? | 306 | 918 | OU_LL | baseline_too_strong,feature_failure |
| NL-TweedeDivisie | G-NLTD | ? | 306 | 918 | OU_LL | baseline_too_strong,feature_failure |
| NO-2Divisjon | G-NO | 2025 | 364 | 1066 | OU_LL | baseline_too_strong,level_misspec |
| NO-Eliteserien | G-NO | ? | 240 | 720 | OU_LL | baseline_too_strong,feature_failure,other |
| NO-OBOSLigaen | G-NO-OBOS | ? | 240 | 960 | OU_LL | baseline_too_strong,level_misspec |
| NZ-Championship | G-NZ | ? | 56 | 92 | 1X2_LL,RPS,OU_LL | thin_data,level_misspec,era_drift,baseline_too_strong,feature_failure |
| PA-LPF | G-PA-LPF | ? | 186 | 382 | 1X2_LL,RPS | thin_data,small_sample_noise,baseline_too_strong |
| PE-Liga1 | G-PE | ? | 323 | 982 | OU_LL | level_misspec,baseline_too_strong |
| PL-IILiga | G-PL-II | ? | 309 | 927 | 1X2_LL,RPS,OU_LL | mover_churn,level_misspec,baseline_too_strong |
| PL-ILiga | G-PL-ILiga | 2025/2026 | 306 | 918 | 1X2_LL,RPS,OU_LL | mover_churn,feature_failure,baseline_too_strong |
| PT-Liga3 | G-PT3 | ? | 296 | 929 | 1X2_LL,RPS,OU_LL | baseline_too_strong,feature_failure |
| PT-LigaPortugal2 | G-PT2 | ? | 306 | 918 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| PY-DivisionProfesional | G-PY | 2026 | 132 | 1056 | OU_LL | level_misspec,baseline_too_strong |
| QA-QatarStars | G-QA | 2025/2026 | 132 | 396 | 1X2_LL,RPS,OU_LL | level_misspec,baseline_too_strong |
| QA-SecondDivision | G-QASD | 2025/2026 | 56 | 28 | 1X2_LL,RPS,OU_LL | thin_data,baseline_too_strong |
| RO-LigaI | G-RO | 2025/2026 | 315 | 945 | OU_LL | level_misspec,baseline_too_strong |
| RO-LigaII | G-RL2 | ? | 317 | 786 | OU_LL | level_misspec,baseline_too_strong |
| RS-SuperLiga | G-RS | 2025/2026 | 296 | 888 | OU_LL | level_misspec,baseline_too_strong |
| RU-1Division | G-RU1 | 2025/2026 | 305 | 918 | RPS,OU_LL | baseline_too_strong |
| RU-PremierLeague | G-RU | 2025/2026 | 240 | 720 | OU_LL | level_misspec,baseline_too_strong |
| RU-SecondLeague | G-RU2 | ? | 888 | 3284 | 1X2_LL,OU_LL | thin_data,mover_churn,level_misspec,baseline_too_strong,other |
| SA-FirstDivision | G-SAFD | 2025/2026 | 304 | 216 | OU_LL | thin_data,baseline_too_strong |
| SA-ProLeague | G-SA | 2025/2026 | 306 | 612 | OU_LL | level_misspec,baseline_too_strong |
| SCO-Championship | G-SCOCH | 2025/2026 | 180 | 540 | 1X2_LL,RPS,OU_LL | baseline_too_strong |
| SCO-LeagueOne | G-SCO-L1 | ? | 180 | 540 | OU_LL | baseline_too_strong |
| SE-Allsvenskan | G-SE | 2025 | 240 | 720 | OU_LL | baseline_too_strong |
| SE-Ettan | G-SE | 2025 | 480 | 1440 | 1X2_LL,RPS,OU_LL | level_misspec,baseline_too_strong |
| SE-Superettan | G-SE2 | 2026 | 240 | 960 | 1X2_LL,RPS,OU_LL | baseline_too_strong,feature_failure |
| SG-PremierLeague | G-SG | 2025/2026 | 84 | 364 | OU_LL | baseline_too_strong |
| SK-1Liga | G-SK | 2025/2026 | 192 | 576 | OU_LL | baseline_too_strong,thin_data |
| SK-2Liga | G-SK2 | 2025/2026 | 240 | 613 | OU_LL | baseline_too_strong,thin_data |
| SLO-PrvaLiga | G-SLO | ? | 161 | 538 | OU_LL | level_misspec,baseline_too_strong |
| SV-PrimeraDivision | G-SV | ? | 264 | 815 | OU_LL | baseline_too_strong,level_misspec |
| TH-ThaiLeague | G-TH | 2025/2026 | 240 | 720 | OU_LL | baseline_too_strong |
| TH-ThaiLeague2 | G-TH2 | 2025/2026 | 306 | 183 | 1X2_LL,RPS,OU_LL | thin_data,baseline_too_strong |
| TR-1Lig | G-TR1 | ? | 379 | 998 | OU_LL | baseline_too_strong,feature_failure |
| TZ-PremierLeague | G-TZ | ? | 239 | 720 | OU_LL | baseline_too_strong,level_misspec,gate_architecture |
| US-MLS | G-US | ? | 540 | 1532 | 1X2_LL,RPS,OU_LL | baseline_too_strong,feature_failure |
| US-USLChampionship | G-USL | ? | 375 | 1318 | OU_LL | baseline_too_strong |
| US-USLLeagueOne | G-USLL1 | ? | 210 | 489 | 1X2_LL,RPS | baseline_too_strong,feature_failure |
| UY-LigaAUF | G-UY | 2025 | 300 | 895 | OU_LL | baseline_too_strong,era_drift,level_misspec |
| UY-SegundaDivision | G-UYSEG | 2026 | 218 | 863 | 1X2_LL,RPS,OU_LL | baseline_too_strong,thin_data,feature_failure,level_misspec |
| VN-VLeague | G-VN | 2025/2026 | 182 | 654 | RPS,OU_LL | baseline_too_strong,thin_data,feature_failure |
| WAL-CymruPremier | G-WAL | ? | 192 | 576 | OU_LL | baseline_too_strong |
| ZA-PSL | G-ZA | 2025/2026 | 240 | 690 | OU_LL | baseline_too_strong |

## SOT (13)

| League | Candidate | Sealed window (from prereg) | Virgin n | Dev n | Failed dev legs | Mechanisms |
|---|---|---|---|---|---|---|
| AT-2Liga | S-AT2 | 2025/2026 | 210 | 708 | OU_LL | era_drift,baseline_too_strong |
| CH-ChallengeLeague | S-CH | 2025/2026 | 181 | 180 | OU_LL | thin_data,baseline_too_strong |
| DK-Superligaen | S-DK | 2025/2026 | 193 | 579 | OU_LL | thin_data,era_drift,feature_failure,baseline_too_strong |
| HU-NBI | S-HU-NBI | ? | 198 | 588 | SIGN_CHECK | baseline_too_strong |
| IE-PremierDivision | S-IE | 2026 | 180 | 540 | OU_LL | baseline_too_strong |
| IT-SerieB | S-ITB | 2025/2026 | 390 | 1169 | OU_LL | era_drift,level_misspec,feature_failure,baseline_too_strong |
| KR-KLeague1 | S-KR | ? | 228 | 684 | OU_LL | baseline_too_strong |
| KR-KLeague2 | S-KR2 | ? | 273 | 461 | OU_LL | era_drift,feature_failure,baseline_too_strong |
| MA-BotolaPro | S-MA | 2025/2026 | 226 | 109 | OU_LL | thin_data,baseline_too_strong,feature_failure |
| QA-SecondDivision | S-QASD | 2026/2027 | 29 | 28 | OU_LL | thin_data,small_sample_noise,baseline_too_strong |
| TH-ThaiLeague | S-TH | 2025/2026 | 240 | 480 | OU_LL | baseline_too_strong |
| VE-PrimeraDivision | S-VE | 2026 | 90 | 91 | OTHER | baseline_too_strong,thin_data |
| ZA-PSL | S-ZA | 2025/2026 | 240 | 448 | OTHER | baseline_too_strong,feature_failure |

## Cards (49)

| League | Candidate | Sealed window (from prereg) | Virgin n | Dev n | Failed dev legs | Mechanisms |
|---|---|---|---|---|---|---|
| AE-ProLeague | K-AE | 2025/2026 | 182 | 545 | OU_LL | feature_failure,baseline_too_strong |
| AT-2Liga | K-AT2 | 2025/2026 | 210 | 720 | OU_LL | feature_failure,baseline_too_strong |
| AT-Bundesliga | K-AT | ? | 195 | 585 | OU_LL | era_drift,baseline_too_strong |
| BG-FirstLeague | K-BG | 2025/2026 | 293 | 859 | OU_LL | feature_failure,era_drift,baseline_too_strong |
| BO-PrimeraDivision | K-BO | 2026 | 199 | 160 | OU_LL | feature_failure,thin_data,baseline_too_strong |
| BR-SerieA | K-BR | 2025 | 380 | 1139 | OU_LL | feature_failure,baseline_too_strong |
| BR-SerieB | K-BRB | 2025 | 380 | 380 | OU_LL | feature_failure,baseline_too_strong |
| CA-PremierLeague | K-CA | 2025 | 112 | 112 | OU_LL | thin_data,feature_failure,baseline_too_strong |
| CH-ChallengeLeague | K-CH | 2025/2026 | 181 | 180 | OU_LL | thin_data,baseline_too_strong |
| CL-LigaDePrimera | K-CL | 2025 | 240 | 720 | OU_LL | baseline_too_strong |
| CO-PrimeraA | K-COA | 2026 | 204 | 1110 | OU_LL | baseline_too_strong,gate_architecture |
| CZ-Liga | K-CZ | 2025/2026 | 270 | 810 | OU_LL | era_drift,level_misspec,baseline_too_strong |
| EG-PremierLeague | K-EG | 2025/2026 | 322 | 824 | OU_LL | era_drift,feature_failure,baseline_too_strong |
| ENG-Championship | K-ENGCH | 2025/2026 | 555 | 1671 | OU_LL | feature_failure,baseline_too_strong |
| ENG-LeagueOne | K-ENGL1 | 2025/2026 | 557 | 1671 | OU_LL | era_drift,feature_failure,baseline_too_strong |
| ES-LaLiga2 | K-ES | 2025/2026 | 468 | 1404 | OU_LL | feature_failure,baseline_too_strong |
| FO-PremierLeague | K-FO | ? | 135 | 539 | OU_LL | baseline_too_strong,gate_architecture |
| FR-Ligue2 | K-FR | 2025/2026 | 306 | 1065 | OU_LL | baseline_too_strong |
| GR-SuperLeague | K-GR | 2025/2026 | 236 | 716 | OU_LL | level_misspec,baseline_too_strong |
| HU-NBI | K-HU-NBI | ? | 198 | 594 | OU_LL | baseline_too_strong |
| ID-SuperLeague | K-ID | ? | 306 | 731 | OU_LL | gate_architecture,thin_data,feature_failure,baseline_too_strong |
| IE-PremierDivision | K-IE | 2026 | 180 | 720 | OU_LL | baseline_too_strong |
| IN-ISL | K-IN | 2025/2026 | 91 | 419 | OU_LL | level_misspec,baseline_too_strong |
| IS-BestaDeildin | K-IS | ? | 162 | 324 | OU_LL | baseline_too_strong,feature_failure |
| IT-SerieB | K-ITB | 2025/2026 | 390 | 1169 | OU_LL | baseline_too_strong |
| J2 | K-J2 | ? | 383 | 1764 | OU_LL | era_drift,data_absence,feature_failure,baseline_too_strong |
| KR-KLeague2 | K-KR2 | ? | 273 | 229 | OU_LL | thin_data,baseline_too_strong |
| LV-Virsliga | K-LV | 2026 | 179 | 133 | OU_LL | thin_data,baseline_too_strong,feature_failure |
| MA-BotolaPro | K-MA | 2025/2026 | 240 | 112 | OU_LL | thin_data,baseline_too_strong,feature_failure,level_misspec |
| MX-LigaMX | K-MX | ? | 153 | 1224 | OU_LL | baseline_too_strong,feature_failure,data_absence |
| NL-EersteDivisie | K-NLE | ? | 380 | 1140 | OU_LL | baseline_too_strong |
| NL-Eredivisie | K-NL | ? | 306 | 918 | OU_LL | baseline_too_strong |
| NO-OBOSLigaen | K-NO-OBOS | ? | 240 | 960 | OU_LL | baseline_too_strong,gate_architecture |
| PE-Liga1 | K-PE | ? | 323 | 475 | OU_LL | gate_architecture,baseline_too_strong,era_drift |
| QA-SecondDivision | K-QASD | 2026/2027 | 29 | 28 | OU_LL | thin_data,small_sample_noise,level_misspec,baseline_too_strong |
| RU-1Division | K-RU1 | 2025/2026 | 305 | 918 | OU_LL | level_misspec,baseline_too_strong |
| SA-FirstDivision | K-SAFD | 2026/2027 | 94 | 214 | OU_LL | thin_data,feature_failure,baseline_too_strong |
| SA-ProLeague | K-SA | 2025/2026 | 306 | 612 | OU_LL | feature_failure,baseline_too_strong |
| SCO-Premiership | K-SCO | 2025/2026 | 228 | 684 | OU_LL | baseline_too_strong |
| SE-Allsvenskan | K-SE | 2025 | 240 | 720 | OU_LL | baseline_too_strong,gate_architecture |
| SK-1Liga | K-SK | 2025/2026 | 192 | 576 | OU_LL | feature_failure,baseline_too_strong |
| TH-ThaiLeague | K-TH | 2025/2026 | 240 | 480 | OU_LL | baseline_too_strong |
| TH-ThaiLeague2 | K-TH2 | 2025/2026 | 306 | 182 | OU_LL | thin_data,feature_failure,baseline_too_strong |
| TR-SuperLig | K-TR | 2025/2026 | 306 | 1033 | OTHER | baseline_too_strong,gate_architecture |
| US-MLS | K-US | ? | 540 | 1529 | OTHER | baseline_too_strong,gate_architecture |
| US-USLChampionship | K-USL | ? | 375 | 1318 | OTHER | baseline_too_strong |
| US-USLLeagueOne | K-USLL1 | ? | 210 | 313 | OTHER | baseline_too_strong,thin_data |
| VE-PrimeraDivision | K-VE | 2026 | 90 | 91 | OTHER | baseline_too_strong,thin_data |
| ZA-PSL | K-ZA | 2025/2026 | 240 | 447 | OTHER | baseline_too_strong,era_drift |

## Corners (7)

| League | Candidate | Sealed window (from prereg) | Virgin n | Dev n | Failed dev legs | Mechanisms |
|---|---|---|---|---|---|---|
| BO-PrimeraDivision | C-BO | 2026 | 199 | 160 | OU_LL | feature_failure,thin_data,baseline_too_strong |
| KR-KLeague2 | C-KR2 | ? | 273 | 461 | OU_LL | era_drift,feature_failure,baseline_too_strong |
| LV-Virsliga | C-LV | 2026 | 179 | 133 | OU_LL | thin_data,baseline_too_strong,feature_failure |
| NL-Eredivisie | C-NL | ? | 306 | 918 | OU_LL | baseline_too_strong,level_misspec,feature_failure |
| PT-LigaPortugal | C-PT | 2026/2027 | 98 | 1224 | OU_LL | level_misspec,feature_failure,baseline_too_strong |
| PY-DivisionProfesional | C-PY | 2026 | 112 | 263 | OU_LL | baseline_too_strong,gate_architecture |
| QA-SecondDivision | C-QASD | 2026/2027 | 29 | 28 | OU_LL | thin_data,level_misspec,feature_failure,baseline_too_strong |

## Total shots (6)

| League | Candidate | Sealed window (from prereg) | Virgin n | Dev n | Failed dev legs | Mechanisms |
|---|---|---|---|---|---|---|
| AU-ALeagueWomen | T-AUW | ? | 110 | 369 | OU_LL | baseline_too_strong |
| CA-PremierLeague | T-CA | ? | 112 | 336 | OU_LL | thin_data,feature_failure,baseline_too_strong |
| HU-NBI | T-HU-NBI | ? | 198 | 588 | OU_LL | baseline_too_strong |
| KR-KLeague2 | T-KR2 | ? | 273 | 461 | OU_LL | era_drift,feature_failure,baseline_too_strong |
| QA-SecondDivision | T-QASD | 2026/2027 | 29 | 28 | OU_LL | thin_data,baseline_too_strong |
| SA-FirstDivision | T-SAFD | 2026/2027 | 94 | 214 | OU_LL | thin_data,baseline_too_strong |

Prereg virgin-season extraction misses: 91 ['G-AL', 'G-AM', 'G-AR', 'G-PBM', 'G-BNAC', 'G-FEDA', 'G-AT', 'G-AUW', 'G-BD', 'G-COA', 'G-CO', 'G-CR']
