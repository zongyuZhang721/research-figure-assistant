"""Create and render artificial examples; never substitutes for research results."""
import argparse
from pathlib import Path
import subprocess
import sys
import pandas as pd

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--outdir',type=Path,default=Path('demo-output'));a=p.parse_args()
    a.outdir.mkdir(parents=True,exist_ok=True);here=Path(__file__).resolve().parent
    fixtures={
        'line':pd.DataFrame([{'budget':x,'objective':100+x*3+(8 if s=='B' else 0),'series':s} for s in ['A','B'] for x in range(1,5)]),
        'stacked':pd.DataFrame([{'condition':x,'component':c,'cost':10*x+j*2} for x in [1,2,3] for j,c in enumerate(['Acquisition','Shortage'])]),
        'heatmap':pd.DataFrame([{'x':x,'y':y,'value':100+x*3-y*2} for x in [.4,1.,1.6] for y in [.4,1.,1.6]]),
        'cost-comparison':pd.DataFrame([{'condition':x,'component':c,'without_cost':100 if c=='Shortage' else 0,'with_cost':100-x*8 if c=='Shortage' else 5+x} for x in [1,2,3] for c in ['Shortage','Preparation']]),
        'convergence':pd.DataFrame({'outer_iteration':list(range(1,10)),'LB':[20,40,70,85,93,96,98,99,100],'UB':[125,120,115,110,105,103,102,101,100],'inner_iterations':[1,1,2,2,3,2,3,2,1]})}
    flags={'line':['--x','budget','--y','objective','--group','series'],
           'stacked':['--x','condition','--y','cost','--component','component'],
           'heatmap':['--x','x','--y','y','--value','value'],
           'cost-comparison':['--x','condition','--component','component'],
           'convergence':['--x','outer_iteration','--inner','inner_iterations']}
    for name,df in fixtures.items():
        f=a.outdir/f'artificial_{name}.csv';df.to_csv(f,index=False)
        subprocess.run([sys.executable,str(here/'plot_csv.py'),name,'--input',str(f),'--outdir',str(a.outdir),'--name','Demo_'+name,*flags[name]],check=True)
    subprocess.run([sys.executable,str(here/'plot_csv.py'),'bar','--input',str(a.outdir/'artificial_line.csv'),'--outdir',str(a.outdir),'--name','Demo_bar','--x','budget','--y','objective','--group','series'],check=True)
    subprocess.run([sys.executable,str(here/'gallery.py'),'--images',*[str(p) for p in sorted(a.outdir.glob('Demo_*.png'))],'--out',str(a.outdir/'Demo.html'),'--demo'],check=True)

if __name__=='__main__':main()
