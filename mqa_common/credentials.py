"""IBM Quantum Runtime access without touching ~/.qiskit."""

from qiskit_ibm_runtime import QiskitRuntimeService


def connect(token: str = "", instance: str = "", channel: str = "ibm_quantum_platform"):
    """Return (service, message). service is None when no usable credentials exist.

    A non-empty token is used directly for this process only; nothing is saved.
    With no token, previously saved default credentials are tried.
    """
    try:
        if token:
            service = QiskitRuntimeService(channel=channel, token=token, instance=instance or None)
            return service, f"Connected with the supplied token ({channel})."
        service = QiskitRuntimeService()
        return service, "Connected with saved default credentials."
    except Exception as exc:  # noqa: BLE001 - surfaced to the UI as text
        if not token:
            return None, "No IBM Quantum credentials. Enter a token above to use hardware."
        return None, f"Could not connect: {type(exc).__name__}: {exc}"
