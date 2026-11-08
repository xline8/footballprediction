# Final Audit — World-League Program

**Status: AUDIT COMPLETE** (started 2026-11-11 01:35 WIB on the
user's direct order, ahead of the last two runner joins; completed
2026-11-11 ~05:20 WIB after a Codex quota wait, reset 04:06 WIB).
Headline: 785 candidates classified — 122 PASS (94 provisional,
28 clean), 309 FAIL (210 dev, 99 sealed), 353 NOT_BUILDABLE,
1 NOT_BUILT. Top causes: data absence (353), no edge over baselines
at dev (210), era drift at the sealed window (99; EDA had the
signals in 90 of 99 cases). 12 bug-fix commits, 59 engine files;
no verdict changed, no gate moved.
Charter: `league/AUDIT_BRIEF.md`. Benchmark study:
`league/EXPERT_METHOD_STUDY.md`.

Audited state at start: 156 leagues complete (157 league directories —
AR-PrimeraBMetropolitana and AR-TorneoFederalA share one FotMob id and
count as one league), 122 passing markets, runner 47 leagues /
100 markets. Joins still in flight at audit start (not touched by this
audit): US-USLLeagueOne (wt-runner47), SK-1Liga (wt-runner50). Any join
landing mid-audit is noted here as audited-at state, not audited.

Method: (i) mechanical skeleton extraction of all 157 config dirs ×
5 markets = 785 candidates; (ii) Codex gpt-6.1-sol classification
batches (one session at a time) reading every candidate's verdict,
prereg and design documents into a fixed schema; (iii) deterministic
sweeps across all 1,390 engine files for known bug patterns;
(iv) clear-bug fixes confined to `league/<L>/engine/`, each with a
recorded re-test. Gates are pre-registered and were NOT moved by this
audit; no failed market is re-passed. Every number below traces to a
verdict, prereg or design file.

## 1. Failure classification — every candidate accounted for

All 785 candidates (157 league directories × 5 markets; the programme's
156 leagues — AR-PrimeraBMetropolitana and AR-TorneoFederalA share one
FotMob id) classified from their own documents. Machine-readable rows:
`league/audit_scratch/class_batch*.jsonl` (schema-validated, 12 batches).

| Outcome | Count | Share |
|---|---|---|
| NOT_BUILDABLE | 353 | 45.0% |
| FAIL | 309 | 39.4% |
| PASS (provisional) | 94 | 12.0% |
| PASS (clean) | 28 | 3.6% |
| NOT_BUILT (deliberate hold) | 1 | 0.1% |

The 122 passes reconcile exactly with the programme ledger's 122
passing markets. Failing point of the 309 FAILs + 353 not-buildables:
dev gate 210, sealed window 99, not-buildable 353, held 1 (T-FI,
feasibility).

**By market** (fail points dev/sealed/not-buildable; pass rate of
built candidates):

| Market | dev | sealed | NB | passes | pass rate of built |
|---|---|---|---|---|---|
| Goals | 135 | 13 | 5 | 4 | 4/152 = 3% |
| SOT | 13 | 23 | 88 | 33 | 33/69 = 48% |
| Corners | 7 | 22 | 88 | 40 | 40/69 = 58% |
| Cards | 49 | 15 | 81 | 12 | 12/76 = 16% |
| Total shots | 6 | 26 | 91 | 33 | 33/65 = 51% |

Goals is buildable almost everywhere (scores always exist) and fails
almost everywhere — 148 of 157 goals candidates failed, 135 of them at
the dev gate. The counting-stat markets invert: they die on data
absence (81–91 not-buildable each) but pass at 48–58% when built.

**By data depth** — the master gradient of the whole programme:

| Stats seasons | candidates | passes | pass rate |
|---|---|---|---|
| 0 | 375 | 3 | 0.8% |
| 1–3 | 75 | 2 | 2.7% |
| 4+ | 330 | 116 | 35% |
| unstated | 5 | 1 | — |

**Not-buildable causes** (nb_missing): stats feed absent/null in the
payloads 248; no gateable dev/sealed window 63; scores-only source 38;
other 4. Every one of the 353 rows carries payload-level numeric
evidence (e.g. "Periods.All null in all 1,311 payloads") — the audit
specifically re-checked the known warehouse defect (the index
`has_stats` flag tests key presence, not non-null stats; TH-ThaiLeague2
payloads are null in 681/681 files while flagged present) and found
**no** not-buildable verdict resting on the flag alone.

