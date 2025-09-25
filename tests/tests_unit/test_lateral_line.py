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
    assert True  # YAH!

    # Too many dimensions

    # Too few dimensions

    # Too few dimensions with channel

    # Channel given but large first dimension


def test_analyze_image_errors_nothresh(mocker):
    assert True  # TODO!
