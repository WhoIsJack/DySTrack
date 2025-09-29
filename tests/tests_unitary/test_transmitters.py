# -*- coding: utf-8 -*-
"""
Created on Mon Jun 09 11:48:26 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  Unit tests against `transmitters.py`.
"""

import fake_winreg as fwinreg

from dystrack.manager import transmitters


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
