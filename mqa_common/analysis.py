from qiskit_device_benchmarking.bench_code.mrb.mirror_rb_analysis import (
    MirrorRBAnalysis,
)


def effective_polarization(rb_data, analysis=None):
    """Run an Effective Polarization fit and block until the figure exists."""
    analysis = analysis or MirrorRBAnalysis()
    analysis.set_options(analyzed_quantity="Effective Polarization")
    result = analysis.run(rb_data)
    result.block_for_results()
    return result
