from pybaselines.utils import Baseline, utils
import numpy as np

x = np.linspace(1, 1000, 1000)
# a measured signal containing several Gaussian peaks
signal = (
    utils.gaussian(x, 4, 120, 5)
    + utils.gaussian(x, 5, 220, 12)
    + utils.gaussian(x, 5, 350, 10)
    + utils.gaussian(x, 7, 400, 8)
    + utils.gaussian(x, 4, 550, 6)
    + utils.gaussian(x, 5, 680, 14)
    + utils.gaussian(x, 4, 750, 12)
    + utils.gaussian(x, 5, 880, 8)
)
true_baseline = 2 + 10 * np.exp(-x / 400)
noise = np.random.default_rng(1).normal(0, 0.2, x.size)
y = signal + true_baseline + noise

baseline_fitter = Baseline(x_data=x)


def test_subtract_polynomial():
    actual_bkg, actual_params = baseline_fitter.modpoly(y, poly_order=3)
    pass
