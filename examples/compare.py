"""Reproduce a controlled style comparison using synthetic public data."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from paper_style import apply_style, color, clean, export_figure, MM

def axes_labels(ax):
    ax.set(xlabel='Disruption budget',ylabel='Objective (cost units)',
           xlim=(.8,4.2),ylim=(95,165),xticks=[1,2,3,4])

def main():
    out=ROOT/'examples'
    data=pd.read_csv(out/'comparison.csv')
    with plt.rc_context():
        fig,ax=plt.subplots(figsize=(180*MM,100*MM))
        for i,(label,group) in enumerate(data.groupby('strategy',sort=False)):
            ax.plot(group.budget,group.objective,label=label,
                    color=['#FF2222','#1038DB'][i],marker=['o','s'][i],linewidth=[3,1][i])
        axes_labels(ax)
        ax.set_xlabel('Disruption budget',fontsize=14,fontfamily='serif')
        ax.set_ylabel('Objective (cost units)',fontsize=10,fontfamily='sans-serif')
        ax.grid(True,color='#999999',linewidth=1)
        ax.legend(loc='upper left',fontsize=10)
        fig.savefig(out/'before.png',dpi=180,bbox_inches='tight',facecolor='white')
        plt.close(fig)
    apply_style()
    fig,ax=plt.subplots(figsize=(180*MM,100*MM))
    clean(ax)
    for i,(label,group) in enumerate(data.groupby('strategy',sort=False)):
        ax.plot(group.budget,group.objective,label=label,color=color(label,i),
                marker=['o','s'][i],linestyle=['-','--'][i])
    axes_labels(ax)
    ax.legend(loc='lower left',bbox_to_anchor=(0,1.015),ncol=2,frameon=False)
    export_figure(fig,out,'after')
    print('Reproduced before.png and after.png/.pdf/.svg from comparison.csv')

if __name__=='__main__':
    main()
