# Daily league runner

The runner reads `active.yaml`; a league or market absent from that file is
never run. It uses FotMob only. Each run lists every configured season once,
deduplicates match ids using the first canonical season returned by FotMob,
fetches only missing played-match `matchDetails`, rebuilds the active league's
two CSVs, predicts every remaining unplayed fixture in the current season,
then settles eligible ledger entries from the refreshed match CSV.

The exact cron command, run from the repository root, is:

```text
.venv/bin/python league/runner/run_daily.py
```

The small YAML reader in `run_daily.py` is a standard-library parser for this
runner's controlled subset (nested maps and scalar lists); PyYAML is not
available in the runtime environment.

Prediction and settlement errors are isolated per league and per market and
are written to `run_log.jsonl`. There is no fixture horizon: all remaining
current-season fixtures are predicted, so an early-season daily CSV can be
large and an off-season or international-break run can have zero or very
far-future fixtures.

The same-day daily CSV is overwritten. The prediction ledger is deduplicated
by `(market, match_id, run_date)`. Settlement uses the per-league
`predictions/settled_keys.json` JSON-list sidecar, so each ledger entry is
settled at most once. The sidecar is runtime state like the daily CSVs, the
ledgers, and the run log: it lives beside them in the working tree and is not
part of the committed runner (only `active.yaml`, `run_daily.py`, and this
README are). If the sidecar is lost, already-settled entries would settle
again on the next run; the grading ledger's
`(market, match_id, run_date)` keys make such duplicates detectable.

CSV refresh is a deterministic full rebuild of the active league only. It
reuses `build_league_data.parse_match` and `team_rows`, sorts by `(date,
match_id)`, and does not call `build_league_data.main()` because that entry
point has a hard-coded total-6228 assertion. This is intentionally a rebuild,
not a true append. Engine season filters use the season values in the CSV;
warehouse directory names use the puller's slash-to-dash convention.

The J1 configuration runs SOT, corners, and arm A total shots; each market's
engine and primary line are declared in `active.yaml`.

