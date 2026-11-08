# Lane 1 — Wave-1 Cohort Analysis

Date: 2026-11-11. Scope: cohort selection only. No preregistration was
written, no sealed window was read, no code was run against sealed data.
Sources: `league/IMPROVEMENT_PROGRAM.md` (Lane 1 rules),
`league/IMPROVEMENT_LANE1_INVENTORY.md` (210 dev-fail candidates),
`league/IMPROVEMENT_STATUS.md`, `league/AUDIT.md` §2/§5,
`league/audit_scratch/class_batch*.jsonl`,
`league/audit_scratch/bugs_batch*.md`, and the named leagues' own
prereg/verdict artefacts (dev artefacts only).

Governing fact (per the task and the charter): re-running a Lane 1
candidate with the SAME method on the SAME dev data deterministically
reproduces its dev FAIL and never reaches its window. A wave-1 entry
therefore needs a legitimate method difference, stated in advance.
Two such differences exist in the audit record: (A) a variant that
already beat both baselines on dev but was never read because Gate
Zero failed (the gate-architecture / variants-moot class), and (B) dev
legs computed under an audit-fixed bug, where corrected code is a
different method from the one that produced the FAIL.

## Headline counts

| Cohort | Screened | Confirmed / survivors | Wave-1 recommended |
|---|---|---|---|
| A — variants-moot (AUDIT §2 cause 4) | 10 named | 10/10 in Lane 1 inventory; **9 clean-eligible**, 1 spoiled (K-TR) | 9 |
| B — bug-affected dev fails (§5.6/§5.9/§5.1/§5.5/§5.10 + extensions) | 42 (39 named-class + 3 extension) | **3 survivors** (all §5.9 M_BAR) | 3 |
| **Wave-1 total** | | | **12** |

Conditional items NOT counted in the 12 (coordinator rulings needed):
K-TR (window spoiled — future window only), K-AT (an 11th documented
variants-moot case found during §5.6 screening; §2's list does not
name it), K-MX (§5.13 recorded deviation — outside the four named
bug classes and never audit-fixed). Details in §4.

---

## 1. Cohort A — variants-moot (AUDIT §2, cause 4)

AUDIT §2 cause 4: "A variant beat both baselines on dev but was never
read because Gate Zero failed: CO-PrimeraA K, FO-PremierLeague K,
ID-SuperLeague K, NO-OBOSLigaen K, PE-Liga1 K, SE-Allsvenskan K,
TR-SuperLig K, US-MLS K, PY-DivisionProfesional C,
TZ-PremierLeague G. Eight of ten are cards, where the blocked variant
is the referee arm."

### 1.1 Inventory confirmation (all 10)

Every one of the 10 is present in `IMPROVEMENT_LANE1_INVENTORY.md`
and in the classification JSONL with `outcome=FAIL`,
`fail_point="dev"`. Quoted `fail_legs` (identical in the inventory's
"Failed dev legs" column and the JSONL):

| Candidate | fail_point | fail_legs (JSONL) | Mechanisms (JSONL) | Sealed window (prereg) | Virgin n |
|---|---|---|---|---|---|
| K-COA | dev | OU_LL | baseline_too_strong, gate_architecture | 2026 – Apertura | 204 |
| K-FO | dev | OU_LL | baseline_too_strong, gate_architecture | 2026 | 135 |
| K-ID | dev | OU_LL | gate_architecture, thin_data, feature_failure, baseline_too_strong | 2025/2026 | 306 |
| K-NO-OBOS | dev | OU_LL | baseline_too_strong, gate_architecture | 2026 | 240 |
| K-PE | dev | OU_LL | gate_architecture, baseline_too_strong, era_drift | 2025 | 323 |
| K-SE | dev | OU_LL | baseline_too_strong, gate_architecture | 2025 | 240 |
| K-TR | dev | OTHER | baseline_too_strong, gate_architecture | 2025/2026 — **SPOILED, see §1.3** | 306 |
| K-US | dev | OTHER | baseline_too_strong, gate_architecture | 2025 | 540 |
| C-PY | dev | OU_LL | baseline_too_strong, gate_architecture | 2026 – Clausura (transitional) | 112 |
| G-TZ | dev | OU_LL | baseline_too_strong, level_misspec, gate_architecture | 2025/2026 | 239 |

**Cohort A confirmed count: 10/10 in the Lane 1 inventory.**
For 9 of 10 the verdict artefact records `virgin_read: false` /
"deliberately NOT read" — the window is genuinely unread. K-TR is
the exception (§1.3).

### 1.2 The blocked variants — exact dev numbers (from each verdict)

All LLs are pooled dev log-loss at the candidate's primary line;
lower is better. "Beats both" = variant LL < base rate AND < naive
trailing-10.

