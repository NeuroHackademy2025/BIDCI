import mne
import matplotlib.pyplot as plt
from src.bidci.utils.helpers import get_save_path  
import os

def plot_raw(raw, config, subject=None, run=None):
    vis_cfg = config.get("visualization", {})
    duration = vis_cfg.get("duration", 60.0)
    start = vis_cfg.get("start", 0.0)
    n_channels = vis_cfg.get("n_channels", 8)
    scalings = vis_cfg.get("scalings", dict(eeg=1e2))
    show_events = vis_cfg.get("show_events", True)

    raw_copy = raw.copy()

    if not show_events:
        raw_copy.set_annotations(None)

    fig = raw_copy.plot(duration=duration,
                  start=start,
                  scalings=scalings,
                  n_channels=n_channels,
                  title="Raw EEG Signal")

    # Get save path and save if enabled
    save_path = get_save_path(config, subject, run, "raw")
    if save_path:
        filepath = os.path.join(save_path, f"raw_eeg_signal.{config['save_figures']['format']}")
        fig.savefig(filepath)
        print(f"Saved: {filepath}")
        plt.close(fig)
    

def plot_psd(raw, config, subject=None, run=None):
    vis_cfg = config.get("visualization", {})
    fmin = vis_cfg.get("psd_fmin", 0.1)
    fmax = vis_cfg.get("psd_fmax", 45.0)
    average = vis_cfg.get("psd_average", True)

    fig = raw.plot_psd(fmin=fmin, fmax=fmax, average=average)
    
    # Get save path and save if enabled
    save_path = get_save_path(config, subject, run, "psd")
    if save_path:
        filepath = os.path.join(save_path, f"power_spectral_density.{config['save_figures']['format']}")
        fig.savefig(filepath, dpi=config['save_figures']['dpi'])
        print(f"Saved: {filepath}")
        plt.close(fig)


def apply_montage(raw, config):
    vis_cfg = config.get("visualization", {})
    if vis_cfg.get("use_montage", False):
        montage_kind = vis_cfg.get("montage_kind", "standard_1020")
        montage = mne.channels.make_standard_montage(montage_kind)
        raw.set_montage(montage)


def plot_sensors(raw, config, subject=None, run=None):
    vis_cfg = config.get("visualization", {})
    if vis_cfg.get("use_montage", False):
        fig = raw.plot_sensors(kind='topomap', ch_type='eeg', show_names=True)
        
        # Get save path and save if enabled
        save_path = get_save_path(config, subject, run, "sensors")
        if save_path:
            filepath = os.path.join(save_path, f"sensor_layout.{config['save_figures']['format']}")
            fig.savefig(filepath, dpi=config['save_figures']['dpi'])
            print(f"Saved: {filepath}")
            plt.close(fig)


def plot_all_conditionwise(epochs, event_labels, config, subject=None, run=None):
    vis_cfg = config.get("visualization", {})
    fmin = vis_cfg.get("psd_fmin", 1)
    fmax = vis_cfg.get("psd_fmax", 40)
    topomap_times = vis_cfg.get("topomap_times", [0.5, 1.0, 1.5])

    for label in event_labels:
        # Plot epochs image
        fig_epochs = epochs[label].plot_image(picks="eeg", combine="mean", show=False)[0]
        
        # Save epochs image
        save_path = get_save_path(config, subject, run, "epochs")
        if save_path:
            filepath = os.path.join(save_path, f"epochs_image_{label}.{config['save_figures']['format']}")
            fig_epochs.savefig(filepath, dpi=config['save_figures']['dpi'])
            print(f"Saved: {filepath}")
            plt.close(fig_epochs)
        
        # Evoked
        evoked = epochs[label].average()
        if not evoked.info.get("dig"):
            montage_kind = vis_cfg.get("montage_kind", "standard_1020")
            evoked.set_montage(mne.channels.make_standard_montage(montage_kind))
        
        fig_topomap = evoked.plot_topomap(times=topomap_times, ch_type='eeg')
        
        # Save topomap
        save_path = get_save_path(config, subject, run, "topomap")
        if save_path:
            filepath = os.path.join(save_path, f"topomap_{label}.{config['save_figures']['format']}")
            fig_topomap.savefig(filepath, dpi=config['save_figures']['dpi'])
            print(f"Saved: {filepath}")
            plt.close(fig_topomap)

        # PSD
        psds, freqs = epochs[label].compute_psd(fmin=fmin, fmax=fmax).get_data(return_freqs=True)
        psds_mean = psds.mean(axis=0)
        psds_std = psds.std(axis=0)

        fig_psd = plt.figure()
        plt.plot(freqs, psds_mean.T)
        plt.fill_between(freqs,
                        (psds_mean - psds_std).mean(axis=0),
                        (psds_mean + psds_std).mean(axis=0),
                        alpha=0.3)
        plt.title(f"PSD (mean ± std) - {label}")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Power")
        
        # Save PSD plot
        save_path = get_save_path(config, subject, run, "psd")
        if save_path:
            filepath = os.path.join(save_path, f"psd_conditionwise_{label}.{config['save_figures']['format']}")
            fig_psd.savefig(filepath, dpi=config['save_figures']['dpi'])
            print(f"Saved: {filepath}")
            plt.close(fig_psd)
        else:
            plt.show()
