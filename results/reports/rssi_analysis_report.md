
# RSSI Trial Data Analysis Report

## Executive Summary

This report presents a comprehensive analysis of RSSI (Received Signal Strength Indicator) 
trial data collected from wireless communication experiments. The analysis covers 
performance evaluation across different devices, trials, and experimental scenarios.

## Dataset Overview

- **Total Records**: 12
- **Number of Devices**: 2
- **Number of Trials**: 6
- **Number of Scenarios**: 5
- **Total Sessions**: 119

## Device Information

- **Device A**:
  - Total Sessions: 61
  - Average Median RSSI: -72.67 ± 3.89 dBm
  - Average Max RSSI: -70.11 ± 4.58 dBm
- **Device B**:
  - Total Sessions: 58
  - Average Median RSSI: -71.78 ± 4.15 dBm
  - Average Max RSSI: -68.84 ± 5.31 dBm


## Key Findings

### 1. Overall RSSI Performance
- **Overall Average Median RSSI**: -72.26 dBm
- **Overall Average Max RSSI**: -69.52 dBm
- **Median RSSI Range**: -78.8 to -67.9 dBm
- **Max RSSI Range**: -78.1 to -64.9 dBm

### 2. Device Performance Comparison
- **Device A**:
  - Average Median RSSI: -72.67 ± 3.89 dBm
  - Average Max RSSI: -70.11 ± 4.58 dBm
  - Total Sessions: 61
- **Device B**:
  - Average Median RSSI: -71.78 ± 4.15 dBm
  - Average Max RSSI: -68.84 ± 5.31 dBm
  - Total Sessions: 58

- **Device Performance Differences**:
  - Median RSSI Difference: 0.89 dBm
  - Max RSSI Difference: 1.27 dBm


### 3. Scenario Performance Analysis
- **Doze Mode**:
  - Average Median RSSI: -72.32 ± nan dBm
  - Average Max RSSI: -70.58 ± nan dBm
  - Total Sessions: 19.0
- **Metal Interference**:
  - Average Median RSSI: -78.84 ± nan dBm
  - Average Max RSSI: -78.11 ± nan dBm
  - Total Sessions: 19.0
- **Pocket**:
  - Average Median RSSI: -74.67 ± nan dBm
  - Average Max RSSI: -71.10 ± nan dBm
  - Total Sessions: 20.0
- **Static 15min**:
  - Average Median RSSI: -70.70 ± nan dBm
  - Average Max RSSI: -66.91 ± nan dBm
  - Total Sessions: 22.0
- **Static 5min**:
  - Average Median RSSI: -67.94 ± nan dBm
  - Average Max RSSI: -64.94 ± nan dBm
  - Total Sessions: 16.0


### 4. Trial Performance Ranking

#### Top 5 Trials by Median RSSI:
1. Trial_001: -67.94 dBm (Static 5min)
2. Trial_003: -69.09 dBm (nan)
3. Trial_002: -70.70 dBm (Static 15min)
4. Trial_004: -72.32 dBm (Doze Mode)
5. Trial_005: -74.67 dBm (Pocket)


#### Top 5 Trials by Max RSSI:
1. Trial_001: -64.94 dBm (Static 5min)
2. Trial_003: -65.48 dBm (nan)
3. Trial_002: -66.91 dBm (Static 15min)
4. Trial_004: -70.58 dBm (Doze Mode)
5. Trial_005: -71.10 dBm (Pocket)


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
*Report generated on 2026-03-02 00:43:39*
