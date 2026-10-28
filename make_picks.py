# -*- coding: utf-8 -*-
"""make_picks.py — generate picks value & append IMMUtable ke ledger/picks.jsonl.

Aturan ledger:
- Append-only; pick lama TIDAK pernah diubah/dihapus (dedupe via pick_id).
- Signal = prob model MURNI (ph_dc/pd_dc/pa_dc, p_over_dc) — dgn disiplin sama
  seperti backtest_value.py (bukan blended).
- Harga = odds opening/day-of dari FD raw (B365) saat pick dibuat (disimpan!).
- Pick lahir hanya bila harga tersedia & edge > 0.02 (grid utama backtest).
- Skor dikerjakan score_ledger.py → grades.jsonl (juga append-only).
"""
import csv
import hashlib
import json
import os
from datetime import date, datetime, timezone

import paths

PROJ = paths.BASE
PRED = os.path.join(PROJ, "predictions_upcoming.csv")
LEDGER = os.path.join(PROJ, "ledger")
PICKS = os.path.join(LEDGER, "picks.jsonl")
THR = 0.02


def fnum(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def main():
    """Generate betting picks and append to ledger."""
    os.makedirs(LEDGER, exist_ok=True)
    existing = set()
    if os.path.exists(PICKS):
        with open(PICKS, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    existing.add(json.loads(line)["pick_id"])

    created = []
    today = date.today().isoformat()
    with open(PRED, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            if (r.get("date") or "") < today:
                continue  # jangan buat pick utk pertandingan yang sudah dimainkan
            base = dict(div=r["div"], date=r["date"], time=r["time"],
                        home=r["home"], away=r["away"])
            cand = []
            for side, pcol, ocol in (("H", "ph_dc", "b365h"), ("D", "pd_dc", "b365d"),
                                     ("A", "pa_dc", "b365a")):
                cand.append(("1X2", side, fnum(r.get(pcol)), fnum(r.get(ocol))))
            cand.append(("OU", "Over", fnum(r.get("p_over_dc")), fnum(r.get("b365o25"))))
            for market, side, pm, o in cand:
                if pm is None or o is None or o <= 1.0:
                    continue  # belum ada harga -> pick belum lahir (job esok mengecek ulang)
                edge = pm - 1.0 / o
                if edge <= THR:
                    continue
                pid = hashlib.md5(f"{base['div']}|{base['date']}|{base['home']}|{base['away']}|{market}|{side}"
                                  .encode()).hexdigest()[:16]
                if pid in existing:
                    continue
                rec = dict(pick_id=pid, ts_created=datetime.now(timezone.utc).isoformat(),
                           model="v2-pure", thr=THR, status="pending",
                           market=market, side=side, p_model=round(pm, 4),
                           odds_open=o, p_imp_open=round(1.0 / o, 4),
                           edge=round(edge, 4), **base)
                created.append(rec)
                existing.add(pid)

    if created:
        with open(PICKS, "a", encoding="utf-8") as f:
            for rec in created:
                f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"picks baru: {len(created)} (total ledger: {len(existing)})")
    for rec in created[:8]:
        print("  +", rec["div"], rec["date"], f'{rec["home"]} v {rec["away"]}',
              rec["market"], rec["side"], "edge=%.3f" % rec["edge"], "@", rec["odds_open"])
    if len(created) > 8:
        print("  ... +", len(created) - 8, "lagi")
    return created


if __name__ == "__main__":
    main()
