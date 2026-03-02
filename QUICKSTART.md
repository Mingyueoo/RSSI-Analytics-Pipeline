# 快速开始指南

## 1. 检查配置

首先测试配置文件是否正常：

```bash
python test_config.py
```

如果看到 "OK - All tests passed!" 说明配置正常。

## 2. 准备数据

确保以下数据文件存在于 `data/raw/` 目录：

- `rssi_history.csv` - RSSI 日志数据
- `ground_truth.csv` - Ground Truth 数据
- `battery_usage.csv` - 电池使用数据（可选）
- `modeAB_C.csv` - 模式分析数据（可选）

## 3. 运行分析

### 方式一：运行完整流程（推荐）

```bash
python main.py
```

这将依次执行：
1. 数据加载和对齐
2. RSSI 可视化分析
3. 电池使用分析
4. 模式性能分析

### 方式二：分步运行

```bash
# 步骤 1: 数据加载
python main.py data

# 步骤 2: RSSI 分析
python main.py rssi

# 步骤 3: 电池分析
python main.py battery

# 步骤 4: 模式分析
python main.py mode
```

## 4. 查看结果

分析完成后，查看以下目录：

- **处理后的数据**: `data/processed/`
  - `evaluation_results.csv`
  - `rssi_statistics_by_trial_device.csv`
  - `rssi_trial_summary.csv`
  - 等等

- **可视化图表**: `results/plots/`
  - `rssi_device_trial_analysis.png`
  - `battery_drain_by_device_and_scenario.png`
  - `detection_rate_by_mode.png`
  - 等等

- **分析报告**: `results/reports/`
  - `rssi_analysis_report.md`

## 5. 自定义配置

编辑 `config/config.yaml` 来自定义：

### 修改路径
```yaml
paths:
  raw_data_dir: "your/custom/path"
```

### 添加新设备
```yaml
devices:
  "your-device-uuid": "Your Device Name"
```

### 修改颜色
```yaml
plotting:
  colors:
    primary: "#YOUR_COLOR"
```

## 常见问题

### Q: 提示找不到数据文件
**解决**: 检查 `data/raw/` 目录是否有数据文件

### Q: 提示找不到模块
**解决**: 确保在项目根目录运行命令

### Q: 某个分析模块失败
**解决**: 可以跳过该模块，单独运行其他模块

## 获取帮助

```bash
python main.py help
```

## 项目结构

```
Orbits/
├── config/config.yaml    # 配置文件
├── data/
│   ├── raw/             # 原始数据
│   └── processed/       # 处理后数据
├── results/
│   ├── plots/           # 图表
│   └── reports/         # 报告
├── src/                 # 源代码
├── main.py              # 主程序
└── test_config.py       # 配置测试
```

## 下一步

- 查看 `README.md` 了解详细文档
- 查看 `CHANGES.md` 了解所有修改
- 根据需要修改 `config/config.yaml`
