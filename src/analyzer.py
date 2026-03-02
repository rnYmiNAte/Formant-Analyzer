import numpy as np
from scipy.signal import lpc
import soundfile as sf

def extract_formants(wav_path, order=12, fs_target=16000):
    # Load audio
    audio, fs = sf.read(wav_path)
    if fs != fs_target:
        # Resample if needed (implement with scipy.resample)
        pass  # Placeholder

    # Pre-emphasis
    pre_emph = 0.97
    audio = np.append(audio[0], audio[1:] - pre_emph * audio[:-1])

    # Frame the signal (e.g., 25ms frames, 10ms overlap)
    frame_length = int(0.025 * fs)
    frame_step = int(0.01 * fs)
    frames = [audio[i:i+frame_length] for i in range(0, len(audio) - frame_length, frame_step)]

    formants = []
    for frame in frames:
        # Apply Hamming window
        frame *= np.hamming(len(frame))

        # Compute LPC coefficients
        A = lpc(frame, order)

        # Find roots of the polynomial
        roots = np.roots(A)
        roots = roots[np.imag(roots) >= 0]  # Positive imaginary parts

        # Compute frequencies and bandwidths
        freqs = np.arctan2(np.imag(roots), np.real(roots)) / (2 * np.pi) * fs
        freqs = sorted(freqs[freqs > 0])  # Sort and filter

        # Take F1 and F2 (first two formants)
        if len(freqs) >= 2:
            f1, f2 = freqs[0], freqs[1]
            # Normalize to 0-100% (assuming typical ranges: F1 200-1000Hz, F2 800-3000Hz)
            f1_norm = (f1 - 200) / (1000 - 200) * 100
            f2_norm = (f2 - 800) / (3000 - 800) * 100
            formants.append((f1_norm, f2_norm))

    # Average over frames
    if formants:
        return np.mean(formants, axis=0)
    return None
