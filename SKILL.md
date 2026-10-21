---
name: research-figure-assistant
description: 科研绘图辅助。根据真实CSV、Excel或计算日志，用Python/Matplotlib选择并绘制清晰、规范、可复用的论文图表；沿用蓝绿/橙/紫配色、统一字体图例、紧凑版式，输出预览与600 DPI PNG、PDF、SVG。用户说“科研绘图辅助”、科研图美化、敏感性分析图、成本分解、热力图、算法收敛、统一论文风格或可复现绘图时使用；支持仅含图像与方法说明的脱敏HTML作品预览。
---

# 科研绘图辅助

根据真实数据和研究问题确定比较关系，再选图。默认沿用本skill固定风格；服从当次期刊、术语和排版要求。用Python绘制数据图，不用图像生成模型生成或改写科学数值。

## 调用约定

按[任务输入与输出](references/task-contract.md)提取输入并交付结果。只在用户要求时记录调用与反馈。

## 按需读取

- 读[图形选择](references/chart-selection.md)，保持信息与结论集中。
- 读[视觉规范](references/style.md)，落实配色、字体、尺寸和图例。
- 交付前读[验证与公开预览](references/validation.md)。
- 说明参考或公开分享时读[来源与许可](references/sources.md)。

## 执行流程

1. **确认数据口径。** 读取CSV、Excel或日志，记录字段、单位、样本量、基准和缺失值。不从截图猜精确数据；缺数据时说明缺项，继续不依赖数据的结构设计。人工示例明确标为演示。
2. **确定核心比较。** 区分趋势、构成、相对变化、方案切换。共享参数的趋势与数量/策略图保留在同一图组，不为增加图数拆散信息。用户只改标签时保留其余内容。
3. **保留变换依据。** 原始值与派生值分开，保存比例分母、聚合、缩放公式和实际绘图表。区分正支出与相对基准节省；不把准备/启动正成本误画成负支出。
4. **Python实现。** 复用`scripts/paper_style.py`中的`apply_style`、`COLORS`和`export_figure`。用`scripts/plot_csv.py`起步；自定义复杂图组而非强套模板。
5. **核对并看图。** 检查唯一键、排序、单位、分母和图例，再实际查看PNG及必要的PDF渲染。排查重叠、裁切、误导色阶和白边。区分重画已有CSV与重新求解优化问题。
6. **按阶段交付。** 只要预览时先给预览，不强附长解读。要复现时提供必要输入、入口、依赖、实际绘图表、检查记录与输出，清除缓存/旧图。公开HTML仅包含允许公开的图片、方法和来源，不嵌入私有源码数据。

## 复用入口

安装`assets/requirements.txt`中的依赖。`<skill-dir>`替换为本技能绝对目录。

```bash
python <skill-dir>/scripts/plot_csv.py line --input results.csv --x budget --y objective --group strategy --xlabel 'Disruption budget' --ylabel 'Objective (USD million)' --outdir Figure --name Sensitivity
python <skill-dir>/scripts/plot_csv.py heatmap --input grid.csv --x cost_multiplier --y profit_multiplier --value objective --xlabel 'Protection cost multiplier' --ylabel 'Transfer profit multiplier' --outdir Figure --name Grid
python <skill-dir>/scripts/plot_csv.py convergence --input outer.csv --x outer_iteration --lower LB --upper UB --inner inner_iterations --inner-log inner.csv --outdir Figure --name Convergence
```

另支持`bar`、`stacked`、`cost-comparison`；用各子命令`--help`查看字段。收敛入口保留原量纲；显式`--scale`才进行数值缩放，须同步写单位。局部放大、类别区域和复杂子图按研究关系编写。

## 固定交付规范

- 默认无图内总标题，用子图字母和外部图注组织。
- 导出600 DPI PNG、矢量PDF/SVG；同一个紧边界供三格式使用，约1 mm缓冲。DPI不代表已裁边。
- 将实际绘图表存入Results/Plot，记录相对来源名、SHA-256和转换。通用入口默认放在`<outdir>/Results/Plot`；不覆盖原始数据。
- 没有禁用复用的对照运行时，不把场景计数差包装成算法加速实验。
- 区分参考原则与个人设计；未核对具体期刊或色盲可读性时不宣称全面合规。

## 脱敏HTML

```bash
python <skill-dir>/scripts/gallery.py --images Figure/*.png --out Portfolio.html
```

只接受PNG/JPEG/WebP像素图，重新编码并内嵌。可编辑默认的简短方法与来源文案。不得夹带私有CSV、模型、Python源码、参数/日志JSON、压缩包及其链接，包括隐藏标签、注释、脚本字符串或data URL。HTML正常界面代码不属于Python研究源码。用户允许公开真实图片时才使用，否则确认范围或使用明确标注的演示图。

本skill只含通用程序和人工构造示例，不包含个人模型与实验结果。用以下入口验证模板后，实际查看输出；不要把示例数值当研究证据。

```bash
python <skill-dir>/scripts/demo.py --outdir demo-output
```
