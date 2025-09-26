# -*- coding: utf-8 -*-
"""
Created on Mon Jun 09 11:38:17 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `manager.py`.
"""

import pytest

import mate.manager.manager as mng


def test_check_fname():

    example_fname = "prescan_somefilename.czi"

    test_conditions = [
        {"file_start": "prescan", "file_end": ".czi", "file_regex": ".*"},
        {"file_start": "prescan"},
        {"file_end": ".czi"},
        {"file_regex": ".*"},
        {"file_start": "prescan", "file_end": ".czi"},
        {"file_start": "prescan", "file_regex": ".*"},
        {"file_end": ".czi", "file_regex": ".*"},
        {"file_start": "", "file_end": "", "file_regex": ""},
        {"file_start": "bad", "file_end": ".czi", "file_regex": ".*"},
        {"file_start": "prescan", "file_end": ".bad", "file_regex": ".*"},
        {"file_start": "prescan", "file_end": ".czi", "file_regex": r"\d.*"},
        {"file_start": "bad", "file_end": ".bad", "file_regex": ".*"},
        {"file_start": "bad", "file_end": ".bad", "file_regex": r"\d.*"},
    ]
    test_expectations = 8 * [True] + 5 * [False]

    for c, e in zip(test_conditions, test_expectations):
        assert mng._check_fname(example_fname, **c) == e


def test_trigger_image_analysis():

    # Prep
    target_path = r"./tests/testdata/example_path.tiff"

    # Mock target function with "correct" signature
    def img_ana_func(target_path, sigma=10):
        return target_path, sigma, 200, "OK", {}

    # Test successful call
    outputs = mng._trigger_image_analysis(
        target_path, img_ana_func, img_kwargs={"sigma": 5.5}, img_cache={}
    )
    assert outputs == ((target_path, 5.5, 200, "OK", {}), None)

    # Test bad img_kwarg
    outputs = mng._trigger_image_analysis(
        r"./tests/testdata/example_path.tiff",
        img_ana_func,
        img_kwargs={"density": 5},
        img_cache={},
    )
    assert outputs[0] == (None, None, None, "Image analysis failed!", {})
    assert "got an unexpected keyword argument 'density'" in str(outputs[1])

    # Test bad img_cache
    outputs = mng._trigger_image_analysis(
        r"./tests/testdata/example_path.tiff",
        img_ana_func,
        img_kwargs={},
        img_cache={"density": 5},
    )
    assert outputs[0] == (
        None,
        None,
        None,
        "Image analysis failed!",
        {"density": 5},
    )
    assert "got an unexpected keyword argument 'density'" in str(outputs[1])

    # Mock target function with incorrect signature
    def img_ana_func(target_path, sigma=10):
        return None

    # Test correct call of incorrect function
    outputs = mng._trigger_image_analysis(
        target_path, img_ana_func, img_kwargs={"sigma": 5.5}, img_cache={}
    )
    assert outputs[0] == (None, None, None, "Image analysis failed!", {})
    assert "cannot unpack non-iterable NoneType object" in str(outputs[1])


def test_trigger_coords_transmission(mocker, capsys):

    # Test custom callable transmission method
    def tra_mock(z_pos, y_pos, x_pos, img_msg, *args, **kwargs):
        print(z_pos, y_pos, x_pos, img_msg, end="")
        return

    mng._trigger_coords_transmission(tra_mock, None, 10, 15, "test_msg")
    captured = capsys.readouterr()
    assert captured.out == "None 10 15 test_msg"

    # Test txt file transmission method
    def tra_txt_mock(fpath, z_pos, y_pos, x_pos, msg):
        print(fpath, z_pos, y_pos, x_pos, msg, end="")
        return

    mocker.patch(
        "mate.manager.transmitters.send_coords_txt", wraps=tra_txt_mock
    )
    mng._trigger_coords_transmission(
        "txt", None, 10, 15, "test_msg", target_dir="."
    )
    captured = capsys.readouterr()
    assert captured.out == ".\\mate_coords.txt None 10 15 test_msg"

    # Test winreg transmission method
    def tra_winreg_mock(z_pos, y_pos, x_pos, codeM, errMsg):
        print(z_pos, y_pos, x_pos, codeM, errMsg, end="")
        return

    mocker.patch(
        "mate.manager.transmitters.send_coords_winreg", wraps=tra_winreg_mock
    )
    mng._trigger_coords_transmission("MyPiC", None, 10, 15, "test_msg", None)
    captured = capsys.readouterr()
    assert captured.out == "None 10 15 focus test_msg"

    # Test for correct error handling with custom callable transmission method
    def tra_error(*args, **kwargs):
        raise Exception("test error")

    tra_e = mng._trigger_coords_transmission(
        tra_error, None, 10, 15, "test_msg"
    )
    assert "test error" in str(tra_e)

    # Test for correct error handling with txt file transmission method
    mocker.patch("mate.manager.transmitters.send_coords_txt", wraps=tra_error)
    tra_e = mng._trigger_coords_transmission(
        "txt", None, 10, 15, "test_msg", target_dir="."
    )
    assert "test error" in str(tra_e)

    # Test for correct error handling with winreg transmission method
    mocker.patch(
        "mate.manager.transmitters.send_coords_winreg", wraps=tra_error
    )
    tra_e = mng._trigger_coords_transmission(
        "MyPiC", None, 10, 15, "test_msg", None
    )
    assert "test error" in str(tra_e)

    # Test invalid transmission method
    with pytest.raises(ValueError) as err:
        tra_e = mng._trigger_coords_transmission(
            "unsupported_method", None, 10, 15, "test_msg"
        )
    assert "invalid `transmission_method`" in str(err)


def NOtest_run_mate_manager_success():
    """NOtest: Test not implemented; covered by integration test."""

    # TODO: Fully unit-testing this function would require extensive mocking.
    #       Since most functionality of `run_mate_manager` is already tested
    #       with a "live" integration test that does not rely on mocking, this
    #       is only nice-to-have and remains a stretch goal for future work.

    pass


def test_run_mate_manager_errors_noexit():
    with pytest.raises(ValueError) as err:
        mng.run_mate_manager(
            "test_dir",
            lambda x: None,
            max_checks=None,
            max_triggers=None,
            end_on_esc=False,
        )
    assert "No ending condition for MATE event loop set" in str(err)


def NOtest_run_mate_manager_errors_OTHER():
    """NOtest: Test not implemented. [low-priority]"""

    # TODO: Test for other errors that `run_mate_manager` may raise.
    #       Requires extensive mocking (see `test_run_mate_manager_success`)
    #       and is currently nice-to-have/low-priority.

    pass
