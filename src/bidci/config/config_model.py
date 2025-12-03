from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class PreprocessingConfig(BaseModel):
    load_data: bool = True
    already_filtered: bool = False
    original_band: Optional[List[float]] = None
    bandpass: Optional[List[float]] = None
    notch_filter: Optional[int] = None
    tmin: Optional[float] = None
    tmax: Optional[float] = None
    baseline: Optional[List[float]] = None


class VisualizationConfig(BaseModel):
    duration: Optional[float] = 60.0
    start: Optional[float] = 0.0
    n_channels: Optional[int] = 8
    scalings: dict = Field(default_factory=dict)
    use_montage: bool = False
    montage_kind: Optional[str] = "standard_1020"
    psd_fmin: Optional[float] = 0.1
    psd_fmax: Optional[float] = 45.0
    psd_average: bool = True
    picks: Optional[str] = "eeg"
    show_events: bool = True
    topomap_times: Optional[List[float]] = None
    baseline: Optional[List[float]] = None


class SaveFiguresConfig(BaseModel):
    enabled: bool = True
    format: str = "png"
    dpi: int = 300


class SanityCheckConfig(BaseModel):
    enable_plots: bool = False


class OutputConfig(BaseModel):
    base_directory: Optional[str] = None


class ConfigModel(BaseModel):
    bids_root: str
    task: str
    subjects: Optional[List[str]] = None
    runs: Optional[List[str]] = None
    verbose: bool = False

    class_map: Optional[dict] = None
    event_id: Optional[dict] = None

    preprocessing: PreprocessingConfig = Field(default_factory=PreprocessingConfig)
    visualization: VisualizationConfig = Field(default_factory=VisualizationConfig)
    sanity_check: SanityCheckConfig = Field(default_factory=SanityCheckConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    save_figures: SaveFiguresConfig = Field(default_factory=SaveFiguresConfig)
