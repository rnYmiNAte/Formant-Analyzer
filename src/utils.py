# src/utils.py
"""
Helper utilities for audio loading, preprocessing, and basic signal operations.
"""

import numpy as np
import soundfile as sf
from scipy.signal import resample


def load_audio(
    filepath: str,
    target_sr: int = 16000,
    mono: bool = True,
    normalize: bool = True
) -> tuple[np.ndarray, int]:
    """
    Load WAV file, optionally resample to target sample rate, convert to mono,
    and normalize peak amplitude to [-1, 1].

    Returns:
        audio: numpy array (float32)
        sample_rate: int
    """
    audio, sr = sf.read(filepath, dtype='float32')

    # Convert to mono if stereo
    if mono and len(audio.shape) > 1:
        audio = np.mean(audio, axis=1)

    # Resample if needed
    if sr != target_sr:
        num_samples = int(len(audio) * target_sr / sr)
        audio = resample(audio, num_samples)
        sr = target_sr

    # Normalize peak amplitude
    if normalize and np.max(np.abs(audio)) > 0:
        audio = audio / np.max(np.abs(audio))

    return audio, sr


def pre_emphasis(signal: np.ndarray, coeff: float = 0.97) -> np.ndarray:
    """
    Apply pre-emphasis filter to boost high frequencies.
    """
    if coeff == 0:
        return signal
    return np.append(signal[0], signal[1:] - coeff * signal[:-1])


def frame_signal(
    signal: np.ndarray,
    frame_length: int,
    hop_length: int,
    window: np.ndarray | None = None
) -> np.ndarray:
    """
    Split signal into overlapping frames.

    Returns:
        2D array of shape (n_frames, frame_length)
    """
    if window is None:
        window = np.hamming(frame_length)

    n_frames = 1 + (len(signal) - frame_length) // hop_length
    frames = np.lib.stride_tricks.sliding_window_view(
        signal, frame_length
    )[::hop_length][:n_frames]

    return frames * window


def seconds_to_samples(time_sec: float, sr: int) -> int:
    """Convert seconds to sample count."""
    return int(time_sec * sr)


def hz_to_mel(hz: float | np.ndarray) -> float | np.ndarray:
    """Convert Hz to mel scale (HTK formula)."""
    return 2595.0 * np.log10(1.0 + hz / 700.0)


def mel_to_hz(mel: float | np.ndarray) -> float | np.ndarray:
    """Convert mel to Hz (HTK formula)."""
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)
