from src.bcivis.io.loader import BIDSDataLoader
from src.bcivis.preprocessing.cleaning_pipeline import preprocess_raw
from src.bcivis.vis.visualization import apply_montage, plot_all_conditionwise, plot_raw, plot_psd, plot_sensors, plot_all_conditionwise
                

class DatasetManager:
    def __init__(self, config):
        self.config = config
        self.loaders = []
        self.epochs_list = []


    def load_all(self):
        subjects = self.config.get("subjects") or [self.config.get("subject")]
        runs = self.config.get("runs") or [self.config.get("run")]

        if not subjects or not runs:
            raise ValueError("Subjects and runs must be specified in the configuration.")
        
        for subject in subjects:
            for run in runs:
                loader = BIDSDataLoader(
                    bids_root=self.config["bids_root"],
                    subject=subject,
                    task=self.config["task"],
                    run=run,
                    config=self.config,
                    verbose=self.config.get("verbose", False)
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
    

    def summarize_all(self, with_plots=False):
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
                plot_sensors(raw, self.config,subject, run)
                plot_raw(raw, self.config, subject, run)
                plot_psd(raw, self.config, subject, run)    

                event_labels = list(loader.event_id.keys())
                plot_all_conditionwise(self.epochs_list[i], event_labels, self.config, subject, run)

                print("Plots generated.")
