# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Functions for sending coordinates and commands to microscopes (or 
            rather to the macros they are running).
            For more information see `run_mate.py`.
            
@usage:     Called by `run_mate.py`.
"""


### Imports

import os
import winreg as winr

     
### Helper function to write to Windows registry

def _write_reg(key, name, value):
    """Write value to key[name] in the Windows registry.
    Assumes HKEY_CURRENT_USER as base key.
    Returns True if successful, False otherwise.
    """
    
    try:

        # Create or open the key
        registry_key = winr.CreateKeyEx(
            winr.HKEY_CURRENT_USER, key, 0, winr.KEY_WRITE)
        
        # Set the key value
        #print "~~", registry_key,name,value
        winr.SetValueEx(registry_key, name, 0, winr.REG_SZ, str(value))
        
        # Close the key
        winr.CloseKey(registry_key)
        
        # Done
        return True
    
    # If things went wrong
    except WindowsError:
        return False


### Function to send coordinates to scope via a txt file

def send_coords_txt(
    fpath, z_pos=None, y_pos=None, x_pos=None, codeM='focus'):
    """Communicate new position for stage movement to the microscope through a
    text file, which should be monitored by the microscope software's macro.

    Parameters
    ----------
    fpath : str
        Path to the coordinate text file.
    z_pos, y_pos, x_pos : integers, optional
        Cooordinates of the new imaging position. Will be None if not given; in 
        this case, nothing new will be written to the coordinate file.
    codeM : string, optional
        Action for the microscope to take.
        Default is 'focus'.
        
    Returns
    -------
    no_error : bool
        True if file writing operation completed without an error.
        False otherwise.
    """

    # Create the file if it doesn't exist yet
    if not os.path.isfile(fpath):
        with open(fpath, 'w') as coordsfile:
            coordsfile.write('Z\tY\tX\tcodeM\n')  # Write header
       
    # Track if all goes well
    no_error = True

    # Write new coordinates
    try:
        with open(fpath, "a") as coordsfile:
            coordsfile.write(f"{z_pos}\t{y_pos}\t{x_pos}\t{codeM}\n")

    # Handle failure cases
    # FIXME: This is too unspecific and should be revisited in the context of
    #        the fallback measures implemented in `run_mate.py`!
    except Exception: 
        no_error = False
    
    # Return
    return no_error


### Function to send coordinates to scope via windows registry

def send_coords_winreg(
    z_pos=None, y_pos=None, x_pos=None, codeM='focus', errMsg=None):
    """Communicate new position for stage movement to the microscope through 
    the Windows registry, then prime it for imaging in the way expected by the
    MyPiC Pipeline Constructor macro. The actual acquisition will be triggered
    once the scope is idle.
        
    Parameters
    ----------
    z_pos, y_pos, x_pos : integers, optional
        Cooordinates of the new imaging position. Will be None if not given; in 
        this case, nothing new will be written to the respective keys.
    codeM : string, optional
        Action for the microscope to take.
        Default is 'focus'.
    errMsg: string, optional
        An error message for the pipeline constructor to log.
        Default is None.
        
    Returns
    -------
    no_error : bool
        True if all registry operations were completed without an error.
        False otherwise.
    """

    # Set registry addresses
    reg_key = r'SOFTWARE\VB and VBA Program Settings\OnlineImageAnalysis\macro'
    name_zpos = 'Z'
    name_ypos = 'Y'
    name_xpos = 'X'
    name_codemic  = 'codeMic'
    name_errormsg = 'errorMsg'
    
    # Track if all goes well
    no_error = True
    
    # Submit the new positions
    if z_pos is not None: 
        no_error &= _write_reg(reg_key, name_zpos, z_pos)
    if y_pos is not None: 
        no_error &= _write_reg(reg_key, name_ypos, y_pos)
    if x_pos is not None: 
        no_error &= _write_reg(reg_key, name_xpos, x_pos)
        
    # Error message if something goes wrong;
    # Note: The MyPiC pipeline constructor copies this message to its log file.
    if errMsg: 
        no_error &= _write_reg(reg_key, name_errormsg, errMsg)
    
    # Message to microscope what to do
    no_error &= _write_reg(reg_key, name_codemic, codeM)
    
    # Return
    return no_error


### handle direct calls

if __name__ == '__main__':
    raise Exception("Can't run this module directly. See 'python run_mate.py -h' for help.")



