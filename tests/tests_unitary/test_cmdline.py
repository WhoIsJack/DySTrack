# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:21:51 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `cmdline.py`.
"""

import pytest

from mate.manager import cmdline
from mate.manager.manager import run_mate_manager


def test_get_func_args():

    # Test edge case without arguments
    def test_func_noargs():
        pass

    func_args_noargs = cmdline._get_func_args(test_func_noargs)
    assert func_args_noargs == tuple()

    # Test case with arguments
    def test_func(a, b, c=None):
        pass

    func_args = cmdline._get_func_args(test_func)
    assert func_args == ("a", "b", "c")


def test_get_docstr_args_numpy():

    # Test edge case without doc string
    def test_func_nodocstr(a, b, c=None):
        pass

    with pytest.raises(ValueError) as nodocstrerr:
        cmdline._get_docstr_args_numpy(test_func_nodocstr)
    assert str(nodocstrerr.value) == "Provided `func` has no doc string."

    # Test edge case with incomplete/non-numpy doc string
    def test_func_wrongdocstr(a, b, c=None):
        """A test function that lacks numpy-style parameters."""
        pass

    with pytest.raises(ValueError) as wrongdocstrerr:
        cmdline._get_docstr_args_numpy(test_func_wrongdocstr)
    assert str(wrongdocstrerr.value) == (
        "Provided `func` does not seem to have a numpy-style doc string "
        + "with both a Parameters section and a Returns section."
    )

    # Test case with proper doc string
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
        "a": "dummy type a",
        "b": "dummy type b",
        "c": "dummy type c, optional, default None",
    }
    expected_argdescr = {
        "a": "Dummy parameter a",
        "b": "Dummy parameter b with a long multi-line description.",
        "c": "Dummy parameter c.",
    }

    assert argtypes == expected_argtypes
    assert argdescr == expected_argdescr


def test_run_via_cmdline(capsys, mocker):
    # TODO: This is far from comprehensive given the complicated functionality
    #       implemented by this function...

    # Prep dummy image analysis function
    def dummy_img_ana_func(
        target_path,
        channel=1,
        verbose=False,
    ):
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

    # Run with --help flag and check that SystemExit is reached
    with pytest.raises(SystemExit):
        cmdline.run_via_cmdline(["dummy", "--help"], dummy_img_ana_func)

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
    argv = [
        "dummy",
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
    assert cmdline.run_via_cmdline(argv, dummy_img_ana_func) == (None, None)

    # Check that mocked run_mate_manager was called with appropriate values
    mocked_manager.assert_called_with(
        "./tests",
        dummy_img_ana_func,
        file_start="prescan_",
        file_end=".czi",
        img_kwargs={"channel": 0, "verbose": True},
        img_cache={},
    )

    # Extra test for edge case of function with incomplete doc string
    def dummy_img_ana_func(
        target_path,
        channel=1,
        verbose=False,
    ):
        """Dummy image analysis function.

        Parameters
        ----------
        target_path : path-like
            Path to the image file that is to be analyzed.
        verbose : bool, optional, default False
            If True, more information is printed.

        Returns
        -------
        None
        """
        return None

    with pytest.raises(AttributeError) as incompletedocstrerr:
        cmdline.run_via_cmdline(argv, dummy_img_ana_func)
    assert str(incompletedocstrerr.value) == (
        "'NoneType' object has no attribute 'groups'"
    )
    captured = capsys.readouterr()
    assert "[!!] Failed to parse doc string" in captured.out
