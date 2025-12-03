from bidci.manager.core import DatasetManager

if __name__ == "__main__":
    # Path to the config file, relative to this test.py file
    config_path = "C:/Users/ncohe/Desktop/Github projects/BIDCI/src/bidci/config/motor_imagery_ds003810.yaml"
    manager = DatasetManager.from_yaml(config_path)
    manager.load_all()
    manager.preprocess_all()
    manager.summarize_all()
