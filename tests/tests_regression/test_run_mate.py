# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 13:21:42 2024

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Regression tests for run_mate.py; ensures correct basic behavior of
            MATE against well-established test data / test cases.
"""


### Imports

import sys
import pytest

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

    with capsys.disabled():
        print(run_mate.main_scheduler)

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

def test_main_scheduler():
    assert True  # TODO!