# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Functions for sending coordinates and commands to microscopes, or
            rather to the macros that are running in their software.
            See `run_mate.py` for more info.

@usage:     Called by `run_mate.py`.
"""


import os
import winreg as winr


def _write_reg(key, name, value):
    """Write value to key[name] in the Windows registry.
    Assumes HKEY_CURRENT_USER as base key.
    """

    # Create or open the key
    registry_key = winr.CreateKeyEx(
        winr.HKEY_CURRENT_USER, key, 0, winr.KEY_WRITE
    )

    # Set the key value
    # print "~~", registry_key,name,value
    winr.SetValueEx(registry_key, name, 0, winr.REG_SZ, str(value))

    # Close the key
    winr.CloseKey(registry_key)


def send_coords_txt(
    fpath, z_pos=None, y_pos=None, x_pos=None, msg="_", precision=4
):
    """Communicate new position for stage movement to the microscope through a
    text file, which should be monitored by the microscope software's macro.

    A new file with header is generated if the file at the provided path does
    not exist yet. Otherwise new data is appended at the end of the file.

    Parameters
    ----------
    fpath : path-like
        Path to the coordinate text file.
    z_pos, y_pos, x_pos : numeric, optional, default 0.0
        Cooordinates of the new imaging position. For any that are None, the
        string value "nan" will be written in place of a coordinate number.
    msg : str, optional, default "_"
        String message to write in 4th column of text file.
    precision : int, optional, default 4
        Number of decimal places to write for coordinate values.
    """

    # Prep
    p = precision
    z_pos, y_pos, x_pos = [
        f"{pos:.{p}f}" if pos is not None else "nan"
        for pos in [z_pos, y_pos, x_pos]
    ]

    # Write new coordinates
    with open(fpath, "a") as coordsfile:
        coordsfile.write(f"{z_pos}\t{y_pos}\t{x_pos}\t{msg}\n")


def send_coords_winreg(
    z_pos=None, y_pos=None, x_pos=None, codeM="focus", errMsg=None
):
    """Communicate new position for stage movement to the microscope through
    the Windows registry, then prime it for imaging in the way expected by the
    MyPiC Pipeline Constructor macro. The actual acquisition will be triggered
    once the scope is idle.

    Parameters
    ----------
    z_pos, y_pos, x_pos : numeric, optional, default None
        Cooordinates of the new imaging position. For any that are None, the
        registry entry is left unchanged.
    codeM : str, optional, default "focus"
        Action for the microscope to take. Default is "focus", which triggers
        a move to the updated coordinates and acquisition as soon as the scope
        is idle. See MyPiC documentation for more information.
    errMsg: str, optional, default None
        An optional error message for MyPiC to copy to its log file.
    """

    # Set registry addresses
    reg_key = r"SOFTWARE\VB and VBA Program Settings\OnlineImageAnalysis\macro"
    name_zpos = "Z"
    name_ypos = "Y"
    name_xpos = "X"
    name_codemic = "codeMic"
    name_errormsg = "errorMsg"

    # Submit the new positions
    if z_pos is not None:
        _write_reg(reg_key, name_zpos, z_pos)
    if y_pos is not None:
        _write_reg(reg_key, name_ypos, y_pos)
    if x_pos is not None:
        _write_reg(reg_key, name_xpos, x_pos)

    # Submit the error message, if any
    if errMsg is not None:
        _write_reg(reg_key, name_errormsg, errMsg)

    # Submit codeM, triggering microscope action
    _write_reg(reg_key, name_codemic, codeM)
