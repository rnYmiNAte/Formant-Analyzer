import matplotlib.pyplot as plt

def plot_formants(f1, f2, output_path='formant_plot.png'):
    fig, ax = plt.subplots()
    # Draw trapezoid-like shape (simplified)
    ax.plot([0, 100], [100, 0], 'k-')  # Diagonal
    ax.plot([100, 100], [0, 100], 'k-')  # Vertical
    ax.plot([0, 100], [100, 100], 'k-')  # Top horizontal
    ax.plot([0, 0], [100, 0], 'k-')  # Left vertical (adjusted for trapezoid)

    # Labels
    ax.text(102, 50, 'F1', rotation=0)
    ax.text(50, 102, 'F2', rotation=0)
    ax.text(102, -5, '100%', rotation=0)
    ax.text(-10, 102, '100%', rotation=0)

    # Plot point if provided
    if f1 is not None and f2 is not None:
        ax.scatter(f1, f2, color='r', label='Extracted Formant')

    ax.set_xlim(0, 110)
    ax.set_ylim(0, 110)
    ax.axis('off')
    plt.savefig(output_path)
    plt.close()