## 2. Ranked root causes

Two layers. First, where candidates died is §1. Second, *why* — the
mechanisms recorded on the 309 FAIL rows (multi-tag; a dev-gate fail
is near-definitionally "lost to a baseline", so the proximate leg and
the underlying mechanism are reported separately):

Proximate legs: OU/LL dev legs 199; sealed LL 68; sealed calibration
59 (+9 OU, +2 1X2); dev 1X2 LL 49 and RPS 47 (the goals model's
1X2/RPS legs); sign check 24.

Underlying mechanisms (tags on FAIL rows): era drift 121;
feature failure 106; level misspecification 69; thin data 63;
small-sample noise 62; mover churn 16; gate architecture 10.

**Ranked causes, with the brief's three families separated:**

1. **Data absence — 353 candidates (45%).** Not a modelling failure
   at all: the FotMob stats feed is absent or null for most of the
   world's smaller leagues (248), or only scores exist (38), or the
   stats era leaves no gateable window (63). Nothing in model design
   reaches these; only a scores-only model family (P3) or a richer
   feed does.
2. **No edge over simple baselines on dev data — 210 candidates.**
   The dominant *modelling* cause, and it is market-shaped: goals
   (135 dev fails — the Dixon-Coles programme, even market-blended,
   adds nothing over climatology in most leagues) and cards (49 —
   the referee-less Gate Zero is weak, see cause 4). For SOT/corners/
   total-shots the same gate killed only 26 candidates combined.
3. **Era drift at the sealed window — 99 candidates.** Of the 221
   candidates that passed dev, 99 (45%) died in the sealed window;
   for goals the conversion was 13 of 17 (76%). Calibration legs
   account for 70 of the 99. The level a model learned in the dev era
   simply was not the level of the sealed season — the mechanism the
   expert study predicted from the admission test's blindness (§4d).
4. **Gate architecture (variants-moot) — 10 documented candidates.**
   A variant beat both baselines on dev but was never read because
   Gate Zero failed: CO-PrimeraA K, FO-PremierLeague K, ID-SuperLeague
   K, NO-OBOSLigaen K, PE-Liga1 K, SE-Allsvenskan K, TR-SuperLig K,
   US-MLS K, PY-DivisionProfesional C, TZ-PremierLeague G. Eight of
   ten are cards, where the blocked variant is the referee arm — the
   one variant carrying genuinely new information. Small in count,
   systematic in kind; the rule was frozen and applied as written
   everywhere, so this is a design cost, not an execution error.
5. **The coin-flip zone — small-sample noise.** Sealed calibration
   breaches: median 1.57 SE; 52 of 70 within 2 SE; only 6 beyond
   3 SE. Symmetrically, 94 of the 122 passes are provisional. A large
   share of the programme's marginal verdicts — in both directions —
   are within noise of the line the gates draw; the gates knew this
   (hence the provisional category) and the audit confirms the
   category is doing heavy work.
6. **Thin samples within built candidates** (thin data 63 tags):
   one-stats-season leagues whose dev windows are a few hundred
   matches; their trait estimates are noise-dominated (the §1 data-
   depth gradient is the same fact seen from the other side).
7. **Transferred constants** (audit-found; verdicts rarely name it):
   the M_BAR class (§5.9) and the halves-split class (§5.1/§5.5) —
   template constants from J1 or a sibling league silently standing
   in for the league's own. Counted separately because classification
   tags understate it: it distorted arm B/C gate numbers in dozens of
   total-shots engines and shipped halves splits in two passing
   goals markets' artefacts, without deciding any verdict.

## 3. EDA self-audit — dev-pass / sealed-fail cases

For all 99 candidates that passed dev and failed in the sealed
window, the audit reopened the league's EDA and design documents and
judged whether the failure mechanism was visible at design time
(spot-verified against source documents by the auditor; citations in
the classification rows):

| Judgement | Count | Share |
|---|---|---|
| EDA missed it (signals were in the EDA) | 53 | 54% |
| Mixed | 37 | 37% |
| Could not have seen it | 9 | 9% |

