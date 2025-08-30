# import pytest
from chromatography_processing.read_metrohm_ic_txt_files import (
    read_metrohm_ic_txt_file,
)
from pathlib import Path

datapath = (
    Path(__file__).parent.parent
    / "tests"
    / "metrohm_ic_test_files"
    / "ancat_chromatogram.txt"
)


def test_first_data_point_is_correct():
    actual_anion, actual_cation = read_metrohm_ic_txt_file(datapath)
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
