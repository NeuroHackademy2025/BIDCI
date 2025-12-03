from mne import Epochs, pick_types
from mne.io import Raw
from bidci.config.config_model import ConfigModel


def preprocess_raw(raw: Raw, event_id: dict, events, config: ConfigModel):
    pre_cfg = config.preprocessing

    # Timing
    tmin = pre_cfg.tmin if pre_cfg.tmin is not None else -0.5
    tmax = pre_cfg.tmax if pre_cfg.tmax is not None else 2.5
    baseline = pre_cfg.baseline
    load_data = bool(pre_cfg.load_data)

    # Filtering
    bandpass = pre_cfg.bandpass or [1.0, 40.0]
    l_freq, h_freq = bandpass[0], bandpass[1]
    already_filtered = bool(pre_cfg.already_filtered)
    original_band = tuple(pre_cfg.original_band) if pre_cfg.original_band is not None else (0.5, 45.0)
    
    if load_data:
         raw.load_data()
    else:
        print("⚠️ Not loading data, assuming it's already loaded, notch filter will not work")

    # Check if already filtered
    if not already_filtered:
        raw.filter(l_freq, h_freq)
    elif (l_freq, h_freq) != original_band:
        print(f"⚠️ Already filtered in {original_band}, but requested: ({l_freq}, {h_freq})")

    # Notch filter
    notch_freq = pre_cfg.notch_filter
    if notch_freq and load_data:
        raw.notch_filter(freqs=notch_freq)

    # Picks
    picks = pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False)

    # Epoching
    epochs = Epochs(
        raw, events, event_id=event_id, tmin=tmin, tmax=tmax,
        baseline=baseline, picks=picks, preload=True,
        event_repeated='merge'  # avoid crash
    )
    return epochs

