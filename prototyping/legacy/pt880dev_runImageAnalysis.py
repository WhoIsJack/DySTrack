# -*- coding: utf-8 -*-
"""
Created on Fri Jan 20 11:08:37 2017

@author:    Jonas Hartmann @ Gilmour group @ EMBL Heidelberg

@descript:  Script to just run the image analysis function of pt880. Useful for
            development and testing. For more details, see pt880_start.
            
@usage:     Run from IDE.
"""


#------------------------------------------------------------------------------


# PREPARATION

# General imports
from __future__ import division
#import os
#import numpy as np
#import scipy.ndimage as ndi
#import matplotlib.pyplot as plt
from warnings import simplefilter
simplefilter('always',UserWarning)


#------------------------------------------------------------------------------

# PARAMETER SPECIFICATION 

## Test img 1: 2D example 1
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/2D/both1_1.tif'
#channel = 1

## Test img 2: 3D example 1
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/3D/e4_515XnucTom_40xH2O_fastOpt2Col_deconv.czi'
#channel = 0

## Test img 3: 3D example 2
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/3D/e5_515_40xH2O_fastOpt_deconv.czi'
#channel = None

## Test img from AIRY 1 ON SCOPE [OLD]
#filename = r'T:\Users\Jonas\images\im_DE_W0001_P0001\im_DE_1_W0001_P0001_T0001.tif'
#channel = None

## Test img from AIRY 1 ON SCOPE [OLD]
#filename = r'T:/Users/Jonas/images/im_DE_W0001_P0001/im_DE_1_W0001_P0001_T0001.czi'
#channel = None

## Test img 4: 3D true low res
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/low_res_1.czi'
#channel = None

## Test img 5: 3D true low res 2
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/low_res_2.czi'
#channel = None

## Test img 6: 3D true low res 3
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/low_res_3.czi'
#channel = None

## Test img 7: 3D true low res from first run 1
## Note: Example of early embryo...
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/low_res_run1_1.czi'
#channel = None

## Test img 8: 3D true low res from first run 2
## Note: Example of early embryo...
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/low_res_run1_2.czi'
#channel = None

## Test img 9: 3D low res that didn't work in run 1 ON SCOPE
#filename = r'D:/Users/Jonas/20170124 - pt880 Online Run 1 - 880/im_DE_W0004_P0001/im_DE_1_W0004_P0001_T0004.czi'
#channel = None

## Test img 10: 3D low res (run 2, embryo 1, time point 19)
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/issuesData1.czi'
#channel = None

## Test img 10: 3D low res (run 1, embryo 4, time point 5)
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/issuesData2.czi'
#channel = None

## Test img 10: 3D low res (run 2, embryo 3, time point 16); z-shift issue (masking)
#filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/issuesData3.czi'
#channel = None

# Test img 10: 3D low res (run 2, embryo 4, time point 25); z-shift issue (z-shift? masking?)
filename = r'C:/Users/Jonas Hartmann/Data/c) EMBL PhD/C Segmentation & Analysis/PY Adaptive Feedback 880/testData/from880/issuesData4.czi'
channel = None

## QUICK TEST
#filename = r'T:/Users/Jonas/images/Test/im_DE_W0001_P0001/im_DE_1_W0001_P0001_T0001.czi'
#channel = None


#------------------------------------------------------------------------------

# CALL THE ANALYSIS FUNCTION

from pt880_analyze import analyze_image
z_pos,y_pos,x_pos = analyze_image(filename,channel=channel,show=True,verbose=True)
print "Returned coords were:"
print "  z:", z_pos
print "  y:", y_pos
print "  x:", x_pos


#------------------------------------------------------------------------------














