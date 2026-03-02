# @Version :1.0
# @Author  : Mingyue
# @File    : __init__.py
# @Time    : 01/03/2026

"""
RSSI 数据分析包
===============

包含数据加载、预处理、可视化和分析功能
"""

from .utils import load_config, ensure_dirs
from .data_loader import process_rssi_data
from .visualization import RSSIAnalyzer
from .battery_analyzer import main as battery_analysis_main
from .mode_analyzer import main as mode_analysis_main

__version__ = '1.0.0'
__author__ = 'Mingyue'

__all__ = [
    'load_config',
    'ensure_dirs',
    'process_rssi_data',
    'RSSIAnalyzer',
    'battery_analysis_main',
    'mode_analysis_main'
]
