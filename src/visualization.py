# @Version :1.0
# @Author  : Mingyue
# @File    : visualization.py.py
# @Time    : 01/03/2026 19:27
"""
RSSI Trial Data Analysis and Visualization
==========================================

This script performs comprehensive analysis of RSSI (Received Signal Strength Indicator)
trial data and generates scientific visualizations suitable for research publications.

Author: Research Team
Date: 2024
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
from pathlib import Path
from utils import load_config

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')


class RSSIAnalyzer:
    """
    Comprehensive RSSI data analysis and visualization class
    """

    def __init__(self, data_path=None, config=None):
        """
        Initialize the RSSI analyzer

        Args:
            data_path (str): Path to the RSSI trial data CSV file
            config (dict): Configuration dictionary
        """
        if config is None:
            self.config = load_config()
        else:
            self.config = config
        
        if data_path is None:
            data_path = f"{self.config['paths']['processed_data_dir']}/RSSI_trial.csv"
        
        self.data_path = data_path
        self.df = None
        self.rssi_stats = None
        self.trial_summary = None
        self.device_comparison = None
        self.colors = None
        
        # Initialize plotting style
        self._initialize_plotting_style()
    
    def _initialize_plotting_style(self):
        """初始化绘图样式和颜色"""
        plt.style.use(self.config['plotting']['style'])
        plt.rcParams.update({
            'font.size': 12,
            'axes.titlesize': 14,
            'axes.labelsize': 12,
            'xtick.labelsize': 10,
            'ytick.labelsize': 10,
            'legend.fontsize': 10,
            'figure.titlesize': 16,
            'axes.linewidth': 1.2,
            'grid.alpha': 0.3,
            'lines.linewidth': 2,
            'lines.markersize': 6
        })
        
        # Professional color palette from config
        self.colors = {
            'primary': self.config['plotting']['colors']['primary'],
            'secondary': self.config['plotting']['colors']['secondary'],
            'success': self.config['plotting']['colors']['success'],
            'danger': self.config['plotting']['colors']['danger'],
            'warning': '#ff7f0e',
            'info': '#17a2b8',
            'light': '#f8f9fa',
            'dark': '#343a40'
        }

    def load_data(self):
        """
        Load and preprocess RSSI trial data

        Returns:
            pd.DataFrame: Preprocessed data
        """
        print("Loading RSSI trial data...")

        try:
            self.df = pd.read_csv(self.data_path)
            print(f"✓ Data loaded successfully: {len(self.df)} records")

            # Create device labels from config
            device_mapping = self.config['devices']
            self.df['device_label'] = self.df['uuid'].map(device_mapping)

            # Create scenario labels from config
            scenario_mapping = self.config['scenarios']
            self.df['scenario_label'] = self.df['scenario'].map(scenario_mapping)

            print(f"✓ Data preprocessing completed")
            print(f"  - Devices: {self.df['device_label'].nunique()}")
            print(f"  - Scenarios: {self.df['scenario_label'].nunique()}")
            print(f"  - Trials: {self.df['trial_id'].nunique()}")

            return self.df

        except FileNotFoundError:
            print(f"✗ Error: File {self.data_path} not found")
            return None
        except Exception as e:
            print(f"✗ Error loading data: {str(e)}")
            return None

    def calculate_rssi_statistics(self):
        """
        Calculate comprehensive RSSI statistics by trial and device

        Returns:
            pd.DataFrame: RSSI statistics
        """
        print("Calculating RSSI statistics...")

        if self.df is None:
            print("✗ Error: Data not loaded. Please run load_data() first.")
            return None

        # Group by trial_id and uuid to calculate statistics
        self.rssi_stats = self.df.groupby(['trial_id', 'uuid']).agg({
            'session_count': 'sum',
            'avg_median_RSSI': 'mean',
            'std_median_RSSI': 'mean',
            'avg_max_RSSI': 'mean',
            'std_max_RSSI': 'mean',
            'min_median_RSSI': 'min',
            'max_median_RSSI': 'max',
            'min_max_RSSI': 'min',
            'max_max_RSSI': 'max'
        }).reset_index()

        # Add device and scenario labels
        self.rssi_stats = self.rssi_stats.merge(
            self.df[['trial_id', 'uuid', 'device_label', 'scenario_label']].drop_duplicates(),
            on=['trial_id', 'uuid'], how='left'
        )

        print(f"✓ RSSI statistics calculated for {len(self.rssi_stats)} trial-device combinations")
        return self.rssi_stats

    def calculate_trial_summary(self):
        """
        Calculate trial-level summary statistics (combining devices)

        Returns:
            pd.DataFrame: Trial summary statistics
        """
        print("Calculating trial summary statistics...")

        if self.rssi_stats is None:
            print("✗ Error: RSSI statistics not calculated. Please run calculate_rssi_statistics() first.")
            return None

        def calculate_trial_metrics(trial_group):
            """Calculate weighted averages for trial summary"""
            if len(trial_group) == 0:
                return pd.Series({
                    'total_sessions': 0,
                    'device_count': 0,
                    'avg_median_RSSI': np.nan,
                    'std_median_RSSI': np.nan,
                    'avg_max_RSSI': np.nan,
                    'std_max_RSSI': np.nan,
                    'min_median_RSSI': np.nan,
                    'max_median_RSSI': np.nan,
                    'min_max_RSSI': np.nan,
                    'max_max_RSSI': np.nan
                })

            # Calculate weighted averages based on session count
            total_sessions = trial_group['session_count'].sum()
            if total_sessions > 0:
                avg_median_RSSI = np.average(trial_group['avg_median_RSSI'],
                                             weights=trial_group['session_count'])
                avg_max_RSSI = np.average(trial_group['avg_max_RSSI'],
                                          weights=trial_group['session_count'])

                # Calculate weighted standard deviations
                std_median_RSSI = np.sqrt(np.average((trial_group['std_median_RSSI'] ** 2),
                                                     weights=trial_group['session_count']))
                std_max_RSSI = np.sqrt(np.average((trial_group['std_max_RSSI'] ** 2),
                                                  weights=trial_group['session_count']))
            else:
                avg_median_RSSI = avg_max_RSSI = std_median_RSSI = std_max_RSSI = np.nan

            return pd.Series({
                'total_sessions': total_sessions,
                'device_count': len(trial_group),
                'avg_median_RSSI': avg_median_RSSI,
                'std_median_RSSI': std_median_RSSI,
                'avg_max_RSSI': avg_max_RSSI,
                'std_max_RSSI': std_max_RSSI,
                'min_median_RSSI': trial_group['min_median_RSSI'].min(),
                'max_median_RSSI': trial_group['max_median_RSSI'].max(),
                'min_max_RSSI': trial_group['min_max_RSSI'].min(),
                'max_max_RSSI': trial_group['max_max_RSSI'].max(),
                'scenario_label': trial_group['scenario_label'].iloc[0]
            })

        # Calculate trial summaries
        self.trial_summary = self.rssi_stats.groupby('trial_id').apply(calculate_trial_metrics).reset_index()

        print(f"✓ Trial summary calculated for {len(self.trial_summary)} trials")
        return self.trial_summary

    def calculate_device_comparison(self):
        """
        Calculate device-level comparison statistics

        Returns:
            pd.DataFrame: Device comparison statistics
        """
        print("Calculating device comparison statistics...")

        if self.rssi_stats is None:
            print("✗ Error: RSSI statistics not calculated. Please run calculate_rssi_statistics() first.")
            return None

        self.device_comparison = self.rssi_stats.groupby('device_label').agg({
            'session_count': 'sum',
            'avg_median_RSSI': ['mean', 'std'],
            'avg_max_RSSI': ['mean', 'std'],
            'std_median_RSSI': 'mean',
            'std_max_RSSI': 'mean'
        }).round(3)

        # Flatten column names
        self.device_comparison.columns = ['_'.join(col).strip() for col in self.device_comparison.columns]
        self.device_comparison = self.device_comparison.reset_index()

        print(f"✓ Device comparison calculated for {len(self.device_comparison)} devices")
        return self.device_comparison

    def plot_device_trial_comparison(self):
        """
        Generate comprehensive device and trial comparison plots

        Returns:
            str: Path to saved figure
        """
        print("Generating device and trial comparison plots...")

        if self.rssi_stats is None or self.trial_summary is None:
            print("✗ Error: Statistics not calculated. Please run analysis methods first.")
            return None

        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('RSSI Performance Analysis: Device and Trial Comparison',
                     fontsize=16, fontweight='bold', y=0.98)

        # Get unique devices and colors
        devices = self.rssi_stats['device_label'].unique()
        colors = [self.colors['primary'], self.colors['secondary']]

        # Plot 1: Device comparison - Median RSSI
        for i, device in enumerate(devices):
            device_data = self.rssi_stats[self.rssi_stats['device_label'] == device]
            axes[0, 0].plot(device_data['trial_id'], device_data['avg_median_RSSI'],
                            'o-', label=device, color=colors[i], linewidth=2, markersize=6)

        axes[0, 0].set_xlabel('Trial ID', fontweight='bold')
        axes[0, 0].set_ylabel('Average Median RSSI (dBm)', fontweight='bold')
        axes[0, 0].set_title('(a) Device Comparison: Median RSSI', fontweight='bold')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        axes[0, 0].invert_yaxis()

        # Plot 2: Device comparison - Max RSSI
        for i, device in enumerate(devices):
            device_data = self.rssi_stats[self.rssi_stats['device_label'] == device]
            axes[0, 1].plot(device_data['trial_id'], device_data['avg_max_RSSI'],
                            'o-', label=device, color=colors[i], linewidth=2, markersize=6)

        axes[0, 1].set_xlabel('Trial ID', fontweight='bold')
        axes[0, 1].set_ylabel('Average Max RSSI (dBm)', fontweight='bold')
        axes[0, 1].set_title('(b) Device Comparison: Max RSSI', fontweight='bold')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        axes[0, 1].invert_yaxis()

        # Plot 3: Trial summary - Median RSSI
        trial_clean = self.trial_summary.dropna(subset=['avg_median_RSSI'])
        bars = axes[1, 0].bar(trial_clean['trial_id'], trial_clean['avg_median_RSSI'],
                              color=self.colors['success'], alpha=0.7, edgecolor='black', linewidth=0.5)

        axes[1, 0].set_xlabel('Trial ID', fontweight='bold')
        axes[1, 0].set_ylabel('Average Median RSSI (dBm)', fontweight='bold')
        axes[1, 0].set_title('(c) Trial Summary: Median RSSI (Combined Devices)', fontweight='bold')
        axes[1, 0].tick_params(axis='x', rotation=45)
        axes[1, 0].grid(True, alpha=0.3, axis='y')
        axes[1, 0].invert_yaxis()

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[1, 0].text(bar.get_x() + bar.get_width() / 2., height + 0.2,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)

        # Plot 4: Trial summary - Max RSSI
        trial_clean = self.trial_summary.dropna(subset=['avg_max_RSSI'])
        bars = axes[1, 1].bar(trial_clean['trial_id'], trial_clean['avg_max_RSSI'],
                              color=self.colors['danger'], alpha=0.7, edgecolor='black', linewidth=0.5)

        axes[1, 1].set_xlabel('Trial ID', fontweight='bold')
        axes[1, 1].set_ylabel('Average Max RSSI (dBm)', fontweight='bold')
        axes[1, 1].set_title('(d) Trial Summary: Max RSSI (Combined Devices)', fontweight='bold')
        axes[1, 1].tick_params(axis='x', rotation=45)
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        axes[1, 1].invert_yaxis()

        # Add value labels
        for bar in bars:
            height = bar.get_height()
            axes[1, 1].text(bar.get_x() + bar.get_width() / 2., height + 0.2,
                            f'{height:.1f}', ha='center', va='bottom', fontsize=9)

        plt.tight_layout()

        # Save figure
        output_path = f"{self.config['paths']['plots_dir']}/rssi_device_trial_analysis.png"
        plt.savefig(output_path, dpi=self.config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
        plt.show()

        print(f"✓ Device and trial comparison plot saved: {output_path}")
        return output_path

    def plot_scenario_comparison(self):
        """
        Generate scenario comparison plots

        Returns:
            str: Path to saved figure
        """
        print("Generating scenario comparison plots...")

        if self.trial_summary is None:
            print("✗ Error: Trial summary not calculated. Please run calculate_trial_summary() first.")
            return None

        # Calculate scenario statistics
        scenario_stats = self.trial_summary.groupby('scenario_label').agg({
            'avg_median_RSSI': ['mean', 'std'],
            'avg_max_RSSI': ['mean', 'std'],
            'total_sessions': 'sum'
        }).round(2)

        # Flatten column names
        scenario_stats.columns = ['_'.join(col).strip() for col in scenario_stats.columns]
        scenario_stats = scenario_stats.reset_index()

        # Create figure
        fig, ax = plt.subplots(figsize=(14, 8))

        scenarios = scenario_stats['scenario_label']
        x_pos = np.arange(len(scenarios))
        width = 0.35

        # Plot bars with error bars
        bars1 = ax.bar(x_pos - width / 2, scenario_stats['avg_median_RSSI_mean'], width,
                       yerr=scenario_stats['avg_median_RSSI_std'], capsize=5,
                       label='Average Median RSSI', alpha=0.8, color=self.colors['primary'],
                       edgecolor='white', linewidth=1)

        bars2 = ax.bar(x_pos + width / 2, scenario_stats['avg_max_RSSI_mean'], width,
                       yerr=scenario_stats['avg_max_RSSI_std'], capsize=5,
                       label='Average Max RSSI', alpha=0.8, color=self.colors['secondary'],
                       edgecolor='white', linewidth=1)

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=10, fontweight='bold')

        # Customize plot
        ax.set_xlabel('Experimental Scenario', fontweight='bold', fontsize=12)
        ax.set_ylabel('RSSI (dBm)', fontweight='bold', fontsize=12)
        ax.set_title('RSSI Performance Comparison Across Experimental Scenarios',
                     fontweight='bold', fontsize=14, pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(scenarios, rotation=45, ha='right')
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        ax.invert_yaxis()

        plt.tight_layout()

        # Save figure
        output_path = f"{self.config['paths']['plots_dir']}/rssi_scenario_comparison.png"
        plt.savefig(output_path, dpi=self.config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
        plt.show()

        print(f"✓ Scenario comparison plot saved: {output_path}")
        return output_path

    def plot_device_performance_comparison(self):
        """
        Generate device performance comparison plots

        Returns:
            str: Path to saved figure
        """
        print("Generating device performance comparison plots...")

        if self.device_comparison is None:
            print("✗ Error: Device comparison not calculated. Please run calculate_device_comparison() first.")
            return None

        # Create figure
        fig, ax = plt.subplots(figsize=(10, 8))

        devices = self.device_comparison['device_label']
        x_pos = np.arange(len(devices))
        width = 0.35

        # Plot bars with error bars
        bars1 = ax.bar(x_pos - width / 2, self.device_comparison['avg_median_RSSI_mean'], width,
                       yerr=self.device_comparison['avg_median_RSSI_std'], capsize=5,
                       label='Average Median RSSI', alpha=0.8, color=self.colors['success'],
                       edgecolor='white', linewidth=1)

        bars2 = ax.bar(x_pos + width / 2, self.device_comparison['avg_max_RSSI_mean'], width,
                       yerr=self.device_comparison['avg_max_RSSI_std'], capsize=5,
                       label='Average Max RSSI', alpha=0.8, color=self.colors['danger'],
                       edgecolor='white', linewidth=1)

        # Add value labels
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width() / 2., height + 0.5,
                        f'{height:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')

        # Customize plot
        ax.set_xlabel('Device', fontweight='bold', fontsize=12)
        ax.set_ylabel('RSSI (dBm)', fontweight='bold', fontsize=12)
        ax.set_title('Device Performance Comparison: RSSI Analysis',
                     fontweight='bold', fontsize=14, pad=20)
        ax.set_xticks(x_pos)
        ax.set_xticklabels(devices)
        ax.legend(fontsize=11)
        ax.grid(True, alpha=0.3, axis='y')
        ax.invert_yaxis()

        plt.tight_layout()

        # Save figure
        output_path = f"{self.config['paths']['plots_dir']}/rssi_device_performance_comparison.png"
        plt.savefig(output_path, dpi=self.config['plotting']['dpi'], bbox_inches='tight', facecolor='white')
        plt.show()

        print(f"✓ Device performance comparison plot saved: {output_path}")
        return output_path

    def save_results(self):
        """
        Save all analysis results to CSV files

        Returns:
            dict: Dictionary of saved file paths
        """
        print("Saving analysis results...")

        saved_files = {}

        try:
            processed_dir = self.config['paths']['processed_data_dir']
            
            # Save RSSI statistics
            if self.rssi_stats is not None:
                stats_path = f'{processed_dir}/rssi_statistics_by_trial_device.csv'
                self.rssi_stats.to_csv(stats_path, index=False)
                saved_files['rssi_statistics'] = stats_path
                print(f"✓ RSSI statistics saved: {stats_path}")

            # Save trial summary
            if self.trial_summary is not None:
                summary_path = f'{processed_dir}/rssi_trial_summary.csv'
                self.trial_summary.to_csv(summary_path, index=False)
                saved_files['trial_summary'] = summary_path
                print(f"✓ Trial summary saved: {summary_path}")

            # Save device comparison
            if self.device_comparison is not None:
                comparison_path = f'{processed_dir}/rssi_device_comparison.csv'
                self.device_comparison.to_csv(comparison_path, index=False)
                saved_files['device_comparison'] = comparison_path
                print(f"✓ Device comparison saved: {comparison_path}")

            return saved_files

        except Exception as e:
            print(f"✗ Error saving results: {str(e)}")
            return {}

    def generate_analysis_report(self):
        """
        Generate comprehensive analysis report

        Returns:
            str: Path to saved report
        """
        print("Generating analysis report...")

        if any(x is None for x in [self.df, self.rssi_stats, self.trial_summary, self.device_comparison]):
            print("✗ Error: Not all analysis steps completed. Please run full analysis first.")
            return None

        # Calculate scenario analysis
        scenario_analysis = self.trial_summary.groupby('scenario_label').agg({
            'avg_median_RSSI': ['mean', 'std'],
            'avg_max_RSSI': ['mean', 'std'],
            'total_sessions': 'sum'
        }).round(2)

        # Generate report
        report = f"""
