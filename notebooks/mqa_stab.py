import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    app_title="MQA: stabilizer simulation (ibm_fez)",
)


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from mqa_common.analysis import effective_polarization
    from mqa_common.backends import (
        STAB_BASIS_RZ,
        build_stabilizer_backend,
        legacy_rz_operator,
        standard_name_mapping,
    )
    from mqa_common.io import save_figure, save_job_bundle, save_json
    from mqa_common.mi_plot import mean_mi_curves, mmi_record, plot_mean_mutual_info
    from mqa_common.paths import RUNS
    from mqa_common.seeding import seed_all
    from mqa_common.topologies import fez_coupling_map
    from qiskit_device_benchmarking.bench_code.mrb import MirrorQA, QuantumAwesomeness

    return (
        MirrorQA,
        QuantumAwesomeness,
        RUNS,
        STAB_BASIS_RZ,
        build_stabilizer_backend,
        effective_polarization,
        fez_coupling_map,
        legacy_rz_operator,
        mean_mi_curves,
        mmi_record,
        mo,
        np,
        plot_mean_mutual_info,
        save_figure,
        save_job_bundle,
        save_json,
        seed_all,
        standard_name_mapping,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mirror Quantum Awesomeness (MQA): Stabilizer Simulation

    Converted from `mqa-stab.ipynb`.

    Simulates MQA on the full 156-qubit `ibm_fez` heavy-hex topology with Aer's stabilizer method and a
    depolarizing noise model (p1 = p2 / 10). The error-rate dropdown covers the sweep stored under
    `StabilizerBackend/mqa-stabilizer-p-curves/`.

    Notes on the conversion: the `rz` entry of the Target's custom name mapping is kept exactly as the
    original wrote it (an RX-shaped matrix, see `mqa_common.backends.legacy_rz_operator`); the original also
    appended reversed edges to an already bidirectional list, which changes nothing in the Target (352 CX
    pairs either way), so the list is used once. Saving is off by default and writes under `runs/<job_id>/`.
    """)
    return


@app.cell(hide_code=True)
def _(mo, np):
    ANGLES = {"0": 0.0, "π/4": np.pi / 4, "π/2": np.pi / 2}
    p2_ui = mo.ui.dropdown({"0.001": 1e-3, "0.01": 1e-2, "0.05": 5e-2, "0.1": 1e-1}, value="0.01", label="p2 (2Q depolarizing); p1 = p2 / 10")
    shots_ui = mo.ui.number(value=10000, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50, 100], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 50, value=20, label="Samples per length")
    angle_ui = mo.ui.dropdown(ANGLES, value="π/2", label="Initial entangling angle θ")
    density_ui = mo.ui.number(value=0.25, start=0.0, stop=1.0, step=0.05, label="2Q gate density ρ")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    save_ui = mo.ui.checkbox(value=False, label="Save circuits, data and figures under runs/<job_id>/")
    mo.vstack(
        [
            mo.hstack([p2_ui, shots_ui, num_samples_ui, seed_ui], justify="start", wrap=True),
            mo.hstack([angle_ui, density_ui], justify="start", wrap=True),
            lengths_ui,
            save_ui,
        ]
    )
    return (
        angle_ui,
        density_ui,
        lengths_ui,
        num_samples_ui,
        p2_ui,
        save_ui,
        seed_ui,
        shots_ui,
    )


@app.cell
def _(
    angle_ui,
    density_ui,
    lengths_ui,
    np,
    num_samples_ui,
    p2_ui,
    seed_all,
    seed_ui,
    shots_ui,
):
    SEED = seed_all(int(seed_ui.value))
    p2 = float(p2_ui.value)
    p1 = p2 / 10
    rz_angle = np.pi / 2
    shots = int(shots_ui.value)
    lengths = sorted(int(x) for x in lengths_ui.value)
    num_samples = int(num_samples_ui.value)
    angle = float(angle_ui.value)
    density = float(density_ui.value)
    return SEED, angle, density, lengths, num_samples, p1, p2, rz_angle, shots


@app.cell
def _(
    SEED,
    STAB_BASIS_RZ,
    build_stabilizer_backend,
    fez_coupling_map,
    legacy_rz_operator,
    mo,
    p1,
    p2,
    rz_angle,
    standard_name_mapping,
):
    coupling_map = fez_coupling_map()
    num_qubits = coupling_map.size()
    with mo.status.spinner(title="Building 156-qubit stabilizer target…"):
        backend = build_stabilizer_backend(
            num_qubits,
            coupling_map,
            STAB_BASIS_RZ,
            p1,
            p2,
            SEED,
            custom_name_mapping=standard_name_mapping(STAB_BASIS_RZ, legacy_rz_operator(rz_angle)),
        )
    mo.md(f"Backend: `AerSimulator(method='stabilizer')`, **{num_qubits}** qubits, {len(coupling_map.get_edges())} directed edges, p1={p1:g}, p2={p2:g}.")
    return backend, num_qubits


@app.cell
def _(
    MirrorQA,
    SEED,
    angle,
    backend,
    density,
    lengths,
    num_qubits,
    num_samples,
    shots,
):
    exp = MirrorQA(
        range(num_qubits),
        lengths=lengths,
        backend=backend,
        two_qubit_gate_density=density,
        num_samples=num_samples,
        initial_entangling_angle=angle,
        seed=SEED,
    )
    exp.set_run_options(shots=shots)
    return (exp,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Run experiment
    """)
    return


