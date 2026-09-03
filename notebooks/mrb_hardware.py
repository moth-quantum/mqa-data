import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MRB: IBM hardware")


@app.cell
def _():
    import marimo as mo
    import pandas as pd

    from mqa_common.analysis import effective_polarization
    from mqa_common.credentials import connect
    from mqa_common.io import save_figure, save_job_bundle
    from mqa_common.paths import RUNS
    from mqa_common.seeding import seed_all
    from qiskit_device_benchmarking.bench_code.mrb import MirrorRB

    return (
        MirrorRB,
        RUNS,
        connect,
        effective_polarization,
        mo,
        pd,
        save_figure,
        save_job_bundle,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mirror Randomised Benchmarking (MRB): Hardware Experiments

    Converted from `mrb-hardware.ipynb`, which ran MRB on `ibm_fez`.

    **Credentials.** Paste an IBM Quantum Platform API key and (optionally) the instance CRN below and submit.
    They are used for this session only; nothing is written to `~/.qiskit`. With the form left empty,
    previously saved default credentials are tried.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    creds = mo.ui.form(
        mo.md("{token}  {instance}").batch(
            token=mo.ui.text(kind="password", label="API token", full_width=True),
            instance=mo.ui.text(kind="password", label="Instance CRN (optional)", full_width=True),
        ),
        submit_button_label="Connect",
        bordered=True,
    )
    creds
    return (creds,)


@app.cell
def _(connect, creds, mo):
    _vals = creds.value or {}
    service, _msg = connect(_vals.get("token", ""), _vals.get("instance", ""))
    mo.stop(service is None, mo.callout(mo.md(_msg), kind="warn"))
    mo.callout(mo.md(_msg), kind="success")
    return (service,)


@app.cell
def _(mo, service):
    _names = sorted(b.name for b in service.backends())
    backend_ui = mo.ui.dropdown(_names, value="ibm_fez" if "ibm_fez" in _names else _names[0], label="Backend")
    backend_ui
    return (backend_ui,)


@app.cell
def _(backend_ui, mo, service):
    backend = service.backend(backend_ui.value)
    mo.md(f"**{backend.name}**: {backend.num_qubits} qubits.")
    return (backend,)


@app.cell(hide_code=True)
def _(mo):
    num_qubits_ui = mo.ui.number(value=20, start=2, stop=200, step=1, label="Qubits (clamped to the backend)")
    shots_ui = mo.ui.number(value=10000, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50, 100], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 50, value=20, label="Samples per length")
    density_ui = mo.ui.number(value=0.25, start=0.0, stop=1.0, step=0.05, label="2Q gate density")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    save_ui = mo.ui.checkbox(value=True, label="Save circuits, seed and figure under runs/<job_id>/")
    mo.vstack(
        [
            mo.hstack([num_qubits_ui, shots_ui, num_samples_ui], justify="start", wrap=True),
            mo.hstack([density_ui, seed_ui], justify="start", wrap=True),
            lengths_ui,
            save_ui,
        ]
    )
    return (
        density_ui,
        lengths_ui,
        num_qubits_ui,
        num_samples_ui,
        save_ui,
        seed_ui,
        shots_ui,
    )


@app.cell
def _(
    MirrorRB,
    backend,
    density_ui,
    lengths_ui,
    num_qubits_ui,
    num_samples_ui,
    seed_all,
    seed_ui,
    shots_ui,
):
    SEED = seed_all(int(seed_ui.value))
    num_qubits = min(int(num_qubits_ui.value), backend.num_qubits)
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
    # basis_gates=None lets the transpiler translate to the backend's native 2Q gate (ECR on ibm_fez).
    exp.set_transpile_options(basis_gates=None, seed_transpiler=SEED)
    return SEED, exp, lengths, num_qubits, num_samples, shots


