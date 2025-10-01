# -*- coding: utf-8 -*-
"""
Created on Mon Jul 07 19:48:19 2025

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Unit tests against `lateral_line_organ.py`.
"""

import os
import warnings
from time import sleep

import numpy as np
import pytest

from dystrack.pipelines import lateral_line_organ


def test_analyze_image_3D_success(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-pllo_880_prescan.czi"

    # Expectations
    expected_output = ["12.6445", "96.9214", "91.4378", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (25, 200, 200)",
        "Detected treshold: 111",
        "Resulting coords (zyx): 12.6445, 96.9214, 91.4378",
    ]

    # For performance, patch loading's sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    output = lateral_line_organ.analyze_image(
        os.path.join(testpath, fname), verbose=True
    )
    output = list(output)
    output[:3] = [f"{c:.4f}" for c in output[:3]]
    stdout = capsys.readouterr().out

    # Compare results
    assert output == expected_output
    for eso in expected_stdouts:
        assert eso in stdout


def test_analyze_image_2D_success(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-pllo_880_prescan2D.tif"

    # Expectations
    expected_output = ["0.0000", "96.1637", "91.7534", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (200, 200)",
        "Detected treshold: 103",
        "Resulting coords (zyx): 0.0000, 96.1637, 91.7534",
    ]

    # For performance, patch loading's sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    output = lateral_line_organ.analyze_image(
        os.path.join(testpath, fname), verbose=True
    )
    output = list(output)
    output[:3] = [f"{c:.4f}" for c in output[:3]]
    stdout = capsys.readouterr().out

    # Compare results
    assert output == expected_output
    for eso in expected_stdouts:
        assert eso in stdout


def test_analyze_image_errors_dimchecks(mocker):

    # Too many dimensions
    mocker.patch(
        "dystrack.pipelines.lateral_line_organ.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((1, 1, 1, 1, 1)),
    )
    with pytest.raises(IOError) as err:
        lateral_line_organ.analyze_image("test_path.tiff")
    assert "Image dimensionality >4" in str(err)

    # Too few dimensions
    mocker.patch(
        "dystrack.pipelines.lateral_line_organ.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((1,)),
    )
    with pytest.raises(IOError) as err:
        lateral_line_organ.analyze_image("test_path.tiff")
    assert "Image dimensionality <2" in str(err)

    # Too few dimensions with channel
    mocker.patch(
        "dystrack.pipelines.lateral_line_organ.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((1, 1)),
    )
    with pytest.raises(IOError) as err:
        lateral_line_organ.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dimensionality is <3!" in str(err)

    # Channel given but large first dimension
    mocker.patch(
        "dystrack.pipelines.lateral_line_organ.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((10, 1, 1, 1)),
    )
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            lateral_line_organ.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dim 0 is of size 10!" in str(err)


def test_analyze_image_errors_nothresh(mocker):

    mocker.patch(
        "dystrack.pipelines.lateral_line_organ.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((100, 100), dtype=np.uint8),
    )
    with pytest.raises(Exception) as err:
        lateral_line_organ.analyze_image("test_path.tiff")
    assert "THRESHOLD DETECTION FAILED" in str(err)
