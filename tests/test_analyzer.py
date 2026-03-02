from src.analyzer import extract_formants

def test_extract_formants():
    # Use a sample WAV from data/
    formants = extract_formants('data/sample_vowel_a.wav')
    assert formants is not None
    assert 0 <= formants[0] <= 100  # F1 in range
