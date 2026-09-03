import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MQA: entangling-angle comparison")


@app.cell
def _():
    import marimo as mo
    import matplotlib.pyplot as plt
    import pandas as pd

    from mqa_common.paths import REPO

    return REPO, mo, pd, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mean mutual information vs. entangling angle (custom noisy backend)

    Converted from `CustomNoisyBackend/mqa-custom-noisy-backend/noisy-backend-angle-graph.ipynb`.

    Four MQA runs on the custom noisy backend, one per entangling-angle configuration, plotted as a 2 x 2 grid
    of paired / spectator / isolated mean mutual information against circuit length.
    """)
    return


@app.cell
def _(REPO):
    DATA = REPO / "CustomNoisyBackend" / "mqa-custom-noisy-backend"
    PANELS = {
        "mmi_data_null_angle.csv": "(a) θ = 0",
        "mmi_data_pi_over_4.csv": "(b) θ = π/4",
        "mmi_data_pi_over_2.csv": "(c) θ = π/2",
        "mmi_data_pi_over_2_density_1.csv": "(d) θ = π/2, ρ = 1",
    }
    return DATA, PANELS


@app.cell(hide_code=True)
def _(PANELS, mo):
    panels_ui = mo.ui.multiselect(list(PANELS), value=list(PANELS), label="Data files (panel order)")
    series_ui = mo.ui.multiselect(["paired", "spectator", "isolated"], value=["paired", "spectator", "isolated"], label="Series")
    logy_ui = mo.ui.checkbox(value=True, label="Log y-axis")
    original_titles_ui = mo.ui.checkbox(value=True, label="Original panel titles (a)-(d)")
    save_ui = mo.ui.checkbox(value=False, label="Save noisy_backend_angle_subplots.png next to the data (300 dpi)")
    mo.vstack([panels_ui, mo.hstack([series_ui, logy_ui, original_titles_ui], justify="start", wrap=True), save_ui])
    return logy_ui, original_titles_ui, panels_ui, save_ui, series_ui


@app.cell
def _(DATA, PANELS, mo, panels_ui, pd):
    files = [f for f in PANELS if f in panels_ui.value]
    dfs = {f: pd.read_csv(DATA / f) for f in files}
    mo.accordion({f"{f}": mo.ui.table(df, selection=None) for f, df in dfs.items()})
    return dfs, files


@app.cell
def _(
    DATA,
    PANELS,
    dfs,
    files,
    logy_ui,
    mo,
    original_titles_ui,
    plt,
    save_ui,
    series_ui,
):
    mo.stop(not files, mo.md("*Select at least one data file.*"))
    _cols = {"paired": ("mmi_paired", "mmi_paired_err"), "spectator": ("mmi_unpaired", "mmi_unpaired_err"), "isolated": ("mmi_singles", "mmi_singles_err")}
    _n = len(files)
    _rows, _ncols = (2, 2) if _n > 2 else (1, _n)
    fig, axs = plt.subplots(_rows, _ncols, figsize=(6 * _ncols, 5 * _rows), squeeze=False)
    for ax in axs.flat[_n:]:
        ax.axis("off")
    for ax, f in zip(axs.flat, files):
        df = dfs[f]
        for name in series_ui.value:
            y, yerr = _cols[name]
            ax.errorbar(df["lengths"], df[y], yerr=df[yerr], label=name)
        if logy_ui.value:
            ax.set_yscale("log")
        ax.legend(fontsize=16)
        ax.set_xlabel("Circuit Length", fontsize=16)
        ax.set_ylabel("Mean Mutual Information", fontsize=16)
        ax.set_title(PANELS[f].split(" ")[0] if original_titles_ui.value else PANELS[f], fontsize=22)
        ax.tick_params(axis="both", which="major", labelsize=16)
    fig.tight_layout()
    if save_ui.value:
        fig.savefig(DATA / "noisy_backend_angle_subplots.png", dpi=300, bbox_inches="tight")
    fig
    return


if __name__ == "__main__":
    app.run()
