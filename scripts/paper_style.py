"""Reusable original scientific-figure style; no research data included."""
from pathlib import Path
import hashlib
import json
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

MM=1/25.4
COLORS={'primary':'#167D9A','secondary':'#C87538','third':'#7267A8',
        'Rerouting':'#167D9A','Recovery':'#C87538','Protection':'#167D9A',
        'Transfer':'#C87538','Acquisition':'#7267A8','Shortage':'#485B70',
        'Procurement':'#55A3B2','Delivery':'#9BA5AD','inner':'#93A6B4',
        'text':'#252C34','baseline':'#7E8B95'}
PALETTE=['#167D9A','#C87538','#7267A8','#485B70','#55A3B2','#9BA5AD']
HATCHES={'Rerouting':'///','Recovery':'..'}

def apply_style():
    plt.style.use(str(Path(__file__).resolve().parents[1]/'assets/paper.mplstyle'))

def color(label,index=0):
    return COLORS.get(str(label),PALETTE[index%len(PALETTE)])

def clean(ax,grid=True):
    if grid:ax.grid(axis='y',color='#D8DFE4',lw=.5,ls=(0,(2,3)))
    ax.set_axisbelow(True)

def export_figure(fig,outdir,name,dpi=600):
    if Path(name).name!=name or name in ('','.','..'):raise ValueError('Use a simple output name')
    out=Path(outdir);out.mkdir(parents=True,exist_ok=True)
    fig.set_dpi(dpi);fig.canvas.draw()
    bbox=fig.get_tightbbox(fig.canvas.get_renderer()).padded(.04)
    for ext in ['png','pdf','svg']:
        payload=io.BytesIO()
        fig.savefig(payload,format=ext,dpi=dpi,bbox_inches=bbox,
                    pad_inches=0,facecolor='white',transparent=False)
        temporary=out/f'{name}.{ext}.tmp'
        temporary.write_bytes(payload.getvalue());temporary.replace(out/f'{name}.{ext}')
    with Image.open(out/f'{name}.png') as source:im=source.convert('RGB')
    im.save(out/f'{name}.png',dpi=(dpi,dpi))
    a=np.asarray(im);yy,xx=np.where(np.any(a<245,axis=2))
    fonts=[t.get_fontsize() for t in fig.findobj(matplotlib.text.Text) if t.get_visible() and t.get_text()]
    result={'name':name,'png_pixels':[im.width,im.height],'dpi':dpi,
            'page_mm':[round(bbox.width*25.4,3),round(bbox.height*25.4,3)],
            'font_pt':[min(fonts),max(fonts)] if fonts else [],
            'visible_white_edges_px':[int(xx.min()),int(yy.min()),int(im.width-1-xx.max()),int(im.height-1-yy.max())] if len(xx) else [],
            'visual_review_required':True}
    (out/f'{name}_export.json').write_text(json.dumps(result,indent=2))
    plt.close(fig)
    return result

def source_info(path):
    p=Path(path)
    return {'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
