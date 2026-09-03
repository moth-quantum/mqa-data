import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MQA: custom noisy backend")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from mqa_common.analysis import effective_polarization
    from mqa_common.backends import NoisyBackend
    from mqa_common.mi_plot import mean_mi_curves, plot_mean_mutual_info
    from mqa_common.seeding import seed_all
    from qiskit_device_benchmarking.bench_code.mrb import MirrorQA, QuantumAwesomeness

    return (
        MirrorQA,
        NoisyBackend,
        QuantumAwesomeness,
        effective_polarization,
        mean_mi_curves,
        mo,
        np,
        plot_mean_mutual_info,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mirror Quantum Awesomeness (MQA): Custom Noisy Backend Simulation

    Converted from `mqa-custom.ipynb`.

    Runs MQA on `NoisyBackend`, a `GenericBackendV2` with uniform depolarizing rates, then analyses the result
    two ways: the MRB Effective Polarization fit, and the mean mutual information of paired, spectator and
    isolated qubits against circuit length.

    The original notebook's unused `real_device` branch (which needed the retired `qiskit_ibm_provider`) was
    dropped; `mqa_hardware.py` covers real devices. A seed control was added for reproducibility.
    """)
    return


@app.cell(hide_code=True)
def _(mo, np):
    ANGLES = {"0": 0.0, "π/4": np.pi / 4, "π/2": np.pi / 2}
    p_ui = mo.ui.number(value=0.0015, start=0.0, stop=0.5, step=0.0001, label="p2 (2Q depolarizing); p1 = p2 / 10")
    num_qubits_ui = mo.ui.slider(2, 20, value=8, label="Qubits (all-to-all backend)")
    shots_ui = mo.ui.number(value=10000, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50, 100], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 50, value=20, label="Samples per length")
    angle_ui = mo.ui.dropdown(ANGLES, value="π/4", label="Initial entangling angle θ")
    density_ui = mo.ui.number(value=0.25, start=0.0, stop=1.0, step=0.05, label="2Q gate density ρ")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    mo.vstack(
        [
            mo.hstack([num_qubits_ui, p_ui, seed_ui], justify="start", wrap=True),
            mo.hstack([shots_ui, num_samples_ui, angle_ui, density_ui], justify="start", wrap=True),
            lengths_ui,
        ]
    )
    return (
        angle_ui,
        density_ui,
        lengths_ui,
        num_qubits_ui,
        num_samples_ui,
        p_ui,
        seed_ui,
        shots_ui,
    )


@app.cell
def _(
    NoisyBackend,
    angle_ui,
    density_ui,
    lengths_ui,
    num_qubits_ui,
    num_samples_ui,
    p_ui,
    seed_all,
    seed_ui,
    shots_ui,
):
    SEED = seed_all(int(seed_ui.value))
    p = float(p_ui.value)
    shots = int(shots_ui.value)
    lengths = sorted(int(x) for x in lengths_ui.value)
    num_samples = int(num_samples_ui.value)
    angle = float(angle_ui.value)
    angle_label = angle_ui.selected_key
    density = float(density_ui.value)
    backend = NoisyBackend(
        num_qubits=int(num_qubits_ui.value),
        basis_gates=["id", "h", "x", "y", "z", "rx", "cx"],
        p1=p / 10,
        p2=p,
    )
    return (
        SEED,
        angle,
        angle_label,
        backend,
        density,
        lengths,
        num_samples,
        shots,
    )


@app.cell
def _(MirrorQA, SEED, angle, backend, density, lengths, num_samples, shots):
    exp = MirrorQA(
        range(backend.num_qubits),
        lengths,
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
def _(backend, lengths, mo, num_samples, shots):
    run_btn = mo.ui.run_button(label="Run experiment", kind="danger")
    mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"**Cost:** {len(lengths) * num_samples} circuits × {shots} shots on a {backend.num_qubits}-qubit "
                    f"Aer simulation. Minutes at the defaults. Results below are cleared whenever a parameter changes; "
                    f"click again to re-run."
                ),
                kind="info",
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
    mo.md(f"Job IDs: `{rb_data.job_ids}`")
    return (rb_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MQA analysis using MRB

    Effective Polarization fit from the MRB analysis pipeline.
    """)
    return


@app.cell
def _(effective_polarization, exp, rb_data):
    analysis = effective_polarization(rb_data, exp.analysis)
    analysis.figure(0).figure
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## MQA analysis using Mutual Information

    Mean mutual information per circuit length for injected pairs, their spectators, and isolated qubits.
    """)
    return


@app.cell
def _(
    QuantumAwesomeness,
    angle_label,
    density,
    exp,
    lengths,
    mean_mi_curves,
    plot_mean_mutual_info,
    rb_data,
):
    qa = QuantumAwesomeness(exp.backend.coupling_map)
    mmi = qa.mean_mutual_info(rb_data.data(), exp._pairs)
    curves = mean_mi_curves(mmi, lengths)
    plot_mean_mutual_info(curves, lengths, title=f"θ = {angle_label}, ρ = {density:g}")
    return


if __name__ == "__main__":
    app.run()
