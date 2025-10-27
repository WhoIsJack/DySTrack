# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 00:13:31 2025

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Utilities for checking and constraining coordinates produced by
            image analysis pipelines.
"""

from warnings import simplefilter, warn

simplefilter("always", UserWarning)


def constrain_z_movement(z_pos, z_size, limit_fract=0.1):
    """Constrain the maximum offset in the z-direction to a given fraction of
    the total number of z-slices. Also emits a warning if the constraint needed
    to be applied.

    Parameters
    ----------
    z_pos : float
        The new z-position as detected by the image analysis pipeline. Must be
        in unit voxels (that is, unit z-slices).
    z_size : int
        Number of slices in the input image.
    limit_fract : float, optional, default 0.1
        Maximum fraction of `z_size` that `z_pos` is allowed to be offset
        relative to the center.

    Returns
    -------
    z_pos : float
        Updated z-position, constrained to the limit if necessary and unchanged
        otherwise.
    """

    # Compute top and bottom limit from fraction
    z_limit_top = (z_size - 1) / 2.0 + limit_fract * (z_size - 1)
    z_limit_bot = (z_size - 1) / 2.0 - limit_fract * (z_size - 1)

    # Check and if necessary apply the limit (and war)
    if z_pos > z_limit_top:
        warn("z_pos > z_limit_top; using z_limit_top!")
        z_pos = z_limit_top
    if z_pos < z_limit_bot:
        warn("z_pos < z_limit_bot; using z_limit_bot!")
        z_pos = z_limit_bot

    # Return result
    return z_pos
