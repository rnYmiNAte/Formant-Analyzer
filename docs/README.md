# Formant Analyzer

Extract and visualize vowel formants (F1 and F2) from WAV audio files, with normalized 0–100% outputs and trapezoid-style vowel space plots inspired by classic phonetic charts.

This tool processes short speech clips (e.g., sustained vowels) using Linear Predictive Coding (LPC) to estimate the first two formants, normalizes them to a percentage scale (0–100%), and generates simple visual diagrams resembling vowel quadrilaterals/trapezoids.

![Example Formant Plot](data/results/sample_vowel_i_plot.png)
*(Example output: /i/ vowel – low F1%, high F2% → upper-left in the space)*

## Features

- Load and preprocess WAV files (mono, resample to 16 kHz if needed)
- Pre-emphasis, framing, Hamming window, LPC-based formant estimation
- Normalization of F1 and F2 to 0–100% (based on approximate human ranges: F1 ~200–1000 Hz, F2 ~800–3000 Hz)
- Simple trapezoid plot with F1 horizontal (low→high left-to-right), F2 vertical (low→high bottom-to-top)
- CLI entry point: `formant-analyzer <file.wav>`
- GitHub Actions workflow: Auto-analyze new/updated WAV files in `data/`, upload plots as artifacts
- Modular structure with tests

## Vowel Space Diagram Explanation



The plot mimics a simplified vowel quadrilateral:

100% F2
       ^
       |
- **F1 = 0–100%**: Low F1 (close/high vowels like /i/) → left side; High F1 (open/low vowels like /a/) → right side
- **F2 = 0–100%**: Low F2 (back vowels) → bottom; High F2 (front vowels) → top

Typical expected positions (approximate, varies by speaker/sex):
- /i/ (as in "see"): F1 ~10–20%, F2 ~80–100% → upper-left
- /a/ or /ɑ/ (as in "father"): F1 ~70–90%, F2 ~20–40% → lower-right

Normalization formula (in code):
```
f1_norm = (f1_hz - 200) / (1000 - 200) * 100   # clipped to 0–100
f2_norm = (f2_hz - 800) / (3000 - 800) * 100   # clipped to 0–100
```
# Clone the repo
```
git clone https://github.com/rnyminate/formant-analyzer.git
cd formant-analyzer
```
# Install dependencies (editable mode recommended for development)
```
pip install -e .
```
# Or just install requirements
pip install -r requirements.txt

```
# Analyze a single file
```
python3 main.py data/sample_vowel_a.wav
```
# Example output:
```
# F1 = 78.45%
# F2 = 32.10%
# → Plot saved as formant_plot.png (or in data/results/)
