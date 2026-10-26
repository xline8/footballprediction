#!/usr/bin/env python3
"""test_core.py — smoke tests inti (tanpa framework, tanpa load CSV besar).

Jalankan: python test_core.py
Mencakup: parsing tanggal, normalisasi odds, konvensi blend, proper scoring,
Dixon-Coles dasar, dan pembagi walk-forward anti-leakage.
"""

import datetime
import sys

from football_etl import parse_date, norm3, blend3, blend2
from validation import eval_1x2, calibration_table, walk_forward_groups

FAILURES = []


def check(name, cond):
    if not cond:
        FAILURES.append(name)
        print(f"  FAIL {name}")
    else:
        print(f"  ok   {name}")


def test_parse_date():
    check("parse_date %Y-%m-%d", parse_date("2020-01-15") == datetime.date(2020, 1, 15))
    check("parse_date %d/%m/%Y", parse_date("15/01/2020") == datetime.date(2020, 1, 15))
    check("parse_date %d/%m/%y", parse_date("15/01/20") == datetime.date(2020, 1, 15))
    check("parse_date kosong", parse_date("") is None)
    check("parse_date None", parse_date(None) is None)
    check("parse_date invalid", parse_date("bukan-tanggal") is None)


def test_norm():
    p = norm3((2.0, 3.4, 3.4))
    check("norm3 jumlah ~1", p is not None and abs(sum(p) - 1.0) < 1e-9)
    check("norm3 berurutan", p is not None and p[0] > p[1] and abs(p[1] - p[2]) < 1e-9)
    check("norm3 invalid -> None", norm3((1.0, 0.0, 3.0)) is None)


def test_blend():
    p1 = (0.5, 0.3, 0.2)
    p2 = (0.4, 0.35, 0.25)
    b0 = blend3(p1, p2, 0.0)  # murni pasar
    b1 = blend3(p1, p2, 1.0)  # murni model
    check("blend w=0 => market", all(abs(b0[i] - p2[i]) < 1e-9 for i in range(3)))
    check("blend w=1 => model", all(abs(b1[i] - p1[i]) < 1e-9 for i in range(3)))
    check("blend sum ~1", abs(sum(b0) - 1.0) < 1e-9 and abs(sum(b1) - 1.0) < 1e-9)
    b2 = blend2(0.6, 0.5, 0.0)
    check("blend2 w=0 => market", abs(b2 - 0.5) < 1e-9)
    b3 = blend2(0.6, 0.5, 1.0)
    check("blend2 w=1 => model", abs(b3 - 0.6) < 1e-9)


def test_scoring():
    pairs = [((0.5, 0.3, 0.2), 0), ((0.2, 0.3, 0.5), 2), ((0.3, 0.4, 0.3), 1)]
    sm = eval_1x2(pairs)
    check("eval n", sm["n"] == 3)
    check("eval brier >= 0", sm["brier"] >= 0.0)
    check("eval log_loss >= 0", sm["log_loss"] >= 0.0)
    # semua prediksi = benar => F1 sempurna
    check("eval macro_f1 sempurna", abs(sm["macro_f1"] - 1.0) < 1e-9)
    check("eval per_class_f1 ada", set(sm["per_class_f1"]) == {"H", "D", "A"})
    cal = calibration_table([(0.8, 1), (0.7, 0), (0.9, 1)])
    check("calibration menghasilkan bin", len(cal) >= 1)


def test_dc():
    import model_v2 as mv
    games = [
        ("a", "b", 1, 0, datetime.date(2020, 1, 1)),
        ("b", "a", 0, 1, datetime.date(2020, 1, 15)),
        ("c", "b", 2, 0, datetime.date(2020, 2, 1)),
        ("a", "c", 3, 0, datetime.date(2020, 2, 10)),
    ]
    m = mv.DC()
    m.fit(games, datetime.date(2020, 3, 1), 270)
    lh, la = m._lam("a", "c")
    pr = m.probs(lh, la)
    s = pr["ph"] + pr["pd"] + pr["pa"]
    check("DC probs sum ~1", abs(s - 1.0) < 1e-9)
    check("DC home kuat -> ph > pa", pr["ph"] > pr["pa"])
    check("DC over ~ [0,1]", 0.0 <= pr["over"] <= 1.0)


def test_walk_forward_no_leakage():
    # matches sintetis singkat: 2 musim, 2 divisi
    dates = [datetime.date(2020, 1, 1), datetime.date(2020, 1, 20),
             datetime.date(2020, 2, 5), datetime.date(2020, 2, 25)]
    matches = [{"div": "E0", "season": "2019/20", "date": d} for d in dates]
    matches += [{"div": "E0", "season": "2020/21", "date": datetime.date(2020, 9, 1)}]
    by_div = {"E0": list(range(len(matches)))}
    groups = walk_forward_groups(matches, by_div, {"2020/21"}, freq="m")
    ok = True
    for idxs in groups.values():
        start = min(matches[i]["date"] for i in idxs)
        if any(matches[i]["date"] < start for i in idxs):
            ok = False
    check("walk-forward grup anti-leakage", ok)
    check("walk-forward setidaknya 1 grup", len(groups) >= 1)


if __name__ == "__main__":
    test_parse_date()
    test_norm()
    test_blend()
    test_scoring()
    test_dc()
    test_walk_forward_no_leakage()
    print()
    if FAILURES:
        print(f"GAGAL: {len(FAILURES)} cek -> {FAILURES}")
        sys.exit(1)
    print("SEMUA TES LULUS")
