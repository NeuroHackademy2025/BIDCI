from mne import Epochs, pick_types
from mne.io import Raw
from bidci.config.config_model import ConfigModel


def _get_timing(pre_cfg):
    """Extract tmin, tmax, baseline with defaults."""
    tmin = pre_cfg.tmin if pre_cfg.tmin is not None else -0.5
    tmax = pre_cfg.tmax if pre_cfg.tmax is not None else 2.5
    baseline = pre_cfg.baseline
    return tmin, tmax, baseline


def _validate_baseline(tmin: float, tmax: float, baseline):
    """Ensure baseline interval is inside the epoch window."""
    if baseline is None:
        return None

    b_start, b_end = baseline

    if b_start is not None and b_start < tmin:
        raise ValueError(
            f"Baseline start {b_start} must be within epoch window starting at {tmin}."
        )
    if b_end is not None and b_end > tmax:
        raise ValueError(
            f"Baseline end {b_end} must be within epoch window ending at {tmax}."
        )

    return (b_start, b_end)


def _apply_bandpass(raw: Raw, pre_cfg) -> Raw:
    """Apply band-pass filter if not already filtered."""
    bandpass = pre_cfg.bandpass or [1.0, 40.0]
    already_filtered = bool(pre_cfg.already_filtered)
    original_band = pre_cfg.original_band or []

    if already_filtered:
        # Optional: warn if bandpass != original_band
        # (but do nothing to avoid double-filtering)
        return raw

    l_freq, h_freq = bandpass
    # Ensure data is loaded before filtering
    raw_copy = raw.copy()
    if not raw_copy.preload:
        raw_copy.load_data()
    return raw_copy.filter(l_freq=l_freq, h_freq=h_freq)


def _apply_notch(raw: Raw, pre_cfg) -> Raw:
    """Apply notch filter for line noise if configured and data is being loaded."""
    notch_freq = pre_cfg.notch_filter
    load_data = bool(pre_cfg.load_data)

    if notch_freq and load_data:
        working = raw.copy()
        if not working.preload:
            working.load_data()
        raw = working.notch_filter(freqs=notch_freq)
    return raw


def _epoch_data(raw: Raw, events, event_id: dict, tmin: float, tmax: float, baseline):
    """Epoch the continuous data around events, picking only EEG channels."""
    picks = pick_types(raw.info, meg=False, eeg=True, stim=False, eog=False)
    epochs = Epochs(
        raw,
        events,
        event_id=event_id,
        tmin=tmin,
        tmax=tmax,
        baseline=baseline,
        picks=picks,
        preload=True,
        event_repeated="merge",
    )
    return epochs


def preprocess_raw(raw: Raw, event_id: dict, events, config: ConfigModel):
    """
    High-level preprocessing pipeline:
    1. Band-pass filter (if needed)
    2. Notch filter (if configured and loading data)
    3. Epoch around events with baseline correction
    """
    pre_cfg = config.preprocessing

    # 1. Timing parameters
    tmin, tmax, baseline = _get_timing(pre_cfg)
    baseline = _validate_baseline(tmin, tmax, baseline)

    # 2. Filtering
    if pre_cfg.notch_filter is not None and pre_cfg.notch_filter < pre_cfg.bandpass[1]:
        raw = _apply_notch(raw, pre_cfg)

    raw = _apply_bandpass(raw, pre_cfg)

    # 3. Epoching (includes picking EEG channels)
    epochs = _epoch_data(raw, events, event_id, tmin, tmax, baseline)

    return epochs
