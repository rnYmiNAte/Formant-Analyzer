# tests/test_plotter.py
import pytest
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt

from src.plotter import plot_formants

# Where to save test plots (will be cleaned up or ignored via .gitignore)
TEST_OUTPUT_DIR = Path("tests/output")
TEST_OUTPUT_DIR.mkdir(exist_ok=True)


@pytest.fixture(autouse=True)
def cleanup_plots():
    """Remove generated test plots after each test (optional)."""
    yield
    for f in TEST_OUTPUT_DIR.glob("*.png"):
        f.unlink(missing_ok=True)


def test_plot_formants_basic():
    """Smoke test: can we generate a plot without crashing?"""
    output_path = TEST_OUTPUT_DIR / "basic_formant_plot.png"

    plot_formants(
        f1=45.0,
        f2=70.0,
        output_path=str(output_path),
        title="Test Vowel /ɛ/"
    )

    assert output_path.exists(), "Plot file was not created"
    assert output_path.stat().st_size > 10000, "Plot file seems empty"


def test_plot_formants_no_point():
    """Should still generate plot even without a formant point"""
    output_path = TEST_OUTPUT_DIR / "empty_formant_plot.png"

    plot_formants(
        f1=None,
        f2=None,
        output_path=str(output_path)
    )

    assert output_path.exists()


@pytest.mark.parametrize("f1,f2", [
    (0.0, 0.0),
    (100.0, 100.0),
    (50.5, 49.5),
    (-10.0, 110.0),   # should be clipped or ignored gracefully
])
def test_plot_formants_range(f1, f2):
    output_path = TEST_OUTPUT_DIR / f"range_{f1}_{f2}.png"

    plot_formants(f1, f2, str(output_path))

    assert output_path.exists()


def test_plot_formants_custom_title():
    """Check if custom title is respected (requires slight plotter modification)"""
    # If you added a title parameter to plot_formants, test it here
    # For now we assume basic version without title
    pass
