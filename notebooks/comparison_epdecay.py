import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="MRB vs MQA: EP decay")


@app.cell
def _():
    import time
    from pprint import pformat

    import marimo as mo
    import numpy as np

    from mqa_common.analysis import effective_polarization
    from mqa_common.backends import (
        STAB_BASIS_RZ,
        build_stabilizer_backend,
        diagonal_rz_operator,
        standard_name_mapping,
    )
    from mqa_common.seeding import seed_all
    from mqa_common.topologies import chain
    from qiskit_device_benchmarking.bench_code.mrb import MirrorQA, MirrorRB
    from qiskit_device_benchmarking.bench_code.mrb.mirror_qa import MirrorQAAnalysis
    from qiskit_device_benchmarking.bench_code.mrb.mirror_rb_analysis import (
        MirrorRBAnalysis,
    )

    return (
        MirrorQA,
        MirrorQAAnalysis,
        MirrorRB,
        MirrorRBAnalysis,
        STAB_BASIS_RZ,
        build_stabilizer_backend,
        chain,
        diagonal_rz_operator,
        effective_polarization,
        mo,
        np,
        pformat,
        seed_all,
        standard_name_mapping,
        time,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Compare MRB and MirrorQA Experiments

    Converted from `Comparision_EPdecay.ipynb`.

    This notebook configures and runs three benchmarking experiments on the same simulated stabilizer backend:
    **MirrorRB**, **MirrorQA**, and **MirrorQA with start/end Clifford layers enabled**. Using identical runtime
    parameters allows a fair comparison of the methods. Every parameter below is live: change one and the
    experiments re-run (a few seconds at the defaults).
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    num_qubits_ui = mo.ui.slider(2, 10, value=5, label="Qubits (linear chain)")
    p2_ui = mo.ui.number(value=0.01, start=0.0, stop=0.5, step=0.001, label="p2 (2Q depolarizing)")
    p1_ui = mo.ui.number(value=0.001, start=0.0, stop=0.5, step=0.0001, label="p1 (1Q depolarizing)")
    shots_ui = mo.ui.number(value=100, start=10, stop=100000, step=10, label="Shots")
    lengths_ui = mo.ui.multiselect([2, 4, 10, 20, 50, 100], value=[2, 4, 10, 20, 50], label="Circuit lengths")
    num_samples_ui = mo.ui.slider(1, 20, value=5, label="Samples per length")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    mo.vstack(
        [
            mo.hstack([num_qubits_ui, shots_ui, num_samples_ui], justify="start", wrap=True),
            mo.hstack([p1_ui, p2_ui, seed_ui], justify="start", wrap=True),
            lengths_ui,
        ]
    )
    return (
        lengths_ui,
        num_qubits_ui,
        num_samples_ui,
        p1_ui,
        p2_ui,
        seed_ui,
        shots_ui,
    )


@app.cell
def _(
    lengths_ui,
    np,
    num_qubits_ui,
    num_samples_ui,
    p1_ui,
    p2_ui,
    seed_all,
    seed_ui,
    shots_ui,
):
    SEED = seed_all(int(seed_ui.value))
    num_qubits = int(num_qubits_ui.value)
    p1, p2 = float(p1_ui.value), float(p2_ui.value)
    shots = int(shots_ui.value)
    lengths = sorted(int(x) for x in lengths_ui.value)
    num_samples = int(num_samples_ui.value)
    rz_angle = np.pi / 2
    return SEED, lengths, num_qubits, num_samples, p1, p2, rz_angle, shots


@app.cell
def _(
    SEED,
    STAB_BASIS_RZ,
    build_stabilizer_backend,
    chain,
    diagonal_rz_operator,
    num_qubits,
    p1,
    p2,
    rz_angle,
    standard_name_mapping,
):
    backend = build_stabilizer_backend(
        num_qubits,
        chain(num_qubits),
        STAB_BASIS_RZ,
        p1,
        p2,
        SEED,
        custom_name_mapping=standard_name_mapping(STAB_BASIS_RZ, diagonal_rz_operator(rz_angle)),
    )
    return (backend,)


@app.cell
def _(
    MirrorQA,
    MirrorRB,
    SEED,
    backend,
    lengths,
    mo,
    np,
    num_qubits,
    num_samples,
    shots,
    time,
):
    def _make(cls, **opts):
        _exp = cls(
            range(num_qubits),
            lengths=lengths,
            backend=backend,
            two_qubit_gate_density=0.25,
            num_samples=num_samples,
            initial_entangling_angle=np.pi / 2,
            seed=SEED,
        )
        if opts:
            _exp.set_experiment_options(**opts)
        _exp.set_run_options(shots=shots)
        return _exp

    exp_rb = _make(MirrorRB)
    exp_qa = _make(MirrorQA)
    exp_qa_cl = _make(MirrorQA, start_end_clifford=True)

    timings = []
    datasets = []
    for _name, _exp in [("MirrorRB", exp_rb), ("MirrorQA", exp_qa), ("MirrorQA + Cliffords", exp_qa_cl)]:
        _t0 = time.time()
        _data = _exp.run()
        _data.block_for_results()
        timings.append({"experiment": _name, "seconds": round(time.time() - _t0, 2), "job_ids": ", ".join(_data.job_ids)})
        datasets.append(_data)
    rb_data, qa_data, qa_cl_data = datasets
    mo.ui.table(timings, selection=None, label="Simulation timings")
    return exp_qa, exp_qa_cl, exp_rb, qa_cl_data, qa_data, rb_data


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Circuits

    First circuit of each experiment, after the static transpilation step. MQA with start/end Cliffords
    prints the same structure as MRB; plain MQA omits the initial and final Clifford layers.
    """)
    return


@app.cell
def _(exp_qa, exp_qa_cl, exp_rb, mo):
    def _panel(_exp):
        return mo.vstack(
            [mo.md(f"**Pairs:** `{_exp._pairs[0]}`"), _exp._static_trans_circuits[0].draw("mpl", fold=-1)]
        )

    mo.ui.tabs({"MirrorRB": _panel(exp_rb), "MirrorQA": _panel(exp_qa), "MirrorQA + Cliffords": _panel(exp_qa_cl)})
    return


@app.cell(hide_code=True)
def _(mo, pformat, qa_cl_data, qa_data, rb_data):
    def _raw(_data):
        _entries = _data.data()
        return mo.vstack([mo.md(f"`{_data}`  \ntotal entries: **{len(_entries)}**"), mo.plain_text(pformat(_entries[0:1]))])

    mo.accordion(
        {
            "Raw payload (first entry)": mo.ui.tabs(
                {"MirrorRB": _raw(rb_data), "MirrorQA": _raw(qa_data), "MirrorQA + Cliffords": _raw(qa_cl_data)}
            )
        }
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Effective Polarization decay
    """)
    return