| Candidate | Line / dev n | Gate Zero LL | Winning variant (arm) | Variant LL | Base rate | Naive t-10 | Why never read |
|---|---|---|---|---|---|---|---|
| K-COA | 5.5 / 1,110 | 0.7001 | **X8 referee multiplier** (J1 mechanics, K_REF=8, clamp [0.67,1.50]) | **0.6918** | 0.6956 | 0.7080 | GZ loses to base rate; prereg's mechanical reading makes the variant moot. Verdict: "A future, separately pre-registered design could register the referee arm as the base architecture." Referee trait r=0.487, dev coverage 95.4%. |
| K-FO | 3.5 / 539 | 0.6847 | **SHRINK** (shrinkage variant of the reference pattern — NOT a referee arm; no referee arm exists, coverage 0/810) | **0.6810** | 0.6824 | 0.6930 | GZ loses to base rate; frozen rule "Gate Zero fails dev ⇒ variants moot". Margin is a whisker (0.0014) and SHRINK loses to base in 2023 — recorded in the verdict itself. |
| K-ID | 4.5 / 731 | 0.7003 | **X5 blend** (mu = 0.5·model + 0.5·naive trailing-10 — NOT a referee arm; X8 dropped, referee identity absent in 1,620/1,620 payloads) | **0.6940** | 0.6959 | 0.6978 | GZ beats neither baseline (0.7003 vs 0.6959/0.6978); frozen rule kills the candidate, variant moot. Scored on events_complete rows only; the 2023/24 block is a 144-match Jul–Oct high-card slice. |
| K-NO-OBOS | 3.5 / 960 | 0.6693 | **X8 referee covariate** (F8 r=0.715 — the program's strongest referee reading at the time) | **0.6553** | 0.6683 | 0.6729 | GZ beats naive but loses to base rate by 0.0010; variant moot by rule. Verdict itself names the remedy: "a future prereg that promotes the referee arm to the reference position." |
| K-PE | 4.5 / 475 | 0.712602 | **X8 referee multiplier** (K_REF=8, clamp [0.67,1.50]; strictness r=0.769 — strongest measured in the program) | **0.687450** | 0.707846 | 0.692826 | GZ fails against BOTH baselines; variant moot, virgin NOT read. X8 beats GZ in all 3 dev blocks. |
| K-SE | 3.5 / 720 | 0.6917 | **X8 referee covariate** (prior weight 8; trait F8 r=0.616) | **0.6770** | 0.6884 | 0.6871 | GZ beats neither baseline; variants moot per the prereg's NOT-built clause. |
| K-TR | 4.5 / 1,033 | 0.697294 | **X8 referee covariate** (strictness r≈0.53; sign check 3/3 vs GZ) | **0.686474** | 0.690967 | 0.698291 | GZ beats naive, loses to base rate; variant moot by the frozen mechanical reading. **Then spoiled — §1.3.** |
| K-US | 4.5 / 1,529 | 0.678407 | **X8 referee covariate** (F8 r=0.634) | **0.670898** | 0.677134 | 0.682714 | GZ beats naive, loses to base rate by 0.001273; X8 moot under the frozen gate order. Per-season: X8 loses 2022 (0.714217 vs GZ 0.706163) but wins 2023/2024 → sign check 2/3. |
| C-PY | 8.5 / 263 | 0.7211 | **X7 opp-box touches multiplier** (touches trait r=0.70 — NOT a referee arm; corners market) | **0.6918** | 0.7313 | 0.7180 | GZ beats base rate but loses to naive (0.7211 vs 0.7180); frozen rule makes X7 moot. X7 better than GZ in both dev blocks. |
| G-TZ | OU 2.5 + 1X2/RPS / 720 | OU 0.716160 (fails); 1X2 LL 0.956279, RPS 0.185632 (both pass) | **SHRINK** (thin-data arm: ratings of teams with 1–5 prior in-league matches shrunk a,d *= n/6 — NOT a referee arm; goals market) | 1X2 LL **0.925501**, RPS **0.180158**, OU **0.689404** | climatology 1X2 1.069080 / RPS 0.223944; OU base 0.692720 | (OU naive 0.715453) | GZ fails one of three dev legs (OU); the prereg makes GZ's dev pass a precondition for any virgin read — virgin leg (i) compares against GZ's virgin LL, which cannot exist. SHRINK passes all three pooled legs on its own numbers, OU by only −0.003316, and bites on just 60 of 720 rows. |

### 1.3 K-TR — in the inventory, but its window is NOT unread (EXCLUDED from wave 1)

K-TR sits in the Lane 1 inventory by the mechanical FAIL-at-dev
definition, but AUDIT §5.7 records the program's one realised
sealed-read breach: "The unguarded path was actually invoked: X8
(dev-passing but moot, Gate Zero having failed dev) was read on the
sealed window against the frozen rule. The programme caught it,
removed the artefacts, and recorded the candidate as spoiled — FAIL
at dev, with the disclosed sealed numbers explicitly 'not gate
results'." The K-TR verdict discloses the spoiled numbers (virgin
LL@4.5 0.674013; calibration +2.208pp, SE 2.807pp) and concludes:
"A future candidate would need a NEW prereg with a fresh virgin
(2026/2027 once complete)."

Disposition: K-TR is **not** a Lane 1 wave-1 entry on 2025/2026 —
that window is burned in substance, whatever the inventory's
mechanical classification says. It becomes eligible only on the
completed 2026/2027 window under a fresh prereg, i.e. a later wave.
This mirrors the charter: "Burned sealed windows stay burned FOR
CLEAN VERDICTS."

