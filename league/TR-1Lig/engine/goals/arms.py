"""G-TR arm adjustments layered over a fitted DC model."""
import math
from collections import defaultdict


def x3_multipliers(games, cutoff):
    stats = defaultdict(lambda: [0.0] * 5)
    league = [0.0] * 5
    league_weight = 0.0
    for g in games:
        vals = (g.get("oph"), g.get("opa"), g.get("sph"), g.get("spa"))
        if any(v is None for v in vals):
            continue
        w = 0.5 ** ((cutoff - g["date"]).days / 270.0)
        league_weight += 2.0 * w
        for team, values in ((g["hi"], (vals[0], vals[1], vals[2], vals[3])),
                             (g["ai"], (vals[1], vals[0], vals[3], vals[2]))):
            s = stats[team]; s[0] += 1; s[1] += w * values[0]; s[2] += w * values[1]; s[3] += w * values[2]; s[4] += w * values[3]
            for i, v in enumerate(values): league[i] += w * v
    n = sum(v[0] for v in stats.values())
    if n == 0:
        return {}
    lop = league[0] / league_weight
    lsp = league[2] / league_weight
    result = {}
    for team, (count, opf, opa, spf, spa) in stats.items():
        if count < 8 or lop <= 0 or lsp <= 0:
            result[team] = {"att": 1.0, "def": 1.0}
            continue
        denom = sum(0.5 ** ((cutoff - g["date"]).days / 270.0) for g in games
                    if (g["hi"] == team or g["ai"] == team) and all(g.get(k) is not None for k in ("oph", "opa", "sph", "spa")))
        att = math.sqrt((opf / denom / lop) * (spf / denom / lsp))
        deff = math.sqrt((opa / denom / lop) * (spa / denom / lsp))
        result[team] = {"att": min(2.0, max(0.5, att)), "def": min(2.0, max(0.5, deff))}
    return result


def _eligible(rows):
    return [r for r in rows if r.get("phase") == "regular" and not r.get("awarded", 0)]


def mover_offsets(season, one_lig_rows, super_rows):
    """Return the frozen X2 mover set, offsets, and transition diagnostics."""
    one = _eligible(one_lig_rows)
    sup = _eligible(super_rows)
    prior = season.split("/")[0]
    previous = f"{int(prior) - 1:04d}/{int(prior):04d}"

    def teams(rows, s):
        return {r[k] for r in rows if r["season"] == s for k in ("hi", "ai")}

    # The season immediately before S is the season whose clubs enter S.
    sl_prev = teams(sup, previous)
    lig_prev = teams(one, previous)
    movers = (sl_prev - lig_prev) & teams(one, season)

    transitions = []
    # T+1 must be strictly before S; only completed old seasons are available.
    seasons = sorted({r["season"] for r in sup} | {r["season"] for r in one})
    for dest in seasons:
        try:
            y = int(dest.split("/")[0])
        except ValueError:
            continue
        if y >= int(prior):
            continue
        origin = f"{y-1:04d}/{y:04d}"
        sl_origin = teams(sup, origin)
        lig_dest = teams(one, dest)
        for team in sorted(sl_origin & lig_dest):
            so = [r for r in sup if r["season"] == origin and team in (r["hi"], r["ai"])]
            ld = [r for r in one if r["season"] == dest and team in (r["hi"], r["ai"])]
            if not so or not ld:
                continue
            def av(rows, side):
                vals = []
                for r in rows:
                    home = r["hi"] == team
                    vals.append(r[side[0] if home else side[1]])
                return sum(vals) / len(vals)
            gf = av(so, ("yh", "ya")); ga = av(so, ("ya", "yh"))
            dgf = av(ld, ("yh", "ya")) - gf
            dga = av(ld, ("ya", "yh")) - ga
            transitions.append({"team_id": team, "origin": origin, "destination": dest,
                                "dGF": dgf, "dGA": dga})
    if not transitions:
        return movers, {"dGF": 0.0, "dGA": 0.0}, []
    return movers, {"dGF": sum(x["dGF"] for x in transitions) / len(transitions),
                    "dGA": sum(x["dGA"] for x in transitions) / len(transitions)}, transitions


def adjusted_lambdas(model, home, away, arm, movers, multipliers, offsets=None):
    ah, da = model.a[home], model.d[away]
    aa, dh = model.a[away], model.d[home]
    if arm in ("shrink", "x3"):
        counts = getattr(model, "team_counts", {})
        for team, attr in ((home, "a"), (away, "a"), (home, "d"), (away, "d")):
            n = min(6, counts.get(team, 0)) / 6.0
            if attr == "a":
                if team == home: ah *= n
                else: aa *= n
            else:
                if team == home: dh *= n
                else: da *= n
    lh, la = math.exp(ah + da + model.h), math.exp(aa + dh)
    if arm == "x3":
        mh, ma = multipliers.get(home, {"att": 1, "def": 1}), multipliers.get(away, {"att": 1, "def": 1})
        lh *= math.sqrt(mh["att"] * ma["def"])
        la *= math.sqrt(ma["att"] * mh["def"])
    if arm == "x2" and offsets:
        dgf, dga = offsets["dGF"], offsets["dGA"]
        for team, is_home in ((home, True), (away, False)):
            if team not in movers:
                continue
            attack = math.log(max(model.mu + dgf, 0.10) / model.mu)
            defence = math.log(max(model.mu + dga, 0.10) / model.mu)
            if is_home:
                lh *= math.exp(attack)
                la *= math.exp(defence)
            else:
                la *= math.exp(attack)
                lh *= math.exp(defence)
    return lh, la
