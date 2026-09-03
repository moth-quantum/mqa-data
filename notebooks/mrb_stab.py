import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    app_title="MRB: stabilizer simulation (30 qubits)",
)


@app.cell
def _():
    import marimo as mo

    from mqa_common.analysis import effective_polarization
    from mqa_common.backends import STAB_BASIS_S, build_stabilizer_backend
    from mqa_common.seeding import seed_all
    from mqa_common.topologies import fez_30_coupling_map
    from qiskit_device_benchmarking.bench_code.mrb import MirrorRB

    return (
        MirrorRB,
        STAB_BASIS_S,
        build_stabilizer_backend,
        effective_polarization,
        fez_30_coupling_map,
        mo,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Configure and Run a Large-Scale MRB Simulation

    Converted from `mrb-stab.ipynb`.

    A 30-qubit noisy stabilizer simulator for large-scale Mirror Randomized Benchmarking: the first 30 qubits
    of the `ibm_fez` coupling map, a depolarizing noise model with independent `p1` / `p2`, and an
    `AerSimulator(method="stabilizer")` backend. Qubit count, noise, lengths, shots, samples and seed are all
    controls below.

    The committed edge list references qubit index 30 while declaring 30 qubits; Qiskit's
    `Target.from_configuration` accepts it, so the list is kept verbatim.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    p1_ui = mo.ui.number(value=0.001, start=0.0, stop=0.5, step=0.0001, label="p1 (1Q depolarizing)")
    p2_ui = mo.ui.number(value=0.01, start=0.0, stop=0.5, step=0.001, label="p2 (2Q depolarizing)")
    shots_ui = mo.ui.number(value=10000, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 50, value=20, label="Samples per length")
    density_ui = mo.ui.number(value=0.25, start=0.0, stop=1.0, step=0.05, label="2Q gate density")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    mo.vstack(
        [
            mo.hstack([p1_ui, p2_ui, seed_ui], justify="start", wrap=True),
            mo.hstack([shots_ui, num_samples_ui, density_ui], justify="start", wrap=True),
            lengths_ui,
        ]
    )
    return (
        density_ui,
        lengths_ui,
        num_samples_ui,
        p1_ui,
        p2_ui,
        seed_ui,
        shots_ui,
    )


@app.cell
def _(
    STAB_BASIS_S,
    build_stabilizer_backend,
    fez_30_coupling_map,
    mo,
    p1_ui,
    p2_ui,
    seed_all,
    seed_ui,
):
    SEED = seed_all(int(seed_ui.value))
    p1, p2 = float(p1_ui.value), float(p2_ui.value)
    num_qubits = 30
    backend = build_stabilizer_backend(num_qubits, fez_30_coupling_map(), STAB_BASIS_S, p1, p2, SEED)
    mo.md(f"Backend: `AerSimulator(method='stabilizer')`, **{num_qubits}** qubits, basis `{STAB_BASIS_S}`, p1={p1:g}, p2={p2:g}.")
    return SEED, backend, num_qubits


@app.cell
def _(
    MirrorRB,
    SEED,
    backend,
    density_ui,
    lengths_ui,
    num_qubits,
    num_samples_ui,
    shots_ui,
):
    shots = int(shots_ui.value)
    lengths = sorted(int(x) for x in lengths_ui.value)
    num_samples = int(num_samples_ui.value)
    exp = MirrorRB(
        range(num_qubits),
        lengths=lengths,
        backend=backend,
        two_qubit_gate_density=float(density_ui.value),
        num_samples=num_samples,
        seed=SEED,
    )
    exp.set_run_options(shots=shots)
    return exp, lengths, num_samples, shots


@app.cell(hide_code=True)
def _(lengths, mo, num_qubits, num_samples, shots):
    run_btn = mo.ui.run_button(label="Run experiment", kind="danger")
    mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"**Cost:** {len(lengths) * num_samples} circuits × {shots} shots on a {num_qubits}-qubit stabilizer "
                    f"simulation. Minutes at the defaults. Results are cleared when a parameter changes."
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
    with mo.status.spinner(title="Running MRB circuits…"):
        rb_data = exp.run()
        rb_data.block_for_results()
    mo.md(f"Job IDs: `{rb_data.job_ids}`")
    return (rb_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analysis

    Effective Polarization fit over circuit length.
    """)
    return


@app.cell
def _(effective_polarization, rb_data):
    analysis = effective_polarization(rb_data)
    analysis.figure(0).figure
    return


if __name__ == "__main__":
    app.run()
