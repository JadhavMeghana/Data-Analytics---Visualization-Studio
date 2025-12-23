"""
Configuration Loader Utility
Loads configuration from YAML file
"""

import yaml
import os
from pathlib import Path


def load_config(config_path='config.yaml'):
    """
    Load configuration from YAML file
    
    Args:
        config_path: Path to config file
        
    Returns:
        dict: Configuration dictionary
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config


def get_db_connection_string(config):
    """
    Build Oracle database connection string
    
    Args:
        config: Configuration dictionary
        
    Returns:
        str: Connection string
    """
    db_config = config['database']
    return f"{db_config['username']}/{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['service_name']}"

