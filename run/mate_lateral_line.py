# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:30:55 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Mate execution file for zebrafish posterior lateral line tracking.

@usage:     From the command line, with python and the MATE package installed,
            run `python mate_lateral_line.py <target_dir> [args]`
"""

### PREP

from mate.manager.cmdline import run_via_cmdline

# -----------------------------------------------------------------------------

### USER CONFIGURATION: Image analysis pipeline function [REQUIRED]

# - Import your image analysis pipeline function as `image_analysis_func`
# - Pipeline functions will be called by MATE with the following signature:
#     z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
#         target_path, verbose=verbose, **img_kwargs, **img_cache)
# - They must therefore accept only one positional argument, which is the path
#   to the image file to be analyzed
# - They must also accept `verbose` as a positional argument, a Boolean that
#   can be used to control whether outputs should be printed
# - They may accept any number of extra arguments (img_kwargs and img_cache);
#   the initial values for these argument should be specified below

from mate.pipelines.lateral_line import analyze_image as image_analysis_func

# -----------------------------------------------------------------------------

### USER CONFIGURATION: Image analysis keyword arguments [optional]

# - Arguments not specified here will be taken from command line input
# - If they are also not specified there, the keyword's default value is used

analysis_kwargs = {
    #"verbose" : False,                                                        # TODO: This is anyway forwarded separately, but maybe that should be removed?!
    #"channel" : None,                                                         # TODO: Can you parse this from the func definition and expose it to the command line?!
    "show"    : False,
}
# TODO: Consider the distinction between kwargs and cache lol...

# -----------------------------------------------------------------------------

### USER CONFIGURATION: Mate manager keyword arguments [optional]

# - Arguments not specified here will be taken from command line input
# - If they are also not specified there, the keyword's default value is used

manager_kwargs = {}

# -----------------------------------------------------------------------------

### RUN FROM THE COMMAND LINE

# - Ensure the right python environment with MATE installed is active
# - Ensure you are in the `MATE\run` folder, where this file is located
# - Start MATE by running `python mate_lateral_line.py <target_dir> [args]`

if __name__ == "__main__":
    run_via_cmdline(
        image_analysis_func,
        analysis_kwargs,
        manager_kwargs
    )

# -----------------------------------------------------------------------------

### ALTERNATIVELY: RUN FROM OTHER PYTHON CODE (e.g. jupyter notebook)

# - Ensure this file is part of your path, as these execution files are user-
#   facing and *not* installed with the MATE package
# - You can load the configs here using `import mate_lateral_line.py as *`
# - Import and call `mate.manager.manager.run_mate_manager` to start MATE