@app.cell
def _(
    effective_polarization,
    exp_qa,
    exp_qa_cl,
    exp_rb,
    qa_cl_data,
    qa_data,
    rb_data,
):
    analysis_rb = effective_polarization(rb_data, exp_rb.analysis)
    analysis_qa = effective_polarization(qa_data, exp_qa.analysis)
    analysis_qa_cl = effective_polarization(qa_cl_data, exp_qa_cl.analysis)
    return analysis_qa, analysis_qa_cl, analysis_rb


@app.cell
def _(analysis_qa, analysis_qa_cl, analysis_rb, mo):
    _rows = [
        {"experiment": _n, "status": str(_a.status()), "figures": ", ".join(_a.figure_names)}
        for _n, _a in [("MirrorRB", analysis_rb), ("MirrorQA", analysis_qa), ("MirrorQA + Cliffords", analysis_qa_cl)]
    ]
    mo.ui.table(_rows, selection=None, label="Analysis status")
    return


@app.cell
def _(analysis_qa, analysis_qa_cl, analysis_rb, mo):
    _figs = {
        "MirrorRB": analysis_rb.figure(0).figure,
        "MirrorQA": analysis_qa.figure(0).figure,
        "MirrorQA + Cliffords": analysis_qa_cl.figure(0).figure,
    }
    mo.vstack([mo.ui.tabs(_figs), mo.hstack(list(_figs.values()), widths="equal", wrap=True)])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Cross-check: MRB data through the MQA processor

    Processing the MRB dataset with the MQA analysis should give the same fit as MQA with Cliffords enabled.
    The `alpha` rows below come from `MirrorRBAnalysis` and `MirrorQAAnalysis` run on the **same** `rb_data`.
    """)
    return


@app.cell
def _(MirrorQAAnalysis, MirrorRBAnalysis, effective_polarization, mo, rb_data):
    _rb_res = effective_polarization(rb_data, MirrorRBAnalysis())
    rb_alpha = _rb_res.analysis_results(dataframe=True).query("name == 'alpha'")[["name", "value"]].astype(str)
    mrb_with_qa_proc = effective_polarization(rb_data, MirrorQAAnalysis())
    qa_alpha = mrb_with_qa_proc.analysis_results(dataframe=True).query("name == 'alpha'")[["name", "value"]].astype(str)
    mo.vstack(
        [
            mo.hstack(
                [
                    mo.ui.table(rb_alpha, selection=None, label="MirrorRBAnalysis on rb_data"),
                    mo.ui.table(qa_alpha, selection=None, label="MirrorQAAnalysis on rb_data"),
                ],
                widths="equal",
            ),
            mo.md("**MRB data + MQA processor**"),
            mrb_with_qa_proc.figure(0).figure,
        ]
    )
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Deterministic reproducibility check

    Runs the MirrorRB experiment twice with a pinned simulator seed and a single thread, then compares the
    canonicalised counts. Metadata (job ids, timestamps) differs run to run, so only counts are compared.
    """)
    return


@app.cell
def _(SEED, backend, exp_rb, mo, shots):
    backend.set_options(seed_simulator=SEED, max_parallel_threads=1, max_parallel_experiments=1)
    exp_rb.set_run_options(shots=shots, seed_simulator=SEED)

    def _counts(_expdata):
        return [dict(sorted(_e.get("counts", {}).items())) for _e in _expdata.data()]

    _run1 = exp_rb.run()
    _run1.block_for_results()
    _run2 = exp_rb.run()
    _run2.block_for_results()
    _c1, _c2 = _counts(_run1), _counts(_run2)
    _same_len = len(_c1) == len(_c2)
    if _same_len and _c1 == _c2:
        _out = mo.callout(mo.md(f"Counts identical across {len(_c1)} circuits."), kind="success")
    else:
        _bad = [_i for _i, (_a, _b) in enumerate(zip(_c1, _c2)) if _a != _b]
        _first = _bad[0] if _bad else None
        _out = mo.callout(
            mo.md(
                f"Counts differ: same length={_same_len} ({len(_c1)} vs {len(_c2)}), mismatches={len(_bad)}, first={_first}\n\n"
                + (f"run1: `{_c1[_first]}`\n\nrun2: `{_c2[_first]}`" if _first is not None else "")
            ),
            kind="danger",
        )
    _out
    return


if __name__ == "__main__":
    app.run()
