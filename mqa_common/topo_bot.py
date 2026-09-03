"""Topological MQA helpers: lattice backends, the pairing bot, checkpoints."""

import hashlib
import json
import pickle
from collections import defaultdict
from pathlib import Path

import networkx as nx
import numpy as np

from qiskit_device_benchmarking.bench_code.mrb import (
    MirrorQATopo,
    QuantumAwesomeness,
    TopoUtil,
)

from .backends import build_stabilizer_backend


def get_topo_mode(topo_full, fake_qubits) -> str:
    """f2f if the fake qubits paired together (or stayed unpaired); f2g otherwise."""
    fake_pairs = [p for p in topo_full if any(q in fake_qubits for q in p)]
    if not fake_pairs:
        return "f2f"
    for p in fake_pairs:
        if all(q in fake_qubits for q in p):
            return "f2f"
    return "f2g"


def lattice_backend(n: int, basis_gates, p1, p2, seed, custom_name_mapping, m: int | None = None):
    """(backend, num_qubits, legit_qubits) for an n x m genuine lattice plus 2 fake qubits."""
    cmap = TopoUtil.makeCouple(n, m or n, 2, "ibm")
    num_qubits = len(list(cmap.physical_qubits))
    legit_qubits = n * (m or n)
    backend = build_stabilizer_backend(
        num_qubits, cmap, basis_gates, p1, p2, seed, custom_name_mapping=custom_name_mapping
    )
    return backend, num_qubits, legit_qubits


def run_topo(
    backend,
    legit_qubits: int,
    lengths,
    num_samples: int,
    shots: int,
    seed: int,
    *,
    ffw: float | None = None,
    two_qubit_gate_density: float = 0.5,
    mode: str = "random",
    initial_entangling_angle: float = np.pi / 2,
    optimization_level: int | None = None,
):
    kwargs = dict(
        lengths=lengths,
        sampling_algorithm="topo",
        mode=mode,
        backend=backend,
        two_qubit_gate_density=two_qubit_gate_density,
        num_samples=num_samples,
        initial_entangling_angle=initial_entangling_angle,
        seed=seed,
    )
    if ffw is not None:
        kwargs["ffw"] = ffw
    exp = MirrorQATopo(range(legit_qubits), **kwargs)
    exp.set_run_options(shots=shots)
    if optimization_level is not None:
        exp.set_transpile_options(optimization_level=optimization_level)
    rb_data = exp.run()
    rb_data.block_for_results()
    return exp, rb_data


def extract_mi(exp, rb_data, legit_qubits: int):
    legit_cmap = exp.backend.coupling_map.reduce(range(legit_qubits))
    return QuantumAwesomeness(legit_cmap).mutual_info(rb_data.data())


def evaluate_bot(mi, exp, legit_qubits: int, num_qubits: int, lengths, acc: float | None = None) -> dict:
    """Score a max-weight-matching bot against the injected pairs.

    acc=None demands the exact pair set (tmqa-simul); a float accepts when at least
    acc * |truth| of the true pairs were recovered (tmqa-fake / tmqa-hardware).
    """
    half = legit_qubits // 2
    fake_qubits = set(range(legit_qubits, num_qubits))
    num_lengths = len(lengths)
    mode_ok, pairs_ok, totals = defaultdict(int), defaultdict(int), defaultdict(int)

    for i, info in enumerate(mi):
        length = lengths[i % num_lengths]
        topo_mode = get_topo_mode(exp._topo_outcomes[i], fake_qubits)

        graph = nx.Graph()
        for (u, v), w in info.items():
            graph.add_edge(u, v, weight=w)
        raw_guess = nx.max_weight_matching(graph, maxcardinality=False, weight="weight")
        bot_pairs = {tuple(sorted(p)) for p in raw_guess}
        bot_mode = "f2f" if len(bot_pairs) == half else "f2g"
        truth = {tuple(sorted(p)) for p in exp._pairs[i]}

        mode_ok[length] += int(bot_mode == topo_mode)
        if acc is None:
            pairs_ok[length] += int(bot_pairs == truth)
        else:
            pairs_ok[length] += int(len(bot_pairs & truth) >= acc * len(truth))
        totals[length] += 1

    ordered = sorted(lengths)
    return {
        "lengths": ordered,
        "p_mode_topo": [mode_ok[l] / totals[l] for l in ordered],
        "p_bot_pairs": [pairs_ok[l] / totals[l] for l in ordered],
    }


def dead_pairs(backend, threshold: float = 0.5):
    """CZ edges whose calibrated error is >= threshold. Returns (stats, [(edge, err)])."""
    cz = {
        tuple(sorted(q)): p.error
        for q, p in backend.target["cz"].items()
        if q and p and p.error is not None
    }
    errs = np.array(list(cz.values()))
    stats = {"median": float(np.median(errs)), "mean": float(errs.mean()), "max": float(errs.max())}
    dead = sorted((e, err) for e, err in cz.items() if err >= threshold)
    return stats, dead


def ckpt_key(n, p1, p2, shots, num_samples, lengths, seed) -> dict:
    return dict(n=n, p1=p1, p2=p2, shots=shots, num_samples=num_samples, lengths=list(lengths), seed=seed)


def ckpt_path(ckpt_dir: Path, **key) -> Path:
    # Same md5 recipe as the original notebook so existing topo_ckpt files stay valid.
    digest = hashlib.md5(json.dumps(key, sort_keys=True).encode()).hexdigest()[:8]
    return ckpt_dir / f"lattice_{key['n']}_p2-{key['p2']:g}_{digest}.pkl"


def save_topo_pickle(path: Path, exp, rb_data, *, lengths, num_samples, num_qubits, shots, seed) -> Path:
    """Write the ibm_miami/<job>/<job>_data.pkl layout consumed by load_saved_job."""
    entries = rb_data.data()
    blob = {
        "counts": [e["counts"] for e in entries],
        "metadata": [e["metadata"] for e in entries],
        "topo_outcomes": exp._topo_outcomes,
        "singles": exp._singles,
        "pairs": exp._pairs,
        "lengths": list(lengths),
        "num_samples": num_samples,
        "num_qubits": num_qubits,
        "shots": shots,
        "seed": seed,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(pickle.dumps(blob))
    return path


class LoadedExp:
    """Minimal stand-in for MirrorQATopo built from a saved pickle."""

    class _Backend:
        pass

    def __init__(self, blob, coupling_map):
        self._pairs = blob["pairs"]
        self._topo_outcomes = blob["topo_outcomes"]
        self._singles = blob["singles"]
        self.backend = self._Backend()
        self.backend.coupling_map = coupling_map


class LoadedRB:
    """Minimal stand-in for ExperimentData built from a saved pickle."""

    def __init__(self, blob, job_id):
        self._data = [{"counts": c, "metadata": m} for c, m in zip(blob["counts"], blob["metadata"])]
        self.job_ids = [job_id]

    def data(self):
        return self._data


def load_saved_job(pkl_path: Path, coupling_map):
    """(exp, rb_data, blob) for a saved <job_id>_data.pkl."""
    blob = pickle.loads(Path(pkl_path).read_bytes())
    job_id = Path(pkl_path).name[: -len("_data.pkl")]
    return LoadedExp(blob, coupling_map), LoadedRB(blob, job_id), blob
