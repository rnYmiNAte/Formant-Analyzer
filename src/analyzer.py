# src/analyzer.py
"""
Core formant extraction using LPC (via librosa).
Averages F1/F2 over voiced frames.
"""

import numpy as np
import librosa
from typing import Tuple, Optional

from .utils import (
    load_audio,
    pre_emphasis,
    frame_signal,
)


def extract_formants(
    wav_path: str,
    order: int = 12,                # LPC order (12–16 common for 16 kHz speech)
    target_sr: int = 16000,
    frame_length_sec: float = 0.025,
    hop_length_sec: float = 0.010,
    pre_emph_coeff: float = 0.97,
    f1_min: float = 200.0,
    f1_max: float = 1000.0,
    f2_min: float = 800.0,
    f2_max: float = 3000.0,
    max_bw: float = 1000.0,         # max formant bandwidth (Hz) to accept
) -> Optional[Tuple[float, float]]:
    """
    Extract average normalized F1 and F2 (%) from a WAV file.

    Returns:
        (f1_norm, f2_norm) or None if no valid formants found
    """
    # Load and preprocess audio
    audio, sr = load_audio(wav_path, target_sr=target_sr, mono=True, normalize=True)
    audio = pre_emphasis(audio, coeff=pre_emph_coeff)

    # Frame parameters in samples
    frame_length = int(frame_length_sec * sr)
    hop_length = int(hop_length_sec * sr)

    if len(audio) < frame_length:
        return None

    # Frame the signal with Hamming window
    frames = frame_signal(audio, frame_length, hop_length)

    f1_list = []
    f2_list = []

    for frame in frames:
        if np.std(frame) < 1e-6:  # skip near-silent frames
            continue

        # Compute LPC coefficients using Burg's method (librosa)
        try:
            a = librosa.lpc(frame, order=order)  # a.shape = (order+1,), a[0] == 1
        except Exception:
            continue

        # Find roots of the LPC polynomial
        roots = np.roots(a)
        roots = roots[np.imag(roots) >= 0]  # keep only positive imag part

        if len(roots) < 2:
            continue

        # Convert to frequencies (Hz) and bandwidths
        angles = np.angle(roots)
        freqs = angles * sr / (2 * np.pi)
        freqs = freqs[freqs > 0]  # positive frequencies only

        # Bandwidth approximation: bw = -ln(|root|) * sr / pi
        magnitudes = np.abs(roots)
        bws = -np.log(magnitudes) * sr / np.pi

        # Sort by frequency
        idx = np.argsort(freqs)
        freqs = freqs[idx]
        bws = bws[idx]

        # Take first two formants with reasonable bandwidth
        valid_formants = []
        for f, bw in zip(freqs, bws):
            if bw < max_bw and f > 50:  # rough sanity filter
                valid_formants.append((f, bw))
            if len(valid_formants) >= 2:
                break

        if len(valid_formants) >= 2:
            f1, _ = valid_formants[0]
            f2, _ = valid_formants[1]

            # Normalize to 0–100%
            f1_norm = np.clip((f1 - f1_min) / (f1_max - f1_min) * 100, 0, 100)
            f2_norm = np.clip((f2 - f2_min) / (f2_max - f2_min) * 100, 0, 100)

            f1_list.append(f1_norm)
            f2_list.append(f2_norm)

    if not f1_list:
        return None

    # Average over valid frames
    avg_f1 = np.mean(f1_list)
    avg_f2 = np.mean(f2_list)

    return avg_f1, avg_f2
