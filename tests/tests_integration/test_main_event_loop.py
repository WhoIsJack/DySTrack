# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:21:42 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Integration test for run_mate_manager; tests the core functionality
            of MATE against a well-established test case.
"""

import os
import shutil
import threading
import time
from datetime import datetime

import pytest

from mate.manager.manager import run_mate_manager
from mate.pipelines import lateral_line


def test_run_mate_manager(capsys):
    """Integration test for main event loop.

    This runs through the following steps:
        1. Generate a temporary test dir in the /testdata/ folder
        2. Launch MATE in a thread to monitor the test dir
        3. Move an example image to the test dir, triggering image analysis
        4. Check the resulting stdout against a saved reference
        5. Check the resulting mate_coords.txt against a saved reference
        6. Remove the temporary test dir

    Saved references can be automatically generated; see 2nd DEV tag below.
    """

    # DEV: Set this to True to see standard outputs during the pytest run;
    # this will make the test fail, but it's very useful for debugging!
    print_MATE_outputs = False

    # DEV: Set this to True to generate a new reference stdout file (which will
    # overwrite the old) if the stdout behavior of the manager has changed.
    # This will force the test to fail, since generating a new reference from
    # the output and then comparing them to each other would always pass.
    # Also, note that this will not work if `print_MATE_outputs` is True.
    create_MATE_stdout = False

    # Config
    datadir = "./tests/testdata"
    prescan_fname = "test-full_prescan_prim_cldnb.czi"
    prescan_fpath = os.path.join(datadir, prescan_fname)
    stdout_fpath = os.path.join(datadir, "test-full_stdout.txt")
    MATE_file_start = "test-full_prescan_"
    MATE_file_end = ".czi"

    # Create transient testing folder
    now = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    testdir = os.path.join(datadir, "testrun_" + now)
    os.mkdir(testdir)

    # Prepare thread object to run MATE monitoring with run_mate_manager
    manager_args = (testdir, lateral_line.analyze_image)
    manager_kwargs = {
        "img_kwargs": {"channel": None, "show": False, "verbose": True},
        "file_start": MATE_file_start,
        "file_end": MATE_file_end,
        "max_triggers": 1,
    }
    thread = threading.Thread(
        target=run_mate_manager,
        args=manager_args,
        kwargs=manager_kwargs,
        daemon=True,  # Enforces thread termination at end of test
    )

    # For nicer output when printing
    if print_MATE_outputs:
        print("\n\n[test_run_mate.py:] Starting MATE monitoring in thread.")

    # Start the MATE monitoring thread
    thread.start()

    # Wait for startup
    # TODO: Would there be a more adaptive way to wait?
    time.sleep(6)

    # Move example prescan into folder
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
        assert captured.out == check_captured

    # Check resulting mate_coords.txt file
    with open(os.path.join(testdir, "mate_coords.txt"), "r") as infile:
        test_mate_coords = infile.read()
    with open(
        os.path.join(datadir, "test-full_mate_coords.txt"), "r"
    ) as infile:
        check_mate_coords = infile.read()
    assert test_mate_coords == check_mate_coords

    # Remove transient testing folder
    shutil.rmtree(testdir)
    assert not os.path.isdir(testdir)

    # Enforce test failure if any of the DEV mode flags were set to True
    assert (
        not print_MATE_outputs
    ), "Cannot test MATE stdout when print_MATE_outputs is set to True; forcing test failure."
    assert (
        not create_MATE_stdout
    ), "Generated new MATE stdout reference file; forcing test failure."
