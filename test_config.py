# @Version :1.0
# @Author  : Mingyue
# @File    : test_config.py
# @Time    : 01/03/2026

"""
配置测试脚本
============
用于验证配置文件是否正确加载
"""

import sys
from pathlib import Path

# 添加 src 目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from src.utils import load_config, ensure_dirs


def test_config():
    """Test configuration loading"""
    print("=" * 60)
    print("Configuration Test")
    print("=" * 60)
    
    try:
        # Load config
        print("\n1. Loading configuration file...")
        config = load_config()
        print("OK - Configuration loaded successfully")
        
        # Display path configuration
        print("\n2. Path Configuration:")
        for key, value in config['paths'].items():
            print(f"   - {key}: {value}")
        
        # Display device mapping
        print("\n3. Device Mapping:")
        for uuid, label in config['devices'].items():
            print(f"   - {uuid[:8]}...: {label}")
        
        # Display scenario mapping
        print("\n4. Scenario Mapping:")
        for scenario, label in config['scenarios'].items():
            print(f"   - {scenario}: {label}")
        
        # Display analysis parameters
        print("\n5. Analysis Parameters:")
        for key, value in config['analysis'].items():
            print(f"   - {key}: {value}")
        
        # Display plotting configuration
        print("\n6. Plotting Configuration:")
        print(f"   - style: {config['plotting']['style']}")
        print(f"   - dpi: {config['plotting']['dpi']}")
        print(f"   - colors:")
        for color_name, color_value in config['plotting']['colors'].items():
            print(f"     * {color_name}: {color_value}")
        
        # Ensure directories exist
        print("\n7. Creating necessary directories...")
        ensure_dirs(config)
        print("OK - Directory check complete")
        
        print("\n" + "=" * 60)
        print("OK - All tests passed! Configuration is working.")
        print("=" * 60)
        
        return True
        
    except FileNotFoundError as e:
        print(f"\nERROR: Configuration file not found")
        print(f"  {str(e)}")
        return False
    except KeyError as e:
        print(f"\nERROR: Configuration file missing required key")
        print(f"  {str(e)}")
        return False
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)
