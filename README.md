# Mirror Quantum Awesomeness [![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20928060.svg)](https://doi.org/10.5281/zenodo.20928060)



Mirror randomized benchmarking (MRB) is an established technique that provides a global error metric at the scale of a whole QPU. To expand upon this we introduce Mirror Quantum Awesomeness (MQA), a hybrid protocol that adds a structured entangling layer to MRB circuits. This enables per-edge correlation dynamics to be tracked via mutual information while preserving the MRB infidelity estimate. The resulting analysis of the injected entangled pairs locates a critical circuit depth, beyond which rudimentary error mitigation techniques can be expected to fail. A topological variant, Topological MQA, supplies a second critical depth via a decoder based on the surface-code decoding problem. Both are validated in simulation and demonstrated on the 156-qubit ibm fez and ibm kingston processors, where MQA closely agrees with MRB on the entanglement infidelity and the critical depth for ibm fez is found to be ∼ 50.

## Data

Experiments on IBM Quantum hardware with over 100 qubits are used to validate and test the method, as well as to benchmark the hardware. Plus, simulation on custom error model on the custom coupling map is also used.

__Data Contact__

* **Haripriya Pettugani <priya@mothquantum.com>** and **María Aguado-Yáñez <maria@mothquantum.com>** - Contact for inqueries regarding `ibm_fez` data and MQA metrics
* **Astryd Park <astryd@mothquantum.com>** - Contact for inqueries regarding Topological analysis and GitHub repository

If one wants to use live QPU data, they must use their **IBM Quantum Platform** API key, CRN and their username in `tmqa-hardware.ipynb`. The way of getting this information can be referenced in the official website.

## Requirements

1. `uv` is required to install code dependencies to your system and run the code locally. To accomplish it, you must clone this repository on your local first.

```
git clone https://github.com/moth-quantum/mqa-data.git
```

2. Install `uv` [here](https://docs.astral.sh/uv/getting-started/installation/) while following the steps.

3. Then, run this command **in the repository's local location** to set up the virtual environment, and install all dependencies.

```
uv sync
```

## Notebooks (marimo)

Every notebook also exists as a [marimo](https://marimo.io) notebook under `notebooks/`. Parameters are UI controls, expensive runs and hardware submissions sit behind a button, and offline data paths work without an IBM account.

```
uv sync
uv run marimo edit notebooks/        # or: task edit
```

| Jupyter | marimo | Runs offline by default |
|---|---|---|
| `Comparision_EPdecay.ipynb` | `notebooks/comparison_epdecay.py` | yes (seconds) |
| `mrb-custom.ipynb` | `notebooks/mrb_custom.py` | yes (seconds) |
| `mqa-custom.ipynb` | `notebooks/mqa_custom.py` | button (Aer simulation) |
| `mqa-stab.ipynb` | `notebooks/mqa_stab.py` | button (156-qubit stabilizer simulation) |
| `mrb-stab.ipynb` | `notebooks/mrb_stab.py` | button (30-qubit stabilizer simulation) |
| `mqa-hardware.ipynb` | `notebooks/mqa_hardware.py` | needs IBM credentials |
| `mrb-hardware.ipynb` | `notebooks/mrb_hardware.py` | needs IBM credentials |
| `tmqa-simul.ipynb` | `notebooks/tmqa_simul.py` | button (hours); checkpoints in `topo_ckpt/` |
| `tmqa-fake.ipynb` | `notebooks/tmqa_fake.py` | yes (loads `FakeMiami/*.pkl`); re-run behind a button |
| `tmqa-hardware.ipynb` | `notebooks/tmqa_hardware.py` | yes (loads `ibm_miami/*/*_data.pkl`); live run needs credentials |
| `CustomNoisyBackend/.../noisy-backend-angle-graph.ipynb` | `notebooks/noisy_backend_angle_graph.py` | yes |
| `StabilizerBackend/.../error_rates_graph.ipynb` | `notebooks/stab_error_rates_graph.py` | yes |

IBM credentials are entered in a password field inside the hardware notebooks and used for that session only; nothing is written to `~/.qiskit`. Anything a notebook saves goes under `runs/` (git-ignored). Shared helpers live in `mqa_common/`.

`task docker:test` builds an image and runs every notebook headlessly with networking disabled, which is the check that they open and execute.

## Publications

**Update ArXiv link underneath!**

 __QPU-scale randomized benchmarking via Bell-pair injection__<br />
Pettugani, H†, Aguado-Yáñez M†, Park A†, Bultrini D, Wootton James R. <br />
2026 ArXiv Preprint. DOI: https://doi.org/10.48550/arXiv.2606.20123

## Authors

* **Haripriya Pettugani** - [GitHub](https://github.com); priya@mothquantum.com ^
* **María Aguado-Yáñez** - [GitHub](https://github.com); [LinkedIn](https://www.linkedin.com/in/mariaaguadoyan/); maria@mothquantum.com ^
* **Astryd Park** - [GitHub](https://github.com/artreadcode); [LinkedIn](https://linkedin.com/in/astrydpark); astryd@mothquantum.com ^
* **Daniel Bultrini** - [GitHub](https://github.com); daniel@mothquantum.com
* **James R. Wootton** - [GitHub](https://github.com/quantumjim); james@mothquantum.com

† Haripriya Pettugani, María Aguado-Yáñez and Astryd Park contributed equally to this work.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE.txt](LICENSE.txt) file for details.

## Acknowledgments

This work was supported as a part of NCCR SPIN, a National Centre of Competence in Research, funded by the Swiss National Science Foundation (grant number 225153).

The authors acknowledge the use of IBM Quantum Credits via the IBM Quantum Startups Program for this work. The views expressed are those of the authors and do not reflect the official policy or position of IBM or the IBM Quantum Platform team.

This repository includes the Moth fork of `qiskit_device_benchmarking` library available [here](https://github.com/moth-quantum/qiskit-device-benchmarking/tree/main). This is derived from the qiskit-community version [here](https://github.com/qiskit-community/qiskit-device-benchmarking).
