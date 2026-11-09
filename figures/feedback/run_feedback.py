import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from resource_io import read_paper_turns
"""Calculate the overall subsequent-feedback estimates used by the paper figures."""
from pathlib import Path
import json, warnings, time
import numpy as np
import pandas as pd
from scipy.special import expit
from scipy.stats import norm
from scipy import sparse
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
RESULTS=Path(os.environ['TBSODS_RESULTS_DIR'])/'feedback'
SOURCE=ROOT/'data/annotated_turns'
OPS=json.loads((ROOT/'taxonomy/taxonomy.json').read_text())['output_contract']['fields']['operations']['values']
OUTCOMES={'contestation':{'contestation'},'appreciation':{'appreciation'},'positive_feedback':{'appreciation','acknowledgement','agreement'}}
GROUPS={'overall':('All','All'),'model':('GPT-4','GPT-3.5'),'region':('Eastern','Western'),'china_us':('China','United States')}

def bh(p, family=None):
    p=np.asarray(p,float); p=np.where(np.isfinite(p),p,1); n=family or len(p)
    o=np.argsort(p); q=np.empty(len(p)); q[o]=np.minimum.accumulate((p[o]*n/np.arange(1,len(p)+1))[::-1])[::-1].clip(0,1);return q

def load():
    cols=['conversation_id','observed_rank','turn_index','strict_next','proxy_id','country','model','timestamp','operations','stances','task_dialogue_act','n_operations','current_user_turn']
    d=read_paper_turns(SOURCE,columns=cols).sort_values(['conversation_id','observed_rank']).reset_index(drop=True)
    assert len(d)==207047 and not d.duplicated(['conversation_id','turn_index']).any()
    d['chars']=d.current_user_turn.str.len(); d=d.drop(columns='current_user_turn')
    for o,labels in OUTCOMES.items():
        cur=d.stances.map(lambda x:int(bool(set(x)&labels)))
        d['current_'+o]=cur
        d['history_'+o]=(cur.groupby(d.conversation_id).cumsum()-cur>0).astype(int)
        d['y_'+o]=cur.groupby(d.conversation_id).shift(-1)
    for label in ['acknowledgement','agreement']:
        d['current_'+label]=d.stances.map(lambda x:int(label in x))
        d['y_'+label]=d['current_'+label].groupby(d.conversation_id).shift(-1)
    nxt=d.groupby('conversation_id').turn_index.shift(-1)
    d['observed_next']=nxt.notna(); d['strict']=(nxt-d.turn_index==1)
    assert (d.strict==d.strict_next).all()
    d['task']=d.task_dialogue_act.ne('no_task')
    for op in OPS:d['op_'+op]=d.operations.map(lambda x:int(op in x))
    cm=pd.read_csv(OUT.parent/'descriptive/country_mapping.csv')
    d=d.merge(cm[['country','region']],on='country',how='left',validate='many_to_one')
    d['region']=d.region.map({'East and Southeast Asia':'Eastern','Europe-plus':'Western','Excluded':'Other'})
    d['model']=np.where(d.model.str.startswith('gpt-4'),'GPT-4','GPT-3.5')
    d['china_us']=d.country.where(d.country.isin(['China','United States']),'Other')
    d['month']=d.timestamp.dt.strftime('%Y-%m');d['overall']='All'
    primary=d[d.strict&d.task].copy().reset_index(drop=True)
    old=d[d.observed_next].copy().reset_index(drop=True)
    assert len(old)==143488 and int(old.y_contestation.sum())==8081 and int(old.y_positive_feedback.sum())==5860
    assert primary.y_appreciation.le(primary.y_positive_feedback).all()
    return d,primary,old

def cmat(frame):
    c,ids=pd.factorize(frame.proxy_id,sort=False); n=len(frame);g=len(ids)
    return sparse.csr_matrix((np.ones(n),(c,np.arange(n))),shape=(g,n)),g

