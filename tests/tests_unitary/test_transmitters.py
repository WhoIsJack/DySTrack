# -*- coding: utf-8 -*-
"""
Created on Mon Jun 09 11:48:26 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `transmitters.py`.
"""

import builtins
import multiprocessing
import os
from datetime import datetime
from multiprocessing.pool import ThreadPool
from time import sleep

import fake_winreg as fwinreg

from dystrack.manager import transmitters


def test_send_coords_txt(mocker):

    # Mock file opening for write
    mock_send = mocker.patch("builtins.open", mocker.mock_open())

    # Call the function
    test_fpath = r"C:\this\is\just\a\test\path\dystrack_coords.txt"
    transmitters.send_coords_txt(
        test_fpath,
        z_pos=None,
        y_pos=50,
        x_pos=42.42,
        msg="test_msg",
        precision=3,
    )

    # Check that things were called as expected
    mock_send.assert_called_once_with(test_fpath, "a")
    mock_send().write.assert_called_once_with(
        f"nan\t50.000\t42.420\ttest_msg\n"
    )


def test_macro_race_safety(mocker):
    """This tests that `transmitters.send_coords_txt()` does not run the risk
    of a race condition when it is writing to a coordinates file that is being
    monitored by a microscope macro. It does so by slowly writing some example
    data while simultaneouly running a subprocess that mimics the way the macro
    would check the file.

    This only ensures safety for write operations that do not exceed the buffer
    size, so `msg` should not be abused to send additional data to the scope.
    Instead, write additional data to a file within the image analysis pipeline
    and then read it from the microscope function *after* the new coordinates
    have been read from the coordinate file.

    One reason this test may fail is when it is run on a non-Windows OS. This
    is currently not supported, so it is up to you to implement a race-safe way
    of writing coordinates for the non-Windows OS you are using.
    """

    # Some config
    repeats = 20
    test_path = r"./tests/testdata/"
    nonwin_msg = (
        "If you are not on Windows OS, failure of this test may be expected."
        + " Note that DySTrack currently only supports Windows."
    )

    # Create temporary dystrack_coords.txt
    now = datetime.now().strftime(r"%Y%m%d-%H%M%S")
    test_fpath = os.path.join(test_path, f"test_dystrack_coords_{now}.txt")
    with open(test_fpath, "w") as testfile:
        testfile.write("Z\tY\tX\tmsg\n")

    # Create mocked `open` function that acts just like the real `open` but
    # when `.write` is called, it writes the input repeatedly and slowly
    real_open = builtins.open

    def mock_open(file, *args, **kwargs):

        # Actually open the file
        handle = real_open(file, *args, **kwargs)
        real_write = handle.write

        # Define the slowed/repeated write function
        def slow_repeated_write(string):
            for i in range(repeats):
                real_write(string)
                sleep(0.1)
            return repeats * len(string)

        # Assign it iff open was called in write or append mode
        mode = args[0] if args else kwargs.get("mode")
        if mode in ["w", "a"]:
            handle.write = slow_repeated_write

        # Done
        return handle

    # Patch in the custom opener
    mock_ready = mocker.patch("builtins.open", mock_open)

    # Define function that mimics microscope macro as it looks for new lines
    # being written to the dystrack_coords file
    def micmacro_await(coords_fpath, lines_read=1):

        while True:
            with open(coords_fpath, "r") as infile:
                lines = infile.readlines()

            if len(lines) > lines_read:
                return lines

            sleep(0.1)

    # Start subprocess with microscope macro await function
    pool = ThreadPool(processes=1)
    thread_result = pool.apply_async(micmacro_await, [test_fpath])
    sleep(0.5)

    # Run the transmitter (with the patched write)
    transmitters.send_coords_txt(
        test_fpath,
        z_pos=None,
        y_pos=50,
        x_pos=42.42,
        msg="test_msg",
        precision=3,
    )

    # Safely collect the thread result...
    try:
        result = thread_result.get(timeout=5)
    except multiprocessing.TimeoutError as te:
        pool.terminate()
        print("Microscope macro mimic task timed out!")
        print(nonwin_msg)
        raise te
    except Exception as e:
        pool.terminate()
        print(nonwin_msg)
        raise e
    finally:
        pool.close()
        pool.join()

    # Assert that microscope macro subprocess did not prematurely read the
    # coords file, but did read it when the write was done
    assert len(result) == (repeats + 1), nonwin_msg
    assert result[-1] == f"nan\t50.000\t42.420\ttest_msg\n", nonwin_msg

    # Clean up the temporary dystrack_coords.txt
    os.remove(test_fpath)


def test_write_reg(monkeypatch, mocker):

    # Set up fake registry for testing
    fake_registry = fwinreg.fake_reg_tools.get_minimal_windows_testregistry()
    fwinreg.load_fake_registry(fake_registry)

    # Monkeypatch fake registry
    monkeypatch.setattr("dystrack.manager.transmitters.winr", fwinreg)
    mock_create = mocker.patch(
        "dystrack.manager.transmitters.winr.CreateKeyEx",
        wraps=fwinreg.CreateKeyEx,
    )
    mock_setval = mocker.patch(
        "dystrack.manager.transmitters.winr.SetValueEx",
        wraps=fwinreg.SetValueEx,
    )
    mock_closek = mocker.patch(
        "dystrack.manager.transmitters.winr.CloseKey", wraps=fwinreg.CloseKey
    )

    # Call the function
    reg_key = (
        r"SOFTWARE\VB and VBA Program Settings\OnlineImageAnalysis\macro_test"
    )
    reg_name = "test_name"
    reg_value = 42
    transmitters._write_reg(reg_key, reg_name, reg_value)

    # Check that the value has been set in the fake registry
    key_handle = fwinreg.OpenKeyEx(fwinreg.HKEY_CURRENT_USER, reg_key)
    assert fwinreg.QueryValueEx(key_handle, reg_name)[0] == str(reg_value)

    # Check that the functions were called as expected
    mock_create.assert_called_once_with(
        fwinreg.HKEY_CURRENT_USER, reg_key, 0, fwinreg.KEY_WRITE
    )
    mock_key_handle = mock_setval.call_args[0][0]
    mock_setval.assert_called_once_with(
        mock_key_handle, reg_name, 0, fwinreg.REG_SZ, str(reg_value)
    )
    mock_closek.assert_called_once_with(mock_key_handle)


def test_send_coords_winreg(mocker):

    # Mock registry writing
    mock_send = mocker.patch("dystrack.manager.transmitters._write_reg")

    # Call the function with different sets of arguments
    transmitters.send_coords_winreg(
        y_pos=50, x_pos=42.42, codeM="focus", errMsg=None
    )
    transmitters.send_coords_winreg(
        z_pos=10.0, y_pos=50, x_pos=42.42, codeM="focus", errMsg="TESTING"
    )

    # Check that the registry write operations were called as expected
    reg_key = r"SOFTWARE\VB and VBA Program Settings\OnlineImageAnalysis\macro"
    calls = [
        # First case
        mocker.call(reg_key, "Y", 50),
        mocker.call(reg_key, "X", 42.42),
        mocker.call(reg_key, "codeMic", "focus"),
        # Second case
        mocker.call(reg_key, "Z", 10.0),
        mocker.call(reg_key, "Y", 50),
        mocker.call(reg_key, "X", 42.42),
        mocker.call(reg_key, "errorMsg", "TESTING"),
        mocker.call(reg_key, "codeMic", "focus"),
    ]
    mock_send.assert_has_calls(calls)
