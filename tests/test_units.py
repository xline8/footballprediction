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


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"PASS {fn.__name__}")
    print(f"{len(fns)} unit tests passed")
