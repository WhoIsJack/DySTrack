# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Image analysis pipeline for live tracking of the posterior lateral
            line primordium using MATE.
            See `run_mate.py` for more info.

@usage:     Called by `run_mate.py`.
"""

import os
from time import sleep
from warnings import simplefilter, warn

simplefilter("always", UserWarning)

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi
from aicsimageio import AICSImage


def analyze_image(target_file, channel=None, show=False, verbose=False):
    """Compute new positions for the microscope to track the zebrafish lateral
    line primordium's movement based on a 2D or 3D image. The primordium is
    masked using object-count thresolding. The new y (and z, if 3D) positions
    are computed as the respective centers of mass of the image. The new x
    position is computed relative to the leading edge position of the mask.

    Parameters
    ----------
    target_file : path-like
        Path to the image file that is to be analyzed.
    channel : int, optional
        Channel to use for masking in case of multi-channel images.
        If channel is not specified, a single-channel image is assumed.
    show :  bool, optional
        Whether to show the threshold plot and the mask. Default is False.
        WARNING: Showing figures halts execution until they are closed.  # FIXME!
    verbose: bool, optional
        If True, more information is printed.

    Returns
    -------
    z_pos, y_pos, x_pos : ints
        New coordinates for the next acquisition.
        For 2D inputs, z_pos is always 0.
    """

    # TODO: Think about how best to expose the various image analysis params
    #       of this pipeline to the user. Adding them as kwargs seems of little
    #       use without cmdline forwarding in run_mate.py, so either a config
    #       file or just a parameter section here at the top might be best?

    ### Load data

    # Make multiple attempts in case loading fails
    attempts_left = 5
    file_size = -1
    while True:

        # Wait until the file is no longer being written to
        # Note: In some cases microscope software may intermittently stop
        #       writing, so this is not a perfect check for whether the file
        #       is complete, hence the multiple attempts!
        while True:
            sleep(2)
            new_file_size = os.stat(target_file).st_size
            if new_file_size > file_size:
                file_size = new_file_size
                attempts_left = 5
            else:
                break

        # If the file writing looks done, make a loading attempt
        try:
            if target_file.split(".")[-1] in ["tif", "tiff", "czi", "nd2"]:
                raw = AICSImage(target_file)
                raw = raw.data
                raw = np.squeeze(raw)

            # Handle unknown file endings
            else:
                errmsg = (
                    "File ending not recognized! Use `run_mate -e END` to "
                    + "control which file endings trigger image analysis."
                )
                raise ValueError(errmsg)

            # Some basic checks to ensure a loader didn't fail silently...
            if not isinstance(raw, np.ndarray):
                errmsg = (
                    "Loaded image object is not instance of `np.array`,"
                    + " indicating that the loader has failed silently!"
                )
                raise IOError(errmsg)
            if raw.size == 0:
                errmsg = (
                    "Loaded image array is of size 0, indicating that"
                    + "that the loader has failed silently!"
                )
                raise IOError(errmsg)

            # Exit the loop of loading attempts if loading was successful
            break

        # In case of failure, retry if there are still attempts left,
        # otherwise raise the Exception
        except Exception as err:
            attempts_left -= 1
            if attempts_left == 0:
                print(
                    f"\n  Multiple attempts to load the image have failed;",
                    "the final one with this Exception:\n  ",
                    repr(err),
                    "\n",
                )
                raise
            else:
                sleep(2)

    # Report
    if verbose:
        print("      Loaded image of shape:", raw.shape)

    # Check dimensionality
    if raw.ndim > 4:
        raise IOError("Image dimensionality >4; this cannot be right!")
    elif raw.ndim < 2:
        raise IOError("Image dimensionality <2; this cannot be right!")
    elif raw.ndim < 3 and channel is not None:
        raise IOError("CHANNEL given but image dimensionality is only 2!")
    elif raw.shape[0] > 5 and channel is not None:
        warn(f"CHANNEL given but image dim 0 is of size {raw.shape[0]}!")

    # If there are multiple channels, select the one to use
    if channel is not None:
        raw = raw[channel, ...]

    # If the image is not 8bit, convert it
    # NOTE: This conversion scales min to 0 and max to 255!
    if raw.dtype != np.uint8:
        warn("Image had to be converted down to 8bit!")
        raw = (
            (raw.astype(float) - raw.min()) / (raw.max() - raw.min()) * 255
        ).astype(np.uint8)

    # Show loaded image
    if show and raw.ndim == 3:
        plt.imshow(np.max(raw, axis=0), interpolation="none", cmap="gray")
        plt.show()

        ## DEV-TEMP: Plot without blocking (untested; work in progress)  # TODO!
        # plt.ion()
        # plt.show(block=False)
        # plt.imshow(np.max(raw, axis=0),interpolation="none",cmap="gray")
        # plt.draw()
        # plt.pause(0.001)  # To give mpl time to draw
        # plt.pause(2.0)    # To give user time to view (optional)

    elif show and raw.ndim == 2:
        plt.imshow(raw, interpolation="none", cmap="gray")
        plt.show()

    ### Mask by object-count thresholding

    # Note: Masking 3D images in full 3D is feasible because we really use a
    #       low-res image with very few pixels. If we were to change this, it
    #       may make sense to use the older alternative approach (see build 1)
    #       because this is much slower, plus it would definitely need some
    #       erosion to prevent skin-cell artifacts...
    # TODO: The above is an old note; look into this!

    # Preprocessing: Gaussian smoothing
    # Note 1: The sigma param here seems to be very important. If it is set
    #         improperly, masking can fail. However, it seems to work fairly
    #         robustly if it's simply at `3` and it seems to be relatively
    #         insensitve to pixel size / resolution!
    # Note 2: sigma = 3 good for cldnb with skin bg
    #         sigma = 1 good for KTR green with little bg
    # TODO: Think of a more robust/generalized approach!
    raw = ndi.gaussian_filter(raw, 3)  # Param!

    # Preparations
    thresh_div = 2.0  # Param!
    thresholds = np.arange(0, 256, 1)
    counts = np.zeros_like(thresholds)

    # Run threshold series
    for index, threshold in enumerate(thresholds):

        # Apply current threshold and count objects
        counts[index] = ndi.label(raw >= threshold)[1]

    # Smoothen the thresholds a bit
    counts_smooth = ndi.gaussian_filter1d(counts, 3)

    # Get the target threshold
    for threshold in thresholds[1:255]:

        # Criterion 1: Is there a threshold before the current one that has more objects?
        if np.max(counts_smooth[:threshold]) > counts_smooth[threshold]:

            # Criterion 2a: Is the current value below the maximum value divided by thresh_div?
            # FIXME: This criterion doesn't seem particularly robust!
            if counts_smooth[threshold] <= (
                np.max(counts_smooth[:threshold]) / thresh_div
            ):
                break

            # Criterion 2b: Alternatively, if the threshold is followed by an
            #               increase in counts again (i.e. it is a local min)
            # FIXME: If there ever is an "early dip" despite smoothing, this
            #        will lead to a low threshold being accepted!
            elif counts_smooth[threshold + 1] > counts_smooth[threshold]:
                break

    # Fallback: If the detected threshold has 0 objects, take the next one
    #           before that had some objects. Note that this is important since
    #           the smoothing will often stretch the curve out too far, leading
    #           to thresholds that yield no objects when applied to the image!
    # FIXME: Robustness...
    if counts[threshold] == 0:
        for backstep in range(1, threshold):
            if counts[threshold - backstep] > 0:
                threshold = threshold - backstep
                break

    # Terminal fallback: If the final result is still nonesense, give up
    if threshold >= 250 or threshold == 0 or counts[threshold] == 0:
        raise Exception(
            "THRESHOLD DETECTION FAILED! Image analysis run aborted..."
        )

    # Binarize with the target threshold
    if verbose:
        print("      Detected treshold:", threshold)
    mask = raw >= threshold

    # TODO: Add plotting before largest-object retention step?

    # Retain only largest object
    img_bin_labeled = ndi.label(mask)[0]
    obj_nums, obj_sizes = np.unique(img_bin_labeled, return_counts=True)
    largest_obj = np.argmax(obj_sizes[1:]) + 1
    mask[img_bin_labeled != largest_obj] = 0

    # Show threshold series and resulting mask
    # TODO: Clean this up and make it non-blocking!
    if show:

        # Plot of counts over threshold series
        plt.plot(counts_smooth)
        plt.plot(counts)
        plt.vlines(threshold, 0, counts.max(), color="g")
        plt.show()

        # Plots of final masks
        if mask.ndim == 3:
            plt.imshow(np.max(mask, axis=0), interpolation="none", cmap="gray")
            plt.show()
            plt.imshow(np.max(mask, axis=1), interpolation="none", cmap="gray")
            plt.show()
        else:
            plt.imshow(mask, interpolation="none", cmap="gray")
            plt.show()

    ### Find new z and y positions

    # Get centroid
    cen = ndi.center_of_mass(mask)

    # Get positions for 3D
    if raw.ndim == 3:

        # Use centroid positions as focusing targets
        z_pos = cen[0]
        y_pos = cen[1]

        # z limit: An absolute limitation on how much it can move!
        z_limit = 0.1  # Fraction of image size
        z_limit_top = (raw.shape[0] - 1) / 2.0 + z_limit * (raw.shape[0] - 1)
        z_limit_bot = (raw.shape[0] - 1) / 2.0 - z_limit * (raw.shape[0] - 1)
        if z_pos > z_limit_top:
            warn("z_pos > z_limit_top; using z_limit_top!")
            z_pos = z_limit_top
        if z_pos < z_limit_bot:
            warn("z_pos < z_limit_bot; using z_limit_bot!")
            z_pos = z_limit_bot

        ## Invert resulting z_position for scope frame of reference
        # z_pos = (raw.shape[0]-1) - z_pos

    # Get positions for 2D
    else:
        z_pos = None
        y_pos = cen[0]

    ### Find leading edge position

    # Collapse to x axis
    if raw.ndim == 3:
        collapsed = np.max(np.max(mask, axis=0), axis=0)
    else:
        collapsed = np.max(mask, axis=0)

    # Find frontal-most non-zero pixel
    front_pos = np.max(np.nonzero(collapsed)[0])

    ### Check if leading edge position is sensible

    # NOTE: This check is rather simple at the moment; it just asks if the new
    #       position is in the leading half of the img but not at the very end.
    # TODO: Optimize this?! It currently handles problems by moving a default
    #       amount, which is not ideal! Also, the check itself could surely
    #       be more refined.

    # If the tip of the mask is behind the center of the image...
    if front_pos < collapsed.shape[0] / 2.0:

        # In this case, the mask probably missed a lot at the tip...
        warn(
            "The detected front_pos is too far back, likely due to a masking error. Moving default distance."
        )

        # Handle it...
        default_step_fract = 1.0 / 8.0  # Param!
        x_pos = (
            0.5 * collapsed.shape[0] + default_step_fract * collapsed.shape[0]
        )
        if verbose:
            print(
                f"      Resulting coords (zyx): {z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
            )
        return z_pos, y_pos, x_pos

    # If the tip of the mask touches the front end of the image
    elif front_pos == collapsed.shape[0] - 1:

        # In this case, the prim has probably moved out of the frame
        warn(
            "The prim has probably moved out of the frame. Moving default catch-up distance."
        )

        # Handle it...
        default_catchup_fract = 1.0 / 5.0  # Param!
        x_pos = (
            0.5 * collapsed.shape[0]
            + default_catchup_fract * collapsed.shape[0]
        )
        if verbose:
            print(
                f"      Resulting coords (zyx): {z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
            )
        return z_pos, y_pos, x_pos

    ### Compute new x-position for scope

    # NOTE: This is currently based on putting 1/5th of the image size between
    #       the current leading edge and the end of the image. This is an
    #       estimate that should work for standard image sizes and timecourses
    #       of about 5min per timepoint.
    # TODO: Optimize this to be 'more adaptive'! Some notes on options:
    #       - Use real scale instead of pixel scale to make it more robust
    #       - Use speed to calculate next position; initially based on prior
    #         data, then based on previous timepoints.
    #       - Use some controller function (PID?) to buffer speed variability
    #         and masking errors?
    blank_fract = 1.0 / 5.0
    x_pos = (
        front_pos + blank_fract * collapsed.shape[0] - 0.5 * collapsed.shape[0]
    )

    ### Return results

    if verbose:
        print(
            f"      Resulting coords (zyx): {z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
        )
    return z_pos, y_pos, x_pos


# Handle direct calls

if __name__ == "__main__":
    raise Exception(
        "Can't run this module directly. See 'python run_mate.py -h' for help."
    )
