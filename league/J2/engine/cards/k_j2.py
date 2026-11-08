#!/usr/bin/env python3
"""Pre-registered J2 yellow-card walk-forward model (Gate Zero and X8)."""

import csv
import json
import math
import os
import sys
from collections import defaultdict, deque
from datetime import date

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
DATA = os.path.join(ROOT, "league/J2/data/j2_matches.csv")
WAREHOUSE = os.path.join(ROOT, "data_enrichment/fotmob_jleague/J2")
OUT = os.path.dirname(__file__)
PRED = os.path.join(ROOT, "league/J2/predictions/k_j2_virgin_predictions.csv")
DEV_SEASONS = ("2021", "2022", "2023", "2024")
VIRGIN_SEASON = "2025"
EXCLUDED = "2026-2027"
HL = 270.0
K_PRIOR = 8.0
K_REF = 8.0
MIN_REF = 8
FB_MU_H, FB_MU_A = 2.15, 1.95


def parse_date(v):
    return date.fromisoformat(str(v)[:10])


class Decayed:
    def __init__(self):
        self.s = self.w = 0.0
        self.last = None

    def move(self, day):
        if self.last is not None and day > self.last:
            f = 0.5 ** ((day - self.last).days / HL)
            self.s *= f
            self.w *= f
        self.last = day

    def value(self, day):
        self.move(day)
        return self.s, self.w

    def add(self, day, x):
        self.move(day)
        self.s += x
        self.w += 1.0


class TeamState:
    def __init__(self):
        self.att_h, self.def_h = Decayed(), Decayed()
        self.att_a, self.def_a = Decayed(), Decayed()


class LeagueState:
    def __init__(self):
        self.mu_h, self.mu_a = Decayed(), Decayed()


def _shrunk(stat, day, mu):
    s, w = stat.value(day)
    return (s + K_PRIOR * mu) / (w + K_PRIOR)


class CardsState:
    def __init__(self):
        self.teams = defaultdict(TeamState)
        self.league = LeagueState()

    def means(self, day):
        sh, wh = self.league.mu_h.value(day)
        sa, wa = self.league.mu_a.value(day)
        return sh / wh if wh and sh > 0 else FB_MU_H, sa / wa if wa and sa > 0 else FB_MU_A

    def predict(self, home, away, day):
        mh, ma = self.means(day)
        th, ta = self.teams[home], self.teams[away]
        eh = mh * (_shrunk(th.att_h, day, mh) / mh) * (_shrunk(ta.def_a, day, mh) / mh)
        ea = ma * (_shrunk(ta.att_a, day, ma) / ma) * (_shrunk(th.def_h, day, ma) / ma)
        return eh, ea, mh, ma

    def update(self, home, away, day, yh, ya):
        th, ta = self.teams[home], self.teams[away]
        th.att_h.add(day, yh); th.def_h.add(day, ya)
        ta.att_a.add(day, ya); ta.def_a.add(day, yh)
        self.league.mu_h.add(day, yh); self.league.mu_a.add(day, ya)


def nb_over(mu, r, line):
    kmax = int(math.floor(line))
    q = mu / (r + mu)
    term = (r / (r + mu)) ** r
    cdf = term
    for k in range(1, kmax + 1):
        term *= (k - 1 + r) / k * q
        cdf += term
    return min(1.0, max(0.0, 1.0 - cdf))


def pois_over(mu, line):
    term = math.exp(-mu)
    cdf = term
    for k in range(1, int(math.floor(line)) + 1):
        term *= mu / k
        cdf += term
    return 1.0 - cdf


def load_rows(seasons=None):
    rows = []
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if r["season"] == EXCLUDED or (seasons and r["season"] not in seasons):
                continue
            try:
                rows.append({
                    "match_id": r["match_id"], "season": r["season"], "date": parse_date(r["date"]),
                    "home_team_id": int(r["home_team_id"]), "home_team": r["home_team"],
                    "away_team_id": int(r["away_team_id"]), "away_team": r["away_team"],
                    "yh": int(r["yellow_home"]), "ya": int(r["yellow_away"]),
                })
            except (KeyError, TypeError, ValueError):
                continue
    return sorted(rows, key=lambda x: (x["date"], x["match_id"]))