### 1.4 Shipping caveats (operational gate — caveat, not exclusion)

Per the task and the AR-PrimeraBNacional precedent (K-BNAC shipped
X8 provisionally with the operational referee condition attached:
"if appointments are not published pre-match, fall back to Gate Zero
for that fixture; no referee identity is imputed"), a referee arm's
dependence on pre-match appointment publication is a shipping
caveat, not a cohort exclusion. MEMORY.md also records the standing
observation behind it: FotMob referee names for upcoming fixtures
can be empty until near matchday (the held DE-2Bundesliga cards
case).

| Candidate | Referee-arm shipping caveat? | Basis |
|---|---|---|
| K-COA (X8) | **YES** | Prereg fallback: unnamed referee / <8 priors → Gate Zero for that fixture. Historical dev coverage 95.4% proves the signal exists post-match; pre-match publication in the live FotMob pipeline is unproven. |
| K-NO-OBOS (X8) | **YES** | Prereg operational condition "as K-J1": "Referee assignment must be known at prediction time in the live pipeline; warehouse records are post-match snapshots and cannot prove pre-match publication." Historical virgin coverage 229/240 = 95.4%. |
| K-PE (X8) | **YES** | Prereg: "if the appointment is not published pre-match in the live pipeline, the fixture falls back to Gate Zero." Historical coverage already thinner: 97.9% (2023) / 84.6% (2024) / 80.5% (virgin 2025). |
| K-SE (X8) | **YES** | Prereg operational condition (inherited), same fallback. Coverage incomplete by design: 0% in 2021 warm-up, 84.6% named in virgin 2025. |
| K-TR (X8) | YES (moot — excluded on the spoiled window first) | Same inherited condition; virgin coverage was 91.5%. |
| K-US (X8) | **YES** | Prereg operational condition, identical K-J1 wording. Historical coverage strong (dev 96.2–99.0%, virgin 96.1%) but still a post-match-snapshot statistic. |
| K-FO (SHRINK) | No — different caveat | No referee input at all. Caveat is statistical thinness: pooled edge over base is 0.0014 LL and the arm loses to base in 1 of 4 seasons on the verdict's own reading (2023). |
| K-ID (X5) | No | No referee input (identity absent league-wide). Caveat: scoring restricted to events_complete matches; dev contains the anomalous 144-match 2023/24 slice. |
| C-PY (X7) | No | No referee input. Caveat is the window itself: 2026–Clausura was TRANSITIONAL (n=112 played at pull) — completeness must be re-pinned verbatim at fresh preregistration. |
| G-TZ (SHRINK) | No | No referee input. Caveat: OU margin −0.003316 is thin and the arm's action is concentrated in 60 rows (two renamed clubs). |

### 1.5 Fresh-prereg design (applies to every cohort-A entry)

One paragraph, stated in advance, identical in structure for all
nine wave-1 entries (per-candidate specifics in the table notes and
§3): **The winning variant named in §1.2 becomes the arm of record
in a fresh preregistration, committed before any window read; Gate
Zero is retained as a baseline only — its dev numbers are recomputed
and reported, but its dev pass is no longer a precondition for the
arm of record's sealed read (that precondition is the
gate-architecture defect this cohort exists to correct, and removing
it is the stated method difference). The gates are otherwise
identical to the original prereg's legs: the dev gate is the arm of
record's pooled dev LL beating BOTH baselines at the original
primary line; the sealed legs are (i) sealed LL ≤ Gate Zero's sealed
LL and ≤ both baselines', (ii) calibration |breach| ≤ 1.0pp clean,
within 1 SE of the boundary provisional, beyond it FAIL, and (iii)
the per-season/block sign check of the arm of record vs Gate Zero in
at least half the dev seasons/blocks (for G-TZ: the three original
pooled legs — 1X2 LL and RPS vs climatology, OU LL vs base rate —
with SHRINK as the arm of record and leg (i) read against
climatology and the baselines, since no Gate Zero sealed LL will be
produced as a gate reference; the coordinator pins this substitution
verbatim in the fresh prereg). All runs execute under
`league/gate_lib/` (P5: fail-closed sealed loader asserting the dev
gate before any sealed load, mechanical prereg-token parsing,
derived-constant checking, one calibration sign convention), under
the P2 design seal (all EDA/reliability artefacts recomputed on
dev-era seasons only; sealed aggregates, if any, generated by the
coordinator after the design freezes), and with P6 worst-fold
reporting (the worst dev season's/block's legs reported beside the
pooled legs in the verdict, information only). One read of the named
sealed window, verdict final, no iteration against the window after
the read. For the six X8 cards entries, the original prereg's
operational condition is carried over verbatim: an unpublished
appointment falls back to Gate Zero for that fixture, with no
imputation, and a PASS ships with that condition attached (the
K-BNAC precedent).**

---

## 2. Cohort B — bug-affected dev fails

