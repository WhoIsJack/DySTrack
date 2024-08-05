# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@author:    Jonas Hartmann @ Gilmour group @ EMBL Heidelberg

@descript:  Image analysis pipeline for prim tracking on the 880.
            For more information see pt880_start.

@usage:     Called by pt880_start.
"""


#------------------------------------------------------------------------------

# PREPARATION

# General imports
from __future__ import division
import os
import numpy as np
import scipy.ndimage as ndi
import matplotlib.pyplot as plt
from warnings import simplefilter,warn
simplefilter('always',UserWarning)

# Specific imports
from time import sleep
from tifffile import imread as tifread
from czifile import imread as cziread


#------------------------------------------------------------------------------

# FUNCTION FOR IMAGE ANALYSIS STEPS

def analyze_image(target_file,channel=None,show=False,verbose=False):
    """
        Compute appropriate new positions for the microscope to track prim
        movement based on a 2D or 3D image. New y (and z, if 3D) positions are
        computed as respective centers of mass of the image. The new x position
        is computed relative to the leading edge position as determined by
        object-count threshold masking of the image (for 2D) or of its center-
        of-mass slice (for 3D).

        Parameters
        ----------
        target_file : path-like
            Path to the file that is to be analyzed.
        channel : int, optional
            Channel to use for masking in case of multi-channel images.
            If channel is not specified, a single-channel image is assumed.
        show:  bool, optional
            Whether to show the threshold plot and the mask.
            Default is False.
        verbose: bool, optional
            If true, more information is printed.

        Returns
        -------
        z_pos,y_pos,x_pos : ints
            New coordinates for the next acquisition. For 2D inputs, z_pos is
            always 0.
    """


    #..........................................................................

    # DATA LOADING

    # Make sure the file has finished writing
    # NOTE: This works in general but still seems to randomly fail sometimes.
    sleep(2)  # Initial delay; helps with stability
    file_size = -1
    while True:
        new_file_size = os.stat(target_file).st_size
        if new_file_size > file_size:
            file_size = new_file_size
            sleep(2)
        else:
            break

    # Loading the image if it is a tif
    if target_file.endswith('.tif'):
        raw = tifread(target_file)
        if verbose: print "~~LOADED IMG SHAPE:", raw.shape

    # Loading the image if it is a czi
    # NOTE: This uses Christoph Gohlke's czifile, which does not seem to be as
    #       stable and well-maintained as his tifffile. It may be better to go
    #       with bio-formats (loci) instead. However, the advantage of czifile
    #       is that it is pure (c)python (no javabridge required).
    if target_file.endswith('.czi'):
        raw = cziread(target_file)
        raw = np.squeeze(raw)           # Remove excess dimensions
        if verbose: print "~~LOADED IMG SHAPE:", raw.shape

    # Check dimensionality
    if raw.ndim > 4:
        raise IOError("Image dimensionality exceeds 4; this cannot be right!")
    elif raw.ndim < 2:
        raise IOError("Image dimensionality lower than 2; this cannot be right!")
    elif raw.ndim < 3 and channel is not None:
        raise IOError("CHANNEL given but image dimensionality cannot contain multiple channels!")
    elif raw.shape[0] > 5 and channel is not None:
        raise IOError("CHANNEL given but image size suggests it does not contain multiple chanels!")

    # If there are multiple channels, select the one to use
    if channel is not None:
        raw = raw[channel,...]

    # If the image is not 8bit, convert it
    # NOTE: This conversion scales min to 0 and max to 255!
    if raw.dtype != np.uint8:
        warn("Image had to be converted down to 8bit!")
        raw = ( (raw.astype(np.float) - raw.min()) / (raw.max() - raw.min()) * 255 ).astype(np.uint8)

    # Show loaded image
    if show and raw.ndim == 3:
        plt.imshow(np.max(raw,axis=0),interpolation="none",cmap="gray")
        plt.show()
    elif show and raw.ndim == 2:
        plt.imshow(raw,interpolation="none",cmap="gray")
        plt.show()


    #..........................................................................

    # MASKING BY OBJECT-COUNT THRESHOLDING
    # Note: Masking 3D images in full 3D is feasible because we really use a
    #       low-res image with very few pixels. If we were to change this, it
    #       may make sense to use the older alternative approach (see build 1)
    #       because this is much slower, plus it would definitely need some
    #       erosion to prevent skin-cell artefacts...

    # Preprocessing: gaussian smoothing
    # Note: The sigma param here seems to be very important. If it is set
    #       improperly, masking can fail. However, it seems to work fairly
    #       robustly if it's simply at `3` and it seems to be relatively
    #       insensitve to pixel size / resolution!
    raw = ndi.gaussian_filter(raw,3)       # Param!

    # Preparations
    thresh_div = 2.0    # XXX: Robustness?  # Param!
    thresholds = np.arange(0,256,1)
    counts = np.zeros_like(thresholds)

    # Run threshold series
    for index,threshold in enumerate(thresholds):

        # Apply current threshold and count objects
        counts[index] = ndi.label(raw>=threshold)[1]

    # Smooth the thresholds a bit
    counts_smooth = ndi.gaussian_filter1d(counts,3)

    # Get the target threshold
    for threshold in thresholds[1:255]:

        # Criterion 1: Is there a threshold before the current one that has more objects?
        if np.max(counts_smooth[:threshold]) > counts_smooth[threshold]:

            # Criterion 2a: Is the current value below the maximum value divided by thresh_div?
            if counts_smooth[threshold] <= (np.max(counts_smooth[:threshold]) / thresh_div):
                break

            # Criterion 2b: Alternatively, if the threshold is followed by an
            #               increase in counts again (i.e. it is a local min.)
            # XXX: If there ever is an "early dip" despite smoothing, this will
            #      lead to a low threshold being accepted!
            elif counts_smooth[threshold+1] > counts_smooth[threshold]:
                break

    # Fallback: If the detected threshold has 0 objects, take the next one
    #           before that had some objects. Note that this is important since
    #           the smoothing will often stretch the curve out too far, leading
    #           to thresholds that yield no objects when applied to the image!
    if counts[threshold] == 0:
        for backstep in range(1,threshold):
            if counts[threshold-backstep] > 0:
                threshold = threshold-backstep
                break

    # Terminal fallback: If the final result is still nonesense, give up
    if threshold >= 250 or threshold == 0 or counts[threshold] == 0:
        raise Exception("THRESHOLD DETECTION FAILED! Image analysis run aborted...")

    # Binarize with the target threshold
    if verbose: print "~~THRESHOLD:", threshold
    mask = raw >= threshold

    # Retain only largest object
    img_bin_labeled = ndi.label(mask)[0]
    obj_nums,obj_sizes = np.unique(img_bin_labeled,return_counts=True)
    largest_obj = np.argmax(obj_sizes[1:])+1
    mask[img_bin_labeled!=largest_obj] = 0

    # Show stuff (DEV)
    if show:
        plt.plot(counts_smooth)
        plt.plot(counts)
        plt.vlines(threshold,0,counts_smooth[threshold])
        plt.show()
        if mask.ndim == 3:
            plt.imshow(np.max(mask,axis=0),interpolation="none",cmap="gray")
            plt.show()
            plt.imshow(np.max(mask,axis=1),interpolation="none",cmap="gray")
            plt.show()
        else:
            plt.imshow(mask,interpolation="none",cmap="gray")
            plt.show()
        #from tifffile import imsave # DEV!
        #imsave(os.path.join(os.path.split(target_file)[0],"DEV_TEMP.tif"),mask.astype(np.uint8),bigtiff=True)


    #..........................................................................

    # FIND NEW Z AND Y POSITIONS

    # Get centroid
    cen = ndi.measurements.center_of_mass(mask)

    # Get positions for 3D
    if raw.ndim == 3:

        # Use centroid positions as focusing targets
        z_pos = cen[0]
        y_pos = cen[1]

        # z limit: An absolute limitation on how much it can move!
        z_limit = 1.0 / 10.0     # Fraction of image size
        z_limit_top = (raw.shape[0]-1)/2.0 + z_limit * (raw.shape[0]-1)
        z_limit_bot = (raw.shape[0]-1)/2.0 - z_limit * (raw.shape[0]-1)
        if z_pos > z_limit_top:
            warn("z_pos > z_limit_top; using z_limit_top!")
            z_pos = z_limit_top
        if z_pos < z_limit_bot:
            warn("z_pos < z_limit_bot; using z_limit_bot!")
            z_pos = z_limit_bot

        # Invert resulting z_position for scope frame of reference
        z_pos = (raw.shape[0]-1) - z_pos  # Inversion for scope frame of ref


    # Get positions for 2D
    else:
        z_pos = None
        y_pos = cen[0]


    #..........................................................................

    # FIND LEADING EDGE X-POSITION

    # Collapse to x axis
    if raw.ndim == 3:
        collapsed = np.max(np.max(mask,axis=0),axis=0)
    else:
        collapsed = np.max(mask,axis=0)

    # Find frontal-most non-zero pixel
    front_pos = np.max(np.nonzero(collapsed)[0])


    #..........................................................................

    # CHECK IF LEADING EDGE POSITION IS SENSIBLE

    # NOTE: This check is rather simple at the moment; it just asks if the new
    #       position is in the leading half of the img but not at the very end.
    # TODO: Optimize this?! It currently handles problems by moving a default
    #       amount, which is not ideal! Also, the check itself could surely
    #       be more refined.

    # If the tip of the mask is behind the center of the image...
    if front_pos < collapsed.shape[0] / 2.0:

        # In this case, the mask probably missed a lot at the tip...
        warn("The detected front_pos is too far back, likely due to a masking error. Moving default distance.")

        # Handle it...
        default_step_fract = 1.0/8.0
        x_pos = 1.0/2.0 * collapsed.shape[0] + default_step_fract * collapsed.shape[0]
        if verbose: print "~~RESULT:", z_pos,y_pos,x_pos
        return z_pos,y_pos,x_pos

    # If the tip of the mask touches the front end of the image
    elif front_pos == collapsed.shape[0] - 1:

        # In this case, the prim has probably moved out of the frame
        warn("The prim has probably moved out of the frame. Moving default catch-up distance.")

        # Handle it...
        default_catchup_fract = 1.0/5.0
        x_pos = 1.0/2.0 * collapsed.shape[0] + default_catchup_fract * collapsed.shape[0]
        if verbose: print "~~RESULT:", z_pos,y_pos,x_pos
        return z_pos,y_pos,x_pos


    #..........................................................................

    # COMPUTE NEW X-POSITION FOR SCOPE

    # NOTE: This is currently based on putting 1/5th of the image size between
    #       the current leading edge and the end of the image. This is an
    #       estimate that should work for standard image sizes and timecourses
    #       of about 5min per timepoint.
    # TODO: Optimize this to be 'more adaptive'! Some notes on options:
    #       - Use real scale instead of pixel scale to make it more robust
    #       - Use speed to calculate next position; initially based on prior
    #         data, then based on previous timepoints.
    #       - Use some controller function (PID?) to buffer speed variability
    #         and masking errors.
    blank_fract = 1.0/5.0
    x_pos = front_pos + blank_fract * collapsed.shape[0] - 1.0/2.0 * collapsed.shape[0]


    #..........................................................................

    # RETURN RESULTS

    if verbose: print "~~RESULT:", z_pos,y_pos,x_pos
    return z_pos,y_pos,x_pos


#------------------------------------------------------------------------------

# HANDLE DIRECT CALLS

if __name__ == '__main__':
    raise Exception("This module is not designed to be called directly. See 'pt880_start -h' for help.")


#------------------------------------------------------------------------------



