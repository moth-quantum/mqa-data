"""Mean mutual-information curves (paired / spectator / isolated)."""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

LABELS = {"paired": "paired", "unpaired": "spectator", "singles": "isolated"}


def mean_mi_curves(mmi: dict, lengths: list, pairtypes=("paired", "unpaired", "singles")) -> dict:
    """Bin QuantumAwesomeness.mean_mutual_info output per length.

    Returns {pairtype: (means, stds)} with one entry per length; empty bins are NaN.
    """
    n = len(lengths)
    curves = {}
    for pairtype in pairtypes:
        bins = [[] for _ in range(n)]
        for j, m in enumerate(mmi[pairtype]):
            arr = np.asarray(m, dtype=float)
            if np.all(np.isnan(arr)):
                continue
            bins[j % n].append(np.nanmean(arr))
        means = [np.mean(b) if b else np.nan for b in bins]
        stds = [np.std(b) if b else 0.0 for b in bins]
        curves[pairtype] = (means, stds)
    return curves


def plot_mean_mutual_info(curves: dict, lengths: list, title: str = "", labels: dict = LABELS) -> Figure:
    fig, ax = plt.subplots()
    for pairtype, (ys, yerrs) in curves.items():
        ax.errorbar(lengths, ys, yerr=yerrs, label=labels.get(pairtype, pairtype))
    ax.set_yscale("log")
    ax.legend()
    ax.set_xlabel("Circuit Length")
    ax.set_ylabel("Mean Mutual Information")
    ax.set_title(title)
    return fig


def mmi_record(lengths: list, curves: dict, labels: dict = LABELS) -> dict:
    """JSON-friendly dict matching the *_mutual_info_data.json layout."""
    rec = {"lengths": list(lengths)}
    for pairtype, (ys, yerrs) in curves.items():
        name = labels.get(pairtype, pairtype)
        rec[name] = [None if np.isnan(y) else float(y) for y in ys]
        rec[f"{name}_err"] = [float(e) for e in yerrs]
    return rec
