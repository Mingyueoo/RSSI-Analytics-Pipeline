# @Version :1.0
# @Author  : Mingyue
# @File    : mode_analyzer.py.py
# @Time    : 01/03/2026 21:05
"""
Mode Performance Analysis Visualization
======================================

This script generates scientific visualizations for mode performance analysis
including detection rates, latency distributions, and error metrics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import warnings
from utils import load_config

warnings.filterwarnings('ignore')

# Global config variable
CONFIG = None
SOFT_COLORS = None


def initialize_plotting_style(config=None):
    """初始化绘图样式和颜色"""
    global CONFIG, SOFT_COLORS
    
    if config is None:
        CONFIG = load_config()
    else:
        CONFIG = config
    
    # Set scientific plotting style from config
    plt.style.use(CONFIG['plotting']['style'])
    plt.rcParams.update({
        'font.size': 11,
        'axes.titlesize': 13,
        'axes.labelsize': 11,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10,
        'figure.titlesize': 15,
        'axes.linewidth': 1.2,
        'grid.alpha': 0.3,
        'lines.linewidth': 2,
        'lines.markersize': 6
    })
    
    # Soft color palette from config
    SOFT_COLORS = {
        'mode_ab': CONFIG['plotting']['colors']['primary'],
        'mode_c': CONFIG['plotting']['colors']['secondary'],
        'primary': CONFIG['plotting']['colors']['success'],
        'secondary': CONFIG['plotting']['colors']['danger'],
        'accent': '#C7A3D1',
        'neutral': '#D4A574',
        'light': '#F7F7F7',
        'dark': '#2C3E50'
    }


def load_and_preprocess_data(config=None):
    """
    Load and preprocess the mode analysis data

    Args:
        config (dict): Configuration dictionary
        
    Returns:
        pd.DataFrame: Preprocessed data
    """
    if config is None:
        config = CONFIG if CONFIG is not None else load_config()
    
    print("Loading mode analysis data...")

    try:
        data_path = f"{config['paths']['processed_data_dir']}/modeAB_C.csv"
        df = pd.read_csv(data_path)
        print(f"✓ Data loaded successfully: {len(df)} records")

        # Create device labels from config
        device_mapping = config['devices']
        df['device_label'] = df['device_uuid'].map(device_mapping)

        # Create scenario labels from config
        scenario_mapping = config['scenarios']
        df['scenario_label'] = df['scenario'].map(scenario_mapping)

        # Handle missing values for mode C (where no detection occurred)
        df['mae'] = pd.to_numeric(df['mae'], errors='coerce')
        df['rmse'] = pd.to_numeric(df['rmse'], errors='coerce')
        df['avg_detection_latency'] = pd.to_numeric(df['avg_detection_latency'], errors='coerce')

        print(f"✓ Data preprocessing completed")
        print(f"  - Devices: {df['device_label'].nunique()}")
        print(f"  - Modes: {df['mode_group'].nunique()}")
        print(f"  - Scenarios: {df['scenario_label'].nunique()}")

        return df

    except FileNotFoundError:
        print(f"✗ Error: File {data_path} not found")
        return None
    except Exception as e:
        print(f"✗ Error loading data: {str(e)}")
        return None


def plot_detection_rate_by_mode(df):
    """
    Generate detection rate comparison by mode

    Args:
        df (pd.DataFrame): Preprocessed data

    Returns:
        str: Path to saved figure
    """
    print("Generating detection rate by mode plot...")

    # Calculate detection rate statistics by mode
    mode_stats = df.groupby('mode_group')['detection_rate'].agg(['mean', 'std', 'count']).round(2)

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    # Plot 1: Detection rate by mode (overall)
    modes = mode_stats.index
    x_pos = np.arange(len(modes))
    colors = [SOFT_COLORS['mode_ab'], SOFT_COLORS['mode_c']]

    bars = ax1.bar(x_pos, mode_stats['mean'],
                   yerr=mode_stats['std'], capsize=8, alpha=0.8,
                   color=colors, edgecolor='white', linewidth=1.5)

    # Add value labels
    for i, (bar, mean_val, std_val) in enumerate(zip(bars, mode_stats['mean'], mode_stats['std'])):
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width() / 2., height + 2,
                 f'{mean_val:.1f}%', ha='center', va='bottom',
                 fontsize=11, fontweight='bold')
        ax1.text(bar.get_x() + bar.get_width() / 2., height - 5,
                 f'±{std_val:.1f}', ha='center', va='top',
                 fontsize=9, alpha=0.8)

    ax1.set_xlabel('Mode Group', fontweight='bold')
    ax1.set_ylabel('Detection Rate (%)', fontweight='bold')
    ax1.set_title('(a) Overall Detection Rate by Mode', fontweight='bold', pad=15)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(modes)
    ax1.set_ylim(0, 110)
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Detection rate by scenario and mode
    scenario_mode_stats = df.groupby(['scenario_label', 'mode_group'])['detection_rate'].mean().unstack()

    # Create grouped bar plot
    x_pos_scenario = np.arange(len(scenario_mode_stats.index))
    width = 0.35

    bars1 = ax2.bar(x_pos_scenario - width / 2, scenario_mode_stats['AB'], width,
                    label='Mode AB', alpha=0.8, color=SOFT_COLORS['mode_ab'],
                    edgecolor='white', linewidth=1)
    bars2 = ax2.bar(x_pos_scenario + width / 2, scenario_mode_stats['C'], width,
                    label='Mode C', alpha=0.8, color=SOFT_COLORS['mode_c'],
                    edgecolor='white', linewidth=1)

    # Add value labels for bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if not np.isnan(height):
                ax2.text(bar.get_x() + bar.get_width() / 2., height + 2,
                         f'{height:.0f}%', ha='center', va='bottom',
                         fontsize=9, fontweight='bold')

    ax2.set_xlabel('Experimental Scenario', fontweight='bold')
    ax2.set_ylabel('Detection Rate (%)', fontweight='bold')
    ax2.set_title('(b) Detection Rate by Scenario and Mode', fontweight='bold', pad=15)
    ax2.set_xticks(x_pos_scenario)
    ax2.set_xticklabels(scenario_mode_stats.index, rotation=45, ha='right')
    ax2.legend(fontsize=10)
    ax2.set_ylim(0, 110)
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save figure
    config = CONFIG if CONFIG is not None else load_config()
    output_path = f"{config['paths']['plots_dir']}/detection_rate_by_mode.png"
    plt.savefig(output_path, dpi=config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"✓ Detection rate plot saved: {output_path}")
    return output_path


def plot_latency_distribution_by_mode(df):
    """
    Generate latency distribution analysis by mode

    Args:
        df (pd.DataFrame): Preprocessed data

    Returns:
        str: Path to saved figure
    """
    print("Generating latency distribution by mode plot...")

    # Filter out missing latency values
    latency_data = df.dropna(subset=['avg_detection_latency'])

    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Latency Distribution Analysis by Mode', fontsize=15, fontweight='bold', y=0.98)

    # Plot 1: Box plot of latency by mode
    mode_latency_data = [latency_data[latency_data['mode_group'] == mode]['avg_detection_latency'].values
                         for mode in latency_data['mode_group'].unique()]
    mode_labels = latency_data['mode_group'].unique()

    box_plot = ax1.boxplot(mode_latency_data, labels=mode_labels, patch_artist=True)
    colors = [SOFT_COLORS['mode_ab'], SOFT_COLORS['mode_c']]

    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax1.set_xlabel('Mode Group', fontweight='bold')
    ax1.set_ylabel('Average Detection Latency (s)', fontweight='bold')
    ax1.set_title('(a) Latency Distribution by Mode', fontweight='bold')
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Latency vs Scenario
    scenario_latency = latency_data.groupby(['scenario_label', 'mode_group'])['avg_detection_latency'].mean().unstack()

    x_pos = np.arange(len(scenario_latency.index))
    width = 0.35

    bars1 = ax2.bar(x_pos - width / 2, scenario_latency['AB'], width,
                    label='Mode AB', alpha=0.8, color=SOFT_COLORS['mode_ab'],
                    edgecolor='white', linewidth=1)
    bars2 = ax2.bar(x_pos + width / 2, scenario_latency['C'], width,
                    label='Mode C', alpha=0.8, color=SOFT_COLORS['mode_c'],
                    edgecolor='white', linewidth=1)

    ax2.set_xlabel('Experimental Scenario', fontweight='bold')
    ax2.set_ylabel('Average Detection Latency (s)', fontweight='bold')
    ax2.set_title('(b) Latency by Scenario and Mode', fontweight='bold')
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels(scenario_latency.index, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Latency variability (standard deviation)
    latency_std = latency_data.groupby(['scenario_label', 'mode_group'])['std_detection_latency'].mean().unstack()

    bars1 = ax3.bar(x_pos - width / 2, latency_std['AB'], width,
                    label='Mode AB', alpha=0.8, color=SOFT_COLORS['mode_ab'],
                    edgecolor='white', linewidth=1)
    bars2 = ax3.bar(x_pos + width / 2, latency_std['C'], width,
                    label='Mode C', alpha=0.8, color=SOFT_COLORS['mode_c'],
                    edgecolor='white', linewidth=1)

    ax3.set_xlabel('Experimental Scenario', fontweight='bold')
    ax3.set_ylabel('Latency Standard Deviation (s)', fontweight='bold')
    ax3.set_title('(c) Latency Variability by Scenario and Mode', fontweight='bold')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(latency_std.index, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # Plot 4: Latency range (max - min)
    latency_range_data = []
    for mode in ['AB', 'C']:
        mode_data = latency_data[latency_data['mode_group'] == mode]
        ranges = mode_data['max_detection_latency'] - mode_data['min_detection_latency']
        latency_range_data.append(ranges.dropna().values)

    box_plot = ax4.boxplot(latency_range_data, labels=['AB', 'C'], patch_artist=True)
    for patch, color in zip(box_plot['boxes'], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax4.set_xlabel('Mode Group', fontweight='bold')
    ax4.set_ylabel('Latency Range (s)', fontweight='bold')
    ax4.set_title('(d) Latency Range Distribution by Mode', fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save figure
    config = CONFIG if CONFIG is not None else load_config()
    output_path = f"{config['paths']['plots_dir']}/latency_distribution_by_mode.png"
    plt.savefig(output_path, dpi=config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"✓ Latency distribution plot saved: {output_path}")
    return output_path


def plot_error_estimation_by_mode(df):
    """
    Generate error estimation analysis (MAE/RMSE) by mode

    Args:
        df (pd.DataFrame): Preprocessed data

    Returns:
        str: Path to saved figure
    """
    print("Generating error estimation by mode plot...")

    # Filter out missing error values
    error_data = df.dropna(subset=['mae', 'rmse'])

    # Create figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Error Estimation Analysis by Mode (MAE/RMSE)', fontsize=15, fontweight='bold', y=0.98)

    # Plot 1: Overall MAE and RMSE by mode
    mode_error_stats = error_data.groupby('mode_group')[['mae', 'rmse']].agg(['mean', 'std']).round(2)

    modes = mode_error_stats.index
    x_pos = np.arange(len(modes))
    width = 0.35

    # MAE bars
    mae_means = mode_error_stats[('mae', 'mean')].values
    mae_stds = mode_error_stats[('mae', 'std')].values
    bars1 = ax1.bar(x_pos - width / 2, mae_means, width,
                    yerr=mae_stds, capsize=5, label='MAE',
                    alpha=0.8, color=SOFT_COLORS['primary'],
                    edgecolor='white', linewidth=1)

    # RMSE bars
    rmse_means = mode_error_stats[('rmse', 'mean')].values
    rmse_stds = mode_error_stats[('rmse', 'std')].values
    bars2 = ax1.bar(x_pos + width / 2, rmse_means, width,
                    yerr=rmse_stds, capsize=5, label='RMSE',
                    alpha=0.8, color=SOFT_COLORS['secondary'],
                    edgecolor='white', linewidth=1)

    # Add value labels
    for bars, values in [(bars1, mae_means), (bars2, rmse_means)]:
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2., height + height * 0.02,
                     f'{value:.0f}', ha='center', va='bottom',
                     fontsize=10, fontweight='bold')

    ax1.set_xlabel('Mode Group', fontweight='bold')
    ax1.set_ylabel('Error (s)', fontweight='bold')
    ax1.set_title('(a) Overall MAE and RMSE by Mode', fontweight='bold')
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(modes)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: MAE by scenario and mode
    scenario_mae = error_data.groupby(['scenario_label', 'mode_group'])['mae'].mean().unstack()

    x_pos_scenario = np.arange(len(scenario_mae.index))

    bars1 = ax2.bar(x_pos_scenario - width / 2, scenario_mae['AB'], width,
                    label='Mode AB', alpha=0.8, color=SOFT_COLORS['mode_ab'],
                    edgecolor='white', linewidth=1)
    bars2 = ax2.bar(x_pos_scenario + width / 2, scenario_mae['C'], width,
                    label='Mode C', alpha=0.8, color=SOFT_COLORS['mode_c'],
                    edgecolor='white', linewidth=1)

    ax2.set_xlabel('Experimental Scenario', fontweight='bold')
    ax2.set_ylabel('MAE (s)', fontweight='bold')
    ax2.set_title('(b) MAE by Scenario and Mode', fontweight='bold')
    ax2.set_xticks(x_pos_scenario)
    ax2.set_xticklabels(scenario_mae.index, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: RMSE by scenario and mode
    scenario_rmse = error_data.groupby(['scenario_label', 'mode_group'])['rmse'].mean().unstack()

    bars1 = ax3.bar(x_pos_scenario - width / 2, scenario_rmse['AB'], width,
                    label='Mode AB', alpha=0.8, color=SOFT_COLORS['mode_ab'],
                    edgecolor='white', linewidth=1)
    bars2 = ax3.bar(x_pos_scenario + width / 2, scenario_rmse['C'], width,
                    label='Mode C', alpha=0.8, color=SOFT_COLORS['mode_c'],
                    edgecolor='white', linewidth=1)

    ax3.set_xlabel('Experimental Scenario', fontweight='bold')
    ax3.set_ylabel('RMSE (s)', fontweight='bold')
    ax3.set_title('(c) RMSE by Scenario and Mode', fontweight='bold')
    ax3.set_xticks(x_pos_scenario)
    ax3.set_xticklabels(scenario_rmse.index, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3, axis='y')

    # Plot 4: MAE vs RMSE correlation
    for mode in ['AB', 'C']:
        mode_data = error_data[error_data['mode_group'] == mode]
        ax4.scatter(mode_data['mae'], mode_data['rmse'],
                    alpha=0.7, s=60, label=f'Mode {mode}',
                    edgecolors='white', linewidth=1)

    # Add correlation line
    z = np.polyfit(error_data['mae'], error_data['rmse'], 1)
    p = np.poly1d(z)
    ax4.plot(error_data['mae'], p(error_data['mae']),
             "k--", alpha=0.8, linewidth=2, label='Trend Line')

    # Calculate and display correlation
    correlation = error_data['mae'].corr(error_data['rmse'])
    ax4.text(0.05, 0.95, f'R = {correlation:.3f}', transform=ax4.transAxes,
             fontsize=11, bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

    ax4.set_xlabel('MAE (s)', fontweight='bold')
    ax4.set_ylabel('RMSE (s)', fontweight='bold')
    ax4.set_title('(d) MAE vs RMSE Correlation', fontweight='bold')
    ax4.legend()
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()

    # Save figure
    config = CONFIG if CONFIG is not None else load_config()
    output_path = f"{config['paths']['plots_dir']}/error_estimation_by_mode.png"
    plt.savefig(output_path, dpi=config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"✓ Error estimation plot saved: {output_path}")
    return output_path


def generate_summary_statistics(df):
    """
    Generate and display summary statistics

    Args:
        df (pd.DataFrame): Preprocessed data
    """
    print("\n" + "=" * 60)
    print("MODE PERFORMANCE ANALYSIS SUMMARY")
    print("=" * 60)

    # Overall statistics
    print(f"\nDataset Overview:")
    print(f"- Total records: {len(df)}")
    print(f"- Number of devices: {df['device_label'].nunique()}")
    print(f"- Number of modes: {df['mode_group'].nunique()}")
    print(f"- Number of scenarios: {df['scenario_label'].nunique()}")

    # Detection rate statistics
    print(f"\nDetection Rate Statistics:")
    detection_stats = df.groupby('mode_group')['detection_rate'].agg(['mean', 'std', 'min', 'max']).round(2)
    for mode, stats in detection_stats.iterrows():
        print(
            f"- Mode {mode}: {stats['mean']:.1f}% ± {stats['std']:.1f}% (range: {stats['min']:.1f}% - {stats['max']:.1f}%)")

    # Latency statistics (excluding missing values)
    latency_data = df.dropna(subset=['avg_detection_latency'])
    if len(latency_data) > 0:
        print(f"\nLatency Statistics:")
        latency_stats = latency_data.groupby('mode_group')['avg_detection_latency'].agg(
            ['mean', 'std', 'min', 'max']).round(2)
        for mode, stats in latency_stats.iterrows():
            print(
                f"- Mode {mode}: {stats['mean']:.2f} ± {stats['std']:.2f} s (range: {stats['min']:.2f} - {stats['max']:.2f} s)")

    # Error statistics (excluding missing values)
    error_data = df.dropna(subset=['mae', 'rmse'])
    if len(error_data) > 0:
        print(f"\nError Estimation Statistics:")
        mae_stats = error_data.groupby('mode_group')['mae'].agg(['mean', 'std']).round(2)
        rmse_stats = error_data.groupby('mode_group')['rmse'].agg(['mean', 'std']).round(2)
        for mode in mae_stats.index:
            print(f"- Mode {mode}:")
            print(f"  * MAE: {mae_stats.loc[mode, 'mean']:.2f} ± {mae_stats.loc[mode, 'std']:.2f} s")
            print(f"  * RMSE: {rmse_stats.loc[mode, 'mean']:.2f} ± {rmse_stats.loc[mode, 'std']:.2f} s")

    print("\n" + "=" * 60)


def main(config=None):
    """
    Main function to run mode analysis visualization
    
    Args:
        config (dict): Configuration dictionary
    """
    if config is None:
        config = load_config()
    
    # Initialize plotting style
    initialize_plotting_style(config)
    
    print("Mode Performance Analysis Visualization")
    print("=" * 50)

    # Load and preprocess data
    df = load_and_preprocess_data(config)

    if df is None:
        print("Failed to load data. Exiting.")
        return

    # Generate summary statistics
    generate_summary_statistics(df)

    # Generate all plots
    print("\nGenerating visualizations...")

    print("\n1. Detection Rate Analysis...")
    plot_detection_rate_by_mode(df)

    print("\n2. Latency Distribution Analysis...")
    plot_latency_distribution_by_mode(df)

    print("\n3. Error Estimation Analysis...")
    plot_error_estimation_by_mode(df)

    print("\n" + "=" * 50)
    print("ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 50)

    print(f"\nGenerated Files:")
    print(f"- detection_rate_by_mode.png")
    print(f"- latency_distribution_by_mode.png")
    print(f"- error_estimation_by_mode.png")

    # Display key findings
    print(f"\nKey Findings:")

    # Detection rate comparison
    detection_comparison = df.groupby('mode_group')['detection_rate'].mean()
    if 'AB' in detection_comparison.index and 'C' in detection_comparison.index:
        ab_rate = detection_comparison['AB']
        c_rate = detection_comparison['C']
        print(f"- Detection Rate: Mode AB ({ab_rate:.1f}%) vs Mode C ({c_rate:.1f}%)")
        print(f"- Detection Rate Difference: {abs(ab_rate - c_rate):.1f} percentage points")

    # Latency comparison
    latency_data = df.dropna(subset=['avg_detection_latency'])
    if len(latency_data) > 0:
        latency_comparison = latency_data.groupby('mode_group')['avg_detection_latency'].mean()
        if 'AB' in latency_comparison.index and 'C' in latency_comparison.index:
            ab_latency = latency_comparison['AB']
            c_latency = latency_comparison['C']
            print(f"- Average Latency: Mode AB ({ab_latency:.2f}s) vs Mode C ({c_latency:.2f}s)")

    # Error comparison
    error_data = df.dropna(subset=['mae'])
    if len(error_data) > 0:
        mae_comparison = error_data.groupby('mode_group')['mae'].mean()
        if 'AB' in mae_comparison.index and 'C' in mae_comparison.index:
            ab_mae = mae_comparison['AB']
            c_mae = mae_comparison['C']
            print(f"- MAE: Mode AB ({ab_mae:.2f}s) vs Mode C ({c_mae:.2f}s)")


if __name__ == "__main__":
    main()
