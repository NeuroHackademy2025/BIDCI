import os
from bidci.config.config_model import ConfigModel


def get_save_path(config: ConfigModel, subject, run, plot_type):

    # Check if saving is enabled
    save_cfg = config.save_figures
    if not bool(save_cfg.enabled):
        return None

    # Get base directory
    base_dir = config.output.base_directory or "results"

    # Build path: base_dir/sub-XX/run-X/plot_type/
    subject_dir = f"sub-{subject}"
    run_dir = f"run-{run}"

    save_path = os.path.join(base_dir, subject_dir, run_dir, plot_type)

    # Create directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    return save_path
