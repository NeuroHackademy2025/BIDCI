import os

def get_save_path(config, subject, run, plot_type):

    # Check if saving is enabled
    save_cfg = config.get("save_figures", {})
    if not save_cfg.get("enabled", False):
        return None
    
    # Get base directory
    base_dir = config.get("output", {}).get("base_directory", "results")
    
    # Build path: base_dir/sub-XX/run-X/plot_type/
    subject_dir = f"sub-{subject}"
    run_dir = f"run-{run}"
    
    save_path = os.path.join(base_dir, subject_dir, run_dir, plot_type)
    
    # Create directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)
    
    return save_path
