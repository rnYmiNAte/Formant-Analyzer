import parselmouth
import pandas as pd
import numpy as np
from pathlib import Path
import sys

def extract_formants(wav_path, time_step=0.01, max_formants=5, max_formant_hz=5500):
    sound = parselmouth.Sound(str(wav_path))
    # Standard settings: time step, max # formants, max freq, window length, pre-emphasis
    formant = sound.to_formant_burg(
        time_step=time_step,
        max_number_of_formants=max_formants,
        maximum_formant=max_formant_hz,   # 5000–5500 Hz common; adjust per speaker sex/age
        window_length=0.025,
        pre_emphasis_from=50
    )

    duration = sound.get_total_duration()
    times = np.arange(0, duration, time_step)

    data = []
    for t in times:
        row = {"time": t}
        for f in range(1, max_formants + 1):
            freq = formant.get_value_at_time(f, t, unit="Hertz")
            bandwidth = formant.get_bandwidth_at_time(f, t, unit="Hertz")
            row[f"F{f}"] = freq if np.isfinite(freq) else np.nan
            row[f"B{f}"] = bandwidth if np.isfinite(bandwidth) else np.nan
        data.append(row)

    df = pd.DataFrame(data)
    return df

if __name__ == "__main__":
    input_dir = Path("audio")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    for wav_file in input_dir.glob("*.wav"):
        print(f"Processing {wav_file.name}...")
        df = extract_formants(wav_file, max_formants=5)
        csv_path = output_dir / f"{wav_file.stem}_formants.csv"
        df.to_csv(csv_path, index=False)
        print(f"Saved: {csv_path}")
