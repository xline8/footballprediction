# TR-1Lig EDA

All fitting evidence uses regular, non-awarded DEV rows only. `eda_numbers.json`
is the measured companion output; 2025/26 and 2026/27 appear only as labelled
virgin/reserved coverage and level descriptives.

## Levels and coverage

Goals are available in every season. SOT, corners, total shots, cards, xG,
touches, and big chances are stats-era quantities: two 2023/24 rows, a
2024/25 fragment, complete 2025/26 virgin coverage, and partial 2026/27. They
are not development evidence for count candidates. Per-season levels,
coverage, event levels, and analysis-scope sample sizes are in the JSON.

The DEV home/away goal levels and outcome rates are also recorded there. Home
advantage is descriptive only until the pre-registered goals model is fit.

## Reliable traits

Career-pooled team-ID split-half reliabilities use DEV seasons only, 60 random
splits, and a 20 team-match minimum. Goals-for and goals-against are the
relevant stable traits for G-TR1; stats-era traits are reported descriptively
but do not unlock count models. The exact coefficients and eligible-team
counts are in `reliability_dev`.

## Halves

The DEV HT source gives a frozen goals 1H share of 0.4482. The observed
per-match share variance is 0.11916 versus a binomial noise floor of 0.12058,
an excess of −0.00142: there is no measurable team timing effect. Count
markets therefore have no halves constants and remain FT-only.

## X2 mover measurement

Compared with the real SüperLig match corpus, 26 same-ID adjacent-season
transitions are measurable: 14 SüperLig→1.Lig and 12 1.Lig→SüperLig. Mean GF
and GA shifts are respectively +0.156/−0.199 for the downward move and
−0.562/+0.596 for the upward move. These are descriptive magnitudes for the
X2 arm, not fitted offsets.

## X3/X4 boundary

Shotmap exists only in the 2024/25 fragment and is absent in virgin 2025/26;
there is no valid dev+virgin shotmap arm. X3, X4, xGOT, and other shotmap-bound
features are therefore dropped.
