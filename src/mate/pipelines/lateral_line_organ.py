# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Image analysis pipeline for live tracking/stabilizing of deposited
            posterior lateral line primordium organs (neuromasts) using MATE.
            This is a very simple adaptation of lateral_line.py, with the only
            difference being that x is computed as the centroid of the mask
            (just like y and z), not as the leading edge.
            TODO: There's room for customizing this further for its purpose!
"""

import os
from time import sleep
from warnings import simplefilter, warn

simplefilter("always", UserWarning)

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi
from aicsimageio import AICSImage


def analyze_image(
    target_path,
    channel=None,
    gauss_sigma=3.0,
    count_reduction=0.5,
    show=False,
    verbose=False,
):
    """Compute new coordinates for the scope to track/stabilize neuromasts, the
    organs deposited by the zebrafish lateral line primordium. They are not
    particularly motile, so this is more about microscope stage drift.

    This is a simple adaptation of lateral_line.py and therefore also based on
    object-count thresholding. It only differs from the other pipeline insofar
    as the new x positions (just like z and y), are based on the center of mass
    instead of tracking the leading edge.

    Note: This was developed for and (mainly) tested on the cldnb:EGFP line.
    While it has been used for some other lines with adjusted parameters, it is
    absolutely not guaranteed to work universally.

    Parameters
    ----------
    target_path : path-like
        Path to the image file that is to be analyzed.
    channel : int, optional, default None
        Index of channel to use for masking in case of multi-channel images.
        If not specified, a single-channel image is assumed.
    gauss_sigma : float, optional, default 3.0
        Sigma for Gaussian filter prior to masking.
    count_reduction : float, optional, default 0.5
        Factor by which object count has to be reduced below its initial peak
        for a threshold value to be accepted.
    show : bool, optional, default False
        Whether to show the threshold plot and the mask. Default is False.
        Note that figures will be shown without blocking execution, so if many
        iterations are performed, many figures will be opened. Also, note that
        all figures will be closed when the python process exits.
    verbose : bool, optional, default False
        If True, more information is printed.

    Returns
    -------
    z_pos, y_pos, x_pos : ints
        New coordinates for the next acquisition. For 2D inputs, z_pos is None.
    img_msg : "_"
        A string output message; required by MATE but here unused; set to "_".
    img_cache : {}
        A dictionary to be passed as keyword arguments to future calls to the
        pipeline; required by MATE but here unused; set to {}.
    """

    ### Load data

    # Make multiple attempts in case loading fails
    attempts_left = 5
    file_size = -1
    while True:

        # Wait until the file is no longer being written to
        # Note: Some microscope software may intermittently stop writing, so
        #       this is not a perfect check for whether the file is complete;
        #       hence the multiple loading attempts...
        while True:
            sleep(2)
            new_file_size = os.stat(target_path).st_size
            if new_file_size > file_size:
                file_size = new_file_size
                attempts_left = 5
            else:
                break

        # If the file writing looks done, make a loading attempt
        try:
            if target_path.split(".")[-1] in ["tif", "tiff", "czi", "nd2"]:
                raw = AICSImage(target_path)
                raw = raw.data
                raw = np.squeeze(raw)

            # Handle unknown file endings
            else:
                errmsg = (
                    "File ending not recognized! Use MATE's `file_end` argument"
                    + " to control which file endings trigger image analysis."
                )
                raise ValueError(errmsg)

            # Some basic checks to ensure a loader didn't fail silently...
            if not isinstance(raw, np.ndarray):
                errmsg = (
                    "The loaded image object is not an instance of `np.array`,"
                    + " indicating that the loader may have failed silently!"
                )
                raise IOError(errmsg)
            if raw.size == 0:
                errmsg = (
                    "The loaded image array is of size 0, indicating that the"
                    + " loader may have failed silently!"
                )
                raise IOError(errmsg)

            # Exit the loop of loading attempts if loading was successful
            break

        # In case of failure, retry if there are still attempts left, otherwise
        # raise the Exception
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
        warn("Image converted down to 8bit using min-max scaling!")
        raw = (
            (raw.astype(float) - raw.min()) / (raw.max() - raw.min()) * 255
        ).astype(np.uint8)

    # Show loaded image
    if show:
        plt.figure()
        if raw.ndim == 3:
            plt.imshow(np.max(raw, axis=0), interpolation="none", cmap="gray")
            plt.title("Raw input image (z-max)")
        else:
            plt.imshow(raw, interpolation="none", cmap="gray")
            plt.title("Raw input image")
        plt.show(block=False)
        plt.pause(0.001)

    ### Mask by object-count thresholding

    # NOTE: This is an old approach that has empirically proven to work well
    # with cldnb:EGFP under standard conditions. However, there would be a lot
    # of room for improvement or for an altogether new approach, including one
    # that diverges further from the primordium tracking pipeline and is more
    # bespoke for the neuromasts.  # TODO!

    # Preprocessing: Gaussian smoothing
    raw = ndi.gaussian_filter(raw, sigma=gauss_sigma)

    # Preparations
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

        # Criterion 1: Is there a previous threshold with more objects?
        if np.max(counts_smooth[:threshold]) > counts_smooth[threshold]:

            # Criterion 2a: Has the number of objects sufficiently reduced?
            # Note: Although it works empirically, this criterion may not be as
            #       robust as we would ideally like it to be!
            if counts_smooth[threshold] <= (
                np.max(counts_smooth[:threshold]) * count_reduction
            ):
                break

            # Criterion 2b: Alternatively, it the current number of objects is
            # a local minimum (i.e. followed by an increase afterwards)
            # Note: An "early dip" despite smoothing could trigger this early!
            elif counts_smooth[threshold + 1] > counts_smooth[threshold]:
                break

    # Fallback: If the detected threshold has zero objects, take the highest
    # previous threshold that did. Important to avoid smoothing issues
    # Note: Although it works empirically, this approach may not be as robust
    #       as we would ideally like it to be!
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

    # Plot threshold series and resulting mask
    if show:

        # Threshold series
        plt.figure()
        plt.plot(counts_smooth)
        plt.plot(counts)
        plt.vlines(threshold, 0, counts.max(), color="g")
        plt.title("Threshold series")
        plt.show(block=False)
        plt.pause(0.001)

        # Resulting mask
        plt.figure()
        if mask.ndim == 3:
            plt.imshow(np.max(mask, axis=0), interpolation="none", cmap="gray")
            plt.title("Mask before clean-up (z-max)")
        else:
            plt.imshow(mask, interpolation="none", cmap="gray")
            plt.title("Mask before clean-up")
        plt.show(block=False)
        plt.pause(0.001)

    # Clean-up: retain only largest object
    img_bin_labeled = ndi.label(mask)[0]
    obj_nums, obj_sizes = np.unique(img_bin_labeled, return_counts=True)
    largest_obj = np.argmax(obj_sizes[1:]) + 1
    mask[img_bin_labeled != largest_obj] = 0

    # Show resulting mask
    if show:
        if mask.ndim == 3:
            plt.figure()
            plt.imshow(np.max(mask, axis=0), interpolation="none", cmap="gray")
            plt.title("Mask after clean-up (z-max)")
            plt.show(block=False)
            plt.pause(0.001)
            plt.figure()
            plt.imshow(np.max(mask, axis=1), interpolation="none", cmap="gray")
            plt.title("Mask after clean-up (y-max)")
            plt.show(block=False)
            plt.pause(0.001)
        else:
            plt.figure()
            plt.imshow(mask, interpolation="none", cmap="gray")
            plt.title("Mask after clean-up")
            plt.show(block=False)
            plt.pause(0.001)

    ### Find new z and y positions

    # Get centroid
    cen = ndi.center_of_mass(mask)

    # Get positions for 3D
    if raw.ndim == 3:

        # Use centroid positions as focusing targets
        z_pos = cen[0]
        y_pos = cen[1]
        x_pos = cen[2]

        # Z limit: An absolute limitation on how much MATE may move in z
        z_limit = 0.1  # Fraction of image size
        z_limit_top = (raw.shape[0] - 1) / 2.0 + z_limit * (raw.shape[0] - 1)
        z_limit_bot = (raw.shape[0] - 1) / 2.0 - z_limit * (raw.shape[0] - 1)
        if z_pos > z_limit_top:
            warn("z_pos > z_limit_top; using z_limit_top!")
            z_pos = z_limit_top
        if z_pos < z_limit_bot:
            warn("z_pos < z_limit_bot; using z_limit_bot!")
            z_pos = z_limit_bot

    # Get positions for 2D
    else:
        z_pos = None
        y_pos = cen[0]
        x_pos = cen[1]

    ### Return results

    if verbose:
        print(
            f"      Resulting coords (zyx): "
            + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
        )

    return z_pos, y_pos, x_pos, "OK", {}
