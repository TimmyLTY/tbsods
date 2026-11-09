import os
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from resource_io import read_paper_turns
"""Turn-level six-axis distributions; source-proxy clustered differences.
Invoked by scripts/reproduce.py.
No original annotation or human reference file is modified.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd
from scipy import sparse,stats
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
RESULTS=Path(os.environ['TBSODS_RESULTS_DIR'])/'descriptive'
RESULTS.mkdir(parents=True,exist_ok=True)
REGION_NAME='East and Southeast Asia'
SOURCE=ROOT/'data/annotated_turns'
tax=json.loads((ROOT/'taxonomy/taxonomy.json').read_text())['output_contract']['fields']
d=read_paper_turns(SOURCE,columns=['conversation_id','turn_index','observed_rank','proxy_id','country','model','timestamp',*tax])
# Supported input checks: wrong row universe or duplicated turn keys would change all denominators.
assert len(d)==207047 and d.conversation_id.nunique()==63559
assert not d.duplicated(['conversation_id','turn_index']).any()
task=(d.task_dialogue_act!='no_task').to_numpy(); valid=d.boundedness.notna().to_numpy(); first=(d.observed_rank==0).to_numpy()
cm=pd.read_csv(OUT/'country_mapping.csv')
d=d.merge(cm[['country','region','english_group']],on='country',how='left',validate='many_to_one')
d['model_family']=np.where(d.model.str.startswith('gpt-4'),'GPT-4','GPT-3.5')
d['china_us']=d.country.where(d.country.isin(['China','United States']),'Excluded')
metrics=[]; arrays={}
for axis,spec in tax.items():
 if spec['kind']=='array':
  arr=[set(x) for x in d[axis]]
  for label in spec['values']:arrays[(axis,label)]=np.array([label in x for x in arr])
  arrays[(axis,'any')]=np.array([bool(x) for x in arr]);arrays[(axis,'empty')]=~arrays[(axis,'any')]
 else:
  for label in spec['values']:arrays[(axis,label)]=(d[axis]==label).to_numpy(dtype=bool)
  if axis=='boundedness': arrays[(axis,'missing')]=~valid
arrays[('joint','disclosure_and_stance')]=arrays[('disclosures','any')] & arrays[('stances','any')]
arrays[('joint','neither_disclosure_nor_stance')]=~arrays[('disclosures','any')] & ~arrays[('stances','any')]
arrays[('support','both')]=arrays[('support','user_material')] & arrays[('support','assistant_material')]
for (axis,label),y in arrays.items():
 for population,m in [('all_turns',np.ones(len(d),bool)),('task_turns',task),('first_turns',first),('valid_bounded_task_turns',task&valid)]:
  metrics.append(dict(axis=axis,label=label,population=population,n=int(m.sum()),count=int(y[m].sum()),percent=float(100*y[m].mean())))
pd.DataFrame(metrics).to_csv(RESULTS/'label_distributions.csv',index=False)
code,ids=pd.factorize(d.proxy_id); G=len(ids); A=sparse.csr_matrix((np.ones(len(d)),(code,np.arange(len(d)))),shape=(G,len(d)))
comparisons=[('model','model_family','GPT-4','GPT-3.5'),('region','region',REGION_NAME,'Europe-plus'),('china_us','china_us','China','United States'),('english','english_group','English official/de facto','Other language environment')]
rows=[]; samples=[]
for contrast,col,a,b in comparisons:
 ga=(d[col]==a).to_numpy();gb=(d[col]==b).to_numpy()
 for name,g in [(a,ga),(b,gb)]:
  samples.append(dict(contrast=contrast,group=name,turns=int(g.sum()),task_turns=int((g&task).sum()),conversations=d.loc[g,'conversation_id'].nunique(),proxies=d.loc[g,'proxy_id'].nunique(),missing_bounded=int((g&task&~valid).sum())))
 for (axis,label),y in arrays.items():
  eligible=np.ones(len(d),bool) if axis=='task_dialogue_act' else task.copy()
  if axis=='boundedness' and label!='missing':eligible &= valid
  ma=ga&eligible;mb=gb&eligible;na=ma.sum();nb=mb.sum();pa=y[ma].mean();pb=y[mb].mean();delta=pa-pb
  influence=np.where(ma,(y-pa)/na,0)-np.where(mb,(y-pb)/nb,0)
  cl=np.asarray(A@influence).ravel();used=np.asarray(A@(ma|mb).astype(float)).ravel()>0;ng=int(used.sum())
  se=float(np.sqrt(ng/(ng-1)*np.square(cl).sum()));p=float(2*stats.norm.sf(abs(delta/se))) if se else (1.0 if delta==0 else 0.0)
  # Equal-weight source-proxy mean is a sensitivity estimand, not unique-person preference.
  def proxymean(m):
   ns=np.asarray(A@m.astype(float)).ravel();ys=np.asarray(A@(m&y).astype(float)).ravel();return np.mean(ys[ns>0]/ns[ns>0])
  rows.append(dict(contrast=contrast,axis=axis,label=label,group_a=a,group_b=b,n_a=int(na),n_b=int(nb),count_a=int(y[ma].sum()),count_b=int(y[mb].sum()),pct_a=100*pa,pct_b=100*pb,diff_pp=100*delta,ci_low=100*(delta-1.96*se),ci_high=100*(delta+1.96*se),p=p,proxy_clusters=ng,first_turn_diff_pp=100*(y[ma&first].mean()-y[mb&first].mean()),equal_proxy_diff_pp=100*(proxymean(ma)-proxymean(mb))))
r=pd.DataFrame(rows)
# One exploratory family covers the four planned contrasts and all 58 schema labels;
# aggregate any/empty/joint and missing diagnostics are descriptive, not added tests.
r['q']=np.nan
ix=r.apply(lambda x:x.axis in tax and x.label in tax[x.axis]['values'],axis=1)
pv=r.loc[ix,'p'].to_numpy();order=np.argsort(pv);q=np.empty(len(pv));q[order]=np.minimum.accumulate((pv[order]*len(pv)/np.arange(1,len(pv)+1))[::-1])[::-1].clip(0,1);r.loc[ix,'q']=q
r.to_csv(RESULTS/'group_comparisons.csv',index=False);pd.DataFrame(samples).to_csv(RESULTS/'group_samples.csv',index=False)
