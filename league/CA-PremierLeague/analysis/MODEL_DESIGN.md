# Phase A model design — CA-PremierLeague

No model is fitted in Phase A. The planned windows are seed 2021, dev 2022–2024, and virgin 2025 for G/S/C/T. Cards use the era-restricted warm-up 2023, dev 2024 and virgin 2025. 2026 is reserved confirmatory inventory and remains in progress.

## Candidates

- **G-CA:** Dixon–Coles goals-only, Gate Zero plus SHRINK. For teams with fewer than six prior in-league matches, shrink attack and defence by `n/6`. X2 is not registered because there is no tier corpus.
- **S-CA:** SOT reference architecture, Gate Zero plus RS with the sanctioned Beta-Binomial prior range 200→20,000. Primary line 7.5 (dev over-rate 0.546875).
- **C-CA:** corners reference architecture, Gate Zero only with full X9 possession + big-chance form. Primary line 9.5 (0.486607).
- **K-CA:** stats-yellows target, Gate Zero only. Cards are warm-up 2023/dev 2024/virgin 2025; event yellows are audit-only because pre-2025 event Yellow is absent. Primary line 4.5 (0.549107).
- **T-CA:** total-shots architecture with Arms A/B/C ported from J1/AR; primary line 22.5 (0.506696). The target is available throughout the corpus, unlike xG/shotmap features.

G-CA primary OU2.5 has dev over-rate 0.495536. Models must use only pre-match trailing observations and must not read 2026 for design decisions.

## Halves

Frozen 2023–2024 constants are goals 0.426343, SOT 0.435196, corners 0.466319, total shots 0.447807 and yellows 0.314532. True SDs from observed-minus-binomial/Poisson noise are 0.056009, 0, 0.018009, 0 and 0.040705. These constants are presentation components, not fit features.
