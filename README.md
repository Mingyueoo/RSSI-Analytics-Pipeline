# RSSI Data Analysis System

A comprehensive RSSI (Received Signal Strength Indicator) data analysis system designed for processing, analyzing, and visualizing wireless communication experimental data.

## Project Structure

```
Orbits/
├── config/
│   └── config.yaml              # Configuration file (paths, device mapping, plot styles, etc.)
├── data/
│   ├── raw/                     # Raw data directory
│   │   ├── rssi_history.csv
│   │   └── ground_truth.csv
│   └── processed/               # Processed data directory
├── results/
│   ├── plots/                   # Plot output directory
│   └── reports/                 # Report output directory
├── src/
│   ├── __init__.py              # Python package initialization
│   ├── utils.py                 # Utility functions (config loading, etc.)
│   ├── data_loader.py           # Data loading and alignment
│   ├── visualization.py         # RSSI visualization analysis
│   ├── battery_analyzer.py      # Battery usage analysis
│   └── mode_analyzer.py         # Mode performance analysis
├── main.py                      # Main entry point
└── README.md                    # This file
```

## Functional Modules

### 1. Data Loading and Alignment (`data_loader.py`)
- Reads raw RSSI logs and Ground Truth data.
- Performs timestamp alignment (with configurable tolerance).
- Handles data preprocessing and cleaning.

### 2.Handles data preprocessing and cleaning. (`visualization.py`)
- Compares performance across different devices.
- Analyzes individual trial data.
- Conducts scenario-based performance comparisons.
- Generates detailed analysis reports.

### 3. Battery Usage Analysis (`battery_analyzer.py`)
- Compares battery consumption across different devices.
- Analyzes battery performance under various scenarios.
- Provides statistical analysis (Mean, Standard Deviation).

### 4. Mode Performance Analysis (`mode_analyzer.py`)
- Detection rate analysis.
- Latency distribution analysis.
- Error estimation (MAE/RMSE).

## Error estimation (MAE/RMSE).

All settings are centralized in `config/config.yaml` 

```yaml
# Path Configurations
paths:
  raw_data_dir: "data/raw"
  processed_data_dir: "data/processed"
  results_dir: "results"
  plots_dir: "results/plots"
  report_dir: "results/reports"

# Device Mapping
devices:
  "403841af-d006-4ce8-854d-b6ab105f150f": "Device A"
  "bbbe7f51-5630-4df7-bd19-84c2ecea35f3": "Device B"

# Scenario Mapping
scenarios:
  "static_1m_5min": "Static 5min"
  "static_1m_15min": "Static 15min"
  "Doze_mode_1m": "Doze Mode"
  # ...

# Analysis Parameters
analysis:
  time_tolerance_seconds: 1

# Plotting Styles
plotting:
  style: "seaborn-v0_8-whitegrid"
  dpi: 300
  colors:
    primary: "#6BA6CD"
    secondary: "#FFB366"
    success: "#7FCDBB"
    danger: "#FF7F7F"
```

## Usage

### 1. Install Dependencies

```bash
pip install pandas numpy matplotlib seaborn pyyaml
```

### 2. Prepare Data

将原始数据文件放入 `data/raw/` 目录：
- `rssi_history.csv`
- `ground_truth.csv`
- `battery_usage.csv`（Required for battery analysis）
- `modeAB_C.csv`（Required for mode analysis）

### 3. Run Analysis

#### Run Full Pipeline
```bash
python main.py
```

#### Run Individual Modules
```bash
# Data loading only
python main.py data

# RSSI analysis only
python main.py rssi

# Battery analysis only
python main.py battery

# Mode analysis only
python main.py mode
```

#### View Help
```bash
python main.py help
```

### 4. View Help

- **Processed Data**: `data/processed/`
- **Visualization Plots**: `results/plots/`
- **Analysis Reports**: `results/reports/`

## Output Files

### Data Files
- `evaluation_results.csv` - Results of data alignment.
- `rssi_statistics_by_trial_device.csv` - RSSI statistical data.
- `rssi_trial_summary.csv` - Summary of trials.
- `rssi_device_comparison.csv` - Device comparison data.

### Plot Files
- `rssi_device_trial_analysis.png` - Comparison between devices and trials.
- `rssi_scenario_comparison.png` - Scenario comparison.
- `rssi_device_performance_comparison.png` - Device performance comparison.
- `battery_drain_by_device_and_scenario.png` - Battery consumption analysis.
- `device_comparison_across_scenarios.png` - Device comparison across scenarios.
- `trial_analysis_by_device.png` - Trial analysis grouped by device.
- `detection_rate_by_mode.png` - Detection rate by mode.
- `latency_distribution_by_mode.png` - Latency distribution.
- `error_estimation_by_mode.png` - Error estimation analysis.

### Error estimation analysis.
- `rssi_analysis_report.md` - Error estimation analysis.

## Customization

### Modify Paths

Edit the `path` in `config/config.yaml` 


### Add Devices
在 `config/config.yaml` 的 `devices` 部分添加新的 UUID 映射。

### Add Scenarios
在 `config/config.yaml` 的 `scenarios` 部分添加新的场景映射。

### Modify Plotting Styles
在 `config/config.yaml` 的 `plotting` 部分修改样式、DPI 和颜色。

## Development Instructions

### Adding New Analysis Modules

1. Create a new Python file in the `src/` 
2. Use `from utils import load_config` to load settings.
3. Export the new module in `src/__init__.py` .
4. Add the invocation logic in `main.py` .

### Coding Standards

- All paths must use settings from the configuration file.
- Devices and scenarios must use mappings from the configuration file.
- Devices and scenarios must use mappings from the configuration file.
- Functions should ideally accept a `config` parameter (optional).



## Version Information

- **Version Information**: 1.0.0
- **Author**: Mingyue
- **Date**: 2026-03-01

## License

This project is intended for research and educational purposes only.