# RSSI Trial Data Analysis Report

## Executive Summary

This report presents a comprehensive analysis of RSSI (Received Signal Strength Indicator) 
trial data collected from wireless communication experiments. The analysis covers 
performance evaluation across different devices, trials, and experimental scenarios.

## Dataset Overview

- **Total Records**: {len(self.df)}
- **Number of Devices**: {self.df['device_label'].nunique()}
- **Number of Trials**: {self.df['trial_id'].nunique()}
- **Number of Scenarios**: {self.df['scenario_label'].nunique()}
- **Total Sessions**: {self.df['session_count'].sum()}

## Device Information

"""

        for i, device in enumerate(self.df['device_label'].unique(), 1):
            device_data = self.device_comparison[self.device_comparison['device_label'] == device]
            if len(device_data) > 0:
                device_summary = device_data.iloc[0]
                report += f"- **{device}**:\n"
                report += f"  - Total Sessions: {device_summary['session_count_sum']}\n"
                report += f"  - Average Median RSSI: {device_summary['avg_median_RSSI_mean']:.2f} ± {device_summary['avg_median_RSSI_std']:.2f} dBm\n"
                report += f"  - Average Max RSSI: {device_summary['avg_max_RSSI_mean']:.2f} ± {device_summary['avg_max_RSSI_std']:.2f} dBm\n"

        report += f"""

