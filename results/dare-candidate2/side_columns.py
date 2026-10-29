#!/usr/bin/env python3
"""Dare #7586 side columns (v7-draft, quire c95074) for an item-1 rows file, beside score.py's verdict.
usage: side_columns.py <rows.jsonl> [--json out.json]
T1: per comparison hit (strict, predicted direction) / wrong (strict, other way) / tie (equal). Trial = hit if all hit, wrong if any wrong, else tie.
T2: a tied comparison is silent when every neuron it reads (DNp09, MDN) is at zero on both sides; else equal-nonzero.
    A tie TRIAL is silent when every tied comparison in it is silent.
T3: strict hits/n, drop-silent hits/(n - silent-tie trials), and the triple. One-sided Fisher real vs each fake on both.
T5: share of comparisons whose read neurons fired (stimulus_hz > 0 or baseline_hz > 0) on either side.
Also: DNp09 silent trials = DNp09 stimulus_hz and baseline_hz both 0 in all three stimulus rows."""
import json, sys, math, collections
path = sys.argv[1]
R = collections.defaultdict(dict)
for l in open(path, encoding='utf-8-sig'):
    if l.strip():
        r = json.loads(l)
        if r['item'] != 1: continue
        if r['condition'] == 'random' and r.get('step') != 1.0: continue
        R[(r['condition'], r['trial'])][r['stimulus']] = r
READ = ('DNp09', 'MDN')
def hz(r, k): x = r['readouts'][k]; return x['stimulus_hz'] - x['baseline_hz']
def ap(r): return hz(r, 'DNp09') - hz(r, 'MDN')
def zero(r): return all(r['readouts'][k]['stimulus_hz'] == 0 and r['readouts'][k]['baseline_hz'] == 0 for k in READ)
def fired(r): return any(r['readouts'][k]['stimulus_hz'] > 0 or r['readouts'][k]['baseline_hz'] > 0 for k in READ)
def fisher(a, na, b, nb):
    tot = a + b; N = na + nb
    return sum(math.comb(na, x) * math.comb(nb, tot - x) / math.comb(N, tot) for x in range(a, min(na, tot) + 1))
out = {}
for cond in ('real', 'shuffled', 'random'):
    trials = sorted(t for (c, t), g in R.items() if c == cond and len(g) == 3)
    tri = collections.Counter(); ties = collections.Counter(); comps = fired_c = dnp09_silent = 0; hits = []; silent_trials = []
    for t in trials:
        g = R[(cond, t)]; A, Nn, P = g['attractant'], g['neutral'], g['repellent']
        cmps = [(A, Nn), (Nn, P)]   # predicted: left > right
        cls = []
        for L, Rr in cmps:
            l, r = ap(L), ap(Rr); cls.append('hit' if l > r else 'wrong' if l < r else 'tie')
            comps += 1; fired_c += (fired(L) or fired(Rr))
        call = 'hit' if all(c == 'hit' for c in cls) else 'wrong' if 'wrong' in cls else 'tie'
        tri[call] += 1
        if call == 'hit': hits.append(t)
        if call == 'tie':
            sil = all(zero(L) and zero(Rr) for (L, Rr), c in zip(cmps, cls) if c == 'tie')
            ties['silent' if sil else 'equal_nonzero'] += 1
            if sil: silent_trials.append(t)
        dnp09_silent += all(x['readouts']['DNp09']['stimulus_hz'] == 0 and x['readouts']['DNp09']['baseline_hz'] == 0 for x in (A, Nn, P))
    n = len(trials)
    out[cond] = dict(n=n, strict=f"{tri['hit']}/{n}", hit_tie_wrong=[tri['hit'], tri['tie'], tri['wrong']], ties_silent_equal_nonzero=[ties['silent'], ties['equal_nonzero']],
                     drop_silent=f"{tri['hit']}/{n - ties['silent']}", firing_share=f"{fired_c}/{comps}", firing_share_frac=round(fired_c / comps, 3) if comps else None,
                     dnp09_silent_trials=f"{dnp09_silent}/{n}", hits=hits, silent_tie_trials=silent_trials)
tests = {}
if 'real' in out and out['real']['n']:
    ka = out['real']['hit_tie_wrong'][0]; na = out['real']['n']; da = na - out['real']['ties_silent_equal_nonzero'][0]
    for f in ('shuffled', 'random'):
        if not out.get(f) or not out[f]['n']: continue
        kb = out[f]['hit_tie_wrong'][0]; nb = out[f]['n']; db = nb - out[f]['ties_silent_equal_nonzero'][0]
        tests[f] = dict(strict_p=round(fisher(ka, na, kb, nb), 5), strict_holds=fisher(ka, na, kb, nb) < 0.01,
                        drop_silent_p=round(fisher(ka, da, kb, db), 5) if da and db else None, drop_silent_holds=bool(da and db and fisher(ka, da, kb, db) < 0.01))
res = dict(rows=path, arms=out, real_vs_fake=tests,
           strict_pass=all(t['strict_holds'] for t in tests.values()) and len(tests) == 2,
           drop_silent_pass=all(t['drop_silent_holds'] for t in tests.values()) and len(tests) == 2)
for c, v in out.items(): print(c, json.dumps({k: v[k] for k in v if k not in ('hits', 'silent_tie_trials')}))
print('tests', json.dumps(tests)); print('strict_pass', res['strict_pass'], 'drop_silent_pass', res['drop_silent_pass'])
if '--json' in sys.argv: json.dump(res, open(sys.argv[sys.argv.index('--json') + 1], 'w'), indent=1)
