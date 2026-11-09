"""Complete all 29 x 3 Overall fits; reuse the unchanged 81 existing fits.
Sparse estimates are retained, but the existing support rule governs display.
"""
import json
import numpy as np
import pandas as pd
from scipy.stats import norm
from run_feedback import RESULTS,load,cmat,design,fit,standardize,bh
_,frame,_=load();A,G=cmat(frame)
r=pd.read_csv(RESULTS/'adjusted_associations_all.csv').query('dimension=="overall"').copy()
d=pd.read_csv(RESULTS/'model_diagnostics.csv').query('dimension=="overall"').copy()
r['support_eligible']=r.status.eq('ok');r['fit_status']=np.where(r.support_eligible,'converged','not_fitted')
for i,row in r[~r.support_eligible].iterrows():
 X,names=design(frame,row.operation,'overall','primary');y=frame['y_'+row.outcome].to_numpy(float)
 beta,V,diag=fit(X,y,A);a,g,p1,p0=standardize(beta,X);se=np.sqrt(g@V@g)
 for k,v in dict(ame_pp=100*a,se_pp=100*se,ci_low=100*(a-1.96*se),ci_high=100*(a+1.96*se),p=2*norm.sf(abs(a/se)),present_pct=100*p1,absent_pct=100*p0,fit_status='converged' if diag['converged'] and diag['condition_number']<1e12 else 'unstable').items():r.loc[i,k]=v
 mask=(d.operation==row.operation)&(d.outcome==row.outcome)
 for k,v in {**diag,'terms':json.dumps(names),'coefficients':json.dumps(beta.tolist())}.items():d.loc[mask,k]=v
r['q_all_fits']=bh(r.p,87)
r['ci_excludes_zero']=(r.ci_low>0)|(r.ci_high<0)
r['display']=r.support_eligible&r.fit_status.eq('converged')&r.ci_excludes_zero&r.operation.ne('other')
r['display_reason']=np.select([~r.support_eligible,~r.fit_status.eq('converged'),r.operation.eq('other'),~r.ci_excludes_zero],['insufficient event support','unstable fit','heterogeneous residual category','CI crosses zero'],default='selected')
r.to_csv(RESULTS/'overall_all_operations.csv',index=False);d.to_csv(RESULTS/'overall_all_operations_diagnostics.csv',index=False)
print(r.groupby(['outcome','display']).size().to_string())
print(r[~r.support_eligible][['operation','outcome','fit_status','ame_pp','ci_low','ci_high']].to_string(index=False))
