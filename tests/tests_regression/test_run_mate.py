# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:21:42 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Regression tests for run_mate.py; ensures correct basic behavior of
            MATE against well-established test data / test cases.
"""


### Imports

import pytest
import sys, os, shutil, time
import multiprocessing
from datetime import datetime
from contextlib import ExitStack

from mate.manager import run_mate


### Regression test for main function (command line parsing)

def test_main(capsys, mocker):
    
    # Run with --help flag and check that SystemExit is reached
    sys.argv.append('--help')
    with pytest.raises(SystemExit):
        run_mate.main()

    # Check that the help message was printed
    captured = capsys.readouterr()
    s1 = "run_mate TARGET_DIR [-s START] [-e END] [-c CHANNEL] [-w] [-v] [-p]"
    s2 = "Start up a MATE manager session."
    assert s1 in captured.out
    assert s2 in captured.out

    # Run with mocked main_scheduler function
    mocked_scheduler = mocker.patch('mate.manager.run_mate.main_scheduler')
    mocked_scheduler.return_value  = "mocked_scheduler_output_stats"
    sys.argv = [
        sys.argv[0], './tests', 
        '-s', 'prescan_', '-e', '.czi', '-c', '0', 
        '-v']
    assert run_mate.main() == "mocked_scheduler_output_stats"

    # Check that mocked main_scheduler was called with appropriate values
    mocked_scheduler.assert_called_with(
        './tests', 
        img_params={'channel':0, 'show':False},
        fileStart='prescan_', fileEnd='.czi',
        write_winreg=False, verbose=True
    )


### Regression test for scheduler (main event loop)

def test_main_scheduler(capsys):

    # DEV: Set this to True to see MATE outputs during the pytest run;
    # this will make the test fail, but it's very useful for debugging!
    print_MATE_outputs = False

    # Config
    datadir        = "./tests/testdata"
    prescan_fname  = "test0_prescan_prim_cldnb.czi"
    prescan_fpath  = os.path.join(datadir, prescan_fname)
    MATE_fileStart = "test0_prescan_"
    MATE_fileEnd   = ".czi"

    # Create transient testing folder
    now = datetime.now().strftime("%Y%m%d-%H%M%S")
    testdir = os.path.join(datadir, "testrun_"+now)
    os.mkdir(testdir)

    # Handle conditional printing of MATE outputs
    with ExitStack() as capsys_stack:
        if print_MATE_outputs:
            _ = capsys_stack.enter_context(capsys.disabled())

        # Start monitoring with scheduler (in separate process)
        scheduler_args = (testdir, )
        scheduler_kwargs = {
            'img_params'   : {'channel':None, 'show':False},
            'fileStart'    : MATE_fileStart,
            'fileEnd'      : MATE_fileEnd,
            'write_winreg' : False,
            'verbose'      : True}
        process = multiprocessing.Process(
            target=run_mate.main_scheduler,
            args=scheduler_args,
            kwargs=scheduler_kwargs)
        process.start()

        # Wait for startup
        # TODO: Would there be a more adaptive way to wait?
        time.sleep(6)

        # Move example test scan into folder
        shutil.copy(prescan_fpath, testdir)
        assert os.path.isfile(os.path.join(testdir, prescan_fname))

        # Wait for completion
        # TODO: Would there be a more adaptive way to wait?
        time.sleep(12)

        # Terminate scheduler monitoring
        # TODO: Have the scheduler exit gracefully when terminated?!
        process.terminate()

        # For nicer output when capsys is off
        print("\n[test_run_mate.py:] MATE process has been terminated.\n\n")

    # Check command line output against expectations
    if not print_MATE_outputs:
        # NOTE: Turns out this is kinda hard, since capsys/capfd do not seem
        #       able to capture stdout from multiprocessing.Process, and there
        #       doesn't seem to be simple method to do so otherwise either. The
        #       closest to success (but also very complicated) is to change the
        #       sys.stdout inside the process into a file object...
        pass  # TODO! YAH!

    # Check resulting mate_coords.txt file
    with open(os.path.join(testdir, "mate_coords.txt"), "r") as infile:
        test_mate_coords = infile.read()
    with open(os.path.join(datadir, "test0_mate_coords.txt"), "r") as infile:
        check_mate_coords = infile.read()
    assert test_mate_coords == check_mate_coords

    # Remove transient testing folder
    shutil.rmtree(testdir)
    assert not os.path.isdir(testdir)

    # Ensure the test fails if the command line output test was skipped
    assert not print_MATE_outputs, "Cannot test MATE command line outputs when print_MATE_outputs is set to True."