# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:30:55 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  MATE config file for zebrafish posterior lateral line deposited 
            neuromast tracking/stabilization.

@usage:     From the command line (with python and the MATE package installed)
            run `python run_lateral_line_organ.py <target_dir> [args]`.
"""

### Prep

from mate.manager.cmdline import run_via_cmdline


# -----------------------------------------------------------------------------
# ------------------------ USER CONFIGURATION SECTION: ------------------------
# -----------------------------------------------------------------------------


### USER CONFIGURATION: Image analysis pipeline function [REQUIRED]

# - Import the desired image analysis pipeline as `image_analysis_func`
# - Pipeline functions included in mate are in `mate.pipelines.lateral_line`,
#   but this could also be a custom function
#
# - Pipeline functions will be called by MATE with the following signature:
#
#     ```
#     z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
#         target_path, **img_kwargs, **img_cache)
#     ```
#
# - They must accept only one positional argument, which is the path to the
#   image file to be analyzed
# - They may accept any number of additional keyword arguments

from mate.pipelines.lateral_line_organ import analyze_image as image_analysis_func


# -----------------------------------------------------------------------------


### USER CONFIGURATION: Image analysis keyword arguments [optional]

# - This dictionary will be forwarded as `**img_kwargs` to `img_analysis_func`
# - Arguments not specified here can be provided as command line input
# - If they are also not specified there, the function's default value is used

analysis_kwargs = {
    "gauss_sigma" : 3,
    "verbose"     : True,
    "show"        : False,
}


# -----------------------------------------------------------------------------


### USER CONFIGURATION: *Cached* image analysis keyword arguments [optional]

# - This dictionary will be forwarded as `**img_cache` to `img_analysis_func`
# - Unlike `analysis_kwargs` above, this dictionary will be updated each time
#   the image analysis pipeline is called (see call signature above)
# - Note that cache arguments cannot be provided via the command line, as they
#   will then be treated as ordinary keyword arguments (triggering an error),
#   so they must be provided here (or left empty, in which case the function's
#   defaults will be used)
# - Many pipelines do not use this feature, in which case an empty dict is fine

analysis_cache = {}


# -----------------------------------------------------------------------------


### USER CONFIGURATION: Mate manager keyword arguments [optional]

# - Arguments not specified here can be provided as command line input
# - If they are also not specified there, the function's default value is used

manager_kwargs = {
    "file_start" : "Prescan_",
    "file_end"   : ".tif",
}


# -----------------------------------------------------------------------------
# --------------------- END OF USER CONFIGURATION SECTION ---------------------
# -----------------------------------------------------------------------------


### Run from command line

# - Ensure the right python environment with MATE installed is active
# - Ensure you are in the `MATE\run` folder, where this file is located
# - Start MATE by running `python mate_lateral_line.py <target_dir> [args]`

if __name__ == "__main__":
    run_via_cmdline(
        image_analysis_func,
        analysis_kwargs,
        manager_kwargs
    )


### ALTERNATIVELY, you can run this from other python code (e.g. a jupyter nb)

# - Ensure this file is available in your PAtH, as these config files are user-
#   facing and therefore *not* installed along with the MATE package
# - You can load the configs here using `import mate_lateral_line.py as *`
# - Import `mate.manager.manager.run_mate_manager` and run it with appropriate
#   arguments to start MATE
