import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MRB: custom noisy backend")


@app.cell
def _():
    import marimo as mo

    from mqa_common.analysis import effective_polarization
    from mqa_common.backends import STAB_BASIS_S, NoisyBackend
    from mqa_common.seeding import seed_all
    from mqa_common.topologies import complete
    from qiskit_device_benchmarking.bench_code.mrb import MirrorRB

    return (
        MirrorRB,
        NoisyBackend,
        STAB_BASIS_S,
        complete,
        effective_polarization,
        mo,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mirror Randomised Benchmarking (MRB): Custom Noisy Backend Simulation

    Converted from `mrb-custom.ipynb`.

    Creates a fully connected quantum device, wraps it in a custom noisy backend (`NoisyBackend`, a
    `GenericBackendV2` with uniform depolarizing rates), and runs Mirror Randomized Benchmarking on it.
    The number of qubits and the noise levels can be changed to simulate different devices.

    The original notebook built a 6-node all-to-all coupling map for an 8-qubit backend and then benchmarked
    only 3 of those qubits ("upper bound the qubit number or sherbrooke doesn't work"). Current Qiskit
    requires the coupling map to cover every backend qubit, so the backend size below drives both.
    A seed was added so runs are reproducible.
    """)


@app.cell(hide_code=True)
def _(mo):
    p_ui = mo.ui.number(value=0.01, start=0.0, stop=0.5, step=0.001, label="p2 (2Q depolarizing); p1 = p2 / 10")
    backend_qubits_ui = mo.ui.slider(2, 12, value=8, label="Backend qubits (all-to-all)")
    num_qubits_ui = mo.ui.slider(1, 12, value=3, label="Qubits benchmarked")
    shots_ui = mo.ui.number(value=100, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50, 100], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 50, value=20, label="Samples per length")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    mo.vstack(
        [
            mo.hstack([backend_qubits_ui, num_qubits_ui], justify="start", wrap=True),
            mo.hstack([p_ui, shots_ui, num_samples_ui, seed_ui], justify="start", wrap=True),
            lengths_ui,
        ]
    )
    return (
        backend_qubits_ui,
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
    STAB_BASIS_S,
    backend_qubits_ui,
    complete,
    mo,
    num_qubits_ui,
    p_ui,
):
    p = float(p_ui.value)
    _n = int(backend_qubits_ui.value)
    backend = NoisyBackend(
        num_qubits=_n,
        basis_gates=STAB_BASIS_S,
        p1=p / 10,
        p2=p,
        coupling_map=[list(edge) for edge in complete(_n).get_edges()],
    )
    num_qubits = min(int(num_qubits_ui.value), _n)
    mo.md(f"Backend: **{backend.num_qubits}** qubits, basis `{STAB_BASIS_S}`, p1={p / 10:g}, p2={p:g}. Benchmarking **{num_qubits}** qubits.")
    return backend, num_qubits


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Configure and run the MRB experiment

    Shots, circuit lengths, qubits and sample count come from the controls above. At the defaults this is
    120 circuits at 100 shots and finishes in seconds, so the experiment re-runs automatically on change.
    """)


@app.cell
def _(
    MirrorRB,
    backend,
    lengths_ui,
    mo,
    num_qubits,
    num_samples_ui,
    seed_all,
    seed_ui,
    shots_ui,
):
    SEED = seed_all(int(seed_ui.value))
    lengths = sorted(int(x) for x in lengths_ui.value)
    exp = MirrorRB(
        range(num_qubits),
        lengths,
        backend=backend,
        two_qubit_gate_density=0.25,
        num_samples=int(num_samples_ui.value),
        seed=SEED,
    )
    exp.set_run_options(shots=int(shots_ui.value))
    rb_data = exp.run()
    rb_data.block_for_results()
    mo.md(f"Job IDs: `{rb_data.job_ids}`")
    return (rb_data,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Analyze and visualize

    Effective Polarization fit over circuit length.
    """)


@app.cell
def _(effective_polarization, rb_data):
    analysis = effective_polarization(rb_data)
    analysis.figure(0).figure


if __name__ == "__main__":
    app.run()
