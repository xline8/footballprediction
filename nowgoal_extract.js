// nowgoal_extract.js v2 — snapshot pre-match + LIVE + FT (skor akhir & HT) + odds (1X2 & AH)
// Sumber resmi: https://www.nowgoal25.com/ (redirect live.nowgoal50.com). movietime.tv HANYA cermin beriklan
// (rotasi domain, sering lag) — jangan pakai untuk pipeline.
// Jalankan: browser -> nowgoal25.com -> klik "Show All" bila ada -> evaluasi IIFE ini via browser_exec.
// Output JSON {total, byStatus, all:[row...]}.
// row: {league, div(E0/SP1/D1/I1/F1|null), date, ko_wib, status(pre|live|ft), minute, home, away,
//       score (skor kini/akhir), ht (skor babak I saat FT), ah_h, x2_h, ah_line, x2_d, ah_a, x2_a, raw}
// Catatan format: x2_* = 1X2 desimal; ah_* = odds AH format HK (0.93 = 1.93 desimal), ah_line = garis AH.
// Simpan setiap snapshot ke raw/odds_nowgoal_<YYYYmmdd_HHMM>.csv (immutable) lalu append baris div!=null
// ke raw/odds_timeseries.csv (dengan kolom captured) — itulah database deret waktu pre/live/post.
// Nama tim = versi situs; wajib alias sebelum dicocokkan ke model (Eintracht Frankfurt->Ein Frankfurt,
// RCD Espanyol->Espanol, dst). Tidak ketemu = SKIP, jangan menebak.
//
(function () {
  var LEAG = { "English Premier League": "E0", "Spanish La Liga": "SP1", "German Bundesliga": "D1", "Italy Serie A": "I1", "France Ligue 1": "F1" };
  var LEAGHIT = /(liga|league|ligue|serie|division|divisi|group|primera|segunda|eredivisie|bundesliga|championship|cup|piala|super)/i;
  var rows = [], curLeague = null, curDate = "";
  var trs = document.querySelectorAll('table tr');
  Array.prototype.forEach.call(trs, function (tr) {
    var txt = (tr.innerText || '').replace(/\s+/g, ' ').trim();
    if (!txt) return;
    if (txt.length < 70 && !/\d{1,2}:\d{2}/.test(txt)) {
      if (LEAG[txt]) { curLeague = txt; return; }
      var ok = null;
      for (var k in LEAG) {
        if (txt.indexOf(k) === 0) {
          var rest = txt.slice(k.length);
          if (!/[0-9]/.test(rest) && !/women|u1[6-9]|u2[1-3]/i.test(rest)) { ok = k; break; }
        }
      }
      if (ok) { curLeague = ok; return; }
      // header liga lain = RESET; tanpa ini ratusan baris mewarisi label terakhir
      if (LEAGHIT.test(txt)) { curLeague = null; return; }
      var dm = txt.match(/\d{2}-\d{2}\b|\d{4}-\d{2}-\d{2}/);
      if (dm && txt.length < 40) { curDate = dm[0]; }
      return;
    }
    var stds = Array.prototype.map.call(tr.querySelectorAll('.oddstd'), function (td) { return (td.innerText || '').replace(/\s+/g, ' ').trim(); });
    if (stds.length < 3) return;
    var ko = '', st = '', nameCells = [], scores = [];
    Array.prototype.forEach.call(tr.cells, function (td) {
      var t = (td.innerText || '').replace(/\s+/g, ' ').trim();
      if (!t) return;
      if (!ko && /\btime\b/i.test(td.className) && /^\d{1,2}:\d{2}$/.test(t)) { ko = t; return; }
      if (/\bstatus\b/i.test(td.className) || (/^\d+('|min)?$/i.test(t) && !ko)) { st = t; return; }
      if (/^\d{1,2}\s*-\s*\d{1,2}$/.test(t)) { scores.push(t); return; }
      if (/Tips$/i.test(t) || /^[-\u2013]$/.test(t)) return;
      if (td.querySelector('.oddstd')) return;
      if (t.length > 1) nameCells.push({ t: t, c: td.className || '' });
    });
    if (!ko) return;
    var home = nameCells[0] ? nameCells[0].t : '', away = nameCells[1] ? nameCells[1].t : '';
    if (!home || !away) return;
    var status = 'pre';
    if (st) { if (/FT|Finished|Ended/i.test(st)) status = 'ft'; else if (/^\d+/.test(st)) status = 'live'; }
    else if (scores.length) status = 'ft';
    function two(t) { var m = t.match(/^\s*([\w./+-]+)\s+([\d.]+)\s*$/); return m ? [m[1], m[2]] : null; }
    var p0 = two(stds[0]), p1 = two(stds[1]), p2 = two(stds[2]);
    if (!(p0 && p1 && p2)) return;
    rows.push({ league: curLeague, div: LEAG[curLeague] || null, date: curDate, ko_wib: ko, status: status, minute: st || null,
      home: home, away: away, score: scores[0] || null,
      ht: (status === 'ft' && scores.length > 1 ? scores[scores.length - 1] : null),
      ah_h: p0[0], x2_h: p0[1], ah_line: p1[0], x2_d: p1[1], ah_a: p2[0], x2_a: p2[1], raw: stds.join(' || ') });
  });
  return JSON.stringify({
    total: rows.length,
    byStatus: rows.reduce(function (a, r) { var k = (r.div || '?') + '/' + r.status; a[k] = (a[k] || 0) + 1; return a; }, {}),
    all: rows
  });
})()