def extract_referees():
    # The referee table covers every match in the CSV (all seasons,
    # including the fitting-excluded 2026-2027) -- read it directly so
    # the EXCLUDED filter in load_rows cannot silently shrink it.
    fixtures = {}
    with open(DATA, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            fixtures[r["match_id"]] = {
                "match_id": r["match_id"], "season": r["season"],
                "date": parse_date(r["date"]), "home_team": r["home_team"],
                "away_team": r["away_team"]}
    refs = {}
    for season in os.listdir(WAREHOUSE):
        d = os.path.join(WAREHOUSE, season)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.endswith(".json"):
                continue
            mid = os.path.splitext(name)[0]
            try:
                with open(os.path.join(d, name), encoding="utf-8") as f:
                    obj = json.load(f)
                ref = obj.get("content", {}).get("matchFacts", {}).get("infoBox", {}).get("Referee", {})
                refs[mid] = str(ref.get("text", "") or "").strip() if isinstance(ref, dict) else ""
            except (OSError, ValueError, TypeError):
                refs[mid] = ""
    fields = ["match_id", "season", "date", "home_team", "away_team", "referee", "referee_present"]
    path = os.path.join(OUT, "referee_table.csv")
    coverage = defaultdict(lambda: [0, 0])
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for mid, r in sorted(fixtures.items(), key=lambda kv: (kv[1]["date"], kv[0])):
            ref = refs.get(mid, "")
            coverage[r["season"]][0] += 1
            coverage[r["season"]][1] += bool(ref)
            w.writerow({"match_id": mid, "season": r["season"], "date": r["date"].isoformat(),
                        "home_team": r["home_team"], "away_team": r["away_team"],
                        "referee": ref, "referee_present": int(bool(ref))})
    return {s: {"present": p, "total": n, "rate": p / n if n else 0.0}
            for s, (n, p) in sorted(coverage.items())}, refs


def ref_history_update(hist, ref, y):
    if ref:
        hist[ref].append(y)


def walk(rows, refs, score_seasons, nb_r=None, virgin=False):
    state, ref_hist = CardsState(), defaultdict(list)
    # Coordinator verification fix (2026-11-09): the naive baseline is
    # trailing-10 by prereg SS6 -- the deque must be capped at 10.
    team_hist, league_hist = defaultdict(lambda: deque(maxlen=10)), []
    groups = defaultdict(list)
    for r in rows:
        groups[r["date"]].append(r)
    output = []
    for day in sorted(groups):
        day_rows = groups[day]
        for r in day_rows:
            eh, ea, mh, ma = state.predict(r["home_team_id"], r["away_team_id"], day)
            mu = eh + ea
            ref = refs.get(r["match_id"], "")
            prior = ref_hist.get(ref, []) if ref else []
            fallback = len(prior) < MIN_REF
            factor = 1.0
            if not fallback:
                league_mu = mh + ma
                rate = (sum(prior) + K_REF * league_mu) / (len(prior) + K_REF)
                factor = min(1.40, max(0.70, rate / league_mu))
            xmu = mu * factor
            base25 = sum(y > 2 for y in league_hist) / len(league_hist) if league_hist else 0.5
            base35 = sum(y > 3 for y in league_hist) / len(league_hist) if league_hist else 0.5
            home_vals = list(team_hist[r["home_team_id"]])
            away_vals = list(team_hist[r["away_team_id"]])
            hm = sum(home_vals) / len(home_vals) if home_vals else (sum(league_hist) / len(league_hist) if league_hist else FB_MU_H + FB_MU_A)
            am = sum(away_vals) / len(away_vals) if away_vals else (sum(league_hist) / len(league_hist) if league_hist else FB_MU_H + FB_MU_A)
            nmu = (hm + am) / 2.0
            pred = dict(r, exp_gz=mu, exp_x8=xmu, ref=ref, fallback=int(fallback),
                        p_gz25=None, p_gz35=None, p_x825=None, p_x835=None,
                        p_base25=base25, p_base35=base35,
                        p_naive25=pois_over(nmu, 2.5), p_naive35=pois_over(nmu, 3.5))
            if nb_r is not None:
                pred.update(p_gz25=nb_over(mu, nb_r, 2.5), p_gz35=nb_over(mu, nb_r, 3.5),
                            p_x825=nb_over(xmu, nb_r, 2.5), p_x835=nb_over(xmu, nb_r, 3.5))
            if r["season"] in score_seasons:
                output.append(pred)
        for r in day_rows:
            y = r["yh"] + r["ya"]
            state.update(r["home_team_id"], r["away_team_id"], day, r["yh"], r["ya"])
            ref_history_update(ref_hist, refs.get(r["match_id"], ""), y)
            team_hist[r["home_team_id"]].append(y); team_hist[r["away_team_id"]].append(y)
            league_hist.append(y)
    return output, state


def ll(rows, field, threshold):
    if not rows: return None
    total = 0.0
    for r in rows:
        p = min(1 - 1e-9, max(1e-9, r[field]))
        total -= math.log(p if r["yh"] + r["ya"] > threshold else 1 - p)
    return total / len(rows)


def metrics(rows):
    return {"n": len(rows), "ll_2.5": ll(rows, "p", 2), "ll_3.5": ll(rows, "p", 3)}


def method_r(rows):
    num = sum(((r["yh"] + r["ya"] - r["exp_gz"]) ** 2 - r["exp_gz"]) for r in rows)
    den = sum(r["exp_gz"] ** 2 for r in rows)
    return 500.0 if num <= 0 else min(500.0, max(5.0, den / num))


def attach(rows, field, source):
    return [dict(r, p=r[source]) for r in rows]


def gate_result(dev):
    b = dev["baselines"]["league_base_rate"]["pooled"]["ll_2.5"]
    n = dev["baselines"]["naive_trailing10"]["pooled"]["ll_2.5"]
    return {arm: dev["arms"][arm]["pooled"]["ll_2.5"] < b and dev["arms"][arm]["pooled"]["ll_2.5"] < n
            for arm in ("gate_zero", "x8")}


def run():
    coverage, refs = extract_referees()
    dev_rows = load_rows(DEV_SEASONS)
    raw, _ = walk(dev_rows, refs, DEV_SEASONS, nb_r=None)
    scored_raw = [r for r in raw if not (r["season"] == "2021" and r["date"].month == 2)]
    r_nb = method_r(scored_raw)
    scored, final_state = walk(dev_rows, refs, DEV_SEASONS, nb_r=r_nb)
    scored = [r for r in scored if not (r["season"] == "2021" and r["date"].month == 2)]
    arms = {}
    for name, fields in (("gate_zero", ("p_gz25", "p_gz35")), ("x8", ("p_x825", "p_x835"))):
        rows3 = [dict(r, p=r[fields[0]], p3=r[fields[1]]) for r in scored]
        arms[name] = {"pooled": {"n": len(rows3), "ll_2.5": ll(rows3, "p", 2), "ll_3.5": ll(rows3, "p3", 3)},
                      "per_season": {s: {"n": sum(r["season"] == s for r in rows3),
                                         "ll_2.5": ll([x for x in rows3 if x["season"] == s], "p", 2),
                                         "ll_3.5": ll([x for x in rows3 if x["season"] == s], "p3", 3)} for s in DEV_SEASONS}}
        arms[name]["fallback_count"] = sum(r["fallback"] for r in scored) if name == "x8" else 0
    baselines = {}
    for name, source in (("league_base_rate", "p_base25"), ("naive_trailing10", "p_naive25")):
        allr = [dict(r, p=r[source], p3=r["p_base35"] if name == "league_base_rate" else r["p_naive35"]) for r in scored]
        baselines[name] = {"pooled": {"n": len(allr), "ll_2.5": ll(allr, "p", 2), "ll_3.5": ll(allr, "p3", 3)},
                           "per_season": {s: {"n": sum(r["season"] == s for r in allr),
                                              "ll_2.5": ll([x for x in allr if x["season"] == s], "p", 2),
                                              "ll_3.5": ll([x for x in allr if x["season"] == s], "p3", 3)} for s in DEV_SEASONS}}
    dev = {"dev_seasons": list(DEV_SEASONS), "scored_n": len(scored), "warmup_excluded": "2021-02",
           "referee_coverage": coverage, "arms": arms, "baselines": baselines, "nb_r": r_nb}
    gate = gate_result(dev); dev["gate"] = gate
    virgin_status = "not read — no arm passed dev gate"
    virgin_rows = []
    if any(gate.values()):
        all_rows = load_rows(tuple(DEV_SEASONS) + (VIRGIN_SEASON,))
        virgin_rows, _ = walk(all_rows, refs, (VIRGIN_SEASON,), nb_r=r_nb, virgin=True)
        virgin_status = "read"
        vstats = {}
        for arm, pfield in (("gate_zero", "p_gz25"), ("x8", "p_x825")):
            rr = [dict(r, p=r[pfield]) for r in virgin_rows]
            actual = sum(r["yh"] + r["ya"] > 2 for r in rr) / len(rr)
            meanp = sum(r["p"] for r in rr) / len(rr)
            var = sum((r["p"] - meanp) ** 2 for r in rr) / len(rr)
            se = math.sqrt(var / len(rr) + actual * (1 - actual) / len(rr))
            vstats[arm] = {"n": len(rr), "ll_2.5": ll(rr, "p", 2), "mean_p_over_2.5": meanp,
                           "actual_over_rate": actual, "calibration_delta": meanp - actual, "se": se,
                           "fallback_count": sum(r["fallback"] for r in rr) if arm == "x8" else 0}
        dev["virgin"] = vstats
        dev["virgin_outcome"] = virgin_status
        write_virgin(virgin_rows, refs)
    else:
        dev["virgin"] = virgin_status
    with open(os.path.join(OUT, "dev_results.json"), "w", encoding="utf-8") as f:
        json.dump(dev, f, indent=2, sort_keys=True)
    mh, ma = final_state.means(date(2024, 12, 31))
    with open(os.path.join(OUT, "fitted_params.json"), "w", encoding="utf-8") as f:
        json.dump({"HL": HL, "K_PRIOR": K_PRIOR, "K_REF": K_REF, "min_ref_history": MIN_REF,
                   "NB_r": r_nb, "final_league_mu_h": mh, "final_league_mu_a": ma,
                   "training_n": len(dev_rows)}, f, indent=2, sort_keys=True)
    write_verdict(dev, gate, coverage, virgin_status)
    print(json.dumps({"referee_coverage": coverage, "dev": dev, "virgin": virgin_status}, indent=2, sort_keys=True))


def write_virgin(rows, refs):
    fields = ["match_id", "date", "season", "home_team_id", "home_team", "away_team_id", "away_team",
              "exp_cards_gz", "p_over_2_5_gz", "p_over_3_5_gz", "exp_cards_x8", "p_over_2_5_x8",
              "p_over_3_5_x8", "referee", "x8_fallback", "actual_yellows"]
    with open(PRED, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for r in rows:
            w.writerow({"match_id": r["match_id"], "date": r["date"].isoformat(), "season": r["season"],
                        "home_team_id": r["home_team_id"], "home_team": r["home_team"],
                        "away_team_id": r["away_team_id"], "away_team": r["away_team"],
                        "exp_cards_gz": r["exp_gz"], "p_over_2_5_gz": r["p_gz25"], "p_over_3_5_gz": r["p_gz35"],
                        "exp_cards_x8": r["exp_x8"], "p_over_2_5_x8": r["p_x825"], "p_over_3_5_x8": r["p_x835"],
                        "referee": r["ref"], "x8_fallback": r["fallback"], "actual_yellows": r["yh"] + r["ya"]})


def write_verdict(dev, gate, coverage, virgin):
    path = os.path.join(ROOT, "league/J2/reports/K_J2_VERDICT.md")
    with open(path, "w", encoding="utf-8") as f:
        f.write("# K-J2 verdict\n\n")
        f.write("## Operational check\n\n")
        f.write("Referees were read only from `content.matchFacts.infoBox.Referee.text`; no external source was checked and no appointments are claimed pre-kickoff. Unknown referees fall back to Gate Zero; none are imputed.\n\n")
        f.write("Coverage by season: " + ", ".join(f"{s} {v['present']}/{v['total']} ({v['rate']:.1%})" for s, v in coverage.items()) + ".\n\n")
        f.write("## Gate\n\n")
        f.write("Gate Zero: **%s**; X8: **%s**. Virgin: **%s**.\n" % ("PASS" if gate["gate_zero"] else "FAIL", "PASS" if gate["x8"] else "FAIL", virgin))
        f.write("\nThe dev gate requires pooled LL@2.5 to beat both baselines; no virgin outcomes are read when both arms fail.\n")


if __name__ == "__main__":
    run()
