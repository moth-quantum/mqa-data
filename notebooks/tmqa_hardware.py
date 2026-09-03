import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="TMQA 3: ibm_miami")


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from qiskit_ibm_runtime.fake_provider import FakeMiami

    from mqa_common.credentials import connect
    from mqa_common.io import save_job_bundle, save_json
    from mqa_common.mi_plot import mean_mi_curves, plot_mean_mutual_info
    from mqa_common.paths import REPO, RUNS
    from mqa_common.plotting import plot_one_minus_p
    from mqa_common.seeding import seed_all
    from mqa_common.topo_bot import (
        evaluate_bot,
        extract_mi,
        load_saved_job,
        save_topo_pickle,
    )
    from qiskit_device_benchmarking.bench_code.mrb import (
        MirrorQATopo,
        QuantumAwesomeness,
    )

    return (
        FakeMiami,
        MirrorQATopo,
        QuantumAwesomeness,
        REPO,
        RUNS,
        connect,
        evaluate_bot,
        extract_mi,
        load_saved_job,
        mean_mi_curves,
        mo,
        np,
        plot_mean_mutual_info,
        plot_one_minus_p,
        save_job_bundle,
        save_json,
        save_topo_pickle,
        seed_all,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Topological MQA (TMQA) 3: `ibm_miami`

    Converted from `tmqa-hardware.ipynb`.

    The third notebook of the Topological MQA series runs the same process on `ibm_miami`, real hardware with
    120 qubits in a 10 x 12 arrangement.

    Two data sources, one analysis path:

    - **Saved job (offline, default).** Loads one of the jobs stored under `ibm_miami/<job_id>/<job_id>_data.pkl`.
      No IBM account needed.
    - **Live run.** Needs an IBM Quantum Platform API key (and optionally the instance CRN). Credentials are used for
      this session only; nothing is written to `~/.qiskit`. The run is behind a button and, when saving is on,
      writes the same `_data.pkl` layout the offline path reads, plus circuits and the bot results, under `runs/`.
    """)
    return


@app.cell(hide_code=True)
def _(REPO, mo):
    source_ui = mo.ui.radio({"Saved job (offline)": "saved", "Live ibm_miami run": "live"}, value="Saved job (offline)", label="Data source")
    available = sorted(REPO.glob("ibm_miami/*/*_data.pkl"))
    job_ui = mo.ui.dropdown(
        {p.parent.name: p for p in available},
        value=available[-1].parent.name if available else None,
        label="Saved job (latest selected by default)",
    )
    acc_ui = mo.ui.slider(0.5, 1.0, step=0.05, value=0.9, label="Bot accuracy threshold acc", show_value=True)
    mo.vstack([source_ui, mo.hstack([job_ui, acc_ui], justify="start", wrap=True)])
    return acc_ui, available, job_ui, source_ui


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Live run settings
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
    backend_name_ui = mo.ui.text(value="ibm_miami", label="Backend")
    num_qubits_ui = mo.ui.number(value=120, start=2, stop=200, step=1, label="Qubits (clamped to the backend)")
    shots_ui = mo.ui.number(value=1000, start=10, stop=100000, step=10, label="Shots (MQA used 10000, topo simulation 1000)")
    lengths_ui = mo.ui.text(value="2, 6, 14, 24, 30", label="Circuit lengths", full_width=True)
    num_samples_ui = mo.ui.number(value=100, start=1, stop=10000, step=1, label="Samples per length")
    ffw_ui = mo.ui.number(value=1.3, start=0.1, stop=5.0, step=0.05, label="ffw")
    dd_ui = mo.ui.checkbox(value=True, label='Dynamical decoupling (dd="xx")')
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    save_ui = mo.ui.checkbox(value=True, label="Save circuits, data.pkl and bot results under runs/<job_id>/")
    mo.vstack(
        [
            creds,
            mo.hstack([backend_name_ui, num_qubits_ui, shots_ui, num_samples_ui], justify="start", wrap=True),
            lengths_ui,
            mo.hstack([ffw_ui, dd_ui, seed_ui], justify="start", wrap=True),
            save_ui,
        ]
    )
    return (
        backend_name_ui,
        creds,
        dd_ui,
        ffw_ui,
        lengths_ui,
        num_qubits_ui,
        num_samples_ui,
        save_ui,
        seed_ui,
        shots_ui,
    )


@app.cell
def _(acc_ui, connect, creds, mo, seed_all, seed_ui, source_ui):
    SEED = seed_all(int(seed_ui.value))
    source = source_ui.value
    acc = float(acc_ui.value)
    service = None
    if source == "live":
        _vals = creds.value or {}
        service, _msg = connect(_vals.get("token", ""), _vals.get("instance", ""))
        _out = mo.callout(mo.md(_msg), kind="success" if service else "warn")
    else:
        _out = mo.md("*Live path disabled; using a saved job.*")
    _out
    return SEED, acc, service, source


@app.cell(hide_code=True)
def _(mo, source):
    run_btn = mo.ui.run_button(label="Submit to hardware", kind="danger")
    if source == "live":
        _out = mo.vstack([mo.callout(mo.md("**Submits a real job** to the selected backend and blocks until results return (queue time can be hours)."), kind="danger"), run_btn])
    else:
        _out = mo.md("")
    _out
    return (run_btn,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Data
    """)
    return


