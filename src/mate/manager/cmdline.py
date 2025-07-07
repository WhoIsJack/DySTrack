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

import mate.manager.manager as mate_manager


def _get_func_args(func):
    func_n_args = func.__code__.co_argcount
    func_vars = func.__code__.co_varnames
    return func_vars[:func_n_args]


def _get_docstr_args_numpy(func, args):
    # TODO: This is simultaneously fun and cringe; look into numpydoc module!

    # Get doc string
    docstr = func.__doc__

    # Filter out Parameters section
    argstr = docstr.split("Parameters\n    ----")[1]
    argstr = argstr.split("Returns\n    ----")[0]

    # Split intos text belonging with each argument
    argstrs = {}
    for arg, arg_next in zip(args[:-1], args[1:]):
        argstrs[arg] = argstr.split(arg + " : ")[1]
        argstrs[arg] = argstrs[arg].split(arg_next + " : ")[0]
    argstrs[args[-1]] = argstr.split(args[-1] + " : ")[1]

    # Split and clean type indicators and descriptions
    argtypes = {k: v.split("\n")[0].strip() for k, v in argstrs.items()}
    argdescr = {
        k: "\n".join(v.split("\n")[1:]).replace("\n    ", " ").strip()
        for k, v in argstrs.items()
    }

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
        mate_manager.run_mate_manager, mgr_args
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
            image_analysis_func, ana_args
        )
    except:
        ana_argtypes = {
            k: "Failed to parse image analysis function doc string!"
            for k in ana_args
        }
        ana_argdescr = {k: "" for k in ana_args}

    # Add image_analysis_func arguments to parser
    for arg in ana_args:

        # Skip fixed or "inherited" arguments
        if arg in ["target_path", "verbose"]:
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

    # Combine analysis_kwargs into manager_kwargs
    manager_kwargs["img_kwargs"] = analysis_kwargs

    # # DEV-TEMP! For testing!
    # print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    # print(target_dir, "\n")
    # for kwarg in manager_kwargs:
    #     if not isinstance(manager_kwargs[kwarg], dict):
    #         print(
    #             kwarg,
    #             manager_kwargs[kwarg],
    #             f"[{type(manager_kwargs[kwarg])}]\n",
    #         )
    #     else:
    #         for kwargkwarg in manager_kwargs[kwarg]:
    #             print(
    #                 "~~",
    #                 kwargkwarg,
    #                 manager_kwargs[kwarg][kwargkwarg],
    #                 f"[{type(manager_kwargs[kwarg][kwargkwarg])}]\n",
    #             )
    # print("\n~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    # # return

    # Start MATE event loop
    coordinates, stats_dict = mate_manager.run_mate_manager(
        target_dir, image_analysis_func, **manager_kwargs
    )

    # Done
    return coordinates, stats_dict


# -----------------------------------------------------------------------------
# DEV-TEMP! For testing!


def my_img_ana_func(target_path, verbose=False, channel=None, sigma=3.0):
    """This my doc string.

    Parameters
    ----------
    target_path : str
        Path to target image file. [MY_IMG_ANA_FUNC]
    verbose : bool, optional, default False
        Whether to print extra information. [MY_IMG_ANA_FUNC]
    channel : int or None, optional, default None
        The channel to use for analysis. [MY_IMG_ANA_FUNC]
    sigma : float, optional, default 3.0
        Sigma of the Gaussian smoothing, in pixels. [MY_IMG_ANA_FUNC]

    Returns
    -------
    Nothing especially
    """
    print(target_path, verbose, channel, sigma)


if __name__ == "__main__":
    run_via_cmdline(
        my_img_ana_func,
        # analysis_kwargs={"channel": 1},
        manager_kwargs={"file_end": ".tif", "file_start": "Prescan_"},
    )
