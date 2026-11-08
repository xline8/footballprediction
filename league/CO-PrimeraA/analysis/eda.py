"""EDA computations for CO-PrimeraA (Step 3). Reads the built CSV only.
Prints every number quoted in EDA.md / FEATURES.md / MODEL_DESIGN.md and
writes eda_summary.json beside this file. Dev era for design purposes:
seed 2021-Ap+Cl; dev eval 2022-Ap..2025-Cl; virgin 2026-Ap (complete);
2026-Cl is in progress and excluded from every fit/gate/constant below
(it appears in coverage tables only, marked)."""
import csv, json, math, random
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "data" / "co_primeraa_matches.csv"
rows = list(csv.DictReader(open(CSV, encoding="utf-8")))
for r in rows:
    for k in ("home_goals", "away_goals"):
        r[k] = int(r[k])

SEASONS = ["2021 - Apertura", "2021 - Clausura", "2022 - Apertura", "2022 - Clausura",
           "2023 - Apertura", "2023 - Clausura", "2024 - Apertura", "2024 - Clausura",
           "2025 - Apertura", "2025 - Clausura", "2026 - Apertura", "2026 - Clausura"]
DEV_EVAL = SEASONS[2:10]          # 2022-Ap .. 2025-Cl
VIRGIN = "2026 - Apertura"
EXCLUDED = "2026 - Clausura"
USABLE = [r for r in rows if r["season"] != EXCLUDED]

def fnum(r, k):
    v = r.get(k)
    return None if v in (None, "") else float(v)

def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None

def pearson(xs, ys):
    n = len(xs)
    if n < 3: return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs); syy = sum((y - my) ** 2 for y in ys)
    return sxy / math.sqrt(sxx * syy) if sxx > 0 and syy > 0 else None

out = {}

# ---------- coverage + phases + teams per season ----------
cov = {}
for s in SEASONS:
    sub = [r for r in rows if r["season"] == s]
    n = len(sub)
    cov[s] = {
        "n": n,
        "has_stats": sum(int(r["has_stats"]) for r in sub) / n,
        "period_splits": sum(int(r["has_period_splits"]) for r in sub) / n,
        "has_xg": sum(int(r["has_xg"]) for r in sub) / n,
        "shotmap": sum(1 for r in sub if int(r["n_shotmap"]) > 0) / n,
        "referee": sum(1 for r in sub if r["referee"]) / n,
        "events_exact": sum(int(r["events_exact"]) for r in sub) / n,
        "phases": dict(Counter(r["phase"] for r in sub)),
        "teams": len(set([r["home_team_id"] for r in sub] + [r["away_team_id"] for r in sub])),
        "date_min": min(r["date"] for r in sub), "date_max": max(r["date"] for r in sub),
        "touches_cov": sum(1 for r in sub if fnum(r, "touches_opp_box_home") is not None) / n,
    }
out["coverage"] = cov
for s in SEASONS:
    c = cov[s]
    print(f"COV {s}: n={c['n']} teams={c['teams']} stats={c['has_stats']:.3f} splits={c['period_splits']:.3f} "
          f"xg={c['has_xg']:.3f} shotmap={c['shotmap']:.3f} ref={c['referee']:.3f} evExact={c['events_exact']:.3f} "
          f"touches={c['touches_cov']:.3f} phases={c['phases']} dates={c['date_min']}..{c['date_max']}")

