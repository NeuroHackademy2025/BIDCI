from bidci.config.config_model import ConfigModel


def run_pipeline(raw, events, event_id, config: ConfigModel):
    """Placeholder motor imagery pipeline entrypoint.

    Parameters
    ----------
    raw : mne.io.Raw
        The raw EEG object.
    events : array-like
        Events array.
    event_id : dict
        Event id mapping.
    config : ConfigModel
        Validated configuration model.

    Notes
    -----
    This module is currently a stub. Implement the full pipeline using
    the typed `ConfigModel` so downstream code can access configuration
    via attributes (e.g., `config.preprocessing.tmin`).
    """
    raise NotImplementedError("Motor imagery pipeline not yet implemented")