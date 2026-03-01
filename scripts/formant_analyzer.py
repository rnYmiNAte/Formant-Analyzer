#!/usr/bin/env python3
"""
Robust 5-formant analyzer using parselmouth
- Skips broken files instead of crashing
- Logs problems clearly
- Creates summary even if some files fail
"""

import parselmouth
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import sys
import warnings
from datetime import datetime

# Suppress parselmouth / Praat warnings that are usually harmless
warnings.filterwarnings("ignore", category=UserWarning, module="parselmouth")

# Reasonable defaults per speaker group
SPEAKER_DEFAULTS = {
    "male": 5000.0,
    "female": 5500.0,
    "child": 6500.0,
    "auto": 5500.0   # fallback when detection fails
}

SPEAKER_KEYWORDS = {
    "male":   ["male", "man", "gent", "guy", "m_", "_m.", "_m ", "father", "dad", "mr"],
    "female": ["female", "woman", "lady", "mom", "mum", "f_", "_f.", "_f ", "mother", "ms", "miss"],
    "child":  ["child", "kid", "baby", "infant", "c_", "_c.", "_c ", "boy", "girl", "son", "daughter", "child"]
}

def detect_speaker_type(filename: str) -> str:
    fname = filename.lower()
    for group, words in SPEAKER_KEYWORDS.items():
        if any(w in fname for w in words):
            return group
    return "auto"


def extract_formants(
    sound: parselmouth.Sound,
    time_step: float = 0.01,
    max_formant: float = 5500.0
) -> pd.DataFrame | None:
    try:
        formant_obj = sound.to_formant_burg(
            time_step=time_step,
            max_number_of_formants=5,
            maximum_formant=max_formant,
            window_length=0.025,
            pre_emphasis_from=50.0
        )

        duration = sound.duration
        if duration < 0.03:  # too short → skip
            return None

        times = np.arange(0, duration + time_step/2, time_step)
        times = times[times <= duration]  # don't go beyond end

        data = {"time_s": np.round(times, 4)}

        for f in range(1, 6):
            values = []
            for t in times:
                try:
                    val = formant_obj.get_value_at_time(
                        formant_number=f,
                        time=t,
                        unit=parselmouth.FormantUnit.HERTZ,
                        interpolation="Linear"
                    )
                    values.append(round(val, 2) if np.isfinite(val) else np.nan)
                except:
                    values.append(np.nan)
            data[f"F{f}"] = values

        df = pd.DataFrame(data)
        # Remove rows that are completely NaN (very rare)
        df = df.dropna(how="all", subset=[f"F{i}" for i in range(1,6)])
        return df

    except Exception as e:
        print(f"    Formant extraction failed: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Robust 5-formant extractor (skips bad files)")
    parser.add_argument("--input-dir",   default="audio",      type=str,   help="folder with .wav files")
    parser.add_argument("--output-dir",  default="results/formants", type=str)
    parser.add_argument("--time-step",   default=0.010,        type=float, help="analysis interval (s)")
    parser.add_argument("--max-formant", default=None,         type=float, help="override ALL files (Hz)")
    parser.add_argument("--speaker",     default="auto",
                        choices=["auto", "male", "female", "child"],
                        help="global speaker type (when --max-formant not set)")
    parser.add_argument("--mono", action="store_true", help="force mono (downmix stereo)")
    args = parser.parse_args()

    input_path  = Path(args.input_dir).expanduser().resolve()
    output_path = Path(args.output_dir).expanduser().resolve()
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Formant analyzer started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Input:  {input_path}")
    print(f"  Output: {output_path}\n")

    wav_files = sorted(input_path.glob("*.wav")) + sorted(input_path.glob("*.WAV"))
    if not wav_files:
        print("No .wav files found in input directory.")
        return 1

    summary_rows = []

    for wav in wav_files:
        print(f"Processing {wav.name} ... ", end="", flush=True)

        try:
            snd = parselmouth.Sound(str(wav))

            # Optional: force mono
            if args.mono and snd.n_channels > 1:
                snd = snd.convert_to_mono()

            # Decide max_formant
            if args.max_formant is not None:
                max_f = args.max_formant
                speaker_label = "override"
            elif args.speaker != "auto":
                max_f = SPEAKER_DEFAULTS[args.speaker]
                speaker_label = args.speaker
            else:
                speaker_label = detect_speaker_type(wav.name)
                max_f = SPEAKER_DEFAULTS[speaker_label]

            print(f"({speaker_label}, {max_f} Hz) ", end="", flush=True)

            df = extract_formants(snd, args.time_step, max_f)

            if df is None or df.empty:
                print("→ SKIPPED (too short / failed)")
                summary_rows.append({
                    "file": wav.name,
                    "status": "failed",
                    "speaker": speaker_label,
                    "max_formant_hz": max_f,
                    "duration_s": round(snd.duration, 3) if 'snd' in locals() else None,
                    "n_frames": None
                })
                continue

            out_csv = output_path / f"{wav.stem}_formants.csv"
            df.to_csv(out_csv, index=False)

            print(f"→ OK  ({len(df)} points)")

            summary_rows.append({
                "file": wav.name,
                "status": "ok",
                "speaker": speaker_label,
                "max_formant_hz": max_f,
                "duration_s": round(snd.duration, 3),
                "n_frames": len(df)
            })

        except Exception as e:
            print(f"→ ERROR: {str(e)}")
            summary_rows.append({
                "file": wav.name,
                "status": "error",
                "speaker": "—",
                "max_formant_hz": None,
                "duration_s": None,
                "n_frames": None,
                "error": str(e)
            })

    # Save summary
    if summary_rows:
        summary_df = pd.DataFrame(summary_rows)
        summary_df.to_csv(output_path / "analysis_summary.csv", index=False)
        print(f"\nSummary saved → {output_path}/analysis_summary.csv")
        print(f"Success: {sum(r['status']=='ok' for r in summary_rows)} / {len(summary_rows)} files")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
