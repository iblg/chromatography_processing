import pytest
from chromatography_processing.fit_dataset import fit_dataset
import pandas as pd


t = [0, 1, 2, 3]
x = [0, 1, 2, 3]
y = [0, 1, 2, 3]
df = pd.DataFrame({"t": t, "x": x, "y": y})
ds = df.set_index("t")
ds = ds.to_xarray()


@pytest.mark.parametrize(
    "data",
    [
        df,
        None,
    ],
)
def test_fit_dataset_TypeError_if_not_passed_dataset(data):
    assert pytest.raises(TypeError, fit_dataset, data)


#
#
# time = [0, 1, 2]
# ion_type = ['cation', 'anion']
# measurement_time = [0, 1, 2]
# signal = [0, 1, 2]
# df1 = pd.DataFrame({'time': time,
#                     'ion_type': ion_type,
#                     'measurement_time': measurement_time,
#                     'signal': signal
#                     })
# df1 = df1.set_index(['time', 'ion_type', 'measurement_time'])
# ds_correct_coords = df1.to_xarray()
# @pytest.mark.parametrize(
#     "actual, expected",
#     [
#         ds, ds_correct_coords
#     ]
# )
# def test_fit_dataset_dims_correct(data, expected):
#     print()
#     actual =
#     assert actual == expected
#     # ds = xr.Dataset({'a': (['x', 'y'], [1, 2, 3])})
#     #
#     # assert pytest.raises(TypeError, fit_dataset(ds))


# def test_pass_two_ion_types_to_fit_dataset():
#     assert pytest.raises(TypeError, fit_dataset)

#
# def test_fit_chromatogram():
#     x = np.linspace(0, 100, 1000)
#     f1 = skewnorm(0.5, loc=10, scale=1).pdf(x)
#     df = pd.DataFrame({"time": x, "signal": f1})
#     chrom = Chromatogram(df)
#     chrom.show()
#     peaks = chrom.fit_peaks()
#     scores = chrom.assess_fit()
#     print(scores)
#     print(type(scores))
#     # result = fit_chromatogram(df)
#     # expected =
#     # fig, ax = plt.subplots()
#     # ax.plot(x, f1)
#     plt.show()

# assert actual == expected


# @pytest.mark.parametrize(
#     "a, b, expected",
#     [
#         # Test whether the dot product function works with 2D and 3D vectors
#         # C1: lists, expect correct float output
#         ([1, 2], [3, 4], 11.0),
#         ([1, 2, 3], [4, 5, 6], 32.0),
#         # C2: tuples, expect correct float output
#         ((1, 2), (3, 4), 11.0),
#         ((1, 2, 3), (4, 5, 6), 32.0),
#         # C3: numpy arrays, expect correct float output
#         (np.array([1, 2]), np.array([3, 4]), 11.0),
#         (np.array([1, 2, 3]), np.array([4, 5, 6]), 32.0),
#     ],
# )
# def test_dot_product(a, b, expected):
#     actual = functions.dot_product(a, b)
#     assert actual == expected
