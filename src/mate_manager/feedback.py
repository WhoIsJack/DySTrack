# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@author:    Jonas Hartmann @ Gilmour group @ EMBL Heidelberg

@descript:  Functions for interacting with the LSM880 through the registry.
            For more information see pt880_start.
            
@usage:     Called by pt880_start.
"""


#------------------------------------------------------------------------------

# PREPARATION

# General imports
from __future__ import division
#import sys,os
#import numpy as np
#import scipy.ndimage as ndi
#import matplotlib.pyplot as plt
from warnings import simplefilter
simplefilter('always',UserWarning)

# Specific imports
import winreg as winr

     
#------------------------------------------------------------------------------

# FUNCTION FOR WRITING TO WINDOWS REGISTRY

def write_reg(key,name,value):
    """
        Write value to key[name] in the Windows registry. 
        Assumes HKEY_CURRENT_USER as base key.
        Returns True if successful, False otherwise.
    """
    
    try:
        
        # Create or open the key
        registry_key = winr.CreateKeyEx(winr.HKEY_CURRENT_USER,key,
                                        0,winr.KEY_WRITE)
        
        # Set the key value
        #print "~~", registry_key,name,value
        winr.SetValueEx(registry_key,name,0,winr.REG_SZ,str(value))
        
        # Close the key
        winr.CloseKey(registry_key)
        
        # Done
        return True
    
    # If things went wrong
    except WindowsError:
        global no_error
        no_error = False
        return False


#------------------------------------------------------------------------------

# FUNCTION FOR SCOPE COMMUNICATION

def send_xyz_to_scope(z_pos=None,y_pos=None,x_pos=None,codeM='focus',errMsg=None):
    """
        Communicate new position for imaging to the microscope through the
        Windows registry, then prime it for imaging (the actual acquisition
        will be triggered when the scope is idle).
        
        Parameters
        ----------
        z_pos,y_pos,x_pos : integers, optional
            Cooordinates of the new imaging position.
            Will be None if not given; in this case, nothing new will be
            written to the respective keys.
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
    global no_error
    no_error = True    
    
    # Submit the new positions
    if z_pos is not None: write_reg(reg_key,name_zpos,z_pos)
    if y_pos is not None: write_reg(reg_key,name_ypos,y_pos)
    if x_pos is not None: write_reg(reg_key,name_xpos,x_pos)
        
    # Error message if something goes wrong;
    # pipeline constructor copies this message to its log file
    if errMsg: write_reg(reg_key,name_errormsg,errMsg)
    
    # Message to microscope what to do.
    write_reg(reg_key,name_codemic,codeM)
    
    # Return
    return no_error


#------------------------------------------------------------------------------

# HANDLE DIRECT CALLS

if __name__ == '__main__':
    raise Exception("This module is not designed to be called directly. See 'pt880_start -h' for help.")


#------------------------------------------------------------------------------