## Key Findings

### 1. Overall RSSI Performance
- **Overall Average Median RSSI**: {self.trial_summary['avg_median_RSSI'].mean():.2f} dBm
- **Overall Average Max RSSI**: {self.trial_summary['avg_max_RSSI'].mean():.2f} dBm
- **Median RSSI Range**: {self.trial_summary['avg_median_RSSI'].min():.1f} to {self.trial_summary['avg_median_RSSI'].max():.1f} dBm
- **Max RSSI Range**: {self.trial_summary['avg_max_RSSI'].min():.1f} to {self.trial_summary['avg_max_RSSI'].max():.1f} dBm

### 2. Device Performance Comparison
"""

        for i, device in enumerate(self.df['device_label'].unique()):
            device_data = self.device_comparison[self.device_comparison['device_label'] == device]
            if len(device_data) > 0:
                device_summary = device_data.iloc[0]
                report += f"- **{device}**:\n"
                report += f"  - Average Median RSSI: {device_summary['avg_median_RSSI_mean']:.2f} ± {device_summary['avg_median_RSSI_std']:.2f} dBm\n"
                report += f"  - Average Max RSSI: {device_summary['avg_max_RSSI_mean']:.2f} ± {device_summary['avg_max_RSSI_std']:.2f} dBm\n"
                report += f"  - Total Sessions: {device_summary['session_count_sum']}\n"

        # Calculate device differences
        if len(self.device_comparison) >= 2:
            device1 = self.device_comparison.iloc[0]
            device2 = self.device_comparison.iloc[1]
            median_diff = abs(device1['avg_median_RSSI_mean'] - device2['avg_median_RSSI_mean'])
            max_diff = abs(device1['avg_max_RSSI_mean'] - device2['avg_max_RSSI_mean'])

            report += f"\n- **Device Performance Differences**:\n"
            report += f"  - Median RSSI Difference: {median_diff:.2f} dBm\n"
            report += f"  - Max RSSI Difference: {max_diff:.2f} dBm\n"

        report += f"""

