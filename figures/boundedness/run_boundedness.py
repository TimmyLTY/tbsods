import os
"""One-vs-rest boundedness analysis; reuses immutable pairing and logistic engine."""
from pathlib import Path
import sys,json,time
import numpy as np
import pandas as pd
from scipy.stats import norm
P=Path(__file__).resolve().parent; R=Path(os.environ['TBSODS_RESULTS_DIR'])/'boundedness'
sys.path.insert(0,str(P.parent/'feedback'))
import run_feedback as fb
LEVELS=['closed','guided','open']

def load():
    allturns,primary,_=fb.load()
    bound=fb.read_paper_turns(fb.SOURCE,columns=['conversation_id','turn_index','boundedness'])
    for name,d in [('all',allturns),('primary',primary)]:
        merged=d.merge(bound,on=['conversation_id','turn_index'],validate='one_to_one',how='left')
        if name=='all':allturns=merged
        else:primary=merged
    eligible=primary[primary.boundedness.isin(LEVELS)].copy().reset_index(drop=True)
    assert len(primary)==138466 and eligible.y_appreciation.le(eligible.y_positive_feedback).all()
    return allturns,primary,eligible

def descriptive(frame,dim,group):
    A,G=fb.cmat(frame);n=len(frame);rows=[]
    for level in LEVELS:
        x=frame.boundedness.eq(level).to_numpy();nx=int(x.sum())
        for outcome in fb.OUTCOMES:
            y=frame['y_'+outcome].to_numpy();ny=int(y.sum());o=int(y[x].sum());e=nx*ny/n
            p1=o/nx;p0=(ny-o)/(n-nx)
            score=np.where(x,(y-p1)/nx,-(y-p0)/(n-nx));u=A@score
            se=np.sqrt(G/(G-1)*np.square(u).sum())
            rows.append(dict(dimension=dim,group=group,boundedness=level,outcome=outcome,
                pairs=n,sources=G,exposed=nx,events=ny,observed=o,expected=e,
                joint_pct=100*o/n,conditional_pct=100*p1,other_pct=100*p0,
                log2_oe=np.log2(o/e) if o else np.nan,
                event_sources=frame.loc[x&(y==1),'proxy_id'].nunique(),
                diff_pp=100*(p1-p0),ci_low=100*(p1-p0-1.96*se),ci_high=100*(p1-p0+1.96*se),
                p=2*norm.sf(abs((p1-p0)/se)) if se else 1))
    return pd.DataFrame(rows)

def design(d,level,dim,variant):
    cols={'intercept':np.ones(len(d)), 'focal':d.boundedness.eq(level).astype(float)}
    if dim!='overall':
        g=d[dim].eq(fb.GROUPS[dim][0]).astype(float)
        cols.update(group_a=g,focal_x_group=cols['focal']*g)
    controls={'log_position':fb.z(np.log1p(d.observed_rank+1)),'log_chars':fb.z(np.log1p(d.chars)),
              'prior_contestation':d.history_contestation,'prior_positive':d.history_positive_feedback}
    if variant=='operation_count':controls['operation_count']=fb.z(d.n_operations)
    else:controls.update({f'op_{o}':d[f'op_{o}'] for o in fb.OPS})
    if variant!='no_current_stance':
        controls.update({f'current_{s}':d[f'current_{s}'] for s in ['contestation','appreciation','acknowledgement','agreement']})
    for cat in ['month']+(['model'] if dim!='model' else [])+(['region'] if dim in ['overall','model'] else []):
        controls.update(pd.get_dummies(d[cat],prefix=cat,drop_first=True,dtype=float).to_dict('series'))
    for k,v in controls.items():
        if np.std(v)>1e-12:cols[k]=v
    return np.column_stack(list(cols.values())),list(cols)

def summarize(est,grad,V):
    se=np.sqrt(max(float(grad@V@grad),0))
    return dict(estimate_pp=100*est,se_pp=100*se,ci_low=100*(est-1.96*se),ci_high=100*(est+1.96*se),p=2*norm.sf(abs(est/se)) if se else 1)

def models(data,dim,variant):
    d=data if dim=='overall' else data[data[dim].isin(fb.GROUPS[dim])]
    d=d.reset_index(drop=True);A,G=fb.cmat(d)
    w=None
    if variant=='equal_source':
        w=1/d.groupby('proxy_id').proxy_id.transform('size').to_numpy();w*=len(d)/w.sum()
    rows=[];diagnostics=[];grs=['All'] if dim=='overall' else list(fb.GROUPS[dim])
    for level in LEVELS:
        X,names=design(d,level,dim,variant)
        focal=d.boundedness.eq(level).to_numpy()
        for outcome in fb.OUTCOMES:
            y=d['y_'+outcome].to_numpy();cells={}
            for group in grs:
                gm=np.ones(len(d),bool) if dim=='overall' else d[dim].eq(group).to_numpy()
                for present in [0,1]:
                    sel=gm&(focal==present);ev=sel&(y==1)
                    cells[group+'/'+str(present)]={'n':int(sel.sum()),'events':int(ev.sum()),'event_sources':int(d.loc[ev,'proxy_id'].nunique())}
            eligible=all(c['events']>=10 and c['n']-c['events']>=10 and c['event_sources']>=5 for c in cells.values())
            base=dict(dimension=dim,boundedness=level,reference=' + '.join(l for l in LEVELS if l!=level),outcome=outcome,variant=variant,pairs=len(d),sources=G,support_eligible=eligible)
            try:
                beta,V,dg=fb.fit(X,y,A,w)
                fit_status='ok' if dg['converged'] and dg['condition_number']<=1e12 else 'unstable_fit'
                status=fit_status if fit_status!='ok' or eligible else 'insufficient_events'
                estimates={}
                for estimand,gval in ([('overall',None)] if dim=='overall' else [('group_a',1.),('group_b',0.)]):
                    est,grad,p1,p0=fb.standardize(beta,X,gval,w)
                    estimates[estimand]=(est,grad)
                    rows.append({**base,'estimand':estimand,'status':status,**summarize(est,grad,V),'present_pct':100*p1,'absent_pct':100*p0})
                if dim!='overall':
                    est=estimates['group_a'][0]-estimates['group_b'][0];grad=estimates['group_a'][1]-estimates['group_b'][1]
                    rows.append({**base,'estimand':'difference','status':status,**summarize(est,grad,V)})
                diagnostics.append({**base,'fit_status':fit_status,**dg,'cells':json.dumps(cells),'terms':json.dumps(names),'coefficients':json.dumps(beta.tolist())})
            except np.linalg.LinAlgError:
                rows.append({**base,'estimand':'overall' if dim=='overall' else 'difference','status':'singular_fit','p':np.nan})
                diagnostics.append({**base,'fit_status':'singular_fit','cells':json.dumps(cells),'terms':json.dumps(names)})
            print(variant,dim,level,outcome,diagnostics[-1]['fit_status'],flush=True)
    return pd.DataFrame(rows),pd.DataFrame(diagnostics)

def main():
    _,_,d=load();R.mkdir(parents=True,exist_ok=True)
    raw = descriptive(d,'overall','All')
    raw['q'] = fb.bh(raw['p'], 9)
    raw.to_csv(R/'cooccurrence_all.csv',index=False)
    result,_=models(d,'overall','primary')
    result['q'] = fb.bh(result['p'].where(result['status'].eq('ok'), 1), 9)
    result.to_csv(R/'adjusted_associations_all.csv',index=False)

if __name__=='__main__':main()
