# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 00:31:36 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `loading.py`.
"""

import os
from time import sleep

import numpy as np
import pytest

from dystrack.pipelines.utilities import loading


def test_robust_load_success(mocker):
    """Test loading of an example file for each supported file type."""

    # Targets
    testpath = r"./tests/testdata/"
    fnames = [
        "test-pllp_980_prescan.tif",  # ImageJ .tif
        "test-pllp_980_prescan.czi",  # ZEISS LSM980 .czi
        "test-pllp_880_prescan.czi",  # ZEISS LSM880 .czi
        "test-pllp_AXR_prescan.tiff",  # Nikon AX R .tiff
        "test-pllp_AXR_prescan.nd2",  # Nikon AX R .nd2
    ]

    # Expectations
    fshapes = [
        (21, 200, 500),
        (21, 200, 500),
        (20, 200, 512),
        (9, 212, 512),
        (21, 128, 256),
    ]
    fdtypes = [np.uint8, np.uint8, np.uint8, np.uint16, np.uint16]

    # Run tests
    for fn, fs, fdt in zip(fnames, fshapes, fdtypes):
        raw = loading.robustly_load_image_after_write(
            os.path.join(testpath, fn), await_write=0.1
        )
        assert raw.shape == fs
        assert raw.dtype == fdt


def test_robust_load_slowrite(mocker):
    """Test if loading waits while file size changes, then proceeds when it has
    stopped changing."""

    # Target
    testpath = r"./tests/testdata/"
    fname = "test-pllp_980_prescan.tif"

    # Patch os.stat to change (apparent) file sizes...
    fake_size_generator = (i for i in [1000, 1001, 1002, 1003, 1003, 42])
    real_stat = os.stat

    def mock_stat(*args, **kwargs):
        if args[0] == os.path.join(testpath, fname):
            stats = real_stat(*args, **kwargs)
            st_size_idx = [
                prop
                for prop in os.stat(".").__dir__()
                if prop.startswith("st_")
            ].index("st_size")
            stats = list(stats)
            stats[st_size_idx] = next(fake_size_generator)
            return os.stat_result(stats)
        else:
            return real_stat(*args, **kwargs)

    mock_stat = mocker.patch(
        "dystrack.pipelines.utilities.loading.os.stat", wraps=mock_stat
    )

    # Run the test
    raw = loading.robustly_load_image_after_write(
        os.path.join(testpath, fname), await_write=0.1
    )
    assert raw.shape == (21, 200, 500)
    assert raw.dtype == np.uint8

    # Check that file size was checked the correct number of times
    assert next(fake_size_generator) == 42


def test_robust_load_errors_filext(mocker, capsys):
    """Test that an unsupported file extension raises the correct error."""

    # Target
    testpath = r"./tests/testdata/"
    fname = "test-pllp_980_prescan.unsupported"

    # Patch os.stat to return filesize for nonexistent path
    real_stat = os.stat

    def mock_stat(*args, **kwargs):
        if args[0] == os.path.join(testpath, fname):

            class MockStat(object):
                pass

            mockstat = MockStat()
            mockstat.st_size = 50
            return mockstat
        else:
            return real_stat(*args, **kwargs)

    mock_stat = mocker.patch(
        "dystrack.pipelines.utilities.loading.os.stat", wraps=mock_stat
    )

    # Test unsupported file ending
    with pytest.raises(ValueError) as err:
        raw = loading.robustly_load_image_after_write(
            os.path.join(testpath, fname),
            await_write=0.1,  # Short for tests perf
        )

    # Check error message
    assert "File ending not recognized!" in str(err.value)

    # Check stdout message
    captured = capsys.readouterr()
    assert "Multiple attempts to load" in captured.out

    # Check number of cycles
    assert len(mock_stat.call_args_list) == 6


def test_robust_load_errors_loadnonnumeric(capsys, mocker):
    """Test that silent failure of the loader producing a non-numeric array
    raises the correct errors."""

    # Target
    testpath = r"./tests/testdata/"
    fname = "test-pllp_980_prescan.tif"

    # Patch Bioimage to return string array
    mock_bioimage = mocker.patch(
        "dystrack.pipelines.utilities.loading.BioImage",
        wraps=lambda fp: np.array(["a", "b", "c"]),
    )

    # Test string array case
    with pytest.raises(IOError) as err:
        raw = loading.robustly_load_image_after_write(
            os.path.join(testpath, fname),
            await_write=0.1,  # Short for tests perf
        )

    # Check error message
    assert "array is not of a numerical type" in str(err.value)

    # Check stdout message
    captured = capsys.readouterr()
    assert "Multiple attempts to load" in captured.out

    # Check number of cycles
    assert len(mock_bioimage.call_args_list) == 5


def test_robust_load_errors_loadempty(capsys, mocker):
    """Test that silent failure of the loader producing an empty array raises
    the correct errors."""

    # Target
    testpath = r"./tests/testdata/"
    fname = "test-pllp_980_prescan.tif"

    # Patch Bioimage to return empty array
    mock_bioimage = mocker.patch(
        "dystrack.pipelines.utilities.loading.BioImage",
        wraps=lambda fp: np.zeros((0,)),
    )

    # Test empty array case
    with pytest.raises(IOError) as err:
        raw = loading.robustly_load_image_after_write(
            os.path.join(testpath, fname),
            await_write=0.1,  # Short for tests perf
        )

    # Check error message
    assert "array is of size 0" in str(err.value)

    # Check stdout message
    captured = capsys.readouterr()
    assert "Multiple attempts to load" in captured.out

    # Check number of cycles
    assert len(mock_bioimage.call_args_list) == 5


def test_robust_load_errors_bioimagearbitrary(capsys, mocker):
    """Test that Bioimage raising some arbitrary error is handled correctly."""

    # Target
    testpath = r"./tests/testdata/"
    fname = "test-pllp_980_prescan.tif"

    # For performance, patch sleep
    mocker.patch(
        "dystrack.pipelines.utilities.loading.sleep", lambda t: sleep(0.1)
    )

    # Patch Bioimage to raise some arbitrary error
    def arbitary_error(fp):
        raise Exception("Some arbitrary error.")

    mock_bioimage = mocker.patch(
        "dystrack.pipelines.utilities.loading.BioImage", wraps=arbitary_error
    )

    # Test arbitrary error case
    with pytest.raises(Exception) as err:
        raw = loading.robustly_load_image_after_write(
            os.path.join(testpath, fname)
        )

    # Check error message
    assert "Some arbitrary error." == str(err.value)

    # Check stdout message
    captured = capsys.readouterr()
    assert "Multiple attempts to load" in captured.out

    # Check number of cycles
    assert len(mock_bioimage.call_args_list) == 5