Method: every candidate named by AUDIT §5.1, §5.5, §5.6, §5.9,
§5.10 (plus the §5.9 carrier sweep across all six total-shots dev
fails and the eligibility-helper family in `bugs_batch*.md`) was
intersected with the Lane 1 inventory. A candidate survives ONLY if
(a) `fail_point = dev`, and (b) its DEV numbers were plausibly
distorted by the bug — judged on the audit's own adjudication.
Where the audit certifies a candidate's FAIL unaffected / neutral /
robust, the candidate is EXCLUDED and the certification is quoted.

**Screened: 42 unique candidates** (39 under the named classes,
including the six-candidate §5.9 total-shots sweep and three
eligibility-helper cases; plus 3 extension cases from §5.12/§5.13
screened for completeness). **In-Lane-1 (dev FAIL) among screened:
28. Survivors: 3.**

### 2.1 §5.6 — gate-arithmetic tokens diverging from prereg (FIXED, commit b7881d90)

AUDIT §5.6 header: token divergences "each verified outcome-neutral
against its verdict before fixing."

| Candidate | In Lane 1? | Bug | Audit adjudication → disposition |
|---|---|---|---|
| K-AR (AR cards) | No — FAIL at sealed (CAL_LINE) | Provisional test `≤.01 OR ≤SE` instead of `≤.01+SE`; sign ≥2 vs ≥3; keys `diff_2_5` | "K-AR arms fail under either form — breaches 3.95/4.95pp vs SE ≈3.2pp." Not a dev fail → out of Lane 1 entirely. (Its §5.8 baseline deviation is likewise sealed-decided.) |
| K-AT (AT cards) | Yes — dev, OU_LL | Same provisional-token class + best-baseline omits naive — both in the VIRGIN-leg verdict writer | Virgin never read (dev FAIL), so virgin-leg tokens never computed any dev number. The dev FAIL (GZ 0.6654 vs naive 0.6636) is produced by the dev harness, not the buggy writer. **EXCLUDED as a cohort-B case.** (But see §4: K-AT is a genuine variants-moot case.) |
| C-AR (AR corners) | No — PASS_PROV | Sign check `sum ≥ 2` vs prereg ≥3 | Verdict reapplied 3/6 and passed. Not a fail → out. |
| K-BR (BR cards) | Yes — dev, OU_LL | Both-pass selection minimised virgin LL at 3.5 instead of frozen 4.5; harness stored 4.5 calibration under `diff_3_5` keys (KeyError crash path in the gate runner) | §5.6: "selection never engaged (no eligible arm in either league)". Dev gate numbers (GZ 0.688573 vs base 0.686601) are computed before any selection. **EXCLUDED as a cohort-B case.** (K-BR's real story is mootness + a computed virgin — §4.) |
| K-BRB (BR-SerieB cards) | Yes — dev, OU_LL | Same wrong-line selection (shared runner line) | Selection never engaged; and on dev numbers X8 (0.68456) also loses to naive (0.68166), so no arm was eligible under any token reading. **EXCLUDED.** |
| C-BR (BR corners) | No — FAIL at sealed | Sealed calibration computed at 9.5 vs prereg primary 10.5 | Verdict already states the correct-line calibration; sealed fail on VIRGIN_LL. Not Lane 1 → out. |
| C-BRB (BR-SerieB corners) | No — PASS_PROV | Same wrong-line sealed calibration | Verdict manually corrected (−2.324pp at 10.5). Not a fail → out. |

**§5.6 survivors: 0.** Every dev-fail instance is a virgin-stage or
selection-stage token that never touched a dev leg, and the audit
certified the class outcome-neutral candidate by candidate.

### 2.2 §5.9 — M_BAR copied level prior, total-shots engines (FIXED where documented, commit 62800ae2)

The T-family `model.py` carries `M_BAR = 24.9` — J1's dev mean total
shots (24.898, PREREG_T_J1) — as the level prior for arm B
(LevelLayer) and arm C (TrailingR). AUDIT §5.9: "Arm A (v1) never
touches M_BAR… For the remaining ~41 carriers, all-rows data means
computed in this audit differ from 24.9 by >1.0 shots in at least 15
leagues… — their arm B/C gate numbers were computed under the same
template prior. None of those B/C arms shipped. Constants left
as-is where no league document states the intended value."

Documented-and-fixed four — none is a dev fail, so none enters
Lane 1: T-CH (PASS_PROV, fixed to 27.44), T-CN (PASS_PROV, fixed to
27.25; its B-over-A selection margin of 0.0010 LL was computed under
the wrong prior — a shipped-selection caveat for the record, not a
Lane 1 case), T-CL (PASS_CLEAN, fixed to ≈26.4), T-CY (PASS_PROV,
fixed to 18.369). §5.10's T-CY eligibility helper (17.5 vs frozen
18.5, same fix commit) is adjudicated in §2.4.

The six Lane 1 total-shots dev fails, screened one by one:

