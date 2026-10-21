"""Generic CSV plotting. Run a chart subcommand with --help for its schema."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from paper_style import apply_style,export_figure,source_info,color,clean,MM,COLORS

def require(df,columns):
    for c in columns:
        if c not in df:raise ValueError(f'Missing column: {c}')
        if df[c].isna().any():raise ValueError(f'Missing values: {c}')

def main():
    p=argparse.ArgumentParser(description=__doc__)
    subs=p.add_subparsers(dest='kind',required=True)
    for kind in ['line','bar','stacked','heatmap','cost-comparison','convergence']:
        a=subs.add_parser(kind)
        a.add_argument('--input',required=True,type=Path)
        a.add_argument('--outdir',type=Path,default=Path('Figure'))
        a.add_argument('--name',default=kind)
        a.add_argument('--x',required=True)
        a.add_argument('--xlabel',default=None);a.add_argument('--ylabel',default=None)
        a.add_argument('--scale',type=float,default=1.,help='Divide plotted amounts by this positive factor')
        a.add_argument('--width',type=float,default=180.);a.add_argument('--height',type=float,default=100.)
        if kind in ['line','bar','stacked']:a.add_argument('--y',required=True)
        if kind in ['line','bar']:a.add_argument('--group',default=None)
        if kind=='heatmap':
            a.add_argument('--y',required=True);a.add_argument('--value',required=True)
        if kind in ['stacked','cost-comparison']:a.add_argument('--component',required=True)
        if kind=='cost-comparison':
            a.add_argument('--with-col',default='with_cost');a.add_argument('--without-col',default='without_cost')
        if kind=='convergence':
            a.add_argument('--lower',default='LB');a.add_argument('--upper',default='UB')
            a.add_argument('--inner',default=None);a.add_argument('--inner-log',type=Path,default=None)
    args=p.parse_args()
    if args.scale<=0:raise ValueError('--scale must be positive')
    apply_style();df=pd.read_csv(args.input);notes={'source':source_info(args.input),'scale_divisor':args.scale,'chart':args.kind}
    require(df,[args.x]);plotted=df.copy()
    fig,ax=plt.subplots(figsize=(args.width*MM,args.height*MM));clean(ax)
    if args.kind in ['line','bar']:
        require(df,[args.y]+([args.group] if args.group else []))
        key=[args.x]+([args.group] if args.group else [])
        if df.duplicated(key).any():raise ValueError('Duplicate x/group keys; resolve before plotting')
        groups=list(df.groupby(args.group,sort=False)) if args.group else [('Result',df)]
        if args.kind=='line':
            for i,(label,q) in enumerate(groups):
                q=q.sort_values(args.x);ax.plot(q[args.x],q[args.y]/args.scale,
                    color=color(label,i),marker=['o','s','^','D'][i%4],ls=['-','--',':','-.'][i%4],label=str(label))
        else:
            xs=list(dict.fromkeys(df[args.x]));width=.75/len(groups)
            for i,(label,q) in enumerate(groups):
                values=q.set_index(args.x).reindex(xs)[args.y]
                if values.isna().any():raise ValueError('Incomplete group grid')
                ax.bar(np.arange(len(xs))+(i-(len(groups)-1)/2)*width,values/args.scale,
                       width=width,color=color(label,i),label=str(label))
            ax.set_xticks(range(len(xs)),[str(x) for x in xs]);ax.set_ylim(bottom=min(0,float(df[args.y].min()/args.scale)))
        plotted[args.y+'_plot']=plotted[args.y]/args.scale
        if args.group:ax.legend(loc='lower left',bbox_to_anchor=(0,1.015),ncol=min(3,len(groups)),frameon=False)
    elif args.kind=='stacked':
        require(df,[args.component,args.y])
        if df.duplicated([args.x,args.component]).any():raise ValueError('Duplicate condition/component')
        matrix=df.pivot(index=args.x,columns=args.component,values=args.y)
        if matrix.isna().any().any():raise ValueError('Incomplete cost component grid')
        if (matrix<0).any().any():raise ValueError('Absolute stacked costs must be nonnegative; use explicit signed design for profits')
        bottom=np.zeros(len(matrix))
        for i,c in enumerate(matrix):
            v=matrix[c].to_numpy()/args.scale;ax.bar(range(len(matrix)),v,bottom=bottom,label=str(c),color=color(c,i),edgecolor='white',lw=.3);bottom+=v
        ax.set_xticks(range(len(matrix)),[str(x) for x in matrix.index]);ax.set_ylim(bottom=0)
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.015),ncol=3,frameon=False)
        plotted[args.y+'_plot']=plotted[args.y]/args.scale
    elif args.kind=='heatmap':
        require(df,[args.y,args.value])
        if df.duplicated([args.x,args.y]).any():raise ValueError('Duplicate grid cells')
        grid=df.pivot(index=args.y,columns=args.x,values=args.value).sort_index().sort_index(axis=1)
        if grid.isna().any().any():raise ValueError('Incomplete grid; do not fill with fabricated zeros')
        xs=grid.columns.to_numpy(dtype=float);ys=grid.index.to_numpy(dtype=float)
        def edges(v):
            return np.array([v[0]-.5,v[0]+.5]) if len(v)==1 else np.r_[v[0]-(v[1]-v[0])/2,(v[:-1]+v[1:])/2,v[-1]+(v[-1]-v[-2])/2]
        vals=grid.to_numpy()/args.scale
        if vals.min()<0<vals.max():
            lim=np.abs(vals).max();cmap='RdBu_r';kw={'vmin':-lim,'vmax':lim}
        else:cmap=LinearSegmentedColormap.from_list('paper',['#F0F5F6','#C0DCE2','#75AAB9','#24697E']);kw={}
        ax.grid(False);im=ax.pcolormesh(edges(xs),edges(ys),vals,cmap=cmap,edgecolors='white',linewidth=.35,**kw)
        ax.set_xticks(xs);ax.set_yticks(ys)
        cb=fig.colorbar(im,ax=ax,orientation='horizontal',pad=.18,fraction=.045);cb.set_label(args.value)
        plotted[args.value+'_plot']=plotted[args.value]/args.scale
    elif args.kind=='cost-comparison':
        require(df,[args.component,args.with_col,args.without_col])
        if df.duplicated([args.x,args.component]).any():raise ValueError('Duplicate condition/component')
        delta=df[args.without_col]-df[args.with_col]
        plotted['saved']=delta.clip(lower=0);plotted['added']=-delta.clip(upper=0)
        plotted['saved_plot']=plotted.saved/args.scale;plotted['added_plot']=plotted.added/args.scale
        xs=list(dict.fromkeys(df[args.x]));components=list(dict.fromkeys(df[args.component]))
        if len(df)!=len(xs)*len(components):raise ValueError('Incomplete component grid')
        pos=np.arange(len(xs));saved=np.zeros(len(xs));added=np.zeros(len(xs));perc=[]
        for i,c in enumerate(components):
            q=plotted[plotted[args.component]==c].set_index(args.x).reindex(xs)
            ax.barh(pos-.18,q.saved_plot,left=saved,height=.29,color=color(c,i),label=str(c),edgecolor='white',lw=.3)
            ax.barh(pos+.18,q.added_plot,left=added,height=.29,color=color(c,i),edgecolor='white',lw=.3)
            saved+=q.saved_plot.to_numpy();added+=q.added_plot.to_numpy()
        for x in xs:
            q=df[df[args.x]==x];baseline=q[args.without_col].sum();benefit=(q[args.without_col]-q[args.with_col]).sum()
            perc.append(100*benefit/baseline if baseline!=0 else np.nan)
        for i,pct in enumerate(perc):ax.text(1.02,i,'undefined' if pd.isna(pct) else f'{pct:.2f}%',transform=ax.get_yaxis_transform(),va='center',fontsize=8)
        for i in pos:
            ax.text(-.02,i-.18,'Saved',transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=7.5)
            ax.text(-.02,i+.18,'Added',transform=ax.get_yaxis_transform(),ha='right',va='center',fontsize=7.5)
        ax.set_yticks(pos,[str(x) for x in xs]);ax.tick_params(axis='y',pad=35,length=0);ax.invert_yaxis();ax.set_xlim(left=0)
        ax.text(1.02,1.02,'Net saving',transform=ax.transAxes,fontsize=8)
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.06),ncol=3,frameon=False)
        notes['formula']='delta=without-with; saved=max(delta,0); added=max(-delta,0); percentage=sum(delta)/sum(without)*100'
        notes['net_saving_pct']=[None if pd.isna(x) else float(x) for x in perc]
    else:
        require(df,[args.lower,args.upper]+([args.inner] if args.inner else []))
        if df[args.x].duplicated().any():raise ValueError('Duplicate outer iterations')
        df=df.sort_values(args.x);plotted=df.copy()
        if (df[args.lower]>df[args.upper]+1e-7).any():raise ValueError('LB exceeds UB; verify definitions')
        if args.inner_log:
            if not args.inner:raise ValueError('--inner-log requires --inner')
            log=pd.read_csv(args.inner_log);require(log,[args.x])
            counts=log.groupby(args.x).size().reindex(df[args.x],fill_value=0).to_numpy()
            if not np.array_equal(counts,df[args.inner].to_numpy()):raise ValueError('Inner log counts do not match outer log')
            notes['inner_log']=source_info(args.inner_log)
        if args.inner:
            if ((df[args.inner]<0)|(df[args.inner]%1!=0)).any():raise ValueError('Inner counts must be nonnegative integers')
            plt.close(fig);fig=plt.figure(figsize=(100*MM,104*MM));gs=fig.add_gridspec(2,1,height_ratios=[3.5,1],hspace=.18)
            ax=fig.add_subplot(gs[0]);b=fig.add_subplot(gs[1],sharex=ax);clean(ax);clean(b)
            b.bar(df[args.x],df[args.inner],color=COLORS['inner'],width=.7,edgecolor='white',lw=.3)
            b.set(xlabel=args.xlabel or 'Outer iteration',ylabel='Inner iterations',ylim=(0,max(1,df[args.inner].max()*1.18)))
            ax.tick_params(labelbottom=False)
        ax.plot(df[args.x],df[args.lower]/args.scale,color=COLORS['primary'],marker='o',label='Lower bound')
        ax.plot(df[args.x],df[args.upper]/args.scale,color=COLORS['secondary'],marker='s',ls='--',label='Upper bound')
        ax.legend(loc='lower left',bbox_to_anchor=(0,1.01),frameon=False,ncol=2)
        if len(df)>=6:
            tail=df.tail(max(3,len(df)//3));ins=ax.inset_axes([.42,.12,.55,.36]);clean(ins)
            ins.plot(tail[args.x],tail[args.lower]/args.scale,color=COLORS['primary'],marker='o',ms=2)
            ins.plot(tail[args.x],tail[args.upper]/args.scale,color=COLORS['secondary'],ls='--',marker='s',ms=2)
            ins.tick_params(labelsize=7)
        plotted[args.lower+'_plot']=plotted[args.lower]/args.scale;plotted[args.upper+'_plot']=plotted[args.upper]/args.scale
        notes['terminal_gap']=float(df[args.upper].iloc[-1]-df[args.lower].iloc[-1])
        notes['convergence_claim']='Not assessed without a user-provided stopping rule'
    if not(args.kind=='convergence' and args.inner):ax.set_xlabel(args.xlabel or ('Cost savings / additional costs' if args.kind=='cost-comparison' else args.x))
    ax.set_ylabel(args.ylabel or ('Objective' if args.kind=='convergence' else ('Condition' if args.kind=='cost-comparison' else args.y)))
    results=args.outdir/'Results/Plot';results.mkdir(parents=True,exist_ok=True)
    plotted.to_csv(results/f'{args.name}.csv',index=False,encoding='utf-8-sig')
    (results/f'{args.name}.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2,allow_nan=False))
    export_figure(fig,args.outdir,args.name)
    print(f'Saved {args.name}: PNG 600 DPI, PDF, SVG and actual plotting data.')

if __name__=='__main__':main()
