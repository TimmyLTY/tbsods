import os
"""Independent boundedness subfigures and an explicit selection record."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
P=Path(__file__).resolve().parent;R=Path(os.environ['TBSODS_RESULTS_DIR'])/'boundedness';F=P.parent
OUTCOMES=['contestation','appreciation','positive_feedback']
TITLES=['Contestation','Appreciation','Positive feedback']
LEVELS=['closed','guided','open']
COLORS=['#AF4B53','#287C9E','#398778']
raw=pd.read_csv(R/'cooccurrence_all.csv');models=pd.read_csv(R/'adjusted_associations_all.csv')
mpl.rcParams.update({'font.family':'DejaVu Serif','font.size':9,'axes.titlesize':11,'axes.titleweight':'bold','axes.labelsize':9,'xtick.labelsize':8,'ytick.labelsize':9,'pdf.fonttype':42,'svg.fonttype':'none','axes.spines.top':False,'axes.spines.right':False,'savefig.facecolor':'white'})

def save(fig,name,data):
    fig.savefig(F/f'{name}.png',dpi=250,facecolor='white')
    plt.close(fig)

def bubbles():
    data=raw[raw.dimension.eq('overall')];fig,ax=plt.subplots(figsize=(5.8,5.1))
    fig.subplots_adjust(left=.21,right=.81,top=.79,bottom=.30)
    norm=TwoSlopeNorm(vmin=-1.5,vcenter=0,vmax=1.5);cmap=mpl.colormaps['RdBu']
    for yi,level in enumerate(LEVELS):
        for xi,outcome in enumerate(OUTCOMES):
            row=data[data.boundedness.eq(level)&data.outcome.eq(outcome)].iloc[0]
            ax.scatter(xi,yi,s=row.joint_pct*850,c=[cmap(norm(row.log2_oe))],edgecolors='#666666',linewidths=.55,zorder=3)
    ax.set(xticks=range(3),xticklabels=['Contestation','Appreciation','Positive\nfeedback'],yticks=range(3),yticklabels=LEVELS,xlim=(-.5,2.5),ylim=(2.5,-.5))
    ax.xaxis.tick_top();ax.tick_params(axis='both',length=0,pad=8);ax.set_ylabel('Boundedness at T−1',labelpad=13)
    for value in [.5,1.5]:ax.axhline(value,color='#e4e4e4',lw=.5);ax.axvline(value,color='#e4e4e4',lw=.5)
    ax.spines[['left','bottom']].set_visible(False)
    fig.text(.54,.945,'Appreciation ⊂ Positive feedback',ha='center',fontsize=9)
    cbax=fig.add_axes([.865,.30,.02,.49]);cb=fig.colorbar(mpl.cm.ScalarMappable(norm=norm,cmap=cmap),cax=cbax);cb.set_ticks([-1.5,-1,-.5,0,.5,1,1.5]);cbax.set_title('log₂(O/E)',fontsize=8,pad=14)
    legendax=fig.add_axes([.24,.025,.65,.20]);legendax.set(xlim=(0,3.8),ylim=(0,1));legendax.axis('off')
    for x,size in zip([.2,1.4,2.8],[.2,1,3]):
        legendax.scatter(x,.5,s=size*850,c='#aaa',edgecolors='#666',linewidths=.55)
        legendax.text(x+.40,.5,f'{size:g}%',va='center',fontsize=8)
    fig.text(.52,.245,'Joint frequency (%)',ha='center',fontsize=8)
    save(fig,'boundedness_cooccurrence',data)

def main():
    bubbles();panels=[];manifest=[]
    for o,title,color in zip(OUTCOMES[:2],TITLES[:2],COLORS[:2]):
        a=models[models.variant.eq('primary')&models.dimension.eq('overall')&models.outcome.eq(o)&models.estimand.eq('overall')].copy()
        panels.append(('overall',o,title,color,a))
    # Shared overall scale permits visual comparison of outcome-specific associations.
    overall=pd.concat([a for dim,o,title,color,a in panels if dim=='overall'])
    lo=min(0,overall.ci_low.min());hi=max(0,overall.ci_high.max());pad=.12*(hi-lo)
    overall_limits=[float(lo-pad),float(hi+pad)]
    comparison={'model':'GPT-4 − GPT-3.5','region':'Eastern − Western','china_us':'China − United States'}
    for dim,o,title,color,a in panels:
        a=a.set_index('boundedness').reindex([l for l in LEVELS if l in a.boundedness.values]).reset_index()
        n=len(a);fig,ax=plt.subplots(figsize=(4.8,2.55));fig.subplots_adjust(left=.19,right=.97,top=.69,bottom=.28)
        ax.axvline(0,color='#888',lw=.75)
        for yi,row in enumerate(a.itertuples()):
            ax.plot([row.ci_low,row.ci_high],[yi,yi],color=color,lw=1.4)
            ax.scatter(row.estimate_pp,yi,s=32,c=color,edgecolors='white',linewidths=.3,zorder=3)
        limits=overall_limits if dim=='overall' else [min(0,a.ci_low.min())-.2,max(0,a.ci_high.max())+.2]
        ax.set(yticks=range(n),yticklabels=a.boundedness,ylim=(n-.5,-.5),xlim=limits,xlabel='Adjusted difference (percentage points)')
        ax.xaxis.set_major_locator(mpl.ticker.MultipleLocator(.5));ax.grid(axis='x',color='#eee',lw=.5);ax.set_axisbelow(True);ax.spines['left'].set_visible(False);ax.tick_params(axis='y',length=0)
        fig.text(.58,.92,title,ha='center',fontsize=11,fontweight='bold')
        subtitle='Present − absent' if dim=='overall' else comparison[dim]+' | Present − absent'
        fig.text(.58,.805,subtitle,ha='center',fontsize=8.5)
        name=f'boundedness_{dim}_{o}';save(fig,name,a);manifest.append(dict(name=name,dimension=dim,outcome=o,title=title,rows=a.boundedness.tolist(),x_limits=limits))

if __name__=='__main__':main()
