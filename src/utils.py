# @Version :1.0
# @Author  : Mingyue
# @File    : utils.py
# @Time    : 01/03/2026 21:20
import yaml
import os


def load_config(config_path="config/config.yaml"):
    """
    Load YAML configuration file
    
    Args:
        config_path (str): Path to config file, default is config/config.yaml
        
    Returns:
        dict: Configuration dictionary
        
    Raises:
        FileNotFoundError: If config file does not exist
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config


def ensure_dirs(config):
    """
    Create output directories based on configuration if they don't exist
    
    Args:
        config (dict): Configuration dictionary
    """
    for key, path in config['paths'].items():
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
            print(f"Created directory: {path}")
