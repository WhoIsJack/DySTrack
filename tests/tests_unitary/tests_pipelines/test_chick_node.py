# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 23:23:41 2024

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `chick_node.py`.
"""

import os
import warnings
from time import sleep

import numpy as np
import pytest

from mate.pipelines import chick_node


# Helper function
def analyze_image_success(
    mocker, capsys, testpath, fname, expected_output, expected_stdouts
):

    # For performance, patch loading's sleep
    mocker.patch(
        "mate.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Run test
    output = chick_node.analyze_image(
        os.path.join(testpath, fname), verbose=True
    )
    output = list(output)
    output[:3] = [f"{c:.4f}" for c in output[:3]]
    stdout = capsys.readouterr().out

    # Compare results
    assert output == expected_output
    for eso in expected_stdouts:
        assert eso in stdout


def test_analyze_image_3D_success_early(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-cnode_early_prescan.tiff"

    # Expectations
    expected_output = ["10.8574", "258.2661", "369.8943", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (21, 512, 512)",
        "Resulting coords (zyx): 10.8574, 258.2661, 369.8943",
    ]

    # Run test and compare results
    analyze_image_success(
        mocker, capsys, testpath, fname, expected_output, expected_stdouts
    )


def test_analyze_image_3D_success_late(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-cnode_late_prescan.tiff"

    # Expectations
    expected_output = ["10.4417", "269.4593", "373.6161", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (21, 512, 512)",
        "Resulting coords (zyx): 10.4417, 269.4593, 373.6161",
    ]

    # Run test and compare results
    analyze_image_success(
        mocker, capsys, testpath, fname, expected_output, expected_stdouts
    )


def test_analyze_image_3D_success_DEVTEMP(mocker, capsys):
    # DEV-TEMP: To be defactored after MATE2DySTrack rename!

    # Targets
    testpath = r"./tests/testdata/"
    fnames = [
        "test-chicknode1_node_HH4_ch3_ds_8bit.tif",
        "test-chicknode2_testrun1_000.tiff",
        "test-chicknode3_testrun1_031.tiff",
        "test-chicknode4_run20250130_042.tiff",
        "test-chicknode5_run20250130_043.tiff",
    ]

    # Expectations
    expected_outputs = [
        ["8.1780", "532.3575", "603.7036", "OK", {}],
        ["21.4710", "247.8483", "399.8783", "OK", {}],
        ["26.8514", "260.8954", "398.1514", "OK", {}],
        ["9.1176", "286.5968", "328.9029", "OK", {}],
        ["10.4417", "269.4593", "373.6161", "OK", {}],
    ]
    expected_stdouts = [
        [
            "Loaded image of shape: (20, 1024, 1024)",
            "Resulting coords (zyx): 8.1780, 532.3575, 603.7036",
        ],
        [
            "Loaded image of shape: (45, 512, 512)",
            "Resulting coords (zyx): 21.4710, 247.8483, 399.8783",
        ],
        [
            "Loaded image of shape: (45, 512, 512)",
            "Resulting coords (zyx): 26.8514, 260.8954, 398.1514",
        ],
        [
            "Loaded image of shape: (21, 512, 512)",
            "Resulting coords (zyx): 9.1176, 286.5968, 328.9029",
        ],
        [
            "Loaded image of shape: (21, 512, 512)",
            "Resulting coords (zyx): 10.4417, 269.4593, 373.6161",
        ],
    ]

    # Run tests and compare results
    for fname, eop, eos in zip(fnames, expected_outputs, expected_stdouts):
        analyze_image_success(mocker, capsys, testpath, fname, eop, eos)


def test_analyze_image_2D_success_early(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-cnode_early_prescan2D.tiff"

    # Expectations
    expected_output = ["0.0000", "261.3771", "349.0650", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (512, 512)",
        "Resulting coords (zyx): 0.0000, 261.3771, 349.0650",
    ]

    # Run test and compare results
    analyze_image_success(
        mocker, capsys, testpath, fname, expected_output, expected_stdouts
    )


def test_analyze_image_2D_success_late(mocker, capsys):

    # Targets
    testpath = r"./tests/testdata/"
    fname = "test-cnode_late_prescan2D.tiff"

    # Expectations
    expected_output = ["0.0000", "270.4000", "342.7758", "OK", {}]
    expected_stdouts = [
        "Loaded image of shape: (512, 512)",
        "Resulting coords (zyx): 0.0000, 270.4000, 342.7758",
    ]

    # Run test and compare results
    analyze_image_success(
        mocker, capsys, testpath, fname, expected_output, expected_stdouts
    )


def test_analyze_image_errors_dimchecks(mocker):

    # Too many dimensions
    mocker.patch(
        "mate.pipelines.chick_node.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((1, 1, 1, 1, 1)),
    )
    with pytest.raises(IOError) as err:
        chick_node.analyze_image("test_path.tiff")
    assert "Image dimensionality >4" in str(err)

    # Too few dimensions
    mocker.patch(
        "mate.pipelines.chick_node.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((1,)),
    )
    with pytest.raises(IOError) as err:
        chick_node.analyze_image("test_path.tiff")
    assert "Image dimensionality <2" in str(err)

    # Too few dimensions with channel
    mocker.patch(
        "mate.pipelines.chick_node.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((1, 1)),
    )
    with pytest.raises(IOError) as err:
        chick_node.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dimensionality is <3!" in str(err)

    # Channel given but large first dimension
    mocker.patch(
        "mate.pipelines.chick_node.robustly_load_image_after_write",
        wraps=lambda fp: np.zeros((10, 1, 1, 1)),
    )
    with pytest.raises(Exception) as err:
        with warnings.catch_warnings():
            warnings.simplefilter(action="error")
            chick_node.analyze_image("test_path.tiff", channel=0)
    assert "CHANNEL given but image dim 0 is of size 10!" in str(err)
