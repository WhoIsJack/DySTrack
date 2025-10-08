# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:21:42 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Integration test for run_dystrack_manager; tests the core
            functionality of DySTrack against a well-established test case.
"""

import os
import shutil
import threading
import time
from datetime import datetime

import pytest

from dystrack.manager.manager import run_dystrack_manager
from dystrack.pipelines import lateral_line


def test_run_dystrack_manager(capsys):
    """Integration test for main event loop.

    This runs through the following steps:
        1. Generate a temporary test dir in the /testdata/ folder
        2. Launch DySTrack in a thread to monitor the test dir
        3. Move an example image to the test dir, triggering image analysis
        4. Check the resulting stdout against a saved reference
        5. Check the resulting dystrack_coords.txt against a saved reference
        6. Remove the temporary test dir

    Saved references can be automatically generated; see 2nd DEV tag below.
    """

    # DEV: Set this to True to see standard outputs during the pytest run;
    # this will make the test fail, but it's very useful for debugging!
    print_dystrack_outputs = False

    # DEV: Set this to True to generate a new reference stdout file (which will
    # overwrite the old) if the stdout behavior of the manager has changed.
    # This will force the test to fail, since generating a new reference from
    # the output and then comparing them to each other would always pass.
    # Also, note that this will not work if `print_dystrack_outputs` is True.
    create_dystrack_stdout = False

    # Config
    datadir = "./tests/testdata"
    prescan_fname = "test-full_prescan_pllp.czi"
    prescan_fpath = os.path.join(datadir, prescan_fname)
    stdout_fpath = os.path.join(datadir, "test-full_stdout.txt")
    dystrack_file_start = "test-full_prescan_"
    dystrack_file_end = ".czi"

    # Create transient testing folder
    now = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    testdir = os.path.join(datadir, "testrun_" + now)
    os.mkdir(testdir)

    # Prepare thread object to run DySTrack monitoring w/ run_dystrack_manager
    manager_args = (testdir, lateral_line.analyze_image)
    manager_kwargs = {
        "img_kwargs": {"channel": None, "show": False, "verbose": True},
        "file_start": dystrack_file_start,
        "file_end": dystrack_file_end,
        "max_triggers": 1,
    }
    thread = threading.Thread(
        target=run_dystrack_manager,
        args=manager_args,
        kwargs=manager_kwargs,
        daemon=True,  # Enforces thread termination at end of test
    )

    # For nicer output when printing
    if print_dystrack_outputs:
        print(
            "\n\n[test_run_dystrack.py:] Starting DySTrack monitoring in thread."
        )

    # Start the DySTrack monitoring thread
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
    if print_dystrack_outputs:
        print(
            "\n[test_run_dystrack.py:] Finished waiting for DySTrack monitoring.\n"
        )
        captured = capsys.readouterr()
        with capsys.disabled():
            print(captured.out)

    # Check command line output against expectations
    if not print_dystrack_outputs:
        captured = capsys.readouterr()

        # Generate reference file
        if create_dystrack_stdout:
            with open(stdout_fpath, "w") as outfile:
                outfile.write(captured.out)

        # Get reference file for comparison
        with open(stdout_fpath, "r") as infile:
            check_captured = infile.read()

        # Drop total checks made from reference
        # Note: The exact number here is unstable due to runtime variations!
        check_captured = check_captured.split("\n")
        check_captured = [
            cc for cc in check_captured if "Total checks made:" not in cc
        ]
        check_captured = "\n".join(check_captured)

        # Drop total checks made from capture
        captured = captured.out.split("\n")
        captured = [cc for cc in captured if "Total checks made:" not in cc]
        captured = "\n".join(captured)

        assert captured == check_captured

    # Check resulting dystrack_coords.txt file
    with open(os.path.join(testdir, "dystrack_coords.txt"), "r") as infile:
        test_dystrack_coords = infile.read()
    with open(
        os.path.join(datadir, "test-full_dystrack_coords.txt"), "r"
    ) as infile:
        check_dystrack_coords = infile.read()
    assert test_dystrack_coords == check_dystrack_coords

    # Remove transient testing folder
    shutil.rmtree(testdir)
    assert not os.path.isdir(testdir)

    # Enforce test failure if any of the DEV mode flags were set to True
    assert (
        not print_dystrack_outputs
    ), "Cannot test DySTrack stdout when print_dystrack_outputs is set to True; forcing test failure."
    assert (
        not create_dystrack_stdout
    ), "Generated new DySTrack stdout reference file; forcing test failure."