# ---------- levels per season ----------
levels = {}
for s in SEASONS:
    sub = [r for r in rows if r["season"] == s]
    n = len(sub)
    g = [r["home_goals"] + r["away_goals"] for r in sub]
    lv = {
        "n": n, "gpm": mean(g), "home_g": mean([r["home_goals"] for r in sub]),
        "away_g": mean([r["away_goals"] for r in sub]),
        "hw": sum(1 for r in sub if r["home_goals"] > r["away_goals"]) / n,
        "draw": sum(1 for r in sub if r["home_goals"] == r["away_goals"]) / n,
        "ou25": sum(1 for x in g if x > 2.5) / n,
        "btts": sum(1 for r in sub if r["home_goals"] > 0 and r["away_goals"] > 0) / n,
        "sot": mean([ (fnum(r, "shotsontarget_home") or 0) + (fnum(r, "shotsontarget_away") or 0)
                      if fnum(r, "shotsontarget_home") is not None else None for r in sub]),
        "corners": mean([ (fnum(r, "corners_home") or 0) + (fnum(r, "corners_away") or 0)
                          if fnum(r, "corners_home") is not None else None for r in sub]),
        "shots": mean([ (fnum(r, "total_shots_home") or 0) + (fnum(r, "total_shots_away") or 0)
                        if fnum(r, "total_shots_home") is not None else None for r in sub]),
        "cards_stats": mean([ (fnum(r, "yellow_cards_home") or 0) + (fnum(r, "yellow_cards_away") or 0)
                              if fnum(r, "yellow_cards_home") is not None else None for r in sub]),
        "cards_ev": mean([int(r["ev_yellow_inc2nd_home"]) + int(r["ev_yellow_inc2nd_away"]) for r in sub]),
        "xg": mean([ (fnum(r, "expected_goals_home") or 0) + (fnum(r, "expected_goals_away") or 0)
                     if fnum(r, "expected_goals_home") is not None else None for r in sub]),
    }
    levels[s] = lv
    print(f"LVL {s}: gpm={lv['gpm']:.3f} H{lv['home_g']:.3f}/A{lv['away_g']:.3f} HW={lv['hw']:.3f} D={lv['draw']:.3f} "
          f"OU={lv['ou25']:.3f} BTTS={lv['btts']:.3f} SOT={lv['sot']:.2f} COR={lv['corners']:.2f} SH={lv['shots']:.2f} "
          f"YCstat={lv['cards_stats']:.2f} YCev={lv['cards_ev']:.2f} xG={lv['xg']}")
out["levels"] = levels

dev = [r for r in USABLE if r["season"] in DEV_EVAL]
print(f"DEV pooled n={len(dev)} gpm={mean([r['home_goals']+r['away_goals'] for r in dev]):.3f} "
      f"OU25={sum(1 for r in dev if r['home_goals']+r['away_goals']>2.5)/len(dev):.3f}")
for name, kh, ka in (("SOT", "shotsontarget_home", "shotsontarget_away"), ("corners", "corners_home", "corners_away"),
                     ("shots", "total_shots_home", "total_shots_away"), ("cards_stats", "yellow_cards_home", "yellow_cards_away")):
    vals = [(fnum(r, kh) or 0) + (fnum(r, ka) or 0) for r in dev if fnum(r, kh) is not None]
    print(f"DEV mean {name} = {mean(vals):.3f} (n={len(vals)})")
print(f"DEV mean cards_ev = {mean([int(r['ev_yellow_inc2nd_home'])+int(r['ev_yellow_inc2nd_away']) for r in dev]):.3f}")

# ---------- cards feed check (dev era only) ----------
print("\nCARDS CHECK (dev eval tournaments):")
tot = {"stats": 0.0, "ev_y": 0.0, "ev_u": 0.0, "exact_y": 0, "exact_u": 0, "n": 0}
for s in DEV_EVAL:
    sub = [r for r in dev if r["season"] == s]
    ms = mean([(fnum(r, "yellow_cards_home") or 0) + (fnum(r, "yellow_cards_away") or 0) for r in sub])
    my = mean([int(r["ev_yellow_home"]) + int(r["ev_yellow_away"]) for r in sub])
    mu = mean([int(r["ev_yellow_inc2nd_home"]) + int(r["ev_yellow_inc2nd_away"]) for r in sub])
    ey = sum(1 for r in sub if int(r["ev_yellow_home"]) + int(r["ev_yellow_away"]) ==
             (fnum(r, "yellow_cards_home") or 0) + (fnum(r, "yellow_cards_away") or 0)) / len(sub)
    eu = sum(1 for r in sub if int(r["ev_yellow_inc2nd_home"]) + int(r["ev_yellow_inc2nd_away"]) ==
             (fnum(r, "yellow_cards_home") or 0) + (fnum(r, "yellow_cards_away") or 0)) / len(sub)
    print(f"  {s}: stats={ms:.3f} evYellow={my:.3f} evUnified={mu:.3f} exactY={ey:.3f} exactU={eu:.3f}")
    tot["stats"] += ms * len(sub); tot["ev_y"] += my * len(sub); tot["ev_u"] += mu * len(sub); tot["n"] += len(sub)
    tot["exact_y"] += ey * len(sub); tot["exact_u"] += eu * len(sub)
print(f"  POOLED: stats={tot['stats']/tot['n']:.3f} evYellow={tot['ev_y']/tot['n']:.3f} evUnified={tot['ev_u']/tot['n']:.3f} "
      f"exactY={tot['exact_y']/tot['n']:.3f} exactU={tot['exact_u']/tot['n']:.3f}")
