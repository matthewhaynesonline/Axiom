import numpy as np
import polars as pl


######
# Normalization
######
def zscore(s: pl.Series) -> pl.Series:
    """
    https://en.wikipedia.org/wiki/Standard_score

    Shifting and scaling an array of numbers so that the average (mean) becomes exactly 0,
    and the "average spread" (standard deviation) becomes exactly 1.

    1. Given [5, 10, 15], subtract the mean from every element (Broadcast)
        - https://numpy.org/doc/stable/user/basics.broadcasting.html
    2. [-5, 0, 5], then divide that (every result) by the standard deviation
    3. [-1.0, 0.0, 1.0]
    """
    return (s - s.mean()) / s.std()


def zscore_np(arr: np.ndarray) -> np.ndarray:
    """
    https://en.wikipedia.org/wiki/Standard_score
    """
    std = arr.std()

    if std == 0:
        return np.zeros_like(arr)

    return (arr - arr.mean()) / std


def minmax(s: pl.Series) -> pl.Series:
    """
    https://en.wikipedia.org/wiki/Feature_scaling#Rescaling_(min-max_normalization)

    A simple linear interpolation that maps an arbitrary range of numbers into a strict [0.0, 1.0] bounds.

    1. Subtract the min from every element
    2. Divide those by the max minus the min
    """
    return (s - s.min()) / (s.max() - s.min())  # type: ignore


def tanh_scale_np(arr: np.ndarray, scale: float = 0.6) -> np.ndarray:
    """
    https://en.wikipedia.org/wiki/Hyperbolic_functions

    Gracefully maps any infinite float into a strict boundary without mathematically destroying
    the spacing of the normal, everyday values in the middle of the pack

    Soft-clip via tanh after zscore.  Avoids the hard ±0.5 bounds produced by
    zscore+minmax, which compress all other terms when one outlier dominates the
    normalization range (e.g. Anarchism pinning Qwen to -0.5 and squashing the
    rest of the scale).

    Output range is the open interval (-0.5, 0.5) — never exactly ±0.5.

    scale controls tail compression:
        0.4  — aggressive (±2σ -> ±0.38)
        0.6  — default    (±2σ -> ±0.46)
        0.8  — loose      (±2σ -> ±0.50, approaches minmax behaviour)

    1. Calculate the Z-score for the entire array (centers to 0, scales spread to 1)
    2. Multiply every Z-score by the scale factor (controls how quickly we hit the edges)
    3. Apply the tanh function to squash all values into a (-1.0, 1.0) range
    4. Divide every result by 2 to shrink the final bounds to strictly (-0.5, 0.5)
    """
    z = zscore_np(arr)

    return np.tanh(z * scale) / 2
