import os
"""Independent scientific subfigures; no montage or composite is generated."""
from pathlib import Path
import json, math
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
from matplotlib.lines import Line2D
from run_feedback import OPS,OUTCOMES,GROUPS
OUT=Path(__file__).resolve().parent;R=Path(os.environ['TBSODS_RESULTS_DIR'])/'feedback';F=OUT.parent
rows=json.loads((OUT/'figure_config.json').read_text())['figure_operations']
raw=pd.read_csv(R/'lagged_cooccurrence_all.csv');raw=raw[raw.dimension=='overall']
overall_all=pd.read_csv(R/'overall_all_operations.csv')
TITLE={'contestation':'Contestation','appreciation':'Appreciation','positive_feedback':'Positive feedback'}
COLORS={'contestation':'#AF4B53','appreciation':'#287C9E','positive_feedback':'#398778'}
mpl.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'axes.titlesize':11,'axes.titleweight':'bold','axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':9,'pdf.fonttype':42,'ps.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})

def save(fig,name,data):
    fig.savefig(F/f'{name}.png',dpi=250,facecolor='white')
    plt.close(fig)

def bubbles(operations,name):
    h=1.7+.52*len(operations);fig,ax=plt.subplots(figsize=(5.8,h));fig.subplots_adjust(left=.25,right=.85,top=1-.80/h,bottom=.90/h)
    data=raw[raw.operation.isin(operations)].copy();norm=TwoSlopeNorm(vmin=-3,vcenter=0,vmax=3);cmap=mpl.colormaps['RdBu']
    for yi,op in enumerate(operations):
        for xi,outcome in enumerate(OUTCOMES):
            a=data[(data.operation==op)&(data.outcome==outcome)].iloc[0]; color=cmap(norm(a.log2_oe)) if np.isfinite(a.log2_oe) else '#DDDDDD'
            ax.scatter(xi,yi,s=a.joint_pct*850,c=[color],edgecolors='#666666',linewidths=.55,zorder=3)
    ax.set(xticks=range(3),xticklabels=['Contestation','Appreciation','Positive\nfeedback'],yticks=range(len(operations)),yticklabels=[o.replace('_',' ') for o in operations],xlim=(-.5,2.5),ylim=(len(operations)-.5,-.5))
    ax.xaxis.tick_top();ax.tick_params(axis='both',length=0,pad=8);ax.set_ylabel('Operations at T−1',labelpad=12)
    for y in np.arange(.5,len(operations)-.5):ax.axhline(y,color='#e4e4e4',lw=.5,zorder=0)
    for x in [.5,1.5]:ax.axvline(x,color='#e4e4e4',lw=.5,zorder=0)
    ax.spines[['left','bottom']].set_visible(False)
    fig.text(.56,1-.18/h,'Appreciation ⊂ Positive feedback',ha='center',fontsize=9)
    cbax=fig.add_axes([.89,.95/h,.021,1-1.80/h]);cb=fig.colorbar(mpl.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cbax);cb.set_ticks([-3,-2,-1,0,1,2,3]);cb.set_label('log₂(O/E)',fontsize=8)
    handles=[plt.scatter([],[],s=x*850,c='#999999',edgecolors='#333',lw=.5,label=f'{x:g}%') for x in [.1,.5,1.]]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.52,.18/h),ncol=3,frameon=False,title='Joint frequency (%)',fontsize=8,title_fontsize=8,labelspacing=2.2,handletextpad=1.8,columnspacing=2.3)
    save(fig,name,data)

bubbles(rows,'feedback_cooccurrence')
manifest=[]
for dim in ['overall']:
    if dim=='overall':
        for outcome in OUTCOMES:
            data=overall_all[(overall_all.outcome==outcome)&overall_all.display].sort_values('ame_pp',ascending=False).copy()
            n=len(data);h=1.10+.29*n
            fig,ax=plt.subplots(figsize=(5.25,h));fig.subplots_adjust(left=.28,right=.97,top=1-.45/h,bottom=.65/h)
            ax.axvline(0,color='#888888',lw=.75)
            for y,a in enumerate(data.itertuples()):
                ax.plot([a.ci_low,a.ci_high],[y,y],color=COLORS[outcome],lw=1.15)
                ax.scatter(a.ame_pp,y,s=24,c=COLORS[outcome],edgecolors='white',linewidths=.3,zorder=3)
            ax.set(yticks=range(n),yticklabels=data.operation,ylim=(n-.5,-.5),xlabel='Adjusted difference (percentage points)')
            ax.set_xlim(min(0,data.ci_low.min())-.25,max(0,data.ci_high.max())+.30)
            ax.grid(axis='x',color='#eeeeee',lw=.5);ax.set_axisbelow(True);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
            ax.set_title(TITLE[outcome],pad=13)
            name=f'feedback_{outcome}';save(fig,name,data)
            manifest.append(dict(name=name,dimension=dim,outcome=outcome,x_limit=None,rows=data.operation.tolist()))
        continue
