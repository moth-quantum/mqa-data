# Mirror Quantum Awesomeness

Quantum processing units now routinely exceed 100 qubits, but scalable performance assessment
remains challenging, particularly for guiding near-term algorithms. Mirror Randomized Benchmark-
ing provides one way to estimate QPU-scale fidelity by using randomized mirror circuits with Pauli
twirls and state preparations, yielding average-layer infidelity via the exponential decay of the ef-
fective polarization. However, a primary disadvantage of this approach is the extensive sampling
overhead that arises as system size increases. To address this, a novel variant of MRB is introduced
in which circuits generate a set of entangled pairs rather than returning a single bit string. This
modification allows the extraction of the same metrics as standard MRB while enabling alternative
analyses with constant overhead, providing deeper insights into the performance of near-term quan-
tum algorithms. Experiments on IBM Quantum hardware with over 100 qubits are used to validate
and test the method, as well as to benchmark the hardware.