out["cards_check"] = {k: (v / tot["n"] if k != "n" else v) for k, v in tot.items()}

# ---------- split-half trait reliability ----------
def team_rows(subset):
    """team-match rows from match rows: (team_id, gf, ga, sot_f, sot_a, cor_f, cor_a, sh_f, sh_a, yc_f(stats), ycu_f(ev), tch_f, bc_f, poss)"""
    out_tm = []
    for r in subset:
        for side, opp in (("home", "away"), ("away", "home")):
            out_tm.append({
                "team": r[f"{side}_team_id"],
                "gf": r[f"{side}_goals"], "ga": r[f"{opp}_goals"],
                "sot_f": fnum(r, f"shotsontarget_{side}"), "sot_a": fnum(r, f"shotsontarget_{opp}"),
                "cor_f": fnum(r, f"corners_{side}"), "cor_a": fnum(r, f"corners_{opp}"),
                "sh_f": fnum(r, f"total_shots_{side}"), "sh_a": fnum(r, f"total_shots_{opp}"),
                "yc_f": fnum(r, f"yellow_cards_{side}"), "yc_a": fnum(r, f"yellow_cards_{opp}"),
                "ycu_f": float(r[f"ev_yellow_inc2nd_{side}"]), "ycu_a": float(r[f"ev_yellow_inc2nd_{opp}"]),
                "tch_f": fnum(r, f"touches_opp_box_{side}"), "tch_a": fnum(r, f"touches_opp_box_{opp}"),
                "bc_f": fnum(r, f"big_chance_{side}"), "bc_a": fnum(r, f"big_chance_{opp}"),
                "poss": fnum(r, f"ballpossesion_{side}"),
                "xg_f": fnum(r, f"expected_goals_{side}"), "xg_a": fnum(r, f"expected_goals_{opp}"),
            })
    return out_tm

def split_half(tm, key, min_matches=20, seed=7):
    by = defaultdict(list)
    for i, t in enumerate(tm):
        if t[key] is not None:
            by[t["team"]].append(t[key])
    rng = random.Random(seed)
    xs, ys = [], []
    for team, vals in by.items():
        if len(vals) < min_matches: continue
        idx = list(range(len(vals))); rng.shuffle(idx)
        h = len(vals) // 2
        xs.append(mean([vals[i] for i in idx[:h]])); ys.append(mean([vals[i] for i in idx[h:]]))
    return pearson(xs, ys), len(xs)

tm_all = team_rows([r for r in USABLE])                     # 2021..2026-Ap
tm_dev = team_rows([r for r in USABLE if r["season"] in SEASONS[:10]])  # through 2025-Cl (fit era)
print("\nRELIABILITY split-half (career through 2025-Cl, teams >=20 matches):")
rel = {}
for key in ("gf", "ga", "sot_f", "sot_a", "cor_f", "cor_a", "sh_f", "sh_a", "yc_f", "yc_a", "ycu_f", "ycu_a", "tch_f", "tch_a", "bc_f", "poss"):
    r_, n_ = split_half(tm_dev, key)
    rel[key] = (r_, n_)
    print(f"  {key}: r={r_:.3f} (teams={n_})" if r_ is not None else f"  {key}: n/a")
# on-target rate trait
def sot_rate_rel(tm, min_matches=20, seed=7):
    by = defaultdict(lambda: [0.0, 0.0, 0])  # not used; do split by matches below
    per = defaultdict(list)
    for t in tm:
        if t["sot_f"] is not None and t["sh_f"]:
            per[t["team"]].append((t["sot_f"], t["sh_f"]))
    rng = random.Random(seed); xs, ys = [], []
    for team, vals in per.items():
        if len(vals) < min_matches: continue
        idx = list(range(len(vals))); rng.shuffle(idx); h = len(vals) // 2
        xs.append(sum(vals[i][0] for i in idx[:h]) / sum(vals[i][1] for i in idx[:h]))
        ys.append(sum(vals[i][0] for i in idx[h:]) / sum(vals[i][1] for i in idx[h:]))
    return pearson(xs, ys), len(xs)
r_, n_ = sot_rate_rel(tm_dev); print(f"  on-target rate (SOT/shots, for): r={r_:.3f} (teams={n_})"); rel["otr"] = (r_, n_)
# per-match corr touches vs corners
tc = [(t["tch_f"], t["cor_f"]) for t in tm_dev if t["tch_f"] is not None and t["cor_f"] is not None]
print(f"  per-match corr touches_for vs corners_for: r={pearson([a for a,_ in tc],[b for _,b in tc]):.3f} (n={len(tc)})")
pc = [(t["poss"], t["cor_f"]) for t in tm_dev if t["poss"] is not None and t["cor_f"] is not None]
print(f"  per-match corr possession vs corners_for: r={pearson([a for a,_ in pc],[b for _,b in pc]):.3f} (n={len(pc)})")
out["reliability"] = {k: v[0] for k, v in rel.items()}

