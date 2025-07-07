# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:21:42 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Regression tests for run_mate.py; ensures correct basic behavior of
            MATE against well-established test data / test cases.
"""


import os
import re
import shutil
import sys
import threading
import time
from contextlib import ExitStack
from datetime import datetime

import pytest

from mate.manager.cmdline import run_via_cmdline
from mate.manager.manager import run_mate_manager


def test_run_via_cmdline(capsys, mocker):
    """Regression test for ~main function~* (command line parsing).

    *ULTRAREFACTORING: Now tests cmdline.run_via_cmdline!
    """

    # Prep dummy image analysis function
    def dummy_img_ana_func(target_path, channel=1, verbose=False):
        """Dummy image analysis function.

        Parameters
        ----------
        target_path : path-like
            Path to the image file that is to be analyzed.
        channel : int, optional, default None
            DUMMY TEST
        verbose : bool, optional, default False
            If True, more information is printed.

        Returns
        -------
        None
        """
        return None

    # Fix docs string parsing...                                               # FIXME: Use regex or numpydoc in doc string parsing instead!
    dummy_img_ana_func.__doc__ = dummy_img_ana_func.__doc__.replace(
        "        ", "    "
    )

    # Run with --help flag and check that SystemExit is reached
    sys.argv.append("--help")
    with pytest.raises(SystemExit):
        run_via_cmdline(dummy_img_ana_func)

    # Check that the help message was printed
    captured = capsys.readouterr()
    assert "usage: pytest [-h]" in captured.out
    assert "Start a MATE session." in captured.out
    assert "  image_analysis_func: dummy_img_ana_func" in captured.out
    assert "[int, optional, default None] DUMMY TEST" in captured.out

    # Run with mocked run_mate_manager function
    mocked_manager = mocker.patch("mate.manager.manager.run_mate_manager")
    mocked_manager.return_value = (None, None)
    mocked_manager.__code__ = run_mate_manager.__code__
    mocked_manager.__doc__ = run_mate_manager.__doc__
    sys.argv = [
        sys.argv[0],
        "./tests",
        "--file_start",
        "prescan_",
        "--file_end",
        ".czi",
        "--channel",
        "0",
        "--verbose",
        "True",
    ]
    assert run_via_cmdline(dummy_img_ana_func) == (None, None)

    # Check that mocked run_mate_manager was called with appropriate values
    mocked_manager.assert_called_with(
        "./tests",
        dummy_img_ana_func,
        file_start="prescan_",
        file_end=".czi",
        img_kwargs={"channel": 0, "verbose": True},
    )


def test_main_scheduler(capsys):
    """Regression test for scheduler (main event loop)."""

    # DEV: Set this to True to see MATE outputs during the pytest run;
    # this will make the test fail, but it's very useful for debugging!
    print_MATE_outputs = False

    # DEV: Set this to True to generate a new reference stdout file (which will
    # overwrite the old) if the stdout behavior of the scheduler has changed.
    # This will force the test to fail, since generating a new reference from
    # the output and then checking them against each other would always pass.
    create_MATE_stdout = False

    # Config
    datadir = "./tests/testdata"
    prescan_fname = "test0_prescan_prim_cldnb.czi"
    prescan_fpath = os.path.join(datadir, prescan_fname)
    stdout_fpath = os.path.join(datadir, "test0_stdout.txt")
    MATE_fileStart = "test0_prescan_"
    MATE_fileEnd = ".czi"

    # Create transient testing folder
    now = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    testdir = os.path.join(datadir, "testrun_" + now)
    os.mkdir(testdir)

    # Prepare thread object to run MATE monitoring with main_scheduler
    scheduler_args = (testdir,)
    scheduler_kwargs = {
        "img_params": {"channel": None, "show": False},
        "fileStart": MATE_fileStart,
        "fileEnd": MATE_fileEnd,
        "write_winreg": False,
        "verbose": True,
    }
    thread = threading.Thread(
        target=run_mate.main_scheduler,
        args=scheduler_args,
        kwargs=scheduler_kwargs,
        daemon=True,  # Ensures MATE thread will terminate at end of test
    )

    # For nicer output when printing
    if print_MATE_outputs:
        print("\n\n[test_run_mate.py:] Starting MATE monitoring in thread.")

    # Start the MATE monitoring thread
    thread.start()

    # Wait for startup
    # TODO: Would there be a more adaptive way to wait?
    time.sleep(6)

    # Move example test scan into folder
    shutil.copy(prescan_fpath, testdir)
    assert os.path.isfile(os.path.join(testdir, prescan_fname))

    # Wait for completion
    # TODO: Would there be a more adaptive way to wait?
    time.sleep(12)

    # Print the outputs (for debugging)
    if print_MATE_outputs:
        print("\n[test_run_mate.py:] Finished waiting for MATE monitoring.\n")
        captured = capsys.readouterr()
        with capsys.disabled():
            print(captured.out)

    # Check command line output against expectations
    if not print_MATE_outputs:
        captured = capsys.readouterr()

        # Generate reference file
        if create_MATE_stdout:
            with open(stdout_fpath, "w") as outfile:
                outfile.write(captured.out)

        # Compare against reference file (with updated testdir time label)
        with open(stdout_fpath, "r") as infile:
            check_captured = infile.read()
        ref_time = re.search(r"testrun_\d{8}-\d{6}", check_captured).group()
        check_captured = check_captured.replace(ref_time, "testrun_" + now)
        assert captured.out == check_captured

    # Check resulting mate_coords.txt file
    with open(os.path.join(testdir, "mate_coords.txt"), "r") as infile:
        test_mate_coords = infile.read()
    with open(os.path.join(datadir, "test0_mate_coords.txt"), "r") as infile:
        check_mate_coords = infile.read()
    assert test_mate_coords == check_mate_coords

    # Remove transient testing folder
    shutil.rmtree(testdir)
    assert not os.path.isdir(testdir)

    # Ensure the test fails if any of the DEV mode flags were set to True
    assert (
        not print_MATE_outputs
    ), "Cannot test MATE stdout when print_MATE_outputs is set to True; forcing test failure."
    assert (
        not create_MATE_stdout
    ), "Generated new MATE stdout reference file; forcing test failure."
