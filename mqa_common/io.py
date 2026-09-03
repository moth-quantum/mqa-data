"""Persist experiment artefacts under runs/<job_id>/."""

import json
from pathlib import Path

import qiskit.qasm2


def save_json(obj, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj))
    return path


def save_figure(fig, path: Path, dpi: int = 300) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    return path


def save_job_bundle(
    out_root: Path,
    job_id: str,
    exp,
    *,
    num_qubits: int,
    seed: int | None = None,
    pairs: bool = True,
    angle: bool = False,
    density: bool = False,
) -> Path:
    """Write qubit count, seed, pairs, options and QASM2 circuits for a job."""
    out = out_root / job_id
    out.mkdir(parents=True, exist_ok=True)
    save_json({"num_qubits": num_qubits}, out / f"{job_id}_qubits.json")
    if seed is not None:
        save_json({"seed": seed}, out / f"{job_id}_seed.json")
    if pairs:
        save_json(exp._pairs, out / f"{job_id}_pairs.json")
    if angle:
        save_json({"initial_entangling_angle": exp._angles[0]}, out / f"{job_id}_angle.json")
    if density:
        save_json(
            {"two_qubit_gate_density": exp.experiment_options.two_qubit_gate_density},
            out / f"{job_id}_density.json",
        )
    for i, circ in enumerate(exp.circuits()):
        with open(out / f"circuit_{i}.json", "w") as fh:
            qiskit.qasm2.dump(circ, fh)
    return out
