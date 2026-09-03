import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="TMQA 2: FakeMiami")


@app.cell
def _():
    import pickle

    import marimo as mo
    import numpy as np
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    from qiskit_ibm_runtime.fake_provider import FakeMiami

    from mqa_common.paths import REPO, RUNS
    from mqa_common.plotting import plot_one_minus_p
    from mqa_common.seeding import seed_all
    from mqa_common.topo_bot import dead_pairs, evaluate_bot, extract_mi, run_topo

    return (
        AerSimulator,
        FakeMiami,
        NoiseModel,
        REPO,
        RUNS,
        dead_pairs,
        evaluate_bot,
        extract_mi,
        mo,
        np,
        pickle,
        plot_one_minus_p,
        run_topo,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Topological MQA (TMQA) 2: `FakeMiami`

    Converted from `tmqa-fake.ipynb`.

    The second notebook of the Topological MQA series runs the same process on `FakeMiami`, a
    [`FakeBackendV2`](https://quantum.cloud.ibm.com/docs/en/api/qiskit-ibm-runtime/fake-provider-fake-miami)
    snapshot with 120 qubits in a 10 x 12 arrangement, so TMQA is demonstrated on a real square lattice.

    The committed result (`FakeMiami/miami_results_bot_0-90.pkl`) loads instantly; re-running the simulation
    (500 circuits on a 120-qubit stabilizer simulation) is behind a button.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    source_ui = mo.ui.radio({"Load saved results": "saved", "Run FakeMiami simulation": "run"}, value="Load saved results", label="Data source")
    shots_ui = mo.ui.number(value=1000, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.text(value="2, 6, 14, 24, 30", label="Circuit lengths (alternative: 26, 40, 54, 68, 82)", full_width=True)
    num_samples_ui = mo.ui.number(value=100, start=1, stop=10000, step=1, label="Samples per length")
    ffw_ui = mo.ui.number(value=1.3, start=0.1, stop=5.0, step=0.05, label="ffw (balances full/random modes)")
    acc_ui = mo.ui.slider(0.5, 1.0, step=0.05, value=0.9, label="Bot accuracy threshold acc", show_value=True)
    threshold_ui = mo.ui.slider(0.05, 1.0, step=0.05, value=0.5, label="Dead-edge CZ error threshold", show_value=True)
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    save_ui = mo.ui.checkbox(value=False, label="Save new results under runs/FakeMiami/")
    mo.vstack(
        [
            source_ui,
            mo.hstack([shots_ui, num_samples_ui, ffw_ui, seed_ui], justify="start", wrap=True),
            lengths_ui,
            mo.hstack([acc_ui, threshold_ui], justify="start", wrap=True),
            save_ui,
        ]
    )
    return (
        acc_ui,
        ffw_ui,
        lengths_ui,
        num_samples_ui,
        save_ui,
        seed_ui,
        shots_ui,
        source_ui,
        threshold_ui,
    )


@app.cell
def _(
    acc_ui,
    lengths_ui,
    num_samples_ui,
    seed_all,
    seed_ui,
    shots_ui,
    source_ui,
):
    SEED = seed_all(int(seed_ui.value))
    source = source_ui.value
    shots = int(shots_ui.value)
    lengths = sorted({int(x) for x in lengths_ui.value.replace(";", ",").split(",") if x.strip()})
    num_samples = int(num_samples_ui.value)
    acc = float(acc_ui.value)
    return SEED, acc, lengths, num_samples, shots, source


@app.cell
def _(AerSimulator, FakeMiami, NoiseModel, SEED, mo):
    miami_hw = FakeMiami()
    leqit = miami_hw.num_qubits
    faqe = leqit + 2
    # readout/thermal errors off to match the custom depolarizing model used in tmqa_simul.
    clifford_noise = NoiseModel.from_backend(miami_hw, thermal_relaxation=False, readout_error=False)
    miami_sim = AerSimulator.from_backend(miami_hw, noise_model=clifford_noise)
    miami_sim.set_options(method="stabilizer", seed_simulator=SEED, max_parallel_experiments=0)
    mo.md(
        f"**FakeMiami**: {miami_hw.configuration().n_qubits} qubits, basis `{miami_hw.configuration().basis_gates}`; "
        f"simulated with `AerSimulator(method='stabilizer')` and Clifford-only noise."
    )
    return faqe, leqit, miami_hw, miami_sim


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Backend health

    Edges with very high calibrated CZ error would make a snapshot look like a bot failure. Listing them first
    means such cases are not counted as wrong results.
    """)
    return


@app.cell
def _(dead_pairs, miami_hw, mo, threshold_ui):
    _stats, _dead = dead_pairs(miami_hw, threshold=float(threshold_ui.value))
    _rows = [{"edge": f"{e}", "cz error": f"{err:.3f}"} for e, err in _dead]
    mo.vstack(
        [
            mo.md(f"CZ error: median={_stats['median']:.3f}, mean={_stats['mean']:.3f}, max={_stats['max']:.3f}. "
                  f"**{len(_dead)}** dead edges (error ≥ {threshold_ui.value}); qubits on them: `{sorted({q for e, _ in _dead for q in e})}`"),
            mo.ui.table(_rows, selection=None, page_size=10) if _rows else mo.md("*No dead edges.*"),
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Results
    """)
    return


@app.cell(hide_code=True)
def _(REPO, mo, source):
    saved_files = sorted((REPO / "FakeMiami").glob("*.pkl"))
    saved_ui = mo.ui.dropdown({p.name: p for p in saved_files}, value=saved_files[0].name if saved_files else None, label="Saved result")
    run_btn = mo.ui.run_button(label="Run FakeMiami simulation", kind="danger")
    if source == "saved":
        _out = saved_ui if saved_files else mo.callout(mo.md("No saved results under `FakeMiami/`. Switch to the run mode."), kind="warn")
    else:
        _out = mo.vstack([mo.callout(mo.md("**Cost:** all lengths × samples circuits on a 120-qubit stabilizer simulation, then one max-weight matching per circuit. Many minutes."), kind="warn"), run_btn])
    _out
    return run_btn, saved_files, saved_ui


@app.cell
def _(
    RUNS,
    SEED,
    acc,
    evaluate_bot,
    extract_mi,
    faqe,
    ffw_ui,
    lengths,
    leqit,
    miami_sim,
    mo,
    np,
    num_samples,
    pickle,
    run_btn,
    run_topo,
    save_ui,
    saved_files,
    saved_ui,
    shots,
    source,
):
    if source == "saved":
        mo.stop(not saved_files, mo.md("*Nothing to load.*"))
        results = pickle.loads(saved_ui.value.read_bytes())
        _note = mo.md(f"Loaded `{saved_ui.value.name}`. Bot accuracy threshold of the saved run is encoded in its filename.")
    else:
        mo.stop(not run_btn.value, mo.md("*Click **Run FakeMiami simulation** to execute.*"))
        with mo.status.spinner(title="Running MirrorQATopo on FakeMiami…"):
            exp, rb_data = run_topo(
                miami_sim, leqit, lengths, num_samples, shots, SEED,
                ffw=float(ffw_ui.value), initial_entangling_angle=np.pi / 2, optimization_level=0,
            )
            mi = extract_mi(exp, rb_data, leqit)
            results = {"miami": evaluate_bot(mi, exp, leqit, faqe, lengths, acc=acc)}
        _note = mo.md(f"Ran {len(exp._pairs)} circuits.")
        if save_ui.value:
            _path = RUNS / "FakeMiami" / f"miami_results_bot_{acc:.2f}.pkl".replace("0.", "0-", 1)
            _path.parent.mkdir(parents=True, exist_ok=True)
            _path.write_bytes(pickle.dumps(results))
            _note = mo.md(f"Ran {len(exp._pairs)} circuits. Saved `{_path}`.")
    _note
    return (results,)


@app.cell
def _(mo, results):
    _r = results["miami"]
    mo.ui.table(
        [{"length": L, "P(pairs)": f"{p:.3f}", "P(topo)": f"{t:.3f}"} for L, p, t in zip(_r["lengths"], _r["p_bot_pairs"], _r["p_mode_topo"])],
        selection=None,
        label="Bot success per length",
    )
    return


@app.cell
def _(mo, plot_one_minus_p, results):
    _r = results["miami"]
    _pairs = plot_one_minus_p({"FakeMiami": (_r["lengths"], _r["p_bot_pairs"])}, r"1-$P(\mathrm{pairs})$", legend_loc="center right")
    _topo = plot_one_minus_p({"FakeMiami": (_r["lengths"], _r["p_mode_topo"])}, r"1-$P(\mathrm{topo})$", legend_loc="center right")
    mo.hstack([_pairs, _topo], widths="equal", wrap=True)
    return


if __name__ == "__main__":
    app.run()
