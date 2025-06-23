# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Manages the main event loop of MATE. This loop monitors the target
            directory for images produced by the scope that fit user-specified
            criteria, then triggers a specified image analysis pipeline that
            determines new coordinates to be sent to the microscope through a
            specified channel.
"""


import os
import re
from msvcrt import getch, kbhit
from time import sleep

import mate.manager.transmitters as trs


def _check_fname(fname, file_start="", file_end="", file_regex=""):
    """Check if a given file name matches all conditions.

    Parameters
    ----------
    fname : string
        The file name to check
    file_start : string, optional, default ""
        The file must start with this string. Ignored if empty string.
    file_end : string, optional, default ""
        The file must end with this string. Ignored if empty string.
    file_regex : string, optional, default ""
        The file must fully match this regez pattern. Ignored if empty string.

    Returns
    -------
    _ : bool
        True if file matches all conditions (including if no conditions are
        specified at all), False otherwise.
    """

    if file_start and not fname.startswith(file_start):
        return False

    if file_end and not fname.endswith(file_end):
        return False

    if file_regex and not re.fullmatch(file_regex, fname):
        return False

    return True


def _trigger_image_analysis(
    target_path,
    image_analysis_func,
    verbose=False,
    img_kwargs={},
    img_cache={},
):
    """Calls image analysis pipeline with a given target file path, ensuring
    that any errors are caught and appropriately forwarded.

    Parameters
    ----------
    target_path : path-like
        Path to the target file used in the image analysis function.
    image_analysis_func : callable
        Image analysis pipeline function. See doc string of `run_mate_manager`
        for more information.
    verbose : bool, optional, default False
        Forwarded to image analysis function to control verbosity.
    img_kwargs : dict, optional, default {}
        Additional keyword arguments forwarded to the image analysis function
        using `**img_kwargs`.
    img_cache : dict, optional, default {}
        Additional keyword arguments forwarded to the image analysis function
        using `**img_kwargs`. Unlike `img_kwargs`, this dictionary is also one
        of the outputs of the image analysis function and can thus be modified
        for the next iteration.

    Returns
    -------
    out : tuple
        Output of the image analysis function:
        `(z_pos, y_pos, x_pos, img_msg, img_cache)`
        If the image analysis function raises an exception, the coordinates are
        each set to None, the img_msg is set to "Image analysis failed!", and
        the img_cache is returned unaltered.
    img_error : None or Exception
        None if the image analysis function did not raise an Exception,
        otherwise contains the Exception object itself.
    """

    # Try running the image analysis
    try:
        z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
            target_path, verbose=verbose, **img_kwargs, **img_cache
        )
        img_error = None

    # Handle any errors
    except Exception as e:
        z_pos, y_pos, x_pos = None, None, None
        img_msg = "Image analysis failed!"
        img_cache = img_cache
        img_error = e

    return (z_pos, y_pos, x_pos, img_msg, img_cache), img_error


def _trigger_coords_transmission(
    tra_method,
    z_pos,
    y_pos,
    x_pos,
    img_msg,
    img_cache={},
    img_error={},
    target_dir=None,
    tra_kwargs={},
):
    """Transmits coordinates to the microscope using one of several predefined
    transmission methods or a user-provided callable.

    Parameters
    ----------
    tra_method : str or callable, optional, default "txt"
        String indicating the method to use for transmitting coordinates to the
        microscope, or alternatively a custom callable. See doc string of
        `run_mate_manager` and the `transmitters` module for more information.
    z_pos, y_pos, x_pos : numeric (or None, or other)
        Coordinate values forwarded to the transmission method.
    img_msg : str or None
        String forwarded to transmission methods that support messaging.
    img_cache : dict, optional, default {}
        Image analysis cache dictionary (see doc string of `run_mate_manager`
        for more info). Forwarded to custom `tra_method` callables.
    img_error : None or Exception
        Error captured during image analysis. Forwarded to custom `tra_method`
        callables.
    target_dir : path-like or None, optional, default None
        Directory path that is being monitored by MATE. Specifies location of
        text file if `tra_method="txt"`, in which case it is required. Also
        forwarded to custom `tra_method` callables.
    tra_kwargs : dict, optional, default {}
        Additional keyword arguments forwrded to transmission methods.

    Returns
    -------
    tra_error : None or Exception
        None if the coordinate transmission method did not raise an Exception,
        otherwise contains the Exception object itself.
    """

    # Send coordinate via a custom method
    if callable(tra_method):
        try:

            tra_method(
                z_pos,
                y_pos,
                x_pos,
                img_msg,
                img_cache,
                img_error,
                target_dir,
                **tra_kwargs,
            )
            tra_error = None

        except Exception as e:
            tra_error = e

    # Send coordinates via a text file
    elif tra_method == "txt":
        try:

            coords_path = os.path.join(target_dir, "mate_coords.txt")
            trs.send_coords_txt(
                coords_path, z_pos, y_pos, x_pos, msg=img_msg, **tra_kwargs
            )
            tra_error = None

        except Exception as e:
            tra_error = e

    # Send coordinates via Windows registry in MyPiC style
    elif tra_method == "MyPiC":
        try:

            trs.send_coords_winreg(
                z_pos,
                y_pos,
                x_pos,
                codeM="focus",
                errMsg=None if img_error is None else img_msg,
                **tra_kwargs,
            )
            tra_error = None

        except Exception as e:
            tra_error = e

    # Handle case where `transmission_method` is unsupported
    else:
        raise ValueError(
            "Could not transmit coordinates; invalid `transmission_method`; "
            + "must be 'txt', 'MyPiC', or a custom callable."
        )

    return tra_error


def run_mate_manager(
    target_dir,
    image_analysis_func,
    max_checks=None,
    max_triggers=None,
    end_on_esc=True,
    delay=1.0,
    recurse=False,
    file_start="",
    file_end="",
    file_regex="",
    img_kwargs={},
    img_cache={},
    img_err_fallback=True,
    tra_method="txt",
    tra_kwargs={},
    tra_err_resume=False,
    write_txt=True,
    verbose=True,
):
    """Manages an event loop that monitors a target directory for new files.
    For each new file found that matches user-defined criteria, the speficied
    image analysis pipeline is triggered and the results are transmitted to the
    microscope.

    The loop keeps going until `max_checks` checks for added files have been
    done or until `max_triggers` image analysis events have been triggered,
    whichever is lower. Alternatively, the loop will end if the Esc key is hit,
    provided `end_on_esc` is True.

    Parameters
    ----------
    target_dir : path-like
        Path to the directory that is to be monitored.
    image_analysis_func : callable
        Function that performs image analysis on detected files and returns new
        coordinates for transmission to the microscope. Call signature:
        ```
        z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
            target_path, verbose=False, **img_kwargs, **img_cache)
        ```
    max_checks : int or None, optional, default None
        Maximum number of checks for new files performed before exiting.
    max_triggers : int or None, optional, default None
        Maximum number of image analysis pipeline calls before exiting.
    max_targets : int or None, optional, default None
        Maximum number of target files sent to analysis before exiting.
    end_on_esc : bool, optional, default True
        If True, hitting the `Esc` key will terminate the loop.
    delay : float, optional, default 1.0
        Time (in seconds) to wait before the next check if no new files have
        been found in the target directory.
    recurse : bool, optional, default False
        If True, subdirectories of `target_dir` are monitored recursively.
    file_start : string, optional, default ""
        Only files that start with this string will trigger the pipeline.
    file_end : string, optional, default ""
        Only files that end with this string will trigger the pipeline.
    file_regex : string, optional, default ""
        A regex pattern. Only file names that fully match this pattern will
        trigger the pipeline.
    img_kwargs : dict, optional, default {}
        Additional parameters passed to the image analysis function.
    img_cache : dict, optional, default {}
        Additional parameters passed to the image analysis function. This will
        be overwritten by the 4th output of the function (after the coordinate
        values) and passed again during the next loop. Use this to pass values
        forward across analysis loops, e.g. for use as priors.
    img_err_fallback : bool, optional, default True
        Whether or not to fall back to the previous coordinates if an image
        analysis call fails.
    tra_method : str or callable, optional, default "txt"
        String indicating the method to use for transmitting coordinates to the
        microscope, or alternatively a custom callable. String options:
            - "txt" : Write to text a file in `target_dir` ("mate_coords.txt")
            - "MyPiC" : Write to the Windows registry for ZEN Black MyPiC macro
        Call signature for custom transmission function:
        ```
        tra_method(
            z_pos, y_pos, x_pos,
            img_msg, img_cache, img_error,
            target_dir, **tra_kwargs)
        ```
    tra_kwargs : dict, optional, default {}
        Additional parameters passed to the coordiante transmission function.
    tra_err_resume : bool, optional, default False
        Whether to resume monitoring after transmission of detected coordinates
        to the microscope has terminally failed.
    write_txt : bool, optional, default True
        If True, coordinates are recorded in a text file ("mate_coords.txt") in
        `target_dir` *regardless* of the specified `tra_method`. If said method
        is "txt", this has no effect as the text file is generated anyway.
    verbose : bool, optional, default True
        Flag forwarded to the image analysis pipeline to set whether it should
        print information.

    Returns
    -------
    coordinates : list of [float, float, float]
        List of all coordinates that have been detected during image analysis
        (or as a fallback). Coordinates are given as `[z_pos, y_pos, x_pos]`.
    stats_dict : dict
        A dictionary containing the following stats about the run:
            - No. of checks made (check_counter)
            - No. of new files found (found_counter)
            - No. of target files found (target_counter)
            - No. of successful image analysis calls (img_success_counter)
            - No. of successful coordiate transmissions (tra_success_counter)
    """

    ### Preparation

    # Check that at least one of the termination conditions is set
    if all([max_checks is None, max_triggers is None, not end_on_esc]):
        raise ValueError(
            "No ending condition for MATE event loop set, so it would run "
            + "indefinitely. At least one of `max_checks` or `max_triggers` "
            + "must not be `None`, or `end_on_esc` must be True."
        )

    # Report
    print("\n\nMATE MANAGER SESSION STARTED!")
    print("Monitoring target dir(s) for new files...")
    if max_checks is not None:
        print(f"Will terminate after {max_checks} checks.")
    if max_triggers is not None:
        print(f"Will terminate after {max_triggers} pipeline trigger events.")
    if end_on_esc:
        print("Press <Esc> to terminate.\n")

    # Generate txt file to record coordinates (if necessary)
    if (tra_method == "txt") or write_txt:
        txt_path = os.path.join(target_dir, "mate_coords.txt")
        if not os.path.isfile(txt_path):
            with open(txt_path, "w") as coordsfile:
                coordsfile.write("Z\tY\tX\tmsg\n")

    # Find existing files in the target dir (and its subdirs)
    if recurse:
        paths = [
            os.path.join(dir_info[0], fname)
            for dir_info in os.walk(target_dir)
            for fname in dir_info[2]
        ]
    else:
        paths = [
            os.path.join(target_dir, fname)
            for fname in os.listdir(target_dir)
            if os.path.isfile(os.path.join(target_dir, fname))
        ]

    # Initialize coordinate list
    coordinates = []

    # Initialize stats
    check_counter = 0
    found_counter = 0
    target_counter = 0
    img_success_counter = 0
    tra_success_counter = 0

    ### Run monitoring loop

    while True:

        # Check if counters have reached their limits to exit loop
        if max_checks is not None:
            if check_counter == max_checks:
                break
        if max_triggers is not None:
            if target_counter >= max_triggers:
                break

        # Listen for ESC keypress to exit loop
        if end_on_esc:
            esc_pressed = False
            while kbhit():
                if ord(getch()) == 27:
                    esc_pressed = True
                    break
            if esc_pressed:
                break

        # Find files in the target dir (and its subdirs)
        if recurse:
            new_paths = [
                os.path.join(dir_info[0], fname)
                for dir_info in os.walk(target_dir)
                for fname in dir_info[2]
            ]
        else:
            new_paths = [
                os.path.join(target_dir, fname)
                for fname in os.listdir(target_dir)
                if os.path.isfile(os.path.join(target_dir, fname))
            ]
        check_counter += 1

        # If something has changed...
        if new_paths != paths:

            # Get all new paths
            target_paths = [p for p in new_paths if p not in paths]
            found_counter += len(target_paths)

            # For each new file...
            for target_path in target_paths:
                target_file = os.path.split(target_path)[-1]

                # Check if the file matches the conditions
                if _check_fname(target_file, file_start, file_end, file_regex):

                    # Stats & report
                    target_counter += 1
                    print("\nTarget file detected:", target_file)

                    # Run image analysis pipeline
                    print("Running image analysis...")
                    img_out, img_err = _trigger_image_analysis(
                        target_path,
                        image_analysis_func,
                        verbose,
                        img_kwargs,
                        img_cache,
                    )
                    z_pos, y_pos, x_pos = img_out[:3]
                    img_msg, img_cache = img_out[3:]

                    # Handle success case
                    if img_err is None:
                        img_success_counter += 1
                        coordinates.append([z_pos, y_pos, x_pos])
                        print("Image analysis complete.")

                    # Handle failure case
                    else:

                        # Hard-fail if fallback to previous is disabled
                        if not img_err_fallback:
                            print(
                                "[!!] Image analysis failed and `fallback="
                                + "False`; raising image analysis error."
                            )
                            raise img_err

                        # Hard-fail if this was the very first acquisition
                        if not coordinates:
                            print(
                                "[!!] Image analysis failed on first try; "
                                + "raising image analysis error."
                            )
                            raise img_err

                        # Fall back to previous position
                        print(
                            "[!!] Image analysis failed; reusing previous"
                            + "position! Skipped error was:"
                        )
                        print("[!!] >>", repr(img_err))
                        z_pos, y_pos, x_pos = coordinates[-1]
                        coordinates.append([z_pos, y_pos, x_pos])

                    # Transmit coordinates to the microscope (with retries)
                    print("Pushing coords to scope...")
                    retry_attempts = 3
                    attempt = 0
                    while attempt <= retry_attempts:
                        attempt += 1
                        tra_err = _trigger_coords_transmission(
                            tra_method,
                            z_pos,
                            y_pos,
                            x_pos,
                            img_msg,
                            img_cache,
                            img_err,
                            target_dir,
                            tra_kwargs,
                        )
                        if tra_err is None:
                            break
                        elif attempt < retry_attempts:
                            print("[!!] Failed to push coords; retrying...")

                    # Handle success case
                    if tra_err is None:
                        tra_success_counter += 1
                        print("Coords pushed.")

                    # Handle failure case
                    else:

                        # Hard-fail if resuming is disabled
                        if not tra_err_resume:
                            print(
                                "[!!] Terminally failed to push coords and "
                                + "`tra_err_resume=False`; raising error."
                            )
                            raise tra_err

                        # Otherwise resume monitoring
                        else:
                            print(
                                "[!!] Terminally failed to push coords but "
                                + "`tra_err_resume=True`; proceeding. "
                                + "Skipped error was:"
                            )
                            print("[!!] >>", repr(tra_err))

                    # Record coordinates in file if necessary
                    if tra_err is None:
                        if write_txt and (tra_method != "txt"):
                            txt_err = _trigger_coords_transmission(
                                "txt",
                                z_pos,
                                y_pos,
                                x_pos,
                                img_msg,
                                target_dir=target_dir,
                            )
                            if txt_err is not None:
                                print(
                                    "[!!] Failed to record coords in txt file;"
                                    + " skipping. This should not affect"
                                    + " anything else. The error was:"
                                )
                                print("[!!] >>", repr(txt_err))

            # Update the paths list
            paths = new_paths

            # Continue monitoring
            print("Resuming monitoring...")
            continue

        # If nothing has changed, wait for the interval to pass,
        # then continue monitoring
        sleep(delay)

    ### Report and return

    # Report
    print("\n\nMATE MONITORING SESSION TERMINATED!")
    print("\nStats:")
    print("  Total checks made:       ", check_counter)
    print("  Total new files found:   ", found_counter)
    print("  Total target files found:", target_counter)
    print("    No. successfully analyzed:", img_success_counter)
    print("    No. coords sent to scope: ", tra_success_counter)

    # Compile information
    stats_dict = {
        "check_counter": check_counter,
        "found_counter": found_counter,
        "target_counter": target_counter,
        "img_success_counter": img_success_counter,
        "tra_success_counter": tra_success_counter,
    }

    # Return
    return coordinates, stats_dict
