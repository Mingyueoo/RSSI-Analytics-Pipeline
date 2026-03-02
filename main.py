# @Version :1.0
# @Author  : Mingyue
# @File    : main.py
# @Time    : 01/03/2026

"""
RSSI 数据分析主程序
==================
统一调度所有分析模块，生成完整的分析报告和可视化结果

使用方法:
    python main.py              # 运行完整流程
    python main.py data         # 仅运行数据加载
    python main.py rssi         # 仅运行 RSSI 分析
    python main.py battery      # 仅运行电池分析
    python main.py mode         # 仅运行模式分析
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils import load_config, ensure_dirs
from src.data_loader import process_rssi_data
from src.visualization import RSSIAnalyzer
from src.battery_analyzer import main as battery_analysis
from src.mode_analyzer import main as mode_analysis


def print_header(title):
    """打印格式化的标题"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_section(title):
    """打印格式化的章节标题"""
    print("\n" + "-" * 80)
    print(f"[{title}]")
    print("-" * 80)


def main():
    """主函数：执行完整的数据分析流程"""
    
    print_header("RSSI 数据分析系统")
    
    # 步骤 0: 加载配置并确保目录存在
    print_section("步骤 0: 加载配置文件")
    try:
        config = load_config()
        ensure_dirs(config)
        print("✓ 配置加载完成")
        print(f"  - 原始数据目录: {config['paths']['raw_data_dir']}")
        print(f"  - 处理数据目录: {config['paths']['processed_data_dir']}")
        print(f"  - 结果目录: {config['paths']['results_dir']}")
        print(f"  - 图表目录: {config['paths']['plots_dir']}")
        print(f"  - 报告目录: {config['paths']['report_dir']}")
    except Exception as e:
        print(f"✗ 配置加载失败: {str(e)}")
        return
    
    # 步骤 1: 数据对齐与预处理
    print_section("步骤 1: 数据对齐与预处理")
    try:
        process_rssi_data(config)
        print("✓ 数据对齐完成")
    except FileNotFoundError as e:
        print(f"✗ 数据文件未找到: {str(e)}")
        print("  请确保原始数据文件存在于 data/raw/ 目录")
        return
    except Exception as e:
        print(f"✗ 数据对齐失败: {str(e)}")
        return
    
    # 步骤 2: RSSI 试验数据分析与可视化
    print_section("步骤 2: RSSI 试验数据分析")
    try:
        analyzer = RSSIAnalyzer(config=config)
        results = analyzer.run_complete_analysis()
        
        if results:
            print("✓ RSSI 分析完成")
            print(f"  - 生成图表: {len([k for k in results.keys() if 'plot' in k])} 个")
            print(f"  - 生成数据文件: {len(results.get('csv_files', {}))} 个")
            if results.get('report'):
                print(f"  - 生成报告: {results['report']}")
        else:
            print("⚠ RSSI 分析未生成结果")
    except FileNotFoundError as e:
        print(f"⚠ RSSI 数据文件未找到，跳过此步骤: {str(e)}")
    except Exception as e:
        print(f"✗ RSSI 分析出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 步骤 3: 电池使用分析
    print_section("步骤 3: 电池使用分析")
    try:
        battery_analysis(config)
        print("✓ 电池分析完成")
    except FileNotFoundError as e:
        print(f"⚠ 电池数据文件未找到，跳过此步骤: {str(e)}")
    except Exception as e:
        print(f"✗ 电池分析出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 步骤 4: 模式性能分析
    print_section("步骤 4: 模式性能分析")
    try:
        mode_analysis(config)
        print("✓ 模式分析完成")
    except FileNotFoundError as e:
        print(f"⚠ 模式数据文件未找到，跳过此步骤: {str(e)}")
    except Exception as e:
        print(f"✗ 模式分析出错: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # 完成
    print_header("分析流程完成")
    print("\n生成的文件位置:")
    print(f"  📁 处理后数据: {config['paths']['processed_data_dir']}/")
    print(f"  📊 可视化图表: {config['paths']['plots_dir']}/")
    print(f"  📄 分析报告: {config['paths']['report_dir']}/")
    print("\n")


def run_data_loader_only():
    """仅运行数据加载和对齐"""
    print_header("数据加载模块")
    config = load_config()
    ensure_dirs(config)
    process_rssi_data(config)
    print("\n✓ 数据加载完成\n")


def run_visualization_only():
    """仅运行 RSSI 可视化分析"""
    print_header("RSSI 可视化分析模块")
    config = load_config()
    analyzer = RSSIAnalyzer(config=config)
    analyzer.run_complete_analysis()
    print("\n✓ RSSI 分析完成\n")


def run_battery_analysis_only():
    """仅运行电池分析"""
    print_header("电池使用分析模块")
    config = load_config()
    battery_analysis(config)
    print("\n✓ 电池分析完成\n")


def run_mode_analysis_only():
    """仅运行模式分析"""
    print_header("模式性能分析模块")
    config = load_config()
    mode_analysis(config)
    print("\n✓ 模式分析完成\n")


def print_usage():
    """打印使用说明"""
    print("\n" + "=" * 80)
    print("RSSI 数据分析系统 - 使用说明".center(80))
    print("=" * 80)
    print("\n用法:")
    print("  python main.py              运行完整分析流程")
    print("  python main.py data         仅运行数据加载和对齐")
    print("  python main.py rssi         仅运行 RSSI 可视化分析")
    print("  python main.py battery      仅运行电池使用分析")
    print("  python main.py mode         仅运行模式性能分析")
    print("  python main.py help         显示此帮助信息")
    print("\n可用模块:")
    print("  - data:    数据加载和对齐")
    print("  - rssi:    RSSI 试验数据分析与可视化")
    print("  - battery: 电池使用分析")
    print("  - mode:    模式性能分析")
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    # 检查命令行参数，支持单独运行某个模块
    if len(sys.argv) > 1:
        module = sys.argv[1].lower()
        
        if module == "data":
            run_data_loader_only()
        elif module == "rssi":
            run_visualization_only()
        elif module == "battery":
            run_battery_analysis_only()
        elif module == "mode":
            run_mode_analysis_only()
        elif module in ["help", "-h", "--help", "?"]:
            print_usage()
        else:
            print(f"\n✗ 未知模块: {module}")
            print_usage()
    else:
        # 运行完整流程
        main()
