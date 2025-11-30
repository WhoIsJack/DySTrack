# -*- coding: utf-8 -*-
"""
Created on Thu Aug 15 00:13:31 2025

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Utilities for image loading in image analysis pipelines.
"""

import os
from time import sleep
from warnings import simplefilter, warn

simplefilter("always", UserWarning)

import numpy as np
from bioio import BioImage


def robustly_load_image_after_write(target_path, await_write=2):
    """Load an image from a specified target path using bioio, ensuring (as)
    (best as possible using simple means) that the image is no longer being
    actively written out by the microscope.

    Works by repeatedly checking the target file size and initiating the load
    only if the size has not increased for at least 2 seconds. Loading itself
    is attempted multiple times in case it fails for some reason.

    Currently supported file types:
        - `["tif", "tiff", "czi", "nd2"]`

    Parameters
    ----------
    target_path : path-like
        Path to the image file that is to be analyzed.
    await_write : int, optional, default 2
        Seconds to wait between each check of the target file size to determine
        if the file is still being written to. Reducing this will shave off
        latency but increases the risk of race conditions.

    Returns
    -------
    raw : numpy array
        Loaded image data.
    """

    # Make multiple attempts in case loading fails
    attempts_left = 5
    file_size = os.stat(target_path).st_size
    while True:

        # Wait until the file is no longer being written to
        # Note: Some microscope software may intermittently stop writing, so
        #       this is not a perfect check for whether the file is complete;
        #       hence the multiple loading attempts...
        while True:
            sleep(await_write)
            new_file_size = os.stat(target_path).st_size
            if new_file_size > file_size:
                file_size = new_file_size
                attempts_left = 5
            else:
                break

        # If the file writing looks done, make a loading attempt
        try:
            if target_path.split(".")[-1] in ["tif", "tiff", "czi", "nd2"]:
                raw = BioImage(target_path)
                raw = raw.data
                raw = np.squeeze(raw)

            # Handle unknown file endings
            else:
                errmsg = (
                    "File ending not recognized! Use DySTrack's `file_end` arg"
                    + " to control which file endings trigger image analysis."
                )
                raise ValueError(errmsg)

            # Basic checks to ensure the loader didn't fail silently...
            if not np.issubdtype(raw.dtype, np.number):
                errmsg = (
                    "The loaded image array is not of a numerical type,"
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

    # In case of success, return the loaded image
    return raw
