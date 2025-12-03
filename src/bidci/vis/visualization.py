import mne
import matplotlib.pyplot as plt
from typing import Optional
from bidci.utils.helpers import get_save_path
from bidci.config.config_model import ConfigModel
import os

def plot_raw(raw, config: ConfigModel, subject: Optional[str] = None, run: Optional[str] = None):
    vis_cfg = config.visualization
    duration = vis_cfg.duration if vis_cfg.duration is not None else 60.0
    start = vis_cfg.start if vis_cfg.start is not None else 0.0
    n_channels = vis_cfg.n_channels if vis_cfg.n_channels is not None else 8
    scalings = vis_cfg.scalings or dict(eeg=1e2)
    show_events = bool(vis_cfg.show_events)

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
        filepath = os.path.join(save_path, f"raw_eeg_signal.{config.save_figures.format}")
        fig.savefig(filepath)
        print(f"Saved: {filepath}")
        plt.close(fig)
    

def plot_psd(raw, config: ConfigModel, subject: Optional[str] = None, run: Optional[str] = None):
    vis_cfg = config.visualization
    fmin = vis_cfg.psd_fmin if vis_cfg.psd_fmin is not None else 0.1
    fmax = vis_cfg.psd_fmax if vis_cfg.psd_fmax is not None else 45.0
    average = bool(vis_cfg.psd_average)

    fig = raw.plot_psd(fmin=fmin, fmax=fmax, average=average)
    
    # Get save path and save if enabled
    save_path = get_save_path(config, subject, run, "psd")
    if save_path:
        filepath = os.path.join(save_path, f"power_spectral_density.{config.save_figures.format}")
        fig.savefig(filepath, dpi=config.save_figures.dpi)
        print(f"Saved: {filepath}")
        plt.close(fig)


def apply_montage(raw, config: ConfigModel):
    vis_cfg = config.visualization
    if bool(vis_cfg.use_montage):
        montage_kind = vis_cfg.montage_kind or "standard_1020"
        montage = mne.channels.make_standard_montage(montage_kind)
        raw.set_montage(montage)


def plot_sensors(raw, config: ConfigModel, subject: Optional[str] = None, run: Optional[str] = None):
    vis_cfg = config.visualization
    if bool(vis_cfg.use_montage):
        fig = raw.plot_sensors(kind='topomap', ch_type='eeg', show_names=True)

        # Get save path and save if enabled
        save_path = get_save_path(config, subject, run, "sensors")
        if save_path:
            filepath = os.path.join(save_path, f"sensor_layout.{config.save_figures.format}")
            fig.savefig(filepath, dpi=config.save_figures.dpi)
            print(f"Saved: {filepath}")
            plt.close(fig)


def plot_all_conditionwise(epochs, event_labels, config: ConfigModel, subject: Optional[str] = None, run: Optional[str] = None):
    vis_cfg = config.visualization
    fmin = vis_cfg.psd_fmin if vis_cfg.psd_fmin is not None else 1
    fmax = vis_cfg.psd_fmax if vis_cfg.psd_fmax is not None else 40
    topomap_times = vis_cfg.topomap_times or [0.5, 1.0, 1.5]

    for label in event_labels:
        # Plot epochs image
        fig_epochs = epochs[label].plot_image(picks="eeg", combine="mean", show=False)[0]
        
        # Save epochs image
        save_path = get_save_path(config, subject, run, "epochs")
        if save_path:
            filepath = os.path.join(save_path, f"epochs_image_{label}.{config.save_figures.format}")
            fig_epochs.savefig(filepath, dpi=config.save_figures.dpi)
            print(f"Saved: {filepath}")
            plt.close(fig_epochs)
        
        # Evoked
        evoked = epochs[label].average()
        if not evoked.info.get("dig"):
            montage_kind = vis_cfg.montage_kind or "standard_1020"
            evoked.set_montage(mne.channels.make_standard_montage(montage_kind))
        
        fig_topomap = evoked.plot_topomap(times=topomap_times, ch_type='eeg')
        
        # Save topomap
        save_path = get_save_path(config, subject, run, "topomap")
        if save_path:
            filepath = os.path.join(save_path, f"topomap_{label}.{config.save_figures.format}")
            fig_topomap.savefig(filepath, dpi=config.save_figures.dpi)
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
            filepath = os.path.join(save_path, f"psd_conditionwise_{label}.{config.save_figures.format}")
            fig_psd.savefig(filepath, dpi=config.save_figures.dpi)
            print(f"Saved: {filepath}")
            plt.close(fig_psd)
        else:
            plt.show()
