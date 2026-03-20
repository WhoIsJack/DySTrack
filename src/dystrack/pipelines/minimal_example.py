# -*- coding: utf-8 -*-
"""
Created on Fri Mar 20 11:33:14 2026

@authors:   Jonas Hartmann @ Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  A minimal example of a DySTrack image analysis pipeline that simply
            tracks the center of mass of intensity in the image. Intended as a
            didactic example; for actual center-of-mass tracking, we recommend
            using `dystrack.pipelines.center_of_mass`.
"""

from warnings import simplefilter, warn

simplefilter("always", UserWarning)

import numpy as np
import scipy.ndimage as ndi

from dystrack.pipelines.utilities.constraints import constrain_z_movement
from dystrack.pipelines.utilities.loading import (
    robustly_load_image_after_write,
)


def analyze_image(
    target_path,
    channel=None,
    await_write=2,
    warn_8bit=True,
    verbose=False,
):
    """A minimal example of a DySTrack image analysis pipeline function. Simply
    tracks the center of mass of intensity in the input image. This is intended
    as a didactic example or as a starting point for customization; for actual
    center-of-mass tracking, use `dystrack.pipelines.center_of_mass`, which
    provides more options.

    Parameters
    ----------
    target_path : path-like
        Path to the image file that is to be analyzed.
    channel : int, optional, default None
        Index of channel to use for masking in case of multi-channel images.
        If not specified, a single-channel image is assumed.
    await_write : int, optional, default 2
        Seconds to wait between each check of the target file size to determine
        if the file is still being written to. Reducing this will shave off
        latency but increases the risk of race conditions.
    warn_8bit : bool, optional, default True
        Whether to emit a warning when a non-8bit image was found and was down-
        converted to 8bit using min-max rescaling.
    verbose : bool, optional, default False
        If True, more information is printed.

    Returns
    -------
    z_pos, y_pos, x_pos : floats
        New coordinates for the next acquisition. For 2D inputs, z_pos is 0.0.
    img_msg : "_"
        A string output message; required by DySTrack but here unused and just
        set to "_".
    img_cache : {}
        A dictionary to be passed as keyword arguments to future calls to the
        pipeline; required by DySTrack but here unused and just set to {}.
    """

    ### Load data

    # This section loads the image data written by the scope using a robust
    # loading function that ensures the file isn't accidentally opened while
    # the microscope is still writing to it.
    # After loading the image, a few checks are performe to ensure that the
    # input shape makes sense. You may wish to customize these checks based on
    # your expectations on the input data for your particular pipeline.
    # This example also includes the option to subselect a channel if the input
    # image has multiple channels, and finally it converts the input image to
    # 8bit format (if it isn't already), which usually is a good idea to speed
    # up image analysis operations and reduce memory consumption.

    # Wait for image to be written and then load it
    raw = robustly_load_image_after_write(target_path, await_write=await_write)

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

    ### Find new coordinates from image data

    # This is the main part of the image analysis pipeline. It should include
    # the necessary operations to take the `raw` image data and identify new
    # coordinates for the next acquisition.
    # In this simplistic example, the new coordinates are just calculated as
    # the center of mass of the image's intensity values. A proper pipeline
    # might involve e.g. some smoothing to reduce noise, thresholding to mask
    # foreground pixels, some clean-up of the resulting mask to identify the
    # target object, and a way of identifying the correct coordinates based on
    # the mask of the target object. For more information and examples of more
    # elaborate pipelines, please see the documentation and the other pipelines
    # included in DySTrack.

    # Find center of mass
    cen = ndi.center_of_mass(raw)

    ### Handling different dimensionalities

    # This example is intended to work for 2D and 3D inputs. To ensure this,
    # the output of `ndi.center_of_mass` needs to be unpacked properly:

    # For the 2D case
    if raw.ndim == 2:

        x_pos = cen[1]
        y_pos = cen[0]
        z_pos = 0.0  # Note that z_pos should be set to 0.0 in the 2D case

    # For the 3D case
    else:

        x_pos = cen[2]
        y_pos = cen[1]
        z_pos = cen[0]

        # Note that, for the 3D case, we usually limit how much DySTrack may
        # move in z, as a big error in z-movements could lead to the objective
        # touching the stage
        z_limit = 0.1  # Fraction of image size
        z_pos = constrain_z_movement(z_pos, raw.shape[0], z_limit)

    ### Return results

    if verbose:
        print(
            f"      Resulting coords (zyx): "
            + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
        )

    return z_pos, y_pos, x_pos, "OK", {}
