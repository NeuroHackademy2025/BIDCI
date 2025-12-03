import mne
from typing import Optional
from mne_bids import BIDSPath, read_raw_bids
from bidci.config.config_model import ConfigModel


class BIDSDataLoader:
    def __init__(self, bids_root: str, subject: str, task: str, session: Optional[str] = None, run: Optional[str] = None, config: ConfigModel = None, verbose: bool = False):
        self.bids_root = bids_root
        self.subject = subject
        self.task = task
        self.session = session
        self.run = run
        self.config: ConfigModel = config
        self.verbose = verbose

        self.raw = None
        self.events = None
        self.event_id = None

    def load(self):
        bids_path = BIDSPath(
            root=self.bids_root,
            subject=self.subject,
            session=self.session,
            task=self.task,
            run=self.run,
            suffix="eeg",
            extension=".edf"
        )
        if self.verbose:
            print(f"Loading BIDS data from: {bids_path}")

        verbose_level = 'CRITICAL' if not self.verbose else True

        self.raw = read_raw_bids(bids_path=bids_path, verbose=verbose_level)
        # typed model stores `event_id` as attribute (may be None)
        # safe fallback: if `config` is None, leave event_map as None
        event_map = None
        if self.config is not None:
            event_map = getattr(self.config, "event_id", None)

        self.events, self.event_id = mne.events_from_annotations(self.raw, event_id=event_map, verbose=verbose_level)
        
    def summary(self):
        print(f"Subject: {self.subject}, Task: {self.task}, Run: {self.run}")
        print(f"Data shape: {self.raw.get_data().shape}")
        print(f"Sampling rate: {self.raw.info['sfreq']} Hz")
        print(f"Number of events: {len(self.events)}")
        print(f"Event ID map: {self.event_id}")

    def get_raw(self):
        return self.raw

    def get_events(self):
        return self.events, self.event_id