@app.cell
def _(
    FakeMiami,
    MirrorQATopo,
    RUNS,
    SEED,
    available,
    backend_name_ui,
    dd_ui,
    ffw_ui,
    job_ui,
    lengths_ui,
    load_saved_job,
    mo,
    np,
    num_qubits_ui,
    num_samples_ui,
    run_btn,
    save_job_bundle,
    save_topo_pickle,
    save_ui,
    service,
    shots_ui,
    source,
):
    if source == "saved":
        mo.stop(not available, mo.callout(mo.md("No saved jobs found under `ibm_miami/`."), kind="warn"))
        exp, rb_data, _blob = load_saved_job(job_ui.value, FakeMiami().coupling_map)
        num_qubits, lengths = _blob["num_qubits"], list(_blob["lengths"])
        job_id = rb_data.job_ids[0]
        _note = mo.md(f"Loaded job **{job_id}**: {len(_blob['pairs'])} circuits, {num_qubits} qubits, lengths {lengths}, {_blob['shots']} shots, seed {_blob['seed']}.")
    else:
        mo.stop(service is None, mo.callout(mo.md("Connect with valid credentials to run on hardware."), kind="warn"))
        mo.stop(not run_btn.value, mo.md("*Click **Submit to hardware** to run.*"))
        backend = service.backend(backend_name_ui.value)
        num_qubits = min(int(num_qubits_ui.value), backend.num_qubits)
        lengths = sorted({int(x) for x in lengths_ui.value.replace(";", ",").split(",") if x.strip()})
        shots, num_samples = int(shots_ui.value), int(num_samples_ui.value)
        exp = MirrorQATopo(
            range(num_qubits),
            lengths=lengths,
            sampling_algorithm="topo",
            mode="random",
            backend=backend,
            num_samples=num_samples,
            ffw=float(ffw_ui.value),
            initial_entangling_angle=np.pi / 2,
            seed=SEED,
        )
        # dd requires Backend.Target's pulse alignments (handled in mirror_rb_experiment).
        exp.set_run_options(shots=shots, **({"dd": "xx"} if dd_ui.value else {}))
        with mo.status.spinner(title="Waiting for the runtime job…"):
            rb_data = exp.run()
            rb_data.block_for_results()
        job_id = rb_data.job_ids[0]
        _job = service.job(job_id)
        _note = mo.md(f"Job **{job_id}** status: `{_job.status()}`; metrics: `{_job.metrics()}`")
        if save_ui.value:
            _out_dir = save_job_bundle(RUNS, job_id, exp, num_qubits=num_qubits, seed=SEED, pairs=True)
            save_topo_pickle(_out_dir / f"{job_id}_data.pkl", exp, rb_data, lengths=lengths, num_samples=num_samples, num_qubits=num_qubits, shots=shots, seed=SEED)
            _note = mo.md(f"Job **{job_id}** status: `{_job.status()}`. Saved circuits and `{job_id}_data.pkl` to `{_out_dir}`.")
    _note
    return exp, job_id, lengths, num_qubits, rb_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Bot analysis

    The bot builds a max-weight matching on the mutual-information graph of the genuine qubits and is scored
    against the injected pairs (`P(pairs)`, with the `acc` overlap threshold) and against the sampler mode
    (`P(topo)`, independent of `acc`).
    """)
    return


@app.cell
def _(
    RUNS,
    acc,
    evaluate_bot,
    exp,
    extract_mi,
    job_id,
    lengths,
    mo,
    num_qubits,
    rb_data,
    save_json,
    save_ui,
    source,
):
    with mo.status.spinner(title="Extracting mutual information and running the bot…"):
        mi = extract_mi(exp, rb_data, num_qubits)
        results_hw = {"miami": evaluate_bot(mi, exp, num_qubits, num_qubits + 2, lengths, acc=acc)}
    _r = results_hw["miami"]
    _saved = ""
    if save_ui.value and source == "live":
        save_json(_r, RUNS / job_id / f"{job_id}_bot_results.json")
        _saved = f" Saved `{job_id}_bot_results.json`."
    mo.vstack(
        [
            mo.md(f"Bot results for **{job_id}** (acc={acc:.2f}).{_saved}"),
            mo.ui.table(
                [{"length": L, "P(pairs)": f"{p:.3f}", "P(topo)": f"{t:.3f}"} for L, p, t in zip(_r["lengths"], _r["p_bot_pairs"], _r["p_mode_topo"])],
                selection=None,
            ),
        ]
    )
    return (results_hw,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Plots
    """)
    return


@app.cell
def _(
    QuantumAwesomeness,
    exp,
    lengths,
    mean_mi_curves,
    plot_mean_mutual_info,
    rb_data,
):
    qa = QuantumAwesomeness(exp.backend.coupling_map)
    mmi = qa.mean_mutual_info(rb_data.data(), exp._pairs)
    curves = mean_mi_curves(mmi, lengths, pairtypes=("paired", "singles"))
    plot_mean_mutual_info(curves, lengths, labels={"paired": "paired", "singles": "singles"})
    return


@app.cell
def _(mo, plot_one_minus_p, results_hw):
    _r = results_hw["miami"]
    _pairs = plot_one_minus_p({"ibm_miami": (_r["lengths"], _r["p_bot_pairs"])}, r"$1 - P(\mathrm{bot} = \mathrm{pairs})$")
    _topo = plot_one_minus_p({"ibm_miami": (_r["lengths"], _r["p_mode_topo"])}, r"$1 - P(\mathrm{bot} = \mathrm{topo})$", legend_loc="center right")
    mo.hstack([_pairs, _topo], widths="equal", wrap=True)
    return


if __name__ == "__main__":
    app.run()