# ---------- halves: shares + variance decomposition ----------
def half_share(subset, total_fn, first_fn, label):
    shares, tot_goals, first_goals, n = [], 0, 0, 0
    for r in subset:
        t, f = total_fn(r), first_fn(r)
        if t is None or f is None: continue
        n += 1; tot_goals += t; first_goals += f
        if t > 0: shares.append(f / t)
    pooled = first_goals / tot_goals if tot_goals else None
    if shares:
        m = mean(shares); obs_var = sum((x - m) ** 2 for x in shares) / len(shares)
        # noise var: E[p(1-p)/T] under binomial with p=pooled
        noise = mean([pooled * (1 - pooled) / t for r in subset
                      for t in [total_fn(r)] if t])
        print(f"HALVES {label}: pooled share={pooled:.4f} (n={n}, events={tot_goals}) obsVar={obs_var:.4f} noiseVar={noise:.4f} trueVar={obs_var - noise:.4f}")
        return pooled, obs_var, noise
    return pooled, None, None

fit_era = [r for r in USABLE if r["season"] in SEASONS[:10]]
half = {}
half["goals"] = half_share([r for r in fit_era if int(r["events_exact"])],
                           lambda r: r["home_goals"] + r["away_goals"],
                           lambda r: (int(r["ht_home_goals"]) + int(r["ht_away_goals"])) if r["ht_home_goals"] not in (None, "") else None,
                           "goals (events, fit era)")
split_era = [r for r in fit_era if int(r["has_period_splits"])]
print(f"split-era matches in fit era: {len(split_era)} ({[s for s in SEASONS[:10] if any(r['season']==s for r in split_era)]})")
for label, kh, ka in (("sot", "shotsontarget_home_1h", "shotsontarget_away_1h"),
                      ("corners", "corners_home_1h", "corners_away_1h"),
                      ("shots", "total_shots_home_1h", "total_shots_away_1h")):
    tot_k = {"sot": ("shotsontarget_home", "shotsontarget_away"), "corners": ("corners_home", "corners_away"),
             "shots": ("total_shots_home", "total_shots_away")}[label]
    half[label] = half_share(split_era,
                             lambda r, a=tot_k[0], b=tot_k[1]: (fnum(r, a) or 0) + (fnum(r, b) or 0) if fnum(r, a) is not None else None,
                             lambda r, a=kh, b=ka: (fnum(r, a) or 0) + (fnum(r, b) or 0) if fnum(r, a) is not None else None,
                             f"{label} (period splits, split era)")
half["cards"] = half_share(fit_era,
                           lambda r: int(r["ev_yellow_inc2nd_home"]) + int(r["ev_yellow_inc2nd_away"]),
                           lambda r: int(r["fh_ev_yellow_home"]) + int(r["fh_ev_yellow_away"]),
                           "cards (events unified, fit era)")
out["halves"] = {k: v[0] for k, v in half.items()}

# ---------- referee trait (dev/fit era) ----------
ref_matches = defaultdict(list)
for r in fit_era:
    if r["referee"]:
        ref_matches[r["referee"]].append(int(r["ev_yellow_inc2nd_home"]) + int(r["ev_yellow_inc2nd_away"]))
big = {k: v for k, v in ref_matches.items() if len(v) >= 8}
rng = random.Random(11); xs, ys = [], []
for k, v in big.items():
    idx = list(range(len(v))); rng.shuffle(idx); h = len(v) // 2
    xs.append(mean([v[i] for i in idx[:h]])); ys.append(mean([v[i] for i in idx[h:]]))
print(f"\nREFEREE: named in fit era {sum(1 for r in fit_era if r['referee'])}/{len(fit_era)}; "
      f"refs>=8 matches: {len(big)}; split-half strictness r={pearson(xs, ys)}")
out["referee"] = {"n_refs_ge8": len(big), "r": pearson(xs, ys),
                  "coverage_fit_era": sum(1 for r in fit_era if r["referee"]) / len(fit_era)}

