# Final Audit Brief — league program (Codex gpt-6.1-sol pass)

User directive, 2026-11-11 01:15 WIB. This brief binds the final audit
pass that produces league/AUDIT.md after the last runner join lands.

## Scope 1 — bug audit (as originally planned)

- Read the verdicts + engines across the league tree; fix only clear
  bugs, each with a re-test. Everything else becomes a proposal.
- Sol is used ONLY for this pass; implementation stays on luna.

## Scope 2 — root-cause diagnosis of small-league gate failures (NEW)

The audit MUST explain, with evidence, why so many markets in small
leagues fail the gates or are not buildable at all. Required method:

1. Classify EVERY failed / not-buildable candidate in the program by
   its failing point, from the prereg + verdict files:
   - not buildable (which input is missing: stats feed, xG, referee,
     fixtures) and since which season the input exists at FotMob;
   - dev-gate failure (which leg: LL/RPS vs baseline, OU leg);
   - sealed-window failure (LL leg vs calibration leg), with the
     breach size vs the 1 SE band.
2. Cross-tabulate by market (G/S/C/K/T) and by league size (matches
   available for fitting, seasons of stats coverage).
3. Separate the mechanisms — do not lump them into "model bad":
   - data absence (feed coverage) vs data thinness (few matches);
   - small-sample calibration noise: how many sealed calibration
     failures fall within 1–2 SE of passing, i.e. would flip on a
     handful of matches;
   - genuine misspecification: recurring patterns (thin-team extreme
     lambdas at season openers, promotion/relegation churn, frozen
     constants transferred from big leagues, era drift).
4. Rank the causes by how many markets each one killed, with counts.
5. AUDIT THE EDA STAGE ITSELF (user hypothesis, 2026-11-11 01:21):
   for every candidate that PASSED the dev gate but FAILED the sealed
   window, reopen that league's EDA artefacts (analysis/, charts/,
   the design doc) and judge, with evidence, whether the failure
   mechanism was already visible at EDA time — borderline split-half
   reliability waved through, correlations that flip sign or collapse
   between seasons, thin slices treated as solid, era drift visible
   in the charts — or whether it was genuinely not visible then.
   Report the split: "EDA missed it" vs "EDA could not have seen it",
   per market, with named examples both ways. Where the EDA method
   itself is at fault (how the data was viewed, which correlations
   were trusted), say so plainly and name the methodological fix.
   Scope limit: this test only applies to dev-pass/sealed-fail cases;
   not-buildable markets had no data to analyse and dev failures were
   caught before the sealed window — neither counts as EDA evidence.
6. End with concrete, costed proposals (data pulls, gate design for
   small-n leagues, shrinkage/prior changes, EDA method changes) for
   a FUTURE program.

## Reference benchmark — how professional football analytics works

(User request, 2026-11-11 01:23: compare our EDA/data method against
expert practice; data-rich leagues also lost many markets at the
sealed window, so method — not just data volume — is in question.)
The EDA self-audit (Scope 2, item 5) must benchmark our method
against the practices taught in:

- Soccermatics / Mathematical Modelling of Football (Uppsala,
  David Sumpter; materials free at soccermatics.readthedocs.io) —
  event-level data handling, xG fitting, distributions, ML; taught
  with club practitioners (Liverpool, Man City, Barcelona alumni).
- Friends of Tracking (YouTube/GitHub) — event + tracking data
  processing pipelines from club data scientists.
- StatsBomb Academy + StatsBomb open data — provider-side xG/data
  methodology.
- Dato Fútbol advanced track — production ML pipelines, custom
  xG/xT/VAEP models on StatsBomb/Wyscout data.
- Validation literature: time-series cross-validation for football
  models; time-aware validation / anti-overfitting practice
  (preprocessing fitted INSIDE folds only, calibration fitted on
  inner slices, never on the test fold).

Differences the audit must specifically check in our method:
(a) our EDA works on match-level aggregates; expert practice builds
    features at event level with context (game state, pressure,
    positions) — which correlations exist at one level and vanish
    at the other?
(b) whether our per-league EDA/reliability checks ever touched the
    sealed seasons (feature selection on full-sample correlations
    would contaminate the sealed test itself);
(c) hierarchical / partial-pooling estimation (mixed effects,
    shrinkage across teams and leagues) — the standard expert tool
    for thin data — vs our mostly independent per-league fits.

## Hard limits

- Diagnosis only. Gates are pre-registered and are NOT moved by this
  audit; no failed market is re-passed retroactively.
- Claims need numbers from the verdict files, not impressions.
