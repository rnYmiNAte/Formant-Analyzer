import parselmouth
import pandas as pd
import argparse
import numpy as np

def extract_formants(audio_path, time_step=0.01, max_formants=5, max_formant_freq=5500,
                     window_length=0.025, preemphasis=50.0):
    """
    Extract F1–F5 formant tracks from an audio file using Praat's Burg method.
    Returns a DataFrame with time and formant frequencies (Hz).
    """
    snd = parselmouth.Sound(audio_path)
    
    formant = snd.to_formant_burg(
        time_step=time_step,
        max_number_of_formants=max_formants,
        maximum_formant=max_formant_freq,   # ceiling; 5500 Hz common for adult males, 5000–6000 typical
        window_length=window_length,
        preemphasis_from=preemphasis
    )
    
    times = formant.ts()  # time points
    data = {'time': times}
    
    for i in range(1, max_formants + 1):
        freqs = []
        for t in times:
            f = formant.get_value_at_time(i, t)
            if np.isnan(f):
                freqs.append(None)
            else:
                freqs.append(round(f, 2))
        data[f'F{i}'] = freqs
    
    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract 5 formants from WAV file")
    parser.add_argument("input_wav", help="Path to input .wav file")
    parser.add_argument("--output", default="formants.csv", help="Output CSV path")
    parser.add_argument("--max_formants", type=int, default=5)
    parser.add_argument("--ceiling", type=float, default=5500.0)
    
    args = parser.parse_args()
    
    df = extract_formants(args.input_wav, max_formants=args.max_formants,
                          max_formant_freq=args.ceiling)
    df.to_csv(args.output, index=False)
    print(f"Formants saved to {args.output}")
    print(df.head())
