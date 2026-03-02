# src/__init__.py
"""
formant-analyzer package
"""

from .analyzer import extract_formants
from .plotter import plot_formants
from .utils import (
    load_audio,
    pre_emphasis,
    frame_signal,
    seconds_to_samples,
    hz_to_mel,
    mel_to_hz,
)

__all__ = [
    "extract_formants",
    "plot_formants",
    "load_audio",
    "pre_emphasis",
    "frame_signal",
    "seconds_to_samples",
    "hz_to_mel",
    "mel_to_hz",
]

__version__ = "0.1.0"
