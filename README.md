# BIDCI

BIDCI is a Python project for loading, preprocessing, and visualizing EEG data for brain–computer interface (BCI) tasks. It currently focuses on BIDS-formatted motor imagery datasets and builds on top of MNE-Python.

The goal of BIDCI is to provide:
- A clear, configurable pipeline for basic EEG preprocessing (filtering, epoching, event handling).
- Reusable visualization functions for sanity checks and condition-wise inspection.
- A structure that can be extended to additional BCI paradigms (e.g., SSVEP, P300) and more advanced analysis.

At this stage, the main entry point is a configuration file (YAML) and a simple Python script (`test.py`) that:
1. Loads the dataset according to the config.
2. Runs a preprocessing pipeline.
3. Generates optional summary plots for each subject and run.

