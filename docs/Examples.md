# 案例与调用｜科研绘图辅助

## 一、问题现状

临时设置容易使线宽、字体、网格和图例缺少一致规范。这里使用八条人工构造记录生成修改前后图，两图数据、单位和坐标范围相同；“修改前”为专门构造的临时设置示例。

## 二、实现与调用

| 临时设置 | 共享规范 |
| --- | --- |
| ![临时设置示例](../examples/before.png) | ![统一样式示例](../examples/after.png) |

运行 `python examples/compare.py` 复现对照，数据见 [comparison.csv](../examples/comparison.csv)。版本 1.2 另按 [调用任务](../examples/session-01/task.md) 实际运行通用折线入口，保留 [PNG](../examples/session-01/Skill_run.png)、[PDF](../examples/session-01/Skill_run.pdf)、[SVG](../examples/session-01/Skill_run.svg)、[实际绘图表](../examples/session-01/Results/Plot/Skill_run.csv) 与 [来源记录](../examples/session-01/Results/Plot/Skill_run.json)。

## 三、改进与判断

固定规则统一了颜色、字体、线型与图例；同一输入可重新生成多格式图形，绘图表与来源记录可用于核对。运行情况见 [复核](../examples/session-01/review.md) 和 [记录](../examples/session-01/run.json)。下一轮观察真实数据更新后的返工，而后决定是否扩展输入能力，见 [复盘](Retrospective.md)。
