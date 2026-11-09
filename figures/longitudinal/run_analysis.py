import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from resource_io import read_paper_turns
"""Compute the ten-bin repeated-use curve with the frozen source bootstrap."""
from pathlib import Path
import json

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
RESULTS = Path(os.environ['TBSODS_RESULTS_DIR']) / 'longitudinal'
SOURCE = ROOT / 'data/annotated_turns'
TAX = json.loads((ROOT / 'taxonomy/taxonomy.json').read_text())['output_contract']['fields']
LABELS = [(axis, label) for axis, spec in TAX.items() for label in spec['values']]
OUTCOMES = {'contestation': {'contestation'}, 'appreciation': {'appreciation'},
            'positive_feedback': {'agreement', 'acknowledgement', 'appreciation'}}
SEED, BOOTSTRAPS = 20261004, 5000


def bootstrap_mean(matrix, seed):
    """Resample whole source rows, jointly across columns; missing is not zero."""
    a = np.asarray(matrix, float)
    present = np.isfinite(a).astype(float)
    values = np.nan_to_num(a)
    n = len(a)
    rng = np.random.default_rng(seed)
    boot = np.full((BOOTSTRAPS, a.shape[1]), np.nan)
    for start in range(0, BOOTSTRAPS, 100):
        size = min(100, BOOTSTRAPS-start)
        weights = rng.multinomial(n, np.full(n, 1/n), size=size).astype(float)
        den = weights @ present
        np.divide(weights @ values, den, out=boot[start:start+size], where=den > 0)
    return np.nanquantile(boot, [0.025, 0.975], axis=0)

