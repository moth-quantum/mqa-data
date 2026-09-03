import matplotlib.pyplot as plt
from matplotlib.figure import Figure


def plot_one_minus_p(series: dict, ylabel: str, legend_loc: str = "center left") -> Figure:
    """series: {label: (lengths, probabilities)}; plots 1 - p against length."""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for label, (lengths, probs) in series.items():
        ax.plot(lengths, [1 - p for p in probs], marker="o", linestyle="-", label=label)
    ax.set_xlabel("Circuit Depth (length)")
    ax.set_ylabel(ylabel)
    ax.grid(True, alpha=0.3)
    ax.legend(loc=legend_loc, frameon=True)
    fig.tight_layout()
    return fig
