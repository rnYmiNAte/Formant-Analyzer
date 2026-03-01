import parselmouth
import csv
from pathlib import Path
import sys

def extract_formants(wav_path, time_step=0.01, max_formants=5, max_formant_hz=5500):
    sound = parselmouth.Sound(str(wav_path))
    formant = sound.to_formant_burg(
        time_step=time_step,
        max_number_of_formants=max_formants,
        maximum_formant=max_formant_hz,
        window_length=0.025,
        pre_emphasis_from=50
    )

    duration = sound.get_total_duration()
    times = [t for t in range(int(duration / time_step) + 1)]
    times = [t * time_step for t in times]  # plain list instead of np.arange

    data = []
    headers = ["time"] + [f"F{f}" for f in range(1, max_formants + 1)] + [f"B{f}" for f in range(1, max_formants + 1)]

    for t in times:
        row = [t]
        for f in range(1, max_formants + 1):
            freq = formant.get_value_at_time(f, t, unit="Hertz")
            bw = formant.get_bandwidth_at_time(f, t, unit="Hertz")
            row.append(freq if freq is not None and freq == freq else None)  # None for NaN/undefined
            row.append(bw if bw is not None and bw == bw else None)
        data.append(row)

    return headers, data

if __name__ == "__main__":
    input_dir = Path("audio")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)

    for wav_file in input_dir.glob("*.wav"):
        print(f"Processing {wav_file.name}...")
        headers, rows = extract_formants(wav_file, max_formants=5)
        csv_path = output_dir / f"{wav_file.stem}_formants.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        print(f"Saved: {csv_path}")