AU-ALeague has joined with SOT (RS), corners (gate_zero), cards
(gate_zero—the runner's first cards adapter), and total shots (arm A).

US-MLS has joined with SOT (GZ), corners (gate_zero), and total shots
(arm C), and BR-SerieA has joined with SOT (RS) and total shots (arm C).
Both are calendar-year world leagues. Their SOT engines take the runner's
`ratio_prior` argument exactly like the AU engine (200 for MLS GZ, 20000
for BR RS), and the MLS data builder's frozen build-time counts are
asserted as floors, like AU's. BR-SerieA's builder carries no frozen
count, so it needed no change. Both leagues are seasonal: at the
2026-11-09 join, MLS's only unplayed listed fixtures were its 2026
playoff slate (14, from 2026-11-20) and BR-SerieA had 41 league fixtures
left in its April–December season. In a deep off-season, when FotMob
lists no unplayed fixtures for the current season, a run for either
league simply predicts zero fixtures and settles nothing, with no error.

AR-LigaProfesional has joined with corners only, using arm `x7` (the shipped
arm in `reports/C_AR_VERDICT.md`), primary line 9.5, ladder 8.5/9.5/10.5,
halves share 0.480, 1H ladder 3.5/4.5/5.5, and 2H ladder 4.5/5.5/6.5. One
adapter fix was needed: `predict_corners`' row adapter now treats the string
`nan` as missing, mirroring the engine cores' own `load` rule, because AR's
builder writes `nan` for missing values (486 rows in `touches_opp_box_*`)
where the other builders write an empty field; without it, NaN leaked into the
territorial windows and the runner's numbers did not reproduce the harness's
X7 predictions. The change is a no-op for the corners leagues already served
(J1, DK, AU, US-MLS have no `nan` strings in the columns the adapter reads).
The corners adapter passes the arm string to the engine's own fit/predict path,
and the AR corners core's non-`gate_zero` branch is the X7 arm, using the
box-touches covariate and BBT grid. The `x7`
label is substantive: on the virgin fit window its box-touch beta fitted to
exactly 0.0, but the fit is its own — gamma and r coincide with Gate Zero's,
while Gate Zero's fit on the same window carries a nonzero big-chance beta
(0.025) in place of the inert box-touch term — so virgin predictions differ
genuinely:
pooled virgin LL is 0.6881 versus 0.6944. Running AR as `gate_zero` would
produce different numbers; the coordinator verified this numerically. One
frozen-artifact presentation discrepancy remains: the shipped virgin
predictions CSV's 1H/2H columns were written by the AR harness with a 0.462
share (the league's total-shots constant), while the prereg and verdict freeze
the corners constant at 0.480. The runner follows the prereg/verdict value,
0.480; the shipped CSV's FT columns are unaffected and reproduce exactly. AR
is a split-season world league, with Apertura/Clausura labels from 2025. Its
builder models only the group phase, excluding playoffs from the training
table by design, and now asserts its frozen counts (2,419 group matches, 45
excluded playoffs, and per-block group counts) as floors, like AU/MLS.
Unplayed current-season fixtures, including the Clausura playoff slate, are
predicted like any other league's.

CH-SuperLeague has joined with SOT (RS), corners (gate_zero), and total
shots (arm A).

SE-Allsvenskan has joined with SOT (arm `X4`), corners (arm `x7`), and total
shots (arm A). The SOT arm is the join's one new mechanic, and it needed no
adapter dispatch: `predict_sot` passes the arm string opaquely into the SE
engine's constructor, and X4's xG/shot quality-ratio mechanics (trailing-25
team xG per shotmap shot versus the league's, with a fallback to the shrunk
on-target ratio under 8 matches) live entirely in the engine's own `predict`
path, exactly as the harness drives it. The one engine change is the AU
pattern: the SE SOT `Engine` constructor now accepts the runner's
`ratio_prior` keyword (no-arg behaviour unchanged), and the configuration
passes 200. For X4 that prior only feeds the base ratio that the arm's
`qratio` then overwrites, and the coordinator verified the runner's
construction is bitwise-identical to the no-arg engine on a live fixture,
while X4 and Gate Zero genuinely differ there (exp_total 8.650 versus 9.059
for AIK–Degerfors, 2026-11-21). Corners `x7` reuses the AR-proven opaque-arm
path; on the full current history at the join its live fit is gamma 0.15,
r 1.1934, beta_bt 0.0, fit_n 1410 (the virgin fit was r 1.1962 on n 946 — the
daily fit is over all played history, as for every corners league). Total
shots arm A takes its ladder and 0.457 half split from the engine's
`fitted_params.json`, with the PREREG_T_SE half lines (1H 11.5/12.5/13.5,
2H 13.5/14.5/15.5) in configuration. SE's data builder needed no change:
its build-equality assertion held at 1,424 matches (five complete 240-match
seasons plus 224 played in 2026), and it encodes missing values as empty
fields — there are no `nan` strings in any column the adapters read
(`touches_opp_box_*` is empty on 382 early-era rows), so the AR `nan` rule
in the corners adapter is a no-op here. SE is a calendar-year league: at
the 2026-11-09 join, FotMob listed the 2026 season's final 16 fixtures
(from 2026-11-21), all predicted in the three markets, and the coordinator
recomputed all 16 fixtures per market through SE's own engines in separate
processes with every field float-exact. Once the season ends, a run
predicts zero fixtures until the next season is listed.

BE-FirstDivisionA has joined with SOT (RS) and cards (gate_zero).

ENG-Championship has joined with SOT (RS) and corners (gate_zero).

To add a league or an existing market type, add its passing configuration to
`active.yaml` when its engine layout matches. A new market type also needs an
adapter function in `run_daily.py`; configuration alone cannot define its
model math. Known limits include no odds (predictions only), corners requiring
corner counts on historical rows, and the all-current-season prediction set
described above.

World-warehouse leagues

A world-warehouse league sets `source: world`, together with `country` and
`world_league` (and its FotMob `fotmob_id`/`ccode`). Its data paths point at
the league's own CSV outputs. The optional `data_builder` selects its
league-local `data/build_data.py`; otherwise that path is the default. The
builder contract is a callable `main()` plus `INDEX` and `MAIN_REPO` globals.
The runner points both globals at this checkout before calling it, so the
builder resolves the warehouse through the worktree's symlink. J1 entries
may omit `source`; the missing value defaults to `jleague` for compatibility.

The SOT and corners adapters take arm, ladder, and halves share from the
market configuration, so any league whose engine keeps the J1 interface
can reuse them. `predict_sot` also takes the engine `div` value, ratio prior,
and 1H/2H line sets from market configuration; J1 and NL explicitly use a
ratio prior of 200, while AU RS uses 20000. Defaults preserve the old J1
values. The cards adapter accepts arms `gate_zero` and `x8`. It
re-estimates the negative-binomial `r` walk-forward with the engine's
`estimate_r` over all played history — except an engine without
`estimate_r`, which supplies its frozen dispersion as module-level `R`
(AR-PrimeraBNacional: `R` 112.39) and a two-argument `nb_over(mu, line)`
— and settles on total yellow cards. History rows read
`home_team_id`/`home_team` when present and fall back to
`home_id`/`home_name` (AR-PrimeraBNacional's builder uses the latter
spelling). The `x8` arm (first joined by AR-PrimeraBNacional) multiplies
the expected total by a referee factor built from the appointed
referee's trailing in-league record exactly as the league's frozen
engine computes it (decayed HL 270, shrunk toward the league mean with
K_REF 8, clamped to [0.8, 1.25]; factor 1.0 when the identity is unknown
or the referee has fewer than 8 priors). Referee identity is attached
to history rows only for `x8`: several `gate_zero` engines carry dormant
referee branches that activate the moment a row has a referee
(KR-KLeague1's `update()` then requires `row["kickoff_utc"]`, which the
runner never supplied), so `gate_zero` rows stay exactly as before. For
upcoming fixtures the adapter fetches the appointed referee from FotMob
matchDetails (one shared client per run; a fixture dict that already
carries a referee uses it; a failed fetch falls back to no referee and
never fails the run). `x8` output rows additionally carry `referee`,
`n_prior`, `multiplier`, `fallback`, and `fallback_reason`. Settlement
reads the match CSV's `yellow_cards_home`/`yellow_cards_away`
columns by default, but a cards market block may override the settlement
actuals with `cards_actual: [col_home, col_away]`. The override exists
because the graded target is league-dependent: AU's gate graded the
stats-feed columns (its builder's `yellow_home` IS `yellow_cards_home`),
while NO's gate graded the event-unified columns `yellow_home`/`yellow_away`
(the stats feed undercounts NO yellows — 171 of 1,407 matches disagree,
42 of them flipping the over/under outcome at the 2.5 line). Prediction
already reads `yellow_home`/`yellow_away` in both leagues; only settlement
needed the per-league columns. With `cards_actual` absent, settlement
resolves to exactly the old column pair, so existing leagues are unchanged.

A corners, SOT, or total-shots market may set `halves_share_1h: null` (key
present, value null) to declare FT-only presentation for a league whose feed
has no period splits. The adapter writes `exp_1h`/`exp_2h` and all `p_1h`/`p_2h`
fields empty and leaves the FT fields unchanged; settlement reads only the FT
fields, so it is unaffected. For total shots, the opt-in also removes the
`fitted_params.json` `half_split` requirement. An absent or numeric value keeps
the existing behavior. RU-1Division is the first corners user; BG-FirstLeague
is the first SOT and total-shots user (its join generalised the opt-in to
total shots; the SOT opt-in itself is the identical code that landed with
the CZ-Liga join, whose own SOT market is held at the operational gate —
diacritic name split; see the CZ-Liga join record below). For total shots
arm A only, a league whose `fitted_params.json` carries no `half_split` at
all (and which is not FT-only) takes the split from its market's
`halves_share_1h` config; CL-LigaDePrimera is the first user. Leagues
carrying `half_split` are unchanged.

A SOT market may also set `team_key: canonical_name` to canonicalise
team names — NFKD diacritic-stripping to ASCII — both when the engine
loads history and when upcoming fixtures are keyed, so one club
accumulates one history. CZ-Liga is the first user: FotMob's 2026/2027
feed spells six of its clubs with diacritics while every gated era is
ASCII, so without the opt-in those clubs key to 9–11 rows of history
instead of 138–180. The opt-in is inert for every league without the
key (the branch is taken only when the key is set, and canonicalisation
is the identity on ASCII names); it is not id-keying — the CZ engine
stays name-keyed by design, as gated — and the one club id with two
spellings inside the gated eras (1860: `FC Fastav Zlin`, seven
2021/2022 rows, beside `FC Zlin`) stays split exactly as gated, since
neither spelling carries a diacritic and no two gated spellings
canonicalise to one string. Gated-product invariance was proved by
replay: a canonicalised walk-forward replay of the shipped virgin
predictions reproduces them at exact 0.0 on every field under the
generation environment, and canonical-vs-raw replays agree at 0.0
under the runner's interpreter too (which differs from the shipped
file by at most 7.1e-15 on either replay — pre-existing
floating-point noise, not the fix).

NO-Eliteserien has joined with corners (gate_zero, primary 10.5, halves
share 0.473), cards (gate_zero, primary 2.5, halves share 0.317,
`cards_actual: [yellow_home, yellow_away]`), and total shots (arm A,
primary 26.5, halves share 0.465). It is a calendar-year world league
(seasons 2021–2026); at the 2026-11-09 join, 33 late-season 2026 fixtures
were upcoming. Its data builder's count assertion compares the built rows
to the world index itself (`len(rows) == len(idx)`), so daily rebuilds
needed no floor change. Corners and total-shots
1H/2H ladders come from market configuration, with the previous hard-coded
sets as defaults. The AU data builder asserts its frozen 857-match count as
a floor for daily rebuilds.
NL-Eredivisie has joined with SOT (GZ) and total shots (arm A), following
the DK world-league pattern. Its data builder uses a count floor (>= 1638)
so daily rebuilds survive new played matches. The total-shots adapter
supports arm A and the preregistered arm C. Arm C
uses the engine's fitted trailing-r dispersion and replays historical matches
grouped by fixture date: state for date D includes only matches dated before
D. Unknown sources and unknown arms are logged as errors isolated to their
league or market.

NL-EersteDivisie has joined with SOT (GZ) and total shots (arm A), both with
halves share 0.451; its data builder's frozen 2,039-match count is asserted as
a floor for daily rebuilds.

SCO-Premiership has joined with goals (Gate Zero—the runner's first goals
adapter: Dixon-Coles walk-forward refit per fixture date on matches strictly
before that date, 1X2/BTTS recorded in the daily CSV, settlement grades only
the primary OU 2.5 line from home_goals/away_goals, 1H/2H via the frozen
0.4405 share), SOT (GZ), corners (gate_zero), and total shots (arm B—the
runner's first arm-B support: the v2 level layer, league level cell from the
engine's fitted params applied over the arm-A base ensemble, replayed
date-grouped like arm C).

DE-2Bundesliga has joined with SOT only (arm RS, primary 9.5, halves
share 0.443). Its SOT engine takes the runner's `ratio_prior` argument
exactly like the AU engine (20000 for RS); no-arg behaviour is unchanged.
Its data builder's count assertion compares the built rows to the world
index itself (`len(out) == len(rows)` for league_id 146), so daily
rebuilds needed no floor change, and it encodes missing values as empty
fields (no `nan` strings in any column the adapters read). Cards (arm
X8, the program's first referee-arm ship) did NOT join: it was stopped
at an operational gate. The X8 engine reproduces its harness exactly
when the appointed referee is known (max difference 0.0 over all 306
virgin predictions), and with an unknown referee it falls back to
exactly Gate Zero by its frozen prereg rule. But the referee is not
available pre-match in the runner's data flow: the FotMob `leagues`
payload that supplies upcoming fixtures carries no referee field at
all, and `matchDetails` — fetched by the runner only for finished
matches — holds `content.matchFacts.infoBox.Referee.text` empty for
every nearest upcoming DE-2 fixture probed on 2026-11-09 (the next
matchday, 2026-11-20/21, 11 days out). The virgin gate had graded a
mostly-real X8 product: 230 of 306 virgin predictions (75.2%) carried
an active referee multiplier, 40 fell back on thin referee history and
36 on unknown identity, and X8's virgin advantage (LL@4.5 0.6734 vs
Gate Zero 0.6807) comes only from the multiplier rows. A daily run
predicting all 207 remaining fixtures would therefore ship Gate Zero
under the X8 label — a different product from the one that passed the
gate — so cards stays out until referee appointments are available
pre-match in the pull. (Its settlement would have needed no override:
the gate graded the stats-feed columns, and the builder's
`yellow_home`/`yellow_away` equal `yellow_cards_home`/`yellow_cards_away`
on all 1,629 matches, matching the runner's default cards actuals.)

KR-KLeague1 has joined with cards only (arm gate_zero, the shipped arm in
`reports/K_KR_VERDICT.md`: PASSED PROVISIONAL, virgin LL 0.6765 at the
primary 3.5 line, calibration -1.74pp within 1 SE of 3.26pp; SOT, corners,
goals, and total shots all failed their gates). Its card configuration is
primary 3.5, ladder 2.5/3.5/4.5, and halves share 0.350 — the frozen KR
constant in `config.yaml` and the shipped virgin predictions
(`mean_1h / expected_total` = 0.350 on every row). The 0.370 figure is the
SE-Allsvenskan constant that leaked into an early version of the shipped
CSV's presentation columns and was corrected before the gate verdict (see
the artifact note in the verdict file); it is not a KR value. Settlement
needs the per-market override `cards_actual: [yellow_home, yellow_away]`,
exactly as NO-Eliteserien's cards block: the K-KR gate graded the
event-unified yellow target (event feed when events exist, stats fallback
otherwise), which the builder writes to `yellow_home`/`yellow_away`,
while the runner's default cards actuals are the stats-feed columns
`yellow_cards_home`/`yellow_cards_away`. The two disagree numerically on
117 of the 1,117 matches where the stats columns are present (and the
stats columns are empty on the other 233), and 22 matches cross the 3.5
line between the two feeds; a synthetic settlement on match 3802053
(Daegu FC vs Seongnam FC, 2022-03-11; unified 3+1=4, stats 2+1=3) graded
actual_total 4.0, proving the override is what settle() reads. It is a
calendar-year world league (seasons 2021–2026); at the 2026-11-09 join,
18 late-season 2026 fixtures were upcoming (the split rounds, from
2026-11-21). Its data builder's count assertion compares the built rows
to the world index itself (`len(out) == len(rows)` for league_id 9080),
so daily rebuilds needed no floor change, and it encodes missing values
as empty fields (no `nan` strings in any column, including the cards
adapter's inputs; the cards adapter reads only `yellow_home`/`yellow_away`,
which are present on all 1,350 built matches). The runner's
`predict_cards` passes no argument the KR cards engine does not accept:
Gate Zero ignores the referee multiplier, so the runner's referee-free
history rows reproduce the harness exactly (an independent recompute of
the first joined fixture from the engine code alone matched all twelve
daily-CSV fields with max difference 0.0, with r = 500.0 as in the frozen
fitted params).
TR-SuperLig has joined with goals (arm X3, the program's second goals
pass and its first non-Gate-Zero goals arm), SOT (arm GZ), corners
(gate_zero), and total shots (arm A). Cards failed its gate and is
excluded. The goals adapter's dispatch now accepts arm `x3` alongside
`gate_zero`: for X3 it computes the frozen set-play multipliers from
the training window (`arms.x3_multipliers(train, cutoff)`) and passes
them to `adjusted_lambdas`, calling each league's engine with the
signature it actually ships — SCO's engine takes the shrink counts as
an argument (`match_counts`), while TR's reads them from the fitted
model (`team_counts`, populated by its DC fit) and takes no counts
argument. Gate Zero behaviour is unchanged: an old-versus-new probe of
SCO goals predictions (including an unseen-team fixture) is
byte-identical, and SCO's daily outputs were bit-identical across the
two proof runs below. The X3 join passed its operational gate on
evidence, not on label: the runner's match CSV carries the
open-play/set-play xG columns the multiplier layer needs
(`expected_goals_open_play_*`, `expected_goals_set_play_*`, populated
from the 2022/2023 xG era onward, empty before it, exactly as the
harness loads them), and a runner-flow recompute of the shipped virgin
window (fit on all matches before 2025-08-08, X3 multipliers over the
same window) reproduces all 306 shipped virgin predictions exactly —
max absolute difference 0.0 across lambdas, 1X2, OU2.5 and BTTS —
while Gate Zero over the same window differs materially (mean total
lambda difference 0.274), so the daily product is the X3 product that
passed the gate, not Gate Zero under an X3 label. In the live run the
multiplier layer is active (25 of 26 teams carry a non-1.0 multiplier
at the virgin cutoff; the sampled first live fixture carries att/def
multipliers 1.506/0.734 at home). TR's data builder needed no floor
change: its only count assertion is a match-id uniqueness check, and
its awarded-row exclusion behaved live exactly as built — the two
proof runs rebuilt 1,818 matches (3,636 team rows) with the builder
reporting 31 awarded rows excluded (29 in 2022/2023, the earthquake
forfeits, plus one each in 2023/2024 and 2024/2025) against the
1,849-row world index for league 71. The SOT engine accepts the
runner's `ratio_prior` keyword exactly as shipped (200 for GZ), and
there are no `nan` strings in any column the adapters read (missing
values are empty fields). One presentation note: TR's virgin CSV
exports were written with the J1 template's presentation constants
(goals 0.412, SOT 0.448, corners 0.447 — the same 0.412 artifact SCO's
goals export carries), and the SOT export's 1H/2H line sets are the
harness's (2.5/3.5/4.5 and 3.5/4.5/5.5); the runner instead uses TR's
frozen halves constants from its config and preregs (goals 0.4403,
SOT 0.4435, corners 0.4801, total shots 0.4544) with the shipped SOT
line sets — halves are presentation-only in every case, and all gated
quantities (primary lines, FT ladders, fitted parameters) agree
between the preregs and the virgin predictions. The world index lists
this league as country `Turkiye`, league `Süper Lig` (fotmob_id 71,
ccode TUR), and the configuration uses those index spellings, which
are also the warehouse path. TR is a split-year world league
(2021/2022–2026/2027); its 2026/2027 season is in progress, with 207
upcoming fixtures predicted in the proof runs (first matchday
2026-11-21). Two end-to-end proof runs on 2026-11-09 predicted 207
fixtures in each of the four markets with zero errors; the second run
fetched nothing new anywhere and every pre-existing league's outputs
were bit-identical between the runs (99 files, md5 sets equal).
ES-LaLiga2 has joined with SOT (GZ — the arm the ES verdict and virgin
predictions label `GZ`, i.e. Gate Zero; primary 7.5, ladder 6.5/7.5/8.5,
halves share 0.4491, 1H ladder 2.5/3.5/4.5, 2H ladder 3.5/4.5/5.5),
corners (arm `x7`, primary 9.5, ladder 8.5/9.5/10.5, halves share
0.4692, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5), and total shots
(arm C, primary 23.5, ladder 22.5/23.5/24.5, halves share 0.4522,
1H ladder 9.5/10.5/11.5, 2H ladder 11.5/12.5/13.5). All three are
PROVISIONAL PASSes; goals and cards failed their gates and are absent.
ES is a world league (FotMob 140, ESP) over seasons 2021/2022–2026/2027;
at the 2026-11-09 join, FotMob listed 321 unplayed 2026/2027 fixtures
(from that night's Las Palmas–Eldense and Sabadell–Real Sociedad B,
02:30 WIB, out to the June play-off dates), all predicted in the three
markets with no errors. Two adapter-level facts are specific to ES.
First, its SOT engine is the programme's only one keying team state on
the FotMob team_id: its `load_matches` "home" field is `home_team_id`,
by design, because 10 of the league's 42 ids carry two name spellings
(accented and unaccented) and name-keying would split those clubs'
histories. `predict_sot` therefore accepts an opt-in `team_key: id`
market key that passes the fixture's `home_id`/`away_id` as strings to
the engine; with the key absent the team name is passed exactly as
before, so every existing league is unchanged (coordinator-verified:
name-keying ES changes its numbers — exp_away 3.654 versus 3.884
id-keyed on a live test fixture — while the runner's id-keyed output
reproduces an engine-only recompute of both of tonight's fixtures at
0.0 difference on every field, in all three markets). The ES SOT
engine also takes the runner's `ratio_prior` argument exactly like the
AU engine (200 for GZ; no-arg behaviour is unchanged, verified
identical). Second, corners `x7` needed no dispatch extension: the
runner passes the arm string opaquely into the league-local core, and
ES's X7 composition is the AR/SE one — the `mu_cs` core mean with a
single box-touch territorial multiplier (`touches_opp_box` for/against
difference, min-8-of-last-10 validity, clamped [0.70, 1.43], single
beta on the ±{0, .01, .02, .03, .04} grid scored at the league's 9.5
primary, which ES's core hard-codes exactly as AR's does). The
construction fact from the verdict reproduces exactly through this
path: ES's virgin fit is gamma 0.0, r 1.0957916247921453, beta [0.0],
fit_n 1861 — identical to the shipped `fitted_params_virgin.json` —
while Gate Zero on the same window fits beta [0.0, 0.025]; X7's virgin
edge is the absence of that big-chance tilt, not a box-touch effect,
and the first 25 shipped virgin predictions reproduce at 0.0
difference. On the full current history at the join the live X7 fit is
gamma 0.15, r 1.1338, beta [0.0], fit_n 2467 (the box-touch beta is
still exactly 0.0). ES's data builder asserts its frozen 2,478-match
count as a floor, like AU/ENGCH, and encodes missing values as empty
fields (283 empty `touches_opp_box_*` rows per side, no `nan` strings
anywhere), so the corners adapter's AR `nan` rule is a no-op here.
Play-off fixtures are ordinary rows in every ES fit (30 in the corpus:
20 semi-finals at matchRound `1/2`, 10 finals; no phase feature), and
upcoming play-off fixtures are predicted like any other.
MX-LigaMX has joined with corners only (arm `gate_zero`; C-MX PASSED
PROVISIONAL — the X7 arm tied Gate Zero exactly on the virgin, both
fitted territorial betas 0.0, so the prereg tie clause ships Gate
Zero). Primary line 9.5, ladder 8.5/9.5/10.5, halves share 0.465 (the
frozen prereg/verdict constant; config.yaml's 0.465223 is the
unrounded measurement, and the shipped virgin predictions use 0.465
exactly), 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5. The corners
engine needed no change: the runner's `predict_corners` calls
(`FeatureBuilder`, `fit_params`, `model_prediction`, `over_prob`)
match the MX core's signatures, and the corners path takes no
ratio-prior-style keyword. The data builder needed one live-data
fix: it excluded the in-progress tournament (`2026/2027 -
Apertura`) wholesale, so a daily rebuild would never add
current-season played matches — the fit would stay frozen at the
virgin window and no MX prediction could ever settle. Regular-phase
rows from the in-progress tournament are now included (block_idx 10,
past the ten frozen blocks); the builder's frozen-block count
assertions were already floors (`>=153` per block, `>=1530` rows)
and are unchanged. Missing values: `touches_opp_box_*` is missing on
195 home / 194 away rows of the frozen table, written as the string
`nan` where other builders write empty fields, but Gate
Zero reads only possession and big chances (complete on every row);
the box-touch columns feed only the unshipped X7 arm, and the runner
adapter's existing `nan` rule (AR join) already maps them to
missing. The cards model's event-derived yellow target is
irrelevant here: the corners adapter reads no event columns. All
other MX markets failed their gates and are excluded. MX is a
split-tournament world league (Apertura/Clausura blocks, regular
phase only; Liguilla/play-in rows stay out of the training table by
the builder's round rule, while unplayed current-season fixtures,
playoffs included, are predicted like any other league's). At the
2026-11-09 join, FotMob listed 22 unplayed fixtures in
the in-progress 2026/2027 Apertura season.
IN-ISL has joined with SOT (GZ) and corners (gate_zero). The SOT arm is
Gate Zero under its harness label `GZ`, exactly as shipped in
`s_in_virgin_predictions.csv` and `fitted_params_virgin.json`: primary
8.5, ladder 7.5/8.5/9.5, halves share 0.453, `div: IN-ISL` (the matches
CSV's `league` value), ratio prior 200, 1H ladder 2.5/3.5/4.5, 2H ladder
3.5/4.5/5.5. Corners is literal `gate_zero`: primary 10.5, ladder
9.5/10.5/11.5, halves share 0.458, 1H ladder 3.5/4.5/5.5, 2H ladder
4.5/5.5/6.5. No engine or builder change was needed: the data builder
already asserts its frozen 653-match count as a floor (a live rebuild
returns exactly 653), the SOT engine already accepts the runner's
`ratio_prior` keyword (the AU pattern, no-arg behaviour unchanged), and
neither CSV contains `nan` strings — missing values are empty fields
(`touches_opp_box_*` empty on 8 rows), which both adapters already read
as missing. IN-ISL is a world league mid-season: at the 2026-11-09 join
FotMob listed 50 unplayed 2026/2027 fixtures (from 2026-11-20), all
predicted in both markets with zero errors, and nothing settled (every
ledger entry is a future fixture). The first fixture of each market was
recomputed through IN-ISL's own engines in a separate process with every
field float-exact (corners live fit gamma 0.15, r 1.2520,
beta [0.0025, -0.025], fit_n 643), and a synthetic settlement check
settled both markets exactly once with independently verified grading
fields, artifacts restored md5-clean. The end-to-end proof ran during
the parallel-join storm on this box: two full runs completed (15
leagues, zero errors, `fetched_new` 0 everywhere, identical per-market
prediction counts), while seven further attempts were OOM-killed and
one was cut by a runtime restart with three to five other runner proofs
active; a partial run's rewrites of the first six leagues' daily CSVs
were md5-identical to a completed run's files.

DE-3Liga has joined with corners (arm `x7`, PROVISIONAL PASS in
`reports/C_DE3_VERDICT.md`: virgin LL 0.6959 at the primary 10.5 line,
calibration +3.29pp within 1 SE of 2.57pp) and total shots (arm A,
PROVISIONAL PASS: virgin LL 0.6874 at 26.5, calibration +2.69pp within
1 SE of 2.55pp); goals, SOT, and cards failed their gates and are
excluded. Corners configuration is primary 10.5, ladder 9.5/10.5/11.5,
halves share 0.466, 1H ladder 4.5/5.5/6.5, and 2H ladder 5.5/6.5/7.5;
total shots is primary 26.5, ladder 25.5/26.5/27.5, halves share 0.452,
1H ladder 11.5/12.5/13.5, and 2H ladder 13.5/14.5/15.5 — all read from
the league's frozen preregs and cross-checked against the shipped
virgin predictions (380 rows each; the corners file's 1H share is
exactly 0.466 and the total-shots file's exactly 0.452 on every row).
The X7 composition check matters here: DE-3's X7 is not the Gate Zero
fit under another label, but its virgin box-touch beta fitted to
exactly 0.0 (all 380 shipped rows carry beta [0.0], and
`active_with_nonzero_beta_share` is 0.0 in `results_virgin.json`),
while Gate Zero's virgin beta is [0.0025, 0.0] on possession. The arms
differ structurally — a single box-touch covariate on the BBT grid
versus possession + big-chance on the BP×BBC grid — so virgin
predictions differ genuinely (LL 0.6959 versus 0.7018). The runner
needs no dispatch extension: `predict_corners` passes the arm string
opaquely into DE-3's own `fit_params`/`multiplier`, whose
non-`gate_zero` branch is exactly the X7 composition, as for AR and
SE. On the full current history at the join, the live fit is gamma
0.15, r 1.1705, beta_bt [0.0], fit_n 1,977 — the multiplier is inert
again, by the engine's own fit. Total shots arm A reads its
lambda/r/ladder/half-split from the engine's `fitted_params.json`,
which matches the virgin params (r_A 101.4033, half_split
0.452/0.548). DE-3's data builder needed no change: its count
assertions compare the built rows to the world index itself (1,992
matches at the join), so daily rebuilds are self-consistent, like
DE-2's and KR's, and it encodes missing values as empty fields — there
are no `nan` strings in any column the adapters read
(`touches_opp_box_*` is empty on 319 early-era matches, where the X7
min-8 rule makes the multiplier inactive, as the prereg states).
Neither joining engine takes an argument the runner does not pass
(the `ratio_prior` trap is SOT-only, and DE-3 has no SOT market). It
is a world league (Germany, `3. Liga`, FotMob id 208) with seasons
2021/2022–2026/2027; at the 2026-11-09 join, FotMob listed 250
unplayed 2026/2027 fixtures (130 played of 380), all predicted in both
markets with zero errors, and the coordinator recomputed the first
fixture of each market (TSV Havelse–Viktoria Köln 1904, 2026-11-20)
through DE-3's own engines in a separate process with every field
float-exact (max difference 0.0). A synthetic settlement on RW
Essen–1860 München (2025-08-01) graded corners actual 15.0 and
total-shots actual 22.0 from the match CSV, and the artifacts were
restored md5-clean.
SA-ProLeague has joined with SOT (RS), corners (gate_zero), and total
shots (arm A). All three engines needed no change for the join: the SOT
engine already accepts the runner's `ratio_prior` keyword (20000 for RS;
no-arg behaviour unchanged), the data builder carries no frozen count
assertion (only a match-id uniqueness check), so daily rebuilds needed
no floor change, and it encodes missing values as empty fields — there
are no `nan` strings in any column the adapters read (the corners
adapter's `nan` rule is a no-op here). The league's regime break at
2023/2024 was handled in its build (dev scored post-break only); the
live engines fit on the full configured history exactly as coded, with
no join-time change to fit behaviour. Goals and cards failed their gates
and are excluded. SA is a split-year world league
(2021/2022–2026/2027); its 2026/2027 season is in progress.

ENG-LeagueOne has joined with SOT (GZ — the arm the ENG-L1 verdict,
virgin predictions, and `fitted_params_virgin.json` label `GZ`, i.e.
Gate Zero; primary 7.5, ladder 6.5/7.5/8.5, halves share 0.4414,
1H ladder 2.5/3.5/4.5, 2H ladder 3.5/4.5/5.5; PROVISIONAL PASS),
corners (gate_zero, primary 9.5, ladder 8.5/9.5/10.5, halves share
0.4672, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5; PASS CLEAN), and
total shots (arm C, primary 23.5, ladder 22.5/23.5/24.5, halves share
0.4551, 1H ladder 9.5/10.5/11.5, 2H ladder 11.5/12.5/13.5;
PROVISIONAL PASS). Goals and cards failed their gates and are absent.
ENG-LeagueOne is a world league (FotMob 108, ENG) over seasons
2021/2022–2026/2027; at the 2026-11-09 join, FotMob listed 386
unplayed 2026/2027 fixtures (from 2026-11-14), all predicted in the
three markets with no errors. No adapter or engine fix was needed.
Its data builder already asserts its frozen 2,943-match count as a
floor (both proof runs rebuilt exactly 2,943 matches and 5,886 team
rows), and its SOT `Engine` already accepts the runner's
`ratio_prior` keyword exactly as shipped (200 for GZ; the signature
was ported from ENG-Championship with the league). The builder
encodes missing values as empty fields — there are no `nan` strings
anywhere in either CSV (`touches_opp_box_*` is empty on 330/331
early-era rows per side) — so the corners adapter's AR `nan` rule is
a no-op here. Play-off fixtures are ordinary rows in every ENG-L1
fit (25 in the corpus, five per complete season including finals;
the virgin window is 552 regular + 5 play-off = 557, unlike the
Championship's incomplete 2025/2026 play-off copy), and upcoming
play-off fixtures are predicted like any other. The total-shots
export defect fixed during the league build was presentation-only
in the league's own virgin export; the runner reads
`fitted_params.json`, whose ladder is the preregistered
22.5/23.5/24.5 with half split 0.4551, and the daily CSV's FT and
1H/2H columns match PREREG_T_ENGL1 exactly. On the full current
history at the join the live corners fit is gamma 0.15, r 1.1855,
beta [0.0, 0.0], fit_n 2931 (the virgin fit was r 1.1574 on n 2216),
and the total-shots trailing r at the first fixture date is 74.1989.
An independent recompute of the first joined fixture (5837255,
AFC Wimbledon–Blackpool, 2026-11-14) from the engine code alone
matched all twelve daily-CSV fields with max difference 0.0 in each
of the three markets, and a synthetic settlement on match 5837087
graded actual totals 4.0 (SOT), 8.0 (corners), and 26.0 (total
shots) correctly, settled nothing on a second pass, and left the
artifacts md5-clean. Two end-to-end proof runs on 2026-11-09 each
predicted 386 fixtures in each of the three markets with zero
errors; the second run fetched nothing new anywhere and every
output was bit-identical between the runs (211 files, md5 sets
equal). Three earlier second-run attempts were lost to
infrastructure — one to a VM reboot and two to OOM kills under
parallel proof load on this box, each dying at the
AR-LigaProfesional rebuild — and their partial rewrites were
already bit-identical to the first run's outputs; the completed
second run was made with `MALLOC_ARENA_MAX=2` on the runner
process, which changes no output.
CO-PrimeraA has joined with SOT (arm `GZ` — the arm the CO-A verdict
and virgin predictions label `GZ`, i.e. Gate Zero; primary 7.5, ladder
6.5/7.5/8.5, halves share 0.4862, 1H ladder 2.5/3.5/4.5, 2H ladder
3.5/4.5/5.5), corners (arm `gate_zero`, primary 8.5, ladder
7.5/8.5/9.5, halves share 0.4956, 1H ladder 4.5/5.5/6.5, 2H ladder
5.5/6.5/7.5), and total shots (arm A, primary 24.5, ladder
23.5/24.5/25.5, halves share 0.4850). SOT is a PROVISIONAL PASS;
corners and total shots are clean PASSes; goals and cards failed
their gates and are absent. CO-A is a split-tournament world league
(FotMob 274, COL; the world index spells it country `Colombia`,
league `Primera A`, which are also the warehouse path) over the
twelve Apertura/Clausura blocks 2021–2026. All values come from the
league's frozen preregs and config, cross-checked against the shipped
virgin predictions (204 rows each): the SOT engine takes the runner's
`ratio_prior` keyword exactly as shipped (200 for GZ, no engine
change; `div` is the matches CSV's league-column value,
`CO-PrimeraA`), the corners core's fit grid hard-codes the 8.5
primary exactly as the reference cores do, and total shots arm A
takes its ladder and half split ([0.485, 0.515]) from the engine's
`fitted_params.json`, with the runner's default halves line sets
(1H 10.5/11.5/12.5, 2H 12.5/13.5/14.5), as for the J1/DK/NL arm-A
joins. Two adapter fixes were needed, both for the same root cause:
CO-A's data builder lower-cases every stat key (its own engines read
the lower-case spellings), while every other builder keeps FotMob's
capitalisation. First, `predict_corners`' possession lookup now falls
back to `ballpossesion_home`/`ballpossesion_away` when the
capitalised column is absent; without it, CO-A's possession windows
were always empty, `z_poss` was always None, and the Gate Zero
territorial multiplier could never engage — with it, 2,446 of the
2,581 feature rows carry an active possession window, and the live
corners fit is gamma 0.15, r 1.1863, beta [0.0, 0.0], fit_n 2571
(the grid scores real territorial values and still chooses zero, as
on the virgin fit). Second, settlement resolves each market's actual
columns to the lower-case spelling when the standard spelling is
absent from the CSV header, because CO-A's SOT actuals live under
`shotsontarget_home`/`shotsontarget_away`; without it, CO-A SOT
entries could never settle. Both fallbacks engage only when the
standard column is absent, so the leagues already served — whose
CSVs all carry the standard spellings — are unchanged. The data
builder is the streaming rewrite (two passes, one payload in memory
at a time; the earlier hold-everything version was OOM-killed during
the league build) and needed one live-data change: its frozen
build-time counts (2,582 matches, per-season counts in
EXPECTED_COUNTS) are now floors, since a daily rebuild grows the
in-progress 2026 - Clausura block. Its finished-status assertion is
kept as-is: the world pull only ever indexes finished matches
(unplayed fixtures are never written to the index), so a live
rebuild only adds finished rows incrementally, and both proof runs
rebuilt exactly 2,582 matches (5,164 team rows) with every season at
its frozen floor. Missing values are empty fields throughout — there
are no `nan` strings in either CSV (the single stats-missing
2022 - Apertura row is dropped by the adapters; `touches_opp_box_*`
is empty on 436 rows per side and feeds only the unshipped X7 arm),
so the AR `nan` rule is a no-op here. Tournament phases are ordinary
flagged rows in every fit (2,332 regular, 216 quadrangular, 34 final
in the rebuilt table; no phase feature), mirroring the shipped
behaviour, and listed fixtures are predicted as listed. The
2026 - Clausura season is in progress (179 played); at the
2026-11-09 join FotMob listed exactly one unplayed fixture for it
(Junior FC–Cúcuta, 2026-11-10; the remaining Clausura and
quadrangular fixtures were not yet listed). Two end-to-end proof
runs that day predicted that fixture in all three markets with zero
errors anywhere; the second run fetched nothing new in any league,
every league's predicted and upcoming counts were identical between
the runs, and all outputs were bit-identical between the runs (360
files, md5 sets equal). An engine-only recompute of the fixture from
the CO-A engine code reproduced every field of the runner's output
at 0.0 difference in all three markets, and a synthetic settlement
exercise settled one entry per market — SOT's actual (13) read
through the lower-case columns — before the artifacts were restored
md5-clean.
BR-SerieB has joined with SOT (RS) and corners (gate_zero), both
PROVISIONAL PASS. The SOT arm is RS exactly as shipped in
`s_brb_virgin_predictions.csv` and `fitted_params_virgin.json`:
primary 7.5, ladder 6.5/7.5/8.5, halves share 0.467, `div: BR-SerieB`
(the matches CSV's `league` value), ratio prior 20000, 1H ladder
2.5/3.5/4.5, 2H ladder 3.5/4.5/5.5. Corners is literal `gate_zero`:
primary 10.5, ladder 9.5/10.5/11.5, halves share 0.472, 1H ladder
3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5. The SOT engine needed no change:
it already accepts the runner's `ratio_prior` keyword (the AU
pattern; with no argument RS still falls back to 20000 on its own).
The data builder needed one live-data fix: its hard-equality assert
(`len(out) == len(rows)` over the world index) is now a floor on the
frozen 2,270-match count plus a match-id uniqueness assert, because
the live index can also list unplayed fixtures, which the builder
skips. Neither CSV contains `nan` strings — missing values are empty
fields (`touches_opp_box_*` empty on 690 rows per side, `big_chance_*`
on 3, corners/shots on 1), which both adapters already read as
missing, so the corners adapter's AR `nan` rule is a no-op here.
BR-SerieB is a calendar-year world league with its 2026 season in
progress (370 played at build time): at the 2026-11-09 join FotMob
listed 14 unplayed fixtures (2026-11-11 to 2026-11-28), all predicted
in both markets with zero errors, and nothing settled (every ledger
entry is a future fixture). The first three fixtures of each market
were recomputed through BR-SerieB's own engines in a separate process
with every field float-exact (corners live fit gamma 0.15, r 1.1516,
beta [-0.0025, 0.0], fit_n 2259), and a synthetic settlement check
settled both markets exactly once with independently verified grading
fields, artifacts restored md5-clean. The end-to-end proof ran during
the parallel-join storm on this box: the first attempt was OOM-killed
(exit 137) at the third league with three other runner proofs active,
and its completed leagues' daily CSVs were md5-identical to the
completed run's files; two full runs then completed (20 leagues, zero
errors, `fetched_new` 0 everywhere, log rows identical apart from
timestamps, identical per-market prediction counts, and identical
88-file md5 sets covering every league's daily CSVs, ledgers, and
settled-keys files).

IT-SerieB has joined with corners (arm `gate_zero`, PROVISIONAL
PASS in `reports/C_ITB_VERDICT.md`: virgin LL 0.6995 at the primary
9.5 line, calibration +3.29pp within 1 SE of 2.55pp) and total
shots (arm A, PASS clean in `reports/T_ITB_VERDICT.md`: virgin LL
0.6666 at 25.5, calibration +0.81pp); goals, SOT, and cards failed
their gates and are excluded. Corners configuration is primary
9.5, ladder 8.5/9.5/10.5, halves share 0.4734, 1H ladder
3.5/4.5/5.5, and 2H ladder 4.5/5.5/6.5; total shots is primary
25.5, ladder 24.5/25.5/26.5, halves share 0.4650, 1H ladder
11.5/12.5/13.5, and 2H ladder 13.5/14.5/15.5 — all read from the
league's frozen preregs and cross-checked against the shipped
virgin predictions (390 rows each; the corners file's 1H share is
exactly 0.4734 and the total-shots file's exactly 0.4650 on every
row; the shipped corners virgin fit is gamma 0.15, beta
[0.0, +0.025], r 1.1914). Total shots arm A reads its
lambda/r/ladder/half-split from the engine's `fitted_params.json`,
which matches the virgin params (lambda 300, r_A 123.5225,
half_split 0.465/0.535). No engine or builder change was needed:
the data builder's count assertion is already a floor
(`>= 2059`, plus match-id uniqueness), its Reggiana alias
(`959006` -> `6500`) is a generic id map applied to every row,
not a frozen match list, and the live rebuild returns exactly 20
distinct team ids in every season (Reggiana reaches its full 38
matches in 2023/2024 only through the alias); missing values are
empty fields — there are no `nan` strings in any column, corners,
total shots, and possession are complete on all 2,059 rows,
`big_chance_*` is empty on 1 row per side and
`touches_opp_box_*` on 194 (the box-touch columns feed only the
unshipped X7 arm, and the corners adapter's missing-value rule
already handles the empty fields). Neither joining engine takes
an argument the runner does not pass (the `ratio_prior` trap is
SOT-only, and IT-SerieB has no SOT market). Play-off and play-out
fixtures are ordinary rows in every IT-SerieB fit (40 promotion
play-off and 9 relegation play-out rows in the corpus, phase
recorded, no phase feature), and upcoming knockout fixtures are
predicted as listed. It is a world league (Italy, `Serie B`,
FotMob id 86) with seasons 2021/2022–2026/2027; at the
2026-11-09 join, FotMob listed 270 unplayed 2026/2027 fixtures
(110 played of 380), all predicted in both markets with zero
errors, and nothing settled (every ledger entry is a future
fixture; the IT-SerieB ledger holds 540 entries with no duplicate
(market, match_id, run_date) key). Two full end-to-end runs
(21 leagues, 50 markets) both completed with zero errors and
`fetched_new` 0 everywhere (the shared warehouse was already
current), 7,009 predictions per run and run logs identical
ignoring timestamps; of 709 snapshotted output files, all were
bit-identical between the runs except the append-only
`run_log.jsonl` itself. The first fixture of each market
(Hellas Verona–Cesena, 2026-11-20) was recomputed through
IT-SerieB's own engines in a separate process with every field
float-exact (max difference 0.0; corners live fit gamma 0.15,
r 1.1708, beta [0.0, 0.0], fit_n 2,049), and a synthetic
settlement on LR Vicenza–Catanzaro (2026-08-21) graded corners
actual 16.0 and total-shots actual 36.0 from the match CSV, with
artifacts restored md5-clean. The proof ran alongside two to
four other runner proofs on this box: no attempt was OOM-killed
or otherwise lost, and the two runs took about 37 and 34 minutes
of wall time under that contention.
PL-Ekstraklasa has joined with SOT only (arm `GZ` — the arm label in
the shipped `fitted_params_virgin.json` and virgin predictions;
primary 8.5, ladder 7.5/8.5/9.5, halves share 0.4584, 1H ladder
3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5; PROVISIONAL PASS — virgin
calibration −1.540pp breaches the 1.0pp boundary within 1 SE of
2.805pp). Goals, corners, and total shots failed their gates and are
absent. PL is a world league (FotMob 196, POL) over seasons
2021/2022–2026/2027. Its SOT `Engine` takes the runner's
`ratio_prior` keyword exactly as shipped (200 for GZ), its data
builder's frozen 1,654-match count assertion is now a floor (both
proof runs rebuilt exactly 1,654 matches and 3,308 team rows), and
missing values are empty fields throughout — no `nan` strings in
either CSV, and the builder keeps FotMob's capitalised stat keys, so
no adapter fallback was needed. Cards (arm X8, a clean PASS and the
programme's second referee-arm ship) did NOT join: it was stopped at
the same operational gate as DE-2Bundesliga's X8. The X8 engine
reproduces its shipped virgin predictions exactly (max difference
0.0 over all 306 rows for expected total, P(over 3.5), and the
referee multiplier, with r = 29.2075 as in the fitted params), and
the virgin gate graded a mostly-real X8 product: 250 of 306
predictions (81.7%) carried an active referee multiplier, 15 fell
back on thin referee history, and 41 on unknown identity (named
coverage 265/306 = 86.6%), and X8's virgin advantage (LL@3.5 0.6779
vs Gate Zero 0.6968) comes only from the multiplier rows. But the
referee is not available pre-match in the runner's data flow: the
FotMob `leagues` payload that supplies upcoming fixtures carries no
referee field at all, and `matchDetails` — fetched by the runner
only for finished matches — holds
`content.matchFacts.infoBox.Referee.text` empty for every one of the
nearest 18 upcoming PL fixtures probed on 2026-11-09 (the
2026-11-20–23 and 2026-11-27–30 matchdays, 11–21 days out), while
the same endpoint returns the appointed referee for finished PL
matches (e.g. match 5804037, Bartosz Frankowski). A daily run
predicting all 182 remaining fixtures would therefore ship Gate
Zero under the X8 label — a different product from the one that
passed the gate — so cards stays out until referee appointments are
available pre-match in the pull. Two notes for any future cards
join: settlement would need the per-market override
`cards_actual: [yellow_home, yellow_away]` (the NO/KR pattern),
because the K-PL gate graded the unified target the builder writes
to `yellow_home`/`yellow_away` — stats feed with an events fallback
for all 306 matches of 2021/2022, where the runner's default
stats-feed columns are empty — and the shipped virgin CSV's
presentation-only `mean_1h`/`mean_2h` columns carry the 0.317 share
hard-coded in the harness export (the NO-Eliteserien constant),
not PL's frozen 0.3338 in `PREREG_K_PL.md` and `config.yaml`; the
gate-graded FT columns are unaffected, and a runner block would use
0.3338. At the 2026-11-09 join, FotMob listed 182 unplayed
2026/2027 fixtures (from 2026-11-20), all predicted in SOT with no
errors. An independent recompute of the first joined fixture
(5804042, Piast Gliwice–Korona Kielce, 2026-11-20) from the PL
engine code alone matched all twelve daily-CSV fields with max
difference 0.0, and a synthetic settlement on match 5804035 (Legia
Warszawa–Raków Częstochowa, 2026-11-08) graded its actual SOT
total 11.0 correctly, settled nothing on a second pass, and left
the artifacts md5-clean. Two end-to-end proof runs on 2026-11-09
each predicted 182 fixtures in SOT (8,391 predictions across all
leagues) with zero errors anywhere; the second run fetched nothing
new in any league and every output was bit-identical between the
runs (431 files, md5 sets equal). The first completed run was
preceded by one attempt lost to a VM reboot at 2026-11-09 16:46
WIB, which died after ten leagues with no errors and no fetched
matches; its partial outputs were already identical to the
completed runs'.

US-USLChampionship has joined with SOT (GZ — the arm the USL verdict,
virgin predictions, and `fitted_params_virgin.json` label `GZ`, i.e.
Gate Zero; PROVISIONAL PASS, virgin calibration −2.36pp within 1 SE
of 2.51pp; primary 8.5, ladder 7.5/8.5/9.5, halves share 0.456,
`div: US-USLChampionship` (the matches CSV's `league` value), ratio
prior 200, 1H ladder 2.5/3.5/4.5, 2H ladder 3.5/4.5/5.5) and total
shots (arm B, PASS CLEAN, virgin calibration −0.59pp; primary 24.5,
ladder 23.5/24.5/25.5, halves share 0.453, 1H ladder 10.5/11.5/12.5,
2H ladder 12.5/13.5/14.5) — all read from the league's frozen
preregs and cross-checked against the shipped virgin predictions
(375 rows each, SOT arm `GZ` and total-shots arm `B` on every row).
Goals, corners, and cards failed their gates and are excluded. The
arm-B dispatch needed no extension: the runner's
`predict_total_shots_arm_b` (the SCO-Premiership precedent) calls
exactly the composition USL ships — USL's total-shots `model.py` is
identical to SCO's except its docstring and the frozen level-layer
mean `M_BAR` 24.4 (SCO: 24.9), with the same
`ShotsRegressionStore` / `NaiveTracker` / `BaseRateTracker` /
`LevelLayer` classes — and USL's `fitted_params.json` carries every
field the dispatch reads (lambda 100.0, r_A 155.1855, level cell
[30, 0.5, 50], ladder 23.5/24.5/25.5, half split [0.453, 0.547]).
The SOT engine likewise needed no change: it already accepts the
runner's `ratio_prior` keyword exactly as shipped (200 for GZ, the
AU pattern; no-arg behaviour unchanged). The data builder needed
one live-data fix: its frozen 2,590-match count was a hard equality
(`len(rows)==2590`), now a floor, so a daily rebuild survives the
next played match being appended; both proof runs rebuilt exactly
2,590 matches and 5,180 team rows. The builder encodes missing
values as empty fields — there are no `nan` strings anywhere in
either CSV (`touches_opp_box_*` is empty on 972 early-era match
rows, a column neither joined market reads; the SOT and total-shots
adapter columns are complete on every row). US-USLChampionship is
a calendar-year world league (United States, `USL Championship`,
FotMob id 8972) over seasons 2021–2026; at the 2026-11-09 join its
2026 season is in its playoff tail — FotMob listed 388 finished
fixtures and exactly 2 unplayed ones (Charleston Battery–Louisville
City FC on 2026-11-14 and New Mexico United–Sacramento Republic FC
on 2026-11-16), both predicted in both markets with zero errors,
and nothing settled (every ledger entry is a future fixture). An
independent recompute of the first fixture (6580858) through USL's
own engines in a separate process matched all 18 daily-CSV fields
with max difference 0.0 in each market, and a synthetic settlement
on match 6545882 (Sacramento Republic FC–El Paso Locomotive FC,
2026-11-08) graded SOT actual 11.0 and total-shots actual 33.0
correctly, settled each market exactly once (a second pass settled
nothing), and left the artifacts md5-clean. Two end-to-end proof
runs on 2026-11-09 (23 leagues, 56 markets) each predicted 8,210
fixtures in total with zero errors; the second run fetched nothing
new anywhere and every output was bit-identical between the runs
(171 files, md5 sets equal). One earlier first-run attempt was cut
by a VM reboot at the TR-SuperLig corners step after 15 leagues
with zero errors; its 38 daily CSVs were already bit-identical to
the completed run's outputs. The completed runs were made with
`MALLOC_ARENA_MAX=2` on the runner process, which changes no
output.
FR-Ligue2 ships two markets: corners (arm gate_zero, primary 8.5,
ladder 7.5/8.5/9.5, halves share 0.4803, 1H ladder 3.5/4.5/5.5, 2H
ladder 4.5/5.5/6.5; PROVISIONAL PASS) and total shots (arm A,
primary 22.5, ladder 21.5/22.5/23.5, halves share 0.4702, 1H ladder
9.5/10.5/11.5, 2H ladder 11.5/12.5/13.5; PROVISIONAL PASS). Goals,
SOT, and cards failed their gates and are absent. FR-Ligue2 is a
world league (FotMob 110, FRA) over seasons 2021/2022–2026/2027;
at the 2026-11-09 join, FotMob listed 198 unplayed 2026/2027
fixtures (from 2026-11-20), all predicted in the two markets with
no errors. No adapter or engine fix was needed. Its data builder
already asserts its match count as a floor (>= 1851; both proof
runs rebuilt exactly 1,859 matches and 3,718 team rows, with
season sizes 380/380/379/306/306/108 — 20 teams through 2023/2024
and 18 from 2024/2025 — and the hard-equality season asserts live
only in dev harness scripts the runner never calls), and its
corners and total-shots engines accept exactly the calls the
runner makes (the runner reads `fitted_params.json` for total
shots, whose ladder and half split match PREREG_T_FR exactly).
The builder encodes missing values as empty fields — there are
no `nan` strings anywhere in either CSV (`touches_opp_box_*` is
empty on 323 early-era rows per side, and one row lacks stats
entirely) — so the corners adapter's AR `nan` rule is a no-op
here. The warehouse holds no play-off matches for this league at
all (all 1,859 rebuilt rows are `phase='regular'`, verified by a
full France-tree scan during the league build), and the runner
mirrors the corpus as it is without any phase filter: if FotMob
ever lists a play-off fixture in the current-season payload it
will be predicted like any other fixture, and a finished one
would enter the rebuilt CSV labelled `phase='non_regular'` and
enter the fits, since neither engine filters on phase. On the
full current history at the join the live corners fit is gamma
0.15, r 1.1596, beta [0.0, 0.0], fit_n 1848 (the virgin fit was
gamma 0.3, r 1.2061 on n 1434). An independent recompute of the
first joined fixture (5803317, Annecy FC–Clermont Foot,
2026-11-20) from the engine code alone matched all twelve
daily-CSV fields with max difference 0.0 in each of the two
markets, and a synthetic settlement on match 5803209 graded
actual totals 7.0 (corners) and 16.0 (total shots) correctly
and left the artifacts md5-clean. Two end-to-end proof runs on
2026-11-09 each predicted 198 fixtures in each of the two
markets with zero errors; the second run fetched nothing new
anywhere and every output was bit-identical between the runs
(741 files, md5 sets equal apart from the appending run log).
Two earlier attempts were lost to infrastructure — one to an
OOM kill (exit 137) at the AR-LigaProfesional rebuild under
parallel proof load on this box, and one to a VM reboot at the
DK-Superligaen rebuild — and their partial rewrites were already
bit-identical to the completed run's outputs; the completed
runs were made with `MALLOC_ARENA_MAX=2` on the runner process,
which changes no output.

GR-SuperLeague has joined with corners (arm `gate_zero`, PASS
clean in `reports/C_GR_VERDICT.md`: virgin LL 0.6939 at the primary
8.5 line, calibration −0.89pp) and total shots (arm C, PASS clean
in `reports/T_GR_VERDICT.md`: virgin LL 0.6825 at 22.5,
calibration +0.64pp); goals, SOT, and cards failed their gates and
are excluded. Corners configuration is primary 8.5, ladder
7.5/8.5/9.5, halves share 0.4862, 1H ladder 3.5/4.5/5.5, and 2H
ladder 4.5/5.5/6.5; total shots is primary 22.5, ladder
21.5/22.5/23.5, halves share 0.4611, 1H ladder 10.5/11.5/12.5, and
2H ladder 11.5/12.5/13.5 — all read from the league's frozen
preregs and cross-checked against the shipped virgin predictions
(236 rows each; the corners file's 1H share is exactly 0.4862 and
the total-shots file's exactly 0.4611 on every row). Two changes
were needed. The data builder's hard-equality count assertions
(1,261 rows, the per-season phase counts, and the in-progress
2026/2027 phase set) are now floors, following the AR pattern, so
a daily rebuild survives new 2026/2027 results and the arrival of
its play-off groups. And the runner's total-shots arm-C path now
honours an opt-in `exclude_seasons` market key (default inert —
no other league sets it): GR's frozen T prereg excludes the
2021/2022 seed season from every fit because that season's shots
feed is a different measurement (mean 16.89 vs 21.96–24.16 later),
and its engine harness loads only the non-excluded seasons, while
the runner had built its fit rows from the full matches CSV; the
GR live fit now uses exactly 1,021 rows (1,261 − 240). No other
engine change was needed: missing values are empty fields — there
are no `nan` strings in any column of the rebuilt table — the
builder keeps FotMob's `BallPossesion` casing, which is what the
corners adapter reads, and neither joining engine takes an
argument the runner does not pass (the corners core's
`fit_params`/`model_prediction`/`over_prob` signatures match the
adapter exactly, and the arm-C model's classes and
`fitted_params.json` keys — lambda 300, r_A 139.5707, level cell
[30.0, 1.0, 50.0], trailing window 200, half split
0.4611/0.5389 — match the virgin params). Play-off rounds are
ordinary flagged rows in every GR fit (240 matches in each of
2021/2022–2023/2024 include 58 play-off rows, 54 in each later
season; phase recorded, no phase feature anywhere), and upcoming
play-off fixtures will be predicted as listed. It is a world
league (Greece, `Super League 1`, FotMob id 135) with seasons
2021/2022–2026/2027; at the 2026-11-09 join, FotMob listed 112
unplayed 2026/2027 fixtures (69 played of 181 listed), all
predicted in both markets with zero errors, and nothing settled
(every ledger entry is a future fixture; the GR ledger holds 224
entries with no duplicate (market, match_id, run_date) key). Two
full end-to-end runs (26 leagues, 63 markets) both completed with
zero errors and `fetched_new` 0 everywhere (the shared warehouse
was already current), 9,001 predictions per run and run logs
identical ignoring timestamps; of 194 snapshotted output files,
all were bit-identical between the runs except the append-only
`run_log.jsonl` itself. The first fixture of each market
(Kalamata–AEK Athens, 2026-11-21, the same fixture in both) was
recomputed through GR's own engines in a separate process with
every field float-exact (max difference 0.0; corners live fit
gamma 0.0, r 1.1094, beta [0.0, 0.0], fit_n 1,247; total-shots
trailing r 98.4243 over the 1,021 non-excluded fit rows), and a
synthetic settlement on Aris Thessaloniki–NFC Volos (2025-08-23)
graded corners actual 9.0 and total-shots actual 22.0 from the
match CSV, with artifacts restored md5-clean. The proof ran
alongside three to five other runner proofs on this box: the
first run-2 attempt was lost to a VM reboot at 18:37 UTC after
16 of 26 leagues (no state was corrupted — ledger appends are
key-deduped and the daily CSV writes are deterministic) and was
rerun in full; the completed runs took about 58 and 66 minutes
of wall time under that contention.

EG-PremierLeague has joined with corners (arm `gate_zero`, PROVISIONAL
PASS in `reports/C_EG_VERDICT.md`: virgin LL 0.6938 at the primary 8.5
line, calibration +1.82pp within 1 SE of 2.79pp — the X7 arm tied Gate
Zero exactly on the virgin, its box-touch beta fitting to 0.0, so the
prereg tie clause ships Gate Zero) and total shots (arm A, PASS clean
in `reports/T_EG_VERDICT.md`: virgin LL 0.65757 at 22.5, calibration
-0.44pp); goals, SOT, and cards failed their gates and are excluded.
Corners configuration is primary 8.5, ladder 7.5/8.5/9.5, halves share
0.4604, 1H ladder 3.5/4.5/5.5, and 2H ladder 4.5/5.5/6.5; total shots
is primary 22.5, ladder 21.5/22.5/23.5, halves share 0.4459, 1H ladder
9.5/10.5/11.5, and 2H ladder 11.5/12.5/13.5 — all read from the
league's frozen preregs and cross-checked against the shipped virgin
predictions (322 rows each; the corners file's arm is `gate_zero` on
every row with 1H share exactly 0.4604, the total-shots file's arm is
`A` with share exactly 0.4459). Total shots arm A reads its
lambda/r/ladder/half-split from the engine's `fitted_params.json`
(lambda 300, r_A 43.6266, half split 0.4459/0.5541); its preregistered
halves ladders differ from the runner's arm-A defaults, so they are
explicit in the configuration, as for SA-ProLeague. No engine,
builder, or adapter change was needed: the data builder carries no
count assertion at all (it prints its counts only — a live rebuild
returns 1,545 matches and 3,090 team rows), both engines match the
runner adapters' call signatures exactly (the `ratio_prior` trap is
SOT-only, and EG has no SOT market), the corners core's fit grid
hard-codes the 8.5 primary exactly as the reference cores do, and the
builder keeps FotMob's stat-key capitalisation (`BallPossesion`,
`big_chance`, `touches_opp_box`), so the CO-PrimeraA lower-case trap
does not arise. Missing values are empty fields — there are no `nan`
strings in either CSV (corners and total shots are empty on 12 rows,
`touches_opp_box_*` on 304, feeding only the unshipped X7 arm), so the
corners adapter's AR `nan` rule is a no-op here. Egypt's format
changed twice in three seasons (18-team double round robin, then a
9+9 split at 225 matches, then a 21-team split at 322); phases are
pooled in every fit with no phase feature, mirroring the shipped
behaviour, and listed fixtures are predicted as listed. It is a world
league (Egypt, `Premier League`, FotMob id 519) with seasons
2021/2022–2026/2027; its 2026/2027 season is in progress (80 played),
and at the join FotMob listed 110 unplayed fixtures (from
2026-11-23), all predicted in both markets with zero errors, and
nothing settled (every ledger entry is a future fixture; the EG
ledger holds 220 entries with no duplicate (market, match_id,
run_date) key). The first fixture of each market (El Gouna FC–Zamalek
SC, 2026-11-23) was recomputed through EG's own engines in a separate
process with every field float-exact (max difference 0.0, twelve
fields per market; corners live fit gamma 0.15, r 1.1892, beta
[0.0, 0.0], fit_n 1,522, against the virgin fit's r 1.1846), and a
synthetic settlement on Wadi Degla FC–ZED FC (2026-08-21) graded
corners actual 3.0 and total-shots actual 10.0 from the match CSV,
settled each market exactly once, and left the artifacts md5-clean.
Two end-to-end proof runs (runner date 2026-11-09; 26 leagues, 63
markets) each produced 8,994 predictions with zero errors; the second
run fetched nothing new anywhere and every output was bit-identical
between the runs (195 files, md5 sets equal) — the only run-log
difference is NO-Eliteserien's single fetched match in the first run.
The proof ran through the parallel-join storm on this box: three
attempts were lost (two OOM kills at the AR-LigaProfesional rebuild
and one VM reboot at NO-Eliteserien) before the first run completed
in about 60 minutes, the second run's first attempt was lost to a
second VM reboot at US-MLS, and its retry completed in about 33
minutes; every partial run's rewrites were bit-identical to the
completed runs' outputs, as the final md5 comparison shows.
RU-PremierLeague has joined with SOT (GZ) and total shots (arm B). RU-PremierLeague has joined with SOT (GZ — Gate Zero; PROVISIONAL PASS, virgin calibration −4.07pp within one standard error of 3.11pp; primary 8.5, ladder 7.5/8.5/9.5, halves share 0.4612, div RU-PremierLeague, ratio prior 200, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5) and total shots (arm B, PROVISIONAL PASS, virgin calibration −2.59pp within one standard error of 3.09pp; primary 25.5, ladder 24.5/25.5/26.5, halves share 0.4602, 1H ladder 11.5/12.5/13.5, 2H ladder 13.5/14.5/15.5) — read from the frozen preregs and verdicts and cross-checked against the shipped virgin predictions. Goals (FAIL at dev), corners, and cards failed their gates and are excluded. The arm-B dispatch needed no extension: the runner's predict_total_shots_arm_b (the SCO-Premiership precedent) calls exactly the composition RU ships — RU's total-shots model.py is identical to SCO's except its docstring (same M_BAR 24.9) — and RU's fitted_params.json carries every field the dispatch reads (lambda 30.0, r_A 91.2360, level cell [30, 0.5, 50], ladder 24.5/25.5/26.5, half split [0.4602, 0.5398]): the registered lines and constant, not the defective shipped-format writer values the league build bypassed (a 25.5/26.5/27.5 FT ladder and a stale 0.4592 half split from another league); the recompute below is the arbiter and it reproduces the runner. The SOT engine needed no change: it already accepts the runner's ratio_prior keyword (the AU pattern), and the coordinator verified the runner's ratio_prior=200 construction is bitwise-identical to the no-arg engine. The data builder needed two fixes: its frozen 1,312-match count was a hard equality — a bug for a league whose 2026/2027 season is still running — now a floor, and it ignored the runner's INDEX/MAIN_REPO globals (it read the index from a hard-coded main-checkout root via argparse); it now follows the runner contract, with the explicit CLI override preserved. The builder encodes missing values as empty fields: there are no 'nan' strings anywhere in either CSV, the SOT and total-shots adapter columns are complete on all 1,312 rows, and no name in either CSV is non-ASCII (FotMob's Russian team and referee names are Latin transliterations; the payloads' only non-ASCII characters are Latin-extended player-name letters that never reach the CSVs), so encoding round-trips through the runner's UTF-8 readers exactly. RU-PremierLeague is a world league (Russia, Premier League, FotMob id 63) over seasons 2021/2022–2026/2027, a clean 240-match double round-robin per complete season (1,312 matches and 2,624 team rows at the join: five complete seasons plus 112 played in 2026/2027); at the 2026-11-09 join, FotMob listed exactly the remaining 128 fixtures of 2026/2027 (from 2026-11-20), all predicted in both markets with zero errors, and nothing settled (every ledger entry is a future fixture). An independent recompute of the first fixture (5847235, FC Rostov–Krylya Sovetov Samara, 2026-11-20) from the engine code alone matched all 18 daily-CSV fields with max difference 0.0 in each market, and a synthetic settlement on match 5847230 (Zenit St. Petersburg–FC Rostov, 2026-11-08) graded SOT actual 8.0 and total-shots actual 22.0 correctly, settled each market exactly once (a second pass settled nothing), and left the artifacts md5-clean. Two end-to-end proof runs on 2026-11-09 (29 leagues, 68 markets) each completed with zero errors and fetched nothing new in any league in either run (9,612 predictions in run 1, 9,606 in run 2); every output was bit-identical between the runs (215 compared files) except ES-LaLiga2's three daily CSVs, because FotMob's LaLiga2 listing dropped two fixtures dated 2026-11-09 (Las Palmas–Eldense and Sabadell–Real Sociedad B) between the runs — 321 upcoming in run 1, 319 in run 2, and neither was fetched as a result — while RU's outputs were bit-identical. The completed runs followed five attempts lost to infrastructure under heavy parallel load on this box: three OOM kills (exit 137) at the NL-Eredivisie stage (whose builder retains every parsed payload in memory), one VM reboot at about 20:38 UTC that also wiped /tmp, and one further OOM kill after the reboot; the successful runs were launched detached with MALLOC_ARENA_MAX=2 on the runner process, which changes no output.
RO-LigaI ships one market: corners (arm gate_zero, primary 8.5,
ladder 7.5/8.5/9.5, halves share 0.477, 1H ladder 3.5/4.5/5.5, 2H
ladder 4.5/5.5/6.5; PROVISIONAL PASS — virgin calibration −3.00pp
with SE 2.74pp, the breach within 1 SE of the 1.0pp boundary).
Goals, SOT, and cards failed their gates and total shots was not
buildable, so all four are absent. The corners candidate is a
preregistered SINGLE arm: the X7 box-touches and big-chance
variants were dropped before fitting because both keys exist only
from 2025/2026, so there was no variant arm to dispatch. RO-LigaI
is a world league (FotMob 189, ROU, Romania `Liga I`) over seasons
2021/2022–2026/2027. No adapter or engine fix was needed: the
runner's corners calls match the engine's signatures exactly
(`FeatureBuilder` / `fit_params` / `model_prediction` /
`over_prob`), and the builder needed no count fix — its only
equality assert is self-referential (finished rows out == index
rows in), not a frozen count. Both proof runs rebuilt exactly
1,702 matches and 3,404 team rows (season sizes 316/317/317/315/
317/120; the build had 1,701 with 119 played in 2026/2027 — run 1
fetched the 120th, match 5853548 Botoșani–Oțelul Galați,
2026-11-09). The builder encodes missing values as empty fields —
there are no `nan` strings anywhere in either CSV, the
`BallPossesion` casing is the standard one, 26 early-era rows lack
corners entirely and are dropped by the adapter, and no row has
corners without total shots, so the core's stats window is safe.
Phase: the corpus holds regular 1,319 / championship-group 150 /
relegation-group 225 / ECL play-off 7. The league models regular,
championship-group, and relegation-group matches as ordinary
fixtures and excluded the ECL play-off from its build corpus
(its own `core.load` filters `phase == "ecl_playoff"`), but the
runner has no phase filter (the FR-Ligue2 precedent, recorded
there): the 7 ECL play-off matches sit in the rebuilt CSV and
enter the runner's history and fit like any other fixture, and a
future ECL play-off fixture would be predicted the same way. No
filter was added. On the full current history at the join the
live corners fit is gamma 0.0, r 1.1515, beta [0.0025], fit_n
1,665 (the virgin fit was gamma 0.0, r 1.1080, beta [0.0025] on
n 1,223). An independent recompute of the first joined fixture
(5853557, Botoșani–FC Voluntari, 2026-11-20) from the engine code
alone matched all twelve daily-CSV fields with max difference
0.0, and a synthetic settlement on match 5853548 graded its
actual corners total 3.0 correctly (log loss exact), settled
nothing on a second pass, and left the artifacts md5-clean. Two
end-to-end proof runs on 2026-11-09 (29 leagues, 67 markets)
each finished with zero errors anywhere; run 1 predicted 9,479
fixtures in total (RO: 120 corners predictions, 1 fetched, 0
settled) and the completed run 2 predicted 9,470 with
`fetched_new` 0 in every league. Run 2 took three attempts: the
first was killed by a VM reboot at 2026-11-09 20:38 UTC at the
ES-LaLiga2 step after 16 leagues with zero errors and nothing
fetched, and the second was OOM-killed at the AR-LigaProfesional
rebuild under parallel proof load from other worktrees — the
same spot recorded in the FR-Ligue2 paragraph; the third attempt
ran clean. Outputs were bit-identical between the completed runs
except ES-LaLiga2's three daily CSVs: two ES fixtures and one
NO-Eliteserien fixture dated 2026-11-09 finished between the
runs and left the upcoming lists (their JSONs had been fetched
into the shared warehouse by concurrent worktree runs, so this
worktree's index never absorbed them and those leagues' rebuilt
histories were unchanged; the remaining ES predictions match run
1 exactly at the primary lines for corners and total shots, and
within 0.00018 for SOT — the SOT engine was verified
deterministic on the final CSV by an exact recompute, so the
micro-difference traces to run 1 reading pre-revision shot
stats). RO-LigaI's own outputs were bit-identical between the
runs. One deviation from the usual join practice: the world
index line for match 5853548 is committed with this join,
because run 1 fetched that file into the shared store — without
the line, the production index would never absorb the match
(the runner's missing check is file-existence based). The
completed runs were made with `MALLOC_ARENA_MAX=2` on the runner
process, which changes no output.
PE-Liga1 has joined with SOT (arm RS, PROVISIONAL PASS in
`reports/S_PE_VERDICT.md`: virgin LL 0.6856 at the primary 8.5 line,
calibration −3.58pp within 1 SE of 2.96pp), corners (arm `x7`,
PROVISIONAL PASS in `reports/C_PE_VERDICT.md`: virgin LL 0.6593 at
9.5, calibration −3.42pp within 1 SE of 2.88pp), and total shots
(arm A, PROVISIONAL PASS in `reports/T_PE_VERDICT.md`: virgin LL
0.6862 at 19.5, calibration −2.69pp within 1 SE of 2.97pp); goals
and cards failed their gates and are excluded. SOT configuration
is primary 8.5, ladder 7.5/8.5/9.5, halves share 0.4611,
`div: PE-Liga1`, ratio prior 20000, 1H ladder 2.5/3.5/4.5, and 2H
ladder 3.5/4.5/5.5; corners is primary 9.5, ladder 8.5/9.5/10.5,
halves share 0.4817, 1H ladder 3.5/4.5/5.5, and 2H ladder
4.5/5.5/6.5; total shots is primary 19.5, ladder
17.5/18.5/19.5/20.5/21.5, halves share 0.4662, 1H ladder
8.5/9.5/10.5, and 2H ladder 9.5/10.5/11.5 — all read from the
league's frozen preregs and `config.yaml` and cross-checked
against the shipped virgin predictions (323 corners rows, 280
scored SOT and total-shots rows). PE-Liga1 is the programme's only
league whose shots target is unified — rich matches
(`has_rich_stats` = 1) count `shotsontarget + shotsofftarget` per
side, sparse matches the `total_shots` key as-is, because the
feed's rich `total_shots` additionally includes blocked shots and
differs from the unified total in 950 of 1,004 rich matches — and
its engines fit only on regular-phase, non-awarded rows (15
play-off and 9 awarded rows excluded). The corners and
total-shots adapters therefore take an opt-in
`shots_target: unified` flag (absent = unchanged for every other
league): history construction then mirrors the engines' own
loaders, including keeping missing-corner rows in the corners
history (they feed the shot and territorial histories), and
total-shots settlement grades the unified actual under the same
flag. The C-PE caveat ships exactly as recorded in its verdict:
the `x7` arm's fitted touches beta is 0.0 in both virgin block
fits and in the live fit (gamma 0.3, r 1.3729, beta [0.0],
fit_n 1,677), so the shipped product is the multiplier-free base
under the `x7` label, not evidence that box touches predict
corners in Peru. The dispatch was verified against the shipped
virgin predictions before the join: the engine-side per-block
reproduction matches all 323 virgin corners rows (mu, r, gamma,
and P(over 9.5)) with max difference 0.0, and the runner's own
`predict_corners` on pre-virgin history reproduces the earliest
virgin date exactly for arm labels `x7` and `X7` alike, since the
PE core treats every non-`gate_zero` arm as the box-touch branch;
the shipped label is the lower-case `x7` of
`fitted_params_virgin.json`. Spot recomputations of the shipped
SOT and total-shots virgin files agree to within 5e-15 (a
one-ulp difference on one SOT expectation field in the shipped
CSV, deterministic in this environment; the live runner-versus-
engine recompute below is bit-exact). The SOT engine and the
data builder needed no change: the engine already accepts the
runner's `ratio_prior` keyword exactly as shipped (20000 for RS,
the AU pattern), `predict_sot` calls its own `load_matches`, the
builder's per-season counts are already floors (each season
>= its frozen expected count and >= 1,860 matches in total; all
proof runs rebuilt exactly 1,860 matches and 3,720 team rows,
season sizes 239/346/344/306/328/297 across the
two-tournaments-per-year calendar format, so no fixed-size
assert can fire as the in-progress 2026 season grows), missing
values are empty fields throughout (no `nan` strings in either
CSV), and the builder's lower-case stat keys are served by the
existing adapter fallbacks (the `ballpossesion` possession
spelling and the lower-case SOT settlement actuals). PE-Liga1 is
a calendar-year world league (Peru, `Liga 1`, FotMob id 131)
over seasons 2021–2026 with 2026 in progress; at the
2026-11-09 join FotMob listed 9 unplayed 2026 fixtures (from
2026-11-15), all predicted in all three markets with zero
errors, and nothing settled (every ledger entry is a future
fixture; the PE-Liga1 ledger holds 27 entries with no duplicate
(market, match_id, run_date) key). An independent recompute of
the first joined fixture (1000017308, Comerciantes
Unidos–Sport Boys, 2026-11-15) through PE-Liga1's own engines in
a separate process matched every daily-CSV field with max
difference 0.0 in each market (12 SOT fields, 12 corners fields,
14 total-shots fields), and a synthetic settlement on match
3547652 (Carlos A. Mannucci–Alianza Atletico, 2021-04-26)
graded SOT actual 17.0, corners actual 5.0, and total-shots
actual 25.0 — the unified total, not the raw `total_shots` sum
of 33.0 — settled each market exactly once (a second pass
settled nothing), and left the artifacts md5-clean. Two full
end-to-end proof runs (29 leagues, 69 markets) each produced
9,377 predictions with zero errors anywhere; the second run
fetched nothing new in any league, and every output was
bit-identical between the two runs (214 files, md5 sets equal).
The completed first run (9,386 predictions, zero errors,
`fetched_new` 0 everywhere) differs from that pair only because
two ES-LaLiga2 fixtures and one NO-Eliteserien fixture finished
in the intervening hour, so the second run fetched 2 ES matches
and settled 2 ES entries per market. Three further attempts
were lost to infrastructure and are recorded plainly: one
run-2 attempt died in a VM reboot after three leagues, its
replacement was OOM-killed at the third league under three
concurrent proof runs on this box, and a third attempt's
supervising shell deadlocked on its own command-line pattern
(the run itself was later completed as the proof pair above).
All completed runs were made with `MALLOC_ARENA_MAX=2` on the
runner process, which changes no output.

RU-1Division has joined with corners only (arm `gate_zero`, PROVISIONAL PASS in `reports/C_RU1_VERDICT.md`: virgin LL 0.698888 at the primary 8.5 line, calibration +3.28pp with the 2.28pp excess over the 1.0pp boundary within one standard error of 2.97pp; dev LL 0.695540 beat both baselines). Goals, SOT, cards, and total shots failed their gates and are excluded. Corners configuration is primary 8.5, ladder 7.5/8.5/9.5, and `halves_share_1h: null` — this league's feed has no period splits at all (`has_period_splits_content` is 0 on all 1,757 built rows, and its frozen config and shipped virgin predictions are FT-only), so it is the first user of the FT-only corners opt-in documented above: the runner writes the halves columns empty, in the same positions as every other corners league, and predicts the FT ladder only. The corners engine is the possession-only Gate Zero variant (the big-chance half of the RU-Premier pair is absent from every payload here; its fit grid hard-codes the 8.5 primary, as the reference cores do), and its `fit_params`/`model_prediction`/`over_prob` signatures match the adapter exactly, so no engine change was needed. The data builder needed the RU-Premier fixes: its frozen 1,756-match count was a hard equality — now a floor, because season sizes vary (380 in 2021/2022, 306 in each of the next three seasons, 305 in 2025/2026) and 2026/2027 is still running — and it ignored the runner's INDEX/MAIN_REPO globals; it now follows the runner contract, with the explicit CLI override preserved. The builder encodes missing values as empty fields: there are no 'nan' strings in either CSV, corners are empty on 89 score-only rows (dropped by the adapter, never imputed), the builder keeps FotMob's `BallPossesion` casing, and no team name is non-ASCII, so encoding round-trips exactly. RU-1Division is a world league (Russia, `1. Division`, FotMob id 338) over seasons 2021/2022–2026/2027 (1,757 matches and 3,514 team rows at the join: five complete seasons plus 154 played in 2026/2027); at the 2026-11-09 join, FotMob listed the remaining 152 fixtures of 2026/2027 (from 2026-11-14), all predicted in corners with zero errors, and nothing settled (every ledger entry is a future fixture; the ledger holds 152 entries with no duplicate (market, match_id, run_date) key). An independent recompute of the first fixture (5897681, Volga Ulyanovsk–Torpedo Moscow, 2026-11-14) from the engine code alone matched all four FT fields with max difference 0.0 and confirmed all eight halves fields empty (live fit gamma 0.15, r 1.4546, beta [0.0], fit_n 1,658), and a synthetic settlement on match 5897664 (FC Yenisey Krasnoyarsk–PFC Sochi, 2026-11-08) graded corners actual 9.0 correctly on the FT line, settled exactly once (a second pass settled nothing), and left the artifacts md5-clean. Two end-to-end proof runs on 2026-11-09 (33 leagues, 75 markets) each completed with zero errors and 10,682 predictions; the first run fetched exactly one match — RU-1Division's 5897663 (Veles Moscow–KamAZ, played 2026-11-09), the new league's first-ever pull — and the second run fetched nothing new in any league; every output was bit-identical between the runs (344 compared files, including both FotMob indexes), so the FT-only amendment changed no pre-existing league's numbers. The first run's first attempt was lost to a VM reboot at about 22:28 UTC after 27 of 33 leagues and was rerun in full; the completed runs were made with `MALLOC_ARENA_MAX=2` on the runner process, which changes no output.
IE-PremierDivision has joined with corners only (arm `gate_zero`,
PROVISIONAL PASS in `reports/C_IE_VERDICT.md`: virgin LL 0.6817 at
the primary 9.5 line, calibration −1.32pp within 1 SE of 3.69pp;
goals, SOT, cards, and total shots all failed their gates and are
excluded). Configuration is primary 9.5, ladder 8.5/9.5/10.5,
halves share 0.4762, 1H ladder 3.5/4.5/5.5, and 2H ladder
4.5/5.5/6.5, all read from the league's frozen prereg and
cross-checked against the shipped virgin predictions (180 rows;
the 1H share is exactly 0.4762 on every row). Two join changes
were needed. First, the data builder's hard-equality assertion
(`len(rows) == len(index_rows)`) is now a floor on the frozen
1,080-match corpus (six seasons of exactly 180 matches): the
corpus grows when the 2027 season is added and the index may
list unplayed fixtures the builder skips, so an exact count
would become a bug. Second, `predict_corners` gained an opt-in
`exclude_seasons` market key, mirroring the total-shots arm-C
precedent, and IE's corners block sets it to `["2021"]`: the
frozen C-IE harness loads only 2022 onward (2021 corners exist
in just 35 of its 180 matches, and the engine's own `core.load`
cannot parse the empty corner rows), while the runner adapter
would otherwise silently fold those 35 partial-era rows into
the history and fit — a replay of the first virgin fixture
through the adapter without the exclusion gave exp_total
10.0268 against the shipped 10.1132. With the exclusion the
adapter reproduces the gated product: the same fixture
(5100791, Derry City–Sligo Rovers, 2026-02-06), replayed
through `predict_corners` on the pre-virgin history, matched
all twelve shipped virgin fields with max difference 0.0, and
an engine-only recompute in a separate process returned the
frozen virgin fit exactly (gamma 0.3, r 1.219469444218345,
beta [0.0, 0.025], fit_n 707). The adapter change is inert for
existing leagues: an old-versus-new probe of a RO-LigaI corners
fixture (no `exclude_seasons` key) was identical. Missing
values are empty fields throughout the IE CSVs — there are no
`nan` strings in any column the adapter reads (corners are
empty on the 145 stats-poor 2021 rows the exclusion removes;
`big_chance_*` is empty on 183 rows and feeds Gate Zero's
territorial windows under the adapter's existing missing-value
rules, exactly as the harness's own load treats them). A
synthetic settlement on match 5100791 graded corners actual
9.0 (9 + 0) at the 9.5 line, settled exactly once, and left
the artifacts clean. IE is a calendar-year world league
(Ireland, `Premier Division`, FotMob id 126, ccode IRL) over
seasons 2021–2026, and its season state at the 2026-11-10 join
is the proof's headline: the 2026 season is complete (ended
2026-10-30) and the 2027 season has not started (the League of
Ireland starts around February), so FotMob listed no upcoming
fixtures in either proof run — IE predicted 0, settled 0, and
errored on nothing, and its daily CSV is header-only. Two full
end-to-end proof runs (35 leagues, 79 markets) each produced
10,677 predictions with zero errors anywhere; the second run
fetched nothing new in any league (`fetched_new` 0 in all 35),
the run logs were identical ignoring timestamps, and every
output was bit-identical between the runs (186 files, md5 sets
equal). Both runs were made with `MALLOC_ARENA_MAX=2`, which
changes no output.
TH-ThaiLeague has joined with corners (arm gate_zero, CLEAN PASS in
`reports/C_TH_VERDICT.md`: virgin LL 0.6994 at the primary 9.5 line,
calibration +0.62pp against a 1.0pp boundary) and total shots
(arm B, PROVISIONAL PASS in `reports/T_TH_VERDICT.md`: virgin LL
0.6908 at the primary 26.5 line, calibration −1.03pp within 1 SE of
3.23pp). Goals, SOT, and cards failed their dev gates and are
excluded. Corners configuration is primary 9.5, ladder
8.5/9.5/10.5, halves share 0.4622, 1H ladder 3.5/4.5/5.5, and 2H
ladder 4.5/5.5/6.5; total shots is primary 26.5, ladder
25.5/26.5/27.5, halves share 0.4522, 1H ladder 11.5/12.5/13.5, and
2H ladder 13.5/14.5/15.5 — all read from the league's frozen
preregs and `config.yaml` and cross-checked against the shipped
virgin predictions. No runner dispatch change was needed: the
corners calls match the engine's signatures exactly
(`FeatureBuilder` / `fit_params` / `model_prediction` /
`over_prob`, with the engine's fit scoring at the registered 9.5
line), and the arm-B dispatch (the SCO/USL/RU precedent) calls
exactly the composition TH ships — TH's total-shots `model.py` is
identical to RU-PremierLeague's, and TH's B parameters match the
verdict (lambda 100, r_A 107.848, level cell (30, 0.5, 50)). One
engine defect was found and fixed: TH's `fitted_params.json`
carried no `half_split`, which the arm-B dispatch reads, so the
file would have crashed the runner; it now carries
[0.4522, 0.5478], the frozen constant the shipped virgin
predictions use (their 1H/FT ratio is 0.4522 on every row). The
data builder needed the usual two fixes: its frozen 1,262-match
count was a hard equality — a bug for a league whose 2026/2027
season is still running — now a floor, and it ignored the
runner's INDEX/MAIN_REPO globals (it read the index from a
hard-coded main-checkout root via argparse); it now follows the
runner contract, with the explicit CLI override preserved. The
builder encodes missing values as empty fields: there are no
'nan' strings anywhere in either CSV, the `BallPossesion` casing
is the standard one, no team name is non-ASCII, and corners and
total shots are missing on exactly the 240 score-only 2021/2022
rows (the stats era starts 2022/2023), which both adapters drop.
TH-ThaiLeague is a world league (Thailand, `Thai League`, FotMob
id 8984) over seasons 2021/2022–2026/2027, a clean 240-match
double round-robin per complete season (1,262 matches and 2,524
team rows at the join: five complete seasons plus 62 played in
2026/2027); at the join FotMob listed exactly the remaining 178
fixtures of 2026/2027 (from 2026-11-21), all predicted in both
markets with zero errors, and nothing settled (every ledger entry
is a future fixture; the TH ledger holds 356 entries with no
duplicate (market, match_id, run_date) key). On the full current
history the live corners fit is gamma 0.15, r 1.1461, beta
[0.0, 0.0], fit_n 1,012 (the virgin fit was r 1.1285 on n 710).
An independent recompute of the first joined fixture (1000017781,
Pattani FC–Sukhothai FC, 2026-11-21) through TH's own engines in
a separate process matched all twelve daily-CSV fields with max
difference 0.0 in each market, and a synthetic settlement on
match 1000017780 (Ratchaburi FC–Buriram United, 2026-11-08)
graded corners actual 9.0 and total-shots actual 35.0 correctly,
settled each market exactly once (a second pass settled nothing),
and left the artifacts md5-clean. Two end-to-end proof runs
(runner date 2026-11-09; 35 leagues, 80 markets) each produced
11,033 predictions with zero errors anywhere and fetched nothing
new in any league in either run; every output was bit-identical
between the runs (256 files, md5 sets equal). The first attempt
at run 1 was OOM-killed at the AR-LigaProfesional rebuild after
seven leagues with zero errors; its full rerun completed in
about 36 minutes and run 2 in about 26 minutes. All completed
runs were made with `MALLOC_ARENA_MAX=2` on the runner process,
which changes no output.
ZA-PSL has joined with corners only (arm `gate_zero`, PROVISIONAL
PASS in `reports/C_ZA_VERDICT.md`: virgin LL 0.6977 at the primary
8.5 line, calibration −3.35pp with the excess over the 1.0pp
boundary within 1 SE of 3.24pp; goals, SOT, cards, and total shots
all failed their gates and are excluded). Configuration is primary
8.5, ladder 7.5/8.5/9.5, halves share 0.4679, 1H ladder 3.5/4.5/5.5,
and 2H ladder 4.5/5.5/6.5, read from the frozen prereg and
cross-checked against the shipped virgin predictions (240 rows).
The data builder needed two changes. Its three hard-equality
assertions (1,255 index rows, 12 excluded, 1,243 built) are now
floors on those frozen counts: ZA season sizes vary — 240 matches
in a normal season, 210 in 2024/2025 (15 teams after Royal AM's
expulsion), and 2026/2027 is in progress (73 played at the join) —
so an exact count would become a bug. And the builder now follows
the RU-1Division contract (`MAIN_REPO`/`INDEX` module globals,
with the `--warehouse-root` CLI override kept): before, `main()`
read only its argparse default pointing at the main checkout and
ignored the globals the runner sets, so a worktree rebuild would
silently have read the main checkout's index. The runner has no
phase filter (the FR/RO precedent) and none was added: the 12
Qualification Group play-off rows in the world index (six in
2021/2022, six in 2022/2023) are excluded by the builder itself,
which drops any payload whose `leagueName` contains
"Qualification" and stamps every kept row `regular`. Those 12
match files already sit in the warehouse store, so the world pull
fetched none of them in either proof run, and the rebuilt CSV
(1,243 matches, 2,486 team rows) contains none of their ids. No
season exclusion is needed: 2021/2022 carries no statistics at all
(corners present on 0 of its 240 rows), so the corners adapter's
own filter drops the whole season, exactly matching the frozen
harness's 2022/2023-onward load. Missing values are empty fields
throughout — there are no `nan` strings in any cell of the built
CSVs — and the possession columns keep FotMob's `BallPossesion`
spelling, which the adapter reads first. Team identity is the
join's sharpest check, and it passes: the corners core and the
runner adapter key every piece of state (shot history, territorial
windows, trailing-10) on the FotMob team id, never on names, and
ZA names are not self-consistent enough to key on — three ids
carry two names inside the live fit window itself (102099 appears
as both SuperSport United and Siwelele in each of 2022/2023,
2023/2024, and 2024/2025; 149599 as both Maritzburg United and
Durban City within 2022/2023; 102100 as AmaZulu FC on 155 rows and
AmaZulu on 2). Id-keying reproduces the gated product exactly: an
engine-only recompute of the virgin returned the frozen fit
(gamma 0.15, r 1.1077477721640459, beta [0.0, 0.0], fit_n 676) and
matched all 240 shipped virgin predictions at 0.0, and a replay of
the first virgin fixture (4909914, AmaZulu FC–Orbit College,
2025-08-09) through `predict_corners` on the pre-virgin history
matched all twelve shipped fields at 0.0. On the full current
history at the join the live fit is gamma 0.15, r 1.1493355197088353,
beta [0.0, 0.0], fit_n 989, and an independent engine-only recompute
of the first live fixture (5955125, Durban City–Polokwane City,
2026-11-24 — Durban City is itself renamed id 149599) matched all
twelve daily-CSV fields at 0.0. A synthetic settlement on match
4909914 graded corners actual 8.0 (7 + 1) at the 8.5 line, settled
exactly once, and left the artifacts clean. ZA-PSL is a split-year
world league (South Africa, `Premier Soccer League`, FotMob id
537, ccode RSA) over seasons 2021/2022–2026/2027; its 2026/2027
season is in progress, and both proof runs predicted all 160
upcoming fixtures (2026-11-24 to 2027-05-22) with no errors. Two
full end-to-end proof runs (37 leagues, 81 markets) produced
11,016 and 11,013 predictions with zero errors anywhere; the
second run fetched nothing new in any league (`fetched_new` 0 in
all 37, as did the first), and ZA's own outputs (daily CSV,
ledger, both data CSVs) are bit-identical between the runs. The
3-prediction difference is CO-PrimeraA's single upcoming fixture
vanishing from FotMob's listing between the runs (one fixture in
each of its three markets; its data CSV is unchanged and nothing
was fetched). Of the 266 snapshot files compared, 261 are
bit-identical; the exceptions are CO's three header-only daily
CSVs and BR-SerieB's corners and SOT daily CSVs, whose numbers
differ from the first run's ledger by at most 1.6e-14 (corners)
and 3.0e-4 in exp_total (SOT) on identical inputs — pre-existing
BR run-to-run variation, untouched by this join. The proof pair
took several attempts to land: earlier launches of the second run
were killed by two VM reboots and by memory pressure while other
joins ran concurrently, and one was aborted during a brief
filesystem-wide `EPERM` window that also broke git index writes;
the completed pair and all checks above ran with
`MALLOC_ARENA_MAX=2`, which changes no output.
CZ-Liga has joined with corners only (arm `gate_zero`, PROVISIONAL PASS in
`reports/C_CZ_VERDICT.md`: virgin LL 0.675211 at the primary
10.5 line, calibration +3.06pp within 1 SE of 2.99pp). SOT
(arm `GZ`, PROVISIONAL PASS in `reports/S_CZ_VERDICT.md`:
virgin LL 0.666555 at the primary 8.5 line, calibration
−1.09pp within 1 SE of 2.97pp) is HELD at the operational
gate — see the diacritic name-split defect below — and joins
only after the canonical-name fix proves gated-product
invariance. Goals and cards failed their gates and total
shots was not buildable, so all three are absent. Corners is
FT-only: period splits exist in this feed only from 2025/2026,
inside the virgin season itself, so the league's frozen config
sets `halves_share_1h: null` and the shipped virgin
predictions carry the FT ladder only (corners 9.5/10.5/11.5;
the SOT config likewise freezes halves null). Corners already
had the runner's FT-only opt-in (RU-1Division); SOT did not —
`predict_sot` read the share unconditionally and the null
crashed it (TypeError) — so this join extends the identical
opt-in to `predict_sot`, documented above with the other
opt-ins; the code lands now, inert, with no active FT-only
SOT market yet — the CZ SOT fix join will be its first user.
The amendment is inert for existing leagues: an old-versus-new
probe of `predict_sot` on CZ history with a numeric share
returned bit-identical rows, an absent key raises the same
`KeyError` in both versions, and every pre-existing league's
outputs were unchanged across the proof runs below. Neither CZ
engine needed a change: the SOT engine already accepts the
runner's `ratio_prior` keyword (200 for GZ, the AU pattern)
and its own `load_matches` is the history filter the harness
uses; the corners core's signatures match the adapter exactly
(`FeatureBuilder` / `fit_params` / `model_prediction` /
`over_prob`, and its fit grid hard-codes the registered 10.5
primary). `div: CZ-Liga` is set because the engine keys its
regression store on the CSV's `league` value. The data builder
needed no change either: its only assertion is match-id
uniqueness, not a frozen count, and it already honours the
runner's `INDEX`/`MAIN_REPO` globals, so the growing
2026/2027 season cannot trip it. No `exclude_seasons` is set for corners: the gated harness loads the full
2021/2022-onward history (2021/2022 is the corners seed), and the stats-missing rows are dropped by the
engine's own completeness rules, exactly as in the harness.
Missing values are empty fields throughout — there are no
`nan` strings in either CSV; exactly 12 rows (4 in 2021/2022,
7 in 2023/2024, 1 in 2024/2025) lack the whole stats feed, so
corners, total shots, and SOT are missing together and no row
has corners without total shots; `big_chance_*` and
`touches_opp_box_*` exist only from 2025/2026 (empty on 1,104
rows) and the shipped Gate Zero corners arm does not read
them. The modelled corpus is 270 matches per complete season
(240 regular + 15 championship + 15 relegation, placement
excluded by the league); at the join the builder wrote 1,492
matches and 2,984 team rows (1,461 included). The runner has
no phase filter (the FR/RO precedent): the 30 stats-complete
placement rows enter the corners history and fit like any other
fixture (live fit gamma 0.0,
r 1.1541233943815075, beta [0.0], fit_n 1,467, versus
r 1.1611131287071759 and fit_n 1,437 through the engine's own
placement-free load — gamma and beta coincide; only the
dispersion moves), and a future placement fixture in the
FotMob payload would be predicted in corners like any other
fixture. No filter was added. One defect is recorded
plainly: FotMob writes six CZ clubs under two name spellings —
ASCII in the dev/virgin era (`Banik Ostrava`) and diacritic
forms in 2026/2027 (`Baník Ostrava`; likewise Hradec Králové,
Viktoria Plzeň, Mladá Boleslav, Slovácko, and FC Zlín, which
also carries the historical `FC Fastav Zlin` / `FC Zlin`
spellings) — and the payloads mix both spellings even within
2026/2027 (50 of the 111 played rows carry a diacritic name).
The CSVs round-trip both spellings exactly (UTF-8 throughout),
and the corners adapter keys on team_id, so corners is
unaffected; but the SOT engine keys team state on the name
exactly as shipped and gated, the upcoming-fixture payload
uses the diacritic spellings, and each diacritic spelling
carries only 9–11 appearances of history against 138–180 for
the ASCII spelling, so SOT predictions for those six clubs
rest on their short diacritic-keyed history plus league means.
The effect is material on the sampled fixture: Baník
Ostrava–Teplice (2026-11-21) predicts exp_total 8.6235 and
P(over 8.5) 0.5437 under the diacritic key, against 8.4732 /
0.4519 under the ASCII key. No keying change was made in this
join — id-keying would be a different product from the one
that passed the gate (the ES engine was id-keyed by design;
CZ's is name-keyed by design), and the virgin window predates
the diacritic spellings, so the gate never measured this.
The SOT market therefore stays out of `active.yaml` until the
canonical-name fix lands; this join ships corners only.
CZ-Liga is a world league (Czechia, `1. Liga`, FotMob id 122,
ccode CZE) over seasons 2021/2022–2026/2027; the 2026/2027
season is in progress (111 played at the join), and at the
join FotMob listed its remaining 129 regular-phase fixtures
(from 2026-11-21), all predicted in corners with zero
errors, and nothing settled (every ledger entry is a future
fixture; the CZ ledger holds 129 entries with no duplicate
(market, match_id, run_date) key). In the branch proof, an
independent recompute of the first joined fixture (5943699,
Artis Brno–Jablonec, 2026-11-21) through CZ's own engines in
a separate process matched all four FT fields with max
difference 0.0 in each market and confirmed all halves fields
empty (with the live corners fit above at gamma 0.0 and beta
[0.0], the corners expectation is the league base total for
every fixture at this fit, 10.0845 to four decimals, varying
only at the 1e-14 level across fixture dates), and a synthetic
settlement on match 5943698 (Slavia Prague–Artis Brno,
2026-11-08) graded SOT actual 12.0 and corners actual 11.0
correctly on the FT lines, settled each market exactly once
(a second pass settled nothing), and left the artifacts
md5-clean. Two end-to-end
proof runs on 2026-11-10 (38 leagues, 84 markets) completed
with zero errors anywhere; run 1 produced 11,470 predictions
and run 2 produced 11,467, fetched nothing new in any league
in either run (every played CZ match was already in the shared
warehouse), and settled nothing. Of 277 compared files, 271
were bit-identical between the runs, including every CZ-Liga
output; the six exceptions are the append-only run log and two
pre-existing leagues whose FotMob payloads moved between the
runs — CO-PrimeraA's only upcoming fixture (1000014224, Junior
FC–Cúcuta, dated 2026-11-10) left the upcoming list between
the runs, so its three daily CSVs are header-only in run 2
(its details file is in no store, so it never entered the
rebuilt CSV and nothing settled), and BR-SerieB's Ponte
Preta–Operário-PR fixture (5190809) was re-listed from
2026-11-14 to 2026-11-12, moving its own SOT expectation by
0.0003 and five other fixtures in its date group by at most
2e-15. Four further attempts were lost to infrastructure and
are recorded plainly: the first attempt at run 1 was killed by
a VM reboot after four leagues with zero errors and was rerun
in full (48 minutes; run 2 took 58 minutes); the first run-2
attempt hit a transient `PermissionError` episode
(02:07:55–02:09:41 UTC) that failed MX-LigaMX's corners settle
step and the IN-ISL through EG-PremierLeague league steps —
an isolated re-test of the failed settle passed minutes later
and the episode did not recur — and was stopped and rerun; its
replacement was killed by a VM reboot at MX-LigaMX, and the
next attempt was OOM-killed (exit 137) at NL-Eredivisie under
concurrent proof load from sibling worktrees. All completed
runs were made with `MALLOC_ARENA_MAX=2` on the runner process,
which changes no output. Merge note (coordinator, 2026-11-10):
that proof pair ran the branch's both-markets configuration;
the merge ships corners only — the SOT market was removed
from `active.yaml` at merge (operational gate, diacritic
defect above) — so the live runner is 39 leagues / 84
markets. The merged state was re-verified with a one-league
run from the main checkout (`run_one_league_cz.py`): CZ
corners reproduces the branch proof's daily file bit-identical
(md5 11704bec79d6c3c100e8312953a4dbc3), 129 fixtures,
fetched_new 0, 0 settled, rebuilt CSVs md5-identical to the
proof (1,492 matches / 1,461 included). The CZ SOT fix takes
the next join slot.


