import json
from pathlib import Path


def get_config_file():
    config = None
    base_dir = Path(__file__).resolve().parent.parent
    config_path = base_dir / 'configs/pricing/current.json'
    with open(config_path, "r") as f:
        config = json.load(f)
    return config