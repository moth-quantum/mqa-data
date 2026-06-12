# Mirror Quantum Awesomeness

Quantum processing units now routinely exceed 100 qubits, but scalable performance assessment remains challenging, particularly for guiding near-term algorithms. Mirror Randomized Benchmarking provides one way to estimate QPU-scale fidelity by using randomized mirror circuits with Pauli twirls and state preparations, yielding average-layer infidelity via the exponential decay of the effective polarization. However, a primary disadvantage of this approach is the extensive sampling overhead that arises as system size increases. To address this, a novel variant of Mirror Randomized Benchmarking (MRB) is introduced in which circuits generate a set of entangled pairs rather than returning a single bit string. This modification allows the extraction of the same metrics as standard MRB while enabling alternative analyses with constant overhead, providing deeper insights into the performance of near-term quantum algorithms.

## Data

Experiments on IBM Quantum hardware with over 100 qubits are used to validate and test the method, as well as to benchmark the hardware. Plus, simulation on custom error model on the custom coupling map is also used.

__Data Contact__

* **Haripriya Pettugani <priya@mothquantum.com>** and **María Aguado-Yáñez <maria@mothquantum.com** - Contact for inqueries regarding `ibm_fez` data and MQA metrics
* **Astryd Park <astryd@mothquantum.com>** - Contact for inqueries regarding Topological analysis and GitHub repository

Most scripts / analysis can be left as they often do not take up substantial amounts of space, so it is important to describe in detail how data should be handled.

## Getting Started

`uv` is recommended to install this repository to your system and run the code locally. To accomplish it, you must clone this repository on your local first.

```
git clone https://github.com/moth-quantum/mqa-data.git
```

Then, run this command in the repository's local location to set up the virtual environment, and install all dependencies. If uv is not installed, this command will install it for you. (Just in case, after installation, run this once more.)

```
uv sync
```

### Requirements

A step by step series of examples that tell you how to get a development/analysis env running

Say what the step will be

```
Give the example
```

And repeat

```
until finished
```

End with an example of getting some data out of the system or using. It is also worth listing what the requirements are.

## Publications

Add ArXiv link underneath!

 __The genetic basis of natural variation in Caenorhabditis elegans telomere length__<br />
Cook DE, Zdraljevic S, Tanny RE, Seo B, Riccardi DD, Noble LM, Rockman MV, Alkema MJ, Braendle C, Kammenga JE, Wang J, Kruglyak L, Fe ́ lix MA, Lee J, Andersen EC. <br />
2016. Genetics 204:371–383. DOI: https://doi.org/10.1534/genetics.116. 191148, PMID: 27449056

## Contributing

Details regarding how to contribute. Coding style conventions, use of tests, etc.

## Notes

Additional notes / precatuions / etc. to make users aware of.

## Authors

List all authors, their contributions, and how to contact; Preferably an internal and external form of contact.

* **Daniel E. Cook** - *Initial work* - [danielecook](https://github.com/danielecook); danielecook@gmail.com

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Hat tip to anyone whose code was used
* Inspiration
* etc