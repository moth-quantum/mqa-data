import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MQA: IBM hardware")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from mqa_common.analysis import effective_polarization
    from mqa_common.credentials import connect
    from mqa_common.io import save_figure, save_job_bundle, save_json
    from mqa_common.mi_plot import mean_mi_curves, mmi_record, plot_mean_mutual_info
    from mqa_common.paths import RUNS
    from mqa_common.seeding import seed_all
    from qiskit_device_benchmarking.bench_code.mrb import MirrorQA, QuantumAwesomeness

    return (
        MirrorQA,
        QuantumAwesomeness,
        RUNS,
        connect,
        effective_polarization,
        mean_mi_curves,
        mmi_record,
        mo,
        np,
        plot_mean_mutual_info,
        save_figure,
        save_job_bundle,
        save_json,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Mirror Quantum Awesomeness (MQA): Hardware Experiments

    Converted from `mqa-hardware.ipynb`, which ran MQA on `ibm_fez`.

    **Credentials.** Paste an IBM Quantum Platform API key and (optionally) the instance CRN below and submit.
    They are used for this session only; unlike the original notebook nothing is written to `~/.qiskit`.
    With the form left empty, previously saved default credentials are tried.

    The per-run variants kept under `ibm_fez&ibm_kingston/` (backend, entangling angle, qubit count) are the
    controls below. Saved artefacts go to `runs/<job_id>/`.
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
    mo.md(f"**{backend.name}**: {backend.num_qubits} qubits, basis `{backend.target.operation_names & {'cz', 'cx', 'ecr', 'rz', 'sx', 'x'}}`.")
    return (backend,)


@app.cell(hide_code=True)
def _(mo, np):
    ANGLES = {"0": 0.0, "π/4": np.pi / 4, "π/2": np.pi / 2}
    num_qubits_ui = mo.ui.number(value=156, start=2, stop=200, step=1, label="Qubits (clamped to the backend)")
    shots_ui = mo.ui.number(value=10000, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50, 100], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 50, value=20, label="Samples per length")
    angle_ui = mo.ui.dropdown(ANGLES, value="π/2", label="Initial entangling angle θ")
    density_ui = mo.ui.number(value=0.25, start=0.0, stop=1.0, step=0.05, label="2Q gate density ρ")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    save_ui = mo.ui.checkbox(value=True, label="Save circuits, data and figures under runs/<job_id>/")
    mo.vstack(
        [
            mo.hstack([num_qubits_ui, shots_ui, num_samples_ui, seed_ui], justify="start", wrap=True),
            mo.hstack([angle_ui, density_ui], justify="start", wrap=True),
            lengths_ui,
            save_ui,
        ]
    )
    return (
        angle_ui,
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
    MirrorQA,
    angle_ui,
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
    exp = MirrorQA(
        range(num_qubits),
        lengths=lengths,
        backend=backend,
        two_qubit_gate_density=float(density_ui.value),
        num_samples=num_samples,
        initial_entangling_angle=float(angle_ui.value),
        seed=SEED,
    )
    exp.set_run_options(shots=shots)
    return SEED, exp, lengths, num_qubits, num_samples, shots


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Run experiment
    """)
    return


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


@app.cell
def _(RUNS, SEED, exp, job_id, mo, num_qubits, save_job_bundle, save_ui):
    out_dir = RUNS / job_id
    if save_ui.value:
        with mo.status.spinner(title="Saving circuits…"):
            save_job_bundle(RUNS, job_id, exp, num_qubits=num_qubits, seed=SEED, pairs=True, angle=True, density=True)
        _msg = mo.md(f"Saved qubits, pairs, angle, density, seed and circuits to `{out_dir}`.")
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
