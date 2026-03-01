import parselmouth
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

def extract_5_formants(wav_path: Path, time_step: float = 0.01, max_formant_hz: float = 5500.0):
    sound = parselmouth.Sound(str(wav_path))
    
    formant = sound.to_formant_burg(
        time_step=time_step,
        max_number_of_formants=5,
        maximum_formant=max_formant_hz,      # 5000 Hz male / 5500 Hz female/child – adjust per speaker
        window_length=0.025,
        pre_emphasis_from=50.0
    )
    
    times = np.arange(0, sound.duration, time_step)
    data = {"time_s": times}
    
    for i in range(1, 6):
        values = [
            formant.get_value_at_time(i, t, unit=parselmouth.FormantUnit.HERTZ, interpolation="Linear")
            for t in times
        ]
        data[f"F{i}"] = values
    
    df = pd.DataFrame(data)
    df = df.round(2)  # clean output
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5-Formant Analyzer")
    parser.add_argument("--input-dir", default="audio", help="Folder with .wav files")
    parser.add_argument("--output-dir", default="results/formants", help="Output folder")
    parser.add_argument("--time-step", type=float, default=0.01, help="Time step in seconds")
    parser.add_argument("--max-formant", type=float, default=5500.0, help="Max formant frequency (Hz)")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wav_files = list(input_dir.glob("*.wav"))
    if not wav_files:
        print("No .wav files found!")
        exit(1)

    print(f"Analyzing {len(wav_files)} audio file(s) for 5 formants...\n")
    for wav in wav_files:
        print(f"→ {wav.name} ({wav.stat().st_size / 1024:.1f} KB)")
        df = extract_5_formants(wav, time_step=args.time_step, max_formant_hz=args.max_formant)
        csv_path = output_dir / f"{wav.stem}_5formants.csv"
        df.to_csv(csv_path, index=False)
        print(f"   Saved → {csv_path} ({len(df)} rows)\n")

    print("✅ All formant analysis complete!")
