# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Image analysis pipeline for live tracking of the posterior lateral
            line primordium using MATE.
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
    """Compute new coordinates for the scope to track the zebrafish lateral
    line primordium's movement based on a 2D or 3D image. The primordium is
    masked using object-count thresolding. The new y (and z, if 3D) positions
    are computed as the respective centers of mass of the mask. The new x
    position is computed relative to the leading edge position of the mask.

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
            # FIXME: It is not clear if this criterion is robust enough!
            if counts_smooth[threshold] <= (
                np.max(counts_smooth[:threshold]) * count_reduction
            ):
                break

            # Criterion 2b: Alternatively, it the current number of objects a
            # local minimum (i.e. followed by an increase afterwards?)
            # FIXME: An "early dip" despite smoothing could trigger this early!
            elif counts_smooth[threshold + 1] > counts_smooth[threshold]:
                break

    # Fallback: If the detected threshold has zero objects, take the highest
    # previous threshold that did. Important to avoid smoothing issues
    # FIXME: It is not clear if this approach is robust enough!
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

    # Get z and y positions for 3D
    if raw.ndim == 3:

        # Use centroid of mask
        z_pos = cen[0]
        y_pos = cen[1]

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

    # Get "z" and y positions for 2D
    else:
        z_pos = None
        y_pos = cen[0]

    ### Find new x (leading edge) position

    # Collapse to x axis
    if raw.ndim == 3:
        collapsed = np.max(np.max(mask, axis=0), axis=0)
    else:
        collapsed = np.max(mask, axis=0)

    # Find frontal-most non-zero pixel
    front_pos = np.max(np.nonzero(collapsed)[0])

    ### Check if leading edge position is sensible

    # - If the new position is too far back (not in the leading half of the
    #   image), this triggers a small default movement (1/8th of the image)
    # - If the new position is touching the front boundary, this triggers a
    #   large default movement (1/5th of the image)

    # If the tip of the mask is behind the center of the image...
    if front_pos < collapsed.shape[0] / 2.0:

        # In this case, the mask is probably missing a lot at the tip
        warn(
            "The detected front_pos is too far back, likely due to a masking"
            + " error. Moving default distance."
        )

        # Handle it...
        default_step_fract = 1.0 / 8.0
        x_pos = (
            0.5 * collapsed.shape[0] + default_step_fract * collapsed.shape[0]
        )
        if verbose:
            print(
                f"      Resulting coords (zyx): "
                + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
            )

        return z_pos, y_pos, x_pos, "WARN:MASK-FAIL-DEFAULT-STEP", {}

    # If the tip of the mask touches the front end of the image
    elif front_pos == collapsed.shape[0] - 1:

        # In this case, the prim has probably moved out of the frame
        warn(
            "The prim has probably moved out of frame. "
            + "Moving catch-up distance."
        )

        # Handle it...
        default_catchup_fract = 1.0 / 5.0
        x_pos = (
            0.5 * collapsed.shape[0]
            + default_catchup_fract * collapsed.shape[0]
        )
        if verbose:
            print(
                f"      Resulting coords (zyx): "
                + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
            )

        return z_pos, y_pos, x_pos, "WARN:CATCH-UP-STEP", {}

    ### If the above issues did not trigger, compute new x-position for scope

    # - This is currently based on putting 1/5th of the image size between the
    #   current leading edge and the end of the image. This is an estimate that
    #   should work for standard image sizes and timecourses of about 5min/tp.
    # - Would be nice to make this more "adaptive", e.g. using a PID controller
    #   based on previous coordinates stored in img_cache.
    # - Would it be beneficial to use micron scale instead of pixel scale?

    blank_fract = 1.0 / 5.0
    x_pos = (
        front_pos + blank_fract * collapsed.shape[0] - 0.5 * collapsed.shape[0]
    )

    ### Return results

    if verbose:
        print(
            f"      Resulting coords (zyx): "
            + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
        )

    return z_pos, y_pos, x_pos, "OK", {}
