# -*- coding: utf-8 -*-
"""
Created on Sun Oct 27 22:38:59 2024

@authors:   Jonas Hartmann @ Mayor lab (UCL)

@descript:  DySTrack image analysis pipeline for tracking of the chick node.
"""

from warnings import simplefilter, warn

simplefilter("always", UserWarning)

import os

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import curve_fit

from dystrack.pipelines.utilities.loading import (
    robustly_load_image_after_write,
)


def analyze_image(target_path, channel=None, show=False, verbose=False):
    """Compute new coordinates for the scope to track the developing chick node
    during axis elongation based on a 2D or 3D image. Stable node coordinates
    are inferred by fitting Gaussians to the intensity profiles in z and y, and
    by fitting a sigmoid function to the intensity profile in x.

    Parameters
    ----------
    target_path : path-like
        Path to the image file that is to be analyzed.
    channel : int, optional, default None
        Index of channel to use for masking in case of multi-channel images.
        If not specified, a single-channel image is assumed.
    show : bool, optional, default False
        Whether to show various intermediate results. Default is False.
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
        # warn("Image converted down to 8bit using min-max scaling!")
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

    ### Approach 6: Fit simple models to intensity profiles in each dimension

    # Define Gaussian model
    def f_gaussian(x, *p):
        A, mu, sg = p
        return (
            A
            / (sg * np.sqrt(2.0 * np.pi))
            * np.exp(-1 / 2 * ((x - mu) / sg) ** 2.0)
        )

    # Define sigmoid model
    # Note: (x0 - x) means it starts high and then decreases, so this assumes
    #       that anterior is on the left; (x - x0) would be the opposite.
    def f_sigmoid(x, *p):
        L, k, x0 = p
        return L / (1.0 + np.exp(-k * (x0 - x)))

    ## Fit Z-axis profile with Gaussian model

    # Proceed if the data is 3D
    if raw.ndim == 3:

        # Prep results plot
        if show:
            fig, ax = plt.subplots(1, 3, figsize=(10, 2.5))
            axi = 0

        # Get normalized z-axis mean profile
        z_prof = np.mean(raw, axis=(1, 2))
        z_prof = (z_prof - z_prof.min()) / (z_prof.max() - z_prof.min())

        # Fit Gaussian function to intensity profile
        z_locs = np.arange(z_prof.size)
        p0 = [z_prof.sum(), z_locs[-1] / 2, z_locs[-1] / 8]  # Initial guess
        p_fit = curve_fit(f_gaussian, z_locs, z_prof, p0=p0)[0]

        # Get z_pos as mu of Gaussian
        z_pos = p_fit[1]

        # Plot the result
        if show:
            ax[axi].plot(z_locs, z_prof, lw=1, alpha=0.8, label="data")
            ax[axi].plot(
                z_locs,
                f_gaussian(z_locs, *p0),
                ":",
                c="k",
                alpha=0.8,
                label="p0",
            )
            ax[axi].plot(
                z_locs,
                f_gaussian(z_locs, *p_fit),
                alpha=0.8,
                label="p_fit",
            )
            ax[axi].legend(fontsize=8, frameon=False)
            ax[axi].set_xlabel("z position [pxl]")
            ax[axi].set_ylabel("mean intensity [au]")
            axi = 1

    # Skip z-axis fit for 2D data
    else:
        z_pos = 0.0

        # Prep plot for 2D case (only 2 subplots)
        if show:
            fig, ax = plt.subplots(1, 2, figsize=(6.66, 2.5))
            axi = 0

    ## Fit Y-axis profile with Gaussian model

    # Get normalized y-axis mean profile
    if raw.ndim == 2:
        y_prof = np.mean(raw, axis=1)
    else:
        y_prof = np.mean(raw, axis=(0, 2))
    y_prof = (y_prof - y_prof.min()) / (y_prof.max() - y_prof.min())

    # Fit function to profile
    y_locs = np.arange(y_prof.size)
    p0 = [y_prof.sum(), y_locs[-1] / 2, y_locs[-1] / 6]  # Initial guess
    p_fit = curve_fit(f_gaussian, y_locs, y_prof, p0=p0)[0]

    # Get y_pos as mu of Gaussian
    y_pos = p_fit[1]

    # Show the results
    if show:
        ax[axi].plot(y_locs, y_prof, lw=1, alpha=0.8, label="data")
        ax[axi].plot(
            y_locs,
            f_gaussian(y_locs, *p0),
            ":",
            c="k",
            alpha=0.8,
            label="p0",
        )
        ax[axi].plot(
            y_locs, f_gaussian(y_locs, *p_fit), alpha=0.8, label="p_fit"
        )
        ax[axi].legend(fontsize=8, frameon=False)
        ax[axi].set_xlabel("y position [pxl]")
        ax[axi].set_ylabel("mean intensity [au]")
        axi += 1

    ## Fit X-axis profile with sigmoid model (kind of an edge tracker really)

    # Get normalized x-axis profile around y position
    if raw.ndim == 2:
        x_prof = np.mean(
            raw[int(y_pos - p_fit[2]) : int(y_pos + p_fit[2]), :], axis=0
        )
    else:
        x_prof = np.mean(
            raw[:, int(y_pos - p_fit[2]) : int(y_pos + p_fit[2]), :],
            axis=(0, 1),
        )
    x_prof = (x_prof - x_prof.min()) / (x_prof.max() - x_prof.min())

    # Fit function to profile
    x_locs = np.arange(x_prof.size)
    p0 = [x_prof.mean(), 10.0 / x_locs[-1], x_locs[-1] / 3 * 2]  # Init. guess
    bounds = (
        [x_prof.min(), 1 / x_locs[-1], x_locs[-1] / 6.0],
        [1.2 * x_prof.max(), 100 / x_locs[-1], x_locs[-1] / 1.2],
    )
    p_fit = curve_fit(f_sigmoid, x_locs, x_prof, p0=p0, bounds=bounds)[0]

    # Get x_pos as x0 of sigmoid function
    x_pos = p_fit[2]

    # Show the results
    if show:
        ax[axi].plot(x_locs, x_prof, lw=1, alpha=0.8, label="data")
        ax[axi].plot(
            x_locs,
            f_sigmoid(x_locs, *p0),
            ":",
            c="k",
            alpha=0.8,
            label="p0",
        )
        ax[axi].plot(
            x_locs, f_sigmoid(x_locs, *p_fit), alpha=0.8, label="p_fit"
        )
        ax[axi].legend(fontsize=7, frameon=False)
        ax[axi].set_xlabel("x position [pxl]")
        ax[axi].set_ylabel("mean intensity [au]")

    # Finalize the open figure
    if show:
        plt.tight_layout()
        plt.show(block=False)
        plt.pause(0.001)

    # Show resulting positions in images / maximum projections
    if (raw.ndim == 3) and show:  # 3D
        plt.figure()
        plt.imshow(np.max(raw, axis=0), interpolation="none", cmap="gray")
        plt.scatter(x_pos, y_pos, c="r", s=5, alpha=1.0)
        plt.show(block=False)
        plt.pause(0.001)
        plt.figure()
        plt.imshow(np.max(raw, axis=1), interpolation="none", cmap="gray")
        plt.scatter(x_pos, z_pos, c="r", s=5, alpha=1.0)
        plt.show(block=False)
        plt.pause(0.001)
    elif show:  # 2D
        plt.figure()
        plt.imshow(raw, interpolation="none", cmap="gray")
        plt.scatter(x_pos, y_pos, c="r", s=5, alpha=1.0)
        plt.show(block=False)
        plt.pause(0.001)

    ### Postprocessing

    # Z limit: An absolute limitation on how much it can move!
    if raw.ndim == 3:

        # Z limit: An absolute limitation on how much DySTrack may move in z
        # z_limit = 0.1  # Fraction of image size
        z_limit = 0.2  # Fraction of image size
        z_limit_top = (raw.shape[0] - 1) / 2.0 + z_limit * (raw.shape[0] - 1)
        z_limit_bot = (raw.shape[0] - 1) / 2.0 - z_limit * (raw.shape[0] - 1)
        if z_pos > z_limit_top:
            warn("z_pos > z_limit_top; using z_limit_top!")
            z_pos = z_limit_top
        if z_pos < z_limit_bot:
            warn("z_pos < z_limit_bot; using z_limit_bot!")
            z_pos = z_limit_bot

        # Invert resulting z_position for scope frame of reference
        # FIXME: This should be removed and integrated into the JOBS scripts to
        #        make the pipelines themselves all consistent!
        z_pos = (raw.shape[0] - 1) - z_pos

    ### Return results

    if verbose:
        print(
            f"      Resulting coords (zyx): "
            + f"{z_pos:.4f}, {y_pos:.4f}, {x_pos:.4f}"
        )

    return z_pos, y_pos, x_pos, "OK", {}
