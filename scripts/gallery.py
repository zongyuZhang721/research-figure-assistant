"""Standalone image-only HTML. Inputs must be authorized public raster figures."""
import argparse
import base64
import html
import io
from pathlib import Path
from PIL import Image

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--images',nargs='+',type=Path,required=True)
    p.add_argument('--out',type=Path,default=Path('Portfolio.html'))
    p.add_argument('--title',default='科研可视化 · 清晰、规范、可复用')
    p.add_argument('--demo',action='store_true',help='Visibly label synthetic examples')
    a=p.parse_args()
    content=['<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+html.escape(a.title)+'</title><style>body{margin:0;background:#f3f5f3;color:#172e3c;font:19px/1.8 system-ui,sans-serif}main{max-width:1150px;padding:30px;margin:auto}h1{font-size:38px;line-height:1.4}h2{font-size:27px}article{background:white;padding:24px;border:1px solid #d6e0e3;border-radius:10px;margin:24px 0}img{display:block;width:100%;height:auto;max-height:950px;object-fit:contain}a{color:#167d9a}small{font-size:16px}@media(max-width:600px){main{padding:16px}article{padding:12px}h1{font-size:30px}}</style><main><h1>'+html.escape(a.title)+'</h1><p>根据数据特征选择图形，参考开源科研绘图项目与期刊布局，通过Python实现、效果评估与多轮调整，形成统一的科研可视化工作流。</p>']
    if a.demo:content.append('<p><strong>人工构造示例数据，仅展示绘图功能，不代表研究结果。</strong></p>')
    for i,path in enumerate(a.images,1):
        with Image.open(path) as src:
            if src.format not in ['PNG','JPEG','WEBP']:raise ValueError('Only raster PNG/JPEG/WebP is allowed')
            rgb=src.convert('RGB')
            im=Image.new('RGB',rgb.size,'white');im.paste(rgb)
        buf=io.BytesIO();im.save(buf,format='PNG',dpi=(600,600))
        # Generic titles avoid exposing private input filenames.
        content.append(f'<article><h2>图表 {i:02d}</h2><img alt="图表 {i}" src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}"></article>')
    content.append('<h2>参考与方法</h2><p>借鉴科研图表的字体、图例与紧凑版式原则；根据自身数据重新设计配色与信息结构，并核对数值及多格式导出。</p><p><a href="https://github.com/Alto-R/nature-figure-craft" target="_blank" rel="noopener noreferrer">nature-figure-craft</a> · <a href="https://github.com/garrettj403/SciencePlots" target="_blank" rel="noopener noreferrer">SciencePlots</a></p><small>由「科研绘图辅助」生成。PNG / PDF / SVG 为绘图工作流的输出格式。</small></main></html>')
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text('\n'.join(content),encoding='utf-8')
    print(a.out)

if __name__=='__main__':main()