| Candidate | M_BAR in engine | League's own dev mean (document) | Dev margins (pooled LL at primary line) | Disposition |
|---|---|---|---|---|
| **T-CA** (CA-PremierLeague, line 22.5, n=336) | 24.15 (the AR value, copied with the port; the harness computes the league mean 22.8326 into `results_dev.json`'s protocol block but never assigns it to the model's M_BAR, so arms B/C ran under 24.15) | **22.8326** (own `results_dev.json` protocol — a league artefact stating the intended value) | A 0.687676, B 0.687951, C 0.687220 vs base 0.696515, naive 0.686318. All beat base; all lose naive — C, the arm whose trailing-r estimator reads M_BAR directly, by **0.0009** | **SURVIVOR.** The distortion (+1.32 shots on the prior) sits on exactly the arms that failed, the binding margin (0.0009) is smaller than any plausible prior effect, and no audit text certifies T-CA neutral — §5.9's carrier statement covers it. |
| **T-HU-NBI** (HU-NBI, line 19.5, n=588) | 24.9 (template value, still in code) | **19.0425** (own prereg, recomputed pre-fitting from the committed CSV: "dev means … total shots 19.0425") | A 0.7067, B 0.7058, C 0.7035 vs base 0.6956, naive 0.7058 (naive figure itself corrupted — §5.12). Binding leg is base rate: C loses it by 0.0079 | **SURVIVOR, with caveats.** Largest M_BAR error in the sweep (+5.86 shots — the prior is 31% above the league's true level, in a league whose verdict notes its shot definition is narrower). No M_BAR-specific neutrality certification exists. Caveats: (i) §5.12 certifies the SEPARATE naive=B bug non-decisive ("all three arms also lose to the true base rate… so the dev FAIL stands on the uncorrupted leg") — that certification covers the baseline bug, not the M_BAR distortion of arms B/C themselves, and a corrected re-evaluation must fix BOTH defects together; (ii) arm A never touches M_BAR and also fails, so — exactly as in cohort A — the fresh prereg must designate the corrected arm as the arm of record (see §2.5); (iii) the base-rate gap (0.0079) is the widest among the survivors. |
| **T-AUW** (AU-ALeagueWomen, line 27.5, n=369) | 24.9 (template value, still in code) | No explicit dev-mean document found in the prereg; the level is pinned by the line itself — primary 27.5 at a 49.9% dev over-rate implies a dev mean at ≈27.5 or above (and §5.9's carrier examples include an "AU 28.1" all-rows mean). Prior error ≈ −2.6 shots or more | A 0.698179, B 0.698950, C 0.698417 vs base 0.698602, naive 0.696919. A/C beat base, lose naive; binding margins: B 0.0020, C 0.0015 vs naive | **SURVIVOR (weakest documentation).** Margins are of the same tiny order as T-CA's and the prior error is large and in the level layer's working direction; §5.9's carrier statement covers the B/C numbers and no neutrality certification exists. The fresh prereg must derive M_BAR from the league's own dev rows via the gate_lib derived-constant checker (P5) — that derivation is part of the corrected method, since no frozen league value exists to restore. |
| T-KR2 (KR-KLeague2, line 24.5, n=461) | Not applicable — different engine family (Gate Zero / X7 / E9 arms; no A/B/C M_BAR structure) | — | GZ 0.723430, E9 0.721798 vs base 0.693141 (gap ≈0.029) | **EXCLUDED.** Not an M_BAR carrier. Its implementation defects (goals-scale IPF step; uncentred ratings) were, per its verdict, "fixed before these results" and all headline LLs recomputed independently to 1e-6 — the FAIL was produced by corrected code. |
| T-QASD (QA-SecondDivision, line 23.5, n=28) | 24.9 (recorded in the verdict's dev parameter list) | Not stated | A/B/C lose naive by 0.0262 / 0.0252 / 0.0255 | **EXCLUDED.** The verdict's own adjudication: "The margin is solid — this is a genuine fail, not a borderline one", uniform across the whole ladder, on n=28. A bounded level-layer correction (factor clamp [0.90, 1.10] in the template) does not plausibly close a 0.025 LL gap, and no arm is within reach of the gate. |
| T-SAFD (SA-FirstDivision, line 23.5, n=214) | 24.9 (SA-port engine) | Not stated | A/B/C lose naive by ≈0.012 (0.677011 / 0.676045 / 0.676726 vs 0.664171) | **EXCLUDED.** The coordinator's verifier note adjudicates the candidate's port mismatches (ladder, half split 0.4559 vs 0.4557 — also a §5.5-class latent instance, "never used"; baseline definition; per-match updates) and concludes: "FAIL is robust under every reading… models beat both [baseline readings] either way… still fail by ~0.012 LL against the naive." A ~0.012 margin plus an explicit robustness certification leaves no plausible M_BAR rescue; its §5.10-family defect (both-pass selection at 24.5 vs frozen 23.5, bugs_batch10) is latent virgin-stage code that never ran. |

**§5.9 survivors: 3 — T-CA, T-HU-NBI, T-AUW.**

### 2.3 §5.1 / §5.5 — halves-split literals (FIXED, commits ca1da555 / 80c06162; HR instance b1942096)

AUDIT §5.1 adjudication is categorical: the divergences sit "in the
build-time virgin-predictions writers (presentation-only halves
columns; FT columns and every verdict unaffected — gates score FT)".
AUDIT §5.5, of the second sweep: the two realised instances are the
PASSING goals markets SCO (virgin lam split 0.412 vs frozen 0.4405)
and TR (0.412 vs 0.4403); "every other instance was latent (the
market failed before any virgin write) or in an unshipped writer",
and §2 cause 7 summarises the class as acting "without deciding any
verdict".

| Screened candidate | In Lane 1? | Disposition |
|---|---|---|
| §5.1: C-AR, C-AUW, C-TR, C-BRB (all PASS_PROV), T-BR (PASS_PROV), T-PL (FAIL at sealed) | No | Out by outcome — none is a dev fail. |
| §5.1: G-CY (CY goals, HALF_SPLIT 0.4542 vs frozen 0.4563) | Yes — dev, OU_LL | **EXCLUDED.** Presentation-only halves literal; the dev FAIL is the FT OU2.5 leg (0.7302 vs 0.6989), which no halves constant enters. §5.1: "every verdict unaffected". |
| §5.5 "probability correct, written lambdas wrong": G-BRB, G-NL, G-CZ, G-RO | Yes — all dev fails | **EXCLUDED.** By the audit's own sub-pattern definition the FT probability computation was correct; only exported 1H lambdas were wrong, and no virgin artefact was ever written (dev fail). G-NL carries an additional, separate disqualifier: its verdict records that the harness fallback computed Gate Zero on the sealed window and concludes the "2025/2026 window should be considered burned for G-NL purposes" — G-NL is in the inventory mechanically but is NOT Lane 1-eligible in substance (flagged for the coordinator; it was not a cohort-A candidate and is not recommended anywhere in this report). |
| §5.5 "both wrong": G-AU, G-DK, G-ENGCH, G-ES, G-SE2, G-KR, G-DE3, G-NLE | Yes — all dev fails | **EXCLUDED.** "Both" = the 1H probability computation and the written lambdas — both are halves (presentation) quantities. The goals gate legs (1X2 LL, RPS, OU2.5 LL) are FT quantities and do not consume the halves split; §5.5 adjudicates every non-passing instance latent and §2 cause 7 states the class decided no verdict. (G-SE2 is independently confirmed by its verdict to fail "on Gate Zero's own legs" with its X2 arm inert.) |
| §5.5 passing pair: G-SCO, G-TR | No — PASS_PROV | Out by outcome (the realised instances; shipped artefacts, not fails). |
| §5.5/§5.12: G-HR (FI halves values 0.4295/0.5705 in exported lambdas vs frozen 0.4320/0.5680) | Yes — dev, OU_LL | **EXCLUDED.** bugs_batch06 adjudication: "dormant because G-HR failed dev" — the literal lives in the virgin exporter that never ran; dev legs are FT. |
| §5.5 also-fixed: C-BR corners complement (sealed fail), K-BR cards writer ladder/loop mismatch | No / Yes (K-BR) | C-BR out by outcome. K-BR: the writer defect is virgin-artefact code; its dev disposition is already recorded in §2.1. **EXCLUDED.** |

**§5.1/§5.5 survivors: 0.**

### 2.4 §5.10 — eligibility helpers (FIXED, commit 62800ae2)

| Candidate | In Lane 1? | Disposition |
|---|---|---|
| T-CY (CY total shots): `run_t_cy.py` computed virgin eligibility (best-baseline min, reference selection, sign check, leg (i), ship selection, persisted primary_line) at 17.5 vs frozen 18.5 | No — PASS_PROV | Out by outcome. Also certified neutral on its own terms: "the verdict's numbers match the JSON's 18.5 ladder to 6dp, and at 17.5 arms B (0.684573) and C (0.685886) still lose leg (i) to A (0.684430) — the eligible set is {A} under both lines." |
| Eligibility-helper family from bugs_batch*.md, screened for completeness: G-PBM (sign check inserted into `dev_gate_pass`, making a sealed-stage leg a dev eligibility condition) | Yes — dev | **EXCLUDED.** bugs_batch01 adjudication: "current X2 already fails dev metrics" — the stricter helper changed no dev outcome; Gate Zero's own dev legs fail independently. |
| S-TH (TH SOT): `choose()`/calibration aliases at 7.5 vs registered primary 9.5 | Yes — dev, OU_LL | **EXCLUDED.** bugs_batch11 adjudication: "dormant sealed function" — the wrong-line code sits in the never-executed sealed path; dev numbers were computed at the correct line by the dev path. |
| T-SAFD selection-at-wrong-line | Yes — dev | Already disposed in §2.2 (latent, never ran). |

**§5.10 survivors: 0.**

### 2.5 What a corrected dev evaluation requires (the 3 survivors)

Common requirements: (1) derive M_BAR from the candidate's OWN dev
rows (all loaded dev-era rows, the §5.9 intended definition) and
state it in the fresh prereg — enforced mechanically by the
gate_lib derived-constant checker (P5), never copied from a template
or a sibling league; (2) re-run the DEV evaluation only, under
`league/gate_lib/`, with the P2 design seal on all artefacts and P6
worst-fold reporting; the sealed window is not touched until the
corrected dev gate passes; (3) because arm A never touches M_BAR,
its dev FAIL reproduces exactly under corrected code — so, exactly
as in cohort A, the fresh prereg must state the method difference in
advance: the M_BAR-corrected arm (B and/or C, named per candidate
below) is designated the arm of record, Gate Zero/arm A is retained
as a baseline only, and the remaining gate legs are the original
prereg's, unchanged; (4) one sealed read, verdict final.

Per survivor:
- **T-CA:** set M_BAR = 22.8326 (the value its own harness already
  computes from the loaded rows — the corrected evaluation is, in
  code terms, wiring that derived value into `model.py`'s
  LevelLayer/TrailingR in place of the copied 24.15). Arm of record:
  C (E9 trailing-r — the M_BAR-reading arm with the 0.0009 binding
  margin), with corrected B also reported. Dev gate re-checked at
  22.5 against both baselines (base 0.696515, naive 0.686318 — the
  baselines do not read M_BAR and stand as recorded).
- **T-HU-NBI:** set M_BAR = 19.0425 (prereg-documented dev mean).
  The corrected evaluation must fix BOTH audit findings in the same
  run: the M_BAR prior AND the §5.12 baseline defect (the "naive"
  baseline must be a true trailing-10, not arm B's blended
  probabilities — otherwise B's dev comparison is vacuous by
  construction). Arms of record: C (best recorded dev LL, 0.7035)
  and corrected B, both reported; binding leg is the true base rate
  (0.6956). Note the HU family's recorded warning (§5.12): persisted
  HU `results_dev.json` gate flags omit the per-season leg — the
  corrected evaluation must apply the full frozen legs via gate_lib,
  not the flags.
- **T-AUW:** derive M_BAR from the league's own dev rows at fresh
  preregistration (no frozen league value exists; the derivation
  rule — pooled mean of total shots over the loaded dev rows — is
  stated in the prereg and checked by gate_lib). Arms of record: B
  (level layer) and C (trailing-r), both reported; binding baseline
  is naive trailing-10 (0.696919). Dev n is modest (369) and the
  corrected margins are expected to be small in either direction —
  the dev re-check is the gate, and if neither corrected arm beats
  both baselines on dev, the candidate dies there and the window
  stays unread.

---

## 3. Recommended wave-1 list (12)

Design note column abbreviates §1.5 (cohort A) / §2.5 (cohort B);
the full design paragraphs there apply verbatim to every row.

| # | Candidate | Cohort | Arm of record | Sealed window (one read) | Design note / caveat |
|---|---|---|---|---|---|
| 1 | K-COA | A | X8 referee | 2026 – Apertura (n=204) | Referee shipping caveat (§1.4). Strongest cards trait support (r=0.487, coverage 95.4%). |
| 2 | K-FO | A | SHRINK | 2026 (n=135) | Thin dev edge (0.0014) — expect the dev re-check under gate_lib to be the real test; no referee input. |
| 3 | K-ID | A | X5 blend | 2025/2026 (n=306) | events_complete scoring only; no referee input. |
| 4 | K-NO-OBOS | A | X8 referee | 2026 (n=240) | Referee shipping caveat. Largest clean X8 dev margin in the cohort (−0.0130 vs base, −0.0176 vs naive). |
| 5 | K-PE | A | X8 referee | 2025 (n=323) | Referee shipping caveat; historical coverage declining (80.5% in window). Largest variant-vs-GZ gain (−0.0252). |
| 6 | K-SE | A | X8 referee | 2025 (n=240) | Referee shipping caveat; coverage incomplete (84.6% in window). |
| 7 | K-US | A | X8 referee | 2025 (n=540) | Referee shipping caveat. Sign check 2/3 on recorded dev seasons — leg (iii) is live, not a formality. |
| 8 | C-PY | A | X7 touches | 2026 – Clausura (n=112 at pull) | Window was transitional — fresh prereg must re-pin the completed window and n verbatim before the read. |
| 9 | G-TZ | A | SHRINK | 2025/2026 (n=239) | Three-leg goals gate; leg (i) reference substitution pinned in the fresh prereg (§1.5). OU margin thin. |
| 10 | T-CA | B (§5.9) | C (corrected M_BAR = 22.8326), B reported | Window per original T-CA prereg (unread; pin verbatim at fresh prereg) | Binding dev margin 0.0009 — the corrected dev re-check decides; window untouched if it fails. |
| 11 | T-HU-NBI | B (§5.9 + §5.12) | C and corrected B (M_BAR = 19.0425, true naive baseline) | 2025/2026 (unread; pin verbatim at fresh prereg) | Both defects fixed in one corrected run; widest binding gap (0.0079 vs base). |
| 12 | T-AUW | B (§5.9) | B and C (M_BAR derived from own dev rows) | Window per original T-AUW prereg (unread; pin verbatim at fresh prereg) | Weakest documentation of the three — derivation rule stated in the prereg and machine-checked. |

Ordering note (for the coordinator, not a gate): within cohort A,
K-PE / K-NO-OBOS / K-COA carry the largest variant margins; K-FO and
G-TZ the thinnest. Within cohort B, T-CA is the tightest case and
T-HU-NBI the largest-distortion case. No ordering changes any gate.

## 4. Conditional / excluded items the coordinator should rule on explicitly

1. **K-TR (cohort A, spoiled window)** — excluded from wave 1
   (§1.3). Eligible only on the completed 2026/2027 window under a
   fresh prereg (later wave). Its X8 dev evidence (0.686474, sign
   3/3) is the joint-strongest in the cohort, which is exactly why
   the spoiled window must not be laundered into a verdict.
2. **K-AT (AT-Bundesliga cards) — an 11th variants-moot case, found
   during §5.6 screening, NOT named in AUDIT §2 cause 4.** Its
   verdict documents the identical shape: Gate Zero 0.6654 loses to
   naive 0.6636; X8 0.6561 beats both baselines (base 0.6803, naive
   0.6636); "the virgin window is NOT read… season 2025/2026 remains
   unread by this candidate"; referee coverage ≥82% in dev, 91.8%
   in the window; the verdict calls X8 "the standing diagnosis for
   any future prereg". It is in the Lane 1 inventory (dev, OU_LL,
   virgin n=195). If the coordinator accepts verdict-documented
   mootness as equivalent to §2 listing, K-AT joins wave 1 under the
   §1.5 design (X8 as arm of record, referee shipping caveat) and
   the wave becomes 13. This report does not count it, because the
   task's cohort A is the §2-named 10.
3. **K-BR (BR cards) — moot on dev, spoiled in effect, and would
   have failed anyway.** X8 beat both baselines on dev (0.682996 vs
   0.686601 / 0.689992), but the harness mechanically computed X8's
   virgin metrics before the gate was applied by hand, and the
   verdict records they fail leg (i) (virgin LL 0.697206 vs base
   0.690470, naive 0.692264). Not a Lane 1 candidate in substance:
   the window has been computed and the variant loses on it. Not
   recommended for any wave on this window.
4. **K-MX (MX cards) — §5.13 recorded deviation, outside the four
   named cohort-B classes and never audit-fixed.** PREREG_K_MX
   freezes r=112.39 for scoring; the harness estimated r from
   warm-up (recorded model r 14.31). AUDIT §5.13: "K-MX fails at dev
   under the as-run numbers; unlike NL-EersteDivisie, the verdict
   does not verify the outcome under the frozen r, so the audit
   records this as one of the two deviations where a corrected
   re-run cannot be certified from documents alone." K-MX is in the
   Lane 1 inventory (dev, OU_LL; GZ fails both baselines, X8 beats
   naive but loses base; late-dev referee coverage collapses to
   24.8%). On the merits it is the strongest uncertified-dev case in
   the audit — but admitting it requires a coordinator ruling that
   cohort B extends to §5.13 recorded (unfixed) deviations, with the
   corrected dev evaluation run at the frozen r=112.39. Not counted
   in the 12.
5. **Extension screening, excluded with certification** (for
   completeness of the §5 sweep): K-NLE — baseline/r definitions
   deviate from prereg, but "both verdicts verify the FAIL survives
   the frozen definitions" (§5.13); C-NL — verdict uses the frozen
   constant baseline (0.7014) rather than the harness's NB baseline
   (0.7218), so the recorded FAIL stands on correct numbers — and
   its window was additionally burned by the fallback sealed read
   (same flag as G-NL, §2.3); S-FI's §5.12 wrong-window baselines are
   a sealed-stage item (baselines scored on 2025 rows against arms
   scored on the 2026 sealed window) — not a dev fail, and §5.12
   adjudicates "FAIL unaffected"; S-COA's §5.12
   baseline definition is non-binding and the candidate PASSes;
   MA-BotolaPro's pre-era leakage (§5.13) touches two sealed fails
   that "fail on their own legs regardless". None is recommended.

## 5. Method and limits

- All dev numbers are quoted from verdict artefacts and
  cross-checked against `results_dev.json` where the file exists in
  the league tree (T-family numbers above are taken from the
  persisted dev JSONs directly). No engine was re-run; no sealed
  artefact was opened. (The spoiled K-TR / K-BR / G-NL sealed figures
  quoted here are the figures the verdicts themselves disclose in
  their transparency sections — no sealed file was read by this
  analysis.)
- Cohort B's survivor test is deliberately strict: an audit
  neutrality/robustness certification for the screened bug excludes,
  and a survivor needs both a documented wrong constant on the
  failing arms and a binding margin small enough for the distortion
  to plausibly matter (T-CA, T-AUW) or a distortion so large that
  plausibility does not turn on the margin (T-HU-NBI, +5.86 shots on
  a 19.04 mean). Whether a corrected dev run actually passes is
  exactly what the corrected dev evaluation in §2.5 exists to
  determine — this report asserts plausibility, never a result.
- Nothing in this report writes a preregistration, moves a gate, or
  re-passes any candidate. Wave-1 entry still requires, per
  candidate, a fresh preregistration committed before its window is
  read (charter, Lane 1).