def raw(frame,dimension,group):
    A,G=cmat(frame);n=len(frame);rows=[]
    for op in OPS:
        x=frame['op_'+op].to_numpy(bool); nx=x.sum()
        for outcome in OUTCOMES:
            y=frame['y_'+outcome].to_numpy(bool);ny=y.sum();o=(x&y).sum();e=nx*ny/n
            p1=o/nx if nx else np.nan;p0=(ny-o)/(n-nx) if n>nx else np.nan
            u=np.where(x,(y-p1)/nx, -(y-p0)/(n-nx)) if nx and nx<n else np.zeros(n)
            v=A@u; se=np.sqrt(G/(G-1)*np.square(v).sum())
            rows.append(dict(dimension=dimension,group=group,operation=op,outcome=outcome,n=n,sources=G,exposed=int(nx),events=int(ny),observed=int(o),expected=e,joint_pct=100*o/n,log2_oe=np.log2(o/e) if o and e else np.nan,observed_minus_expected=o-e,event_sources=frame.loc[x&y,'proxy_id'].nunique(),present_pct=100*p1,absent_pct=100*p0,diff_pp=100*(p1-p0),se_pp=100*se,ci_low=100*(p1-p0-1.96*se),ci_high=100*(p1-p0+1.96*se),p=2*norm.sf(abs((p1-p0)/se)) if se else 1))
    return pd.DataFrame(rows)

def z(v):
    v=np.asarray(v,float);s=v.std();return (v-v.mean())/(s if s else 1)

def design(frame,op,dimension,variant):
    f=frame['op_'+op].to_numpy(float);cols=[np.ones(len(frame)),f];names=['intercept',op]
    comparison=dimension!='overall'
    if comparison:
        g=(frame[dimension]==GROUPS[dimension][0]).to_numpy(float)
        cols += [g,f*g];names+=['group_a','operation_x_group_a']
    if variant=='legacy':
        controls={'position':z(frame.observed_rank+1),'chars':z(frame.chars),'total_operations':z(frame.n_operations),'prior_contestation':frame.history_contestation}
    else:
        controls={'log_position':z(np.log1p(frame.observed_rank+1)),'log_chars':z(np.log1p(frame.chars)),'other_operations':z(frame.n_operations-f),'prior_contestation':frame.history_contestation,'prior_positive':frame.history_positive_feedback}
        if variant!='no_current_stance':
            controls.update({x:frame['current_'+x] for x in ['contestation','appreciation','acknowledgement','agreement']})
        for cat in ['month']+(['model'] if dimension!='model' else [])+(['region'] if dimension in ['overall','model'] else []):
            dd=pd.get_dummies(frame[cat],prefix=cat,drop_first=True,dtype=float)
            controls.update({c:dd[c] for c in dd})
    for name,v in controls.items():
        v=np.asarray(v,float)
        if v.std()>1e-12:cols.append(v);names.append(name)
    return np.column_stack(cols),names

def fit(X,y,A,w=None):
    n,p=X.shape;g=A.shape[0]
    if w is None:w=np.ones(n)
    beta=np.zeros(p);mean=np.average(y,weights=w);beta[0]=np.log(mean/(1-mean))
    converged=False
    def loss(b):
        eta=X@b;return np.sum(w*(np.logaddexp(0,eta)-y*eta))
    for it in range(80):
        pr=expit(X@beta); W=w*pr*(1-pr);H=X.T@(W[:,None]*X);score=X.T@(w*(y-pr))
        step=np.linalg.solve(H,score); oldloss=loss(beta);scale=1.
        while scale>1/1024 and loss(beta+scale*step)>oldloss+1e-8:scale/=2
        beta+=scale*step
        if np.max(abs(scale*step))<1e-7:converged=True;break
    pr=expit(X@beta);H=X.T@((w*pr*(1-pr))[:,None]*X);cond=np.linalg.cond(H)
    bread=np.linalg.inv(H);scores=A@(X*(w*(y-pr))[:,None]);V=(g/(g-1))*((n-1)/(n-p))*bread@(scores.T@scores)@bread
    return beta,V,dict(converged=converged,iterations=it+1,condition_number=float(cond),parameters=p,sources=g,max_score_per_row=float(np.max(abs(X.T@(w*(y-pr))))/n))

def standardize(beta,X,gval=None,w=None):
    a=X.copy();b=X.copy();a[:,1]=1;b[:,1]=0
    if gval is not None:a[:,2]=b[:,2]=gval;a[:,3]=gval;b[:,3]=0
    pa=expit(a@beta);pb=expit(b@beta)
    if w is None:w=np.ones(len(X))
    w=w/w.sum();grad=(w*pa*(1-pa))@a-(w*pb*(1-pb))@b
    return float(w@(pa-pb)),grad,float(w@pa),float(w@pb)

