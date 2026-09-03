"""Repository-relative paths, valid from any working directory."""

from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
RUNS = REPO / "runs"
CKPT = REPO / "topo_ckpt"