@app.cell(hide_code=True)
def _(lengths, mo, num_qubits, num_samples, shots):
    run_btn = mo.ui.run_button(label="Run experiment", kind="danger")
    mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"**Cost:** {len(lengths) * num_samples} circuits × {shots} shots on a {num_qubits}-qubit stabilizer "
                    f"simulation. Tens of minutes to hours at the defaults. Results are cleared when a parameter changes."
                ),
                kind="warn",
            ),
            run_btn,
        ]
    )
    return (run_btn,)


@app.cell
def _(exp, mo, run_btn):
    mo.stop(not run_btn.value, mo.md("*Click **Run experiment** to execute.*"))
    with mo.status.spinner(title="Running MQA circuits…"):
        rb_data = exp.run()
        rb_data.block_for_results()
    job_id = rb_data.job_ids[0]
    mo.md(f"Job IDs: `{rb_data.job_ids}`")
    return job_id, rb_data


@app.cell
def _(RUNS, SEED, exp, job_id, mo, num_qubits, save_job_bundle, save_ui):
    out_dir = RUNS / job_id
    if save_ui.value:
        with mo.status.spinner(title="Saving circuits…"):
            save_job_bundle(RUNS, job_id, exp, num_qubits=num_qubits, seed=SEED, pairs=True)
        _msg = mo.md(f"Saved qubits, pairs, seed and circuits to `{out_dir}`.")
    else:
        _msg = mo.md("*Saving disabled.*")
    _msg
    return (out_dir,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MQA analysis using MRB
    """)
    return


@app.cell
def _(
    effective_polarization,
    exp,
    job_id,
    out_dir,
    rb_data,
    save_figure,
    save_ui,
):
    analysis = effective_polarization(rb_data, exp.analysis)
    fig_ep = analysis.figure(0).figure
    if save_ui.value:
        save_figure(fig_ep, out_dir / f"{job_id}_mrb_plot.png")
    fig_ep
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MQA analysis using Mutual Information
    """)
    return


@app.cell
def _(
    QuantumAwesomeness,
    exp,
    job_id,
    lengths,
    mean_mi_curves,
    mmi_record,
    out_dir,
    plot_mean_mutual_info,
    rb_data,
    save_figure,
    save_json,
    save_ui,
):
    qa = QuantumAwesomeness(exp.backend.coupling_map)
    mmi = qa.mean_mutual_info(rb_data.data(), exp._pairs)
    curves = mean_mi_curves(mmi, lengths)
    fig_mi = plot_mean_mutual_info(curves, lengths)
    if save_ui.value:
        save_json(mmi_record(lengths, curves), out_dir / f"{job_id}_mutual_info_data.json")
        save_figure(fig_mi, out_dir / f"{job_id}_mutual_info_plot.png")
    fig_mi
    return


if __name__ == "__main__":
    app.run()