def load():
    cols = ['conversation_id','observed_rank','turn_index','strict_next','proxy_id',
            'timestamp','model', *TAX]
    d = read_paper_turns(SOURCE, columns=cols).sort_values(['conversation_id','observed_rank']).reset_index(drop=True)
    # These detect a changed corpus, duplicate inputs, or an incorrect feedback shift.
    assert len(d) == 207047 and d.conversation_id.nunique() == 63559
    assert not d.duplicated(['conversation_id','turn_index']).any()
    assert d.groupby('conversation_id').timestamp.nunique().max() == 1
    assert not d.proxy_id.isna().any() and not d.timestamp.isna().any()
    nxt = d.groupby('conversation_id').turn_index.shift(-1)
    d['observed_next'] = nxt.notna()
    d['strict'] = (nxt-d.turn_index == 1)
    assert d.strict.eq(d.strict_next).all()
    d['task'] = d.task_dialogue_act.ne('no_task')
    for outcome, labels in OUTCOMES.items():
        current = d.stances.map(lambda x: int(bool(set(x) & labels)))
        d['y_'+outcome] = current.groupby(d.conversation_id).shift(-1)
    primary = d.loc[d.task & d.strict]
    assert len(primary) == 138466
    assert primary[['y_contestation','y_appreciation','y_positive_feedback']].sum().tolist() == [7811, 1803, 5423]
    c = d.drop_duplicates('conversation_id')[['conversation_id','proxy_id','timestamp']].copy()
    ties = c.duplicated(['proxy_id','timestamp'], keep=False)
    tied_sources = c.loc[ties,'proxy_id'].unique()
    audit = dict(total_turns=len(d), total_conversations=len(c), total_sources=c.proxy_id.nunique(),
                 timestamp_tied_conversations=int(ties.sum()), timestamp_tied_sources=len(tied_sources),
                 n2_before_ties=int(c.groupby('proxy_id').size().ge(2).sum()),
                 n10_before_ties=int(c.groupby('proxy_id').size().ge(10).sum()),
                 reproduced_feedback_pairs=len(primary), reproduced_feedback_events={k:int(primary['y_'+k].sum()) for k in OUTCOMES})
    # Do not invent within-timestamp order; exclude affected source trajectories.
    c = c.loc[~c.proxy_id.isin(tied_sources)].sort_values(['proxy_id','timestamp']).copy()
    c['n_conversations'] = c.groupby('proxy_id').conversation_id.transform('size')
    c['conversation_rank'] = c.groupby('proxy_id').cumcount()+1
    c['relative_rank'] = (c.conversation_rank-.5)/c.n_conversations
    c['decile'] = np.floor(10*c.relative_rank).astype(int)+1
    c['phase'] = np.select([c.conversation_rank <= c.n_conversations//2,
                           c.conversation_rank > c.n_conversations-c.n_conversations//2], [0,1], default=-1)
    c['day'] = c.timestamp.dt.floor('D')
    source = c.groupby('proxy_id').agg(n_conversations=('conversation_id','size'),
               active_days=('day','nunique'), first=('timestamp','min'), last=('timestamp','max'))
    source['span_days'] = (source['last']-source['first']).dt.total_seconds()/86400
    d = d.merge(c.drop(columns=['proxy_id','timestamp','day']), on='conversation_id', how='inner', validate='many_to_one')
    return d, c, source, audit

def curve(d, ids, scheme, seed):
    f=d.loc[d.proxy_id.isin(ids)].copy()
    f['bin']=f.decile if scheme=='decile' else f.conversation_rank
    f=f.loc[f.bin<=10]
    idx=pd.MultiIndex.from_product([ids,range(1,11)],names=['proxy_id','bin'])
    pairs=f.loc[f.task&f.strict]
    groups=pairs.groupby(['proxy_id','bin'])
    den=groups.size().reindex(idx,fill_value=0)
    mats=[]; nums=[]; outcomes=list(OUTCOMES)
    for outcome in outcomes:
        num=groups['y_'+outcome].sum().reindex(idx,fill_value=0)
        mats.append((num/den.replace(0,np.nan)).unstack('bin').reindex(ids).to_numpy())
        nums.append(num)
    task=f.loc[f.task].groupby(['proxy_id','bin'])
    taskden=task.size().reindex(idx,fill_value=0)
    for outcome,col in [('observed_continuation','observed_next'),('strict_pair_coverage','strict')]:
        num=task[col].sum().reindex(idx,fill_value=0)
        mats.append((num/taskden.replace(0,np.nan)).unstack('bin').reindex(ids).to_numpy())
        nums.append(num);outcomes.append(outcome)
    ci=bootstrap_mean(np.concatenate(mats,axis=1),seed)
    rows=[]
    for oi,outcome in enumerate(outcomes):
        deno=den if oi<3 else taskden
        for bi in range(10):
            ar=mats[oi][:,bi]; valid=np.isfinite(ar); nn=nums[oi].xs(bi+1,level=1);dd=deno.xs(bi+1,level=1)
            ff=pairs if oi<3 else f.loc[f.task]
            rows.append(dict(scheme=scheme,outcome=outcome,bin=bi+1,cohort_sources=len(ids),
                  sources=int(valid.sum()),event_sources=int((nn>0).sum()),events=int(nn.sum()),eligible=int(dd.sum()),
                  conversations=int(ff.loc[ff.bin==bi+1,'conversation_id'].nunique()),
                  rate_pct=100*np.nanmean(ar),ci_low=100*ci[0,oi*10+bi],ci_high=100*ci[1,oi*10+bi],
                  pooled_rate_pct=100*nn.sum()/dd.sum()))
    return rows,mats

def main():
    RESULTS.mkdir(parents=True,exist_ok=True)
    d,_,source,_=load()
    ids=source.index[source.n_conversations>=10]
    f=d.loc[d.proxy_id.isin(ids)&d.task&d.strict]
    counts=f.groupby('proxy_id').decile.nunique()
    complete=counts.index[counts==10]
    assert len(complete)==200
    rows,_=curve(d,complete,'decile',SEED+31)
    pd.DataFrame(rows).to_csv(RESULTS/'feedback_complete_bins.csv',index=False)

if __name__=='__main__':main()
