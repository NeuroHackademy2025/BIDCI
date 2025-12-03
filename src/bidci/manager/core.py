from pathlib import Path
import yaml
from bidci.io.loader import BIDSDataLoader
from bidci.preprocessing.cleaning_pipeline import preprocess_raw
from bidci.vis.visualization import apply_montage, plot_all_conditionwise, plot_raw, plot_psd, plot_sensors
from bidci.config.config_model import ConfigModel


class DatasetManager:
    def __init__(self, config: ConfigModel):
        """Expect a validated `ConfigModel` instance and store it."""
        self.config: ConfigModel = config
        self.loaders = []
        self.epochs_list = []

    @classmethod
    def from_yaml(cls, config_path: str | Path) -> "DatasetManager":
        """
        Load a YAML configuration file and return an initialized DatasetManager.

        Parameters
        ----------
        config_path : str or Path
            Path to the YAML configuration file.

        Returns
        -------
        DatasetManager
            A DatasetManager instance constructed from the given config.
        """
        # Normalize and read the YAML file using UTF-8
        config_path = Path(config_path).expanduser().resolve()
        with config_path.open("r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        # Validate and coerce with Pydantic. This returns a typed ConfigModel.
        cfg = ConfigModel.model_validate(raw)
        return cls(config=cfg)
    
    
    def load_all(self):
        # With the full typed migration we require `subjects` and `runs`
        # to be provided as lists on the `ConfigModel` instance.
        subjects = self.config.subjects
        runs = self.config.runs

        if not subjects or not runs:
            raise ValueError("`subjects` and `runs` must be provided as lists in the configuration (ConfigModel).")
        
        for subject in subjects:
            for run in runs:
                loader = BIDSDataLoader(
                    bids_root=self.config.bids_root,
                    subject=subject,
                    task=self.config.task,
                    run=run,
                    config=self.config,
                    verbose=bool(self.config.verbose)
                )
                loader.load()
                self.loaders.append(loader)


    def preprocess_all(self):
        if not self.loaders:
            raise RuntimeError("No data loaders available. Please load data first.")
        
        for loader in self.loaders:
            raw = loader.get_raw()
            events, event_id = loader.get_events()
            epochs = preprocess_raw(raw, event_id, events, self.config)
            self.epochs_list.append(epochs)

    def get_all_epochs(self):
        return self.epochs_list
    

    def summarize_all(self, with_plots: bool | None = None):
        # If caller didn't provide a value, read it from the manager's config
        if with_plots is None:
            with_plots = bool(self.config.sanity_check.enable_plots)

        for i, loader in enumerate(self.loaders):
            print(f"\n✅ Loader {i+1}")
            print(f"Subject: {loader.subject} | Run: {loader.run}")
            print("Raw info:", loader.raw.info)
            print("Event IDs:", loader.event_id)
            print("Events shape:", loader.events.shape)
            print("Epochs shape:", self.epochs_list[i].get_data().shape)
          
            subject = loader.subject
            run = loader.run
          
            if with_plots:
                print("Generating plots...")
                raw = loader.get_raw()
                apply_montage(raw, self.config)
                plot_sensors(raw, self.config, subject, run)
                plot_raw(raw, self.config, subject, run)
                plot_psd(raw, self.config, subject, run)

                event_labels = list(loader.event_id.keys())
                plot_all_conditionwise(self.epochs_list[i], event_labels, self.config, subject, run)

                print("Plots generated.")
