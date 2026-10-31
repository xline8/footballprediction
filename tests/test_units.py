"""Unit tests for the project's core math.

These tests are data-free on purpose: they exercise pure functions with
fixed inputs, so they run in CI on a fresh checkout where the generated
data files (gitignored) do not exist. The data-dependent smoke tests stay
in test_core.py and run in the full local environment.

Run with pytest (`python -m pytest tests/ -q`) or directly
(`python tests/test_units.py`).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backtest_picks import _fair_probs
from grade_recommendations import (settle_1x2, settle_btts, settle_corner,
                                   settle_dc, settle_ou, settle_slip_unit)
from model_v2 import DC
from predict_cups import p_adv
from score_ledger import settle as ledger_settle, _result_label
from slip_recommender import _search
from ta_model import fair_odds

TOL = 1e-6


# ------------------------------------------------------------ de-vig (Shin)

def test_fair_probs_mult_sums_to_one():
    p = _fair_probs((1.72, 4.37, 4.89), "mult")
    assert abs(sum(p) - 1.0) < 1e-9
    assert all(0.0 < x < 1.0 for x in p)


def test_fair_probs_shin_golden():
    # Book from a real market_compare row (Frosinone vs Lecce, 2026-10-29).
    p = _fair_probs((1.72, 4.37, 4.89), "shin")
    assert abs(sum(p) - 1.0) < 1e-9
    assert abs(p[0] - 0.57560) < 1e-4
    assert abs(p[1] - 0.22432) < 1e-4
    assert abs(p[2] - 0.20008) < 1e-4


def test_shin_moves_prob_from_longshot_to_favourite():
    # Shin's method, unlike proportional de-vigging, shifts probability
    # mass from longshots toward the favourite.
    o = (1.72, 4.37, 4.89)
    mult = _fair_probs(o, "mult")
    shin = _fair_probs(o, "shin")
    assert shin[0] > mult[0]
    assert shin[2] < mult[2]


# ------------------------------------------------------------ Dixon-Coles

def test_dc_probs_sum_to_one():
    pr = DC().probs(2.0, 1.0)
    assert abs(pr["ph"] + pr["pd"] + pr["pa"] - 1.0) < 1e-9
    for k in ("ph", "pd", "pa", "over", "over15", "over35", "btts"):
        assert 0.0 <= pr[k] <= 1.0


def test_dc_probs_golden_and_monotone():
    pr = DC().probs(2.0, 1.0)
    assert abs(pr["ph"] - 0.5987) < 1e-3
    assert abs(pr["over"] - 0.5768) < 1e-3
    stronger = DC().probs(2.6, 1.0)
    assert stronger["ph"] > pr["ph"]


# ------------------------------------------------------------ p_adv (cups)

def test_p_adv_golden_bayern_like():
    # Verified against the live system on 2026-10-29 (Bayern-like tie).
    pr = DC().probs(2.29, 0.747)
    adv_h, adv_a = p_adv(pr["ph"], pr["pd"], pr["pa"], 2.29, 0.747)
    assert abs(adv_h - 0.87044) < 1e-4
    assert abs(adv_h + adv_a - 1.0) < 1e-9


def test_p_adv_invariants():
    pr = DC().probs(1.4, 1.1)
    adv_h, adv_a = p_adv(pr["ph"], pr["pd"], pr["pa"], 1.4, 1.1)
    assert abs(adv_h + adv_a - 1.0) < 1e-9
    # Advancing can only be at least as likely as winning in 90 minutes,
    # and never more likely than not losing in 90 minutes.
    assert adv_h >= pr["ph"] - 1e-12
    assert adv_h <= 1.0 - pr["pa"] + 1e-9
    assert adv_a >= pr["pa"] - 1e-12


def test_p_adv_symmetric_tie_is_fifty_fifty():
    adv_h, adv_a = p_adv(0.4, 0.2, 0.4, 1.3, 1.3)
    assert abs(adv_h - 0.5) < 1e-9
    assert abs(adv_a - 0.5) < 1e-9


# ------------------------------------------------------------ slip search

def _leg(match, date, o, pm):
    return {"match": match, "date": date, "home": match, "away": "x",
            "comp": "", "market": "DC", "line": "", "sel": "1X",
            "o": o, "pm": pm}


def test_slip_search_picks_highest_joint_in_band():
    by_match = {
        "A": [_leg("A", "2026-10-29", 1.30, 0.80),
              _leg("A", "2026-10-29", 2.60, 0.45)],
        "B": [_leg("B", "2026-10-29", 1.50, 0.70),
              _leg("B", "2026-10-29", 1.45, 0.72)],
        "C": [_leg("C", "2026-10-29", 1.90, 0.55)],
    }
    best_in, _ = _search(by_match, 2, 4, 1.85, 2.15, 2.0)
    assert best_in is not None
    tot, jp, ev, legs = best_in
    # A@1.30 x B@1.45 = 1.885, joint 0.576 beats A@1.30 x B@1.50 (0.56).
    assert abs(tot - 1.885) < 1e-9
    assert abs(jp - 0.576) < 1e-9
    assert len({l["match"] for l in legs}) == len(legs)  # one leg per match


def test_slip_search_fallback_is_nearest_to_target():
    by_match = {
        "A": [_leg("A", "2026-10-29", 1.10, 0.90)],
        "B": [_leg("B", "2026-10-29", 1.10, 0.90)],
    }
    best_in, best_near = _search(by_match, 2, 4, 1.85, 2.15, 2.0)
    assert best_in is None  # 1.21 cannot reach the band
    assert best_near is not None
    assert abs(best_near[0] - 1.21) < 1e-9


# ------------------------------------------------------------ ta fair odds

def test_fair_odds_with_push():
    # (1 - p_push) / p_win; a push refunds the stake.
    assert abs(fair_odds(0.6, 0.1) - 1.5) < 1e-12
    assert fair_odds(0.0, 0.5) == 999.0


# ------------------------------------------------------------ settlement (grade)

def test_settle_1x2_win_draw_lose():
    assert settle_1x2(2, 1, "1") == "hit"     # home win
    assert settle_1x2(2, 1, "X") == "lose"
    assert settle_1x2(2, 1, "2") == "lose"
    assert settle_1x2(1, 1, "X") == "hit"     # draw
    assert settle_1x2(1, 1, "1") == "lose"
    assert settle_1x2(1, 1, "2") == "lose"
    assert settle_1x2(1, 2, "2") == "hit"     # away win
    assert settle_1x2(1, 2, "1") == "lose"


def test_settle_dc_three_sides():
    assert settle_dc(2, 1, "1X") == "hit"
    assert settle_dc(2, 1, "12") == "hit"
    assert settle_dc(2, 1, "X2") == "lose"
    assert settle_dc(1, 1, "1X") == "hit"     # draw: 1X & X2 hit
    assert settle_dc(1, 1, "X2") == "hit"
    assert settle_dc(1, 1, "12") == "lose"
    assert settle_dc(0, 2, "X2") == "hit"
    assert settle_dc(0, 2, "1X") == "lose"


def test_settle_ou_with_push_on_round_line():
    assert settle_ou(3, 2.5, "Over") == "hit"
    assert settle_ou(3, 2.5, "Under") == "lose"
    assert settle_ou(2, 2.5, "Under") == "hit"
    # garis bulat: total == line -> push (kedua sisi)
    assert settle_ou(3, 3.0, "Over") == "push"
    assert settle_ou(3, 3.0, "Under") == "push"
    assert settle_ou(4, 3.0, "Over") == "hit"


def test_settle_btts_yes_no():
    assert settle_btts(2, 1, "Yes") == "hit"
    assert settle_btts(2, 1, "No") == "lose"
    assert settle_btts(1, 0, "No") == "hit"
    assert settle_btts(1, 0, "Yes") == "lose"
    assert settle_btts(0, 0, "No") == "hit"


def test_settle_corner_over_under_push():
    assert settle_corner(11, 10.5, "Over") == "hit"
    assert settle_corner(9, 10.5, "Under") == "hit"
    assert settle_corner(10, 10.0, "Over") == "push"
    assert settle_corner(10, 10.0, "Under") == "push"


def test_settle_slip_unit_all_hit_is_hit():
    assert settle_slip_unit(["hit", "hit", "hit"]) == "hit"


def test_settle_slip_unit_one_lose_is_lose():
    assert settle_slip_unit(["hit", "lose", "hit"]) == "lose"


def test_settle_slip_unit_push_dropped_rest_hit():
    assert settle_slip_unit(["hit", "push", "hit"]) == "hit"


def test_settle_slip_unit_all_push_is_push():
    assert settle_slip_unit(["push", "push"]) == "push"


def test_settle_slip_unit_any_pending_is_pending():
    assert settle_slip_unit(["hit", "pending", "push"]) == "pending"


def test_settle_slip_unit_ungradeable_excluded():
    assert settle_slip_unit(["hit", "ungradeable", "hit"]) == "hit"


def test_cup_90min_draw_settles_as_ft():
    # Piala: seri 90 menit -> home 1X2 lose, DC X2 hit (aturan 90 menit).
    assert settle_1x2(1, 1, "1") == "lose"
    assert settle_dc(1, 1, "X2") == "hit"


# ------------------------------------------- score_ledger settle (impor
# modul ini aman sejak refactor main(): tidak ada eksekusi saat impor)

def test_ledger_settle_1x2_and_foreign_side():
    ret, won, push = ledger_settle("1X2", "H", 2, 1, 2.25)
    assert won and not push and abs(ret - 2.25) < TOL
    ret, won, push = ledger_settle("1X2", "A", 2, 1, 2.25)
    assert not won and ret == 0.0
    try:
        ledger_settle("1X2", "1", 2, 1, 2.0)
        raise AssertionError("side asing harus raise ValueError")
    except ValueError:
        pass


def test_ledger_settle_ou_quarter_lines_split():
    ret, _, _ = ledger_settle("OU", "Over", 1, 1, 2.0, line="2.25")
    assert abs(ret - 0.5) < TOL  # total 2: setengah kalah
    ret, _, _ = ledger_settle("OU", "Over", 2, 1, 2.0, line="2.75")
    assert abs(ret - 1.5) < TOL  # total 3: setengah menang
    ret, _, push = ledger_settle("OU", "Over", 1, 1, 1.9, line="2.0")
    assert push and ret == 1.0


def test_ledger_result_label_halves():
    assert _result_label(2.0, 2.0, False) == "win"
    assert _result_label(0.0, 2.0, False) == "loss"
    assert _result_label(1.5, 2.0, False) == "half_win"
    assert _result_label(0.5, 2.0, False) == "half_loss"
    assert _result_label(1.0, 2.0, True) == "push"


# ------------------------------------------------- audit ronde 7

def test_cur_season_label_is_month_aware():
    from datetime import date as _date

    from pipeline_orchestrator import PipelineOrchestrator
    f = PipelineOrchestrator._cur_season_label
    assert f(_date(2026, 10, 30)) == "2026/27"
    assert f(_date(2027, 1, 15)) == "2026/27"   # versi lama: "2027/28"
    assert f(_date(2027, 6, 30)) == "2026/27"
    assert f(_date(2027, 7, 1)) == "2027/28"


def test_clean_stats_counts_per_division():
    import tempfile

    from pipeline_orchestrator import PipelineOrchestrator
    rows = [
        "Div,Season,Date,HomeTeam,AwayTeam",
        "E0,2026/27,2026-10-01,A,B",
        "E0,2026/27,2026-10-02,C,D",
        "D1,2025/26,2025-09-01,E,F",
    ]
    with tempfile.NamedTemporaryFile(
            "w", suffix=".csv", delete=False) as fh:
        fh.write("\n".join(rows) + "\n")
        path = fh.name
    st = PipelineOrchestrator._clean_stats(path)
    assert st["total"] == 3 and st["max_date"] == "2026-10-02"
    assert st["div_counts"] == {"E0": 2, "D1": 1}


def test_records_meta_write_merges_existing_keys():
    import json
    import tempfile

    from backtest_picks import _write_records_meta
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "records_cache.jsonl")
        meta_path = os.path.join(td, "records_cache.meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump({"data_fingerprint": "65899|2026-10-26|1816|1"}, f)
        _write_records_meta(out, "999:42")
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    assert meta["data_fingerprint"] == "65899|2026-10-26|1816|1"
    assert meta["data_stamp"] == "999:42"
    assert meta["dc_fit_mode"]


def test_records_meta_write_stamps_schema():
    import json
    import tempfile

    from backtest_picks import RECORDS_SCHEMA, _write_records_meta
    with tempfile.TemporaryDirectory() as td:
        out = os.path.join(td, "records_cache.jsonl")
        _write_records_meta(out, "1:1")
        with open(os.path.join(td, "records_cache.meta.json"),
                  encoding="utf-8") as f:
            meta = json.load(f)
    assert meta["records_schema"] == RECORDS_SCHEMA == 2


def test_meta_walkforward_fills_later_months_only():
    from backtest_picks import _add_meta_walkforward

    def rec(date, yi):
        return {"div": "E0", "date": date, "yi": yi,
                "ph_dc": 0.45, "pd_dc": 0.28, "pa_dc": 0.27,
                "ph_t3": 0.44, "pd_t3": 0.29, "pa_t3": 0.27,
                "o": [2.2, 3.4, 3.6]}

    recs = ([rec("2024-01-0%d" % (i + 1), i % 3) for i in range(6)]
            + [rec("2024-02-0%d" % (i + 1), (i + 1) % 3) for i in range(6)]
            + [rec("2024-03-0%d" % (i + 1), (i + 2) % 3) for i in range(6)])
    filled = _add_meta_walkforward(recs, min_train=5)
    # Bulan pertama tidak punya riwayat latih: tidak terisi. Dua bulan
    # berikutnya terisi penuh dan probabilitasnya ternormalisasi.
    assert filled == 12
    assert all("ph_meta" not in r for r in recs[:6])
    for r in recs[6:]:
        s = r["ph_meta"] + r["pd_meta"] + r["pa_meta"]
        assert abs(s - 1.0) < 1e-6
        assert all(0.0 < r[k] < 1.0 for k in
                   ("ph_meta", "pd_meta", "pa_meta"))


def test_select_safest_priced_negative_ev_beats_unpriced():
    from best_picks import _select_safest
    priced = {"prob": 0.5, "tier": "fallback", "ev": None,
              "ev_model": -0.30, "tag": "priced"}
    unpriced = {"prob": 0.5, "tier": "fallback", "ev": None,
                "ev_model": None, "tag": "unpriced"}
    # Seri probabilitas: kandidat terharga (EV negatif nyata) menang
    # atas kandidat tanpa harga — None bukan 0.
    assert _select_safest([], [unpriced, priced])["tag"] == "priced"
    # Probabilitas tetap raja di atas semua tie-break.
    likelier = {"prob": 0.6, "tier": "fallback", "ev": None,
                "ev_model": None, "tag": "likelier"}
    assert _select_safest([], [priced, likelier])["tag"] == "likelier"


def _stub_orchestrator(statuses):
    from collections import defaultdict

    import pipeline_orchestrator as po
    orch = po.PipelineOrchestrator.__new__(po.PipelineOrchestrator)
    orch.stats = defaultdict(int)
    orch.verbose = False
    names = ["step_refresh_training_data", "step_check_data",
             "step_build_xg", "step_fit_models", "step_score_upcoming",
             "step_score_corners", "step_integrate_odds",
             "scrape_live_odds", "step_ta_model", "step_predict_cups",
             "step_generate_picks", "step_validation"]
    for nm in names:
        st = statuses.get(nm, {"status": "success"})
        setattr(orch, nm, (lambda st: lambda: dict(st))(st))
    return orch, po


def test_pipeline_gates_dependents_on_failed_refresh():
    import tempfile

    orch, po = _stub_orchestrator(
        {"step_refresh_training_data": {"status": "failed"}})
    with tempfile.TemporaryDirectory() as td:
        old = po.BASE_DIR
        po.BASE_DIR = td
        try:
            res = orch.run_full_pipeline()
        finally:
            po.BASE_DIR = old
        with open(os.path.join(td, "last_full_pipeline.json"),
                  encoding="utf-8") as f:
            import json
            rec = json.load(f)
    assert res["status"] == "failed"
    assert res["xg"]["status"] == "skipped"
    assert res["scoring"]["status"] == "skipped"
    assert res["picks"]["status"] == "skipped"
    assert res["ta_model"]["status"] == "success"  # TA independen
    assert rec["status"] == "failed" and rec["failed_steps"] == ["refresh"]


def test_pipeline_gates_scoring_on_partial_xg_only():
    orch, po = _stub_orchestrator(
        {"step_build_xg": {"status": "partial"}})
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        old = po.BASE_DIR
        po.BASE_DIR = td
        try:
            res = orch.run_full_pipeline()
        finally:
            po.BASE_DIR = old
    assert res["scoring"]["status"] == "skipped"
    assert res["model"]["status"] == "success"       # fit tak butuh xg step
    assert res["corner_model"]["status"] == "success"
    assert res["picks"]["status"] == "skipped"       # rantai skip menular
    assert res["status"] == "failed"                  # partial = gagal


def test_calibration_overall_unique_dedupes_selections():
    from grade_recommendations import _build_summary

    def leg(product, market, sel, p, status="hit"):
        return {"status": status, "level": "leg", "product": product,
                "market": market, "selection": sel, "p_model": p,
                "date": "2026-10-29", "home": "fiorentina",
                "away": "atalanta", "line": "", "reason": ""}

    store = {
        "a": leg("single", "DC", "X2", 0.6845),
        "b": leg("slip2", "DC", "X2", 0.6845),   # seleksi sama, produk lain
        "c": leg("pick_teraman", "OU", "Over", 0.8088),
    }
    s = _build_summary(store)
    assert s["overall"]["n"] == 3
    assert s["overall_unique"]["n"] == 2


def test_pipeline_soft_partial_model_and_odds():
    import json
    import tempfile

    orch, po = _stub_orchestrator(
        {"step_fit_models": {"status": "partial"},
         "step_integrate_odds": {"status": "partial"}})
    with tempfile.TemporaryDirectory() as td:
        old = po.BASE_DIR
        po.BASE_DIR = td
        try:
            res = orch.run_full_pipeline()
        finally:
            po.BASE_DIR = old
        with open(os.path.join(td, "last_full_pipeline.json"),
                  encoding="utf-8") as f:
            rec = json.load(f)
    # Partial lunak: scoring/picks tetap jalan, run tidak gagal,
    # tapi partial-nya tercatat di hasil dan di file status.
    assert res["scoring"]["status"] == "success"
    assert res["picks"]["status"] == "success"
    assert res["status"] == "completed"
    assert sorted(res["partial_steps"]) == ["model", "odds"]
    assert rec["failed_steps"] == []
    assert sorted(rec["partial_steps"]) == ["model", "odds"]


def test_pipeline_exception_step_is_named():
    import json
    import tempfile

    orch, po = _stub_orchestrator({})

    def boom():
        raise RuntimeError("data hilang")

    orch.step_check_data = boom
    with tempfile.TemporaryDirectory() as td:
        old = po.BASE_DIR
        po.BASE_DIR = td
        try:
            res = orch.run_full_pipeline()
        finally:
            po.BASE_DIR = old
        with open(os.path.join(td, "last_full_pipeline.json"),
                  encoding="utf-8") as f:
            rec = json.load(f)
    assert res["status"] == "failed"
    assert res["error_step"] == "data"
    assert rec["failed_steps"] == ["data"]
    assert rec["error_step"] == "data" and "data hilang" in rec["error"]


def test_cups_step_honors_inner_failed_status():
    import types

    import pipeline_orchestrator as po

    fake = types.ModuleType("predict_cups")
    fake.main = lambda: {"status": "failed", "n_gol": 0, "n_corner": 0,
                         "n_fixtures": 3}
    old = sys.modules.get("predict_cups")
    sys.modules["predict_cups"] = fake
    try:
        orch = po.PipelineOrchestrator.__new__(po.PipelineOrchestrator)
        r = orch.step_predict_cups()
        assert r["status"] == "failed" and r["n_fixtures"] == 3
        fake.main = lambda: {"status": "success", "n_gol": 2,
                             "n_corner": 2, "n_fixtures": 1}
        r = orch.step_predict_cups()
        assert r["status"] == "success" and r["n_gol"] == 2
    finally:
        if old is None:
            sys.modules.pop("predict_cups", None)
        else:
            sys.modules["predict_cups"] = old


def test_match_game_id_exact_names_two_day_window_unique_only():
    import tempfile

    import market_orchestration as mo

    hdr = "game_id,home,away,date,league\n"
    with tempfile.TemporaryDirectory() as td:
        old = mo.TA
        mo.TA = td
        try:
            with open(os.path.join(td, "fixtures.csv"), "w",
                      encoding="utf-8") as f:
                f.write(hdr + "111,Lorient,Brest,2026-11-02,"
                              "France - Ligue 1\n")
            # ±1 hari: perilaku lama.
            assert mo._match_game_id("Lorient", "Brest",
                                     "2026-11-01") == "111"
            # ±2 hari, nama eksak kedua sisi, kandidat unik: terjodohkan.
            assert mo._match_game_id("Lorient", "Brest",
                                     "2026-10-31") == "111"
            # Kandidat kedua dalam ±2 hari -> ambigu -> tidak menebak.
            with open(os.path.join(td, "fixtures.csv"), "a",
                      encoding="utf-8") as f:
                f.write("112,Lorient,Brest,2026-10-29,"
                        "France - Ligue 1\n")
            assert mo._match_game_id("Lorient", "Brest",
                                     "2026-10-31") is None
        finally:
            mo.TA = old


def test_download_out_is_paths_raw_dir():
    import download
    import paths

    assert download.OUT == paths.RAW_DIR


def _refresh_env(td):
    """Arahkan paths ke tmp + stub modul refresh; kembalikan
    (orchestrator, restore). Untuk tes step_refresh_training_data
    tanpa menyentuh data asli."""
    import types

    import pipeline_orchestrator as po
    import paths

    raw_dir = os.path.join(td, "raw")
    xg_dir = os.path.join(td, "xg_raw")
    os.makedirs(raw_dir)
    os.makedirs(xg_dir)
    saved = {k: getattr(paths, k)
             for k in ("DATA_CLEAN", "DATA_RAW", "RAW_DIR", "XGRAW")}
    paths.RAW_DIR = raw_dir
    paths.XGRAW = xg_dir
    paths.DATA_RAW = os.path.join(td, "all_matches.csv")
    paths.DATA_CLEAN = os.path.join(td, "all_matches_clean.csv")

    stubs = {}
    for name in ("download", "prepare", "clean", "refresh_fixtures"):
        stubs[name] = sys.modules.get(name)
    dl = types.ModuleType("download")
    dl.download = lambda seasons, force: {"ok": 21, "total": 21}
    pp = types.ModuleType("prepare")
    pp.prepare = lambda: {}
    cc = types.ModuleType("clean")
    cc.clean = lambda: {}
    rf = types.ModuleType("refresh_fixtures")
    rf.fetch = lambda slug: [1, 2, 3]
    sys.modules.update({"download": dl, "prepare": pp, "clean": cc,
                        "refresh_fixtures": rf})

    orch = po.PipelineOrchestrator.__new__(po.PipelineOrchestrator)
    orch._rebuild_records_if_changed = lambda: False

    def restore():
        for k, v in saved.items():
            setattr(paths, k, v)
        for name, mod in stubs.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod

    return orch, paths, restore


def test_refresh_rollback_keeps_raw_files_when_stats_fail():
    # Kegagalan SEBELUM fase backup selesai (di sini _clean_stats
    # raise karena path file bersih berupa direktori) tidak boleh
    # membuat rollback menghapus file raw yang sudah ada: catatan
    # `existed` kini diisi lengkap sebelum try (audit ronde 9).
    import tempfile
    import types

    with tempfile.TemporaryDirectory() as td:
        orch, paths, restore = _refresh_env(td)
        try:
            os.makedirs(paths.DATA_CLEAN)  # direktori -> stats raise
            raws = {}
            for nm in ("E0_2627.csv", "D1_2627.csv"):
                p = os.path.join(paths.RAW_DIR, nm)
                with open(p, "w", encoding="utf-8") as f:
                    f.write(f"RAW-{nm}")
                raws[p] = f"RAW-{nm}"
            r = orch.step_refresh_training_data()
            assert r["status"] == "failed"
            for p, content in raws.items():
                assert os.path.exists(p), f"{p} terhapus rollback"
                with open(p, encoding="utf-8") as f:
                    assert f.read() == content
        finally:
            restore()


def test_refresh_post_commit_failure_is_a_step_result():
    # reload_data raise SETELAH data ter-commit: langkah harus
    # mengembalikan failed dengan committed=True, bukan melempar
    # exception keluar langkah (audit ronde 9).
    import tempfile
    import types

    hdr = "Date,Div,Season\n"
    before = hdr + "2026-08-01,E0,2026/27\n"
    grown = before + "2026-08-02,E0,2026/27\n"
    with tempfile.TemporaryDirectory() as td:
        orch, paths, restore = _refresh_env(td)
        try:
            with open(paths.DATA_CLEAN, "w", encoding="utf-8") as f:
                f.write(before)
            with open(paths.DATA_RAW, "w", encoding="utf-8") as f:
                f.write("ALL-OLD")
            for nm in ("E0_2627.csv",):
                with open(os.path.join(paths.RAW_DIR, nm), "w",
                          encoding="utf-8") as f:
                    f.write("RAW-OLD")
            import pipeline_orchestrator as po
            for slug in po.XG_SLUGS:
                with open(os.path.join(paths.XGRAW, f"{slug}_2026.json"),
                          "w", encoding="utf-8") as f:
                    f.write("[1, 2]")

            def _clean():
                with open(paths.DATA_CLEAN, "w", encoding="utf-8") as f:
                    f.write(grown)
                return {}

            sys.modules["clean"].clean = _clean

            def boom():
                raise RuntimeError("loader rusak")

            orch.loader = types.SimpleNamespace(reload_data=boom)
            r = orch.step_refresh_training_data()
            assert r["status"] == "failed" and r["committed"] is True
            with open(paths.DATA_CLEAN, encoding="utf-8") as f:
                assert f.read() == grown  # data memang ter-commit
        finally:
            restore()


def test_fit_models_rollup_zero_divisions_fails():
    import types
    from collections import defaultdict

    import pipeline_orchestrator as po

    class FakeState:
        def __init__(self, div):
            pass

        def load(self):
            return True

    old_state = po.ModelState
    po.ModelState = FakeState
    try:
        orch = po.PipelineOrchestrator.__new__(po.PipelineOrchestrator)
        orch.loader = types.SimpleNamespace(
            get_matches_by_div=lambda div: [])
        orch.stats = defaultdict(int)
        r = orch.step_fit_models()
        assert r["status"] == "failed"
    finally:
        po.ModelState = old_state


def test_load_fixtures_drops_results_and_started_matches():
    # Loader liga hanya boleh memuat fixture prematch (audit GPT
    # 2026-10-31, A): laga selesai (isResult) dan laga yang kickoff
    # UTC-nya sudah tercapai pada tanggal yang sama harus gugur.
    import json
    import tempfile
    from datetime import datetime, timedelta, timezone

    import football_etl

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    fmt = "%Y-%m-%d %H:%M:%S"

    def item(dt, is_result, hid):
        return {"id": hid, "datetime": dt.strftime(fmt),
                "isResult": is_result,
                "h": {"title": "Arsenal"}, "a": {"title": "Chelsea"}}

    items = [
        item(now + timedelta(days=2), False, 1),   # masa depan: lolos
        item(now + timedelta(days=2), True, 2),    # sudah selesai: gugur
        item(now - timedelta(hours=1), False, 3),  # kickoff lewat: gugur
        item(now - timedelta(days=1), False, 4),   # kemarin: gugur
    ]
    with tempfile.TemporaryDirectory() as td:
        with open(os.path.join(td, "EPL_2026_fixtures.json"), "w",
                  encoding="utf-8") as f:
            json.dump(items, f)
        with open(os.path.join(td, "map_full.json"), "w",
                  encoding="utf-8") as f:
            json.dump({"E0|Arsenal": "Arsenal", "E0|Chelsea": "Chelsea"}, f)
        old = football_etl.XGRAW
        football_etl.XGRAW = td
        try:
            fx = football_etl.load_fixtures("2026")
        finally:
            football_etl.XGRAW = old
    assert [x["uid"] for x in fx] == [1], fx


def test_model_state_data_fingerprint_gate():
    # State yang di-fit atas data yang kemudian berubah (koreksi skor /
    # xG) harus dianggap basi lewat fingerprint (audit GPT, C).
    import tempfile

    import model_state

    with tempfile.TemporaryDirectory() as td:
        old = model_state.CACHE_DIR
        model_state.CACHE_DIR = td
        try:
            st = model_state.ModelState("E0")
            st._initialized = True
            for _t in ("Arsenal", "Chelsea"):
                st.attack[_t] = 1.0
                st.defense[_t] = 1.0
            st.data_fp = model_state.current_data_fingerprint()
            assert st.data_stale() is False
            assert st.needs_fit([("Arsenal", "Chelsea")], None) is False
            st.data_fp = "fingerprint-lama"
            assert st.data_stale() is True
            assert st.needs_fit([("Arsenal", "Chelsea")], None) is True
            # roundtrip save/load mempertahankan cap fingerprint
            st.data_fp = model_state.current_data_fingerprint()
            st.updated_at = "2026-10-31T00:00:00"
            st.save()
            st2 = model_state.ModelState("E0")
            assert st2.load() is True
            assert st2.data_fp == st.data_fp
        finally:
            model_state.CACHE_DIR = old


def test_refresh_clean_violations_block_commit():
    # violations dari clean() adalah gerbang pra-commit (audit GPT, D):
    # data cacat -> langkah gagal dan file bersih lama dipulihkan,
    # bukan ter-commit.
    import tempfile

    hdr = "Date,Div,Season\n"
    before = hdr + "2026-08-01,E0,2026/27\n"
    grown = before + "2026-08-02,E0,2026/27\n"
    with tempfile.TemporaryDirectory() as td:
        orch, paths, restore = _refresh_env(td)
        try:
            with open(paths.DATA_CLEAN, "w", encoding="utf-8") as f:
                f.write(before)
            with open(paths.DATA_RAW, "w", encoding="utf-8") as f:
                f.write("ALL-OLD")
            with open(os.path.join(paths.RAW_DIR, "E0_2627.csv"), "w",
                      encoding="utf-8") as f:
                f.write("RAW-OLD")
            import pipeline_orchestrator as po
            for slug in po.XG_SLUGS:
                with open(os.path.join(paths.XGRAW, f"{slug}_2026.json"),
                          "w", encoding="utf-8") as f:
                    f.write("[1, 2]")

            def _clean():
                with open(paths.DATA_CLEAN, "w", encoding="utf-8") as f:
                    f.write(grown)
                return {"rows": 2, "violations": 2}

            sys.modules["clean"].clean = _clean
            r = orch.step_refresh_training_data()
            assert r["status"] == "failed", r
            assert not r.get("committed"), r
            with open(paths.DATA_CLEAN, encoding="utf-8") as f:
                assert f.read() == before  # rollback, bukan commit
        finally:
            restore()


def test_ta_parse_keeps_raw_status():
    # Status mentah AET/PEN dipertahankan walau status kanonis tetap FT
    # (audit GPT, E) — bukti untuk audit settlement 90 menit berikutnya.
    import ta_scrape

    html = ('<span class="league-name"><span>England - EFL Cup</span>'
            '<a class="game" href="/match/alpha-beta-123456">'
            '<span class="time notime started">20:00</span>'
            '<span class="status play">AET</span>'
            '<span class="teams">'
            '<span class="home"><span>Alpha</span></span>'
            '<span class="score scsm play">2 - 1</span>'
            '<span class="away"><span>Beta</span></span>'
            '</span>'
            '<span class="odds"><span class="o1">2.10</span>'
            '<span class="oX">3.20</span><span class="o2">3.40</span></span>'
            '</a>')
    games = ta_scrape.parse_date_page(html, "2026-10-28")
    assert len(games) == 1, games
    assert games[0]["status"] == "FT"
    assert games[0]["status_raw"] == "AET"
    assert (games[0]["score_h"], games[0]["score_a"]) == ("2", "1")


def test_score_ledger_ta_league_results_fill():
    # Hasil liga TipsterArea dimuat untuk mengisi kekosongan dump
    # Understat (audit GPT, F): hanya liga TOP5 dan hanya status FT.
    import tempfile

    import score_ledger

    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "ta"))
        with open(os.path.join(td, "ta", "results.csv"), "w",
                  encoding="utf-8") as f:
            f.write("game_id,date,league,home,away,score_h,score_a,"
                    "status,source_url,updated_at\n")
            f.write("1,2026-10-29,Italy - Serie A,Fiorentina,Atalanta,"
                    "2,2,FT,http://x,2026-10-30\n")
            f.write("2,2026-10-29,Italy - Serie B,Modena,Bari,"
                    "1,0,FT,http://x,2026-10-30\n")
            f.write("3,2026-10-29,England - Premier League,Arsenal,"
                    "Chelsea,,,NS,http://x,2026-10-30\n")
        old = score_ledger.PROJ
        score_ledger.PROJ = td
        try:
            out = score_ledger._load_ta_league_results()
        finally:
            score_ledger.PROJ = old
    from football_etl import normalize_name
    key = ("I1", "2026-10-29", normalize_name("Fiorentina"),
           normalize_name("Atalanta"))
    assert out == {key: (2, 2)}, out


def test_shadow_fixture_age_thresholds():
    # Umur fixture dinilai dari file liga paling basi (audit GPT, G).
    import tempfile
    import time as _time

    import run_daily_shadow as rds

    with tempfile.TemporaryDirectory() as td:
        xg = os.path.join(td, "xg_raw")
        os.makedirs(xg)
        for slug in rds.FIXTURE_SLUGS:
            p = os.path.join(xg, f"{slug}_2026_fixtures.json")
            with open(p, "w", encoding="utf-8") as f:
                f.write("[]")
        old = rds.BASE
        rds.BASE = td
        try:
            assert rds._fixtures_age_h() < 0.1
            stale = os.path.join(xg, "EPL_2026_fixtures.json")
            old_t = _time.time() - 72 * 3600
            os.utime(stale, (old_t, old_t))
            assert rds._fixtures_age_h() > 71
            os.remove(os.path.join(xg, "Ligue_1_2026_fixtures.json"))
            assert rds._fixtures_age_h() == float("inf")
        finally:
            rds.BASE = old


def test_fingerprint_paths_point_at_consumed_files():
    # A12-1: cap fingerprint PR #32 menunjuk xg_matches.csv di root
    # proyek — file yang tidak pernah dibaca fit — sehingga komponen
    # xG permanen "absent". Tes ini mengunci path ke lokasi yang
    # benar-benar dikonsumsi: gol di root, xG di folder XGRAW (lokasi
    # yang sama yang dibaca features.py).
    import model_state
    from paths import BASE as _BASE, XGRAW as _XGRAW

    by_label = dict(model_state._FP_FILES)
    assert by_label["all_matches_clean.csv"] == os.path.join(
        _BASE, "all_matches_clean.csv")
    assert by_label["xg_matches.csv"] == os.path.join(
        _XGRAW, "xg_matches.csv")
    # Bila file xG nyata ada di mesin ini, komponennya tidak boleh
    # "absent" — inilah persis kegagalan yang lolos di PR #32.
    if os.path.exists(by_label["xg_matches.csv"]):
        fp = model_state.current_data_fingerprint()
        assert "xg_matches.csv:absent" not in fp, fp


def test_fingerprint_flips_on_xg_only_change():
    # Revisi xG-saja (tanpa perubahan gol) harus membatalkan cache:
    # fingerprint berubah dan data_stale() menyala.
    import tempfile

    import model_state

    with tempfile.TemporaryDirectory() as td:
        goals = os.path.join(td, "all_matches_clean.csv")
        xg = os.path.join(td, "xg_matches.csv")
        with open(goals, "w", encoding="utf-8") as f:
            f.write("date,home\n2026-01-01,A\n")
        with open(xg, "w", encoding="utf-8") as f:
            f.write("key,xg\nm1,1.20\n")
        old_files, old_memo = model_state._FP_FILES, model_state._fp_memo
        model_state._FP_FILES = (
            ("all_matches_clean.csv", goals), ("xg_matches.csv", xg))
        model_state._fp_memo = {}
        try:
            fp1 = model_state.current_data_fingerprint()
            st = model_state.ModelState("E0")
            st.data_fp = fp1
            assert not st.data_stale()
            with open(xg, "w", encoding="utf-8") as f:
                f.write("key,xg\nm1,1.85\n")
            fp2 = model_state.current_data_fingerprint()
            assert fp2 != fp1
            assert st.data_stale()
        finally:
            model_state._FP_FILES, model_state._fp_memo = old_files, old_memo


def test_calibrate_falls_back_when_worse_than_raw():
    # B12-1: laga favorit kuat (Barcelona vs Alaves, angka audit ronde
    # 12). Matriks mentah di lambda DC sudah cocok dengan target dalam
    # 0,003; kalibrasi lama berakhir di total gol 7,81 dan BTS Yes
    # 0,8968. Pagar harus memakai matriks mentah dan menandainya.
    import ta_model as tm

    m, fell_back = tm.calibrate(2.957, 0.851, 0.7952, 0.1303, 0.0745)
    assert fell_back is True
    bts = tm.market_probs(m, "BTS")["Yes"][0]
    assert bts < 0.60, bts
    ph, pd, pa = tm.outcomes(m)
    assert max(abs(ph - 0.7952), abs(pd - 0.1303), abs(pa - 0.0745)) < 0.005


def test_calibrate_keeps_converged_result():
    # Laga seimbang: kalibrasi yang konvergen ke target tidak boleh
    # diganggu pagar.
    import ta_model as tm

    m, fell_back = tm.calibrate(1.60, 1.10, 0.50, 0.27, 0.23)
    assert fell_back is False
    ph, pd, pa = tm.outcomes(m)
    assert max(abs(ph - 0.50), abs(pd - 0.27), abs(pa - 0.23)) < 0.005


def test_ta_picks_ranked_by_shrunk_probability():
    # B12-4: peringkat pick ta_model memakai p_shrunk (campuran
    # p_model/p_market menurut SHRINK ta_model), bukan p_model mentah.
    import csv
    import tempfile

    import best_picks as bp

    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "ta"))
        with open(os.path.join(td, "ta", "best_bets.csv"), "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=[
                "bet_id", "created_at", "game_id", "kickoff_utc",
                "league", "home", "away", "market", "line", "selection",
                "bookmaker", "price", "p_model", "p_market", "ev",
                "tier", "status", "score", "result", "profit",
                "graded_at"])
            w.writeheader()
            w.writerow({
                "bet_id": "t1", "created_at": "", "game_id": "1",
                "kickoff_utc": "2099-01-01T20:00:00+00:00",
                "league": "Spain - La Liga", "home": "Barcelona",
                "away": "Alaves", "market": "BTS", "line": "",
                "selection": "Yes", "bookmaker": "x", "price": "2.85",
                "p_model": "0.90", "p_market": "0.50", "ev": "0.30",
                "tier": "aman", "status": "OPEN", "score": "",
                "result": "", "profit": "", "graded_at": ""})
        old_proj, old_anchor = bp.PROJ, bp.ANCHOR
        bp.PROJ, bp.ANCHOR = td, "2000-01-01"
        try:
            picks = bp._load_ta_picks()
        finally:
            bp.PROJ, bp.ANCHOR = old_proj, old_anchor
    assert len(picks) == 1, picks
    # SHRINK = 0.5: 0.5*0.90 + 0.5*0.50 = 0.70, bukan 0.90 mentah.
    assert picks[0]["prob"] == 0.70, picks[0]


def test_refresh_returns_per_league_source():
    # A12-2: pemanggil harus bisa membedakan konten segar dari
    # fallback disk — main() mengembalikan {div: sumber}.
    import tempfile

    import refresh_fixtures as rf

    with tempfile.TemporaryDirectory() as td:
        for slug in rf.LEAGUES:
            with open(os.path.join(td, f"{slug}_2026_fixtures.json"),
                      "w", encoding="utf-8") as f:
                f.write("[]")
            with open(os.path.join(td, f"{slug}_2026_all.json"),
                      "w", encoding="utf-8") as f:
                f.write("[]")

        def fake_fetch(slug):
            if slug == "EPL":
                return [{"datetime": "2099-01-01 20:00:00",
                         "h": {"title": "A"}, "a": {"title": "B"}}]
            raise RuntimeError("sumber mati (stub tes)")

        old_xg, old_fetch = rf.XG, rf.fetch
        rf.XG, rf.fetch = td, fake_fetch
        try:
            srcs = rf.main()
        finally:
            rf.XG, rf.fetch = old_xg, old_fetch
    assert srcs["E0"] == "understat.com", srcs
    for div in ("SP1", "D1", "I1", "F1"):
        assert srcs[div].startswith("fallback disk"), srcs


def test_save_date_page_persists_status_raw():
    # C12-2 + A12-5: status_raw tersimpan di fixtures.csv DAN
    # results.csv; pengisian status_raw belakangan (skor sama)
    # tetap memicu tulis ulang baris hasil.
    import csv as _csv
    import tempfile

    import ta_scrape

    game = {"game_id": "991", "date": "2026-10-30", "time": "20:00",
            "league": "Germany - DFB Pokal", "country": "Germany",
            "home": "A", "away": "B", "status": "FT", "score_h": "1",
            "score_a": "1", "o1": "", "ox": "", "o2": "",
            "url": "u", "status_raw": ""}
    with tempfile.TemporaryDirectory() as td:
        old_dir = ta_scrape.DIR
        ta_scrape.DIR = td
        try:
            ta_scrape.save_date_page([dict(game)], "2026-10-30T00:00:00")
            g2 = dict(game, status_raw="AET")
            ta_scrape.save_date_page([g2], "2026-10-30T01:00:00")
            with open(os.path.join(td, "results.csv"),
                      newline="", encoding="utf-8") as f:
                res = list(_csv.DictReader(f))
            with open(os.path.join(td, "fixtures.csv"),
                      newline="", encoding="utf-8") as f:
                fix = list(_csv.DictReader(f))
        finally:
            ta_scrape.DIR = old_dir
    assert res[0]["status_raw"] == "AET", res
    assert fix[0]["status_raw"] == "AET", fix


def test_slip_search_matches_brute_force():
    # B12-2: fase pita branch-and-bound harus mengembalikan optimum
    # menyeluruh yang sama dengan enumerasi brute force (bukan
    # kandidat awalan ruang seperti DFS lama yang terpotong).
    import itertools
    import random

    from slip_recommender import _search

    rng = random.Random(20261031)
    for _trial in range(6):
        by_match = {}
        for mi in range(6):
            legs = []
            for _k in range(3):
                o = round(rng.uniform(1.2, 2.6), 2)
                pm = round(rng.uniform(0.35, 0.85), 3)
                legs.append(_leg(f"M{mi}", "2026-10-31", o, pm))
            by_match[f"M{mi}"] = legs
        best_in, _ = _search(by_match, 2, 4, 1.85, 2.15, 2.0)
        pools = list(by_match.values())
        brute = None
        for r in range(2, 5):
            for combo in itertools.combinations(range(len(pools)), r):
                for legs in itertools.product(*[pools[i] for i in combo]):
                    tot = jp = 1.0
                    for l in legs:
                        tot *= l["o"]
                        jp *= l["pm"]
                    if 1.85 <= tot <= 2.15 and (brute is None or jp > brute):
                        brute = jp
        if brute is None:
            assert best_in is None
        else:
            assert best_in is not None
            assert abs(best_in[1] - brute) < 1e-9, (best_in[1], brute)


def test_slip_csv_carries_search_truncated():
    # B12-2: flag kualitas pencarian persisten sebagai kolom produk.
    import csv
    import tempfile

    import slip_recommender as sr

    best = (2.0, 0.5, 0.0, [_leg("A", "2026-10-31", 2.0, 0.5)])
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "slip.csv")
        sr._write_slip(p, sr.SLIP_COLS, best, True,
                       extra={"search_truncated": "true"})
        with open(p, newline="", encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
    assert rows and rows[0]["search_truncated"] == "true", rows


def test_ta_key_name_folds_alias_variants():
    # C12-1: ejaan Understat dan TipsterArea untuk klub yang sama
    # harus bertemu di kunci yang sama.
    from score_ledger import _ta_key_name

    assert _ta_key_name("FC Cologne") == _ta_key_name("FC Koln")
    assert _ta_key_name("Internazionale") == _ta_key_name("Inter Milan")
    assert _ta_key_name("Stade Rennais") == _ta_key_name("Rennais")
    assert _ta_key_name("Nottingham Forest") == _ta_key_name("Nottingham")
    assert _ta_key_name("RasenBallsport Leipzig") == \
        _ta_key_name("RB Leipzig")
    # Klub berbeda tidak boleh terlipat jadi satu.
    assert _ta_key_name("FC Cologne") != _ta_key_name("RB Leipzig")


def test_by_teams_index_sorted_by_date():
    # C12-4: indeks fallback laga tunda terurut tanggal menaik.
    from score_ledger import _by_teams_index

    keyed = {("E0", "2026-03-01", "a", "b"): (1, 0),
             ("E0", "2026-01-15", "a", "b"): (2, 2),
             ("E0", "2026-02-01", "a", "c"): (0, 1)}
    idx = _by_teams_index(keyed)
    assert idx[("E0", "a", "b")] == [("2026-01-15", (2, 2)),
                                     ("2026-03-01", (1, 0))]


def test_match_result_postponed_fallback():
    # C12-4: leg laga tunda ketemu hasilnya di tanggal main baru —
    # tanggal setelah pick yang PALING AWAL (bukan pertemuan putaran
    # kedua), dan tidak pernah dari tanggal sebelum pick. Ronde 13:
    # return kini menyertakan tanggal hasil yang cocok, dan
    # pemindaian dibatasi 45 hari.
    from grade_recommendations import _match_result, norm

    idx = {
        "2026-11-20": [(norm("Arsenal"), norm("Chelsea"), 3, 0,
                        "England - Premier League")],
        "2026-11-05": [(norm("Arsenal"), norm("Chelsea"), 2, 1,
                        "England - Premier League")],
        "2026-10-01": [(norm("Arsenal"), norm("Chelsea"), 9, 9,
                        "England - Premier League")],
    }
    got = _match_result(idx, "2026-10-28", "Arsenal", "Chelsea", "")
    assert got == (2, 1, "2026-11-05"), got
    # Batas 45 hari: pertemuan 79 hari sesudah pick (putaran kedua)
    # TIDAK boleh menilai leg yang laganya dibatalkan.
    idx_far = {
        "2027-01-15": [(norm("Arsenal"), norm("Chelsea"), 1, 0,
                        "England - Premier League")],
    }
    assert _match_result(idx_far, "2026-10-28", "Arsenal",
                         "Chelsea", "") is None
    # Tepat di batas (45 hari) masih termasuk.
    idx_edge = {
        "2026-12-12": [(norm("Arsenal"), norm("Chelsea"), 4, 2,
                        "England - Premier League")],
    }
    assert _match_result(idx_edge, "2026-10-28", "Arsenal",
                         "Chelsea", "") == (4, 2, "2026-12-12")


def test_sim_containment_and_match_result_foreign_trap():
    # Ronde 15 (temuan saat verifikasi live): sim() memberi 0,88
    # untuk pasangan tak berhubungan karena token "b" (tim cadangan)
    # terkandung di nama lain — "augsburg" vs "wellington phoenix b".
    # Grader lalu menilai leg Bundesliga dari laga Selandia Baru
    # bertanggal sama (produk 0,774 >= ambang 0,75). Dua lapis fix:
    # containment menuntut kedua token >= 5 huruf, dan _match_result
    # menuntut sim per sisi >= 0,80.
    from grade_recommendations import _match_result, norm
    from ta_model import sim

    assert sim(norm("augsburg"), norm("wellington phoenix b")) < 0.5
    assert sim(norm("freiburg"), norm("auckland b")) < 0.5
    # containment yang sah tetap bekerja
    assert sim(norm("gladbach"), norm("monchengladbach")) >= 0.88
    assert sim(norm("inter"), norm("internazionale")) >= 0.88

    idx_trap = {"2026-10-31": [
        (norm("wellington phoenix b"), norm("auckland b"), 3, 2,
         "New Zealand - National League")]}
    assert _match_result(idx_trap, "2026-10-31", "augsburg",
                         "freiburg", "") is None
    idx_true = {"2026-10-31": [
        (norm("wellington phoenix b"), norm("auckland b"), 3, 2,
         "New Zealand - National League"),
        (norm("augsburg"), norm("freiburg"), 2, 1,
         "Germany - Bundesliga")]}
    assert _match_result(idx_true, "2026-10-31", "augsburg",
                         "freiburg", "") == (2, 1, "2026-10-31")
    # Lantai per sisi menambat secara independen: sim satu sisi
    # 0,78 (produk 0,78 >= 0,75) tetap ditolak karena sisi itu
    # di bawah 0,80 — pasangan timpang bukan laga yang sama.
    assert 0.70 < sim(norm("city rangers"),
                      norm("city wanderers")) < 0.80
    idx_weak = {"2026-10-31": [
        (norm("city wanderers"), norm("omega"), 2, 0, "X League")]}
    assert _match_result(idx_weak, "2026-10-31", "city rangers",
                         "omega", "") is None


def test_postponed_lookup_bounded():
    # Ronde 13: fallback laga tunda score_ledger memakai helper yang
    # sama-sama dibatasi 45 hari dan mengambil tanggal paling awal
    # setelah pick.
    from score_ledger import _postponed_lookup

    entries = [("2026-11-07", (2, 1)), ("2026-11-27", (0, 0)),
               ("2027-02-15", (3, 3))]
    assert _postponed_lookup(entries, "2026-10-28") == (2, 1)
    # Semua kandidat di luar jendela -> None (bukan putaran kedua).
    assert _postponed_lookup([("2027-02-15", (3, 3))],
                             "2026-10-28") is None
    # Tanggal pick sendiri dan sebelumnya tidak pernah dipakai.
    assert _postponed_lookup([("2026-10-28", (9, 9)),
                              ("2026-10-20", (8, 8))],
                             "2026-10-28") is None
    assert _postponed_lookup([], "2026-10-28") is None
    assert _postponed_lookup(None, "2026-10-28") is None


def test_missing_archive_dates():
    # C12-3/ronde 13: perhitungan tanggal arsip hilang diekstrak murni
    # dan nama folder non-tanggal disaring — satu folder asing tidak
    # boleh mematikan peringatan secara diam-diam.
    from datetime import date

    from grade_recommendations import (_is_date_name,
                                       _missing_archive_dates)

    assert _is_date_name("2026-10-31")
    assert not _is_date_name("notes")
    assert not _is_date_name("2026-13-01")
    assert _missing_archive_dates([], date(2026, 11, 2)) == []
    assert _missing_archive_dates(
        ["2026-10-29", "2026-10-31"], date(2026, 11, 2)) == ["2026-10-30"]
    # Folder terakhir di masa depan tidak memperluas rentang lampau
    # kemarin.
    assert _missing_archive_dates(
        ["2026-10-29", "2026-10-30"], date(2026, 10, 31)) == []


def test_regrade_orphans_settles_store_only_rows():
    # C15-1: leg/unit pending yang tidak ter-regenerasi arsip mana pun
    # (arsip rusak/tergenerasi ulang) harus dinilai dari store sebelum
    # prune sempat menghapusnya — kasus nyata: 13 leg 2026-10-30
    # (Elversberg/Lille/Villarreal) yang laganya sudah FT.
    import hashlib

    import grade_recommendations as gr

    def leg(product, home, away, market, line, sel, p, odds,
            date="2026-10-30", tier=""):
        g = {"date": date, "product": product, "level": "leg",
             "home": home, "away": away, "competition": "",
             "market": market, "line": line, "selection": sel,
             "p_model": p, "odds": odds, "tier": tier,
             "status": "pending", "score": "", "reason": "no_result_yet",
             "graded_at": "2026-10-30T01:00:00+00:00", "result_date": ""}
        return gr._key(g), g

    store = {}
    # 1: leg yatim, hasil ada (4-1, OU 2.5 Over -> hit)
    k1, g1 = leg("slip2", "elversberg", "mainz 05", "OU", "2.5",
                 "Over", 0.7422, 1.47)
    store[k1] = g1
    # 2: leg yatim, laga belum main -> tetap pending
    k2, g2 = leg("single", "future fc", "later united", "OU", "2.5",
                 "Over", 0.60, 1.90, date="2026-11-05")
    store[k2] = g2
    # 3: leg yang MASIH dihasilkan arsip (ada di seen) -> bukan urusan
    # proses ulang store; dibiarkan pending di sini
    k3, g3 = leg("slip2", "elversberg", "mainz 05", "DC", "",
                 "12", 0.7817, 1.27)
    store[k3] = g3
    # 4: leg corner yatim (pick_teraman), aktual HC/AC sudah ada:
    # total 11 vs Over 9.5 -> hit
    k4, g4 = leg("pick_teraman", "corner fc", "wing united", "Corners",
                 "9.5", "Over", 0.61, None)
    store[k4] = g4
    # 5: unit slip2 yatim dari dua leg yatim (satu hit, satu lose)
    k5a, g5a = leg("slip2", "alpha", "beta", "OU", "2.5", "Over",
                   0.70, 1.50)
    k5b, g5b = leg("slip2", "gamma", "delta", "1X2", "", "1",
                   0.60, 1.80)
    store[k5a] = g5a
    store[k5b] = g5b
    sig = ";".join(sorted("|".join(map(str, gr._key(g)))
                          for g in (g5a, g5b)))
    unit = {"date": "2026-10-30", "product": "slip2", "level": "unit",
            "home": "", "away": "", "competition": "", "market": "",
            "line": "",
            "selection": "unit:" + hashlib.md5(sig.encode()).hexdigest()[:12],
            "p_model": 0.42, "odds": 2.70, "tier": "",
            "status": "pending", "score": "", "reason": "legs_pending",
            "graded_at": "2026-10-30T01:00:00+00:00"}
    ku = gr._key(unit)
    store[ku] = unit
    # 6: unit yatim tanpa kecocokan hash -> tetap pending
    unit6 = dict(unit)
    unit6["selection"] = "unit:000000000000"
    unit6["p_model"] = 0.50
    k6 = gr._key(unit6)
    store[k6] = unit6

    res_idx = {"2026-10-30": [
        (gr.norm("elversberg"), gr.norm("mainz 05"), 4, 1, "x"),
        (gr.norm("alpha"), gr.norm("beta"), 3, 1, "x"),
        (gr.norm("gamma"), gr.norm("delta"), 0, 2, "x"),
    ]}
    cor_idx = {("2026-10-30", gr.norm("corner fc"),
                gr.norm("wing united")): 11}
    now = "2026-10-31T02:00:00+00:00"
    changed = gr._regrade_orphans(store, {k3}, res_idx, cor_idx, now)

    assert store[k1]["status"] == "hit", store[k1]
    assert store[k1]["score"] == "4-1"
    assert store[k1]["result_date"] == "2026-10-30"
    assert store[k2]["status"] == "pending"
    assert store[k3]["status"] == "pending"  # seen: tidak disentuh
    assert store[k4]["status"] == "hit" and store[k4]["score"] == "11"
    assert store[k5a]["status"] == "hit"
    assert store[k5b]["status"] == "lose"
    assert store[ku]["status"] == "lose", store[ku]  # satu leg kalah
    assert store[k6]["status"] == "pending"
    assert changed == 5, changed  # k1, k4, k5a, k5b, unit


def test_archive_unit_recovered_by_regrade():
    # L4 audit-diri ronde 15: format sig unit ditulis di DUA fungsi
    # (_grade_archive yang memproduksi, _regrade_orphans yang
    # memulihkan) — tes ini menambat keduanya bersama: unit yang
    # diproduksi jalur arsip harus bisa dipulihkan jalur store,
    # kalau tidak pemulihan akan gagal senyap selamanya. Sekalian
    # menambat jendela L1: satu leg jatuh di tanggal unit + 4 hari
    # (ekspansi penuh S10_MAX_EXPAND_DAYS).
    import csv
    import shutil
    import tempfile

    import grade_recommendations as gr

    td = tempfile.mkdtemp()
    saved = gr.ARCHIVE
    try:
        arc = os.path.join(td, "archive", "2026-10-30")
        os.makedirs(arc)
        with open(os.path.join(arc, "recommended_slip10.csv"), "w",
                  newline="") as f:
            w = csv.writer(f)
            w.writerow(["date", "home", "away", "competition",
                        "market", "line", "selection", "o_1xbet",
                        "p_model", "slip_total_odds",
                        "slip_joint_prob"])
            w.writerow(["2026-10-30", "alpha", "beta", "", "OU",
                        "2.5", "Over", 1.50, 0.70, 3.99, 0.2503])
            w.writerow(["2026-10-31", "gamma", "delta", "", "DC",
                        "", "1X", 1.40, 0.65, 3.99, 0.2503])
            w.writerow(["2026-11-03", "epsilon", "zeta", "", "1X2",
                        "", "1", 1.90, 0.55, 3.99, 0.2503])
        gr.ARCHIVE = os.path.join(td, "archive")
        store = {}
        now = "2026-10-30T12:00:00+00:00"
        # run 1: hasil belum ada -> leg + unit pending
        gr._grade_archive("2026-10-30", store, {}, {}, now, set())
        units = [g for g in store.values() if g["level"] == "unit"]
        assert len(store) == 4 and len(units) == 1, store
        assert all(g["status"] == "pending" for g in store.values())
        # run 2: arsip "rusak" (seen kosong), hasil sudah ada ->
        # proses ulang store memulihkan leg DAN unit produksi arsip
        res_idx = {
            "2026-10-30": [(gr.norm("alpha"), gr.norm("beta"),
                            3, 1, "x")],
            "2026-10-31": [(gr.norm("gamma"), gr.norm("delta"),
                            1, 1, "x")],
            "2026-11-03": [(gr.norm("epsilon"), gr.norm("zeta"),
                            2, 0, "x")],
        }
        changed = gr._regrade_orphans(store, set(), res_idx, {}, now)
        assert changed == 4, changed
        assert all(g["status"] == "hit" for g in store.values()), store
    finally:
        gr.ARCHIVE = saved
        shutil.rmtree(td, ignore_errors=True)


def test_merge_bets_refreshes_open_rows_only():
    # Ronde 13 (MEDIUM siklus hidup best_bets): bet_id yang terbit
    # lagi memperbarui baris OPEN-nya; baris settle tidak berubah;
    # bet baru ditambahkan.
    from ta_model import _merge_bets

    def winner(gid, pm, price, ev):
        return {"game_id": gid, "date": "2026-11-05", "home": "H",
                "away": "A", "market": "OU", "line": "2.5",
                "selection": "Over", "book_best": "book",
                "odds_best": price, "p_model": pm, "p_market": 0.40,
                "ev_shrunk": ev, "tier": "aman"}

    old = {
        "1|OU|2.5|Over": {"bet_id": "1|OU|2.5|Over", "status": "OPEN",
                          "created_at": "T0", "price": 9.99,
                          "kickoff_utc": "2026-11-01T18:00",
                          "p_model": 0.1111, "p_market": 0.40,
                          "ev": 0.01, "tier": "lama", "bookmaker": "x"},
        "2|OU|2.5|Over": {"bet_id": "2|OU|2.5|Over", "status": "SETTLED",
                          "created_at": "T0", "price": 2.50,
                          "kickoff_utc": "2026-11-01T18:00",
                          "p_model": 0.5000, "p_market": 0.40,
                          "ev": 0.05, "tier": "lama", "bookmaker": "x"},
    }
    fixtures = {g: {"time": "20:00", "league": "L"} for g in "123"}
    rows, n_new, n_ref = _merge_bets(
        old, [winner("1", 0.61, 2.10, 0.20), winner("2", 0.62, 2.20, 0.30),
              winner("3", 0.63, 2.30, 0.40)], fixtures, "T1")
    assert (n_new, n_ref) == (1, 1), (n_new, n_ref)
    by_id = {r["bet_id"]: r for r in rows}
    r1 = by_id["1|OU|2.5|Over"]
    assert r1["p_model"] == 0.61 and r1["price"] == 2.10, r1
    assert r1["created_at"] == "T0", r1  # tanggal buat dipertahankan
    # L13-3: kickoff ikut diperbarui (laga bisa saja ditunda)
    assert r1["kickoff_utc"] == "2026-11-05T20:00", r1
    r2 = by_id["2|OU|2.5|Over"]
    assert r2["p_model"] == 0.5000 and r2["price"] == 2.50, r2
    assert r2["kickoff_utc"] == "2026-11-01T18:00", r2
    assert by_id["3|OU|2.5|Over"]["status"] == "OPEN"


def _undefined_names(path):
    """Nama yang dirujuk di dalam fungsi/kelas tetapi tidak terikat
    di mana pun: bukan lokal/parameter/impor di lingkupnya, bukan
    nama bebas (closure), bukan terikat di level modul, bukan
    builtin. Inilah kelas bug H13-1 (NameError dtf di loader corner):
    nama yatim yang hanya meledak saat jalur file-driven dijalankan,
    tak terlihat oleh tes yang hanya menguji predikatnya."""
    import builtins
    import symtable

    with open(path, encoding="utf-8") as f:
        code = f.read()
    top = symtable.symtable(code, path, "exec")
    module_bound = {s.get_name() for s in top.get_symbols()
                    if s.is_assigned() or s.is_imported()
                    or s.is_namespace()}
    builtin_names = set(dir(builtins)) | {
        "__file__", "__name__", "__doc__", "__package__", "__loader__",
        "__spec__", "__builtins__", "__annotations__", "__cached__"}
    bad = []

    def walk(table):
        for child in table.get_children():
            if child.get_type() in ("function", "class"):
                for s in child.get_symbols():
                    if not s.is_referenced():
                        continue
                    if (s.is_assigned() or s.is_parameter()
                            or s.is_imported() or s.is_free()):
                        continue
                    name = s.get_name()
                    if name in module_bound or name in builtin_names:
                        continue
                    bad.append(f"{child.get_name()}:{name}")
            walk(child)

    walk(top)
    return bad


def test_no_undefined_names_in_chain_modules():
    # D14-2: sapuan symtable stdlib untuk modul-modul rantai harian —
    # jaring murah bagi kelas bug nama-yatim yang lolos dari seluruh
    # suite di ronde 13 (mutasi H13-1 yang dibuat ulang terdeteksi
    # persis sebagai predict_upcoming:dtf saat audit ronde 14).
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mods = ["run_daily_shadow.py", "ta_model.py", "best_picks.py",
            "grade_recommendations.py", "score_ledger.py",
            "slip_recommender.py", "model_corners_v3.py",
            "predict_cups.py", "refresh_fixtures.py", "ta_scrape.py",
            "market_orchestration.py", "make_picks_live.py",
            "predict_upcoming_refactored.py",
            # F8 ronde 15: modul langkah [16/16] sendiri tadinya
            # terlewat dari daftar ini.
            "resolve_and_monitor.py"]
    for m in mods:
        bad = _undefined_names(os.path.join(root, m))
        assert not bad, (m, bad)


def test_undefined_names_helper_detects_orphans():
    # D15-2: sweep tanpa positive control bisa hijau vakum — bila
    # helper-nya rusak senyap (API symtable berubah, bug walk), tes
    # rantai di atas lolos dengan daftar kosong. Paksa helper
    # membuktikan ia MENANGKAP nama yatim yang diketahui, dan tidak
    # menandai kode yang bersih.
    import shutil
    import tempfile

    td = tempfile.mkdtemp()
    try:
        bad = os.path.join(td, "bad.py")
        with open(bad, "w") as f:
            f.write("def loader():\n    return dtf + 1\n")
        assert _undefined_names(bad) == ["loader:dtf"]
        good = os.path.join(td, "good.py")
        with open(good, "w") as f:
            f.write("import os\n\ndef ok():\n    x = os.sep\n"
                    "    return x\n")
        assert _undefined_names(good) == []
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_kickoff_started_predicate():
    # B14-1: predikat jangkar datetime best_picks.
    from datetime import datetime

    from best_picks import _kickoff_started

    now = datetime(2026, 10, 30, 20, 7)
    assert _kickoff_started("2026-10-30", "20:05", now) is True
    assert _kickoff_started("2026-10-30", "20:07", now) is True  # tepat kini
    assert _kickoff_started("2026-10-30", "20:09", now) is False
    assert _kickoff_started("2026-10-30", "", now) is False      # tanpa jam
    assert _kickoff_started("2026-10-30", "xx", now) is False    # jam rusak
    assert _kickoff_started("2026-10-31", "00:05", now) is False


def test_best_picks_main_skips_started_matches():
    # B14-1 integrasi: main() tidak menyajikan pick untuk laga yang
    # sudah kickoff — baik di best_picks.csv (loader DC) maupun di
    # best_picks_today.csv (jalur pindai); baris hari ini untuk laga
    # itu kosong, kontrak satu baris per laga tetap terjaga.
    import shutil
    import tempfile
    from datetime import datetime, timedelta, timezone

    import best_picks as bp

    now = datetime.now(timezone.utc)
    today = now.date().isoformat()
    # Jepit jam agar tak menyeberang tengah malam UTC (jendela lemah
    # yang sama dengan tes loader TA ronde 13).
    started = ("00:00" if now.hour < 3
               else (now - timedelta(hours=2)).strftime("%H:%M"))
    future = ("23:59" if now.hour >= 22
              else (now + timedelta(hours=2)).strftime("%H:%M"))
    hdr = ("div,date,time,home,away,lam_h,lam_a,ph_dc,pd_dc,pa_dc,"
           "p_over_dc,p_over15_dc,p_over35_dc,p_btts,p_dc_1x,p_dc_x2,"
           "p_dc_12,b365h,b365d,b365a\n")
    row = ("E0,{d},{t},{h},Rival,1.5,1.0,0.70,0.20,0.10,0.60,0.85,"
           "0.30,0.40,0.90,0.30,0.80,2.0,3.5,5.0\n")
    td = tempfile.mkdtemp()
    saved = (bp.PROJ, bp.OUT, bp.ANCHOR)
    try:
        bp.PROJ = td
        bp.OUT = os.path.join(td, "best_picks.csv")
        with open(os.path.join(td, "predictions_upcoming.csv"), "w") as f:
            f.write(hdr)
            f.write(row.format(d=today, t=started, h="Started FC"))
            f.write(row.format(d=today, t=future, h="Future FC"))
        # Baris corner untuk kedua laga (L-3 audit-diri): pick corner
        # hanya dilindungi filter terpusat started_keys di main() —
        # file corner tak punya kolom jam — jadi jalur itu harus ikut
        # teruji, bukan hanya loader DC.
        chdr = ("div,date,home,away,mu_shots_cs,r_cs,rec_line,rec_side,"
                "recommendation,rec_prob,p_gt_6.5,p_gt_7.5,p_gt_8.5,"
                "p_gt_9.5,p_gt_10.5,p_gt_11.5\n")
        crow = ("E0,{d},{h},Rival,10.0,2.5,8.5,Over,x,0.70,0.90,0.80,"
                "0.70,0.50,0.40,0.30\n")
        with open(os.path.join(td, "predictions_corners_upcoming.csv"),
                  "w") as f:
            f.write(chdr)
            f.write(crow.format(d=today, h="Started FC"))
            f.write(crow.format(d=today, h="Future FC"))
        argv = sys.argv
        sys.argv = ["best_picks.py", "--date", today]
        try:
            bp.main()
        finally:
            sys.argv = argv
        tops = bp._read_csv(os.path.join(td, "best_picks.csv"))
        assert [r["home"] for r in tops] == ["Future FC"], tops
        full = bp._read_csv(os.path.join(td, "best_picks_full.csv"))
        assert all(r["home"] != "Started FC" for r in full), full
        assert any(r["home"] == "Future FC" and r["market"] == "Corners"
                   for r in full), full
        today_rows = bp._read_csv(os.path.join(td, "best_picks_today.csv"))
        assert len(today_rows) == 2, today_rows
        by_home = {r["home"]: r for r in today_rows}
        assert by_home["Started FC"]["market"] == "", by_home["Started FC"]
        assert by_home["Future FC"]["market"] != "", by_home["Future FC"]
    finally:
        bp.PROJ, bp.OUT, bp.ANCHOR = saved
        shutil.rmtree(td, ignore_errors=True)


def test_archive_snapshots_write_once():
    # C14-1: arsip adalah snapshot pra-kickoff untuk grading; rerun
    # pasca-kickoff tidak boleh menimpanya (leg laga yang sudah main
    # lenyap dari snapshot -> tak ter-generate -> ter-pangkas yatim
    # tanpa dinilai). File yang hilang tetap dilengkapi.
    import shutil
    import tempfile
    from datetime import date

    import market_orchestration as mo

    td = tempfile.mkdtemp()
    try:
        src = os.path.join(td, "src")
        arc = os.path.join(td, "archive")
        os.makedirs(src)
        f1, f2 = mo.ARCHIVE_FILES[0], mo.ARCHIVE_FILES[1]
        with open(os.path.join(src, f1), "w") as f:
            f.write("h\nprematch\n")
        with open(os.path.join(src, f2), "w") as f:
            f.write("h\nv1\n")
        saved = (mo.HERE, mo.ARCHIVE)
        mo.HERE, mo.ARCHIVE = src, arc
        try:
            r1 = mo.archive_snapshots(target_date=date(2026, 10, 30))
            assert sorted(r1["archived"]) == sorted([f1, f2]), r1
            # sumber berubah (output pasca-kickoff) + satu file hilang
            with open(os.path.join(src, f1), "w") as f:
                f.write("h\npostkickoff\n")
            dest = os.path.join(arc, "2026-10-30")
            os.remove(os.path.join(dest, f2))
            r2 = mo.archive_snapshots(target_date=date(2026, 10, 30))
            assert r2["archived"] == [f2], r2      # hanya yang hilang
            assert r2["kept"] == [f1], r2
            with open(os.path.join(dest, f1)) as f:
                assert f.read() == "h\nprematch\n"  # tak tertimpa
            # L-2: arsip berisi header saja (run pertama terdegradasi)
            # boleh diperbaiki sumber yang punya baris data
            with open(os.path.join(dest, f2), "w") as f:
                f.write("h\n")
            with open(os.path.join(src, f2), "w") as f:
                f.write("h\nv2\n")
            r3 = mo.archive_snapshots(target_date=date(2026, 10, 30))
            assert r3["archived"] == [f2], r3
            assert r3["kept"] == [f1], r3
            with open(os.path.join(dest, f2)) as f:
                assert f.read() == "h\nv2\n"
        finally:
            mo.HERE, mo.ARCHIVE = saved
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_unit_recovery_fast_in_dense_window():
    # A16-1: pencarian subset versi enumerasi-penuh menghabiskan
    # 52,6 dtk untuk SATU unit tak-pulih di jendela 40 kandidat,
    # dibayar setiap run. Jendela padat yang sama kini harus
    # selesai jauh di bawah 2 dtk, unit yang bisa pulih tetap
    # pulih (termasuk lewat jalur hash-murni saat angka unit
    # tidak lengkap), dan unit tak-pulih tetap pending.
    import hashlib as _hl
    import time as _time

    from grade_recommendations import _key, _regrade_orphans

    def leg(i, status="pending"):
        return {"date": "2026-10-30", "product": "slip10",
                "level": "leg", "home": f"team{i}", "away": f"opp{i}",
                "competition": "", "market": "OU", "line": "2.5",
                "selection": "Over", "p_model": 0.35 + 0.005 * i,
                "odds": 1.31 + 0.037 * i, "tier": "",
                "status": status, "score": "", "reason": "no_result_yet",
                "graded_at": "", "result_date": ""}

    def unit_for(members, odds_mult=1.0, p_mult=1.0, blank_numbers=False):
        sig = ";".join(sorted("|".join(map(str, _key(m))) for m in members))
        o = p = 1.0
        for m in members:
            o *= m["odds"]
            p *= m["p_model"]
        return {"date": "2026-10-30", "product": "slip10",
                "level": "unit", "home": "", "away": "",
                "competition": "", "market": "", "line": "",
                "selection": "unit:" + _hl.md5(sig.encode()).hexdigest()[:12],
                "p_model": None if blank_numbers else round(p * p_mult, 4),
                "odds": None if blank_numbers else round(o * odds_mult, 3),
                "tier": "", "status": "pending", "score": "",
                "reason": "legs_pending", "graded_at": ""}

    store = {}
    legs = [leg(i) for i in range(40)]
    # unit pulih-1: leg 10..12, sudah final -> settle dari status leg
    for i in (10, 11, 12):
        legs[i]["status"] = "hit"
    u1 = unit_for([legs[10], legs[11], legs[12]])
    # unit pulih-2: angka unit kosong -> jalur hash murni
    for i in (30, 31):
        legs[i]["status"] = "lose"
    u2 = unit_for([legs[30], legs[31]], blank_numbers=True)
    # unit tak-pulih: sidik untuk leg yang tidak ada di store
    # (angka unit masuk akal: total ±5,8, joint ±0,125)
    ghost = []
    for j in range(3):
        g = leg(900 + j)
        g["home"], g["away"] = f"ghost{j}", f"phantom{j}"
        g["odds"], g["p_model"] = 1.80, 0.50
        ghost.append(g)
    u3 = unit_for(ghost)
    for g in legs + [u1, u2, u3]:
        store[_key(g)] = g

    t0 = _time.monotonic()
    _regrade_orphans(store, set(), {}, {}, "2026-10-31T00:00:00+00:00")
    elapsed = _time.monotonic() - t0
    assert store[_key(u1)]["status"] == "hit", store[_key(u1)]
    assert store[_key(u2)]["status"] == "lose", store[_key(u2)]
    assert store[_key(u3)]["status"] == "pending", store[_key(u3)]
    assert elapsed < 2.0, f"pemulihan unit lambat: {elapsed:.2f} dtk"


def test_archive_skips_wrong_generation_and_blank_rows():
    # Ronde 15. F5: "berdata" dinilai dari sel, bukan baris fisik —
    # header + baris kosong BUKAN data, jadi tetap bisa di-repair.
    # C15-2: file produk generasi tanggal lain tidak diarsipkan ke
    # folder ini (arsip 2026-10-30 nyata memuat slip10 berisi leg
    # 2026-10-31).
    import shutil
    import tempfile
    from datetime import date

    import market_orchestration as mo

    # _has_data_rows langsung
    td0 = tempfile.mkdtemp()
    try:
        p = os.path.join(td0, "x.csv")
        with open(p, "w") as f:
            f.write("h\n\n")
        assert mo._has_data_rows(p) is False
        with open(p, "w") as f:
            f.write("h\n   \n")
        assert mo._has_data_rows(p) is False
        with open(p, "w") as f:
            f.write("")
        assert mo._has_data_rows(p) is False
        with open(p, "w") as f:
            f.write("h\ndata\n")
        assert mo._has_data_rows(p) is True
    finally:
        shutil.rmtree(td0, ignore_errors=True)

    td = tempfile.mkdtemp()
    try:
        src = os.path.join(td, "src")
        arc = os.path.join(td, "archive")
        os.makedirs(src)
        dest = os.path.join(arc, "2026-10-30")
        os.makedirs(dest)
        f_pred = mo.ARCHIVE_FILES[0]  # predictions_upcoming.csv
        # dest berisi header + baris kosong -> bukan data -> repair
        with open(os.path.join(dest, f_pred), "w") as f:
            f.write("h\n\n")
        with open(os.path.join(src, f_pred), "w") as f:
            f.write("h\nreal\n")
        # slip10 generasi BESOK: semua leg 2026-10-31 -> dilewati
        with open(os.path.join(src, "recommended_slip10.csv"), "w") as f:
            f.write("date,home\n2026-10-31,besok fc\n")
        # slip2 tanggal cocok -> diarsipkan
        with open(os.path.join(src, "recommended_slip.csv"), "w") as f:
            f.write("date,home\n2026-10-30,hari ini fc\n")
        # best_picks_today bercampur tanggal lain -> dilewati
        with open(os.path.join(src, "best_picks_today.csv"), "w") as f:
            f.write("date,home\n2026-10-30,a\n2026-10-31,b\n")
        saved = (mo.HERE, mo.ARCHIVE)
        mo.HERE, mo.ARCHIVE = src, arc
        try:
            r = mo.archive_snapshots(target_date=date(2026, 10, 30))
        finally:
            mo.HERE, mo.ARCHIVE = saved
        assert f_pred in r["archived"], r
        with open(os.path.join(dest, f_pred)) as f:
            assert f.read() == "h\nreal\n"
        assert "recommended_slip10.csv" in r["skipped"], r
        assert not os.path.exists(
            os.path.join(dest, "recommended_slip10.csv"))
        assert "recommended_slip.csv" in r["archived"], r
        assert "best_picks_today.csv" in r["skipped"], r
        assert not os.path.exists(
            os.path.join(dest, "best_picks_today.csv"))
        # L5 audit-diri ronde 15: sisi TERIMA penjaga — slip10
        # ekspansi yang sah (leg di tanggal folder + hari
        # berikutnya) harus tetap diarsipkan.
        with open(os.path.join(src, "recommended_slip10.csv"),
                  "w") as f:
            f.write("date,home\n2026-10-31,hari ini fc\n"
                    "2026-11-01,besok fc\n")
        saved = (mo.HERE, mo.ARCHIVE)
        mo.HERE, mo.ARCHIVE = src, arc
        try:
            r2 = mo.archive_snapshots(target_date=date(2026, 10, 31))
        finally:
            mo.HERE, mo.ARCHIVE = saved
        assert "recommended_slip10.csv" in r2["archived"], r2
        assert os.path.exists(os.path.join(
            arc, "2026-10-31", "recommended_slip10.csv"))
    finally:
        shutil.rmtree(td, ignore_errors=True)


def test_archive_helpers_tolerate_non_utf8():
    # D16-3: tangkapan UnicodeDecodeError di kedua pembaca arsip
    # (lipatan L3 ronde 15) tidak punya tambat tes — mutasi yang
    # membuangnya tetap hijau. File latin-1 harus diperlakukan
    # tak-berdata / tanpa vonis, bukan meledak.
    import tempfile

    import market_orchestration as mo

    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "recommended_slip.csv")
        with open(p, "wb") as f:
            f.write("date,home,away\r\n2026-10-30,Montréal,Real\r\n"
                    .encode("latin-1"))
        assert mo._has_data_rows(p) is False
        assert mo._product_date_mismatch(p, "2026-10-31") is False


def test_purge_bogus_spares_issued_and_settled_rows():
    # Audit-diri ronde 13: purge harga mustahil tidak boleh membuang
    # baris yang build saat ini terbitkan sendiri (produk > 1,02 di
    # sana = ketidaksepakatan model-pasar yang sah; membuangnya
    # membuat build berikutnya menerbitkan ulang — churn abadi) dan
    # tidak boleh menyentuh riwayat settle.
    from datetime import datetime

    from ta_model import _purge_bogus

    def row(bid, status, price, pmkt, ko):
        return {"bet_id": bid, "status": status, "price": price,
                "p_market": pmkt, "kickoff_utc": ko}

    now = datetime(2026, 10, 31, 12, 0)
    rows = [
        # 1,08, kickoff lewat > 2 hari, bukan terbitan kini: dibuang
        row("a", "OPEN", 4.50, 0.24, "2026-10-28T20:00"),
        # 1,08 tapi diterbitkan build ini -> disimpan
        row("b", "OPEN", 4.50, 0.24, "2026-10-28T20:00"),
        # riwayat settle -> tak pernah dibuang
        row("c", "SETTLED", 4.50, 0.24, "2026-10-28T20:00"),
        # 0,80: wajar
        row("d", "OPEN", 2.00, 0.40, "2026-10-28T20:00"),
        # A14-1: 1,08, berhenti diterbitkan ulang, tapi kickoff masih
        # di masa depan -> posisi masih bisa dinilai, disimpan
        row("e", "OPEN", 4.50, 0.24, "2026-11-05T20:00"),
        # kickoff tak ter-parse -> tanpa pengecualian, dibuang
        row("f", "OPEN", 4.50, 0.24, ""),
        # L-1 audit-diri: kickoff baru lewat 16 jam — hasil mungkin
        # belum tersinkron, grading belum sempat terjadi -> tenggang
        # 2 hari menyimpannya
        row("g", "OPEN", 4.50, 0.24, "2026-10-30T20:00"),
        # F1 ronde 15: price non-numerik -> korup, dibuang (dulu
        # TypeError dan build mati)
        row("h", "OPEN", "", 0.24, "2026-11-05T20:00"),
        # F2 ronde 15: kickoff jauh di masa depan (> 14 hari) tidak
        # memberi pengecualian tenggang -> dibuang
        row("i", "OPEN", 4.50, 0.24, "2027-06-01T20:00"),
        # D15-1 ronde 15: tambat tenggang PERSIS 2 hari — 47 jam
        # yang lalu masih di dalam tenggang (disimpan), 49 jam
        # sudah di luar (dibuang). Apitan lama hanya 16 vs 64 jam,
        # sehingga regresi tenggang ke 1 hari lolos tak tertangkap.
        row("j", "OPEN", 4.50, 0.24, "2026-10-29T13:00"),
        row("k", "OPEN", 4.50, 0.24, "2026-10-29T11:00"),
        # L5 audit-diri ronde 15: tambat batas horizon PERSIS —
        # tepat now+14 hari masih terlindungi, semenit sesudahnya
        # tidak.
        row("l", "OPEN", 4.50, 0.24, "2026-11-14T12:00"),
        row("m", "OPEN", 4.50, 0.24, "2026-11-14T12:01"),
    ]
    kept, n = _purge_bogus(rows, {"b"}, now)
    assert n == 6, n
    assert [r["bet_id"] for r in kept] == ["b", "c", "d", "e", "g",
                                           "j", "l"], kept


def test_build_end_to_end_sandbox():
    # Titik buta teratas grup D ronde 15: build() tidak pernah
    # dipanggil suite — hanya unit-unitnya. Sandbox TA/PRED temporer:
    # (1) fixtures kosong -> rc 1 dan model_markets tidak ditulis;
    # (2) best_bets lama berisi baris OPEN korup non-numerik ->
    # build TIDAK crash (F1 di jalur nyata) dan baris korup
    # ter-purge dari file hasil, baris sehat bertahan.
    import csv
    import shutil
    import tempfile

    import ta_model as tm

    td = tempfile.mkdtemp()
    saved = (tm.TA, tm.PRED)
    try:
        ta = os.path.join(td, "ta")
        os.makedirs(ta)
        pred = os.path.join(td, "preds.csv")
        tm.TA, tm.PRED = ta, pred
        with open(os.path.join(ta, "fixtures.csv"), "w") as f:
            f.write("game_id,date,time,home,away,league\n")
        with open(pred, "w") as f:
            f.write("div,date,home,away,lam_h,lam_a,ph_dc,pd_dc,pa_dc\n")
        assert tm.build() == 1
        assert not os.path.exists(os.path.join(ta, "model_markets.csv"))

        with open(os.path.join(ta, "fixtures.csv"), "w") as f:
            f.write("game_id,date,time,home,away,league\n")
            f.write("999,2027-06-01,20:00,Alpha,Beta,Test League\n")
        with open(pred, "w") as f:
            f.write("div,date,home,away,lam_h,lam_a,ph_dc,pd_dc,pa_dc\n")
            f.write("E0,2027-06-01,Alpha,Beta,1.5,1.0,0.45,0.28,0.27\n")
        base = {c: "" for c in tm.BET_COLS}
        with open(os.path.join(ta, "best_bets.csv"), "w",
                  newline="") as f:
            w = csv.DictWriter(f, fieldnames=tm.BET_COLS)
            w.writeheader()
            w.writerow(dict(base, bet_id="1|OU|2.5|Over",
                            game_id="1", status="OPEN", price="",
                            p_market="",
                            kickoff_utc="2027-06-01T20:00"))
            w.writerow(dict(base, bet_id="2|OU|2.5|Over",
                            game_id="2", status="OPEN", price="2.00",
                            p_market="0.40",
                            kickoff_utc="2027-06-01T20:00"))
        assert tm.build() == 0
        rows = tm.read_csv(os.path.join(ta, "best_bets.csv"))
        assert [r["bet_id"] for r in rows] == ["2|OU|2.5|Over"], rows
    finally:
        tm.TA, tm.PRED = saved
        shutil.rmtree(td, ignore_errors=True)


def test_best_picks_ta_loader_skips_started_matches():
    # Ronde 13: loader TA best_picks berjangkar datetime penuh —
    # bet laga yang sudah kickoff hari ini tidak boleh masuk
    # peringkat (kasus Le Havre–PSG: tanggal sama, laga berjalan).
    # Nilai peringkat (prob/EV) diambil dari model_markets TERKINI,
    # bukan dari baris bet tersimpan: baris bet di bawah sengaja
    # membawa p_model basi 0,99 — yang boleh lolos hanya nilai
    # berjalan 0,60/0,50. Bet tanpa baris pasar berjalan jatuh ke
    # nilai tersimpan (di sini EV tersimpan 0 -> tetap tersaring).
    import csv
    import tempfile
    from datetime import datetime, timedelta, timezone

    import best_picks as bp

    now = datetime.now(timezone.utc)

    def row(gid, kickoff, status="OPEN", ev="9.99"):
        return {"game_id": gid, "status": status, "kickoff_utc": kickoff,
                "league": "Spain - Primera Division", "home": "A",
                "away": "B", "market": "OU", "line": "2.5",
                "selection": "Over", "ev": ev, "p_model": "0.99",
                "p_market": "0.01"}

    def mrow(gid, pm="0.60", pmkt="0.50", ev="0.10"):
        return {"game_id": gid, "market": "OU", "line": "2.5",
                "selection": "Over", "p_model": pm, "p_market": pmkt,
                "ev_shrunk": ev}

    fmt = "%Y-%m-%dT%H:%M"
    rows = [
        row("1", (now - timedelta(hours=1)).strftime(fmt)),  # sudah mulai
        row("2", (now + timedelta(hours=3)).strftime(fmt)),  # lolos
        row("3", (now + timedelta(hours=5)).strftime(fmt), status="SETTLED"),
        row("4", (now + timedelta(hours=6)).strftime(fmt), ev="0"),
    ]
    mrows = [mrow("1"), mrow("2"), mrow("3")]
    with tempfile.TemporaryDirectory() as td:
        os.makedirs(os.path.join(td, "ta"))
        with open(os.path.join(td, "ta", "best_bets.csv"), "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        with open(os.path.join(td, "ta", "model_markets.csv"), "w",
                  newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=list(mrows[0].keys()))
            w.writeheader()
            w.writerows(mrows)
        old_proj, old_anchor = bp.PROJ, bp.ANCHOR
        bp.PROJ = td
        bp.ANCHOR = now.date().isoformat()
        try:
            picks = bp._load_ta_picks()
        finally:
            bp.PROJ, bp.ANCHOR = old_proj, old_anchor
    assert len(picks) == 1, picks
    assert picks[0]["source"] == "ta_model"
    assert picks[0]["prob"] == 0.55, picks  # tersusut 0.5*0.60+0.5*0.50
    assert picks[0]["ev"] == 0.10, picks    # EV berjalan, bukan 9,99 basi


def test_prematch_kickoff_predicates():
    # D12-10/ronde 13: predikat filter prematch piala + corner liga
    # diekstrak dari loader supaya teruji unit (wilayah kode ini
    # menghasilkan temuan di dua ronde audit berurutan).
    from datetime import date, datetime

    from model_corners_v3 import _kickoff_in_future
    from predict_cups import _fixture_still_open

    now = datetime(2026, 10, 31, 19, 0)
    d = date(2026, 10, 31)
    assert _fixture_still_open(d, "20:00", now) is True
    assert _fixture_still_open(d, "18:00", now) is False
    assert _fixture_still_open(d, "19:00", now) is False  # tepat kickoff
    assert _fixture_still_open(d, "", now) is True        # jam kosong
    assert _fixture_still_open(d, "xx", now) is True      # jam rusak
    assert _fixture_still_open(d, None, now) is True

    assert _kickoff_in_future(datetime(2026, 10, 31, 20, 0), now) is True
    assert _kickoff_in_future(datetime(2026, 10, 31, 18, 0), now) is False
    assert _kickoff_in_future(datetime(2026, 10, 31, 19, 0), now) is False


def test_slip_search_large_pool_matches_brute_force():
    # Ronde 13 (MEDIUM celah tes): tes properti B12-2 yang lama memakai
    # pool 6 laga — DFS lama pun mengembalikan optimum di pool sekecil
    # itu, jadi tesnya tidak bisa gagal oleh cacat pemotongan aslinya.
    # Tes ini memakai kelas ukuran slate yang mematahkan DFS lama
    # (23 laga / 142 leg; slate riil 2026-10-31: 23 laga / 136 leg,
    # DFS lama terpotong di 200 ribu node dengan joint 0,6061 vs
    # optimum 0,6350) dan menambatkan: (1) optimum branch-and-bound ==
    # enumerasi independen yang hanya memakai pruning legalitas pita,
    # (2) pencarian selesai TIDAK terpotong dengan node jauh di bawah
    # anggaran lama 200 ribu.
    import random

    from slip_recommender import _search

    rng = random.Random(20261031)
    by_match = {}
    for mi in range(23):
        legs = []
        for _k in range(rng.randint(5, 7)):
            o = round(rng.uniform(1.25, 3.10), 2)
            pm = round(rng.uniform(0.45, 0.88), 3)
            legs.append(_leg(f"M{mi}", "2026-10-31", o, pm))
        by_match[f"M{mi}"] = legs

    stats = {}
    best_in, _near = _search(by_match, 2, 4, 1.85, 2.15, 2.0, stats)
    assert best_in is not None
    assert stats["truncated"] is False, stats
    assert stats["nodes"] < 200_000, stats

    keys = list(by_match)
    ref = [None]

    def rec(i, tot, jp, nlegs):
        if tot > 2.15:
            return
        if nlegs >= 2 and tot >= 1.85:
            if ref[0] is None or jp > ref[0]:
                ref[0] = jp
        if i == len(keys) or nlegs == 4:
            return
        rec(i + 1, tot, jp, nlegs)
        for l in by_match[keys[i]]:
            rec(i + 1, tot * l["o"], jp * l["pm"], nlegs + 1)

    rec(0, 1.0, 1.0, 0)
    assert ref[0] is not None
    assert abs(best_in[1] - ref[0]) < 1e-9, (best_in[1], ref[0])


def _shadow_env(pred_status):
    """Stub semua langkah run_daily_shadow untuk tes gerbang.

    Mengembalikan (modul shadow, daftar panggilan tercatat, restore).
    Pola stub sys.modules yang sama dengan _refresh_env.
    """
    import types

    import run_daily_shadow as sh

    calls = []

    def rec(name):
        def f(*a, **k):
            calls.append(name)
        return f

    saved = {}

    def stub(name, **attrs):
        saved[name] = sys.modules.get(name)
        m = types.ModuleType(name)
        for k, v in attrs.items():
            setattr(m, k, v)
        sys.modules[name] = m

    stub("predict_upcoming_refactored",
         generate_predictions=lambda: calls.append("pred") or
         {"status": pred_status, "n_output_rows": 10})
    stub("predict_cups",
         main=lambda: {"n_gol": 0, "n_corner": 0, "status": "ok"})
    stub("make_picks_live", main=lambda: calls.append("picks") or 0)
    stub("ta_model", grade=rec("ta_grade"),
         build=lambda: calls.append("ta_build") or 0)
    stub("ta_scrape", sync_dates=lambda *a, **k: {"markets": 0})
    stub("market_orchestration",
         model_fixture_ids=lambda days: calls.append("mkt_ids") or [],
         build_market_compare=lambda: calls.append("mkt_cmp") or
         {"fixtures": 0, "rows": 0},
         archive_snapshots=lambda: calls.append("archive") or
         {"date": "2026-10-31", "archived": []},
         sync_cup_picks_to_ledger=lambda: calls.append("cup_ledger") or 0)
    stub("slip_recommender",
         recommend=lambda: calls.append("recommend") or {
             "single": {"pick": "x", "ev": 0},
             "slip2": {"n_legs": 0, "total_odds": 0, "in_band": False},
             "slip10": {"n_legs": 0, "total_odds": 0, "in_band": False}})
    stub("grade_recommendations", main=lambda: calls.append("grade") or 0)
    stub("resolve_and_monitor", main=rec("resolve"))

    orig_run_py = sh._run_py
    orig_age = sh._fixtures_age_h

    class _R:
        returncode = 0
        stdout = "ok"
        stderr = ""

    def fake_run_py(script, *args):
        calls.append(f"py:{script}")
        return _R()

    sh._run_py = fake_run_py
    sh._fixtures_age_h = lambda: 1.0
    # Pemeriksaan kesegaran file corner membandingkan mtime dengan
    # waktu mulai langkah: buat file corner terlihat baru ditulis.
    orig_getmtime = os.path.getmtime

    def fake_getmtime(p):
        if str(p).endswith("predictions_corners_upcoming.csv"):
            import time as _t
            return _t.time()
        return orig_getmtime(p)

    os.path.getmtime = fake_getmtime

    def restore():
        sh._run_py = orig_run_py
        sh._fixtures_age_h = orig_age
        os.path.getmtime = orig_getmtime
        for name, mod in saved.items():
            if mod is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = mod

    return sh, calls, restore


def _run_shadow(sh):
    import contextlib
    import io

    buf = io.StringIO()
    code = None
    with contextlib.redirect_stdout(buf):
        try:
            sh.main()
        except SystemExit as e:
            code = e.code
    return code, buf.getvalue()


def test_shadow_gate_skips_consumers_when_predictions_fail():
    # Gerbang pred_ok (audit GPT B) tidak pernah punya tes integrasi:
    # sandbox PR #32 manual dan hilang. Prediksi gagal -> semua
    # konsumen prediksi dilewati, arsip tidak dibuat, run keluar 1;
    # langkah independen prediksi (corner/piala/grading TA/rute
    # piala/score_ledger/resolve) tetap jalan.
    sh, calls, restore = _shadow_env("error")
    try:
        code, _out = _run_shadow(sh)
    finally:
        restore()
    assert code == 1, code
    for skipped in ("picks", "py:best_picks.py", "mkt_ids", "mkt_cmp",
                    "ta_build", "recommend", "archive"):
        assert skipped not in calls, (skipped, calls)
    for ran in ("py:model_corners_v3.py", "ta_grade", "py:ta_scrape.py",
                "cup_ledger", "py:score_ledger.py", "resolve"):
        assert ran in calls, (ran, calls)


def test_shadow_gate_runs_all_consumers_on_success():
    # Jalur sukses: semua konsumen jalan, termasuk build ta_model
    # harian (langkah baru ronde 13) SEBELUM best_picks.
    sh, calls, restore = _shadow_env("success")
    try:
        code, _out = _run_shadow(sh)
    finally:
        restore()
    assert code is None, code
    for ran in ("pred", "picks", "mkt_cmp", "ta_build",
                "py:best_picks.py", "recommend", "archive", "grade"):
        assert ran in calls, (ran, calls)
    assert calls.index("ta_build") < calls.index("py:best_picks.py"), calls


def test_shadow_ta_build_rc_failure_marks_run_failed():
    # A14-2: build() mengembalikan 1 (ta/fixtures.csv kosong) tanpa
    # menulis model_markets — shadow harus menandai run gagal, bukan
    # mencetak selesai. Pipeline tetap lanjut (best_picks memakai
    # file terakhir yang ada), sesuai desain langkahnya.
    sh, calls, restore = _shadow_env("success")
    try:
        sys.modules["ta_model"].build = lambda: 1
        code, out = _run_shadow(sh)
    finally:
        restore()
    assert code == 1, code
    assert "[10/16] FAILED ta_model build" in out, out
    assert "py:best_picks.py" in calls, calls


def test_shadow_prints_archive_skipped():
    # D16-4: cabang cetak file ter-skip di langkah [14/16] tidak
    # dicakup tes mana pun (semua stub gerbang mengembalikan hasil
    # arsip tanpa "skipped"). Ganti stub arsip sesudah _shadow_env
    # dan asersi baris peringatannya muncul di output run.
    sh, calls, restore = _shadow_env("success")
    try:
        sys.modules["market_orchestration"].archive_snapshots = (
            lambda: {"date": "2026-10-31", "archived": [], "kept": [],
                     "skipped": ["recommended_slip10.csv"]})
        code, out = _run_shadow(sh)
    finally:
        restore()
    assert code is None, code
    assert "file dilewati (generasi tanggal lain)" in out, out
    assert "recommended_slip10.csv" in out, out


def test_shadow_fallback_flagged_when_refresh_raises_mid_loop():
    # Ronde 13: refresh mati di tengah loop sesudah satu liga ditulis
    # dari fallback disk -> run tetap ditandai gagal dan liga disebut,
    # walau jalur sukses A12-2 tidak tercapai. Sumber per liga dibaca
    # dari refresh_fixtures.LAST_SOURCES.
    import types

    sh, calls, restore = _shadow_env("success")
    try:
        rf = types.ModuleType("refresh_fixtures")

        def _boom():
            raise RuntimeError("jaringan mati di tengah loop")

        rf.main = _boom
        rf.LAST_SOURCES = {"E0": "fallback disk (boom)"}
        saved_rf = sys.modules.get("refresh_fixtures")
        sys.modules["refresh_fixtures"] = rf
        ages = iter([20.0, 20.0])
        sh._fixtures_age_h = lambda: next(ages, 20.0)
        try:
            code, out = _run_shadow(sh)
        finally:
            if saved_rf is None:
                sys.modules.pop("refresh_fixtures", None)
            else:
                sys.modules["refresh_fixtures"] = saved_rf
    finally:
        restore()
    assert code == 1, code
    assert "pred" in calls, calls  # prediksi tetap jalan (umur <= 48j)
    assert "E0" in out and "fallback" in out, out[-2000:]


def test_corner_stats_window_golden():
    # D12-1: fungsi corner yang tersaji tidak pernah tersentuh tes.
    # Nilai golden dihitung dari implementasi saat ini pada histori
    # sintetis tetap — perubahan rumus apa pun harus menabrak tes ini
    # secara sadar.
    from datetime import date

    import model_corners_v3 as mc

    games = [("A", "B", 6, 4, 12, 9, date(2026, 1, 28)),
             ("C", "A", 5, 5, 10, 11, date(2026, 1, 21)),
             ("B", "C", 7, 3, 14, 8, date(2026, 1, 10))]
    bh, ba, bmu, r_base, L = mc.stats_window(games, date(2026, 1, 31))
    assert abs(bh - 5.990688) < 1e-5, bh
    assert abs(ba - 4.009312) < 1e-5, ba
    assert abs(L - 10.662552) < 1e-5, L
    # Jendela kosong: nol, bukan ZeroDivisionError.
    assert mc.stats_window([], date(2026, 1, 31)) == (0.0,) * 5
    mu = mc.mu_cs({"base_h": 5.2, "base_a": 4.6, "fhp": 1.1,
                   "fhc": 0.9, "fap": 1.05, "fac": 0.95}, 0.15)
    assert abs(mu - 9.795578) < 1e-5, mu
    pmf = mc.pmf_k(10.4, 8.0)
    assert abs(sum(pmf) - 1.0) < 1e-9
    assert abs(sum(pmf[10:]) - 0.525424) < 1e-5


def test_corner_cups_parity_golden():
    # D12-2/B12-3: logika corner piala adalah duplikat logika liga —
    # kunci fungsi bersama (pmf_k identik byte-for-byte hasilnya) dan
    # mu piala pada histori sintetis tetap, supaya drift salah satu
    # sisi tertangkap.
    from datetime import date

    import model_corners_v3 as mc
    import predict_cups as pc

    assert pc.pmf_k(10.4, 8.0) == mc.pmf_k(10.4, 8.0)
    assert pc.pmf_k(9.1, 5.5) == mc.pmf_k(9.1, 5.5)

    def M(d, h, a, hc, ac, hs, asx):
        return {"div": "E0", "date": d, "home": h, "away": a,
                "hc": hc, "ac": ac, "hs": hs, "as": asx}

    ms = [M(date(2026, 1, 5), "Arsenal", "Chelsea", 7, 3, 15, 9),
          M(date(2026, 1, 12), "Liverpool", "Arsenal", 6, 5, 13, 12),
          M(date(2026, 1, 19), "Chelsea", "Liverpool", 4, 6, 10, 14),
          M(date(2026, 1, 26), "Arsenal", "Liverpool", 8, 4, 16, 11)]
    # Golden dihitung pada gamma 0,15: pin eksplisit (ronde 13) —
    # tanpa pin, refit corner_params.json yang ter-commit akan
    # menggeser golden tanpa perubahan rumus apa pun dan kegagalannya
    # terlihat seperti regresi rumus.
    saved_gamma = pc._gamma_cache
    pc._gamma_cache = 0.15
    try:
        mu = pc.corner_mu(ms, "Arsenal", "Chelsea", "E0", "E0",
                          date(2026, 2, 1))
    finally:
        pc._gamma_cache = saved_gamma
    assert abs(mu - 10.768281) < 1e-5, mu


def test_feature_rows_do_not_leak_own_result():
    # D12-3: baris fitur sebuah laga tidak boleh bergantung pada
    # hasil laga itu sendiri. Bangun dua kali dengan skor laga kedua
    # yang berbeda — fitur pra-laga untuk laga kedua harus identik.
    from datetime import date

    import football_etl
    import features

    def M(d, h, a, yh, ya, ftr):
        return {"div": "E0", "date": d, "season": "2026", "home": h,
                "away": a, "yh": yh, "ya": ya, "ftr": ftr}

    m1 = M(date(2026, 1, 1), "Arsenal", "Chelsea", 3, 0, "H")

    class FakeCache:
        def __init__(self, matches):
            self.matches = matches

    old = football_etl.MatchCache
    try:
        football_etl.MatchCache = lambda: FakeCache(
            [m1, M(date(2026, 1, 8), "Chelsea", "Arsenal", 0, 1, "A")])
        rows_a = features.build_feature_rows()
        football_etl.MatchCache = lambda: FakeCache(
            [m1, M(date(2026, 1, 8), "Chelsea", "Arsenal", 5, 0, "H")])
        rows_b = features.build_feature_rows()
    finally:
        football_etl.MatchCache = old
    feat_keys = ("elo_h", "elo_a", "elo_diff", "form_pts_h",
                 "form_pts_a", "goals_diff_h", "goals_diff_a",
                 "rest_h", "rest_a", "n_played_h", "n_played_a")
    ra, rb = rows_a[1], rows_b[1]
    for k in feat_keys:
        assert ra[k] == rb[k], (k, ra[k], rb[k])
    # Dan nilainya memang hanya mencerminkan laga pertama:
    # Chelsea kalah tandang -> 0 poin form, selisih gol -3, 1 laga.
    assert ra["form_pts_h"] == 0.0
    assert ra["goals_diff_h"] == -3.0
    assert ra["n_played_h"] == 1


def test_fitmodel_stats_come_from_train_only():
    # D12-4: imputasi/standarisasi T3 dihitung HANYA dari data latih
    # (termasuk penanganan NaN-nya) dan tidak berubah saat prediksi.
    import numpy as np

    from model_features_1x2 import FitModel

    Xtr = np.array([[1.0, 10.0], [3.0, np.nan], [5.0, 30.0],
                    [7.0, 40.0]])
    ytr = np.array([0, 1, 2, 0])
    m = FitModel(Xtr, ytr, epochs=2)
    assert np.allclose(m.med, [4.0, 30.0])          # median train
    imputed = np.array([[1.0, 10.0], [3.0, 30.0], [5.0, 30.0],
                        [7.0, 40.0]])
    assert np.allclose(m.mu, imputed.mean(axis=0))  # mean sesudah imputasi
    assert np.allclose(m.sd, imputed.std(axis=0))
    mu0, med0, sd0 = m.mu.copy(), m.med.copy(), m.sd.copy()
    p = m.predict(np.array([[100.0, -50.0]]))
    assert abs(float(p.sum()) - 1.0) < 1e-9
    assert np.array_equal(m.mu, mu0)
    assert np.array_equal(m.med, med0)
    assert np.array_equal(m.sd, sd0)


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)} unit tests passed")
