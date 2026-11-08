"""S-NO-OBOS virgin predictions export (record copy).

Per PREREG_S_NO_OBOS outputs: the shipped arm's virgin predictions, or
Gate Zero's labelled as such if nothing ships. S-NO-OBOS shipped
nothing (see reports/S_NO_OBOS_VERDICT.md), so this exports the Gate
Zero replay. FT only — no halves source exists in this league.
Also writes fitted_params_virgin.json (the pattern's frozen constants).
"""
import csv, json, os
from model import Engine, load_matches, NB_R
from harness import DATA, OUT, actual

PRED = os.path.join(os.path.dirname(OUT), '..', 'predictions', 's_no_obos_virgin_predictions.csv')
ARM = 'GZ'  # fallback label: nothing ships


def main():
    ms = load_matches(DATA, set(('2021', '2022', '2023', '2024', '2025', '2026')))
    eng = Engine(ms, ARM)
    rows = []
    for m in ms:
        if m['season'] == '2026':
            rows.append((m, eng.predict(m)))
        eng.update(m)
    os.makedirs(os.path.dirname(PRED), exist_ok=True)
    fields = ['match_id', 'date', 'home_team', 'away_team', 'actual_sot_total',
              'exp_sot_home', 'exp_sot_away', 'exp_sot_total', 'arm',
              'p_over_8.5', 'p_over_9.5', 'p_over_10.5']
    with open(PRED, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for m, p in rows:
            w.writerow({'match_id': m['match_id'], 'date': m['date'].isoformat(),
                        'home_team': m['home'], 'away_team': m['away'],
                        'actual_sot_total': m['sot_h'] + m['sot_a'],
                        'exp_sot_home': p['exp_h'], 'exp_sot_away': p['exp_a'],
                        'exp_sot_total': p['exp_h'] + p['exp_a'], 'arm': ARM,
                        'p_over_8.5': p['probs'][8.5], 'p_over_9.5': p['probs'][9.5],
                        'p_over_10.5': p['probs'][10.5]})
    with open(os.path.join(OUT, 'fitted_params_virgin.json'), 'w') as f:
        json.dump({'arm_exported': ARM, 'ships': False, 'nb_r': NB_R,
                   'note': 'v5 frozen constants; export is the Gate Zero record copy — no arm passed the virgin legs.'}, f, indent=2)
    print('wrote', PRED, len(rows), 'rows')


if __name__ == '__main__':
    main()
