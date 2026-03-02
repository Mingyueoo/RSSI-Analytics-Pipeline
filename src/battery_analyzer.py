# @Version :1.0
# @Author  : Mingyue
# @File    : battery_analyzer.py.py
# @Time    : 01/03/2026 21:11
"""
Battery Usage Analysis by Device Across Three Trials
===================================================

This script analyzes battery usage data for Device A and Device B across three trials,
calculating mean and standard deviation for each device in each scenario, and generates
scientific visualizations.

Author: Research Team
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle
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
        'device_a': CONFIG['plotting']['colors']['primary'],
        'device_b': CONFIG['plotting']['colors']['secondary'],
        'primary': CONFIG['plotting']['colors']['success'],
        'secondary': CONFIG['plotting']['colors']['danger'],
        'accent': '#C7A3D1',
        'neutral': '#D4A574',
        'light': '#F7F7F7',
        'dark': '#2C3E50'
    }

def load_and_preprocess_data(config=None):
    """
    Load and preprocess the battery usage data

    Args:
        config (dict): Configuration dictionary
        
    Returns:
        pd.DataFrame: Preprocessed data
    """
    if config is None:
        config = CONFIG if CONFIG is not None else load_config()
    
    print("Loading battery usage data...")

    try:
        data_path = f"{config['paths']['processed_data_dir']}/battery_usage.csv"
        df = pd.read_csv(data_path)
        print(f"✓ Data loaded successfully: {len(df)} records")

        # Clean column names
        df.columns = df.columns.str.strip()

        # Create device labels for consistency
        device_mapping = {
            'Phone A': 'Device A',
            'Phone B': 'Device B'
        }
        df['device_label'] = df['Device'].map(device_mapping)

        # Create scenario labels for better readability
        scenario_mapping = {
            'Idle baseline -ON': 'Idle (ON)',
            'Idle baseline -OFF': 'Idle (OFF)',
            'Foreground scan': 'Foreground Scan',
            'Background scan': 'Background Scan',
            'Doze mode': 'Doze Mode'
        }
        df['scenario_label'] = df['Scenario'].map(scenario_mapping)

        # Convert numeric columns
        df['Drain%'] = pd.to_numeric(df['Drain%'], errors='coerce')
        df['Drain%/h'] = pd.to_numeric(df['Drain%/h'], errors='coerce')

        print(f"✓ Data preprocessing completed")
        print(f"  - Devices: {sorted(df['device_label'].unique())}")
        print(f"  - Scenarios: {sorted(df['scenario_label'].unique())}")
        print(f"  - Trials: {sorted(df['Trial_ID'].unique())}")

        # Display device distribution
        device_counts = df['device_label'].value_counts()
        for device, count in device_counts.items():
            print(f"  - {device}: {count} records")

        return df

    except FileNotFoundError:
        print(f"✗ Error: File {data_path} not found")
        return None
    except Exception as e:
        print(f"✗ Error loading data: {str(e)}")
        return None

def calculate_device_scenario_statistics(df):
    """
    Calculate mean and standard deviation for each device in each scenario

    Args:
        df (pd.DataFrame): Preprocessed data

    Returns:
        pd.DataFrame: Statistics summary
    """
    print("Calculating statistics for each device in each scenario...")

    # Group by device and scenario, calculate statistics across the three trials
    stats = df.groupby(['device_label', 'scenario_label']).agg({
        'Drain%': ['mean', 'std', 'count', 'min', 'max'],
        'Drain%/h': ['mean', 'std', 'count', 'min', 'max']
    }).round(3)

    # Flatten column names
    stats.columns = ['_'.join(col).strip() for col in stats.columns]
    stats = stats.reset_index()

    # Fill NaN values with 0 for scenarios with no variation (like Doze mode)
    stats = stats.fillna(0)

    print(f"✓ Statistics calculated for {len(stats)} device-scenario combinations")
    return stats

def plot_battery_drain_by_device_and_scenario(stats):
    """
    Generate battery drain analysis by device and scenario

    Args:
        stats (pd.DataFrame): Statistics data

    Returns:
        str: Path to saved figure
    """
    print("Generating battery drain analysis by device and scenario...")

    # Create figure
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))

    # Get unique devices and scenarios
    devices = sorted(stats['device_label'].unique())
    scenarios = sorted(stats['scenario_label'].unique())

    # Plot 1: Battery drain percentage comparison
    x_pos = np.arange(len(scenarios))
    width = 0.35

    for i, device in enumerate(devices):
        device_stats = stats[stats['device_label'] == device]
        means = device_stats['Drain%_mean'].values
        stds = device_stats['Drain%_std'].values

        color = SOFT_COLORS['device_a'] if device == 'Device A' else SOFT_COLORS['device_b']

        bars = ax1.bar(x_pos + i*width - width/2, means, width,
                      yerr=stds, capsize=5, alpha=0.8,
                      label=device, color=color, edgecolor='white', linewidth=1)

        # Add value labels
        for bar, mean_val, std_val in zip(bars, means, stds):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.3,
                    f'{mean_val:.1f}%', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
            if std_val > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height - 0.5,
                        f'±{std_val:.1f}%', ha='center', va='top',
                        fontsize=8, alpha=0.8)

    ax1.set_xlabel('Scenario', fontweight='bold')
    ax1.set_ylabel('Battery Drain (%)', fontweight='bold')
    ax1.set_title('(a) Battery Drain Percentage by Device and Scenario\n(Mean ± SD across 3 trials)', fontweight='bold', pad=20)
    ax1.set_xticks(x_pos + width/2 - width/4)
    ax1.set_xticklabels(scenarios, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Battery drain rate per hour comparison
    for i, device in enumerate(devices):
        device_stats = stats[stats['device_label'] == device]
        means = device_stats['Drain%/h_mean'].values
        stds = device_stats['Drain%/h_std'].values

        color = SOFT_COLORS['device_a'] if device == 'Device A' else SOFT_COLORS['device_b']

        bars = ax2.bar(x_pos + i*width - width/2, means, width,
                      yerr=stds, capsize=5, alpha=0.8,
                      label=device, color=color, edgecolor='white', linewidth=1)

        # Add value labels
        for bar, mean_val, std_val in zip(bars, means, stds):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{mean_val:.2f}', ha='center', va='bottom',
                    fontsize=10, fontweight='bold')
            if std_val > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height - 0.1,
                        f'±{std_val:.2f}', ha='center', va='top',
                        fontsize=8, alpha=0.8)

    ax2.set_xlabel('Scenario', fontweight='bold')
    ax2.set_ylabel('Battery Drain Rate (%/hour)', fontweight='bold')
    ax2.set_title('(b) Battery Drain Rate by Device and Scenario\n(Mean ± SD across 3 trials)', fontweight='bold', pad=20)
    ax2.set_xticks(x_pos + width/2 - width/4)
    ax2.set_xticklabels(scenarios, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save figure
    config = CONFIG if CONFIG is not None else load_config()
    output_path = f"{config['paths']['plots_dir']}/battery_drain_by_device_and_scenario.png"
    plt.savefig(output_path, dpi=config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"✓ Battery drain analysis plot saved: {output_path}")
    return output_path

def plot_device_comparison_across_scenarios(stats):
    """
    Generate device comparison across scenarios

    Args:
        stats (pd.DataFrame): Statistics data

    Returns:
        str: Path to saved figure
    """
    print("Generating device comparison across scenarios...")

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Device Performance Comparison Across Scenarios',
                fontsize=16, fontweight='bold', y=0.98)

    devices = sorted(stats['device_label'].unique())
    scenarios = sorted(stats['scenario_label'].unique())

    # Plot 1: Battery drain percentage comparison
    device_drain_comparison = stats.pivot(index='scenario_label', columns='device_label', values='Drain%_mean')

    x_pos = np.arange(len(device_drain_comparison.index))
    width = 0.35

    bars1 = axes[0, 0].bar(x_pos - width/2, device_drain_comparison['Device A'], width,
                          label='Device A', alpha=0.8, color=SOFT_COLORS['device_a'],
                          edgecolor='white', linewidth=1)
    bars2 = axes[0, 0].bar(x_pos + width/2, device_drain_comparison['Device B'], width,
                          label='Device B', alpha=0.8, color=SOFT_COLORS['device_b'],
                          edgecolor='white', linewidth=1)

    # Add error bars
    device_a_stds = stats[stats['device_label'] == 'Device A']['Drain%_std'].values
    device_b_stds = stats[stats['device_label'] == 'Device B']['Drain%_std'].values

    axes[0, 0].errorbar(x_pos - width/2, device_drain_comparison['Device A'],
                       yerr=device_a_stds, fmt='none', color='black', capsize=3)
    axes[0, 0].errorbar(x_pos + width/2, device_drain_comparison['Device B'],
                       yerr=device_b_stds, fmt='none', color='black', capsize=3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 0.2,
                           f'{height:.1f}%', ha='center', va='bottom',
                           fontsize=9, fontweight='bold')

    axes[0, 0].set_xlabel('Scenario', fontweight='bold')
    axes[0, 0].set_ylabel('Average Battery Drain (%)', fontweight='bold')
    axes[0, 0].set_title('(a) Average Battery Drain Comparison', fontweight='bold')
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(scenarios, rotation=45, ha='right')
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # Plot 2: Battery drain rate comparison
    device_rate_comparison = stats.pivot(index='scenario_label', columns='device_label', values='Drain%/h_mean')

    bars1 = axes[0, 1].bar(x_pos - width/2, device_rate_comparison['Device A'], width,
                          label='Device A', alpha=0.8, color=SOFT_COLORS['device_a'],
                          edgecolor='white', linewidth=1)
    bars2 = axes[0, 1].bar(x_pos + width/2, device_rate_comparison['Device B'], width,
                          label='Device B', alpha=0.8, color=SOFT_COLORS['device_b'],
                          edgecolor='white', linewidth=1)

    # Add error bars
    device_a_rate_stds = stats[stats['device_label'] == 'Device A']['Drain%/h_std'].values
    device_b_rate_stds = stats[stats['device_label'] == 'Device B']['Drain%/h_std'].values

    axes[0, 1].errorbar(x_pos - width/2, device_rate_comparison['Device A'],
                       yerr=device_a_rate_stds, fmt='none', color='black', capsize=3)
    axes[0, 1].errorbar(x_pos + width/2, device_rate_comparison['Device B'],
                       yerr=device_b_rate_stds, fmt='none', color='black', capsize=3)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.05,
                           f'{height:.2f}', ha='center', va='bottom',
                           fontsize=9, fontweight='bold')

    axes[0, 1].set_xlabel('Scenario', fontweight='bold')
    axes[0, 1].set_ylabel('Average Drain Rate (%/hour)', fontweight='bold')
    axes[0, 1].set_title('(b) Average Drain Rate Comparison', fontweight='bold')
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(scenarios, rotation=45, ha='right')
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # Plot 3: Device performance trends
    for device in devices:
        device_stats = stats[stats['device_label'] == device]
        color = SOFT_COLORS['device_a'] if device == 'Device A' else SOFT_COLORS['device_b']
        axes[1, 0].plot(scenarios, device_stats['Drain%_mean'].values, 'o-',
                       label=device, color=color, linewidth=2, markersize=8)
        axes[1, 0].fill_between(scenarios,
                               device_stats['Drain%_mean'].values - device_stats['Drain%_std'].values,
                               device_stats['Drain%_mean'].values + device_stats['Drain%_std'].values,
                               alpha=0.3, color=color)

    axes[1, 0].set_xlabel('Scenario', fontweight='bold')
    axes[1, 0].set_ylabel('Battery Drain (%)', fontweight='bold')
    axes[1, 0].set_title('(c) Battery Drain Trends with Error Bars', fontweight='bold')
    axes[1, 0].set_xticklabels(scenarios, rotation=45, ha='right')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Heatmap of battery drain by device and scenario
    pivot_data = stats.pivot(index='device_label', columns='scenario_label', values='Drain%_mean')

    sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='RdYlBu_r',
                ax=axes[1, 1], cbar_kws={'label': 'Battery Drain (%)'},
                linewidths=0.5, linecolor='white')

    axes[1, 1].set_title('(d) Battery Drain Heatmap', fontweight='bold')
    axes[1, 1].set_xlabel('Scenario', fontweight='bold')
    axes[1, 1].set_ylabel('Device', fontweight='bold')

    plt.tight_layout()

    # Save figure
    config = CONFIG if CONFIG is not None else load_config()
    output_path = f"{config['paths']['plots_dir']}/device_comparison_across_scenarios.png"
    plt.savefig(output_path, dpi=config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"✓ Device comparison plot saved: {output_path}")
    return output_path

def plot_trial_analysis_by_device(df):
    """
    Generate trial-by-trial analysis for each device

    Args:
        df (pd.DataFrame): Original data

    Returns:
        str: Path to saved figure
    """
    print("Generating trial-by-trial analysis by device...")

    # Create figure
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Trial-by-Trial Analysis by Device',
                fontsize=16, fontweight='bold', y=0.98)

    devices = sorted(df['device_label'].unique())
    scenarios = sorted(df['scenario_label'].unique())
    trials = sorted(df['Trial_ID'].unique())

    # Plot 1: Trial comparison - Battery drain
    trial_comparison = df.groupby(['Trial_ID', 'device_label'])['Drain%'].mean().unstack()

    x_pos = np.arange(len(trial_comparison.index))
    width = 0.35

    bars1 = axes[0, 0].bar(x_pos - width/2, trial_comparison['Device A'], width,
                          label='Device A', alpha=0.8, color=SOFT_COLORS['device_a'],
                          edgecolor='white', linewidth=1)
    bars2 = axes[0, 0].bar(x_pos + width/2, trial_comparison['Device B'], width,
                          label='Device B', alpha=0.8, color=SOFT_COLORS['device_b'],
                          edgecolor='white', linewidth=1)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            axes[0, 0].text(bar.get_x() + bar.get_width()/2., height + 0.2,
                           f'{height:.1f}%', ha='center', va='bottom',
                           fontsize=10, fontweight='bold')

    axes[0, 0].set_xlabel('Trial', fontweight='bold')
    axes[0, 0].set_ylabel('Average Battery Drain (%)', fontweight='bold')
    axes[0, 0].set_title('(a) Trial Comparison: Average Battery Drain', fontweight='bold')
    axes[0, 0].set_xticks(x_pos)
    axes[0, 0].set_xticklabels(trial_comparison.index)
    axes[0, 0].legend()
    axes[0, 0].grid(True, alpha=0.3, axis='y')

    # Plot 2: Trial comparison - Drain rate
    trial_rate_comparison = df.groupby(['Trial_ID', 'device_label'])['Drain%/h'].mean().unstack()

    bars1 = axes[0, 1].bar(x_pos - width/2, trial_rate_comparison['Device A'], width,
                          label='Device A', alpha=0.8, color=SOFT_COLORS['device_a'],
                          edgecolor='white', linewidth=1)
    bars2 = axes[0, 1].bar(x_pos + width/2, trial_rate_comparison['Device B'], width,
                          label='Device B', alpha=0.8, color=SOFT_COLORS['device_b'],
                          edgecolor='white', linewidth=1)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            axes[0, 1].text(bar.get_x() + bar.get_width()/2., height + 0.05,
                           f'{height:.2f}', ha='center', va='bottom',
                           fontsize=10, fontweight='bold')

    axes[0, 1].set_xlabel('Trial', fontweight='bold')
    axes[0, 1].set_ylabel('Average Drain Rate (%/hour)', fontweight='bold')
    axes[0, 1].set_title('(b) Trial Comparison: Average Drain Rate', fontweight='bold')
    axes[0, 1].set_xticks(x_pos)
    axes[0, 1].set_xticklabels(trial_rate_comparison.index)
    axes[0, 1].legend()
    axes[0, 1].grid(True, alpha=0.3, axis='y')

    # Plot 3: Device performance consistency
    device_consistency = df.groupby(['device_label', 'scenario_label'])['Drain%'].std().unstack()

    x_pos = np.arange(len(device_consistency.columns))

    for i, device in enumerate(devices):
        color = SOFT_COLORS['device_a'] if device == 'Device A' else SOFT_COLORS['device_b']
        axes[1, 0].plot(x_pos, device_consistency.loc[device].values, 'o-',
                       label=device, color=color, linewidth=2, markersize=8)

    axes[1, 0].set_xlabel('Scenario', fontweight='bold')
    axes[1, 0].set_ylabel('Standard Deviation (%)', fontweight='bold')
    axes[1, 0].set_title('(c) Performance Consistency (Lower = More Consistent)', fontweight='bold')
    axes[1, 0].set_xticks(x_pos)
    axes[1, 0].set_xticklabels(scenarios, rotation=45, ha='right')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    # Plot 4: Overall device comparison
    device_summary = df.groupby('device_label')[['Drain%', 'Drain%/h']].agg(['mean', 'std']).round(2)

    metrics = ['Drain%', 'Drain%/h']
    x_pos = np.arange(len(metrics))
    width = 0.35

    for i, device in enumerate(devices):
        color = SOFT_COLORS['device_a'] if device == 'Device A' else SOFT_COLORS['device_b']
        means = [device_summary.loc[device, (metric, 'mean')] for metric in metrics]
        stds = [device_summary.loc[device, (metric, 'std')] for metric in metrics]

        bars = axes[1, 1].bar(x_pos + i*width - width/2, means, width,
                             yerr=stds, capsize=5, alpha=0.8,
                             label=device, color=color, edgecolor='white', linewidth=1)

        # Add value labels
        for bar, mean_val in zip(bars, means):
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                           f'{mean_val:.1f}', ha='center', va='bottom',
                           fontsize=9, fontweight='bold')

    axes[1, 1].set_xlabel('Metric', fontweight='bold')
    axes[1, 1].set_ylabel('Value', fontweight='bold')
    axes[1, 1].set_title('(d) Overall Device Performance Summary', fontweight='bold')
    axes[1, 1].set_xticks(x_pos)
    axes[1, 1].set_xticklabels(['Battery Drain (%)', 'Drain Rate (%/h)'])
    axes[1, 1].legend()
    axes[1, 1].grid(True, alpha=0.3, axis='y')

    plt.tight_layout()

    # Save figure
    config = CONFIG if CONFIG is not None else load_config()
    output_path = f"{config['paths']['plots_dir']}/trial_analysis_by_device.png"
    plt.savefig(output_path, dpi=config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
    plt.show()

    print(f"✓ Trial analysis plot saved: {output_path}")
    return output_path

def generate_detailed_statistics_table(stats):
    """
    Generate and display detailed statistics table

    Args:
        stats (pd.DataFrame): Statistics data
    """
    print("\n" + "="*100)
    print("DETAILED STATISTICS: MEAN ± STANDARD DEVIATION BY DEVICE AND SCENARIO")
    print("="*100)

    devices = sorted(stats['device_label'].unique())
    scenarios = sorted(stats['scenario_label'].unique())

    print(f"\n{'Scenario':<20} {'Device A - Drain%':<20} {'Device A - Rate':<20} {'Device B - Drain%':<20} {'Device B - Rate':<20}")
    print("-" * 100)

    for scenario in scenarios:
        device_a_stats = stats[(stats['device_label'] == 'Device A') & (stats['scenario_label'] == scenario)]
        device_b_stats = stats[(stats['device_label'] == 'Device B') & (stats['scenario_label'] == scenario)]

        if len(device_a_stats) > 0 and len(device_b_stats) > 0:
            a_drain = f"{device_a_stats['Drain%_mean'].iloc[0]:.2f} ± {device_a_stats['Drain%_std'].iloc[0]:.2f}"
            a_rate = f"{device_a_stats['Drain%/h_mean'].iloc[0]:.2f} ± {device_a_stats['Drain%/h_std'].iloc[0]:.2f}"
            b_drain = f"{device_b_stats['Drain%_mean'].iloc[0]:.2f} ± {device_b_stats['Drain%_std'].iloc[0]:.2f}"
            b_rate = f"{device_b_stats['Drain%/h_mean'].iloc[0]:.2f} ± {device_b_stats['Drain%/h_std'].iloc[0]:.2f}"

            print(f"{scenario:<20} {a_drain:<20} {a_rate:<20} {b_drain:<20} {b_rate:<20}")

    print("\n" + "="*100)

    # Summary statistics
    print("\nOVERALL PERFORMANCE SUMMARY:")
    print("-" * 50)

    for device in devices:
        device_stats = stats[stats['device_label'] == device]
        print(f"\n{device}:")
        print(f"  Average Battery Drain: {device_stats['Drain%_mean'].mean():.2f}% ± {device_stats['Drain%_mean'].std():.2f}%")
        print(f"  Average Drain Rate: {device_stats['Drain%/h_mean'].mean():.2f}%/h ± {device_stats['Drain%/h_mean'].std():.2f}%/h")
        print(f"  Most Power-Consuming Scenario: {device_stats.loc[device_stats['Drain%_mean'].idxmax(), 'scenario_label']} ({device_stats['Drain%_mean'].max():.2f}%)")
        print(f"  Least Power-Consuming Scenario: {device_stats.loc[device_stats['Drain%_mean'].idxmin(), 'scenario_label']} ({device_stats['Drain%_mean'].min():.2f}%)")

    print("\n" + "="*100)

def main(config=None):
    """
    Main function to run battery usage analysis by device
    
    Args:
        config (dict): Configuration dictionary
    """
    if config is None:
        config = load_config()
    
    # Initialize plotting style
    initialize_plotting_style(config)
    
    print("Battery Usage Analysis by Device Across Three Trials")
    print("=" * 60)

    # Load and preprocess data
    df = load_and_preprocess_data(config)

    if df is None:
        print("Failed to load data. Exiting.")
        return

    # Calculate statistics
    stats = calculate_device_scenario_statistics(df)

    # Generate detailed statistics table
    generate_detailed_statistics_table(stats)

    # Generate all plots
    print("\nGenerating visualizations...")

    print("\n1. Battery Drain Analysis by Device and Scenario...")
    plot_battery_drain_by_device_and_scenario(stats)

    print("\n2. Device Comparison Across Scenarios...")
    plot_device_comparison_across_scenarios(stats)

    print("\n3. Trial-by-Trial Analysis by Device...")
    plot_trial_analysis_by_device(df)

    print("\n" + "="*60)
    print("ANALYSIS COMPLETED SUCCESSFULLY")
    print("="*60)

    print(f"\nGenerated Files:")
    print(f"- battery_drain_by_device_and_scenario.png")
    print(f"- device_comparison_across_scenarios.png")
    print(f"- trial_analysis_by_device.png")

    # Display key findings
    print(f"\nKey Findings:")

    # Overall battery drain comparison
    device_summary = df.groupby('device_label')['Drain%'].agg(['mean', 'std']).round(2)
    print(f"- Average Battery Drain: Device A ({device_summary.loc['Device A', 'mean']:.2f}% ± {device_summary.loc['Device A', 'std']:.2f}%) vs Device B ({device_summary.loc['Device B', 'mean']:.2f}% ± {device_summary.loc['Device B', 'std']:.2f}%)")

    # Most power-consuming scenario
    scenario_drain = df.groupby('scenario_label')['Drain%'].mean().round(2)
    max_scenario = scenario_drain.idxmax()
    max_drain = scenario_drain.max()
    print(f"- Most Power-Consuming Scenario: {max_scenario} ({max_drain:.2f}%)")

    # Least power-consuming scenario
    min_scenario = scenario_drain.idxmin()
    min_drain = scenario_drain.min()
    print(f"- Least Power-Consuming Scenario: {min_scenario} ({min_drain:.2f}%)")

if __name__ == "__main__":
    main()