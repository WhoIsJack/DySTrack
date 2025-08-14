# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:21:51 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `cmdline.py`.
"""

from mate.manager import cmdline


def test_get_func_args():

    def test_func(a, b, c=None):
        pass

    func_args = cmdline._get_func_args(test_func)
    assert func_args == ("a", "b", "c")


def test_get_docstr_args_numpy():

    def test_func(a, b, c=None):
        """A test function for testing of doc string argument retrieval.

        Parameters
        ----------
        a : dummy type a
            Dummy parameter a
        b : dummy type b
            Dummy parameter b with a long
            multi-line description.
        c : dummy type c, optional, default None
            Dummy parameter c.

        Returns
        -------
        Nothing
        """
        pass
    
    argtypes, argdescr = cmdline._get_docstr_args_numpy(test_func)

    expected_argtypes = {
        'a': 'dummy type a', 
        'b': 'dummy type b', 
        'c': 'dummy type c, optional, default None'
    }
    expected_argdescr = {
        'a': 'Dummy parameter a', 
        'b': 'Dummy parameter b with a long multi-line description.', 
        'c': 'Dummy parameter c.'
    }

    assert argtypes == expected_argtypes
    assert argdescr == expected_argdescr


def test_run_via_cmdline():
    assert False, "# TODO: Implement this test!"  # YAH!



# -----------------------------------------------------------------------------
# TAKEN FROM BOTTOM OF cmdline.py FOR REFERENCE!
# -----------------------------------------------------------------------------

# DEV-TEMP! For testing!  

# def my_img_ana_func(target_path, verbose=False, channel=None, sigma=3.0):
#     """This my doc string.

#     Parameters
#     ----------
#     target_path : str
#         Path to target image file. [MY_IMG_ANA_FUNC]
#     verbose : bool, optional, default False
#         Whether to print extra information. [MY_IMG_ANA_FUNC]
#     channel : int or None, optional, default None
#         The channel to use for analysis. [MY_IMG_ANA_FUNC]
#     sigma : float, optional, default 3.0
#         Sigma of the Gaussian smoothing, in pixels. [MY_IMG_ANA_FUNC]

#     Returns
#     -------
#     Nothing especially
#     """
#     print(target_path, verbose, channel, sigma)


# if __name__ == "__main__":
#     run_via_cmdline(
#         my_img_ana_func,
#         # analysis_kwargs={"channel": 1},
#         manager_kwargs={"file_end": ".tif", "file_start": "Prescan_"},
#     )


# -----------------------------------------------------------------------------
# TAKEN FROM FUNCTION BODY OF run_via_cmdline() FOR REFERENCE!
# -----------------------------------------------------------------------------

#     # DEV-TEMP! For testing!
#     print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
#     print(target_dir, "\n")
#     for kwarg in manager_kwargs:
#         if not isinstance(manager_kwargs[kwarg], dict):
#             print(
#                 kwarg,
#                 manager_kwargs[kwarg],
#                 f"[{type(manager_kwargs[kwarg])}]\n",
#             )
#         else:
#             for kwargkwarg in manager_kwargs[kwarg]:
#                 print(
#                     "~~",
#                     kwargkwarg,
#                     manager_kwargs[kwarg][kwargkwarg],
#                     f"[{type(manager_kwargs[kwarg][kwargkwarg])}]\n",
#                 )
#     print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
#     # return


# -----------------------------------------------------------------------------
# A COPY FOR THE OLD `test_run_mate.py` FOR REFERENCE
# -----------------------------------------------------------------------------

if __name__ == "_DEV_TEMP_":  # (Protect from pytest)


    import os
    import re
    import shutil
    import sys
    import threading
    import time
    from contextlib import ExitStack
    from datetime import datetime

    import pytest

    from mate.manager import run_mate

    def test_main(capsys, mocker):
        """Regression test for main function (command line parsing)."""

        # Run with --help flag and check that SystemExit is reached
        sys.argv.append("--help")
        with pytest.raises(SystemExit):
            run_mate.main()

        # Check that the help message was printed
        captured = capsys.readouterr()
        s1 = "run_mate TARGET_DIR [-s START] [-e END] [-c CHANNEL] [-w] [-v] [-p]"
        s2 = "Start up a MATE manager session."
        assert s1 in captured.out
        assert s2 in captured.out

        # Run with mocked main_scheduler function
        mocked_scheduler = mocker.patch("mate.manager.run_mate.main_scheduler")
        mocked_scheduler.return_value = "mocked_scheduler_output_stats"
        sys.argv = [
            sys.argv[0],
            "./tests",
            "-s",
            "prescan_",
            "-e",
            ".czi",
            "-c",
            "0",
            "-v",
        ]
        assert run_mate.main() == "mocked_scheduler_output_stats"

        # Check that mocked main_scheduler was called with appropriate values
        mocked_scheduler.assert_called_with(
            "./tests",
            img_params={"channel": 0, "show": False},
            fileStart="prescan_",
            fileEnd=".czi",
            write_winreg=False,
            verbose=True,
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
            print(
                "\n\n[test_run_mate.py:] Starting MATE monitoring in thread."
            )

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
            print(
                "\n[test_run_mate.py:] Finished waiting for MATE monitoring.\n"
            )
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
            ref_time = re.search(
                r"testrun_\d{8}-\d{6}", check_captured
            ).group()
            check_captured = check_captured.replace(ref_time, "testrun_" + now)
            assert captured.out == check_captured

        # Check resulting mate_coords.txt file
        with open(os.path.join(testdir, "mate_coords.txt"), "r") as infile:
            test_mate_coords = infile.read()
        with open(
            os.path.join(datadir, "test0_mate_coords.txt"), "r"
        ) as infile:
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
