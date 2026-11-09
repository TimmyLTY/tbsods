import os
"""Reproducible manuscript figures and independent panels; edits are config-driven.
Invoked by scripts/reproduce.py.
No annotation files are written. The display contains model and China–United States contrasts; inference retains the original BH family.
"""
from pathlib import Path
import json
import numpy as np,pandas as pd,matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
O=Path(__file__).resolve().parent;cfg=json.loads((O/'paper_figure_config.json').read_text());R=Path(os.environ['TBSODS_RESULTS_DIR'])/'descriptive';F=O.parent
D=pd.read_csv(R/'label_distributions.csv');C=pd.read_csv(R/'group_comparisons.csv')
tax=json.loads((O.parents[1]/'taxonomy/taxonomy.json').read_text())['output_contract']['fields']
COL=cfg['colors'];GROUP={a['axis']:a['group'] for a in cfg['axes']}
STYLE={'font.family':'DejaVu Serif','font.size':10,'axes.titlesize':11,'axes.titleweight':'bold','axes.labelsize':9.5,'xtick.labelsize':9,'ytick.labelsize':10,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.edgecolor':'#5A6470','axes.linewidth':.7,'xtick.major.width':.6,'ytick.major.size':0,'svg.fonttype':'none','pdf.fonttype':42,'ps.fonttype':42,'savefig.facecolor':'white'}
def name(s):return s.replace('_',' ')
def fmt(v):return f'{v:.2f}' if v>=.01 else '<0.01'
def axisdata(a,full=False):
 p=D[(D.axis==a['axis'])&(D.population==a['population'])&D.label.isin(tax[a['axis']]['values'])].sort_values('percent',ascending=False).copy()
 return p if full or not a['top'] else p.head(a['top'])
def export(fig,path):
 fig.savefig(path.with_suffix('.png'),dpi=350,bbox_inches='tight',pad_inches=.08)
 plt.close(fig)
def distribution(ax,a,letter=None,full=False):
 p=axisdata(a,full);y=np.arange(len(p));col=COL[a['group']];ax.barh(y,p.percent,color=col,height=.68,zorder=2)
 ax.set_yticks(y,[name(s) for s in p.label]);ax.invert_yaxis();ax.set_xlim(0,a['limit']);ax.set_xticks(np.linspace(0,a['limit'],4));ax.grid(axis='x',color='#E5E7E9',linewidth=.65,zorder=0);ax.set_axisbelow(True)
 ax.set_title(a['title'],loc='left',pad=6)
 ax.set_xlabel('Turns (%)',labelpad=3)
 for yy,v in zip(y,p.percent):ax.text(v+a['limit']*.013,yy,fmt(v),va='center',fontsize=8.7,clip_on=False)
 return p

def comparedata(p):
 rows=[]
 for ax,lab in p['labels']:
  r=C[(C.contrast==p['key'])&(C.axis==ax)&(C.label==lab)].iloc[0].copy()
  assert r.q<.05,(p['key'],ax,lab,r.q)
  r['group']=GROUP[ax];rows.append(r)
 return pd.DataFrame(rows)
def contrast(ax,p,letter=None):
 d=comparedata(p);y=np.arange(len(d));ax.set_yticks(y,[name(v) for v in d.label]);ax.set_ylim(len(d)-.4,-.7);ax.set_xlim(-30,30);ax.set_xticks([-30,-15,0,15,30]);ax.axvline(0,color='#77818A',lw=.8);ax.grid(axis='x',color='#E5E7E9',linewidth=.6);ax.set_axisbelow(True)
 for yy,(_,r) in zip(y,d.iterrows()):
  color=COL[r.group];ax.errorbar(r.diff_pp,yy-.075,xerr=[[r.diff_pp-r.ci_low],[r.ci_high-r.diff_pp]],fmt='o',color=color,markersize=4.7,capsize=2,elinewidth=1.05)
  ax.scatter(r.equal_proxy_diff_pp,yy+.16,s=24,marker='D',facecolors='white',edgecolors=color,linewidths=1,zorder=4)
  ax.text(31,yy,f'{r.diff_pp:+.2f}',va='center',fontsize=9,clip_on=False)
 ax.set_title(p['title'],loc='left',pad=7)
 return d

def render():
 with plt.rc_context(STYLE|{'font.size':9,'axes.titlesize':10,'xtick.labelsize':8,'ytick.labelsize':9}):
  fig=plt.figure(figsize=(7.6,9.0))
  fig.legend(handles=[Patch(facecolor=COL[k],label=t) for k,t in [('work','Delegated work'),('material','Material support'),('expression','Disclosure and stance')]],loc='upper center',ncol=3,frameon=False,fontsize=8.5,bbox_to_anchor=(.55,.997))
  fig.text(.03,.945,'Overall distribution',fontweight='bold',fontsize=11);fig.text(.615,.945,'Group differences',fontweight='bold',fontsize=11)
  counts=[len(axisdata(a)) for a in cfg['axes']];total=sum(n+3.7 for n in counts);top=.89
  for a,n in zip(cfg['axes'],counts):
   unit=.83/total;h=(n+.3)*unit;ax=fig.add_axes([.205,top-h,.29,h]);distribution(ax,a);ax.set_title(a['title'],loc='left',fontsize=10);ax.set_xlabel('Turns (%)' if a==cfg['axes'][-1] else '',fontsize=8,labelpad=2);top-=(n+3.7)*unit
  selected=[]
  for i,p in enumerate(c for c in cfg['contrasts'] if c['key'] in ('model','china_us')):
   d=comparedata(p);selected.append(d);ax=fig.add_axes([.79,.56-i*.415,.27,.30]);ax.set_yticks(range(4),[name(x) for x in d.label]);ax.set_ylim(3.55,-.55)
   ax.set_xlim((0,16) if i==0 else (-30,30));ax.set_xticks([0,4,8,12,16] if i==0 else [-30,-15,0,15,30]);ax.axvline(0,color='#77818A',lw=.9);ax.grid(axis='x',color='#E5E7E9',lw=.6);ax.set_axisbelow(True)
   for j,(_,r) in enumerate(d.iterrows()):
    col=COL[r.group];ax.errorbar(r.diff_pp,j-.065,xerr=[[r.diff_pp-r.ci_low],[r.ci_high-r.diff_pp]],fmt='o',color=col,markersize=5,capsize=4,capthick=1.3,elinewidth=1.6)
    ax.scatter(r.equal_proxy_diff_pp,j+.16,s=29,marker='D',facecolors='white',edgecolors=col,linewidths=1.2,zorder=4)
    ax.text(1.04,j,f'{r.diff_pp:+.2f}',transform=ax.get_yaxis_transform(),va='center',fontsize=8)
   ax.set_title(p['title'],loc='left',x=-.68,fontsize=10,pad=12);ax.tick_params(axis='y',labelsize=8.5)
   ax.set_xlabel('Difference (percentage points)',fontsize=8,labelpad=5)
  fig.legend(handles=[Line2D([0],[0],color='#444444',marker='o',lw=1.6,markersize=5,label='Turn weighted (95% CI)'),Line2D([0],[0],color='#444444',marker='D',markerfacecolor='white',lw=0,markersize=5,label='Equal source weighting')],loc='lower left',bbox_to_anchor=(.59,.035),frameon=False,fontsize=8)
  export(fig,F/'delegation_combined')

if __name__=='__main__':render()
