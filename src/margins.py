#!/usr/bin/env python3
"""Per-call margins for a v6 rows file, and where a second seat's flips sit in them (Meridian c80107, Aura c80130).
usage: margins.py <rows.jsonl> [<other_rows.jsonl>] [--out results/v6-margins.json]
A call is one (condition, item, jitter, trial). Its signed margin is the smallest gap among the inequalities of the
item's predicate in score.py (positive = predicate holds); |margin| is the distance to the bar in Hz. With a second
rows file, a flip is a call whose predicate sign differs between the two files. Margins are computed from the FIRST
file only, so a census published from one seat's rows is fixed before any perturbation arm runs."""
import json, sys, collections, statistics
args=[a for a in sys.argv[1:] if not a.startswith('--')]; out=sys.argv[sys.argv.index('--out')+1] if '--out' in sys.argv else 'results/v6-margins.json'
def load(path):
    R=collections.defaultdict(dict)
    for l in open(path, encoding='utf-8-sig'):
        if l.strip(): r=json.loads(l); R[(r['condition'],r['item'],r.get('jitter'),r['trial'])][r['stimulus']]=r
    return R
def hz(r,k): x=r['readouts'][k]; return x['stimulus_hz']-x['baseline_hz']
def ap(r): return hz(r,'DNp09')-hz(r,'MDN')
def margin(item,g):
    if item==1: a,n,p=ap(g['attractant']),ap(g['neutral']),ap(g['repellent']); return min(a-n, n-p)
    if item==2: return ap(g['low'])-ap(g['high'])
    if item==3: return ap(g['none'])-ap(g['co2'])
    if item==4: return hz(g['loom'],'DNp01')-hz(g['control_visual'],'DNp01')
    if item==5:
        ra,rb=(g['rot_a'],g['rot_b']) if 'rot_a' in g else (g['right_a'],g['right_b'])
        ha=hz(ra,'HS_R')-hz(ra,'HS_L'); hb=hz(rb,'HS_R')-hz(rb,'HS_L'); da=hz(ra,'DNa02_R')-hz(ra,'DNa02_L'); db=hz(rb,'DNa02_R')-hz(rb,'DNa02_L')
        return (1 if (ha*hb<0 and da*db<0) else -1)*min(abs(ha),abs(hb),abs(da),abs(db))
    if item==6:
        ft,cv,no=g['female_taste'],g['cva'],g['none']; return min(hz(ft,'pC1')-hz(no,'pC1'), hz(ft,'pIP10')-hz(no,'pIP10'), hz(no,'pC1')-hz(cv,'pC1'))
A=load(args[0]); B=load(args[1]) if len(args)>1 else None
calls={k:margin(k[1],g) for k,g in A.items()}
absm={k:abs(v) for k,v in calls.items()}; order=sorted(absm,key=absm.get); rank={k:i+1 for i,k in enumerate(order)}
res={'rows':args[0],'other':args[1] if B else None,'calls':len(calls),'ties_at_bar':sum(1 for v in absm.values() if v==0),
     'by_arm':{arm:{'n':len(v),'median_abs_margin_hz':round(statistics.median(v),3),'share_under_1hz':round(sum(1 for x in v if x<1)/len(v),3)} for arm in ('real','shuffled','random') for v in [[absm[k] for k in absm if k[0]==arm]]},
     'by_item':{it:{'n':len(v),'median_abs_margin_hz':round(statistics.median(v),3),'under_1hz':sum(1 for x in v if x<1)} for it in range(1,7) for v in [[absm[k] for k in absm if k[1]==it]]},
     'bins':[{'margin_hz':[lo,hi],'calls':sum(1 for k in absm if lo<=absm[k]<hi)} for lo,hi in [(0,1),(1,2),(2,5),(5,10),(10,None)] for hi in [hi if hi else 1e18]]}
if B:
    flips=[k for k in calls if (calls[k]>0)!=(margin(k[1],B[k])>0)]
    res['flips']=[{'call':[k[0],k[1],k[2],k[3]],'abs_margin_hz':round(absm[k],4),'rank_of_%d'%len(calls):rank[k]} for k in sorted(flips,key=lambda k:absm[k])]
    for b in res['bins']: lo,hi=b['margin_hz']; b['flips']=sum(1 for k in flips if lo<=absm[k]<hi)
    drift=collections.Counter(); 
    for k in A:
        if any(A[k][s]['readouts']!=B[k][s]['readouts'] for s in A[k]): drift[('item',k[1])]+=1; drift[('arm',k[0])]+=1
    res['calls_with_any_differing_readout']={'by_item':{it:drift[('item',it)] for it in range(1,7)},'by_arm':{a:drift[('arm',a)] for a in ('real','shuffled','random')}}
json.dump(res,open(out,'w'),indent=1); print(json.dumps({k:res[k] for k in ('calls','ties_at_bar','by_arm','by_item','bins')}, indent=None)[:1200]); print('flips', res.get('flips')); print('drift', res.get('calls_with_any_differing_readout'))
