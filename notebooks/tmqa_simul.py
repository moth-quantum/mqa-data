import marimo

__generated_with = "0.24.0"
app = marimo.App(width="medium", app_title="TMQA 1: lattice simulation")


@app.cell
def _():
    import gc
    import pickle

    import marimo as mo
    import numpy as np

    from mqa_common.backends import (
        STAB_BASIS_RZ,
        legacy_rz_operator,
        standard_name_mapping,
    )
    from mqa_common.paths import CKPT
    from mqa_common.plotting import plot_one_minus_p
    from mqa_common.seeding import seed_all
    from mqa_common.topo_bot import (
        ckpt_key,
        ckpt_path,
        evaluate_bot,
        extract_mi,
        lattice_backend,
        run_topo,
    )

    return (
        CKPT,
        STAB_BASIS_RZ,
        ckpt_key,
        ckpt_path,
        evaluate_bot,
        extract_mi,
        gc,
        lattice_backend,
        legacy_rz_operator,
        mo,
        np,
        pickle,
        plot_one_minus_p,
        run_topo,
        seed_all,
        standard_name_mapping,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Topological MQA (TMQA) 1: Simulation

    Converted from `tmqa-simul.ipynb`.

    Welcome to the first notebook for topological analysis of Mirror Quantum Awesomeness (Topological MQA, or
    TMQA). It runs different sizes of square lattice through the TMQA algorithm.

    We tested the benchmarking process for 4x4, 6x6, 8x8 and 10x10 on a classical computer (MacBook Pro M3 Max,
    32GB RAM) and it took a few hours, so we recommend starting with these square lattices.

    Key files:

    - `qiskit_device_benchmarking/utilities/sampling_utils.py`: `TopoSampler` and its parent class `NewSampler`.
    - `qiskit_device_benchmarking/bench_code/mrb/mirror_rb_experiment.py`: the `if not self.experiment_options.full_sampling`
      branch holds the workflow for `TopoSampler` / `NewSampler`.
    - `qiskit_device_benchmarking/bench_code/mrb/mirror_qa_topo.py`: the `MirrorQATopo` class and its utilities.

    The logic:

    - Choose the error rate (`p2`), the circuit depths (`lengths`), the number of `samples` and `shots`, and the
      lattice sizes. Non-square lattices such as 10 x 12 (IBM Nighthawk) are supported by `lattice_backend`.
    - `MirrorQATopo` stores these and asks the sampler to pick, per layer, either as many pairs as possible
      (`mode=full`) or a torus-like pairing that abandons one qubit per boundary and pairs "imaginary" qubits
      around the map (`mode=random`). With `mode="random"` both conditions appear equally often.
    - `TopoSampler` places two-qubit gates (`CXGate`) only on even circuit indices with pairs chosen by MWPM and
      random single-qubit gates on odd indices.
    - `.run()` executes all circuits. Besides the Effective Polarization and Mutual Information analyses, a *bot*
      deduces the pairs and the `mode` from the MI data. `P(pairs)` and `P(topo)` are its success probabilities;
      the plots use `1-P(...)` so the *critical point*, where wrong answers explode, is visible.

    **Checkpoints.** Each lattice result is pickled under `topo_ckpt/` keyed by its parameters (same md5 recipe as the
    original notebook, so existing checkpoints load). Cached sizes appear immediately; missing sizes need the run button.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    RECOMMENDED_LENGTHS = {
        "0.001": [26, 40, 54, 68, 82],
        "0.01": [26, 40, 54, 68, 82],
        "0.05": [16, 18, 20, 22, 24],
        "0.1": [8, 10, 12, 14, 16],
    }
    p2_ui = mo.ui.dropdown({"0.001": 1e-3, "0.01": 1e-2, "0.05": 5e-2, "0.1": 1e-1}, value="0.01", label="p2 (2Q depolarizing); p1 = p2 / 10")
    sizes_ui = mo.ui.multiselect([4, 6, 8, 10, 12], value=[4, 6, 8, 10], label="Lattice sizes n (n x n)")
    shots_ui = mo.ui.number(value=1000, start=10, stop=100000, step=10, label="Shots")
    num_samples_ui = mo.ui.number(value=1000, start=1, stop=10000, step=1, label="Samples per length")
    seed_ui = mo.ui.number(value=123, start=0, stop=2**31 - 1, step=1, label="Seed")
    mo.vstack(
        [
            mo.hstack([p2_ui, shots_ui, num_samples_ui, seed_ui], justify="start", wrap=True),
            sizes_ui,
        ]
    )
    return (
        RECOMMENDED_LENGTHS,
        num_samples_ui,
        p2_ui,
        seed_ui,
        shots_ui,
        sizes_ui,
    )


@app.cell(hide_code=True)
def _(RECOMMENDED_LENGTHS, mo, p2_ui):
    # Re-created whenever p2 changes so the default follows the authors' per-error-rate recommendation.
    lengths_ui = mo.ui.text(
        value=", ".join(str(x) for x in RECOMMENDED_LENGTHS[p2_ui.selected_key]),
        label=f"Circuit lengths (recommended for p2={p2_ui.selected_key}; 0.1% has no recorded recommendation)",
        full_width=True,
    )
    lengths_ui
    return (lengths_ui,)


@app.cell
def _(
    STAB_BASIS_RZ,
    legacy_rz_operator,
    lengths_ui,
    np,
    num_samples_ui,
    p2_ui,
    seed_all,
    seed_ui,
    shots_ui,
    sizes_ui,
    standard_name_mapping,
):
    SEED = seed_all(int(seed_ui.value))
    p2 = float(p2_ui.value)
    p1 = p2 / 10
    rz_angle = np.pi / 2
    shots = int(shots_ui.value)
    num_samples = int(num_samples_ui.value)
    lengths = sorted({int(x) for x in lengths_ui.value.replace(";", ",").split(",") if x.strip()})
    sizes = sorted(int(n) for n in sizes_ui.value)
    custom_name_mapping = standard_name_mapping(STAB_BASIS_RZ, legacy_rz_operator(rz_angle))
    return (
        SEED,
        custom_name_mapping,
        lengths,
        num_samples,
        p1,
        p2,
        shots,
        sizes,
    )


@app.cell
def _(
    CKPT,
    SEED,
    ckpt_key,
    ckpt_path,
    lengths,
    mo,
    num_samples,
    p1,
    p2,
    pickle,
    shots,
    sizes,
):
    cached = {}
    for _n in sizes:
        _ckpt = ckpt_path(CKPT, **ckpt_key(_n, p1, p2, shots, num_samples, lengths, SEED))
        if _ckpt.exists():
            _res = pickle.loads(_ckpt.read_bytes())
            # Guard against a hash collision / hand-edited file: verify provenance.
            if _res.get("params", {}).get("p2") != p2:
                raise RuntimeError(f"Checkpoint {_ckpt.name} has p2={_res.get('params', {}).get('p2')} but current p2={p2}. Delete it and rerun.")
            cached[_n] = _res
    missing = [_n for _n in sizes if _n not in cached]
    mo.md(f"Cached lattices: **{sorted(cached) or 'none'}**. Missing: **{missing or 'none'}** (from `{CKPT}`).")
    return cached, missing


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Build and run the experiments
    """)
    return


@app.cell(hide_code=True)
def _(lengths, missing, mo, num_samples, shots):
    run_btn = mo.ui.run_button(label="Run missing lattices", kind="danger", disabled=not missing)
    mo.vstack(
        [
            mo.callout(
                mo.md(
                    f"**Cost per lattice:** {len(lengths) * num_samples} circuits × {shots} shots on a stabilizer simulation "
                    f"plus a max-weight matching per circuit. Hours for the default sizes. Each finished lattice is checkpointed."
                ),
                kind="warn",
            ),
            run_btn,
        ]
    )
    return (run_btn,)


@app.cell
def _(
    CKPT,
    SEED,
    STAB_BASIS_RZ,
    cached,
    ckpt_key,
    ckpt_path,
    custom_name_mapping,
    evaluate_bot,
    extract_mi,
    gc,
    lattice_backend,
    lengths,
    missing,
    mo,
    num_samples,
    p1,
    p2,
    pickle,
    run_btn,
    run_topo,
    shots,
):
    mo.stop(missing and not run_btn.value, mo.md(f"*Click **Run missing lattices** to simulate {missing}.*"))
    results = dict(cached)
    log = []
    for n in mo.status.progress_bar(missing, title="Lattices", subtitle="stabilizer simulation + bot"):
        _backend, _num_qubits, _legit = lattice_backend(n, STAB_BASIS_RZ, p1, p2, SEED, custom_name_mapping)
        _exp, _rb = run_topo(_backend, _legit, lengths, num_samples, shots, SEED)
        _mi = extract_mi(_exp, _rb, _legit)
        results[n] = evaluate_bot(_mi, _exp, _legit, _num_qubits, lengths)
        results[n]["params"] = ckpt_key(n, p1, p2, shots, num_samples, lengths, SEED)
        _ckpt = ckpt_path(CKPT, **results[n]["params"])
        _ckpt.parent.mkdir(exist_ok=True)
        _ckpt.write_bytes(pickle.dumps(results[n]))
        log.append(f"{n}x{n}: ran {len(_exp._pairs)} circuits, saved {_ckpt.name}")
        del _exp, _rb, _mi, _backend
        gc.collect()
    mo.md("  \n".join(log) if log else "*All lattices loaded from checkpoints.*")
    return (results,)


@app.cell
def _(mo, results, sizes):
    _rows = [
        {"lattice": f"{n}x{n}", **{f"L={L}": f"{p:.3f}" for L, p in zip(results[n]["lengths"], results[n]["p_bot_pairs"])}}
        for n in sizes
    ]
    mo.ui.table(_rows, selection=None, label="P(bot = pairs) per lattice and length")
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Final comparison plots

    Left: `1-P(pairs)`. Right: `1-P(topo)`.
    """)
    return


@app.cell
def _(mo, plot_one_minus_p, results, sizes):
    _pairs = plot_one_minus_p({f"L={n}": (results[n]["lengths"], results[n]["p_bot_pairs"]) for n in sizes}, r"1-$P(\mathrm{pairs})$")
    _topo = plot_one_minus_p({f"L={n}": (results[n]["lengths"], results[n]["p_mode_topo"]) for n in sizes}, r"1-$P(\mathrm{topo})$")
    mo.hstack([_pairs, _topo], widths="equal", wrap=True)
    return


if __name__ == "__main__":
    app.run()
