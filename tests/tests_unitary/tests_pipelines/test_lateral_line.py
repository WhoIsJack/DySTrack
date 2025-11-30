# -*- coding: utf-8 -*-
"""
Created on Mon Jul 07 19:48:19 2025

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Unit tests against `lateral_line.py`.
"""

import os
import warnings
from time import sleep

import numpy as np
import pytest

from dystrack.pipelines import lateral_line


def test_analyze_image_3D_success(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-pllp_AXR_prescan.tiff"

    # Expectations
    expected_output = ["3.4705", "107.8477", "258.4000", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (9, 212, 512)",
        "Detected treshold: 13",
        "Resulting coords (zyx): 3.4705, 107.8477, 258.4000",
    ]

    # For performance, patch loading's sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    with pytest.warns(
        UserWarning,
        match="Image converted down to 8bit using min-max scaling!",
    ) as w:
        output = lateral_line.analyze_image(
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
    fname = "test-pllp_980_prescan2D.tif"

    # Expectations
    expected_output = ["0.0000", "106.7561", "348.0000", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (200, 500)",
        "Detected treshold: 11",
        "Resulting coords (zyx): 0.0000, 106.7561, 348.0000",
    ]

    # For performance, patch loading's sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    output = lateral_line.analyze_image(
        os.path.join(testpath, fname), verbose=True
    )
    output = list(output)
    output[:3] = [f"{c:.4f}" for c in output[:3]]
    stdout = capsys.readouterr().out

    # Compare results
    assert output == expected_output
    for eso in expected_stdouts:
        assert eso in stdout


def test_analyze_image_errors_inputchecks(mocker):

    # Too many dimensions
    mocker.patch(
        "dystrack.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((1, 1, 1, 1, 1)),
    )
    with pytest.raises(IOError) as err:
        lateral_line.analyze_image("test_path.tiff")
    assert "Image dimensionality >4" in str(err)

    # Too few dimensions
    mocker.patch(
        "dystrack.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((1,)),
    )
    with pytest.raises(IOError) as err:
        lateral_line.analyze_image("test_path.tiff")
    assert "Image dimensionality <2" in str(err)

    # Too few dimensions with channel
    mocker.patch(
        "dystrack.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((1, 1)),
    )
    with pytest.raises(IOError) as err:
        lateral_line.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dimensionality is <3!" in str(err)


def test_analyze_image_warnings_inputchecks(mocker):
    # Note: Error wrapping is done for perf (to halt function at warning)

    # Channel given but large first dimension
    mocker.patch(
        "dystrack.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((10, 1, 1, 1)),
    )
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            lateral_line.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dim 0 is of size 10!" in str(err)

    # Conversion to 8bit
    mocker.patch(
        "dystrack.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((3, 5, 5), dtype=np.uint16),
    )
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            lateral_line.analyze_image("test_path.tiff")
    assert "Image converted down to 8bit using min-max scaling!" in str(err)


def test_analyze_image_errors_nothresh(mocker):

    mocker.patch(
        "dystrack.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((100, 100), dtype=np.uint8),
    )
    with pytest.raises(Exception) as err:
        lateral_line.analyze_image("test_path.tiff")
    assert "THRESHOLD DETECTION FAILED" in str(err)