**The user's hypothesis is largely confirmed.** In 90 of 99 cases the
mechanism was at least partly visible at EDA time. The recurring
pattern is not misread correlations — the trait reliabilities were
mostly honest — it is **level drift printed in the EDA's own tables
and designed around**: AE-ProLeague S/C (EDA F1: SOT 9.61 → 9.06,
corners 10.60 → 9.54 across dev, sealed row 8.18/9.15 in the same
table; the design kept a decayed-level architecture with no
level-break treatment); AR-LigaProfesional S/K/T (EDA identifies the
2025 format break and the hot sealed context explicitly; HL270
frozen anyway); CH-ChallengeLeague C (EDA F1 "explicitly flags
corners 9.99 → 8.49 as calibration problem"; trait-rating design
retained); BR-SerieA C (corners easing 11.01 → 10.57 → 10.16 in F1);
AT-2Liga C/T, AT-Bundesliga S/C/T, BE-FirstDivisionA G — the same
shape. Because the EDA stage inspected all seasons (§4b), several of
these workbooks literally contain the sealed season's level; the
designs saw the drift and the architecture had no sanctioned way to
respond to it.

The genuine could-not-see cases (9) are level breaks with no dev-era
precursor: BR-SerieB T (dev shots stable 25.8–26.5 across four
seasons; the sealed rise is absent from dev), CH-ChallengeLeague T
(stats-era shots consistent at 25.61/25.30; sealed 27.01), and seven
more of the same kind. No EDA reading, however careful, catches a
break that has not happened yet — the defence against those is
architectural (P1/P4), not analytical.

## 4. Benchmark vs expert practice

Checked against `league/EXPERT_METHOD_STUDY.md` (the commissioned
comparison with published football-analytics practice) and verified
against this audit's own evidence:

**(a) Event-level vs match-aggregate features.** The gap is real but
bounded, and mostly not actionable here: event/shotmap data exists
only for the top-5 and J.League corpora in this warehouse. The
programme's aggregate-feature design matches what the data supports
for ~155 of 157 leagues. No finding.

**(b) Did EDA/reliability ever touch the sealed seasons? YES —
structurally.** J1's design document states EDA inspected aggregates
across ALL seasons including the sealed one, and the pattern was
inherited: this audit directly observed sealed-season level rows
inside EDA workbooks (e.g. AE-ProLeague's EDA table contains a row
labelled "2025/2026 (virgin)"; AR-LigaProfesional's EDA quotes the
sealed context explicitly). The sealed windows were fit-sealed and
read-once for scoring, but they were **not design-sealed**: level
regimes that later failed calibration were, in several leagues,
printed in the design documents themselves (§3). This is the single
largest methodological divergence from expert practice found.

**(c) Hierarchical/partial pooling vs independent per-league fits.**
The programme fits each league independently with asserted shrinkage
(fixed ridge λ, fixed priors, hand-set constants — and, per §5.9, in
one component a constant copied from another league entirely).
Expert practice estimates variance components from data. The audit's
failure census is consistent with the cost: thin leagues' ratings
are either over-shrunk toward wrong levels or under-shrunk into
noise, and there is no cross-league borrowing for the large share of
candidates that died on data absence/thinness. Candidate remedy is
§6 proposal P3 — it is also the only expert-study candidate that
reaches scores-only leagues.

**(d) Reliability measurement.** The admission test used career-pooled
split-half reliability on random splits — it measures the wrong kind
of stability (within-era consistency) and is blind to level shift
between eras, which §2 shows is the dominant sealed-window killer.
The expert study's proposed replacement (a time-ordered
forward-stability leg) is §6 proposal P1.

**(e) What matched expert practice.** Pre-registration with frozen
gates; read-once sealed windows for scoring; walk-forward dev
protocol; baseline discipline (every candidate must beat a base rate
and a naive tracker); calibration judged with its standard error
rather than as a point estimate; mechanical ship selection. The
gate *architecture* is sound — the failures are concentrated in what
the gates were fed (design-seal, admission test, asserted shrinkage),
not in gate discipline. No gate was found to have been moved after
results were seen; §5's divergences are code-vs-prereg mismatches,
each adjudicated, none applied retroactively.

## 5. Bugs found and fixed

**Tally: 12 fix commits, 59 engine files corrected** (plus
documentation-only corrections in AUDIT.md itself and the CL engine
READMEs). Every fix was adjudicated against its candidate's verdict
before being applied: each is either in a path the verdict did not
use, or verified outcome-neutral from persisted artefacts (the
arithmetic is shown in the relevant subsection). No fix changes any
recorded verdict, and no gate was re-run. Two deviations could not
be certified outcome-neutral from documents alone (AR cards baseline
definition, §5.8; MX cards fixed-r, §5.13) — both are recorded, not
repaired into a different history.

