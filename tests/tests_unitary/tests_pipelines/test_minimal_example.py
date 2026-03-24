# -*- coding: utf-8 -*-
"""
Created on Thu Mar 20 12:04:09 2026

@authors:   Jonas Hartmann @ Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Unit tests against `minimal_example.py`.
"""

import os
import warnings
from time import sleep

import numpy as np
import pytest

from dystrack.pipelines import minimal_example


def test_analyze_image_3D_intensity_success(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-pllo_cyto_880_prescan.czi"

    # Expectations
    expected_output = ["12.8844", "95.4037", "93.8372", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (25, 200, 200)",
        "Resulting coords (zyx): 12.8844, 95.4037, 93.8372",
    ]

    # For performance, patch loading's sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    output = minimal_example.analyze_image(
        os.path.join(testpath, fname), verbose=True
    )
    output = list(output)
    output[:3] = [f"{c:.4f}" for c in output[:3]]
    stdout = capsys.readouterr().out

    # Compare results
    assert output == expected_output
    for eso in expected_stdouts:
        assert eso in stdout


def test_analyze_image_2D_intensity_success(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-pllo_cyto_880_prescan2D.tif"

    # Expectations
    expected_output = ["0.0000", "94.8775", "102.7212", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (200, 200)",
        "Resulting coords (zyx): 0.0000, 94.8775, 102.7212",
    ]

    # For performance, patch loading's sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    output = minimal_example.analyze_image(
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
        "dystrack.pipelines.minimal_example.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((1, 1, 1, 1, 1)),
    )
    with pytest.raises(IOError) as err:
        minimal_example.analyze_image("test_path.tiff")
    assert "Image dimensionality >4" in str(err)

    # Too few dimensions
    mocker.patch(
        "dystrack.pipelines.minimal_example.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((1,)),
    )
    with pytest.raises(IOError) as err:
        minimal_example.analyze_image("test_path.tiff")
    assert "Image dimensionality <2" in str(err)

    # Too few dimensions with channel
    mocker.patch(
        "dystrack.pipelines.minimal_example.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((1, 1)),
    )
    with pytest.raises(IOError) as err:
        minimal_example.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dimensionality is <3!" in str(err)


def test_analyze_image_warnings_inputchecks(mocker):
    # Note: Error wrapping is done for perf (to halt function at warning)

    # Channel given but large first dimension
    mocker.patch(
        "dystrack.pipelines.minimal_example.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((10, 1, 1, 1)),
    )
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            minimal_example.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dim 0 is of size 10!" in str(err)

    # Conversion to 8bit
    mocker.patch(
        "dystrack.pipelines.minimal_example.robustly_load_image_after_write",
        wraps=lambda fp, await_write: np.zeros((3, 5, 5), dtype=np.uint16),
    )
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            minimal_example.analyze_image("test_path.tiff")
    assert "Image converted down to 8bit using min-max scaling!" in str(err)
