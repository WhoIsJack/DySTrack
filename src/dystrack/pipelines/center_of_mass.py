# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Image analysis pipeline for generic center-of-mass tracking using
            either intensity values directly or simple masking.
"""

from warnings import simplefilter, warn

simplefilter("always", UserWarning)

import matplotlib.pyplot as plt
import numpy as np
import scipy.ndimage as ndi
from skimage.filters import threshold_otsu

from dystrack.pipelines.utilities.loading import (
    robustly_load_image_after_write,
)


def analyze_image(
    target_path,
    channel=None,
    method="intensity",
    gauss_sigma=3.0,
    count_reduction=0.5,
    warn_8bit=True,
    show=False,
    verbose=False,
):
    """Compute new coordinates for the scope to track/stabilize tissues based
    on the center of mass of either intensity values directly or masks derived
    using simple masking methods.

    The following masking methods are currently implemented:
        - "intensity": get center of mass directly from intensity values;
          best for tracking sparsely labeled tissues
        - "otsu": use Otsu's method to threshold, then retain only the largest
          object and get the center of mass of its mask; best for tracking
          compact objects / densely labeled tissues.
        - "objct": use object-count method to threshold, then retain only the
          largest object and get the center of mass of its mask; can succeed in
          some cases where Otsu is thrown off by structured background.

    Parameters
    ----------
    target_path : path-like
        Path to the image file that is to be analyzed.
    channel : int, optional, default None
        Index of channel to use for masking in case of multi-channel images.
        If not specified, a single-channel image is assumed.
    method : str, optional, default "intensity"
        Masking method. One of "intensity", "otsu", or "objct". See doc string
        header for details.
    gauss_sigma : float, optional, default 3.0
        Sigma for Gaussian filter prior to masking.
    count_reduction : float, optional, default 0.5
        Factor by which object count has to be reduced below its initial peak
        for a threshold value to be accepted. Only relevant if `method` is set
        to "objct".
    warn_8bit : bool, optional, default True
        Whether to emit a warning when a non-8bit image was found and was down-
        converted to 8bit using min-max rescaling.
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
        New coordinates for the next acquisition. For 2D inputs, z_pos is 0.0.
    img_msg : "_"
        A string output message; required by DySTrack but here unused and just
        set to "_".
    img_cache : {}
        A dictionary to be passed as keyword arguments to future calls to the
        pipeline; required by DySTrack but here unused and just set to {}.
    """

    ### Load data

    # Wait for image to be written and then load it
    raw = robustly_load_image_after_write(target_path)

    # Report
    if verbose:
        print("      Loaded image of shape:", raw.shape)

    # Check dimensionality
    if raw.ndim > 4:
        raise IOError("Image dimensionality >4; this cannot be right!")
    elif raw.ndim < 2:
        raise IOError("Image dimensionality <2; this cannot be right!")
    elif raw.ndim < 3 and channel is not None:
        raise IOError("CHANNEL given but image dimensionality is <3!")
    elif raw.shape[0] > 5 and channel is not None:
        warn(f"CHANNEL given but image dim 0 is of size {raw.shape[0]}!")

    # If there are multiple channels, select the one to use
    if channel is not None:
        raw = raw[channel, ...]

    # If the image is not 8bit, convert it
    # NOTE: This conversion scales min to 0 and max to 255!
    if raw.dtype != np.uint8:
        if warn_8bit:
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

    # Preprocessing: Gaussian smoothing
    raw = ndi.gaussian_filter(raw, sigma=gauss_sigma)

    ### Method "intensity": do not mask

    if method == "intensity":

        mask = raw

    ### Method "otsu": use Otsu's method for masking

    elif method == "otsu":

        # Run Otsu thresholding
        threshold = threshold_otsu(raw)
        if verbose:
            print("      Detected treshold:", threshold)
        mask = raw >= threshold

        # Plot resulting mask
        if show:

            plt.figure()
            if mask.ndim == 3:
                plt.imshow(
                    np.max(mask, axis=0), interpolation="none", cmap="gray"
                )
                plt.title(
                    f"Mask before clean-up (z-max); threshold: {threshold}"
                )
            else:
                plt.imshow(mask, interpolation="none", cmap="gray")
                plt.title(f"Mask before clean-up; threshold: {threshold}")
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
                plt.imshow(
                    np.max(mask, axis=0), interpolation="none", cmap="gray"
                )
                plt.title("Mask after clean-up (z-max)")
                plt.show(block=False)
                plt.pause(0.001)
                plt.figure()
                plt.imshow(
                    np.max(mask, axis=1), interpolation="none", cmap="gray"
                )
                plt.title("Mask after clean-up (y-max)")
                plt.show(block=False)
                plt.pause(0.001)
            else:
                plt.figure()
                plt.imshow(mask, interpolation="none", cmap="gray")
                plt.title("Mask after clean-up")
                plt.show(block=False)
                plt.pause(0.001)

    ### Method "objct": use object-count thresholding for masking

    # NOTE: This is an old approach that has empirically proven to work well
    # with bright membrane-labeled tissues like cldnB:EGFP in the lateral line.

    elif method == "objct":

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
                # Note: Although it works empirically, this criterion may not
                #       be as robust as we would ideally like it to be!
                if counts_smooth[threshold] <= (
                    np.max(counts_smooth[:threshold]) * count_reduction
                ):
                    break

                # Criterion 2b: Alternatively, it the current number of objects
                # is a local minimum (i.e. followed by an increase afterwards)
                # Note: An "early dip" despite smoothing could trigger this
                #       early!
                elif counts_smooth[threshold + 1] > counts_smooth[threshold]:
                    break

        # Fallback: If the detected threshold has zero objects, take highest
        # previous threshold that did. Important to avoid smoothing issues
        # Note: Although it works empirically, this approach may not be as
        #       robust as we would ideally like it to be!
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
                plt.imshow(
                    np.max(mask, axis=0), interpolation="none", cmap="gray"
                )
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
                plt.imshow(
                    np.max(mask, axis=0), interpolation="none", cmap="gray"
                )
                plt.title("Mask after clean-up (z-max)")
                plt.show(block=False)
                plt.pause(0.001)
                plt.figure()
                plt.imshow(
                    np.max(mask, axis=1), interpolation="none", cmap="gray"
                )
                plt.title("Mask after clean-up (y-max)")
                plt.show(block=False)
                plt.pause(0.001)
            else:
                plt.figure()
                plt.imshow(mask, interpolation="none", cmap="gray")
                plt.title("Mask after clean-up")
                plt.show(block=False)
                plt.pause(0.001)

    ### Invalid method

    else:
        raise NotImplementedError(
            f"{method} is not a valid method for center_of_mass."
        )

    ### Find new z and y positions

    # Get centroid
    cen = ndi.center_of_mass(mask)

    # Get positions for 3D
    if raw.ndim == 3:

        # Use centroid positions as focusing targets
        z_pos = cen[0]
        y_pos = cen[1]
        x_pos = cen[2]

        # Z limit: An absolute limitation on how much DySTrack may move in z
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
        z_pos = 0.0
        y_pos = cen[0]
        x_pos = cen[1]

    ### Return results

    if verbose:
        print(
            f"      Resulting coords (zyx): "
            + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
        )

    return z_pos, y_pos, x_pos, "OK", {}
