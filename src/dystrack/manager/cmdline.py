# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Provides a command line interface to run MATE. This is intended for
            import in MATE config files (see `run` dir) to handle command line
            inputs and launch the MATE manager event loop.
"""


import argparse
import re

import dystrack.manager.manager as mate_manager


def _get_func_args(func):
    """Get a tuple of all arguments in the function definition of `func`."""
    func_n_args = func.__code__.co_argcount
    func_vars = func.__code__.co_varnames
    return func_vars[:func_n_args]


def _get_docstr_args_numpy(func):
    """Get the argument types and argument descriptions from a numpy-style doc
    string of function `func`. Requires the docstring to contain Parameters and
    Returns sections and to document *all* its parameters.

    For example, the following doc string:

    ```
    Parameters
    ----------
    param1 : type_of_param1
        Description of param1.
    param2 : type_of_param2 or None
        Description of param2

    Results
    -------
    foo : bar
       foobar
    ```

    would return this `argtypes` dict:

    `{"param1" : "type_of_param1", "param2" : "type_of_param2 or none"}`

    and thos `argdescr` dict:

    `{"param1" : "Description of param1", "param2" : "Description of param2"}

    WARNING: This is a fun but very basic and probably quite fragile homebrew
             approach; look into `numpydoc` or something like that?! Also, for
             the types it would be better to use type annotations.  # TODO!
    """

    # Get arguments and doc string
    args = _get_func_args(func)
    docstr = func.__doc__

    # Fail if there is no (proper) doc string
    if docstr is None:
        raise ValueError("Provided `func` has no doc string.")
    if "Parameters" not in docstr or "Returns" not in docstr:
        raise ValueError(
            "Provided `func` does not seem to have a numpy-style doc string "
            + "with both a Parameters section and a Returns section."
        )

    # Filter out Parameters section
    argstr = re.split(
        r"^\s+Parameters$\n^\s+----------$", docstr, flags=re.MULTILINE
    )[1]
    argstr = re.split(
        r"^\s+Returns$\n^\s+-------$", argstr, flags=re.MULTILINE
    )[0]

    # Identify type annotations and text descriptions for each argument
    argtypes, argdescr = {}, {}
    for arg, arg_next in zip(args[:-1], args[1:]):
        argtypes[arg], argdescr[arg] = re.search(
            rf"^\s+({arg} : )(.+)$\s^\s+([\S\s]+)({arg_next} : )",
            argstr,
            flags=re.MULTILINE,
        ).groups()[1:3]
    argtypes[args[-1]], argdescr[args[-1]] = re.search(
        rf"^\s+({args[-1]} : )(.+)$\s^\s+([\S\s]+)", argstr, flags=re.MULTILINE
    ).groups()[1:]

    # Clean text descriptions
    for arg in args:
        argdescr[arg] = argdescr[arg].strip()
        argdescr[arg] = re.sub(r"\n[\s]*", " ", argdescr[arg])

    # Done
    return argtypes, argdescr


def run_via_cmdline(
    argv,
    image_analysis_func,
    analysis_kwargs={},
    analysis_cache={},
    manager_kwargs={},
):
    """Parses command-line arguments and launches the MATE manager event loop.

    This is intended to be called through a MATE config file (see `run` dir for
    examples), which specifies the image analysis pipeline function to use
    (`image_analysis_func`) and optionally fixes any other parameters.

    The MATE event loop target directory (`target_dir`) must be provided as the
    first positional argument of the command line invocation.

    For all other arguments, the command line tool is dynamically generated to
    expose any suitable kwargs of `run_mate_manager` that are *not* already
    specified in `manager_kwargs`, as well as any suitable kwargs of the
    `image_analysis_func` that are *not* already given in `analysis_kwargs` or
    in `analysis_cache`. Any arguments that do not have type "bool", "int",
    "float", or "str" as their main doc string type annotation are ignored.

    Note: This feature *strictly* depends on numpy-style doc strings for the
    provided `image_analysis_func`, which *must* include both a Parameters and
    a Returns section and *must* document all parameters.

    For more information on the MATE event loop itself, see the function that
    this one ultimately calls: `mate.manager.manager.run_mate_manager()`.

    Parameters
    ----------
    argv : list
        List of command line arguments exactly as returned by `sys.argv`.
    image_analysis_func : callable
        Function that performs image analysis on detected files and returns new
        coordinates for transmission to the microscope.
        This function *must* have a numpy-style doc string that documents *all*
        parameters and has both a Parameters and a Returns section.
        Call signature:
        ```
        z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
            target_path, **img_kwargs, **img_cache)
        ```
        The `target_path` argument corresponds to the first and only required
        argument in the cmdline call signature generated here. The keyword
        arguments (both `img_kwargs` and `img_cache`) will be parsed from the
        function's numpy-style doc string and exposed to the cmdline interface
        unless they are already set in `analysis_kwargs` and `analysis_cache`,
        respectively (see below).
        Note that all keyword arguments provided via the command line will be
        treated as `img_kwargs`, not as `img_cache`. This means `img_cache`
        arguments cannot be provided via the command line and must instead be
        given in `analysis_cache` (or left blank) to function properly.
    analysis_kwargs : dict, optional, default {}
        Additional keyword arguments to be passed to the image analysis func as
        `**img_kwargs`. These will not be exposed to the cmdline interface.
    analysis_cache : dict, optional, default {}
        Additional keyword arguments to be passed to the image analysis func as
        `**img_cache`. These will not be exposed to the cmdline interface.
    manager_kwargs : dict, optional, default {}
        Additional keyword arguments to be passed to `run_mate_manager`. These
        will not be exposed to the cmdline interface.
    """

    # Prep description
    description = "Start a MATE session.\n\n"
    description += "Already fixed arguments:"
    description += f"\n  image_analysis_func: {image_analysis_func.__name__}"
    if manager_kwargs:
        for k in manager_kwargs:
            description += f"\n  {k}: {manager_kwargs[k].__repr__()}"
    if analysis_kwargs:
        description += "\n  analysis_kwargs:"
        for k in analysis_kwargs:
            description += f"\n    {k}: {analysis_kwargs[k].__repr__()}"
    if analysis_cache:
        description += "\n  analysis_cache:"
        for k in analysis_cache:
            description += f"\n    {k}: {analysis_cache[k].__repr__()}"

    # Prep parser
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add strictly required cmdline arguments
    parser.add_argument(
        "target_dir", help="Path to the directory that is to be monitored."
    )

    # Configure supported types for keyword arguments
    type_dict = {"bool": bool, "int": int, "float": float, "str": str}

    # Get run_mate_manager arguments
    mgr_args = _get_func_args(mate_manager.run_mate_manager)

    # Get run_mate_manager argument types and descriptions from doc string
    mgr_argtypes, mgr_argdescr = _get_docstr_args_numpy(
        mate_manager.run_mate_manager
    )

    # Add run_mate_manager arguments to parser
    for arg in mgr_args:

        # Skip fixed arguments
        if arg in ["target_dir", "image_analysis_func"]:
            continue

        # Skip arguments provided via config file
        if arg in manager_kwargs:
            continue

        # Skip arguments that cannot be provided via cmdline
        if not any([mgr_argtypes[arg].startswith(t) for t in type_dict]):
            continue

        # Add argument
        parser.add_argument(
            "--" + arg,
            default="__NOT_PROVIDED__",
            help=f"[{mgr_argtypes[arg]}] {mgr_argdescr[arg]}",
        )

    # Get image_analysis_func arguments
    ana_args = _get_func_args(image_analysis_func)

    # Get image_analysis_func argument types and descriptions from doc string
    try:
        ana_argtypes, ana_argdescr = _get_docstr_args_numpy(
            image_analysis_func
        )
    except Exception as e:
        print(
            "[!!] Failed to parse doc string of `image_analysis_func`; may "
            + "not be a proper numpy-style doc string, may be missing either "
            + "the Parameters and/or the Returns section, or may not have all"
            + "its parameters fully documented."
        )
        print("[!!] The exception raised was:")
        raise (e)

    # Add image_analysis_func arguments to parser
    for arg in ana_args:

        # Skip fixed arguments
        if arg in ["target_path"]:
            continue

        # Skip arguments provided via config file
        if arg in analysis_kwargs:
            continue
        if arg in analysis_cache:
            continue

        # Skip arguments that cannot be provided via cmdline
        if not any([ana_argtypes[arg].startswith(t) for t in type_dict]):
            continue

        # Add argument
        parser.add_argument(
            "--" + arg,
            default="__NOT_PROVIDED__",
            help=f"[{ana_argtypes[arg]}] {ana_argdescr[arg]}",
        )

    # Parse arguments
    cmd_args = vars(parser.parse_args(argv[1:]))

    # Pop out target_dir
    target_dir = cmd_args.pop("target_dir")

    # Separate manager and analysis arguments
    # Note: There's currently no way of separating out img_cache arguments.
    cmd_mgr_kwargs = {k: v for k, v in cmd_args.items() if k in mgr_args}
    cmd_ana_kwargs = {k: v for k, v in cmd_args.items() if k in ana_args}

    # Remove arguments that were not provided
    cmd_mgr_kwargs = {
        k: v for k, v in cmd_mgr_kwargs.items() if v != "__NOT_PROVIDED__"
    }
    cmd_ana_kwargs = {
        k: v for k, v in cmd_ana_kwargs.items() if v != "__NOT_PROVIDED__"
    }

    # Handle argument types
    # Note: Argparse fails at this because there's no way of providing defaults
    #       of a different type, which would be required here to give deference
    #       to the defaults of the functions themselves.
    for arg in cmd_mgr_kwargs:
        for t in type_dict:
            if mgr_argtypes[arg].startswith(t):
                cmd_mgr_kwargs[arg] = type_dict[t](cmd_mgr_kwargs[arg])
    for arg in cmd_ana_kwargs:
        for t in type_dict:
            if ana_argtypes[arg].startswith(t):
                cmd_ana_kwargs[arg] = type_dict[t](cmd_ana_kwargs[arg])

    # Combine with arguments from config file
    manager_kwargs = manager_kwargs | cmd_mgr_kwargs
    analysis_kwargs = analysis_kwargs | cmd_ana_kwargs

    # Add analysis_kwargs into manager_kwargs
    manager_kwargs["img_kwargs"] = analysis_kwargs
    manager_kwargs["img_cache"] = analysis_cache

    # Start MATE event loop
    coordinates, stats_dict = mate_manager.run_mate_manager(
        target_dir, image_analysis_func, **manager_kwargs
    )

    # Done
    return coordinates, stats_dict
