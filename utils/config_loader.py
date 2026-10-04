from pathlib import Path
import yaml

BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG_PATH = BASE_DIR / "config" / "config.yaml"


def load_config(config_path: str | Path | None = None) -> dict:
    path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    print(f"Loading configuration from: {path}")

    if not path.is_absolute():
        path = BASE_DIR / path

    with path.open("r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    return config