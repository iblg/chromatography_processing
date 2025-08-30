import pandas as pd
from pybaselines import Baseline
import numpy as np


def find_custom_bc_baseline(
    data: pd.DataFrame,
    x: str = "time",
    y: str = "signal",
    crossover_index_number: int = 160,
    lam: float = 1e8,
    lam_flexible: float = 1e6,
    method: str = "arpls",
    sampling: int = 15,
) -> (np.ndarray, dict):
    """
    data: pd.DataFrame
    The data for which you want to find the baseline signal.

    x: str, default 'time'
    The name of the column in data which serves as the x-axis.
    Note: if x is not 'time', it currently causes problems with HPLC-py.
    It is recommended to name it 'time'.

    y: str
    The name of the column in data which serves as the y-axis.

    crossover_index_number: int, default 160

    lam: float, default 1e8

    lam_flexible: float, default 1e6

    method: str, default 'arpls'

    sampling: int, default 15

    Returns:
    bck: np.ndarray
    The data points of the baseline.

    params: dict
    The params of the baseline
    """
    x = data[x]
    y = data[y]
    crossover_index = np.argmin(abs(x - crossover_index_number))
    baseline_fitter = Baseline(x_data=x)

    bck, params = baseline_fitter.custom_bc(
        y,
        method,
        regions=([crossover_index, None],),
        sampling=sampling,
        method_kwargs={"lam": lam_flexible},
        lam=lam,
    )

    return bck, params
