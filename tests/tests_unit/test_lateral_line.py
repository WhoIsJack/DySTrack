# -*- coding: utf-8 -*-
"""
Created on Mon Jul 07 19:48:19 2025

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Unit tests against `lateral_line.py`.
"""

import os
import warnings

import pytest

import numpy as np

from mate.pipelines import lateral_line


def test_analyze_image_3D_success(capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-pllp_NSPARC_prescan.tiff"

    # Expectations
    expected_output = ["3.4705", "107.8477", "258.4000", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (9, 212, 512)",
        "Detected treshold: 13",
        "Resulting coords (zyx): 3.4705, 107.8477, 258.4000",
    ]

    # Run test
    with pytest.warns(
        UserWarning,
        match="Image converted down to 8bit using min-max scaling!",
    ) as w:
        output = lateral_line.analyze_image(
            os.path.join(testpath, fname),
            channel=None,
            show=False,
            verbose=True,
        )
    output = list(output)
    output[:3] = [f"{c:.4f}" for c in output[:3]]
    stdout = capsys.readouterr().out

    # Compare results
    assert output == expected_output
    for eso in expected_stdouts:
        assert eso in stdout


def test_analyze_image_2D_success(capsys):

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

    # Run test
    output = lateral_line.analyze_image(
        os.path.join(testpath, fname),
        channel=None,
        show=False,
        verbose=True,
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
        "mate.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp : np.zeros((1, 1, 1, 1, 1)))
    with pytest.raises(IOError) as err:
        lateral_line.analyze_image(
            "test_path.tiff", channel=None, show=False, verbose=True
        )
    assert "Image dimensionality >4" in str(err)

    # Too few dimensions
    mocker.patch(
        "mate.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp : np.zeros((1,)))
    with pytest.raises(IOError) as err:
        lateral_line.analyze_image(
            "test_path.tiff", channel=None, show=False, verbose=True
        )
    assert "Image dimensionality <2" in str(err)

    # Too few dimensions with channel
    mocker.patch(
        "mate.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp : np.zeros((1, 1)))
    with pytest.raises(IOError) as err:
        lateral_line.analyze_image(
            "test_path.tiff", channel=0, show=False, verbose=True
        )
    assert "CHANNEL given but image dimensionality is <3!" in str(err)

    # Channel given but large first dimension
    mocker.patch(
        "mate.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp : np.zeros((10, 1, 1, 1)))
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            lateral_line.analyze_image(
                "test_path.tiff", channel=0, show=False, verbose=True
            )
    assert "CHANNEL given but image dim 0 is of size 10!" in str(err)


def test_analyze_image_errors_nothresh(mocker):

    mocker.patch(
        "mate.pipelines.lateral_line.robustly_load_image_after_write",
        wraps=lambda fp : np.zeros((100, 100), dtype=np.uint8))
    with pytest.raises(Exception) as err:
        lateral_line.analyze_image(
            "test_path.tiff", channel=None, show=False, verbose=True
        )
    assert "THRESHOLD DETECTION FAILED" in str(err)

