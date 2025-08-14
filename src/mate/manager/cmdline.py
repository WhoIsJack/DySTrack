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

import mate.manager.manager as mate_manager


def _get_func_args(func):
    """Get a tuple of all arguments in the function definition of `func`."""
    func_n_args = func.__code__.co_argcount
    func_vars = func.__code__.co_varnames
    return func_vars[:func_n_args]


def _get_docstr_args_numpy(func):
    """Get the argument types and argument descriptions from a numpy-style doc
    string of function `func`."""
    # TODO: This is simultaneously fun and cringe; look into numpydoc module?!

    # Get arguments and doc string
    args = _get_func_args(func)
    docstr = func.__doc__

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
    image_analysis_func, analysis_kwargs={}, manager_kwargs={}
):
    """Parses command-line arguments and launches the MATE manager event loop.

    This is intended to be called through a MATE config file (see `run` dir for
    examples), which specifies the image analysis pipeline function to use
    (`image_analysis_func`) and optionally fixes any other parameters.

    The MATE event loop target directory (`target_dir`) must be provided as the
    first positional argument of the command line invocation.

    For all other arguments, the command line tool is dynamically generated to
    expose any suitable kwargs of `run_mate_manager` (that are *not* already
    specified in `manager_kwargs`), as well as any suitable kwargs of the
    `image_analysis_func` (that are *not* already given in `analysis_kwargs`.
    (Note that this feature depends on numpy-style doc strings.)

    For more information on the MATE event loop, see the function that this
    ultimately calls: `mate.manager.manager.run_mate_manager()`.
    """

    # Prep description
    description = "Start a MATE session.\n\n"
    description += "already fixed arguments:"
    description += f"\n  image_analysis_func: {image_analysis_func.__name__}"
    if manager_kwargs:
        for k in manager_kwargs:
            description += f"\n  {k}: {manager_kwargs[k].__repr__()}"
    if analysis_kwargs:
        description += "\n  analysis_kwargs:"
        for k in analysis_kwargs:
            description += f"\n    {k}: {analysis_kwargs[k].__repr__()}"

    # Prep parser
    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # Add strictly required cmdline arguments
    parser.add_argument(
        "target_dir", help="Path to the directory that is to be monitored."
    )

    # Get run_mate_manager arguments
    mgr_args = _get_func_args(mate_manager.run_mate_manager)

    # Get run_mate_manager argument descriptions from doc string
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
        if arg in ["img_kwargs", "img_cache", "tra_kwargs"]:
            continue

        # Add argument
        parser.add_argument(
            "--" + arg,
            default="__NOT_PROVIDED__",
            help=f"[{mgr_argtypes[arg]}] {mgr_argdescr[arg]}",
        )

    # Get image_analysis_func arguments
    ana_args = _get_func_args(image_analysis_func)

    # Get image_analysis_func argument descriptions from doc string
    try:
        ana_argtypes, ana_argdescr = _get_docstr_args_numpy(
            image_analysis_func
        )
    except:
        ana_argtypes = {
            k: "Failed to parse image analysis function doc string!"
            for k in ana_args
        }
        ana_argdescr = {k: "" for k in ana_args}

    # Add image_analysis_func arguments to parser
    for arg in ana_args:

        # Skip fixed arguments
        if arg in ["target_path"]:
            continue

        # Skip arguments provided via config file
        if arg in analysis_kwargs:
            continue

        # Skip arguments that cannot be provided via cmdline
        # ->> This can't easily be done for arbitrary functions

        # Add argument
        parser.add_argument(
            "--" + arg,
            default="__NOT_PROVIDED__",
            help=f"[{ana_argtypes[arg]}] {ana_argdescr[arg]}",
        )

    # Parse arguments
    cmd_args = vars(parser.parse_args())

    # Pop out target_dir
    target_dir = cmd_args.pop("target_dir")

    # Separate manager and analysis arguments
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
    #       of a different type, which is required here to give deference to
    #       the defaults of the functions themselves...
    for arg in cmd_mgr_kwargs:
        if mgr_argtypes[arg].startswith("bool"):
            cmd_mgr_kwargs[arg] = bool(cmd_mgr_kwargs[arg])
        if mgr_argtypes[arg].startswith("int"):
            cmd_mgr_kwargs[arg] = int(cmd_mgr_kwargs[arg])
        if mgr_argtypes[arg].startswith("float"):
            cmd_mgr_kwargs[arg] = float(cmd_mgr_kwargs[arg])
    for arg in cmd_ana_kwargs:
        if ana_argtypes[arg].startswith("bool"):
            cmd_ana_kwargs[arg] = bool(cmd_ana_kwargs[arg])
        if ana_argtypes[arg].startswith("int"):
            cmd_ana_kwargs[arg] = int(cmd_ana_kwargs[arg])
        if ana_argtypes[arg].startswith("float"):
            cmd_ana_kwargs[arg] = float(cmd_ana_kwargs[arg])

    # Combine with arguments from config file
    manager_kwargs = manager_kwargs | cmd_mgr_kwargs
    analysis_kwargs = analysis_kwargs | cmd_ana_kwargs

    # Add analysis_kwargs into manager_kwargs
    manager_kwargs["img_kwargs"] = analysis_kwargs

    # Start MATE event loop
    coordinates, stats_dict = mate_manager.run_mate_manager(
        target_dir, image_analysis_func, **manager_kwargs
    )

    # Done
    return coordinates, stats_dict