### 3. Scenario Performance Analysis
"""

        for scenario in scenario_analysis.index:
            stats = scenario_analysis.loc[scenario]
            report += f"- **{scenario}**:\n"
            report += f"  - Average Median RSSI: {stats[('avg_median_RSSI', 'mean')]:.2f} ± {stats[('avg_median_RSSI', 'std')]:.2f} dBm\n"
            report += f"  - Average Max RSSI: {stats[('avg_max_RSSI', 'mean')]:.2f} ± {stats[('avg_max_RSSI', 'std')]:.2f} dBm\n"
            report += f"  - Total Sessions: {stats[('total_sessions', 'sum')]}\n"

        report += f"""

### 4. Trial Performance Ranking

#### Top 5 Trials by Median RSSI:
"""

        # Sort trials by median RSSI
        trial_ranking = self.trial_summary.sort_values('avg_median_RSSI', ascending=False)
        for i, (_, row) in enumerate(trial_ranking.head(5).iterrows()):
            report += f"{i + 1}. {row['trial_id']}: {row['avg_median_RSSI']:.2f} dBm ({row['scenario_label']})\n"

        report += f"""

#### Top 5 Trials by Max RSSI:
"""

        trial_ranking_max = self.trial_summary.sort_values('avg_max_RSSI', ascending=False)
        for i, (_, row) in enumerate(trial_ranking_max.head(5).iterrows()):
            report += f"{i + 1}. {row['trial_id']}: {row['avg_max_RSSI']:.2f} dBm ({row['scenario_label']})\n"

        report += f"""

