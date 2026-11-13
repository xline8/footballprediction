#!/usr/bin/env python3
"""Ringkasan kesehatan pagi gabungan: API + rantai top-5 + runner liga.

Satu-satunya pekerjaan skrip ini adalah MEMBACA keadaan yang sudah
dihasilkan pipeline orang lain (endpoint health, logs/run_status_<tgl>.json,
league/runner/run_log.jsonl, umur file kunci) dan mencetak satu ringkasan
pendek berbahasa Indonesia. Tidak menulis apa pun, tidak menjalankan
pipeline. Dipakai cron football-health-summary (±10:07 WIB, sesudah kedua
laporan pagi terbit) dan bisa dijalankan manual kapan pun:

    .venv/bin/python health_summary.py
"""

import json
import os
import urllib.request
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

BASE = os.path.dirname(os.path.abspath(__file__))
WIB = ZoneInfo("Asia/Jakarta")
CORNER_PARAMS_MAX_AGE_DAYS = 14.0   # gerbang fail-fast model_corners_v3
CORNER_PARAMS_WARN_DAYS = 11.0
PREDICTIONS_MAX_AGE_HOURS = 48.0    # gerbang API MAX_PREDICTIONS_AGE_HOURS


def _age_hours(path, now):
    return (now.timestamp() - os.path.getmtime(path)) / 3600.0


def main():
    now = datetime.now(WIB)
    today = now.date()
    lines = [f"RINGKASAN KESEHATAN SISTEM — {today.isoformat()}"]
    warnings = []

    # --- API -------------------------------------------------------------
    try:
        with urllib.request.urlopen("http://127.0.0.1:8000/api/health",
                                    timeout=10) as resp:
            body = json.loads(resp.read().decode())
        if body.get("status") == "healthy":
            lines.append("• API: sehat")
        else:
            lines.append(f"• API: menjawab tapi status={body.get('status')!r}")
            warnings.append("API tidak melaporkan status healthy")
    except Exception as exc:  # API mati / tidak menjawab
        lines.append(f"• API: TIDAK MENJAWAB ({exc.__class__.__name__})")
        warnings.append("API mati — watchdog 10 menit seharusnya "
                        "menghidupkannya; cek service football-prediction")

    # --- Rantai top-5 ------------------------------------------------------
    status_path = os.path.join(BASE, "logs", f"run_status_{today}.json")
    if os.path.exists(status_path):
        st = json.load(open(status_path))
        products = st.get("products", {})
        failed = [name for name, p in products.items()
                  if p.get("status") != "OK"]
        if st.get("run_ok") and not failed:
            lines.append(f"• Rantai top-5: OK — {len(products)}/"
                         f"{len(products)} produk OK")
        else:
            lines.append(f"• Rantai top-5: {len(products) - len(failed)}/"
                         f"{len(products)} produk OK; gagal: "
                         f"{', '.join(failed) if failed else '-'}")
            warnings.append("produk top-5 gagal: "
                            + (", ".join(failed) if failed else "run_ok=false"))
    else:
        lines.append("• Rantai top-5: status hari ini belum ada "
                     "(run pagi belum selesai / belum jalan)")
        warnings.append("run_status hari ini tidak ditemukan")

    # --- Runner liga -------------------------------------------------------
    log_path = os.path.join(BASE, "league", "runner", "run_log.jsonl")
    start_utc = datetime(today.year, today.month, today.day,
                         tzinfo=WIB).astimezone(timezone.utc)
    end_utc = start_utc + timedelta(days=1)
    leagues_done, n_errors, n_pred, n_settled = set(), 0, 0, 0
    if os.path.exists(log_path):
        with open(log_path) as fh:
            for line in fh:
                try:
                    d = json.loads(line)
                    ts = datetime.fromisoformat(d["ts"])
                except Exception:
                    continue
                if not (start_utc <= ts < end_utc):
                    continue
                if d.get("step") == "summary":
                    leagues_done.add(d.get("league"))
                n_errors += len(d.get("errors") or [])
                n_pred += d.get("predicted") or 0
                n_settled += d.get("settled") or 0
    if leagues_done:
        n_pred_id = f"{n_pred:,}".replace(",", ".")
        lines.append(f"• Runner liga: {len(leagues_done)} liga selesai, "
                     f"{n_errors} error, {n_pred_id} prediksi baru, "
                     f"{n_settled} settlement")
        if n_errors:
            warnings.append(f"runner liga mencatat {n_errors} error hari ini")
    else:
        lines.append("• Runner liga: belum ada liga yang selesai hari ini")
        warnings.append("runner liga belum menghasilkan summary hari ini")

    # --- Kesegaran file kunci ----------------------------------------------
    pred_path = os.path.join(BASE, "predictions_upcoming.csv")
    if os.path.exists(pred_path):
        age_h = _age_hours(pred_path, now)
        lines.append(f"• File prediksi top-5: umur {age_h:.1f} jam "
                     f"(batas API {PREDICTIONS_MAX_AGE_HOURS:.0f} jam)")
        if age_h > PREDICTIONS_MAX_AGE_HOURS:
            warnings.append("file prediksi melewati batas basi API (48 jam)")
    else:
        lines.append("• File prediksi top-5: TIDAK ADA")
        warnings.append("predictions_upcoming.csv hilang")

    cp_path = os.path.join(BASE, "ta", "corner_params.json")
    if os.path.exists(cp_path):
        age_d = _age_hours(cp_path, now) / 24.0
        lines.append(f"• Parameter corner: umur {age_d:.1f} hari "
                     f"(gerbang gagal pada {CORNER_PARAMS_MAX_AGE_DAYS:.0f} "
                     "hari; refit manual)")
        if age_d >= CORNER_PARAMS_MAX_AGE_DAYS:
            warnings.append("parameter corner SUDAH melewati gerbang 14 hari "
                            "— langkah corner akan gagal; refit manual sekarang")
        elif age_d >= CORNER_PARAMS_WARN_DAYS:
            warnings.append(f"parameter corner berumur {age_d:.1f} hari — "
                            "refit manual sebelum genap 14 hari")
    else:
        lines.append("• Parameter corner: TIDAK ADA")
        warnings.append("ta/corner_params.json hilang")

    # --- Peringatan ----------------------------------------------------------
    if warnings:
        lines.append("⚠ Peringatan: " + "; ".join(warnings))
    else:
        lines.append("✓ Tidak ada peringatan — semua jalur sehat.")

    print("\n".join(lines))


if __name__ == "__main__":
    main()
