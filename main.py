import sys
from src.analyzer import extract_formants
from src.plotter import plot_formants

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python main.py <wav_file>")
        sys.exit(1)
    wav_path = sys.argv[1]
    formants = extract_formants(wav_path)
    if formants:
        f1, f2 = formants
        print(f"F1 = {f1:.2f}%")
        print(f"F2 = {f2:.2f}%")
        plot_formants(f1, f2)
    else:
        print("No formants extracted.")