@app.cell(hide_code=True)
def _(backend, lengths, mo, num_qubits, num_samples, shots):
    run_btn = mo.ui.run_button(label="Submit to hardware", kind="danger")
    mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"**Submits a real job:** {len(lengths) * num_samples} circuits × {shots} shots on {num_qubits} qubits of "
                    f"**{backend.name}**. Queue time can be hours; this cell blocks until results return."
                ),
                kind="danger",
            ),
            run_btn,
        ]
    )
    return (run_btn,)


@app.cell
def _(exp, mo, run_btn):
    mo.stop(not run_btn.value, mo.md("*Click **Submit to hardware** to run.*"))
    with mo.status.spinner(title="Waiting for the runtime job…"):
        rb_data = exp.run()
        rb_data.block_for_results()
    job_id = rb_data.job_ids[0]
    mo.md(f"Job IDs: `{rb_data.job_ids}`")
    return job_id, rb_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Effective Polarization
    """)
    return


@app.cell
def _(effective_polarization, rb_data):
    analysis = effective_polarization(rb_data)
    fig_ep = analysis.figure(0).figure
    fig_ep
    return (fig_ep,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Save the benchmark configuration and circuits

    A folder named after the job ID receives the qubit count, the seed, all generated MRB circuits (QASM 2)
    and the fit figure, so the run can be reloaded or shared without regenerating circuits.
    """)
    return


@app.cell
def _(
    RUNS,
    SEED,
    exp,
    fig_ep,
    job_id,
    mo,
    num_qubits,
    save_figure,
    save_job_bundle,
    save_ui,
):
    if save_ui.value:
        with mo.status.spinner(title="Saving circuits…"):
            out_dir = save_job_bundle(RUNS, job_id, exp, num_qubits=num_qubits, seed=SEED, pairs=False)
            save_figure(fig_ep, out_dir / f"{job_id}_mrb_plot.png")
        _msg = mo.md(f"Saved to `{out_dir}`.")
    else:
        _msg = mo.md("*Saving disabled.*")
    _msg
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ### Compare gate counts before and after transpilation

    Counts single-qubit (1Q) and two-qubit (2Q) gates across all MRB circuits before and after transpilation.
    The difference is the transpilation overhead, which affects circuit depth and benchmark performance.
    Pick the gate names your backend treats as two-qubit gates.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    two_q_ui = mo.ui.multiselect(["cz", "cx", "ecr", "iswap"], value=["cz", "cx", "ecr", "iswap"], label="Two-qubit gate names")
    two_q_ui
    return (two_q_ui,)


@app.cell
def _(exp, mo, pd, rb_data, two_q_ui):
    rb_data  # noqa: B018 - count only after the run so the gate table sits with the results
    _two_q = set(two_q_ui.value)
    _orig = exp.circuits()
    _trans = exp._transpiled_circuits()

    def _split(_circ):
        _ops = _circ.count_ops()
        _n2 = sum(n for g, n in _ops.items() if g in _two_q)
        return sum(_ops.values()) - _n2, _n2

    _per = pd.DataFrame(
        [
            {"circuit": i, "1Q before": a[0], "2Q before": a[1], "1Q after": b[0], "2Q after": b[1]}
            for i, (a, b) in enumerate(zip(map(_split, _orig), map(_split, _trans)))
        ]
    )
    _summary = pd.DataFrame(
        {
            "stage": ["Before transpilation", "After transpilation", "Overhead"],
            "1Q gates": [_per["1Q before"].sum(), _per["1Q after"].sum(), _per["1Q after"].sum() - _per["1Q before"].sum()],
            "2Q gates": [_per["2Q before"].sum(), _per["2Q after"].sum(), _per["2Q after"].sum() - _per["2Q before"].sum()],
        }
    )
    mo.vstack(
        [
            mo.ui.table(_summary, selection=None, label="Gate count summary (all RB circuits)"),
            mo.md(f"Circuit 0 ops after transpilation: `{dict(_trans[0].count_ops())}`"),
            mo.accordion({"Per-circuit counts": mo.ui.table(_per, selection=None, page_size=20)}),
        ]
    )
    return


if __name__ == "__main__":
    app.run()