BG-FirstLeague has joined with SOT (arm GZ, PROVISIONAL PASS in
`reports/S_BG_VERDICT.md`: virgin LL 0.6487 at the primary 8.5
line, calibration −2.74pp within 1 SE of 2.79pp of the 1.0pp
boundary), corners (arm gate_zero, CLEAN PASS in
`reports/C_BG_VERDICT.md`: virgin LL 0.6838 at the primary 9.5
line, calibration +0.38pp), and total shots (arm A, CLEAN PASS
in `reports/T_BG_VERDICT.md`: virgin LL 0.6611 at the primary
17.5 line, calibration +0.77pp). Goals and cards failed their
gates and are excluded. All three markets are FT-only: this
league's feed has no period splits in any season
(`has_period_splits_content` is 0 on all 1,471 built rows, the
halves constants for these markets are null in its frozen
config, and the shipped virgin predictions carry FT ladders
only), so all three market blocks set `halves_share_1h: null`.
Corners already had that opt-in (RU-1Division); the SOT
opt-in is the identical code that landed with the CZ-Liga
join, and this join extends the same opt-in to all three
total-shots arms, and for total shots it also removes the
`fitted_params.json` `half_split` requirement (BG's file
carries none). SOT configuration is primary 8.5, ladder
7.5/8.5/9.5, div BG-FirstLeague, ratio prior 200 — the engine
accepts the runner's `ratio_prior` keyword exactly as the AU
engines do; corners is primary 9.5, ladder 8.5/9.5/10.5, and
its engine's `fit_params` grid scores at the registered 9.5
line; total shots is primary 17.5, ladder 16.5/17.5/18.5,
lambda 100.0, r_A 8186.5. Keying follows each engine: corners
and total shots key team state on the FotMob team id, while
the SOT engine keys on the team name — and BG has two ids with
unstable names (10144 appears as CSKA Sofia, CSKA-Sofia, and
PFC CSKA-Sofia; 10135 as Etar and Etar Veliko Tarnovo) — so
the SOT adapter passes names exactly as the engine's
`load_matches` does, with no `team_key` opt-in; the name
variants sit in the fitted regression's team list as separate
entries, as they did for the virgin predictions. The data
builder needed the usual two fixes: its frozen phase-count
table and 1,471-match count were hard equalities — now floors,
because season sizes vary (182 regular-phase matches in
2021/2022, 240 in each later complete season, split phases on
top, and 2026/2027 is back to 14 teams and still running) —
and it ignored the runner's INDEX/MAIN_REPO globals; it now
follows the runner contract, with the explicit CLI override
preserved. The builder encodes missing values as empty fields:
there are no `nan` strings in either CSV, the `BallPossesion`
casing is the standard one, `big_chance` and
`touches_opp_box` are empty on every row (absent from the feed,
as the corners prereg recorded in advance), and the stats
columns are empty on exactly the 24 score-only rows, which the
adapters drop. BG-FirstLeague is a world league (Bulgaria,
`First Professional League`, FotMob id 270) over seasons
2021/2022–2026/2027 (1,471 matches and 2,942 team rows at the
join: five complete seasons plus 97 played in 2026/2027); at
the 2026-11-10 join, FotMob listed the remaining 85 fixtures
of 2026/2027 (2026-11-20 to 2027-04-17, split phases included
as listed), all predicted in all three markets with zero
errors, and nothing settled (the ledger holds 255 entries, 85
per market, no duplicate keys). An independent recompute of
the first fixture (5760536, Septemvri Sofia–Lokomotiv
Plovdiv, 2026-11-20) from the engine code alone matched every
FT field with max difference 0.0 in each market and confirmed
all halves fields empty (corners live fit gamma 0.15,
r 1.2495, beta [0.0, 0.0], fit_n 1,437), and a synthetic
settlement on match 5760520 (Levski Sofia–CSKA Sofia,
2026-11-08) graded SOT actual 11.0, corners actual 6.0, and
total-shots actual 15.0 correctly on the FT lines, settled
each market exactly once (a second pass settled nothing), and
left the artifacts md5-clean. Two end-to-end proof runs on
2026-11-10 (38 leagues, 85 markets) each completed with zero
errors and 11,464 predictions; the second fetched nothing new
in any league, and every output was bit-identical between the
two (389 compared files, including both FotMob indexes), so
the FT-only amendments changed no pre-existing league's
numbers. The first completed run before them fetched nothing
new anywhere either (11,467 predictions) and differs from the
proof pair only in CO-PrimeraA (one match, 1000014224, Junior
FC–Cúcuta, finished during the proof window and settled in
CO's three markets; its single added world-index line is
committed with this join, following the RO-LigaI precedent)
and in BR-SerieB's two daily CSVs, whose values moved only at
floating-point level (at most 3.0e-4 on one SOT expectation,
the rest at 1e-13 or below — the SOT regression's iterative
fit under that hour's load; a later direct recompute of
BR-SerieB SOT reproduced the proof pair's values exactly).
The road to the completed pair was rough and is recorded
plainly: the first attempt at the second run was killed by a
VM reboot after six leagues, its rerun died silently at the
AR-LigaProfesional rebuild (no traceback; the box was under
load average ~29 from parallel programme work), and two
further attempts collapsed under a system-wide intermittent
write block (`PermissionError: Operation not permitted` on
ordinary file writes, observed independently of the runner);
both collapsed attempts left every output file byte-identical
to before, verified by md5. All completed runs were made with
`MALLOC_ARENA_MAX=2` on the runner process, which changes no
output. Merge note (coordinator, 2026-11-10): the branch was
based on an older runner (37 leagues / 82 markets); the merge
lands after the CZ-Liga join, so the live runner is 40
leagues / 87 markets. The only code overlap was the SOT
FT-only opt-in, which both joins implemented identically —
the merged file keeps one copy. The merged state was
re-verified with a one-league run from the main checkout
(`run_one_league_bg.py`): all three BG daily files and both
rebuilt data CSVs are bit-identical to the branch proof
(corners md5 73e9616cf9c66db551dce36f111c3d54, SOT
a06d42bb8d3ca881c83a4e0b3246d6dc, total shots
5c509bc04d247ea6c349ad574d890a8d), 85 fixtures in each
market, fetched_new 0, 0 settled, ledger 255 entries.

CL-LigaDePrimera has joined with SOT (arm `RS`, PROVISIONAL PASS in
`reports/S_CL_VERDICT.md`: virgin LL 0.669732 at the primary 8.5
line, calibration −2.56pp within 1 SE of 3.16pp), corners (arm
`gate_zero`, PROVISIONAL PASS in `reports/C_CL_VERDICT.md`: virgin
LL 0.694482 at the primary 9.5 line, calibration +1.86pp within
1 SE of 3.24pp), and total shots (arm `A`, CLEAN PASS in
`reports/T_CL_VERDICT.md`: virgin LL 0.638337 at the primary 25.5
line, calibration −0.65pp). Goals and cards failed their dev gates
(virgin not read) and are excluded. SOT configuration is primary
8.5, ladder 7.5/8.5/9.5, halves share 0.4456, `div:
CL-LigaDePrimera`, ratio prior 20000, 1H ladder 2.5/3.5/4.5, 2H
ladder 3.5/4.5/5.5. The SOT engine accepts the runner's
`ratio_prior` keyword exactly as the AU engines do, and the value
is load-bearing: with 20000 the engine reproduces all 240 shipped
virgin predictions to 5.8e-15, while the runner's default of 200
differs by up to 0.416 — the config therefore carries 20000
explicitly (the PE-Liga1 RS pattern). Corners is primary 9.5,
ladder 8.5/9.5/10.5, halves share 0.4644, 1H ladder 3.5/4.5/5.5,
2H ladder 4.5/5.5/6.5; on the virgin the two registered arms are
numerically identical (both fits select gamma 0.0, r
1.085980122368, beta [0.0], fit_n 981, and both reproduce the
shipped predictions at 0.0), so the simpler Gate Zero ships, and
its core's fit grid hard-codes the registered 9.5 primary, as the
reference cores do. Total shots is primary 25.5, ladder
24.5/25.5/26.5, halves share 0.4535, 1H ladder 10.5/11.5/12.5, 2H
ladder 12.5/13.5/14.5 (the runner's arm-A default line sets),
lambda 300.0, r_A 172.0647; a walk-forward replay of arm A
reproduces the shipped virgin predictions to 3.4e-8 on the point
estimate (the regression solver's convergence level; the
probabilities agree to 2.5e-9). One adapter amendment was
genuinely needed: CL's frozen `fitted_params.json` carries no
`half_split` (every other non-FT-only league's carries one), so
`predict_total_shots` arm A now falls back to the market's
`halves_share_1h` config when `half_split` is absent — documented
with the other opt-ins above. The amendment is inert for existing
leagues: an old-versus-new probe of `predict_total_shots` returned
bit-identical rows on NL-EersteDivisie, BG-FirstLeague (FT-only),
PE-Liga1, and J1, and every pre-existing league's outputs were
unchanged across the proof runs below except the one ZA-PSL file
noted there. Halves presentation follows the league's frozen
constants (period splits exist from 2023: 873 of the 1,448 built
rows carry first/second-half splits); the league freezes no halves
ladders, so the 1H/2H line sets are the runner's defaults for
these adapters, and the shipped virgin CSVs carry FT ladders
only. (The T-CL prereg's Outputs parenthetical claims FT-only
presentation and no halves constant; that contradicts the same
prereg's Halves bullet, the league config, and the verdict, which
govern.) The data builder needed no change: its only assertion is
already a floor (`>= 1448` matches), it honours the runner's
`INDEX`/`MAIN_REPO` globals (verified by a simulated runner
import: 1,448 matches, 2,896 team rows), missing values are empty
fields (no `nan` strings in either CSV; corners, SOT, and total
shots are missing together on exactly 3 rows — 1 in 2022, 2 in
2026 — which the adapters drop), and its `BallPossesion` casing
is the standard one. Keying follows each engine: the builder
canonicalises team names by FotMob id (four ids carry multiple
raw spellings — Unión La Calera, Curicó Unido, Ñublense, and
Universidad Católica each also appear in an ASCII or older form),
the SOT engine keys on those canonical names, and corners and
total shots key on the team id. All 24 upcoming payload names at
the join match the canonical CSV names exactly, so CL has no
CZ-type SOT name split. One documentation defect in the league
build is recorded plainly: the engine READMEs under
`league/CL-LigaDePrimera/engine/` state wrong primary lines
(SOT 7.5, corners 8.5, total shots 15.5 — stale template copies);
the preregs, verdicts, shipped virgin predictions, and the
engines' own fit grids all agree on 8.5 / 9.5 / 25.5, and those
govern. CL-LigaDePrimera is a calendar-year world league (Chile,
`Liga de Primera`, FotMob id 273, ccode CHI) with a single
round-robin and no Apertura/Clausura or play-off phase in the
feed (every built row is phase `regular`), over seasons
2021–2026 (272 matches in 2021, 240 in each of 2022–2025, 216
played in 2026 at the join; the virgin is the complete 2025
season). At the 2026-11-10 join, FotMob listed the remaining 24
fixtures of 2026 (from 2026-11-20), all predicted in all three
markets with zero errors, and nothing settled (the ledger holds
72 entries, 24 per market, no duplicate keys). The live corners
fit is gamma 0.15, r 1.1354203407175327, beta [0.0], fit_n 1,435.
An independent recompute of the first fixture (1000013269,
Cobresal–Audax Italiano, 2026-11-20) from the engine code alone
matched all twelve daily-CSV fields with max difference 0.0 in
each market, and a synthetic settlement on match 1000013267
(Universidad de Concepción–O'Higgins, 2026-11-08) graded SOT
actual 11.0, corners actual 7.0, and total-shots actual 32.0
correctly on the FT lines, settled each market exactly once (a
second pass settled nothing), and left the artifacts md5-clean.
Two end-to-end proof runs on 2026-11-10 (41 leagues, 90
markets) each completed with zero errors and 11,825 predictions; both
fetched nothing new in any league (every played CL match was
already in the shared warehouse), and nothing settled. Of 442
compared files, 440 were bit-identical between the runs,
including every CL-LigaDePrimera output and both FotMob indexes;
the exceptions are the append-only run log and ZA-PSL's corners
daily CSV — a pre-existing league untouched by this join: its FT
values in run 2 are bit-equal to run 1's ledger values on all 160
fixtures (exp_total and all three ladder lines at 0.0) and a
fresh process reproduces the run-2 file exactly, so the delta is
confined to the non-ledger fields (derived halves values and/or
the payload name spellings ZA is documented to be unstable for).
All runs were made with `MALLOC_ARENA_MAX=2` on the runner
process, which changes no output.
CN-SuperLeague has joined with SOT (arm `GZ` — the arm the S-CN
verdict, virgin predictions, and `fitted_params_virgin.json` label
`GZ`, i.e. Gate Zero; PROVISIONAL PASS: virgin LL 0.6667 at the
primary 9.5 line, calibration +1.16pp within 1 SE of 3.15pp; the RS
arm failed the prereg's dev sign leg and is ineligible), cards
(gate_zero, PROVISIONAL PASS: virgin LL 0.6752 at the primary 3.5
line, calibration +1.98pp within 1 SE of 3.18pp), and total shots
(arm B, PROVISIONAL PASS: virgin LL 0.6556 at the primary 26.5
line, calibration +3.20pp within 1 SE of 3.11pp; arm C failed
virgin leg (i)). Goals and corners failed their gates and are
absent. CN is a calendar-year world league (FotMob 120, CHN; the
world index spells it country `China`, league `Super League`,
which are also the warehouse path) over seasons 2021–2026. All
three markets fit on the frozen era 2023+ only (2021/2022 are
excluded eras), so each market block carries
`exclude_seasons: ["2021", "2022"]`. SOT configuration is primary
9.5, ladder 8.5/9.5/10.5, halves share 0.4580, 1H ladder
3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5, `div: Super League` (the
matches CSV's `league` value), ratio prior 200, and
`team_key: id`; cards is primary 3.5, ladder 3.5/4.5 (the frozen
shipped ladder), halves share 0.3328, 1H ladder 0.5/1.5/2.5, 2H
ladder 1.5/2.5/3.5; total shots arm B is primary 26.5, ladder
25.5/26.5/27.5 (read from the engine's `fitted_params.json`),
halves share 0.4594, 1H ladder 11.5/12.5/13.5, 2H ladder
13.5/14.5/15.5. The virgin arbiters pin every value: replaying
the shipped virgin predictions through CN's own engines in
harness order reproduces all 240 SOT rows at max difference
7.4e-15 with the era filter and prior 200 (prior 20000 differs
by up to 0.409, and loading all seasons differs by up to
0.260, so both the explicit prior and the era exclusion are
load-bearing even though 200 is also the runner default), all
240 cards rows at exactly 0.0 with the era filter and the
stats-feed target (the fitted r 38.879133 is reproduced
exactly; all-seasons loading differs by up to 0.110 and the
event-feed target by up to 0.378), and all 240 total-shots
arm-B rows at 3.3e-9 with the era filter (all-seasons loading
differs by up to 0.552). Three adapter amendments were needed,
all opt-in or fallback-only. First, `predict_sot` now honours a
market `exclude_seasons` key (the corners/arm-C precedent) and,
under `team_key: id`, casts fixture ids to int when the loaded
history's keys are ints: CN's SOT engine keys team state on the
FotMob team_id as an int (CSL clubs rename across seasons, so
name keying would split histories), while ES-LaLiga2's keys are
strings and stay strings. Second, `predict_cards` resolves its
history columns to `yellow_cards_home`/`yellow_cards_away` when
the `yellow_home`/`yellow_away` alias is absent from the CSV
header, and honours `exclude_seasons`: CN's builder writes no
alias — its frozen stats-feed target lives directly under the
`yellow_cards_*` columns, which are also the runner's
settlement default, so CN cards needs no `cards_actual`
override (the gate graded the stats feed, not an event-unified
target; the prereg's event-target sensitivity is not the graded
product). Third, `predict_total_shots` arm B falls back to the
market's `halves_share_1h` when `fitted_params.json` carries no
`half_split` (the arm-A CL fallback, extended to arm B; CN is
the only arm-B league without one) and honours
`exclude_seasons`. Inertness was proven before the full runs:
an old-versus-new probe of the four touched adapter paths
returned bit-identical rows on ES-LaLiga2 SOT (string-id path),
NL-Eredivisie SOT (name path, no exclusion key), AU-ALeague
cards (alias present), and SCO-Premiership total shots arm B
(`half_split` present). Two builder defects are recorded, not
fixed here (the join commit touches runner files only): the CN
builder asserts its frozen count as a hard equality
(`len(rows) == len(index_rows) == 1442`), and it does not
honour the runner's `INDEX`/`MAIN_REPO` globals — its `main()`
reads its own argparse `--warehouse-root` default, which
coincides with the worktree root, so a runner rebuild resolves
the warehouse through the worktree's symlink and works. The
equality cannot trip under the configured seasons — every
season 2021–2026 is complete in the index (176 + 306 + 240 x 4
= 1,442) — but the assert must become a floor before a 2027
season is added to the configuration, or the first daily
rebuild of that season will fail. Missing values are empty
fields throughout (no `nan` strings in either CSV), and no
joining market keys on team names, so there is no
canonicalisation question. At the 2026-11-10 join the 2026
season is complete (240 of 240 played, last matchday
2026-11-08), so FotMob lists no unplayed CN fixtures: both
proof runs predict zero CN fixtures and settle nothing, and a
run will keep predicting zero until the 2027 season is listed
and configured. The adapters were exercised on a synthetic
2027-01-15 fixture (Zhejiang Professional–Henan FC): an
engine-only recompute in a separate process matched the
runner's output on every field at 0.0 difference in all three
markets (live cards r 52.8269 over the 960 era matches; the
arm-B level factor is active at 1.0126, not inert). A
synthetic settlement on match 5186644 (Zhejiang
Professional–Henan FC, 2026-11-08) graded SOT actual 12.0,
cards actual 2.0 (stats feed, 0+2), and total-shots actual
37.0 correctly, settled each market exactly once (a second
pass settled nothing), and left the artifacts md5-clean. Two
full end-to-end proof runs on 2026-11-10 (42 leagues, 93
markets) each completed with zero errors and 11,825
predictions; the second run fetched nothing new in any league
(the first run fetched nothing either — the shared warehouse
was already current) and every per-market prediction count
was identical between the runs. Of 449 snapshotted output
files, 448 were bit-identical between the runs; the exception
is ZA-PSL's corners daily CSV, the pre-existing case already
recorded at the CL join — its run-2 FT values are bit-equal
to run 1's ledger values on all 160 fixtures, and the graded
ledger itself is bit-identical. The first second-run attempt
was cut by a SIGTERM after 24 leagues (no errors, nothing
fetched); its partial outputs were already bit-identical to
run 1's, and the completed second run followed. All runs were
made with `MALLOC_ARENA_MAX=2` on the runner process, which
changes no output.


The canonical-name fix has landed (see the `team_key:
canonical_name` opt-in above): CZ-Liga SOT (GZ, primary 8.5,
ladder 7.5/8.5/9.5, halves null, div CZ-Liga, ratio prior 200)
is active in `active.yaml` and the runner is 42 leagues / 94
markets. The invariance premise holds in substance:
canonicalisation is the identity on all 19 gated-era names
with zero canonical collisions, and a canonicalised
walk-forward replay reproduces the shipped virgin predictions
at exact 0.0 under the generation environment
(canonical-vs-raw 0.0 under the runner's interpreter too). One
literal exception is recorded plainly: club id 1860 carries two
ASCII spellings inside the gated eras (`FC Fastav Zlin`, seven
2021/2022 rows, beside `FC Zlin`) — neither carries a diacritic,
so the fix preserves the split exactly as gated and the replay
confirms it. Live effect on the sampled fixture: Baník
Ostrava–Teplice (2026-11-21) predicts exp_total 8.5077 and
P(over 8.5) 0.5362 with the opt-in, against 8.6235 / 0.5437
thin-keyed without it (the fixture-only ASCII rename gives
8.4732 / 0.4519 — the opt-in additionally merges the ten
diacritic 2026/2027 rows into the history). Two end-to-end
proof runs (39 leagues, 85 markets) completed with zero errors
and fetched nothing new in any league in either run (11,627
predictions in run 1, 11,630 in run 2); every output was
bit-identical between the runs except ENG-LeagueOne's three
daily CSVs and ledger, because FotMob added one fixture to its
listing between the runs (386 upcoming in run 1, 387 in run 2).
A synthetic settlement on match 5943698 (Slavia Prague–Artis
Brno, 2026-11-08) graded SOT actual 12.0 correctly, settled
exactly once, and left the artifacts md5-clean. Inertness was
verified on NL-Eredivisie and J1 (old-vs-new `predict_sot` max
difference 0.0). The proof pair took four attempts: the first
run 2 was lost to a filesystem-wide EPERM window (07:57–08:02
UTC) that failed whole league steps, and its rerun was killed
by a VM reboot two leagues from the end; both were rerun in
full, and a second EPERM strike during the synthetic
settlement truncated the CZ ledger to empty — the ledger was
rebuilt byte-identical from the daily CSVs via the runner's
own entry construction (md5-verified) before the settlement
was retried and passed. All completed runs were made with
`MALLOC_ARENA_MAX=2`, which changes no output.

CY-1Division has joined with corners (arm `gate_zero`, CLEAN PASS:
virgin LL 0.688133 at the primary 9.5 line, calibration −0.26pp) and
total shots (arm A, PROVISIONAL PASS: virgin LL 0.688140 at the
primary 18.5 line, calibration +1.468pp within 1 SE of 3.217pp; the
prereg dev over-rates are 0.452 for corners and 0.465 for total
shots, n=765 each). Goals, SOT, and cards failed their gates and
are absent. CY is a Cyprus 1. Division world league (FotMob 136,
CYP; the world index spells it country `Cyprus`, league
`1. Division`, which are also the warehouse path) over seasons
2021/2022–2026/2027, 1,271 matches and 2,542 team rows, of which
1,248 rows carry corners/shots stats. Both markets are FT-only
(`halves_share_1h: null`): corners is primary 9.5, ladder
8.5/9.5/10.5; total shots arm A is primary 18.5, ladder
17.5/18.5/19.5 (read from the engine's `fitted_params.json`:
lambda 300.0, r_A 39.77268245663654, level cell [120.0, 0.5, 50.0],
M_bar 24.9, trailing-r window 200). The virgin arbiters pin every
value: replaying the shipped virgin predictions through CY's own
engines in harness order reproduces all 239 corners rows at
exactly 0.0 on mu and p_over 8.5/9.5/10.5 (the fit check
reproduces the frozen params exactly: gamma 0.0, r
1.241313582648889, beta [0.005, 0.0], fit_n 935), while all 239
total-shots rows differ by at most 0.0802 on exp_total (worst
match 4878008) and 0.0064/0.0061/0.0060 on p_over 17.5/18.5/19.5.
The gap is decomposed, not hand-waved: an exact-harness walk
reproduces the shipped values to 7.1e-15, a walk refitting the
regression store at every match day reproduces the runner replay
to 1.47e-08, and the shipped values sit exactly on the harness's
7-day refit cadence — the harness refits the store every 7 days
(theta up to 7 days stale) while the replay fits fresh at each
fixture day, and the production runner uses the same 7-day
cadence as the harness (anchored at the run's first fixture
date), so the gap is a harness artefact, not a runner error. One
score-only virgin fixture is skipped by both arbiters (match
4877904, Pafos FC–APOEL Nicosia, 2026-02-04, no corners/shots
stats); the runner still predicts it from history. No adapter
amendment was needed: `run_daily.py` is untouched by this join.
Two builder items are recorded: the builder's hard-equality count
assert was floored to `>=` (1,271 matches, per-season/per-phase
floors; the AU/MLS pattern) in the join commit, and the builder
does not honour the runner's `INDEX`/`MAIN_REPO` globals — its
`main()` reads the index and payloads from the hard-coded
main-checkout root, which is inert in production (the runner runs
from the main checkout) and agreed with the worktree index at
proof time (1,271 CY rows, max date 2026-11-08).
`fitted_params_virgin.json` for total shots carries a stale
`primary_line: 17.5`, a defect in the shipped file that the runner
never reads (the runner reads `fitted_params.json`, primary 18.5).
A synthetic settlement on match 5975448 (Pafos FC vs Omonia 29
Maiou, 2026-11-08) graded corners actual 11.0 (pred exp 9.776,
p9.5 0.5043, hit, LL 0.6846) and total-shots actual 26.0 (pred exp
20.725, p18.5 0.6328, hit, LL 0.4576), settled each market exactly
once (a second pass settled nothing), and left the artifacts
md5-clean. Two full end-to-end proof runs on 2026-11-10 on the
rebased base (43 leagues, 95 markets on the branch base; 96 in the merged state, the +1 being CZ-Liga SOT which landed after the branch base) each completed with zero
errors, fetched nothing new in any league, and produced 12,066
predictions; CY predicts 119 upcoming fixtures in both markets,
spanning 2026-11-21 to 2027-03-06, the first 5975455 Omonia
Aradippou–Pafos FC 2026-11-21 (corners exp 9.069, p9.5 0.4204;
shots exp 20.748, p18.5 0.6336). Of 181 snapshotted output files,
180 were bit-identical between the runs; the exception is ZA-PSL's
corners daily CSV, the pre-existing case already recorded at the
CL join — its run-B FT values are bit-equal to the ledger on all
160 fixtures (0 mismatches on exp_total and p_over 7.5/8.5/9.5),
the graded ledger itself is bit-identical, and the difference is
confined to the non-ledger half-split columns. The CY files are
also bit-identical to a pre-rebase run on the old base (all four
md5s match), and the join commit was rebased onto cdb5a09b (the
DZ-Ligue1 merge, league #119) after the git-freeze lift,
replaying cleanly with no conflicts. All runs were made with
`MALLOC_ARENA_MAX=2` on the runner process, which changes no
output.

NO-OBOSLigaen has joined with corners only (arm `gate_zero`, PROVISIONAL PASS in `reports/C_NO_OBOS_VERDICT.md`: virgin LL 0.6898 at the primary 10.5 line, calibration +1.14pp with the 0.14pp excess over the 1.0pp boundary within one standard error of 3.24pp; dev LL 0.6969 beat both baselines, league base rate 0.7257 and naive trailing-10 0.7205; Gate Zero and PLAIN tied exactly on the virgin window — the virgin fit chose beta [0.0], so the possession multiplier is inactive and the two arms are identical — and the frozen tie rule ships the simpler arm, Gate Zero). Goals, SOT, cards, and total shots failed their gates or were not buildable and are excluded. Corners configuration is primary 10.5, ladder 9.5/10.5/11.5, and `halves_share_1h: null` — this league's feed has no period splits at all (its frozen config has `corners_1h_share: null` and the shipped virgin predictions are FT-only), so it uses the FT-only corners opt-in documented above (RU-1Division precedent): the runner writes the halves columns empty and predicts the FT ladder only. The data builder needed no change: its only count assert is `len(rows) == len(idx)`, a self-consistent check that grows with the index rather than a frozen build-time count, so there is no AU/MLS trap to floor. NO-OBOSLigaen is a world league (Norway, `OBOS-ligaen`, FotMob id 203) over calendar-year seasons 2021–2026 (1,440 matches and 2,880 team rows at the join: six complete 240-match seasons; the virgin is the complete 2026 season, 237 matches with a corners target); at the 2026-11-10 join FotMob listed no upcoming fixtures (the 2026 season ended 2026-11-08 and 2027 is not requested), so nothing was predicted and nothing settled — the daily corners CSV is header-only and the ledger holds no entries. An independent recompute through the real runner adapter reproduced the shipped virgin predictions exactly: the fit on the pre-virgin window (2021–2025) reproduces `fitted_params_virgin.json` bit-for-bit (gamma 0.15, r 1.165312214160854, beta [0.0], fit_n 1,080), and the apply replay over all 237 fixtures on 66 dates matched mu and all three ladder lines with max difference 0.0 and confirmed all halves fields empty. The production live refit on full history (2021–2026) keeps gamma 0.15 and beta [0.0] with r 1.1671928089114483 (fit_n 1,317); its predictions on the virgin fixtures differ by at most 0.0002 in p_over, which is the runner's by-design daily refit, not a defect — no adapter change to `run_daily.py` was needed. A synthetic settlement on match 5105318 (Sandnes Ulf–Åsane, 2026-11-08) graded corners actual 15.0 correctly on the FT line (live prediction exp_total 11.0629, P(over 10.5) 0.5379, chosen over, hit, log loss 0.62), settled exactly once (a second pass settled nothing), and left the artifacts md5-clean. Two end-to-end proof runs on 2026-11-10 (43 leagues; 92 markets in run 1, 95 in run 2) each produced 11,957 predictions; run 1 fetched 74,852 matches (a fresh worktree with an empty warehouse) with exactly one error row — CO-PrimeraA's league step, see below — and run 2 fetched nothing new in any league with zero errors. Of 366 compared files, 363 were bit-identical between the runs, including every NO-OBOSLigaen output; the exceptions are BR-SerieB's corners and SOT daily CSVs and ZA-PSL's corners daily CSV. ZA-PSL's FT values are bit-equal to run 1's ledger on all 160 fixtures (max difference 0.0), so its delta is confined to non-ledger fields, as documented for that league. BR-SerieB differs on a single fixture, 5190810 (São Bernardo–Athletic Club MG): FotMob rescheduled it from 2026-11-14 in run 1's pull to 2026-11-12 in run 2's pull — the ledger records the run-1 date — and the fixture date anchors both models' decay/refit computation, so SOT exp_total moved 8.48895 to 8.48875 (p_over shifts at most 0.000013, no side flip) and corners mu moved 1.4e-14; the other 13 fixtures in each market are bit-identical. CO-PrimeraA's six files appear only in run 2: it failed in run 1 because its builder also reads Primera B warehouse JSONs, which no runner league pulls and a fresh worktree lacks — a pre-existing cross-league warehouse dependency, not caused by this join; the Primera B files were populated from the main checkout's warehouse (no code change) and CO then rebuilt and predicted cleanly in run 2 (0 upcoming, 0 predicted). The proof pair took four launches: run 1 completed at the first attempt, and run 2's first attempt was cut short by a service restart two leagues in, its second was OOM-killed (exit 137) at the AR-LigaProfesional stage under heavy parallel load on this box, and its third completed. All completed runs were made with `MALLOC_ARENA_MAX=2`, which changes no output.

SE-Superettan has joined with cards only (arm `gate_zero`,
PROVISIONAL PASS: virgin LL 0.667511 at the primary 3.5 line,
calibration +3.77pp, breach within 1 SE of 3.14pp; the prereg
dev gate passed at LL 0.672526 vs base 0.690891). Goals, SOT,
corners, and total shots failed their gates and are absent
(corners passed dev and virgin leg (i) but died on virgin leg
(ii) calibration −6.63pp). It is a calendar-year world league
(FotMob 168, SWE, Sweden Superettan; seasons 2021–2026, 1,440
matches and 2,880 team rows). Cards is primary 3.5, ladder
2.5/3.5/4.5, halves yellows share 0.3344 — the frozen
league constant from event times on the dev era; the 1H/2H
p_over ladders use the runner defaults (0.5/1.5/2.5 and
1.5/2.5/3.5), the same values NO-Eliteserien and KR-KLeague1
configure explicitly. The gate target is event-derived unified
yellows (Yellow + YellowRed card events), which the builder
writes to `yellow_home`/`yellow_away`; X8 is impossible
(referee names empty in 1,440/1,440 payloads), so Gate Zero is
the only arm and there is no operational-gate question. No
adapter amendment was needed: `run_daily.py` is untouched by
this join. Settlement does need the per-market override
`cards_actual: [yellow_home, yellow_away]`, exactly as
NO-Eliteserien and KR-KLeague1: the runner's default cards
actuals are the stats-feed columns
`yellow_cards_home`/`yellow_cards_away`, which are empty on all
1,440 SE2 rows (the stats feed carries no card keys), so the
default path would settle nothing — a synthetic settlement on
match 5125446 (Helsingborg–Östers IF, 2026-04-03; unified 1+0=1)
settled 0 under the default and 1 under the opt-in (actual 1.0,
p3.5 0.5684, miss, LL 0.8401), a second pass settled 0, and the
artifacts were restored afterwards. The independent recompute
of the shipped virgin predictions reproduces all 240 rows at
exactly 0.0 on every field (expected home/away/total, p_over
2.5/3.5/4.5, mean 1H/2H) with r_model recomputed as
152.08755422697251, identical to the frozen
`fitted_params_virgin.json`; LL@3.5 and calibration recompute
from the shipped CSV as 0.667511 and +3.77pp / SE 3.14pp,
exact to all printed digits. Replaying those predictions
through the runner's existing `predict_cards` adapter (DEV-only
history, 2026 fixtures as upcoming) differs by up to 1.3875 on
exp_total (worst match 5125655, 2026-10-18) and 0.2999 on
p_over 3.5, mean |dmu| 0.2813 — decomposed, not hand-waved:
the first virgin fixture (2026-04-03) replays at exactly 0.0,
and the gap grows monotonically with the season (mean |dmu|
0.105 in April to 0.504 in October), because the harness
interleaves each 2026 result into the state before predicting
the next fixture while the runner predicts all upcoming
fixtures from the final DEV state. That is a harness artefact
of the replay construction, not a runner error: in production
the runner's state at prediction time already includes every
played match, so live predictions carry no such staleness.
The pre-ship defect the verdict already documents is recorded
here too: the harness first split expected totals with
SE-Allsvenskan's yellows constant 0.370, corrected to this
league's frozen 0.3344 before shipping (the shipped CSV's 1H
share is exactly 0.3344 on all 240 rows; FT probabilities and
the gate outcome were never affected). The builder's count
assert compares the built rows to the world index itself
(`len(out) == len(rows)` for league_id 168, 1,440 == 1,440),
so daily rebuilds needed no floor change — the same dynamic
form NO-Eliteserien, DE-2Bundesliga, and KR-KLeague1 carry
unfloored. Two full end-to-end proof runs on 2026-11-10 (44
leagues, 97 markets) each completed with zero errors, fetched
nothing new in any league, and produced 12,195 predictions;
all 229 snapshotted output files (97 daily CSVs, ledgers,
settled-keys sidecars, grading ledgers) are bit-identical
between the runs — no ZA-PSL-style exception this time.
SE-Superettan predicted nothing in either run: the 2026 season
is complete (last round 2026-11-07, 240/240) and the 2027
season is not yet listed, so its daily CSV is header-only, its
ledger and grading ledger empty, and its cards market will
first predict when 2027 fixtures appear. The proof pair took
four attempts for run 1: the first attempt died in a VM reboot
after 18 leagues, the next two were OOM-killed at about 7
leagues in while three Codex builder processes and a sibling
proof run shared the VM, and the fourth completed once that
load eased (run 2 then completed first try). All completed
runs were made with `MALLOC_ARENA_MAX=2`. One environment item:
this worktree arrived without the `data_enrichment/fotmob_world`
symlink the other runner worktrees carry, so the runner's
rebuild could not resolve the warehouse; the symlink to the
main checkout's warehouse was restored (git-ignored, no commit
impact) before the proof runs.

FI-Veikkausliiga has joined with cards only (arm `gate_zero`,
PROVISIONAL PASS: virgin LL 0.679517 at the primary 3.5 line,
calibration −2.16pp, breach within 1 SE of 3.71pp; the prereg
dev gate passed at LL 0.673991 vs base 0.674319 and naive
0.677092 — by 0.000328 over the base rate, the thinnest dev
margin in this league's build, recorded as such; per season the
model loses to the base rate in 2022 and 2023 and wins in 2024
and 2025, but the frozen gate is on the pooled number). Goals,
SOT, and corners failed their gates and are absent (corners
failed on the virgin calibration leg); total shots was NOT
BUILT (definition break between the thin era 2021–24 and the
rich era 2025–26; only one rich-era dev season exists). It is
a calendar-year world league (FotMob 51, FIN, Finland
Veikkausliiga; seasons 2021–2026, 1,017 matches and 2,034 team
rows; the virgin is the complete 2026 season, 177/177, last
match 2026-11-08). Cards is primary 3.5, ladder 2.5/3.5/4.5,
halves yellows share 0.3109 — the frozen league constant from
event times on the dev era; the 1H/2H p_over ladders use the
runner defaults (0.5/1.5/2.5 and 1.5/2.5/3.5), the same values
NO-Eliteserien and KR-KLeague1 configure explicitly. The gate
target is event-derived unified yellows (Yellow + YellowRed
card events), which the builder writes to
`yellow_home`/`yellow_away`; X8 is impossible (referee names
empty in all of 2021–2024 and in 141/177 of 2025), so Gate Zero
is the only arm and there is no operational-gate question. The
fitted NB size hit the estimator cap: r = 500.0 for
model/base/naive (`fitted_params_virgin.json`) — the
virgin-era yellows distribution is effectively Poisson at this
scale; recorded, not adjusted. No adapter amendment was
needed: `run_daily.py` is untouched by this join. Settlement
does need the per-market override `cards_actual:
[yellow_home, yellow_away]`, exactly as NO-Eliteserien,
KR-KLeague1, and SE-Superettan — but FI differs from SE2 in
one respect: the stats feed DOES carry card keys in 2025–2026,
so the runner's default cards actuals
(`yellow_cards_home`/`yellow_cards_away`) would not settle
nothing, they would grade the wrong target. The stats totals
disagree with the event target on 73 of 354 matches in
2025–2026 (41 of 177 in 2026), including 13 in 2026 that
straddle the 3.5 line and would flip hit/miss; the default
path also grades nothing at all on the 663 pre-2025 rows,
where the stats keys are empty. A synthetic settlement on
match 5147518 (FC Inter Turku–Ilves, 2026-04-11; event 4,
stats 3) settled 1 under the default with actual 3.0 (hit, LL
0.5976) and 1 under the opt-in with actual 4.0 (miss, LL
0.7988), a second pass settled 0, and the artifacts were
restored afterwards. The independent recompute of the shipped
virgin predictions reproduces all 177 rows at exactly 0.0 on
every field (expected home/away/total, p_over 2.5/3.5/4.5,
mean 1H/2H) with r recomputed as 500.0 on all three arms,
identical to the frozen `fitted_params_virgin.json`; LL@3.5
and calibration recompute from the shipped CSV as 0.679517
and −2.16pp / SE 3.71pp, exact to all printed digits.
Replaying those predictions through the runner's existing
`predict_cards` adapter (DEV-only history, 2026 fixtures as
upcoming) differs by up to 0.9708 on exp_total (worst match
6145898, 2026-09-08) and 0.1768 on p_over 3.5 (worst match
5147540, 2026-05-08), mean |dmu| 0.2724 — decomposed, not
hand-waved: the first virgin fixture (5147507, 2026-04-04)
replays at exactly 0.0, and the gap grows over the season
(mean |dmu| 0.1139 in April to 0.3849 in September), because
the harness interleaves each 2026 result into the state before
predicting the next fixture while the runner predicts all
upcoming fixtures from the final DEV state. That is the same
harness artefact of the replay construction SE-Superettan
documented, not a runner error: in production the runner's
state at prediction time already includes every played match,
so live predictions carry no such staleness. The pre-ship
defect the verdict already documents is recorded here too:
the SE2 harness this engine was adapted from carried a
foreign yellows constant 0.3344; it was corrected to this
league's frozen 0.3109 before shipping (the shipped CSV's 1H
share is exactly 0.3109 on all 177 rows; FT probabilities and
the gate outcome were never affected). The builder's count
assert compares the built rows to the world index itself
(`len(out) == len(rows)` for league_id 51, 1,017 == 1,017),
so daily rebuilds needed no floor change — the same dynamic
form SE-Superettan, NO-Eliteserien, DE-2Bundesliga, and
KR-KLeague1 carry unfloored; `build_data.py` is untouched.
Two full end-to-end proof runs on 2026-11-10 (46 leagues, 99
markets) each completed with zero errors, fetched nothing new
in any league, and produced 12,195 predictions; all 237
snapshotted output files (99 daily CSVs, ledgers,
settled-keys sidecars, grading ledgers) are bit-identical
between the runs — no exceptions at all, including every
FI-Veikkausliiga output. FI-Veikkausliiga predicted nothing
in either run: the 2026 season is complete (last match
2026-11-08, 177/177) and the 2027 season is not yet listed,
so its daily CSV is header-only, its ledger empty, and its
cards market will first predict when 2027 fixtures appear.
Run 1 took two launches: the first was cut short by a VM
reboot at 40 of 46 leagues (the reboot also wiped /tmp,
including the replay and settlement scripts — those runs had
already completed and their numbers are recorded here, not
re-derived); the relaunch completed first try, as did run 2. The first launch fetched 2,092 J1 matches into the fresh
worktree's jleague store; the completed run 1 and run 2 each
fetched nothing new in any league. All completed runs were
made with `MALLOC_ARENA_MAX=2`. Two environment items: this
worktree arrived without the `data_enrichment/fotmob_world`
symlink the other runner worktrees carry, so the runner's
rebuild could not resolve the warehouse; the symlink to the
main checkout's warehouse was restored (git-ignored, no commit
impact) before the proof runs. The CO-PrimeraA fresh-worktree
trap did not trigger: its builder also reads Primera B
warehouse JSONs, which are present via the symlinked
main-checkout warehouse, so CO rebuilt and predicted cleanly
in both runs with no copy and no code change.

HU-NBI has joined with corners only (arm `gate_zero`, PROVISIONAL PASS in
`reports/C_HU_VERDICT.md`: dev LL 0.6931 at the primary 9.5 line vs base
0.7417 and naive 0.7384, beating both baselines in all 3 seasons; plain
0.6969 also passes dev. Virgin 2025/2026, n=198, read ONCE, fit on
2021/22–2024/25: Gate Zero LL@9.5 0.6755 vs best baseline 0.7121,
calibration −1.56pp, breach within 1 SE of 3.55pp → PROVISIONAL PASS; Gate
Zero has the lower virgin LL and ships per the tie rule). Goals, SOT,
cards, and total shots failed their gates and are excluded. Corners
configuration is primary 9.5, ladder 8.5/9.5/10.5, and
`halves_share_1h: null` — this league's feed has no period splits at all
(its frozen config has `corners_1h_share: null` and the shipped virgin
predictions carry only the primary line, no ladder columns), so it uses
the FT-only corners opt-in documented above (RU-1Division precedent):
the runner writes the halves columns empty, computes the ladder from mu,
and predicts the FT ladder only. Unlike most leagues in this program, the
territorial multiplier is genuinely active here: β_poss = 0.005 fitted on
the virgin fit window, active on 190/198 virgin rows (γ = 0.0, NB r =
1.086, fit_n = 775) — the replay below verifies the runner actually
applies it, rather than matching mu while dropping it. HU-NBI is a world
league (Hungary, `Nemzeti Bajnokság I`, FotMob id 212) over split-format
seasons 2021/2022–2026/2027 (1,067 matches at the join: five complete
198-match seasons — 12 teams, triple round robin, no playoff phase in the
feed — plus 77 played in the in-progress 2026/2027). HU has NO
`team_matches` file — its builder writes a single matches CSV — so the
`data:` block carries `matches` only; the world rebuild path
`rebuild_csv_world` reads only `cfg["data"]["matches"]` and `team_matches`
is referenced only by the top-5 `rebuild_csv` path, so this is safe, and
the proof runs rebuild it that way. The builder's count asserts are
`len(out) == len(rows)` (dynamic) and `len(out) >= 1067` (floor) — the
rebuild produces exactly 1,067 rows at the join, so the floor is met
exactly and no change was needed; `build_data.py` is untouched. This join
needed an adapter amendment, the first of its kind in the program:
HU's CSV uses non-standard column names (`corners_h`/`corners_a`,
`total_shots_h`/`total_shots_a`, `possession_h`/`possession_a`,
`big_chances_h`/`big_chances_a`, `box_touches_h`/`box_touches_a`,
`home_id`/`away_id`) while the runner's corners adapter reads the
standard ones (`corners_home`, `total_shots_home`, `BallPossesion_home`,
`big_chance_home`, `touches_opp_box_home`, `home_team_id`, ...), so the
unmapped `good` filter would have dropped every HU row. Renaming columns
in `build_data.py` was not an option: the CSV schema is the league's
frozen build output and the frozen engine's `core.load` reads the `_h` /
`_a` names. Instead `run_daily.py` gained one minimal, default-inert
mechanism — a per-market `columns` map in `active.yaml`, consulted by
both `predict_corners` and the corners branch of `settle()` only when
present (all existing leagues, which carry no such key, resolve every
name to itself). It mirrors the `cards_actual` precedent for settle-side
column selection, extended to one mechanism for both paths rather than
two. Inertness was proven on NO-OBOSLigaen, the natural probe (same
FT-only corners shape, no `columns` key): `predict_corners` run with the
HEAD version of `run_daily.py` and with the amended version on identical
inputs produced identical output on every field of every row (8
pseudo-upcoming fixtures from the last 2026 round; 13 rows each, the
extra 5 being the same played matches matching by match_id in both
versions alike), and `settle()` run with both versions against scratch
roots graded match 5105318 identically (actual 15.0, chosen over, hit,
log loss 0.6201), a second pass settling nothing in both. The settle
mapping itself was proven on HU with a synthetic settlement on virgin
match 4813070: settled 1 with actual 6.0 read from `corners_h` /
`corners_a` (p_over 9.5 0.5577, chosen over, miss, LL 0.8159), a second
pass settling 0. The independent recompute of the shipped virgin
predictions reproduces all 198 rows at exactly 0.0 on mu and p_over at
9.5: the refit on the pre-virgin window reproduces
`fitted_params_virgin.json` bit-for-bit (gamma 0.0, r 1.0861219180167718,
beta [0.005], fit_n 775), beta-active rows 190/198, LL@9.5 0.6755 and
calibration −1.56pp recomputed exact to all printed digits. The
multiplier is not decorative: it moves mu on all 190 active rows, most
on match 4813172 (z_poss 41.4, mu 9.607 → 11.816, +2.21). Replaying the
live predictions through the runner adapter (full-history production
refit: gamma 0.15, r 1.1494594183097007, beta [0.005], fit_n 1050 — beta
unchanged from the virgin fit) reproduces all 121 live fixtures at
exactly 0.0 on mu and p_over 9.5, and the multiplier moves mu on 121/121
fixtures, most on match 5865544 (Ferencváros–Kisvárda, 2027-02-13, z_poss
28.6, mu 9.555 → 11.024, +1.47). One verification trap is recorded for
future joins: the first live-replay construction built a single
FeatureBuilder over history plus ALL fixtures, which lets fixture rows
(ch=0) contaminate later dates' state and showed max |dmu| 4.314; the
adapter builds per date group precisely so fixtures never enter another
date's state, and rebuilding per date group reproduces 0.0. Two full
end-to-end proof runs on 2026-11-10 (47 leagues, 100 markets) each
completed with zero errors and produced 12,316 predictions; run 2
fetched nothing new in any league. Run 1 took three launches: the first
died in a VM reboot at 28 of 47 leagues (it had fetched 2,092 J1 matches
into the fresh worktree's jleague store; HU was never reached), and the
relaunch completed first try, as did run 2. All completed runs were made
with `MALLOC_ARENA_MAX=2`. Of 241 snapshotted output files (100 daily
CSVs, ledgers, settled-keys sidecars, grading ledgers), 240 are
bit-identical between the runs, including every HU-NBI output; the sole
exception is ZA-PSL's corners daily CSV, the known pre-existing case —
its FT values are bit-equal to run 1's ledger on all 160 fixtures (max
difference 0.0), so its delta is confined to non-ledger fields. Unlike
the last three joins, HU-NBI predicted real fixtures on day one: 121
upcoming 2026/2027 fixtures (198 − 77 played), 2026-11-21 to 2027-05-22,
first 2026-11-21 Puskás FC Academy–MTK Budapest (mu 9.2243, P(over 9.5)
0.4399); the ledger holds 121 entries and nothing has settled yet. Two
environment items: this worktree arrived without the
`data_enrichment/fotmob_world` symlink the other runner worktrees carry,
so the runner's rebuild could not resolve the warehouse; the symlink to
the main checkout's warehouse was restored (git-ignored, no commit
impact) before the proof runs. The CO-PrimeraA fresh-worktree trap did
not trigger: its builder also reads Primera B warehouse JSONs, which are
present via the symlinked main-checkout warehouse, so CO rebuilt and
predicted cleanly in both runs with no copy and no code change.
US-USLLeagueOne has joined with corners (arm `gate_zero`, PROVISIONAL PASS in `reports/C_USLL1_VERDICT.md`: dev pooled LL@9.5 0.684403 vs league base 0.693505 and naive trailing-10 0.691119, n=486, 2022-2024 regular; virgin 2025 LL@9.5 0.688533 vs base 0.697479; calibration +1.490pp, breach within 1 SE of 3.441pp; the X7 box-touch arm failed its dev gate outright at 0.714615 and is excluded) and total shots (arm `B`, PROVISIONAL PASS in `reports/T_USLL1_VERDICT.md`: dev gate pool 2023-2024, n=321: B 0.679305 vs league base 0.694009 and naive 0.684291; virgin 2025 LL@24.5 B 0.693325 vs league base 0.696400, lowest of the three arms; calibration +2.866pp, breach within 1 SE of 3.444pp; arm C fails the dev-sign leg vs A (0/2) and is excluded; arm A is provisional but B has the lower virgin LL). Goals, SOT and cards failed their gates and are excluded. Corners configuration is primary 9.5, ladder 8.5/9.5/10.5, halves share 0.469, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5; total-shots configuration is primary 24.5, ladder 23.5/24.5/25.5, halves share 0.461, 1H ladder 10.5/11.5/12.5, 2H ladder 12.5/13.5/14.5. Both markets set the new `exclude_phases: ["playoff"]` opt-in: the league's frozen phase rule excludes playoff rows from every fitting/scoring window (both engines' load functions drop non-regular rows), and the runner adapters previously included them — without the opt-in the corners fit on the pre-virgin window flips to gamma 0.0, beta [0.0025, 0.0], fit_n 665 (vs the frozen gamma 0.15, beta [0.0, 0.0], fit_n 643), and the total-shots arm-B replay sits 0.69 in mu off the shipped file. With the opt-in the fit reproduces the frozen `fitted_params_virgin.json` bit-for-bit and the total-shots replay residual is the adapter's date-grouped state only (see below). The opt-in is default-inert and mirrors the `exclude_seasons` precedent: SCO-Premiership corners and US-USLChampionship total shots arm B (84 playoff rows in its history) produce bit-identical adapter output before and after the change when the key is absent, and SCO corners is unchanged even with the key set (it has no playoff rows), while USLChampionship arm B moves on all 375 probe rows when the key is set, proving the opt-in engages (no other league's config sets the key, so no other league's behaviour changes). The data builder's frozen 1,174-match count is now a floor (`len(rows)>=1174`), so a daily rebuild survives the next played match being appended; every rebuild in the proof produced exactly 1,174 matches and 2,348 team rows. US-USLLeagueOne is a world league (USA, `USL League One`, FotMob id 9296) over calendar-year seasons 2021-2026. An independent recompute through the frozen engines reproduced both shipped virgin predictions from the rebuilt data: corners exactly (max difference 0.0 on mu, r and all nine ladder lines over all 210 rows, and the refit on the pre-virgin window reproduces `fitted_params_virgin.json` bit-for-bit), total shots to 1.7e-9 (float repr); the total-shots `fitted_params.json` values match the virgin file's arm-B values exactly (lambda 300.0, r_A 117.1426320116539, level cell [60, 1.0, 20], half split [0.461, 0.539]). The replay through the runner adapters differs only by named, by-design causes: corners max |mu| difference 1.384 (max |p_over| 0.170 at the 9.5 line) because the replay device truncates history at 2024-12-31 while the shipped file's features include earlier-2025 matches — the first-date fixtures match exactly (diff 0.0) and the gap grows through the season as within-2025 history accumulates — and total shots max |mu| difference 0.371 (max |p_over| 0.027) because the adapter defers state updates to end of day while the total-shots harness consumes same-day earlier matches (a date-grouped-harness variant reproduces the adapter value exactly); in production the adapters see complete history up to each fixture date, so neither gap is a production defect. Note the brief's claim that `predict_corners` pins the fit to `fitted_params_virgin.json` is incorrect: the runner live-fits every corners league (verified: no such code exists, `git log -S fitted_params_virgin` on `run_daily.py` is empty), and the live refit on full history (all regular rows 2021-2026) keeps gamma 0.15 but moves r to 1.1255 and beta to [0.0025, 0.025] (fit_n 1,131), shifting the virgin fixtures' mu by at most 1.40 and p_over at 9.5 by at most 0.167 — the runner's by-design daily refit, as for NO-OBOSLigaen, not a defect, and no pinning mechanism was added. Two end-to-end proof runs on 2026-11-10 (45 leagues; 99 markets): run 1 produced 12,197 predictions with 54,492 matches fetched (fresh worktree) and zero errors; run 2 produced 12,227 predictions with fetched_new=0 in every league and zero errors. The proof pair took five launches: run 1's first attempt was killed by a runtime restart at league 12/45 (after fetching 20,281 matches, zero errors) and its completed restart ran clean; run 2's first attempt was killed by a service-restart SIGTERM at league 41/45 (fetched 0, 11,885 predictions, zero errors), its second attempt was OOM-killed (exit 137) at league 7/45 while the wt-runner49 agent's full run shared the box, and its third attempt completed cleanly (overlapping the wt-runner50 agent's run, which also finished). The run-1 md5 snapshot was lost when the restarts wiped /tmp, so the run-1/run-2 file comparison was recovered through the ledgers, as the brief's exception clause allows: all 12,197 non-CO rows are bit-equal on exp_total, every FT ladder p_over and date against run 1's ledger entries (exact float equality, 0 mismatches, 0 rows without a ledger entry), and USLL1's halves recompute exactly from exp_total with the live corners r and the frozen total-shots r_A. The sole fixture-set difference is CO-PrimeraA: 0 predicted in run 1, 10 per market in run 2 (FotMob published the 2026-11-12 matchday between 16:37 and 18:14) — new rows, not changed values; its pre-copied Primera B warehouse files meant the known fresh-worktree trap never fired. At the join FotMob listed exactly one upcoming USLL1 fixture, the 2026 final on 2026-11-15 (Charlotte Independence vs Boise, match 1000023200), predicted in both markets in both runs (corners exp_total 8.8729, P(over 9.5) 0.3967; total shots exp_total 29.0744, P(over 24.5) 0.7694), and nothing settled (the final is in the future). A synthetic settlement on the latest finished match, the 2026-11-09 semi-final 1000023079 (Charlotte Independence vs Forward Madison FC), graded both markets correctly through the real adapters and settle path (corners live exp_total 9.4832, P(over 9.5) 0.4722, chosen under, actual 6.0, hit, log loss 0.6391; total shots live exp_total 27.0347, P(over 24.5) 0.6572, chosen over, actual 26.0, hit, log loss 0.4197), settled exactly once per market (a second pass settled nothing), matched an independent recompute, and left every artifact md5-clean after the synthetic entries were removed. All completed runs were made with `MALLOC_ARENA_MAX=2`, which changes no output. Defects found (pre-existing, not changed by this join): the frozen builder's phase rule keys off the FotMob league name ending in "Playoff", so the six 2026 playoff matches (quarter-finals 2026-10-30/11-02 and semi-finals 2026-11-08/09, round names "Championship - Quarter-finals/Semi-finals") are flagged "regular" and enter the production fit and state, while the 29 properly-flagged 2021-2025 playoff rows are excluded — bounded impact (6 of 1,174 rows), and the coming final will be flagged the same way when played; and the entry's `warehouse:` field says "United States/USL League One" while the runner pulls with `country: USA` into "USA/USL League One" — cosmetic only, since world leagues never read the `warehouse:` field (only the J-League rebuild path does).
SK-1Liga has joined with SOT only (arm `GZ`, CLEAN PASS in
`reports/S_SK_VERDICT.md`: dev pooled LL@8.5 0.683432 vs league base
0.702388 and naive trailing-10 0.695303; sealed window 2025/2026,
n=192, Gate Zero LL@8.5 0.687872 vs base 0.696309 and naive 0.693703,
calibration −0.88pp inside the 1.0pp clean band — no SE rescue needed.
Leg (i) and leg (ii) both PASS. RS also passes dev but fails its sign
check 1/3 and was NOT read on the sealed window). SOT configuration is
primary 8.5, ladder 7.5/8.5/9.5, and `halves_share_1h: null` — this
league's frozen config has `sot_1h_share: null`, so it uses the FT-only
SOT opt-in (CZ-Liga precedent): the runner writes the halves columns
empty and predicts the FT ladder only. Goals, corners, and cards failed
their gates and are excluded; total shots was NOT BUILDABLE
(definition break at 2025/2026: dev ~19.3 → sealed window 27.1). The
declared total-shots level-break risk (prereg) did NOT bite: the
walk-forward's in-season state updates adapted to the rich-era shot
counting, and calibration landed inside the clean band despite the
break sitting exactly at the sealed-window boundary. SK-1Liga is a
world league (Slovakia, `1. liga`, FotMob id 176) over split-year
seasons 2021/2022–2026/2027 (1,053 matches at the join: five complete
seasons of 195/195/192/195/192 plus 84 played in the in-progress
2026/2027; 9 ECL play-off ties excluded via the `included` flag; 69
rows lack stats and the engine's `load_matches` drops them, so the
adapter fits on 975). The `div: SK-1Liga` block value matches the
rebuilt CSV's `league` column on all 1,053 rows, so fixture and
history resolve to the same division the frozen
`fitted_params_virgin.json` keys `league_means` by (home 4.796608 /
away 3.890263). `ratio_prior: 200` is stated explicitly — the v5
default, never tuned. This join sets `team_key: canonical_name`, and
it is load-bearing, not cosmetic: FotMob's 2026/2027 feed spells 8 of
the 12 clubs with diacritics (Žilina, Trenčín, Ružomberok, Komárno,
FC Košice, Dukla Banská Bystrica, Zemplín Michalovce, Zeleziarne
Podbrezová) alongside their ASCII spellings — in the live fixtures
and in the 2026/2027 history rows themselves (20 spellings for 12
teams) — while every gated era is ASCII, so without the opt-in those
clubs would key to split histories and diacritic fixtures would miss
the fitted regression entirely. A probe proves it: a Žilina–Trenčín
live fixture scores mu 9.670 with the key vs 10.157 without
(Δ −0.488), and even an ASCII-spelled Zilina–Trencin fixture differs
(9.670 vs 9.287) because canonicalisation also merges the split
2026/2027 history. No `run_daily.py` change was needed: the opt-in
already existed (CZ-Liga precedent) and `build_data.py` is untouched
(its only assert is the duplicate-match_id check; the rebuild produces
exactly 1,053 rows, the world-index count). The independent recompute
of the shipped sealed-window predictions reproduces all 192 rows at
exactly 0.0 on mu and every ladder probability (LL@8.5 0.687872,
calibration −0.88pp, SE 3.60pp, actual-over rate 0.53125, mean
predicted 0.52245 — exact to all printed digits), and the fitted
regression theta and league means reproduce exactly too; a
canonicalised causal replay agrees with the raw replay at 0.0 on every
field, proving the opt-in is gated-product invariant for SK.
Replaying the live predictions through the runner adapter
(full-history production refit on all 975 loadable rows) differs from
the shipped sealed-window predictions by max |dmu| 0.965, mean |dmu|
0.238, max |dp| 0.258, LL@8.5 0.677159 vs shipped 0.687872 — decomposed
with numbers: update order (predict-before-update vs the adapter's
update-all-first) mean |dmu| 0.169, max 0.655; the extra 2026/2027
history mean |dmu| 0.170, max 0.544; the two halves contribute about
equally, and the adapter's LL on sealed-window actuals is better
(0.677 vs 0.688) because its ratings see later matches — the expected
live-refit leakage, same pattern as the NO-OBOS corners diagnostic,
not a defect. Two full end-to-end proof runs on 2026-11-10 (48 leagues,
101 markets) each completed with zero errors and produced 12,394
predictions; run 2 fetched nothing new in any league. Run 2 needed a
relaunch: its first attempt was killed at 23 of 48 leagues by a
runtime restart (which also wiped the /tmp md5 snapshot of run 1's
outputs), and the full relaunch completed first try. The lost snapshot
means the run-1-vs-run-2 file comparison rests on substitute evidence
instead of md5s: all 101 (league, market) prediction counts are
identical between the runs, the SK daily CSV's values match the
recorded run-1 values to full printed precision (first mu
8.431483393887682, last mu 9.594356676591348, mu range and mean
identical), the SK ledger still holds exactly 48 entries with its
mtime untouched by run 2 (deduplication appended nothing), and the
ZA-PSL corners daily CSV — the known pre-existing case — is bit-equal
to run 1's ledger on FT values on all 160 rows (max difference 0.0).
Unlike the last three joins, SK-1Liga predicted real fixtures on day
one: 48 remaining regular-phase fixtures (132 − 84 played),
2026-11-21 to 2027-02-27, first 2026-11-21 Ružomberok–Slovan
Bratislava (mu 8.4315, P(over 8.5) 0.4978); the ledger holds 48
entries and nothing has settled yet. A live recompute of all 48
through `predict_sot` reproduces the daily CSV at exactly 0.0 on mu
and every ladder probability. Two environment items: this worktree
arrived without the `data_enrichment/fotmob_world` symlink the other
runner worktrees carry, so the symlink to the main checkout's
warehouse was restored (git-ignored, no commit impact) before the
proof runs. The CO-PrimeraA fresh-worktree trap did not trigger in
either run: its builder also reads Primera B warehouse JSONs, which
are present via the symlinked main-checkout warehouse, so CO rebuilt
and predicted cleanly in both runs with no copy and no code change.
AE-ProLeague has joined with total shots (arm `C`, PROVISIONAL PASS in `reports/T_AE_VERDICT.md`: dev pooled n=545 LL@25.5 A 0.682015, B 0.682259, C 0.681906 vs league base 0.696534 and naive 0.695637, all three arms passing dev; virgin 2025/2026 n=182 arm C LL@25.5 0.686302 — lowest of the three arms (A 0.687007, B 0.687541) and below league base 0.691060; calibration breach +3.10pp (actual−predicted −3.10pp; the virgin season ran cold on shots, 24.48/match vs 25.67–26.87 dev, so every arm overstates the over-rate), inside 1 SE (3.67pp) of the 1.0pp boundary — legs (i) and (iii) PASS, leg (ii) PROVISIONAL. Both-pass rule: A and C pass all legs; the lower pooled virgin LL ships → arm C. Arm B is excluded (fails leg (i) vs A). Goals, SOT, corners and cards failed their gates and are excluded. Total-shots configuration is primary 25.5, ladder 24.5/25.5/26.5, halves share 0.4608, 1H ladder 10.5/11.5/12.5, 2H ladder 12.5/13.5/14.5. No `exclude_seasons`: the frozen harness fits on all seasons (2021/2022 is the tuning seed, scored from 2022/2023), and the adapter reads `trailing_r_window` 200 from `fitted_params.json` as designed — no block key was added for it. Two changes were needed. The data builder's frozen-count asserts are now floors (completed seasons stay exact at 182 each, the in-progress 2026/2027 season `>= 49`, total `>= 959`), following the AU/MLS/USLL1 trap precedent, so a daily rebuild survives new 2026/2027 results. And the runner's total-shots arm-C path now falls back to the market's frozen `halves_share_1h` when `fitted_params.json` carries no `half_split` — AE is the first arm-C league without one (all six existing arm-C leagues carry it; the unamended adapter raised `KeyError: 'half_split'` on the first replay attempt), mirroring the arm-A (CL-LigaDePrimera) and arm-B (CN-SuperLeague) fallback precedent. Inertness was proven on GR-SuperLeague, the natural probe (same arm C, `half_split` present): `predict_total_shots_arm_c` run with the HEAD version of `run_daily.py` and with the amended version on identical inputs produced byte-identical output on all 8 fixed pseudo-upcoming fixtures. The independent recompute of the shipped virgin predictions (182 rows, arm C) reproduces the verdict exactly from the CSV itself (LL@25.5 0.686302, breach +3.10pp); replaying them through the runner adapter differs by max |mu| 0.0210 (mean 0.0027) and max |p_over@25.5| 0.00148, replay LL@25.5 0.686260 — and the gap is fully decomposed, not assumed: re-running the replay with the 2 awarded matches removed from history (the frozen harness drops them; the runner adapter includes them, pre-existing uniform adapter behaviour, not changed by this join) reproduces the shipped file to max |mu| 1.8e-07, so the entire replay difference is the awarded-rows effect on the live refit. Fitted params: lambda 300.0, r_A 156.5851, level cell [120.0, 0.5, 50.0], trailing window 200. Two full end-to-end proof runs on 2026-11-10 (VM date; 2026-11-11 WIB) — 49 leagues, 12,418 predictions each, zero errors in either run; run 2 fetched nothing new in any league. Both runs completed first try with `MALLOC_ARENA_MAX=2` (run 1 ~34 min, run 2 ~32 min) despite the SK-1Liga join proof run and the final Codex-sol audit sharing the box — no kills, no restarts, no retries. Of 250 snapshotted output files (daily CSVs, ledgers, settled-keys sidecars, grading ledgers), 249 are bit-identical between the runs, including every AE-ProLeague output; the sole exception is ZA-PSL's corners daily CSV, the known pre-existing case — its FT values are bit-equal to run 1's ledger on all 160 fixtures (max difference 0.0 on exp_total and all 480 ladder p_over values), so its delta is confined to non-ledger fields. Unlike the last joins, AE-ProLeague predicted real fixtures on day one: 70 upcoming 2026/2027 fixtures in both runs (2026-11-19 to 2027-02-21), first 2026-11-19 Al-Wasl–Hatta (match 1000022240, exp_total 26.9833, P(over 25.5) 0.5816); exp_total spans 24.3319–28.5102, the 1H share is exactly 0.4608 on all 70 rows, the ledger holds 70 entries, and nothing has settled yet (all fixtures are in the future). It is a world league (United Arab Emirates, `Pro League`, FotMob id 538) over split-year seasons 2021/2022–2026/2027, 14 teams, straight double round-robin, no play-offs; at the join the rebuild held 959 matches (182 per completed season, 49 played in 2026/2027). Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the CO-PrimeraA fresh-worktree trap did not trigger — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted 10 fixtures per market in both runs with no copy and no code change. Run 1's only fetch was J1's 2,092 matches into the fresh worktree's J-League store; AE fetched nothing new in either run.

HR-HNL has joined with corners only (arm `x7`, PROVISIONAL PASS in
`reports/C_HR_VERDICT.md`: dev pooled LL@8.5 X7 0.693357 vs Gate Zero
0.695758, league base 0.725167 and naive trailing-10 0.725569, n=540
(warm-up 2021/2022, scored 2022/2023–2024/2025); X7 beats Gate Zero in
2 of 3 dev seasons, so the sign leg passes. Sealed window 2025/2026,
n=180: X7 LL@8.5 0.685221 (mean P(over) 0.5481, actual 0.5778,
calibration −2.97pp, SE 3.70pp) vs Gate Zero 0.693697 (cal −3.16pp, SE
3.73pp); leg (i) PASS for both, leg (ii) PROVISIONAL for both (breach
within 1 SE of the 1.0pp boundary), leg (iii) X7 ✓. Both-pass rule:
lower pooled virgin LL ships → X7; Gate Zero is excluded (higher
virgin LL). Corners configuration is primary 8.5, ladder 7.5/8.5/9.5,
halves share 0.4793, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5. Goals
failed dev (OU leg); SOT failed virgin legs (i) and (ii); total shots
failed virgin leg (i); cards were NOT BUILT (stats-vs-events
era-flipped target artefact, EDA F6) — all excluded. Stated plainly:
the fitted touches beta is 0.0 in every dev season and in the virgin
fit (dev active-with-nonzero-beta share 0.0 despite a 63.9%
both-teams-active share), so the X7 arm never applies a touches
multiplier — it is the corners_v3 core without the territorial
multiplier, and it beat Gate Zero because the territorial multiplier
itself was the worse component in this league. The ship is honest
under the frozen arm definition, but no box-touch signal ships. HR-HNL
is a world league (Croatia, `HNL`, FotMob id 252) over split-year
seasons 2021/2022–2026/2027 (964 matches at the join: five complete
seasons of 180 plus 64 played in the in-progress 2026/2027; 10 teams,
straight quadruple round-robin, no split or play-off phase in the
feed). No `run_daily.py` change was needed: the adapter passes the
`arm: x7` string to the engine's own fit/predict path (SE-Allsvenskan /
DE-3Liga precedent) and `build_data.py` is untouched (its only asserts
are self-consistency; the rebuild produces exactly 964 matches and
1,928 team rows). The independent recompute of the shipped sealed-window
predictions reproduces all 180 rows at exactly 0.0 on mu, r and every
ladder probability (LL@8.5 0.685221, calibration −2.97pp), and the refit
on the pre-virgin window reproduces `fitted_params_virgin.json`
bit-for-bit for both arms (gamma 0.15, r 1.1582846692836015, X7 beta
[0.0], Gate Zero beta [0.0, 0.025], fit_n 710). Replaying the shipped
predictions through the runner adapter (live refit on full history)
differs only by named, by-design causes: the refit keeps gamma 0.15
and beta [0.0] but moves r to 1.2280 (fit_n 954), and on the
causal-state copy the adapter reproduces the shipped mu at exactly 0.0
(max |dmu| 0.0) and exp_1h at exactly 0.0, with p differing only via r
(max |dp| 0.0076 at 7.5, 0.0054 at 8.5; LL@8.5 0.685652 vs shipped
0.685221). A naive replay shows max |dmu| 0.7629, but that is a
replay-device artefact, not a production defect: the adapter appends
each fixture group after the full sorted history, so a past-dated
virgin fixture sees post-date state (its fixture copy and its own
history-row copy differ by up to 0.7629); in production every upcoming
fixture is dated after all history, so this cannot occur. No adapter
change was made, so no inertness probe was required. Two full
end-to-end proof runs on 2026-11-10 (50 leagues, 104 markets) each
completed with zero errors and produced 12,512 predictions; run 1
fetched 2,092 matches (all J1 — the fresh worktree carried no
fotmob_jleague store; every world league fetched 0 via the symlinked
warehouse). Run 2 needed a relaunch: its first attempt was killed by a
runtime restart at 38 of 50 leagues (last summary ZA-PSL) and the
relaunch, after a 60-second pause, completed first try with
fetched_new=0 in every league. Of the 104 daily files, 103 are
bit-identical between the runs; the sole differ is ZA-PSL corners, the
known pre-existing case — its FT values are bit-equal to run 1's ledger
on all 160 rows (max difference 0.0 on exp_total, every ladder p_over
and date; only the halves columns move, its exp_1h sitting up to
0.0009 off share*mu). The HR-HNL daily CSV is bit-identical between
the runs (md5 c0a567bccdcafebd3780ba5f890daa77) and its ledger still
holds exactly 116 entries with its mtime untouched by run 2
(deduplication appended nothing). HR-HNL predicted real fixtures on
day one: 116 remaining 2026/2027 fixtures (180 − 64 played),
2026-11-21 to 2027-05-22, in both runs (first 2026-11-21 Dinamo Zagreb
vs NK Istra 1961, mu 9.7025, P(over 8.5) 0.6122; mu range 9.111–9.702,
P(over 8.5) 0.544–0.612); the ledger holds 116 entries and nothing has
settled yet. Two environment items: this worktree arrived without the
`data_enrichment/fotmob_world` symlink the other runner worktrees
carry, so the symlink to the main checkout's warehouse was restored
(git-ignored, no commit impact) before the proof runs. The CO-PrimeraA
fresh-worktree trap did not trigger in either run: its builder also
reads Primera B warehouse JSONs, which are present via the symlinked
main-checkout warehouse, so CO rebuilt and predicted cleanly in both
runs with no copy and no code change. All proof runs were made with
`MALLOC_ARENA_MAX=2`.

DK-1Division has joined with corners (arm `x5`, PROVISIONAL PASS in `reports/C_DK1_VERDICT.md`), cards (arm `gate_zero`, clean PASS in `reports/K_DK1_VERDICT.md`), SOT (arm `GZ`, PROVISIONAL PASS in `reports/S_DK1_VERDICT.md`), and total shots (arm `x5`, PROVISIONAL PASS in `reports/T_DK1_VERDICT.md`). Goals failed the dev gate (`engine/goals/results_virgin.json`: virgin deliberately unread) and are excluded. It is a Denmark 1. division world league (FotMob id 85, ccode DEN, `1. Division`, 12 teams, 192 matches per completed season; the rebuild held 1,044 matches — 192 per season 2021/2022–2025/2026 plus 84 played in 2026/2027 (one more than at build time, a match finished 2026-11-09) — and 2,088 team rows). The 2021/2022 season carries no stats at all in the feed, so every adapter's history starts at the 2022/2023 seed season, exactly as the frozen harnesses do. Configuration: corners primary 9.5, ladder 8.5/9.5/10.5, halves share 0.469, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5; cards primary 3.5, ladder 2.5/3.5/4.5, halves share 0.314, 1H ladder 0.5/1.5/2.5, 2H ladder 1.5/2.5/3.5; SOT primary 9.5, ladder 8.5/9.5/10.5, halves share 0.455, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5, div DK-1Division, ratio_prior 200; total shots primary 26.5, ladder 25.5/26.5/27.5, halves share 0.461, 1H ladder 11.5/12.5/13.5, 2H ladder 13.5/14.5/15.5. Gate arithmetic. Corners virgin 2025/2026 (n=192, dev seed 2022/2023, scored 2023/2024–2024/2025, n=384): Gate Zero LL 0.7051, calibration −5.16pp — it FAILS the calibration leg (|−5.16|pp > 1.0 + SE 3.64 = 4.64pp), so Gate Zero cannot ship; X5 LL 0.7035, calibration −3.71pp, inside the 4.64pp provisional bound, so X5 ships PROVISIONAL (X7 0.7065 fails likewise at −5.29pp; 2025/2026 was a high-corner season and every arm under-predicted, X5's trailing blend adapting best). Cards virgin (n=192): Gate Zero LL 0.6780, calibration +0.03pp, SE 3.56pp — clean PASS; X5 0.6861 fails the LL leg against Gate Zero. SOT virgin (n=192): Gate Zero LL 0.6902 vs base 0.6909 — the LL leg passes by 0.0007 (thin); X5 0.6904 fails the LL leg; calibration −1.48pp, SE 3.60pp — beyond the 1.0pp clean boundary but within 1 SE, so PROVISIONAL. Total shots virgin (n=192): X5 LL 0.6764, calibration −1.70pp (PROVISIONAL); Gate Zero 0.6786, calibration −0.77pp (clean); X7 0.6786 — the both-pass rule ships the lower pooled virgin LL, so provisional X5 ships over clean Gate Zero. X5 is new to the runner (no `x5` string existed in `run_daily.py`). Both X5 arms are the same construction from the league's own harness: a 0.5/0.5 trailing-rate blend. Corners: `mu = 0.5*mu_GZ + 0.5*naive` where naive is the trailing-10 total from `core.attach_naive`, with Gate Zero's r — implemented inside `predict_corners`, engaged only when `arm == "x5"` (the adapter fits Gate Zero's params and blends; `attach_naive` is date-grouped like every other state in that engine, so same-date fixtures never see each other). Total shots: `mu = 0.5*GZ + 0.5*(nh+na)` from the shots-family `NaiveTracker`, a single NB on the blended mu with the frozen r — implemented as the new `predict_total_shots_arm_x5`, which reads lambda/r from the league's `fitted_params_virgin.json` (lambda 100.0, r 57.00194178382675; there is no `fitted_params.json` for this arm and the ladder lives in `active.yaml`) and walks the pointer exactly like arm C minus the base-rate/level/trailing-r layers X5 does not use. No new engine, no parallel prediction path, no change to any other arm. Fitted params: corners gamma 0.15, r 1.2188132180917006, beta [0.0025, 0.0], fit_n 565; cards r 27.70577184854863; SOT nb_r 79.94; total shots lambda 100.0, r 57.00194178382675, beta_x7 0.0. Four defects in the join path were found and fixed inside `run_daily.py` (the league builder was not touched). (1) DK's builder omits the `league` column every SOT loader reads as its division key (`div = r["league"]`), so `predict_sot` would raise KeyError; `rebuild_csv_world` now appends the column (league name) when absent, only for leagues that run SOT — no joined SOT league's CSV lacks the column, so the branch engages for DK only. (2) The frozen cards target is stats-feed yellow+red, but the builder's `yellow_home` alias is yellow only, so the default cards path would fit and grade the wrong target; the new opt-in `cards_target: yellow_plus_red` reads yellow_cards+red_cards on both sides in `predict_cards` and in `settle` (the existing `cards_actual` opt-in names two columns and cannot express a four-column sum). (3) DK's SOT `Engine` takes only `(matches, arm)` — it fixes the ratio prior at 200.0 for non-RS arms — while `predict_sot` unconditionally passed `ratio_prior`; `predict_sot` now passes the argument only when the engine accepts it (signature check, mirroring the goals adapter's call-each-engine- as-it-is-written rule). (4) DK's SOT loader keys history on team names, but three FotMob ids carry two spellings inside the fit window (9814 Horsens/AC Horsens, 8487 Sønderjyske/SønderjyskE, 8470 Aalborg BK/AaB), so name-keyed history splits those teams; with `team_key: id` the adapter now remaps history names to ids from the match CSV (a name mapping to more than one id is left alone — none does here), and the existing fixture-key cast then keys fixtures on ints. Also corrected: the brief's `ccode: DNK` is wrong — the FotMob index and DK-Superligaen both use `DEN` for Denmark, and the join uses `DEN`. Replay (independent recompute of the shipped virgin predictions, 192 rows per market; shipped CSVs carry only the primary-line p_over, so the check is mu + primary p + 1H/2H expected totals). Engine-only harness walks reproduce all four shipped files at CSV rounding level (max |mu| ≤ 0.0005, max |p| ≤ 5e-5). Corners: the fit on the pre-virgin window reproduces `fitted_params_virgin.json` bit-for-bit (gamma 0.15, r 1.2188132180917006, beta [0.0025, 0.0], fit_n 565); the first virgin fixture through the real adapter matches at rounding level (mu 9.6238 vs 9.624, p9.5 0.4862); the full apply replay with frozen params matches all 192 at rounding level. Total shots: the adapter walk (one real `predict_total_shots_arm_x5` call over all 192 virgin fixtures) matches all 192 at rounding level too — the same-day naive difference that could have arisen does not, because each team plays once per matchday, so no same-day match can enter either fixture team's trailing-10. Cards: the adapter walk matches mu/1H/2H at rounding level on all 192; p_over 3.5 differs by at most 0.0056 (worst fixture 5272926, 2026-05-22 Aarhus Fremad–AaB), fully decomposed: the adapter re-estimates r on the growing window (r 46.79 on 756 records there vs the frozen rs_v 27.71), while the harness freezes rs_v — the runner's by-design live re-estimation, not an adapter error. SOT: the adapter walk (id-keyed) differs by at most 0.0884 on mu and 0.0055 on p9.5 (worst fixture 4812058, Lyngby–Hillerød), fully decomposed: a fresh-refit walk reproduces those exact maxima, so the whole gap is the RegressionStore refit anchor — the harness's theta is up to 7 days stale, the adapter fits fresh at each fixture day (the CY-class artefact). Without the id remap the name-keyed walk is worse (max |mu| 0.1268, worst fixture 5272880 AC Horsens–Esbjerg fB — a renamed team), which is what the remap removes. The production live refit on full history (corners gamma 0.15 → 0.0, r 1.2188 → 1.2235, fit_n 840) moves virgin-fixture predictions by at most 0.370 on mu and 0.044 on p9.5 — the runner's by-design daily refit on the longer window, which now includes the high-corner 2025/2026 season and 83 matches of 2026/2027. Inertness: old (HEAD) vs new adapter outputs on pre-existing leagues are byte-identical on all 8 probes (corners GZ DK-Superligaen, corners X7 AR-LigaProfesional, total shots C DK-Superligaen, A NL-Eredivisie, B US-USLLeagueOne, cards GZ AU-ALeague, SOT GZ NL-Eredivisie, SOT RS AU-ALeague) — 0 field diffs. Synthetic settlement on finished match 5764501 (Hobro–Kolding IF, 2026-10-10; chosen because it carries a red card, so the cards target discriminates: yellow+red 4.0 vs yellow-only 3.0): corners actual 14.0 (pred exp 10.0483, p9.5 0.5347, over, hit, LL 0.6261); cards actual 4.0 — the yellow+red target, proving the opt-in in the settle path (pred exp 3.5299, p3.5 0.4664, under, miss, LL 0.7626; yellow-only would have graded 3.0, a hit); SOT actual 9.0 (pred exp 8.4587, p9.5 0.3787, under, hit, LL 0.4760); total shots actual 21.0 (pred exp 24.7316, p26.5 0.3652, under, hit, LL 0.4545). Each market settled exactly once (a second settle pass settled nothing). Two full end-to-end proof runs on 2026-11-10 (VM date; 2026-11-11 WIB), 51 leagues, 108 markets. Run 1 (first attempt, exit 0, ~33 min): 12,658 total predictions across 108 daily files, 0 error rows in 369 run-log rows; fetched_new 2,092 for J1 (fresh J-League store) and 1,044 for DK — the DK fetch was a case bug (below), every other league 0. DK predicted 48 upcoming fixtures per market (2026-11-19 to 2027-03-19), first Fredericia–Hillerød 2026-11-19 match 5764470 (corners exp 9.4488 p9.5 0.4655; cards exp 3.1437 p3.5 0.3840; SOT exp 10.2144 p9.5 0.5473; total shots exp 29.5998 p26.5 0.6636); 192 ledger entries (48 per market), nothing settled, settled_keys empty. Run 2 (first attempt, exit 0, ~32 min): 12,658 total predictions across the same 108 daily files, 0 error rows in 369 run-log rows, fetched_new=0 in every league (including DK — the case fix works, and J1's store is now populated too); DK again 48 upcoming fixtures per market, same dates, same first fixture, identical expected totals (corners 9.448767250658385, cards 3.1436974819915218, SOT 10.214422993807698, total shots 29.59980218718723); the DK ledger still holds exactly 192 entries, all run_date 2026-11-10 (run 2 added none — dedup by market/match_id/run_date works), settled_keys still empty, grading ledger still empty. Of 361 snapshotted files, 359 are bit-identical between the two runs; the two exceptions are the run log (accumulates rows by design) and ZA-PSL's daily_2026-11-10_corners.csv — the known recurring case: all 160 rows match the run-1 ledger on exp_total, all three ladder p_over values and the primary-line p_over (primary 8.5) with 0 mismatches, and the ledger itself is bit-identical between runs, so the file differs only in row order (rows are sorted by date only, and 143 of its 160 fixtures sit in 37 same-date groups) — every predicted value is bit-equal to run 1. No retries were needed on either run. One more defect, found by the proof run itself: the brief wrote `world_league: 1. division` (lowercase d), but FotMob's league name and the warehouse directory are `1. Division`. The case-sensitive pull path treated all 1,044 finished DK matches as missing and re-fetched them over HTTP into a duplicate lowercase directory `Denmark/1. division/` (154 MB) in the shared warehouse, and the worktree index rows were rewritten to the lowercase paths. The config now uses `1. Division`; the duplicate directory was deleted, the index paths restored to the capital-D spelling, and the one match that existed only in the duplicate (5764526, finished 2026-11-09) was re-fetched into the correct directory. Four recent matches (5764525, 5764528, 5764529, 5764530 — round 14, 2026-11-06/07) had their stats revised by FotMob between the original pull and the re-fetch (e.g. 5764528 total shots home 9 → 10, SOT home 2 → 4); those four JSONs were refreshed so the warehouse holds the current snapshot, and the rebuilt CSV is now md5-identical to the run-1 CSV (b32e186e5770c322811c3c138f2203d3). Run 2 must show fetched_new=0 for DK, proving the fix. Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the CO-PrimeraA fresh-worktree trap did not trigger in either run — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted cleanly in both runs with no copy and no code change. Both runs shared the box with the HR-HNL join proof run and the final Codex-sol audit — no kills, no restarts, no retries.

AU-ALeagueWomen has joined with corners (arm `x7`) and SOT (arm `RS`), both PROVISIONAL PASS; cards (arm `X8`) did NOT join — it was stopped at the X8 operational gate (see below). Corners in `reports/C_AUW_VERDICT.md`: dev pooled n=330 X7 LL@9.5 0.695593 vs Gate Zero 0.700197, league base 0.713786 and naive 0.716623 — both pass dev; virgin 2025/2026 n=110 X7 LL@9.5 0.684884, calibration −3.205pp, SE 4.739pp; Gate Zero 0.694234 FAILS leg (i) against naive (0.688210), so X7 is the only eligible arm; dev sign check 2/3 PASS. Fitted params: gamma 0.15, r 1.1887220308967725, beta [0.0] (no box-touch signal ships), fit_n 429. Corners configuration is primary 9.5, ladder 8.5/9.5/10.5, halves share 0.48, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5. SOT in `reports/S_AUW_VERDICT.md`: dev pooled n=330 RS LL@10.5 0.683937 vs Gate Zero 0.685236, base 0.694965 and naive 0.691271 — both pass dev; virgin n=110 RS LL@10.5 0.643041 vs Gate Zero 0.643941 (a 0.0009 LL margin — RS ships on the lower virgin LL), calibration +1.471pp, SE 4.546pp; dev sign check 2/3 PASS. SOT configuration is primary 10.5, ladder 8.5/9.5/10.5, halves share 0.469, div AU-ALeagueWomen, ratio_prior 20000 (stated explicitly; the RS default is 20000), 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5, team_key id. Goals failed dev and total shots failed dev — both excluded. Cards X8 (K-AUW PROVISIONAL PASS on the numbers: dev pooled n=330 X8 LL@2.5 0.673358 vs Gate Zero 0.676237; virgin n=110 X8 0.597092, calibration +1.616pp, SE 4.328pp; dev sign 3/3) was STOPPED at the X8 operational gate, the same gate that stopped DE-2Bundesliga and PL-Ekstraklasa cards X8: the referee arm needs pre-match appointments, and FotMob carries none for AUW — the leagues payload for 2026/2027 has 91 upcoming fixtures, 0 of which mention a referee anywhere in their JSON, and a per-fixture matchDetails check of all 91 shows the infoBox Referee text empty on every one (the key exists, the name does not). The history column is populated (19/19 played 2026/2027 matches, 550/597 overall) but that does not pass the gate, which is about pre-match appointments only. No cards block was added and no X8 plumbing was shipped; do not ship Gate Zero in its place. Latent defect recorded for any future cards attempt: `predict_cards` would silently drop all AUW history anyway, because the builder writes home_yellow_cards/away_yellow_cards while the adapter only accepts yellow_home/yellow_away or yellow_cards_home/yellow_cards_away. Three adapter/config points, all verified. First, the AUW builder writes home_-prefixed stat columns (home_corners, home_total_shots, home_ShotsOnTarget) and no `league` column, so the stock adapters cannot read it: `predict_corners` works through its existing `columns` opt-in (HU-NBI precedent) plus `exclude_phases: ["finals"]` (the frozen harnesses are regular-only; US-USLLeagueOne precedent), with no code change. Second, `predict_sot` needed the same two opt-ins added, mirroring the corners precedent: a `columns` mapping rewrites the CSV through a temp file (standard name -> the CSV's actual name), the market div is injected as `league` when that column is absent, and with team_key id the team-name columns are swapped for the team ids exactly as the frozen harness keys its rows — without this the frozen engine's load_matches silently loads ZERO rows from the AUW CSV (verified: 0 rows unamended, 568 regular rows with the mapping). Inertness was proven on AU-ALeague, the natural probe (same country, RS arm, no columns key): HEAD vs amended `predict_sot` on 8 fixed pseudo-upcoming fixtures produced byte-identical output. Third, `settle` now honours the `columns` mapping for SOT exactly as it already did for corners: without it the SOT actuals would resolve to the lower-case fallback and AUW SOT would never settle (verified with a synthetic ledger entry: SOT settles with actual_total 7.0 and corners with 6.0 on the same played match; inertness on AU-ALeague SOT settle: 3 settled under both versions with identical grading lines). The config differs from the brief's block in four stated ways: no `team_matches` line (the builder writes no team table; HU-NBI precedent), the SOT block adds team_key id + columns + exclude_phases, the corners block adds columns + exclude_phases, and the cards block is omitted (gate fail). The data builder's frozen-count assert is now a floor (`>= 597`, AU/MLS/USLL1/AE precedent) and nothing else in it changed; the rebuild holds 597 rows (568 regular + 29 finals). Corners shipped-CSV ladder note: the shipped virgin CSV's ladder columns are [9.5, 10.5, 11.5] while the frozen protocol ladder is [8.5, 9.5, 10.5] — the evaluated lines reproduce exactly (col 9.5 LL 0.684884, col 10.5 LL 0.655306), so the CSV simply does not export the 8.5 column; the block ladder follows the frozen protocol. The shipped CSV's halves also use a stale 0.452 share (fixed to the frozen 0.480 in the harness by ca1da555 after the CSV was written), so the adapter's 1H/2H columns differ from the shipped CSV by design and the replay check is on FT mu and the 9.5/10.5 columns. The independent recompute of the shipped virgin predictions reproduces all three verdicts exactly from the per-match CSVs (corners X7 LL@9.5 0.684884, SOT RS LL@10.5 0.643041, cards X8 LL@2.5 0.597092). Replaying through the runner adapters (live refit on full history) differs by named, by-design causes only: corners max |dmu| 1.771, mean 0.718, replay LL@9.5 0.733020 vs shipped 0.684884; on pre-virgin history only max |dmu| 0.951, mean 0.315, LL 0.691199; and on the exact causal-state copy the adapter reproduces the shipped mu at exactly 0.0 (max |dmu| 0.0, max |dp| 0.0) with the frozen fitted params (gamma 0.15, r 1.1887220308967725, beta [0.0], fit_n 429). SOT live refit max |dmu| 1.569, mean 0.334, replay LL@10.5 0.619206 vs shipped 0.643041; on pre-virgin history max |dmu| 1.990, mean 0.794, LL 0.694654 — the whole causal gap is the update-order effect (the adapter predicts all 110 virgin fixtures from pre-virgin state while the frozen harness updates as it walks the season): a harness-style replay with within-virgin updates suppressed reproduces mean |dmu| 0.793747 exactly, and the harness-style causal replay itself reproduces the shipped file at max |dmu| 1.8e-15. Two full end-to-end proof runs on 2026-11-10 (VM date; 2026-11-11 WIB) — 52 leagues, 107 markets, 12,764 predictions each, zero errors in either run; run 1 fetched only J1's 2,092 matches into the fresh worktree, run 2 fetched_new=0 in every league. Both runs completed first try with `MALLOC_ARENA_MAX=2` (run 1 ~34 min, run 2 ~27 min) despite the DK-1Division join proof run sharing the box for the first half of run 1 — no kills, no restarts, no retries. Of 263 snapshotted output files (daily CSVs, ledgers, settled-keys sidecars, grading ledgers), all 263 are bit-identical between the runs, including every AU-ALeagueWomen output (the ZA-PSL known pre-existing case did not differ this time); the AUW ledger still holds exactly 182 entries with run 2 appending nothing. AU-ALeagueWomen predicted real fixtures on day one: 91 upcoming 2026/2027 fixtures per market in both runs (2026-11-14 to 2027-04-11), first 2026-11-14 Melbourne City FC (W)–Newcastle Jets (W) (corners mu 8.5740, P(over 9.5) 0.3620; SOT mu 10.4237, P(over 10.5) 0.4006); corners mu spans 7.3751–9.3085, SOT mu spans 8.9312–11.3478, the 1H shares are exactly 0.48 (corners) and 0.469 (SOT) on all 91 rows, the ledger holds 182 entries, and nothing has settled yet (all fixtures are in the future). It is a world league (Australia, `A-League Women`, FotMob id 9495) over split-year seasons 2021/2022–2026/2027, 11 teams in 2025/2026 and 2026/2027 (10 in 2021/2022, 12 in 2023/2024–2024/2025), straight double round-robin plus finals (finals excluded from every fit by the frozen regular-only rule); at the join the rebuild held 597 matches (70/99/132/138/110 regular per completed season plus 29 finals, 19 played in the in-progress 2026/2027). Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs, and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`; the CO-PrimeraA fresh-worktree trap did not trigger in either run — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted cleanly in both runs with no copy and no code change.
IS-BestaDeildin has joined with SOT (arm `GZ`), corners (arm `x7`) and total shots (arm `B`), all PROVISIONAL PASS in `reports/S_IS_VERDICT.md`, `reports/C_IS_VERDICT.md` and `reports/T_IS_VERDICT.md`. Goals and cards failed dev and are excluded. It is an Iceland world league (FotMob id 215, ccode ISL, `Besta deildin`, 12 teams, 162 matches per completed season; the rebuild held 942 matches — 132 in 2021 plus 162 per season 2022–2026 — and 1,884 team rows). The 2021/2022 seasons carry no stats at all in the feed, so every adapter's history starts at the 2023 seed season, exactly as the frozen harnesses do. Configuration: SOT primary 9.5, ladder 8.5/9.5/10.5, halves share 0.4644, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5, div IS-BestaDeildin, ratio_prior 200; corners primary 11.5, ladder 10.5/11.5/12.5, halves share 0.4707, 1H ladder 5.0/5.5/6.0, 2H ladder 5.5/6.0/6.5; total shots primary 27.5, ladder 26.5/27.5/28.5, halves share 0.4623, 1H ladder 11.5/12.5/13.5, 2H ladder 13.5/14.5/15.5. No `exclude_phases`: the frozen harnesses score all phases and the virgin n=162 is the full 2026 season (132 regular + 15 championship + 15 relegation). Virgin LLs, recomputed exactly from the shipped per-match CSVs: SOT GZ 0.631861 vs base 0.672605 / naive 0.640239, calibration −1.398pp, SE 3.707pp; corners X7 0.674422 vs GZ 0.698517 / base 0.689293, calibration −2.353pp, SE 3.863pp; total shots B 0.553977 vs A 0.559717 / C 0.566887 / base 0.608400, calibration −3.446pp, SE 3.381pp. Fitted params: SOT nb_r 79.94; corners gamma 0.3, r 1.1860067504340819, beta [0.0], fit_n 474; total shots lambda 300.0, r_A 150.81292325968832, level_cell [30.0, 1.0, 50.0], M_bar 27.93. No adapter change to `run_daily.py` was needed. The SOT frozen walk (harness-style, ratio_prior 200) reproduces all 162 shipped rows at exactly 0.0 on all 12 columns; the corners frozen params on adapter-built features reproduce all 162 at exactly 0.0 on all 12 columns; the total-shots adapter call reproduces mu within 0.426 (mean 0.071), entirely the same-day level-layer effect — zero (max 7.1e-15) on single-match dates, since the harness updates the league-wide level layer after each match while the adapter feeds a whole date at once — with adapter LL@27.5 0.555773 vs shipped 0.553977. The SOT live-adapter gap (max |Δmu| 1.885, mean 0.380) decomposes into the within-virgin update effect (pre-virgin-state-only walk vs shipped: max 1.871, mean 0.302) and the future-leakage effect (live adapter vs pre-virgin-state-only: max 2.199, mean 0.603) — both by-design consequences of the adapter predicting from full-history state. The corners live-adapter gap is only the r refit (live fit keeps gamma 0.3 and beta [0.0], r 1.1860 → 1.1974 on full history): mu matches at 0.0, p_over 11.5 within 0.0013, live LL@11.5 0.674457 vs shipped 0.674422. Two adapter-path findings, both verified immaterial for this league. First, the team-name split is real: nine FotMob ids carry two spellings (4472 Keflavik/Keflavík, 4516 HK Kopavogs/HK Kópavogs, 6017 Vikingur Reykjavik/Víkingur Reykjavík, 6291 Fram Reykjavik/Fram Reykjavík, 8004 IA Akranes/ÍA Akranes, 8130 KR Reykjavik/KR Reykjavík, 8151 FH Hafnarfjordur/FH Hafnarfjörður, 8299 IBV Vestmannaeyjar/ÍBV Vestmannaeyjar, 8332 Breidablik/Breiðablik); the diacritic spelling becomes sole in 2026 for all nine, and Keflavík (4472) and Víkingur Reykjavík (6017) appear in diacritic form only in 2026. The frozen harness keys history on raw names, so the runner does the same — no `team_key`, no canonicalisation: an id-keyed walk is worse (max |Δmu| 1.064 vs 0.0 name-keyed), which is what the DK precedent's remap would have broken here. Second, the corners adapter's in-memory history build bypasses `core.load`'s 2023 touches quarantine, so z_bt differs on 38 of 648 rows — but quarantined vs unquarantined fits are identical on the same window (gamma 0.3, beta [0.0], r equal to 15 digits), so no quarantine opt-in was added and no blocker arose. Total shots: `fitted_params.json` carries no `half_split`, so the arm-B fallback to the market's frozen `halves_share_1h` engages (CN precedent) — the 1H share is exactly 0.4623 on all 162 replay rows. The data builder's frozen-count assert is now a floor (`>= 942`, AE/USLL1 precedent); the rebuild holds exactly 942 rows. Two full end-to-end proof runs on 2026-11-10/11 (VM dates; 2026-11-11 WIB), 54 leagues, 114 markets, 12,956 predictions each, zero errors in either run; run 1 fetched only J1's 2,092 matches into the fresh worktree, run 2 fetched_new=0 in every league. The runs straddled midnight UTC, so run 2's ledger entries carry run_date 2026-11-11 while run 1's carry 2026-11-10: of 276 snapshotted files, the only 48 that differ are the ledger.jsonl files, each holding exactly the run-1 entries plus an identical set dated 2026-11-11 (e.g. DK-1Division 192+192, J1 720+720); all 228 other files, including every IS-BestaDeildin output, are bit-identical. The 2026 season is complete and 2027 fixtures are not published yet, so IS predicted 0 upcoming fixtures per market in both runs and nothing settled; the daily CSVs are header-only and the ledger holds no entries from the runs. A synthetic settlement on finished match 5225640 (2026-05-21, ÍA Akranes–ÍBV Vestmannaeyjar; actuals SOT 9.0, corners 12.0, total shots 28.0, each within 1.0 of its primary line) proves `settle()` works: SOT live exp 10.1068, P(over 9.5) 0.6474, chosen over, miss, LL 1.0426; corners live exp 11.5311, P(over 11.5) 0.4782, chosen under, miss, LL 0.7378; total shots live exp 29.6751, P(over 27.5) 0.6258, chosen over, hit, LL 0.4687. Each market settled exactly once (a second settle pass settled nothing). Replay artefact, stated plainly: feeding a played match as an upcoming fixture makes `predict_corners` return two rows for it (the history copy with correct prior-only features, exp 11.5311, and the fixture copy whose features are built on leaked full-history prior, exp 12.6920, because the out-of-order fixture rows land at the end of the FeatureBuilder input); both rows landed in the ledger — `write_predictions` dedups only against the pre-existing ledger, not within one call — and `settle()` graded the first (correct) entry. In production this cannot occur: upcoming fixtures are future-dated and absent from the CSV, so exactly one prediction per fixture with correct prior. Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs, and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`; the CO-PrimeraA fresh-worktree trap did not trigger in either run — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted cleanly in both runs with no copy and no code change. All proof runs were made with `MALLOC_ARENA_MAX=2`.

SA-FirstDivision has joined with SOT (arm `GZ`), CLEAN PASS in `reports/S_SAFD_VERDICT.md`. Goals, corners, total shots and cards all failed their gates and are excluded. It is a Saudi Arabia world league (FotMob id 10721, ccode KSA, `Saudi First Division`, 18 teams, 306 regular matches per completed season plus 3 promotion-playoff matches; the rebuild held 712 matches — 309 per completed season 2024/2025 and 2025/2026, 94 played in the in-progress 2026/2027 — and 1,424 team rows). The 2024/2025 season carries no stats at all in the feed, so every adapter's history starts at the 2025/2026 seed season, exactly as the frozen harness does. SOT configuration is primary 8.5, ladder 7.5/8.5/9.5, halves share 0.454, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5, div SA-FirstDivision, ratio_prior 200 (documentary — the engine is `Engine(ms, arm)` and fixes the prior at 200 internally, DK pattern). Dev pooled n=214 (90 warm-up + 214 scored, date-grouped predict-then-update): Gate Zero LL@8.5 0.6944 vs league base 0.6963 / naive 0.6987 — both arms pass dev. Virgin 2026/2027 TRANSITIONAL n=94, read once: Gate Zero LL 0.686013 vs base 0.690133 / naive 0.705866; calibration −0.686pp pred−actual, SE 5.145pp — inside the 1.0pp clean band. RS 0.686166 fails leg (i) vs Gate Zero and does not ship. Fitted params: nb_r 79.94. Two adapter changes in `run_daily.py`, both opt-in and engaged only by new market keys. First, `predict_sot` now honours a `seasons` allowlist, mirroring the `ratio_prior` signature-check pattern: when the market carries a `seasons` list AND the loader's signature accepts a second positional, it is passed; leagues without the key call exactly as before. SA's loader is `load_matches(path, seasons)` with seasons REQUIRED, so the stock one-argument call raises TypeError (verified: HEAD raises `TypeError: load_matches() missing 1 required positional argument: 'seasons'`), and SA passes ["2025/2026", "2026/2027"] only — score-only 2024/2025 (all 309 rows with empty stat fields) would crash the loader's bare `float(r[k])`. Inertness: HEAD vs amended `predict_sot` on DK-1Division (GZ, team_key id) is byte-identical on 8 fixed pseudo-upcoming fixtures. Second, `predict_sot` now honours `regular_rounds_only`: the frozen harness excludes playoffs, but the pull returns whatever FotMob lists as upcoming; the pull's fixture dicts carry `round` (verified on the completed 2025/2026 payload: "1".."34" regular, "Promotion Play-offs - Semi-finals"/"Final" for the 3 playoff fixtures), so when the market opts in, fixtures whose round is not a plain round number are skipped — a fixture with no round info passes through, and leagues without the key are unchanged (verified: a playoff-round fixture is skipped for SA and kept for DK). The pull also carries `round` in its upcoming dicts for world leagues (additive; no other consumer reads it). One defect in the join path was found by the first proof run and fixed in the league builder: SA's `build_data.py` had no `main()` (every other world builder defines one), so `rebuild_csv_world` raised `AttributeError: module 'daily_SA-FirstDivision_builder' has no attribute 'main'` and SA predicted nothing in that run; `main()` now wraps the existing `__main__` block, and `rebuild_csv_world` rebuilds 712 rows cleanly. Replay (independent recompute of the shipped virgin predictions, 94 rows): the harness-style causal walk reproduces the shipped CSV at max |Δmu| 1.8e-15 and the virgin LL at 0.686013 exactly. The live adapter walk differs by at most 0.4580 on mu (mean 0.1242) and 0.2181 on p_over 8.5 (worst fixture 1000018433, 2026-08-31 Al-Saqer FC–Al Akhdoud, adapter 0.525 vs shipped 0.307 — both clubs are 2026/2027 newcomers with no dev history, so the adapter's full-history state knows far more about them than the harness did at that date), with replay LL@8.5 0.637147 — decomposed: the refit-anchor effect is exactly 0.0000 (the adapter's first refit lands on the harness's 7-day grid), the no-within-virgin-update effect is 0.4676, and the future-leakage effect (the adapter's Ratings/naive state is built from the full history including later virgin matches, while the harness updates as it walks) is 0.5856 max pairwise; the adapter's replay LL looks better than the gated 0.686013 only because of that leakage, and is not the gated number. The 1H/2H columns differ by at most 0.044 (mean 0.011), the same mu-driven cause — the 1H share is exactly 0.454 on all 94 replay rows. The loader's exclusions were verified in the replay: it returns 398 rows (304 dev + 94 virgin), excluding the 3 playoff and 2 awarded rows of 2025/2026. Team names: the fitted 24 teams equal the union of the 2025/2026 and 2026/2027 team sets exactly, and the FotMob index names match the CSV's canonical names on all 712 matches — no split, so no `team_key` and no canonicalisation. Two edge findings. First, playoffs: the 2026/2027 promotion playoffs (~May 2027) are not yet published — FotMob lists fixtures only ~2 months ahead, and the current pull's 68 upcoming fixtures run 2026-11-18 to 2027-01-10, all regular rounds (the 9 round-19 fixtures dated 2027-01-03..05 are marked cancelled in the feed and the pull already skips cancelled fixtures); the `regular_rounds_only` opt-in above is what will keep the playoffs unpredicted when they appear. Second, awarded matches at settlement: 2026/2027 has 0 awarded rows; the only 2 awarded rows in the data are 2025/2026 regular matches (2026-01-21 Al-Faisaly–Abha 3-0, match 1000006540; 2026-01-22 Al-Ula FC–Al-Wehda 0-3, match 1000006697) and both carry scores but NO SOT/total-shots stats (empty fields), so `settle()`'s empty-actual guard skips them rather than grading them wrongly. The risk is latent only: if FotMob ever attaches stats to an awarded match, `settle()` would grade it while the harness excludes awarded rows from scoring. Proposed minimal opt-in, NOT implemented: a market key `exclude_awarded_settle: true` making `settle()` skip rows with `awarded` != "0" (the CSV already carries the column). Three full end-to-end proof runs on 2026-11-11 (VM date; 2026-11-11 WIB), 55 leagues, 115 markets, all with `MALLOC_ARENA_MAX=2`. Run 1 (exit 0, ~34 min): 12,956 predictions, 0 settled, 1 error row in 392 log rows — the SA `main()` defect above, so SA predicted nothing (fetched_new 2,092 for J1's fresh store only, every other league 0). Run 2's first attempt was killed by a runtime restart at 5 leagues (log rows 392..426, no error — the restart, not the run); the relaunched run 2 (exit 0, ~28 min): 13,024 predictions, 0 settled, 0 errors in 395 log rows, fetched_new=0 in every league; SA predicted 68 upcoming fixtures, first 2026-11-18 Al-Adalah–Al-Orobah FC (match 1000018504, exp_total 8.0903, p_over 8.5 0.4167), mu range 7.2146–9.3080, 1H share exactly 0.454 on all 68 rows, ledger 68 entries, nothing settled, settled_keys empty. Run 3 (exit 0, ~28 min): 13,024 predictions, 0 settled, 0 errors in 395 log rows, fetched_new=0 in every league; SA again 68 fixtures with the same first fixture and values, ledger still exactly 68 entries (dedup by market/match_id/run_date works). Of 280 snapshotted output files (daily CSVs, ledgers, settled-keys sidecars, grading ledgers), all 280 are bit-identical between runs 2 and 3, including every SA-FirstDivision output — the known ZA-PSL corners case did not differ this time. Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`. The CO-PrimeraA fresh-worktree trap did not trigger in any run — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted cleanly in all runs with no copy and no code change.

LV-Virsliga has joined with SOT (arm `GZ`), CLEAN PASS in `reports/S_LV_VERDICT.md`. Goals, corners, total shots and cards all failed their gates and are excluded. It is a Latvia world league (FotMob id 226, ccode LVA, `Virsliga`, 10 teams, straight quadruple round-robin, 36 rounds, 180 matches per complete season, no play-offs in the feed; calendar-year seasons 2021–2026; the rebuild held 1,011 matches and 2,022 team rows — 112 in truncated 2021, 180 per season 2022–2025, 179 in 2026 — with the 6 two-legged relegation finals of 2022–2024 excluded by the builder). The stats era starts 2025-03-05 (no stats block before it); SOT dev is a walk-forward over the stats era only (warm-up 2025-03-05–04-30, scored 2025-05-01–11-09, n=133): Gate Zero LL@9.5 0.682846 vs league base 0.689921 / naive 0.683999 — Gate Zero beats both baselines on dev (vs naive by only 0.00115 — thin, but a pass); RS 0.685650 loses to naive and is dead at dev. Virgin 2026 n=179, read once: Gate Zero LL 0.679910 vs league base 0.679994 / naive 0.680898; calibration +0.21pp actual−predicted, SE 3.697pp. Leg (i) passes by 0.000084 over the league base rate — the frozen rule is a comparison, not a margin, and it passes; leg (ii) |+0.21pp| ≤ 1.0pp is clean; leg (iii) Gate Zero is exempt (RS dead at dev). Mean predicted SOT 8.98 vs actual 9.19 on virgin. SOT configuration is primary 9.5, ladder 8.5/9.5/10.5, halves share 0.4637, 1H ladder 3.5/4.5/5.5, 2H ladder 4.5/5.5/6.5, div LV-Virsliga, ratio_prior 200. Fitted params: walk-forward model, no single fitted parameter set (`engine/sot/fitted_params_virgin.json` carries only the market/line/arm record — see the engine README). No `run_daily.py` change was needed: the stock `predict_sot` path fits — the loader is `load_matches(path, allowed_seasons=None, ...)` (SOT v5 pattern, same as IS), requires `has_stats_all == "1"` plus the four stat columns, reads `div = r["league"]` (the builder writes the `league` column), keys history on raw team names, and the engine is `Engine(matches, arm, *, ratio_prior=None)`, so the runner's `ratio_prior: 200` kwarg is accepted; no `seasons` key (the SA opt-in does not apply — pre-stats rows are dropped by the `has_stats_all` filter exactly as the harness does), no `columns`/`exclude_phases`/`team_key` (the 6 relegation finals are excluded from the CSV tables by the builder itself, and the CSV carries standard stat names). No adapter change was made, so no inertness probe was required. The builder's asserts are untouched hard equalities (source 1,017 / rows 1,011 / excluded 6): the RFS–Riga FC round-36 match has NOT appeared — a live FotMob probe shows match 5162094 (Riga FC vs RFS, 2026-11-08) is listed as cancelled/postponed, not finished, so it is neither fetched nor predicted and the counts are unchanged. Team names: the two ids with two spellings (8016 FK Liepaja/FK Liepāja, 662738 Grobina/Grobiņa) each use a single spelling across the whole stats era (FK Liepāja and Grobiņa in all 359 stats rows; the ASCII spellings occur only in pre-stats seasons the loader drops), so the name-keyed history is unsplit — no canonicalisation, no `team_key`. Replay (independent recompute of the shipped virgin predictions, 179 rows): the harness-style causal walk reproduces the shipped CSV at max |Δmu| 3.6e-15 and max |Δp| 0.0 on every ladder line (LL@9.5 0.679910 exact). The live adapter walk (full-history state, no within-virgin updates) differs by at most 0.8429 on mu and 0.1922 on p_over 9.5 (worst fixture 5161934, 2026-04-04, adapter mu 8.9837 vs shipped 9.8265, p 0.4332 vs 0.5361), with replay LL@9.5 0.672860 — decomposed: the refit-anchor effect is 7.8e-14 (the adapter's refit grid anchored at the first virgin date reproduces the harness thetas exactly), the no-within-virgin-update effect is 0.5888 on mu (0.1730 on p), and the future-leakage effect (the adapter's Ratings/naive state is built from the full history including later virgin matches, while the harness updates as it walks) is 0.8540 on mu (0.1419 on p); the adapter's replay LL looks better than the gated 0.679910 only because of that leakage, and is not the gated number. The 1H share is exactly 0.4637 on all 179 replay rows. Two full end-to-end proof runs on 2026-11-11 (VM date; 2026-11-11 WIB), 56 leagues, 116 markets, all with `MALLOC_ARENA_MAX=2`. Run 1 (exit 0, ~28 min, log 03:00–03:27 UTC): 13,024 predictions, 0 settled, 0 errors in 400 log rows; fetched_new 2,092 for J1's fresh store only, every other league 0. Run 2's first attempt was killed by a runtime restart at 18 leagues (138 log rows, 03:37–03:48 UTC, 0 errors — the restart, not the run); the relaunched run 2 (exit 0, ~27 min, log 03:49–04:17 UTC): 13,022 predictions, 0 settled, 0 errors in 400 log rows, fetched_new=0 in every league. The 2-prediction difference is a live-feed change, not a runner defect: AU-ALeagueWomen fixture 1000020337 (Newcastle Jets (W) vs Adelaide United (W), 2026-11-21) was listed as postponed/cancelled by FotMob between the runs — verified by a live probe — so the relaunch correctly stopped predicting it (91→90 rows in both its markets). LV predicted 0 upcoming fixtures and settled 0 in every run (the 2026 season is complete and the 2027 season is unpublished); its daily CSV is header-only and its ledger holds no entries from the runs. Of 284 snapshotted output files (daily CSVs, ledgers, settled-keys sidecars, grading ledgers), 281 are bit-identical between run 1 and the relaunched run 2; the only 3 that differ are the two AU-ALeagueWomen files above and ZA-PSL corners, whose difference is a live-feed team-name spelling change ("AmaZulu FC" → "AmaZulu" on 19 rows) with every numeric value bit-equal (max |d| 0.0 on exp_total, every ladder p_over, both halves columns, and dates). One process caveat, stated plainly: the run-1 snapshot tar lived in /tmp and was lost in the same runtime restart that killed run 2's first attempt, so the comparison baseline is the post-run-1 on-disk state re-snapshotted to `~/workspace/lv-proof` after the killed attempt — 38 leagues' files are pristine run-1 outputs, while the 18 leagues the killed attempt had processed carry daily CSVs it deterministically rewrote (per-league/market predicted counts match run 1 exactly on all 43 common entries; ledgers are deduplicated, so no duplicate lines). A synthetic settlement on finished match 5161946 (2026-04-14, SK Super Nova–Riga FC; actual SOT 9.0, within 0.5 of the 9.5 primary line) proves `settle()` works: adapter exp_total 9.3850, P(over 9.5) 0.4270, chosen under, hit, log loss 0.5569; it settled exactly once (a second settle pass settled 0), and the four touched runtime files were restored byte-identical to the post-proof-run state afterward (verified against the snapshot). Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`. The CO-PrimeraA fresh-worktree trap did not trigger in any run — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted cleanly in all runs with no copy and no code change.

AR-PrimeraBNacional has joined with cards only (arm `x8`), PROVISIONAL PASS in `reports/K_BNAC_VERDICT.md`: dev pooled n=1,334 (2024+2025) Gate Zero LL@4.5 0.680252, X8 0.659605 — both pass dev, X8 wins the dev sign check 2/2 blocks; virgin 2026 n=648, read once, X8 LL@4.5 0.669291 vs Gate Zero 0.676939 / league base 0.692222 / naive 0.687911, calibration −1.0611pp actual−predicted, SE 1.9191pp (breach 0.0611pp ≤ 1 SE → PROVISIONAL); the both-pass rule ships the lowest virgin LL, X8. Goals FAIL dev and are excluded. It is an Argentina world league (FotMob id 8965, ccode ARG, `Primera B Nacional`, 36 teams in 2026; calendar-year seasons 2021–2026; the rebuild held 3,874 matches and 7,748 team rows). The builder asserts phase counts group 3,874 / playoff 92 but writes group rows only, so the CSV carries no playoff rows and the virgin 648 is the full 2026 group season — no `exclude_phases` (the frozen harness scores all phases, and there are none to exclude). Cards configuration is primary 4.5, ladder 3.5/4.5/5.5, halves share 0.3900912370, 1H ladder 0.5/1.5/2.5, 2H ladder 1.5/2.5/3.5, `exclude_seasons: ["2021", "2022"]`, and `cards_actual: [yellow_home, yellow_away]`; there is no `team_matches` key (the builder writes `team_matches.csv`, not `bnac_team_matches.csv`, and the world rebuild path never reads the key). The two added keys are forced, not stylistic: the 2021/2022 `yellow_home`/`yellow_away` values are literal `"nan"` strings, which the default empty-value skip does not drop and `int(float("nan"))` crashes on, so the seasons must be excluded (CN precedent); and the CSV carries no `yellow_cards_home`/`yellow_cards_away` columns, so without the `cards_actual` override `settle()` would silently grade nothing (KR/NO/FI precedent). Fitted params: HL 270, K_PRIOR 8, K_REF 8, r 112.39, shipped_arm x8. The operational gate passed, measured the day of the join: 9 upcoming fixtures (all 2026 Reducido playoffs, 2026-11-14/15), 0/9 carry a referee mention in the leagues payload, 1/9 carries a referee name in matchDetails infoBox (match 6575527 Godoy Cruz vs Tristán Suárez, 2026-11-15, Maximiliano Ramírez) — stated plainly, that one appointed referee has zero in-league priors, so all 9 production predictions are Gate-Zero-equivalent (multiplier 1.0 on every row); the gate passes on its ≥1 rule, and the per-fixture Gate Zero fallback covers the rest. This is the FIRST X8 join, so `predict_cards` in `run_daily.py` gained the X8 path, all of it opt-in by `arm == "x8"`: it accepts the arm; it extracts history-row construction into `_cards_history_rows` (which also adds the team-column alias, `home_team_id`/`home_team` preferred, `home_id`/`home_name` fallback — this builder uses the latter spelling — and attaches `referee` plus the harness's `(date, match_id)` `key` tuple); for `x8` it fetches each upcoming fixture's appointed referee from FotMob matchDetails (one shared client per run, `follow_redirects=True`, a fixture dict that already carries a referee uses it, a failed fetch falls back to no referee and never fails the run); an engine without `estimate_r` supplies its frozen dispersion as module-level `R` (112.39 here) with a two-argument `nb_over(mu, line)`, while every other cards engine keeps the existing `estimate_r` + three-argument path; and `x8` output rows additionally carry `referee`, `n_prior`, `multiplier`, `fallback`, `fallback_reason` (mirroring the harness's `_csv_row`). One defect in that first version was caught by the inertness probe and fixed before the proof runs: attaching `referee` to history rows unconditionally activated dormant referee branches in `gate_zero` engines (KR-KLeague1's `update()` then requires `row["kickoff_utc"]`, which the runner never supplied, raising `KeyError`) — referee identity is now attached only for `x8`, so `gate_zero` rows are exactly as before. Inertness was proven on KR-KLeague1 cards (`gate_zero`): HEAD vs amended `predict_cards` on 8 fixed pseudo-upcoming fixtures is byte-identical. The BNAC engine was never adapter-runnable under `gate_zero` (HEAD fails at `home_team_id`, the amended adapter at `row["referee"]`) — not a regression; the joined arm is `x8`. Replay (independent recompute of the shipped virgin predictions, 648 rows): the harness-style causal walk through the adapter's own history-row builder reproduces the shipped CSV at max |Δmu| 0.0 and max |Δp| 0.0 on every row, multiplier/fallback/`n_prior` exact on 648/648, LL@4.5 0.669291 exact — and the same walk with arm `gate_zero` reproduces the verdict's Gate Zero virgin LL 0.676939 exactly. The live adapter walk (one `predict_cards` call, upcoming = all 648 virgin fixtures, full-history state) differs by max |Δmu| 1.96456 (mean 0.3758) and max |Δp| 0.2841 at 4.5, LL@4.5 0.629376 — decomposed, not assumed: the gap is entirely state timing, the first virgin fixture (2026-02-13) sits 0.7029 off while the last (2026-11-02) sits 0.0961 off, and all 601 multiplier mismatches come from extra referee priors in the full-history state (0 have identical `n_prior`; e.g. Maximiliano Manduca shipped `n_prior` 0 → replay 29), while the pre-virgin-state-only walk differs by max |Δmu| 1.44879 (mean 0.3034), LL@4.5 0.678042 — the no-within-2026-learning direction. The replay LL looks better than the gated 0.669291 only because of future leakage, and is not the gated number. Team names: all 16 upcoming team names and ids match the CSV exactly, no split, no canonicalisation; live infoBox Referee text matches the CSV `referee` column on 8/8 sampled finished 2026 matches. Two full end-to-end proof runs on 2026-11-11 (VM date; 2026-11-11 WIB), 57 leagues, 117 markets, all with `MALLOC_ARENA_MAX=2`. Run 1 (exit 0, ~28 min, log 04:49–05:17 UTC): 13,031 predictions, 0 settled, 0 errors in 405 log rows; fetched_new 2,092 for J1's fresh store only, every other league 0. Run 2 (exit 0, ~28 min, log 05:17–05:45 UTC): 13,031 predictions, 0 settled, 0 errors in 405 log rows, fetched_new=0 in every league. Of 288 snapshotted output files (daily CSVs, ledgers, settled-keys sidecars, grading ledgers), all 288 are bit-identical between the runs, including every AR-PrimeraBNacional output — the known ZA-PSL corners case did not differ this time. AR-PrimeraBNacional predicted its 9 real upcoming fixtures in both runs (first 2026-11-14 Godoy Cruz–Tristán Suárez, match 6546950, exp_total 4.5341, P(over 4.5) 0.4724; exp_total range 3.8819–5.6716; the 1H share is exactly 0.3900912370 on all 9 rows; the ledger holds exactly 9 entries, run_date 2026-11-11) and settled nothing (all fixtures are in the future). A synthetic settlement on finished match 5239418 (2026-10-31, Godoy Cruz–Almirante Brown; actual yellows 3+2=5, shipped multiplier 1.0322) proves `settle()` works through the `cards_actual` override: live exp_total 4.9448, P(over 4.5) 0.5462, multiplier 1.0341, chosen over, hit, log loss 0.6048; it settled exactly once (a second pass settled nothing), and the four touched files were restored byte-identical afterward. Two environment items: this worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`. The CO-PrimeraA fresh-worktree trap did not trigger in either run — its builder also reads Primera B warehouse JSONs, which are present via the symlinked main-checkout warehouse, so CO rebuilt and predicted cleanly in both runs with no copy and no code change. Two process caveats, stated plainly: the Codex implementation run crashed mid-task (a Rust stderr-pipe panic after printing a large grep dump) before delivering its summary, so its adapter change was reviewed line-by-line and its inertness probe re-run by the runner instead of taken on trust; and a runtime restart wiped /tmp between the proof runs and the synthetic settlement, so the gate/probe/replay scripts are gone but their outputs are recorded here and the proof snapshots live in `~/workspace/arb-proof/`.

KZ-PremierLeague has joined with goals only (Gate Zero, PROVISIONAL PASS in `reports/G_KZ_VERDICT.md`: virgin 2026, complete season, n=240, 1X2 LL 1.0152 vs climatology 1.0678; calibration home-win −1.26pp (SE 3.09pp) and OU2.5 −3.21pp (SE 3.21pp), both breaches within 1 SE → PROVISIONAL on both legs; dev pooled 1X2 LL 1.0290 < climatology 1.0712, RPS 0.2135 < 0.2285, OU2.5 LL 0.6819 < base-rate 0.6929; SHRINK is identical to Gate Zero everywhere it was measured, so the both-pass rule ships the simpler arm). SOT, corners, cards, and total shots are NOT BUILDABLE and are excluded — it is a scores-only league (no SOT target, no corners target, zero plain Yellow, no total-shots target). Goals configuration is primary 2.5, ladder 1.5/2.5/3.5, halves share 0.4539 (the frozen KZ goals constant), 1H ladder 0.5/1.5/2.5, 2H ladder 1.5/2.5/3.5. The shipped virgin fitted params are rho 0.0, mu 1.3373, h 0.2543, 22 teams — the two 2026 entrants, Altai Semey and Irtysh Pavlodar, start at the league mean, a = d = 0. It is a Kazakhstan world league (FotMob id 225, calendar-year seasons 2021–2026, 1,124 matches at the join; the 2026 season is complete at 240 matches). This is the third goals join and the first to need the signature-dispatched adapter: the goals adapter now calls `adjusted_lambdas` with exactly the signature each engine ships — engines taking `(model, home, away, arm, counts)` are called with five arguments, all other engines take the existing path. The trap was proven real: HEAD raises TypeError on KZ in both call forms, and the amended code predicts. Inertness was proven on SCO-Premiership and TR-SuperLig goals: HEAD vs amended `predict_goals` on 8 fixed fixtures each is byte-identical (max |d| 0.0). Replay (independent recompute of the shipped virgin predictions, 240 rows): the harness-style causal walk reproduces the shipped CSV exactly — max |Δlam| 0.0, max |Δp| 0.0, LL 1.015226 = verdict 1.0152 — while the live-adapter walk (one `predict_goals` call, upcoming = all 240 virgin fixtures, full-history state) gives LL 1.000751, decomposed as refit-anchor 0.009951 + within-virgin-update 1.741266 on lam, future leakage 0 by construction. A FotMob probe the day of the join found the 2027 season unpublished (`selectedSeason='2026'`, 0 upcoming), so the join predicts nothing live until FotMob publishes 2027. Two full end-to-end proof runs on 2026-11-11, 58 leagues, 118 markets, all with `MALLOC_ARENA_MAX=2`. Run 1 (exit 0, ~31 min): 13,031 predictions, 0 settled, 0 errors in 410 log rows; fetched_new 2,092 for J1's fresh store only, every other league 0. Run 2 (exit 0, ~30 min, log 07:49–08:19 UTC): 13,031 predictions, 0 settled, 0 errors in 410 log rows, fetched_new=0 in every league. KZ in both runs: 0 upcoming / 0 predicted / 0 errors, header-only daily goals CSV, empty ledger, `[]` settled keys. Of 292 snapshotted output files, 291 are bit-identical between the runs; the one exception is HR-HNL's daily corners CSV, where FotMob moved 12 fixture dates between the runs (2026-11-21→22, 11-28→27/29, 12-05→06/07, 12-12→13/14) — same 116 match_ids and teams, max float difference 1.1e-14 — an upstream listing change, not a code difference. Run 2's first attempt was killed mid-run by a runtime restart at 14:46 WIB (225 of ~410 rows, last write EG-PremierLeague `data_refresh`) and was relaunched from scratch; the partial run is not a proof and was not compared. A synthetic settlement on finished match 5204163 (2026-07-05, Atyrau–Kaspiy Aktau 1–2, actual total 3) proves `settle()` works through the adapter: live exp_total 1.6096, p_over_2.5 0.2191, chosen under, missed, log loss 1.5181; it settled exactly once (a second pass settled nothing), and the four touched files were restored byte-identical afterward. This worktree arrived without the `data_enrichment/fotmob_world` symlink the other runner worktrees carry, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`.

BA-PremierLeague has joined with goals only (Gate Zero, PROVISIONAL PASS in `reports/G_BA_VERDICT.md`: virgin 2026/2027 in progress, n=64, 1X2 LL 0.8880 vs climatology 1.0625, RPS 0.1630; calibration home-win −1.00pp (breach 0.004pp over the 1.0pp boundary, SE 5.41pp) and OU2.5 −2.45pp (breach 1.45pp, SE 6.32pp), both breaches within 1 SE → PROVISIONAL on both legs; dev pooled n=772 1X2 LL 0.9473 < climatology 1.0522, RPS 0.1947 < 0.2283, OU2.5 LL 0.6845 < base-rate 0.6972; SHRINK is identical to Gate Zero everywhere it was measured — the arm is degenerate in this league by construction, since no team ever has 1–5 prior matches under expanding season-blocked fits — so the both-pass rule ships the simpler arm). SOT, corners, cards, and total shots are NOT BUILDABLE and are excluded — it is a scores-only league. Goals configuration is primary 2.5, ladder 1.5/2.5/3.5, halves share 0.4493 (the frozen BA goals constant), 1H ladder 0.5/1.5/2.5, 2H ladder 1.5/2.5/3.5, plus the `exclude_awarded: true` opt-in. The shipped virgin fitted params are rho 0.0, mu 1.1811, h 0.3204, training n=968 — the two 2026/2027 newcomers, Čelik Zenica and BSK Banja Luka, start at the league mean, a = d = 0. It is a Bosnia-Herzegovina world league (FotMob id 267, seasons 2021/2022–2026/2027, 1,036 matches at the join). This is the fourth goals join and the first to need two adapter changes in `predict_goals`: the xG columns are now read with `.get()` (BA's builder writes no expected-goals columns, so None degrades to the goals-only observation exactly as the engines do; leagues carrying the columns are unchanged), and the `exclude_awarded` opt-in drops BA's 4 awarded matches from every fit, matching the frozen prereg and the harness loader — other goals leagues (SCO, TR, KZ) do not opt in, so their fits are unchanged. Inertness was proven on SCO-Premiership and TR-SuperLig goals: HEAD vs amended `predict_goals` on 8 fixed fixtures each is byte-identical. Replay (independent recompute of the shipped virgin predictions, 64 rows): the harness-style causal walk reproduces the shipped CSV exactly — max |Δlam| 0.0, max |Δp| 0.0, LL 0.8880 = verdict 0.8880 — while the live-adapter walk (one `predict_goals` call, upcoming = all 64 virgin fixtures, full-history state) gives LL 0.9271, decomposed as refit-anchor 0.0005 on lam and within-virgin-update 1.0063 on lam (the live fit also sees earlier 2026/2027 results, which the frozen virgin fit does not), future leakage 0 by construction. An independent recompute of the 115 live daily predictions through the real runner adapter in a separate process reproduces the shipped daily CSV exactly — all 19 numeric fields, max |diff| 0.0. Two full end-to-end proof runs on 2026-11-11, 59 leagues, 119 markets. Run 1 (exit 0, log 09:49–10:17 UTC, ~28 min): 13,146 predictions, 0 settled, 0 errors in 415 log rows; fetched_new=0 in every league. Run 2 (exit 0, log 10:22–10:50 UTC, ~28 min): 13,146 predictions, 0 settled, 0 errors in 415 log rows, fetched_new=0 in every league. BA in both runs: 115 upcoming (first 2026-11-21 BSK Banja Luka–Zrinjski Mostar, match 6141013) / 115 predicted / 0 settled / 0 errors, ledger holds 115 entries, `[]` settled keys. Of 296 snapshotted output files, 295 are bit-identical between the runs; the one exception is ZA-PSL's daily corners CSV, where FotMob renamed AmaZulu to AmaZulu FC between the runs — same 160 rows, same match ids and dates, all numeric predictions identical — an upstream listing change, not a code difference. A synthetic settlement on finished match 5927590 (2026-09-02, Široki Brijeg–FK Sarajevo 1–2, actual total 3) proves `settle()` works through the adapter: live exp_total 2.3888, p_over_2.5 0.4274, chosen under, missed, log loss 0.8502; it settled exactly once (a second pass settled nothing), and the four touched files were restored byte-identical afterward. As with the KZ join, this worktree arrived without the `data_enrichment/fotmob_world` symlink, so the symlink to the main checkout's warehouse was restored (git-ignored, no commit impact) before the proof runs; and the worktree carries no `.venv`, so the proof runs used the main checkout's `.venv`.

TZ-PremierLeague has joined with goals only (arm `shrink`, PROVISIONAL
PASS under Lane 1 entry G-TZ-L1 — see
`league/TZ-PremierLeague/reports/VERDICT_L1_G_TZ.md`). Two adapter
opt-ins: `team_key: name` (the frozen prereg keys teams by name —
FotMob ids are shared across the Singida Big Stars / Fountain Gate
FC and Ihefu FC / Singida Black Stars renames, and SHRINK's bite
depends on not merging them) and `exclude_awarded: true` (the two
awarded matches stay out of every fit). The goals arm whitelist now
also accepts `shrink`; leagues without `team_key` key by id exactly
as before. Verified at join prep: the runner's name-keyed SHRINK fit
reproduces the Lane 1 virgin fit float-exactly (max diff 0.0) on the
virgin window's first matchday, and the league builder's frozen
counts are asserted as floors so the in-progress 2026/2027 season
can grow.
FO-PremierLeague has joined with cards only (arm `shrink`, CLEAN PASS
under Lane 1 entry L1-K-FO — see
`league/FO-PremierLeague/reports/VERDICT_L1_K_FO.md`: SHRINK pooled
dev LL@3.5 0.681000 vs base rate 0.682420 / naive 0.693044, reproduced
exactly under `league/gate_lib/`; single sealed read on 2026, n=135 —
SHRINK LL@3.5 0.686989 vs Gate Zero 0.688355 / base 0.693280 / naive
0.730895, calibration predicted − actual −0.63pp (SE 4.29pp), clean;
sign check 3/4). Goals FAIL and SOT/corners/total shots are NOT
BUILDABLE, so cards is the league's only market. It is a Faroe
Islands world league (FotMob id 250, ccode FRO, calendar-year seasons
2021–2026, 810 matches at the join, one awarded match excluded).
Cards configuration is primary 3.5, ladder 1.5/2.5/3.5/4.5, halves
share 0.348 (the frozen FO cards constant), 1H ladder 0.5/1.5/2.5,
2H ladder 1.5/2.5/3.5, `cards_actual: [yellow_home, yellow_away]`
(the graded target is the event-unified yellows, which the builder
writes under those columns), plus the new `exclude_excluded: true`
opt-in. The join needed three adapter changes in `run_daily.py`, all
inert for the leagues already served: the cards arm whitelist now
also accepts `shrink`; `predict_cards` dispatches on the engine's
own interface — an `Online` whose constructor takes the shrinkage
prior is built with K=8 for `gate_zero` / K=16 for `shrink` (FO's
J1-seed engine is the first such engine in the runner), and an
engine exposing `predict(row)` instead of `prediction(row, arm)` is
called through that entry point, with `date`/`match_id` added to the
prediction row for its causality assertion (the other engines ignore
the extra keys); and `_cards_history_rows` drops `excluded=1` rows
when a market opts into `exclude_excluded` (FO's awarded match) and
falls back to the builder's `home`/`away` team columns when no
`home_team`/`home_name` column exists. FO's builder was also brought
to the runner contract: it now exposes `INDEX`/`MAIN_REPO` and a
no-argument `main()` writing the league's own matches CSV (the CLI
form is unchanged and byte-identical), with its frozen build-time
totals asserted as floors so future seasons can grow the index; the
six completed seasons keep their exact eligible counts. Verified at
join prep (NOT a full end-to-end runner proof — that runs at merge
time, as with the other Lane 1 joins): the runner-form builder
rebuilds the 810-row table byte-identically; the runner's
`predict_cards` on a dev-only history reproduces the shipped virgin
fit float-exactly on the virgin window's first fixture (match
5136308, AB Argir–B68 Toftir: exp_total 4.254741778131308,
P(over 3.5) 0.6001950627998901, and the full ladder/halves row
identical); a future-dated live prediction runs cleanly; a synthetic
settlement on match 5136308 (actual total 3 via
`yellow_home`/`yellow_away`) settled exactly once with the touched
files restored; and inertness was proven on AU-ALeague cards
(`gate_zero`): HEAD vs amended `predict_cards` on a fixed fixture is
identical. No referee arm exists in this league (identity coverage
0/810) and none is configured. The 2026 season is complete, so the
join predicts nothing live until FotMob publishes the 2027 season
(the `seasons` list will need the new season added then, as for the
other calendar-year leagues). This worktree arrived without the
`data_enrichment/fotmob_world` symlink, so the symlink to the main
checkout's warehouse was restored (git-ignored, no commit impact)
before the builder proof; the worktree carries no `.venv`, so the
proofs used the main checkout's `.venv`.
ID-SuperLeague has joined with cards only (arm `x5`, CLEAN PASS under
Lane 1 entry L1-K-ID — see `league/ID-SuperLeague/reports/VERDICT_L1_K_ID.md`:
dev pooled LL@4.5 0.6940 reproduced exactly via gate_lib against base
rate 0.6959 and naive trailing-10 0.6978, Gate Zero 0.7003 failing dev
as documented; single sealed read of 2025/2026, n=306: X5 LL@4.5
0.6846 vs Gate Zero 0.6859, base rate 0.6923, naive 0.6933;
calibration −0.91pp (SE 2.84pp), clean; sign check 3/3). Goals failed
its dev gate in the original build and SOT, corners and total shots
are NOT BUILDABLE (no stats-feed target in the virgin season), so
cards is the league's only market. The target is event-unified
yellows scored only on events_complete matches — the builder writes
`yellow_home`/`yellow_away` empty for truncated feeds, so the
runner's history loader drops those rows exactly as the frozen
harness does — and the market opts into `exclude_phases`
(championship_playoff, stray_playoff) so non-regular rows stay out
of every fit, mirroring the harness's phase rule. Two adapter
changes, both inert for existing leagues: the cards arm whitelist
now accepts `x5` (the shipped mean is 0.5·model + 0.5·naive
trailing-10, scored with the model's r, exactly as the frozen
harness), and `_cards_history_rows` honours the `exclude_phases`
opt-in (absent the key, every row loads as before). The league
builder now derives the payload root from its INDEX at call time so
the runner's INDEX override governs rebuilds. X5 uses no referee
data (referee identity is absent in this league), so there is no
referee operational gate. Join preparation only — NOT merged; the
coordinator's join proof (two full runner runs + byte-compare) runs
before any merge, per the established pattern.
CO-PrimeraA cards has joined provisionally (Lane 1, proof run 3; coordinator gate passed 2/10 on 2026-11-12 16:58 WIB): cards arm x8 joins the existing SOT/corners/total-shots markets under L1-K-CO. The named gate fixtures were Deportivo Pasto–Junior FC (1000014235, Diego Alejandro Ruíz Casas) and Llaneros FC–Chicó FC (1000014232, Carlos Márquez). The frozen verdict remains PROVISIONAL: X8 dev LL@5.5 0.6918 versus base 0.6956 and naive 0.7080; sealed 2026 Apertura n=204, LL 0.665796, calibration −1.574pp with SE 3.413pp, sign 5/5. Configuration remains primary 5.5, ladder 3.5/4.5/5.5/6.5, halves 0.3543, event-unified yellows, and pre-2023 season exclusions. Proof run 3 completed two end-to-end runs on 62 leagues / 123 markets: 13,521 then 13,520 predictions, 0 errors, CO 10 upcoming / 40 predictions per run, and run 2 fetched_new=0 everywhere. The 397-file comparison had 394 byte-identical files; the two live-feed differences are documented in the K-CO proof report. Independent recompute matched all 40 CO rows with max float diff 0.0; cards history loaded 1,336 frozen dev-era rows; AR x8 and AU gate_zero inertness probes were 8/8 byte-identical; synthetic match 5121316 settled 1 then 0 and artifacts were restored byte-identically. Status: PROVISIONAL joined (merge c6ecf8fc).
