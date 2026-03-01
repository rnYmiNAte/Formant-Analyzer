import parselmouth
import pandas as pd
import numpy as np
from pathlib import Path
import argparse

SPEAKER_DEFAULTS = {
    "male": 5000.0,
    "female": 5500.0,
    "child": 6500.0,
    "unknown": 5500.0
}

SPEAKER_KEYWORDS = {
    "male": ["male", "man", "gent", "guy", "m_", "_m.", "_m_"],
    "female": ["female", "woman", "lady", "mom", "f_", "_f.", "_f_"],
    "child": ["child", "kid", "baby", "infant", "c_", "_c.", "_c_", "boy", "girl", "son", "daughter"]
}

def detect_speaker_type(filename: str) -> str:
    fname = filename.lower()
    for sp, keywords in SPEAKER_KEYWORDS.items():
        if any(k in fname for k in keywords):
            return sp
    return "unknown"

def extract_5_formants(wav_path: Path, time_step: float = 0.01, max_formant_hz: float = 5500.0):
    sound = parselmouth.Sound(str(wav_path))
    formant = sound.to_formant_burg(
        time_step=time_step,
        max_number_of_formants=5,
        maximum_formant=max_formant_hz,
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
    df = pd.DataFrame(data).round(2)
    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="5-Formant Analyzer with speaker-specific settings")
    parser.add_argument("--input-dir", default="audio", help="Folder with .wav files")
    parser.add_argument("--output-dir", default="results/formants", help="Output folder")
    parser.add_argument("--time-step", type=float, default=0.01)
    parser.add_argument("--max-formant", type=float, default=None, help="Global override (Hz)")
    parser.add_argument("--speaker-type", choices=["auto", "male", "female", "child"], default="auto",
                        help="Global speaker type (auto = filename detection)")
    args = parser.parse_args()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    wav_files = sorted(input_dir.glob("*.wav"))
    if not wav_files:
        print("No .wav files found!")
        exit(1)

    print(f"Analyzing {len(wav_files)} audio file(s) with speaker-aware 5-formant tracking...\n")
    summary = []

    for wav in wav_files:
        if args.max_formant is not None:
            max_f = args.max_formant
            sp_type = "manual_override"
        elif args.speaker_type != "auto":
            sp_type = args.speaker_type
            max_f = SPEAKER_DEFAULTS[sp_type]
        else:
            sp_type = detect_speaker_type(wav.name)
            max_f = SPEAKER_DEFAULTS.get(sp_type, 5500.0)

        print(f"→ {wav.name} | Speaker: {sp_type.capitalize():7} | Max formant: {max_f:4.0f} Hz")

        df = extract_5_formants(wav, time_step=args.time_step, max_formant_hz=max_f)
        csv_path = output_dir / f"{wav.stem}_5formants.csv"
        df.to_csv(csv_path, index=False)

        summary.append({
            "file": wav.name,
            "speaker": sp_type,
            "max_formant_hz": max_f,
            "frames": len(df),
            "duration_s": round(df["time_s"].iloc[-1], 2)
        })

    # Save summary for easy review
    pd.DataFrame(summary).to_csv(output_dir / "analysis_summary.csv", index=False)
    print(f"\n✅ All done! {len(wav_files)} files processed.")
    print(f"   Results → {output_dir}/")
    print(f"   Summary  → {output_dir}/analysis_summary.csv")
