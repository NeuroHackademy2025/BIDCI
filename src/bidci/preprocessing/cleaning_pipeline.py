from mne import Epochs, pick_types
from mne.io import Raw

def preprocess_raw(raw: Raw, event_id: dict, events, config: dict):
    pre_cfg = config.get("preprocessing", {})
    
    # Timing
    tmin = pre_cfg.get("tmin", -0.5)
    tmax = pre_cfg.get("tmax", 2.5)
    baseline = pre_cfg.get("baseline", None)
    load_data = pre_cfg.get("load_data", False)

    # Filtering
    l_freq, h_freq = pre_cfg.get("bandpass", [1., 40.])
    already_filtered = pre_cfg.get("already_filtered", False)
    original_band = tuple(pre_cfg.get("original_band", [0.5, 45.]))
    
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
    notch_freq = pre_cfg.get("notch_filter", 50)
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

