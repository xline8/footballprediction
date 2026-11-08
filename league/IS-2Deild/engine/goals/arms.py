"""Pre-registered G-IS2 rating adjustments."""
import math
from collections import defaultdict


def match_counts(games):
    counts = defaultdict(int)
    for g in games:
        counts[g["hi"]] += 1
        counts[g["ai"]] += 1
    return counts


def x2_shifts(transitions, csv_rows, mu, target_season):
    """Return source -> log attack/defence shifts from prior transitions only."""
    by_season = defaultdict(lambda: [0, 0])
    for row in csv_rows:
        by_season[row["season"]][0] += row["yh"] + row["ya"]
        by_season[row["season"]][1] += 1
    prior = defaultdict(list)
    for t in transitions:
        season = str(t["season"])
        if season < str(target_season) and t["source"] in ("relegated-from-1Deild", "from-below"):
            total, matches = by_season.get(season, (0, 0))
            if matches:
                mean = total / (2.0 * matches)
                prior[t["source"]].append((t["arrival_gf"] - mean, t["arrival_ga"] - mean))
    shifts = {}
    for source, values in prior.items():
        if len(values) < 3:
            continue
        dgf = sum(v[0] for v in values) / len(values)
        dga = sum(v[1] for v in values) / len(values)
        shifts[source] = {
            "att": math.log(max(mu + dgf, 0.10) / mu),
            "def": math.log(max(mu + dga, 0.10) / mu),
            "n_prior": len(values),
            "dGF": dgf,
            "dGA": dga,
        }
    return shifts


def adjusted_lambdas(model, home, away, arm, multipliers, counts):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm in ("shrink", "x2"):
        ah *= min(1.0, counts.get(home, 0) / 6.0)
        da *= min(1.0, counts.get(away, 0) / 6.0)
        aa *= min(1.0, counts.get(away, 0) / 6.0)
        dh *= min(1.0, counts.get(home, 0) / 6.0)
    if arm == "x2":
        mh, ma = multipliers.get(home), multipliers.get(away)
        if mh:
            ah += mh["att"]; dh += mh["def"]
        if ma:
            aa += ma["att"]; da += ma["def"]
    return math.exp(ah + da + model.h), math.exp(aa + dh)
