import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MQA: peak shift vs. error rate")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd

    from mqa_common.paths import REPO

    return REPO, mo, np, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Isolated-qubit mutual information vs. two-qubit error rate (stabilizer backend)

    Converted from `StabilizerBackend/mqa-stabilizer-p-curves/error_rates_graph.ipynb`.

    Overlays the `singles` (isolated qubit) mean mutual information for stabilizer simulations of `ibm_fez` at
    p2 = 0.1, 0.05, 0.01 and 0.001. The peak shifts to longer circuits as the error rate drops.

    The original read the CSVs from its own directory, but they live in per-rate subfolders (`0.1/`, `0.05/`, ...);
    the paths are fixed here.
    """)
    return


@app.cell
def _(REPO):
    DATA = REPO / "StabilizerBackend" / "mqa-stabilizer-p-curves"
    RATES = ["0.1", "0.05", "0.01", "0.001"]
    return DATA, RATES


@app.cell(hide_code=True)
def _(RATES, mo):
    rates_ui = mo.ui.multiselect(RATES, value=RATES, label="p2 values")
    logy_ui = mo.ui.checkbox(value=True, label="Log y-axis")
    xtick_ui = mo.ui.slider(1, 20, value=5, label="x-tick spacing", show_value=True)
    dpi_ui = mo.ui.dropdown(["150", "300", "900"], value="900", label="Save dpi")
    save_ui = mo.ui.checkbox(value=False, label="Save peak_shift_comparison.png next to the data")
    mo.vstack([rates_ui, mo.hstack([logy_ui, xtick_ui, dpi_ui], justify="start", wrap=True), save_ui])
    return dpi_ui, logy_ui, rates_ui, save_ui, xtick_ui


@app.cell
def _(DATA, RATES, mo, pd, rates_ui):
    rates = [p for p in RATES if p in rates_ui.value]
    dfs = {p: pd.read_csv(DATA / p / f"singles_data_stab_fez_whole_pi_over_2_p_{p}.csv") for p in rates}
    mo.accordion({f"p2 = {p}": mo.ui.table(df, selection=None) for p, df in dfs.items()})
    return dfs, rates


@app.cell
def _(DATA, dfs, dpi_ui, logy_ui, mo, np, plt, rates, save_ui, xtick_ui):
    mo.stop(not rates, mo.md("*Select at least one error rate.*"))
    fig, ax = plt.subplots(figsize=(8, 5))
    for p in rates:
        df = dfs[p]
        ax.errorbar(df["lengths"], df["mmi_singles"], yerr=df["mmi_singles_err"], label=rf"$p_2 = {p}$")
    if logy_ui.value:
        ax.set_yscale("log")
    ax.legend(loc="lower right")
    ax.set_xlabel("Circuit Length")
    ax.set_ylabel("Mean Mutual Information")
    _step = int(xtick_ui.value)
    ax.set_xticks(_step * np.arange(0, 100 // _step + 1))
    fig.tight_layout()
    if save_ui.value:
        fig.savefig(DATA / "peak_shift_comparison.png", dpi=int(dpi_ui.value))
    fig
    return


if __name__ == "__main__":
    app.run()
