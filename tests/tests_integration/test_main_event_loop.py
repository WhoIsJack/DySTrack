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
import sys
import threading
import time
from datetime import datetime
from queue import Empty, Queue

import pytest

from dystrack.manager.manager import run_dystrack_manager
from dystrack.pipelines import lateral_line


def test_run_dystrack_manager():
    """Integration test for main event loop.

    This runs through the following steps:
        1. Generate a temporary test dir in the /testdata/ folder
        2. Launch DySTrack in a thread to monitor the test dir
        3. Move an example image to the test dir, triggering image analysis
        4. Check the resulting stdout against a saved reference
        5. Check the resulting dystrack_coords.txt against a saved reference
        6. Remove the temporary test dir

    Note that the temporary test dir will usually *not* be removed if the test
    fails for one reason or another. Test directories thus require occasional
    manual removal.
    """

    # DEV: Set this to True to see standard outputs during the pytest run;
    # useful for debugging (but forces test failure at the very end to ensure
    # it is not left on in a final commit).
    print_dystrack_outputs = False

    # DEV: Set this to True to generate a new reference stdout file (which will
    # overwrite the old) if the stdout behavior of the manager has changed.
    # This will force the test to fail, since generating a new reference from
    # the output and then comparing them to each other would always pass.
    # Note that dystrack_coords.txt files need to be manually updated or copied
    # from the temporary test directory if the reference file needs updating.
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

    # Prepare arguments for run_dystrack_manager
    manager_args = (testdir, lateral_line.analyze_image)
    manager_kwargs = {
        "img_kwargs": {"channel": None, "show": False, "verbose": True},
        "file_start": dystrack_file_start,
        "file_end": dystrack_file_end,
        "max_triggers": 1,
    }

    # To monitor DySTrack as it runs within a separate thread, stdout needs to
    # be redirected to a thread-save queue...
    class MonitoringQueue(Queue):

        def __init__(self, *args, **kwargs):
            Queue.__init__(self, *args, **kwargs)

        def write(self, msg):
            self.put(msg)

        def flush(self):
            sys.__stdout__.flush()

    mq = MonitoringQueue()
    original_stdout = sys.stdout
    sys.stdout = mq
    captured = ""

    # Set up the DySTrack thread
    thread = threading.Thread(
        target=run_dystrack_manager,
        args=manager_args,
        kwargs=manager_kwargs,
        daemon=True,
    )

    # Start it
    thread.start()
    time.sleep(0.5)

    # Wait for startup to complete
    time_start, time_elapsed, time_limit = time.time(), 0.0, 20.0
    startup_complete = False
    while thread.is_alive() and (time_elapsed < time_limit):
        try:
            captured += mq.get(timeout=0.1)
            if "Press <Esc> to terminate." in captured:
                time.sleep(0.5)  # Avoid possible race condition...
                startup_complete = True
                break
        except Empty:
            continue
        time_elapsed = time.time() - time_start
    if time_elapsed >= time_limit:
        raise Exception("DySTrack test thread startup exceeded time limit!")
    if not startup_complete:
        raise Exception("DySTrack test thread died during startup.")

    # Move example prescan into folder
    shutil.copy(prescan_fpath, testdir)
    assert os.path.isfile(os.path.join(testdir, prescan_fname))

    # Wait for image analysis to complete
    # Note: DySTrack exits on completion since max_triggers is 1, but you can't
    #       just wait via `thread.join()`, as that may deadlock with the queue!
    time_start, time_elapsed, time_limit = time.time(), 0.0, 20.0
    analysis_complete = False
    while time_elapsed < time_limit:
        try:
            captured += mq.get(timeout=0.1)
            if "No. coords sent to scope:" in captured:
                time.sleep(0.5)  # Avoid possible race condition...
                analysis_complete = True
                break
        except Empty:
            continue
        time_elapsed = time.time() - time_start
    if time_elapsed >= time_limit:
        raise Exception("Image analysis test run exceeded time limit!")
    if not analysis_complete:
        raise Exception("DySTrack test thread died during image analysis.")

    # Capture out anything that remains in the queue
    # Note: Queue must be empty to avoid possible deadlock on join
    while not mq.empty():
        captured += mq.get()

    # Ensure the thread properly exited/exits
    # Note: The thread should exit on its own because max_triggers is 1
    thread.join(timeout=5)
    if thread.is_alive():
        raise Exception("Join of DySTrack test thread unexpectedly timed out.")

    # Reset sys.stdout
    sys.stdout = original_stdout

    # Print the outputs (for debugging)
    if print_dystrack_outputs:
        print("\n\n[Printing captured output:]")
        print(captured)
        print("\n")

    # Check command line output against expectations
    if not print_dystrack_outputs:

        # Generate reference file
        if create_dystrack_stdout:
            with open(stdout_fpath, "w") as outfile:
                outfile.write(captured)

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
        captured = captured.split("\n")
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
    ), "`print_dystrack_outputs` is set to True; forcing test failure."
    assert (
        not create_dystrack_stdout
    ), "Generated new DySTrack stdout reference file; forcing test failure."
