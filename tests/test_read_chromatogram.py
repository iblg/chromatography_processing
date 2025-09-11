# import pytest
from chromatography_processing.read_chromatogram import read_chromatogram
from pathlib import Path

datapath = (
    Path(__file__).parent.parent
    / "tests"
    / "metrohm_ic_test_files"
    / "ancat_chromatogram.txt"
)


def test_first_data_point_is_correct():
    data, ident, meas_time, types = read_chromatogram(datapath)
    actual_anion = data[0]
    actual_cation = data[1]
    actual_anion = actual_anion.iloc[0]
    actual_anion = (float(actual_anion["time"]), float(actual_anion["signal"]))
    actual_cation = actual_cation.iloc[0]
    actual_cation = (
        float(actual_cation["time"]),
        float(actual_cation["signal"]),
    )

    expected_cation = (0.0, -1416.9126988467353)
    expected_anion = (0.0, 0.9642913942058996)
    assert actual_cation == expected_cation
    assert actual_anion == expected_anion