def models(frame,dimension,variant='primary',operations=None):
    ops=operations or OPS;rows=[];diag=[]
    if dimension!='overall':frame=frame[frame[dimension].isin(GROUPS[dimension])].copy()
    frame=frame.reset_index(drop=True);A,G=cmat(frame);weights=None
    if variant=='equal_source':
        counts=frame.groupby('proxy_id').proxy_id.transform('size').to_numpy();weights=1/counts;weights*=len(frame)/weights.sum()
    for oi,op in enumerate(ops):
        X,names=design(frame,op,dimension,variant)
        f=frame['op_'+op].to_numpy(bool)
        for outcome in OUTCOMES:
            y=frame['y_'+outcome].to_numpy(float)
            grs=GROUPS[dimension] if dimension!='overall' else ('All',)
            cells=[]
            for group in grs:
                gm=np.ones(len(frame),bool) if group=='All' else frame[dimension].eq(group).to_numpy()
                for value in [0,1]:
                    sel=gm&(f==value);ev=sel&(y==1)
                    cells.append({'group':group,'present':value,'n':int(sel.sum()),'events':int(ev.sum()),'event_sources':int(frame.loc[ev,'proxy_id'].nunique())})
            status='ok' if all(c['events']>=10 and c['n']-c['events']>=10 and c['event_sources']>=5 for c in cells) else 'insufficient_events'
            base=dict(dimension=dimension,operation=op,outcome=outcome,variant=variant,n=len(frame))
            if status!='ok':
                rows.append({**base,'estimand':'overall' if dimension=='overall' else 'difference','status':status,'p':np.nan})
                diag.append({**base,'status':status,'cells':json.dumps(cells)});continue
            try:
                beta,V,dg=fit(X,y,A,weights)
                if not dg['converged'] or dg['condition_number']>1e12:status='unstable_fit'
                values={}
                for group,gvalue in ([("overall",None)] if dimension=='overall' else [('group_a',1.),('group_b',0.)]):
                    ame,grad,p1,p0=standardize(beta,X,gvalue,weights);values[group]=(ame,grad)
                    se=np.sqrt(max(float(grad@V@grad),0));pval=2*norm.sf(abs(ame/se)) if se else 1
                    rows.append({**base,'estimand':group,'status':status,'ame_pp':100*ame,'se_pp':100*se,'ci_low':100*(ame-1.96*se),'ci_high':100*(ame+1.96*se),'p':pval,'present_pct':100*p1,'absent_pct':100*p0})
                if dimension!='overall':
                    est=values['group_a'][0]-values['group_b'][0];grad=values['group_a'][1]-values['group_b'][1];se=np.sqrt(max(float(grad@V@grad),0))
                    rows.append({**base,'estimand':'difference','status':status,'ame_pp':100*est,'se_pp':100*se,'ci_low':100*(est-1.96*se),'ci_high':100*(est+1.96*se),'p':2*norm.sf(abs(est/se)) if se else 1,'log_odds_interaction':beta[3],'log_odds_interaction_p':2*norm.sf(abs(beta[3]/np.sqrt(V[3,3])))})
                diag.append({**base,'status':status,**dg,'cells':json.dumps(cells),'terms':json.dumps(names),'coefficients':json.dumps(beta.tolist())})
            except np.linalg.LinAlgError as e:
                rows.append({**base,'estimand':'overall' if dimension=='overall' else 'difference','status':'singular_fit','p':np.nan})
                diag.append({**base,'status':'singular_fit','cells':json.dumps(cells)})
        if (oi+1)%5==0:print(f'{variant} {dimension}: {oi+1}/{len(ops)} operations',flush=True)
    return pd.DataFrame(rows),pd.DataFrame(diag)

def main():
    _,primary,_=load();RESULTS.mkdir(parents=True,exist_ok=True)
    rawdf=raw(primary,'overall','All');rawdf['q']=bh(rawdf.p,87)
    rawdf.to_csv(RESULTS/'lagged_cooccurrence_all.csv',index=False)
    fitted,diagnostics=models(primary,'overall')
    fitted['q']=bh(fitted.p,87)
    fitted.to_csv(RESULTS/'adjusted_associations_all.csv',index=False)
    diagnostics.to_csv(RESULTS/'model_diagnostics.csv',index=False)

if __name__=='__main__':main()