### 5.1 Halves-split constants diverging from the frozen prereg (FIXED, commit ca1da555)

Deterministic sweep of every hard-coded half/share literal in all
league engines against each league's frozen `halves_constants`
(config.yaml, mirrored from the prereg): 103 literals checked. Seven
divergences, all in the build-time virgin-predictions writers
(presentation-only halves columns; FT columns and every verdict
unaffected — gates score FT). Verified in the archived artefacts
themselves (median mu_1h/mu in the shipped virgin CSVs):

| League / market | Engine literal | Frozen constant | Archived CSV evidence |
|---|---|---|---|
| AR-LigaProfesional corners | 0.462 | 0.480 | mu_1h/mu median 0.4620 (n=240) — the instance the ledger had already flagged |
| AU-ALeagueWomen corners | 0.452 | 0.480 | 0.4520 (n=110) |
| TR-SuperLig corners | 0.447 (= J1's constant, template residue) | 0.4801 | 0.4470 (n=306) |
| BR-SerieB corners | 0.474 / 0.512 (pair sums to 0.986) | 0.472 / 0.528 | 0.4740 / 0.5120 (n=380) |
| BR-SerieA total shots | 0.463 / **0.530** (pair sums to 0.993) | 0.463 / 0.537 | pred_total_2h ratio 0.5300 (n=380) |
| PL-Ekstraklasa total shots | 0.456 / 0.544 in `fitted_params_virgin.json` writer | 0.4592 / 0.5408 | params file not on disk at audit time; source-vs-prereg divergence verified in code |
| CY-1Division goals | HALF_SPLIT 0.4542 | 0.4563 (EDA-frozen) | code-vs-EDA divergence verified in source |

Fix: each literal replaced by the frozen constant (complement to
1.0). Re-test: `py_compile` passes on all edited files; the full-tree
re-sweep (two independent matchers) now reports **0 divergent
literals out of 103**. The archived virgin CSVs are historical
artefacts and were deliberately NOT rewritten — the record of what
was scored stands; the runner never used these harnesses (it follows
the prereg constants itself).

### 5.2 CL-LigaDePrimera engine READMEs — wrong primary lines (FIXED, commit ca1da555)

Docs-only defect (already recorded in the ledger): the four engine
READMEs carried stale template primary lines. Corrected to the
prereg-governed values — SOT 7.5 → **8.5** (ladder 7.5/8.5/9.5),
corners 8.5 → **9.5** (ladder 8.5/9.5/10.5), total shots 15.5 →
**25.5** (ladder 24.5/25.5/26.5) — plus a fourth instance the ledger
had not recorded: cards 4.5 → **5.5** (ladder 4.5/5.5/6.5, prereg
PREREG_K_CL gate at 5.5). Engines, verdicts and virgin CSVs always
agreed with the preregs; only the READMEs lied.

### 5.3 CY-1Division cards harness — stale cross-league comment (FIXED, commit ca1da555)

Comment in `engine/cards/harness.py` read "Frozen BG half split
(0.3183)" — a Bulgaria template residue in the Cyprus engine. CY's
frozen cards half constant is 0.3693 (prereg). Comment-only; the code
writes FT-only predictions. Corrected.

### 5.4 Findings recorded, NOT fixed (outside the fix scope or not code bugs)

- **World index `has_stats` false positive** (ledger-flagged,
  TH-ThaiLeague2): the warehouse index tests key presence
  (`"All" in periods`), not non-null stats; TH2 payloads carry a
  null-valued stats key in 681/681 files, so real coverage is 0.
  The index lives in `data_enrichment/`, outside this audit's fix
  scope (`league/<L>/engine/` only). Whether any feasibility verdict
  rested on the flag alone is checked in §1/§2.
- **KR-KLeague3 dev file naming**: `predictions_dev.csv` instead of
  the program-norm `results_dev.csv` — naming only, data present.
- **TZ-PremierLeague / NI-Premiership**: dev-fail leagues ship no
  `results_virgin.json` marker; the virgin-not-read state lives in
  the verdict text and the harness guard only. Process note, §6.
- **AR-LigaProfesional prereg calibration-leg wording** (literal
  reading "provisional iff |diff| ≤ 0.01 + SE") implemented in one
  harness but never exercised (virgin unread). Recorded for §6.

### 5.5 Halves-split literals, second sweep (FIXED, commit 80c06162)

A short-form multiplier sweep (`* .412` / `*.383` shapes the first
sweep missed) found the same class in 24 more files, each adjudicated
against the league's prereg (not just its config): J1 constants
(.412/.588 goals, .448 SOT, .383 cards) or another league's value
sitting where the prereg froze the league's own. Two sub-patterns:
probability computation correct but written lambdas wrong (BR-SerieB,
NL-Eredivisie, CZ-Liga, RO-LigaI), and both wrong (AU-ALeague,
DK-Superligaen, ENG-Championship, ES-LaLiga2, SCO-Premiership,
TR-SuperLig, SE-Superettan, KR-KLeague1, DE-3Liga, NL-EersteDivisie —
the last internally inconsistent, .444 in one line and .412 in the
next). Realised in shipped artefacts for the two passing goals
markets: SCO virgin CSV lam split median **0.412 vs frozen 0.4405**
(n=228) and TR **0.412 vs 0.4403** (n=306); every other instance was
latent (the market failed before any virgin write) or in an unshipped
writer. Also fixed in this batch: BR-SerieA corners complement typo
(0.512 for 0.526, pair summed to 0.986); BR-SerieA cards writer
(fields 2.5/3.5/4.5 vs loop (3.5,4.5,4.5) vs prereg ladder
3.5/4.5/5.5, plus §5.7); AT-Bundesliga cards verdict-writer identity
(wrote `K_J1_VERDICT.md` titled "K-J1" — the artefact on disk is the
correct `K_AT_VERDICT.md`, so the defect was latent in code).
Re-test: py_compile OK; the multiplier sweep now reports **0
divergent literals tree-wide**.

### 5.6 Gate-arithmetic tokens diverging from prereg (FIXED, commit b7881d90)

Token-level divergences between harness verdict-writers / gate
runners and the frozen prereg text, each verified outcome-neutral
against its verdict before fixing:

- AR cards + AT cards verdict writers: provisional calibration test
  `|diff| ≤ .01 OR |diff| ≤ SE` instead of the prereg's `≤ .01 + SE`
  (strictly stricter; K-AR arms fail under either form — breaches
  3.95/4.95pp vs SE ≈3.2pp; K-AT virgin never read).
- AR cards sign check `≥2` of 6 blocks and AR corners `sum ≥ 2`,
  where the prereg requires at least half (≥3); verdicts reapplied
  or observed 6/6 — neutral.
- AT cards best-baseline omitted the naive baseline from the min.
- BR/BRB cards both-pass selection minimised virgin LL at line 3.5
  where PREREG_K freezes selection at LL@4.5; selection never engaged
  (no eligible arm in either league).
- BR/BRB corners sealed calibration computed at 9.5 where the prereg
  primary is 10.5; both verdicts already state the correct-line
  calibration (C-BR +3.38pp would-be-provisional, moot under its leg
  (i) LL failure; C-BRB manually corrected) — code now computes at
  10.5.
- BR cards harness stored the 4.5-line calibration under keys
  `diff_3_5`/`se_3_5` while its gate runner reads `diff_4_5` (a
  KeyError crash path); AR cards stored it under the inherited name
  `diff_2_5` (disclosed in the K-AR verdict itself). Keys renamed to
  the true line in code; archived JSONs untouched.

### 5.7 Systemic latent class — unguarded sealed-read paths (RECORDED, not fixed)

Across the twelve batches, dozens of callable paths in league
engines would read the sealed season without the prereg's dev-pass
guard (unguarded `virgin-predict` CLI branches, `passing or
[gate_zero]` fallbacks, `virgin()` variants that load sealed rows
before checking dev results, cards virgin paths in the TR/US family
that never require Gate Zero to pass, loader-level materialisation
of sealed rows in goals `dc.py` files where fits are unaffected).
In all but one case the verdict and the coordinator's verification
record that the guarded path was the one executed and the sealed
window was read exactly once or not at all — no verdict is affected.

**The one realised breach: K-TR (TR-SuperLig cards).** The unguarded
path was actually invoked: X8 (dev-passing but moot, Gate Zero having
failed dev) was read on the sealed window against the frozen rule.
The programme caught it, removed the artefacts, and recorded the
candidate as spoiled — FAIL at dev, with the disclosed sealed numbers
explicitly "not gate results". The procedural immune response
worked; the episode is nonetheless the strongest evidence for §6-P5:
a guard that lives only in procedure eventually fails once in 785
candidates.

The class is otherwise recorded here rather than patched
file-by-file: the engines are frozen build artefacts, and a blanket
patch would churn ~150 files to protect paths nobody will invoke
again. It becomes a build-checklist proposal in §6 (the guard must
live in code, not in procedure).

### 5.8 Recorded deviations inside verdicts (not code bugs)

- AR cards harness computed its dev baselines differently from
  PREREG_K_AR (NB-over of a decayed mean instead of the empirical
  prior-block over-rate; NB sizes re-estimated instead of the frozen
  r=112.39). The K-AR verdict ran on, and disclosed, the numbers
  that actually ran; the candidate fails on the virgin calibration
  leg under any of these variants. Recorded, not rewritten.
- SOT harnesses in the J1-template family return Gate Zero as the
  "chosen" arm when no arm passes, and write its predictions CSV
  "for the record only". Verdicts govern (FAIL is stated plainly);
  the shape is misleading but documented in the verdicts themselves.

### 5.9 The total-shots level prior M_BAR — J1's mean in ~45 engines (FIXED where documented, commit 62800ae2)

The T-family `model.py` (copied league to league; one header still
reads "the preregistered T-RU model") carries `M_BAR = 24.9` — J1's
dev mean total shots (24.898, per PREREG_T_J1) — as the level prior
for the level layer (arm B) and the trailing-r estimator (arm C).
About 45 of 60 T engines keep the template value verbatim; the
minority that set their own (AR 24.15, BO 30.04, CO 25.06, NL-Eredivisie
27.01, PE 19.727, US-USLLeagueOne 24.8 "frozen: dev mean"…) show the
intended definition: **M_BAR is the league's own dev mean**.

Where the league's own documents state a dev mean differing from
24.9, the constant is a documented divergence and is fixed: CH 27.44
(T_CH_VERDICT), CN 27.25 (PREREG_T_CN), CL ≈26.4 (PREREG_T_CL),
CY 18.369 (eda_numbers.json). Exposure assessment:

- Arm A (v1) never touches M_BAR. Every shipped T arm except two is
  arm A → no shipped exposure (CH, CL, CY, NO-Eliteserien, TR…).
- **CN-SuperLeague ships arm B** (the level layer). Its both-pass
  selection of B over A was by **0.0010 LL**, computed under the
  wrong prior; both arms were eligible and the pass itself does not
  depend on the selection, but the selection arithmetic did. The
  daily runner imports the league's `model.py` live, so CN daily T
  predictions also used the wrong prior until this fix (distortion
  bounded by the level-layer clamp [0.90, 1.10], cell k=50).
- SCO-Premiership ships arm B with a small divergence (data mean
  ≈25.5 vs 24.9) — recorded, not adjusted (no league document states
  a frozen M_BAR value to restore).
- For the remaining ~41 carriers, all-rows data means computed in
  this audit differ from 24.9 by >1.0 shots in at least 15 leagues
  (BG 17.4, RU-1Division 15.2, SE-Superettan 20.2, NO-OBOS 20.9,
  CY 18.2, AU 28.1…) — their arm B/C gate numbers were computed
  under the same template prior. None of those B/C arms shipped.
  Constants left as-is where no league document states the intended
  value; the class feeds §6 (template constants must be re-derived
  per league and stated in the prereg).

### 5.10 CY total-shots eligibility helper at the wrong line (FIXED, commit 62800ae2)

`run_t_cy.py` computed its virgin eligibility (best-baseline min,
reference selection, sign check, leg (i), ship selection, persisted
`primary_line`) at 17.5 where PREREG_T_CY freezes 18.5. Verified
outcome-neutral from `results_virgin.json`: the verdict's numbers
match the JSON's 18.5 ladder to 6dp, and at 17.5 arms B (0.684573)
and C (0.685886) still lose leg (i) to A (0.684430) — the eligible
set is {A} under both lines. Helper now uses 18.5 throughout.

### 5.11 Sign conventions differ by template family (recorded)

DE-3Liga's SOT/corners/cards harnesses store calibration as
predicted − actual where its preregs freeze actual − predicted;
the verdicts reverse the displayed sign and |diff| eligibility is
unchanged. BR-SerieA vs BR-SerieB corners harnesses likewise use
opposite conventions (each internally consistent, each stated in
its verdict). No fix: the conventions are per-engine historical
facts; §6 proposes one frozen convention for any future program.

### 5.12 Further adjudicated items, batches 04–06

- **FI-Veikkausliiga SOT sealed baselines scored on the wrong window
  (FIXED, commit 2768ed6d).** The harness scored both baselines on
  2025 rows while the arms were scored on the 2026 sealed window.
  The S-FI verdict used the correct-window naive (0.691100) and both
  arms lost to it — FAIL unaffected.
- **GR-SuperLeague total-shots calibration sign (FIXED, 2768ed6d).**
  The accumulator returned predicted − actual against PREREG_T_GR's
  actual − predicted, which also mis-centred its SE. T-GR is a clean
  pass on |diff| (0.638pp), which neither the sign nor the SE can
  change.
- **HU-NBI total-shots "naive" baseline is arm B (recorded).**
  `run_t_hu.py` scores the naive-trailing-10 baseline from arm B's
  blended probabilities, so B's self-comparison is vacuous and A/C
  faced a stronger-than-frozen comparator. Verified non-decisive:
  all three arms also lose to the true base rate (0.6956 vs A 0.7067,
  B 0.7058, C 0.7035 in `results_dev.json`), so the dev FAIL stands
  on the uncorrupted leg. The T-HU verdict itself had flagged the
  full-precision B ≡ naive equality without identifying the cause.
- **HU-NBI dev_pass flags omit the per-season leg (recorded).** All
  five HU harnesses flag dev pass on the pooled comparison only;
  the verdicts applied the frozen per-season improvement leg
  manually (e.g. S-HU declared FAIL on the 2024/25 sign leg against
  its own flags). The persisted `results_dev.json` flags for HU are
  therefore not safe to consume mechanically — every HU verdict
  states the full legs in text. Same family: HU cards harness still
  iterates the unregistered X8 arm the verdict says was removed
  before gating.
- **CO-PrimeraA SOT dev baseline definition (recorded).** The league
  base-rate baseline is an expanding within-dev window starting
  empty, where PREREG_S_COA freezes a pooled rate seeded by the 2021
  season. Non-binding: the gate's binding baseline is the unaffected
  naive (0.6962) and the affected baseline (0.7194) would need an
  implausible 0.034 LL improvement to bind against arms at
  0.6851/0.6855.
- **HR-HNL goals writer halves literals (FIXED, commit b1942096):**
  FI's 0.4295/0.5705 in the exported 1H lambdas vs HR's frozen
  0.4320/0.5680 used elsewhere in the same row; dormant (dev FAIL).
- Batch 04's remaining items are instances of §5.7's latent class
  (unguarded virgin-predict CLIs across DE/DK/EG/ENG/ES goals
  engines; variants-moot bypasses in corners virgin(); loader-level
  sealed-row materialisation in EC/IL goals `dc.py`, fits unaffected)
  and §5.11's sign-convention class (DE-3Liga ×3).

### 5.13 Further adjudicated items, batches 10–12

- **PY-DivisionProfesional SOT virgin naive = Gate Zero (recorded).**
  The harness's virgin naive baseline reads model probs, making leg
  (i)'s naive comparison vacuous; the S-PY verdict confirms the leg
  against the true naive and ships RS on that basis. Same family as
  S-COA (§5.12), there disclosed by its own verdict. PY's dev
  baseline also excludes the seed (expanding window from empty).
- **RU cards virgin paths ship unconditionally (latent).** Both RU
  engines' cards virgin path sets `shipped_arm` and writes params
  without testing any sealed leg; unreachable in the recorded runs
  (dev failure) and both verdicts FAIL their candidates explicitly.
  RU-1Division's copies also carry RU-PremierLeague protocol identity.
- **TH-ThaiLeague copied identities (dormant).** Sealed functions in
  three TH engines name RU-1Division/RU-PremierLeague and RU output
  filenames; all sit behind dev-fail guards that held. TH's
  not-buildable verdicts rested on payload counts (§1), not on the
  defective index flag.
- **SE-Superettan goals X2 membership defect (verdict-confirmed).**
  The X2 arm tests parent-league membership in the same season, so
  completed transitions are empty by construction and the arm was
  inert; the verdict confirms the defect and the candidate fails on
  Gate Zero's own legs.
- **MA-BotolaPro pre-era state leakage (partly disclosed).** Eight
  pre-era rows the prereg excludes update model state in the corners
  and total-shots engines; the T-MA verdict discloses its instance.
  Both candidates fail on their own legs regardless.
- **NL-EersteDivisie cards + NL-Eredivisie corners baseline
  definitions** deviate from their preregs (estimated NB sizes /
  NB-mean baselines instead of the frozen constants); both verdicts
  verify the FAIL survives the frozen definitions. §5.8 family.
- **MX-LigaMX cards fixed r (recorded, not certified).** PREREG_K_MX
  freezes r=112.39 for scoring; the harness estimates r from warm-up
  (recorded model r 14.31). K-MX fails at dev under the as-run
  numbers; unlike NL-EersteDivisie, the verdict does not verify the
  outcome under the frozen r, so the audit records this as one of
  the two deviations where a corrected re-run cannot be certified
  from documents alone. No re-run was performed; the verdict stands.
  (The other is the AR cards baseline deviation, §5.8, where the
  virgin calibration leg independently decides the candidate.)

## 6. Proposals for a future program

Proposals only — nothing here is adopted, and every test design is
pre-registered in form: hypothesis, Gate Zero, gate, and a kill rule.
Costs are in builder-days on this VM's observed throughput
(~1 league-day per league-market family in the completed program).

**P1 — Time-ordered forward-stability admission leg** (from
EXPERT_METHOD_STUDY candidate 1; addresses §2's dominant sealed
mechanism, era drift). *Design:* before a candidate's sealed read, in
addition to pooled dev legs, require the arm to beat both baselines
on the LAST dev season alone (the forward slice), not only pooled.
*Gate Zero test:* replay the rule over the 122 already-passing
candidates' persisted dev artefacts: the rule is worth adopting only
if it would have stopped ≥⅓ of the sealed calibration failures while
killing ≤10% of eventual passes. *Cost:* ~2 days (artefact replay,
no refits). *Kill rule:* if the replay shows it mostly duplicates
the pooled leg, drop it.

**P2 — Design-seal the EDA stage** (study candidate 2; addresses
§4(b)). *Design:* EDA and reliability artefacts may only be computed
on dev-era seasons; sealed-season aggregates are generated by the
coordinator after the design document freezes, and are never shown
to the builder. *Gate Zero test:* process control, not statistics —
apply to the next 10 league builds and audit the artefacts for
sealed-season contamination (target: zero rows). *Cost:* ~0.5 day
of tooling (a season filter in the EDA generator) + discipline.

**P3 — Variance-component ratings (partial pooling)** (study
candidate 3; the only proposal reaching scores-only leagues).
*Design:* replace fixed ridge/prior constants with per-market
variance components estimated on dev data (team-trait variance,
era-level variance, noise), shrinking thin leagues toward regional/
global means by estimated — not asserted — amounts. *Gate Zero
test:* offline, on 6 already-built thin leagues with persisted
artefacts (2 scores-only, 2 one-stats-season, 2 mid): pooled dev LL
must improve on the shipped Gate Zero in ≥5 of 6 with no league
worse by >0.002. *Cost:* ~5 days. *Kill rule:* Gate Zero failure
ends it; no sealed window is read for this test.

**P4 — Sanctioned recalibration arm** (study candidate 4).
*Design:* a pre-registered arm that re-fits ONLY the level
(intercept) on the most recent dev slice, competing under the same
legs; targets the level-misspecification mechanism without touching
trait structure. *Gate Zero test:* same replay protocol as P1 over
persisted artefacts. *Cost:* ~2 days. *Kill rule:* as P1.

**P5 — Guards in code, not procedure** (from §5.7/§5.12). *Design:*
a shared gate library — dev-pass assertion before any sealed load,
frozen-line/calibration/sign/baseline tokens from the prereg parsed
mechanically, template constants (M_BAR class) required to be
re-derived and stated per league, one calibration sign convention.
*Gate Zero test:* the library must reproduce every shipped verdict's
legs from persisted artefacts bit-for-bit on 10 sampled leagues
before any new build uses it. *Cost:* ~4 days. This is the cheapest
proposal and removes the audit's entire latent-bug class.

**P6 — Worst-fold dev reporting** (study candidate 5). *Design:*
every verdict reports the worst dev season's legs beside the pooled
legs (no gate change — information only, one season of the existing
sign check generalised). *Cost:* ~0.5 day. Adoptable independently.

**Explicitly NOT proposed** (per the expert study's do-not-adopt
list and this audit's evidence): tracking-data methods (no data),
high-capacity ML on match aggregates, random-split cross-validation,
any recalibration fitted on a read sealed window, reopening the
closed top-5 topics (two-stage generative SOT, half-share modelling,
lineup/absence features), and any retroactive re-passing of a failed
candidate under corrected code — the deviations in §5 change future
artefacts, never recorded verdicts.
