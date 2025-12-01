import yaml
from src.bcivis.manager.core import DatasetManager


config_path = "C:/Users/ncohe/Desktop/Github projects/BIDCI/src/bcivis/config/motor_imagery_ds003810.yaml"
with open(config_path, "r") as f:
    config = yaml.safe_load(f)

manager = DatasetManager(config=config)
manager.load_all()
manager.preprocess_all()
manager.summarize_all(with_plots=config.get("sanity_check", {}).get("enable_plots", False))

