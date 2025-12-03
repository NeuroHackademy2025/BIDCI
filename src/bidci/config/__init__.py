"""Configuration package for BIDCI.

This package contains Pydantic config models used to validate YAML configuration
files for the project.
"""

from .config_model import ConfigModel

__all__ = ["ConfigModel"]
