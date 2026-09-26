import yml
import os

def load_config(config_path: str = "config/config.yml") -> dict:
    """
    Load configuration from a YAML file.

    Args:
        config_path (str): Path to the YAML configuration file.

    Returns:
        dict: The loaded configuration.
    """
    with open(config_path, 'r') as f:
        config = yml.safe_load(f)
    return config