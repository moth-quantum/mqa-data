import os
import random

import numpy as np


def seed_all(seed: int) -> int:
    """Seed Python, NumPy and the hash seed. Returns `seed` so callers can chain on it."""
    os.environ["PYTHONHASHSEED"] = str(seed)
    random.seed(seed)
    np.random.seed(seed)
    return seed