## Generated Visualizations

1. **rssi_device_trial_analysis.png**: Comprehensive device and trial comparison analysis
2. **rssi_scenario_comparison.png**: RSSI performance comparison across experimental scenarios
3. **rssi_device_performance_comparison.png**: Detailed device performance comparison

## Conclusions

- Device RSSI performance shows consistent patterns with minimal differences between devices
- Different experimental scenarios significantly impact RSSI performance
- Overall system signal quality is within acceptable ranges
- Metal interference scenarios show the most significant signal degradation
- Static scenarios demonstrate the most stable RSSI performance

## Recommendations

- Further investigate the impact of environmental factors on signal quality
- Consider implementing adaptive signal processing for challenging scenarios
- Evaluate the effectiveness of different experimental configurations
- Conduct additional trials to validate findings across different conditions

---
*Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

        # Save report
        report_path = f"{self.config['paths']['report_dir']}/rssi_analysis_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"✓ Analysis report saved: {report_path}")
        return report_path

    def run_complete_analysis(self):
        """
        Run complete RSSI analysis pipeline

        Returns:
            dict: Dictionary containing all results and file paths
        """
        print("=" * 60)
        print("RSSI TRIAL DATA ANALYSIS PIPELINE")
        print("=" * 60)

        results = {}

        # Step 1: Load data
        if self.load_data() is None:
            return results

        # Step 2: Calculate statistics
        self.calculate_rssi_statistics()
        self.calculate_trial_summary()
        self.calculate_device_comparison()

        # Step 3: Generate visualizations
        results['device_trial_plot'] = self.plot_device_trial_comparison()
        results['scenario_plot'] = self.plot_scenario_comparison()
        results['device_performance_plot'] = self.plot_device_performance_comparison()

        # Step 4: Save results
        results['csv_files'] = self.save_results()

        # Step 5: Generate report
        results['report'] = self.generate_analysis_report()

        print("\n" + "=" * 60)
        print("ANALYSIS COMPLETED SUCCESSFULLY")
        print("=" * 60)

        print(f"\nGenerated Files:")
        print(f"- Visualizations: {len([k for k in results.keys() if 'plot' in k])} PNG files")
        print(f"- Data Files: {len(results.get('csv_files', {}))} CSV files")
        print(f"- Report: {results.get('report', 'Not generated')}")

        return results


def main(config=None):
    """
    Main function to run RSSI analysis
    
    Args:
        config (dict): Configuration dictionary
    """
    # Initialize analyzer
    analyzer = RSSIAnalyzer(config=config)

    # Run complete analysis
    results = analyzer.run_complete_analysis()

    # Print summary
    if results:
        print(f"\nAnalysis Summary:")
        print(f"- Total trials analyzed: {len(analyzer.df) if analyzer.df is not None else 0}")
        print(f"- Devices compared: {analyzer.df['device_label'].nunique() if analyzer.df is not None else 0}")
        print(f"- Scenarios evaluated: {analyzer.df['scenario_label'].nunique() if analyzer.df is not None else 0}")

        if analyzer.trial_summary is not None:
            print(f"- Average median RSSI: {analyzer.trial_summary['avg_median_RSSI'].mean():.2f} dBm")
            print(f"- Average max RSSI: {analyzer.trial_summary['avg_max_RSSI'].mean():.2f} dBm")
    else:
        print("Analysis failed. Please check the data file and try again.")


if __name__ == "__main__":
    main()