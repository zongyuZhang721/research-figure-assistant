# 调用任务与命令

读取 ../comparison.csv，比较两种策略随 budget 变化的 objective。按统一风格绘制折线图，纵轴为演示成本单位；导出 PNG、PDF、SVG，并保存实际绘图表。

在项目根目录执行的命令：

```bash
python scripts/plot_csv.py line --input examples/comparison.csv --x budget --y objective --group strategy --xlabel "Disruption budget" --ylabel "Objective (cost units)" --outdir examples/session-01 --name Skill_run
```

该命令已实际运行；输入是八条人工构造记录。执行结果与复核见本目录 run.json、review.md。
