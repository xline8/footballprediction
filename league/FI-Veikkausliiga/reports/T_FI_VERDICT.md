# Verdict — T-FI (FI-Veikkausliiga total shots): **NOT BUILT (feasibility)**

Frozen decision: PREREG_T_FI.md (1889033, before any fitting).

No model was fitted, no dev gate was run, and the virgin was not read for
total shots. Reason, in one paragraph: the `total_shots` target changes
definition between the warehouse's thin stats era (2021–2024: 19.377 /
16.898 / 15.940 / 15.162 per match) and its rich era (2025–2026: 26.395 /
26.305), while SOT stays flat across the break (8.198–9.463) — the two
eras do not measure the same quantity. The rich-era quantity exists in
exactly one dev season (2025), which cannot support the programme's
season-blocked walk-forward dev protocol, and pooling thin-era rows
would gate an arm on a different target than the one it would ship
against. This is a feasibility verdict recorded pre-fitting, not a gate
FAIL. T-FI may be pre-registered fresh once a second rich-era dev season
exists; it may not be rescued inside this prereg.