# ---------- movers (X2 question, reverse of CO-B) ----------
print("\nMOVERS (promoted from Primera B; deltas in first A year vs that year's league mean per team):")
movers = {}
for year in range(2022, 2027):
    sub = [r for r in USABLE if r["season"].startswith(str(year))]
    if not sub: continue
    ids = sorted(set([r["home_team_id"] for r in sub if int(r["home_mover_up"])] + [r["away_team_id"] for r in sub if int(r["away_mover_up"])]))
    names = {}
    for r in sub:
        names[r["home_team_id"]] = r["home_team"]; names[r["away_team_id"]] = r["away_team"]
    gpm = mean([r["home_goals"] + r["away_goals"] for r in sub]); base = gpm / 2
    movers[str(year)] = []
    for tid in ids:
        gf = []; ga = []
        for r in sub:
            if r["home_team_id"] == tid: gf.append(r["home_goals"]); ga.append(r["away_goals"])
            if r["away_team_id"] == tid: gf.append(r["away_goals"]); ga.append(r["home_goals"])
        d = {"team": names[tid], "n": len(gf), "dgf": mean(gf) - base, "dga": mean(ga) - base}
        movers[str(year)].append(d)
        print(f"  {year} {names[tid]}: n={len(gf)} dGF={d['dgf']:+.3f} dGA={d['dga']:+.3f}")
    if not ids: print(f"  {year}: none")
dev_movers = [d for y in ("2022", "2023", "2024", "2025") for d in movers.get(y, [])]
if dev_movers:
    print(f"  DEV-era pooled (2022-2025 arrivals): dGF={mean([d['dgf'] for d in dev_movers]):+.3f} dGA={mean([d['dga'] for d in dev_movers]):+.3f} "
          f"({len(dev_movers)} club-years; GF same-sign {sum(1 for d in dev_movers if d['dgf'] < 0)}/{len(dev_movers)} negative, GA {sum(1 for d in dev_movers if d['dga'] > 0)}/{len(dev_movers)} positive)")
out["movers"] = movers

# absent-prev (non-B) arrivals per year, for context
for year in range(2022, 2027):
    sub = [r for r in USABLE if r["season"].startswith(str(year))]
    both = set([r["home_team_id"] for r in sub if int(r["home_absent_prev"])] + [r["away_team_id"] for r in sub if int(r["away_absent_prev"])])
    up = set([r["home_team_id"] for r in sub if int(r["home_mover_up"])] + [r["away_team_id"] for r in sub if int(r["away_mover_up"])])
    print(f"ABSENT {year}: absent_prev={len(both)} of which mover_up={len(up)} other={len(both - up)}")

# ---------- SHRINK context: priors at each dev tournament start ----------
print("\nPRIORS at tournament starts (matches strictly before the tournament's first date):")
ordered = sorted(USABLE, key=lambda r: (r["date"], r["match_id"]))
for s in DEV_EVAL + [VIRGIN]:
    first = min(r["date"] for r in USABLE if r["season"] == s)
    prior_counts = Counter()
    seen = Counter()
    for r in ordered:
        if r["date"] < first:
            seen[r["home_team_id"]] += 1; seen[r["away_team_id"]] += 1
    teams_s = set([r["home_team_id"] for r in USABLE if r["season"] == s] + [r["away_team_id"] for r in USABLE if r["season"] == s])
    low = {t: seen.get(t, 0) for t in teams_s if seen.get(t, 0) < 6}
    print(f"  {s}: teams={len(teams_s)} with <6 priors: {low}")

# ---------- xG era descriptive (virgin-era only; NOT used for any arm) ----------
xg_era = [r for r in USABLE if int(r["has_xg"])]
if xg_era:
    gx = mean([(fnum(r, "expected_goals_home") or 0) + (fnum(r, "expected_goals_away") or 0) for r in xg_era])
    gg = mean([r["home_goals"] + r["away_goals"] for r in xg_era])
    print(f"\nXG ERA (2025-Cl..2026-Ap, n={len(xg_era)}): mean xG={gx:.3f} mean goals={gg:.3f} goals/xG={gg/gx:.3f}")
    sm = [r for r in xg_era if int(r["n_shotmap"]) > 0]
    print(f"  shotmap present in xG era: {len(sm)}/{len(xg_era)}")

# stadiums / altitude context
cities = Counter(r["stadium_city"] for r in USABLE if r["stadium_city"])
print(f"\nSTADIUM cities (top): {cities.most_common(8)}; distinct={len(cities)}")

json.dump(out, open(HERE / "eda_summary.json", "w"), indent=1, default=str)
print("\nwrote eda_summary.json")
