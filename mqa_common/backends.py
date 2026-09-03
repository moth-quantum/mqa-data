"""Simulated backends shared by the MQA/MRB notebooks."""

import numpy as np
from qiskit.providers.fake_provider import GenericBackendV2
from qiskit.quantum_info import Operator
from qiskit.transpiler import CouplingMap, Target
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

STAB_BASIS_RZ = ["id", "h", "x", "y", "z", "rz", "cx"]
STAB_BASIS_S = ["id", "h", "x", "y", "z", "s", "cx"]


class NoisyBackend(GenericBackendV2):
    """GenericBackendV2 with uniform depolarizing rates p1 (1Q) and p2 (2Q)."""

    def __init__(
        self,
        num_qubits: int,
        basis_gates: list[str] | None = None,
        coupling_map: list[list[int]] | None = None,
        p1: float = 0.0,
        p2: float = 0.0,
    ):
        self.p = (p1, p2)
        super().__init__(
            num_qubits,
            basis_gates,
            coupling_map=coupling_map,
            noise_info=(p1 > 0 or p2 > 0),
        )

    def _get_noise_defaults(self, name: str, num_qubits: int) -> tuple:
        if name in ["delay", "reset"]:
            return (self.p[0], self.p[0])
        if num_qubits == 1:
            return (0, 0, self.p[0], self.p[0])
        return (0, 0, self.p[1], self.p[1])


def legacy_rz_operator(angle: float) -> Operator:
    # Kept verbatim from mqa-stab / tmqa-simul: this matrix is RX(angle), not RZ.
    # Aer's stabilizer method dispatches on the gate *name*, so the mapping only
    # gives the Target an instruction identity; preserved so results stay comparable.
    return Operator(
        [
            [np.cos(angle / 2), -1j * np.sin(angle / 2)],
            [-1j * np.sin(angle / 2), np.cos(angle / 2)],
        ]
    )


def diagonal_rz_operator(angle: float) -> Operator:
    return Operator(np.array([[np.exp(-1j * angle / 2), 0], [0, np.exp(1j * angle / 2)]]))


_FIXED = {
    "id": Operator(np.eye(2)),
    "h": Operator(np.array([[1, 1], [1, -1]]) / np.sqrt(2)),
    "x": Operator(np.array([[0, 1], [1, 0]])),
    "y": Operator(np.array([[0, -1j], [1j, 0]])),
    "z": Operator(np.array([[1, 0], [0, -1]])),
    "s": Operator(np.array([[1, 0], [0, 1j]])),
    "cx": Operator(np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 0, 1], [0, 0, 1, 0]])),
}


def standard_name_mapping(basis_gates: list[str], rz_operator: Operator | None = None) -> dict:
    mapping = {g: _FIXED[g] for g in basis_gates if g in _FIXED}
    if "rz" in basis_gates:
        if rz_operator is None:
            raise ValueError("basis includes 'rz'; pass rz_operator")
        mapping["rz"] = rz_operator
    return mapping


def depolarizing_noise_model(basis_gates: list[str], p1: float, p2: float) -> NoiseModel:
    model = NoiseModel()
    err1, err2 = depolarizing_error(p1, 1), depolarizing_error(p2, 2)
    for gate in basis_gates:
        model.add_all_qubit_quantum_error(err2 if gate == "cx" else err1, gate)
    return model


def build_stabilizer_backend(
    num_qubits: int,
    coupling_map: CouplingMap,
    basis_gates: list[str],
    p1: float,
    p2: float,
    seed: int,
    custom_name_mapping: dict | None = None,
) -> AerSimulator:
    target = Target.from_configuration(
        num_qubits=num_qubits,
        basis_gates=basis_gates,
        coupling_map=coupling_map,
        custom_name_mapping=custom_name_mapping,
    )
    noisy = p1 > 0 or p2 > 0
    return AerSimulator(
        method="stabilizer",
        noise_model=depolarizing_noise_model(basis_gates, p1, p2) if noisy else None,
        target=target,
        max_parallel_threads=0,
        max_parallel_experiments=0,
        seed_simulator=seed,
    )
