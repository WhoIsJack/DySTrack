# -*- coding: utf-8 -*-
"""
Created on Fri Jun 20 19:30:55 2025

@authors:   Jonas Hartmann @ Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  DySTrack config file for tracking of the migratory zebrafish 
            posterior lateral line primordium.

@usage:     From the command line (with the dystrack python environment active)
            run `python run_lateral_line.py <target_dir> [args]`.
"""

### Prep

from dystrack.manager.cmdline import run_via_cmdline


# -----------------------------------------------------------------------------
# USER CONFIGURATION SECTION
# -----------------------------------------------------------------------------


### USER CONFIGURATION: Image analysis pipeline function [REQUIRED]

# - Import the desired image analysis pipeline as `image_analysis_func`
# - Pipeline functions included in DySTrack are found in `dystrack.pipelines`
#
# - Alternatively, it could be a custom function with this call signature:
#
#     ```
#     z_pos, y_pos, x_pos, img_msg, img_cache = image_analysis_func(
#         target_path, **img_kwargs, **img_cache
#     )
#     ```
#
# - Such functions must accept only one positional argument, which is the path
#   to the image file to be analyzed
# - They may accept any number of additional keyword arguments (see below)
# - To run DySTrack from the command line, these functions *must* have a numpy-
#   style doc string that documents *all* parameters and has both a Parameters 
#   and a Returns section

from dystrack.pipelines.lateral_line import analyze_image as image_analysis_func


### USER CONFIGURATION: Image analysis keyword arguments [optional]

# - This dictionary will be forwarded as `**img_kwargs` to `img_analysis_func`
# - Arguments not specified here can be provided as command line input *if* 
#   they are of type `bool`, `int`, `float`, or `str`
# - For any arguments not specified either here or in the command line, the
#   function's default values will be used

analysis_kwargs = {
    "gauss_sigma" : 3,      # Use 3 for cldnb, 1 for KTR green
    "verbose"     : True,
    "show"        : False,
}


### USER CONFIGURATION: *Cached* image analysis keyword arguments [optional]

# - This dictionary will be forwarded as `**img_cache` to `img_analysis_func`
# - Unlike `analysis_kwargs` above, this dictionary will be updated each time
#   the image analysis pipeline is called (see call signature above)
# - Note that cache arguments cannot be provided via the command line, as they
#   would then be treated as ordinary keyword arguments (triggering an error),
#   so they must be provided here (or left empty, in which case the function's
#   defaults will be used)
# - Many pipelines do not use this feature, in which case an empty dict is fine

analysis_cache = {}


### USER CONFIGURATION: DySTrack manager keyword arguments [optional]

# - Arguments not specified here can be provided as command line input
# - For any arguments not specified either here or in the command line, the
#   function's default values will be used

manager_kwargs = {
    "file_start" : "Prescan_",
    "file_end"   : ".tif",
}


# -----------------------------------------------------------------------------
# EMD OF USER CONFIGURATION SECTION
# -----------------------------------------------------------------------------


### Run from command line

# - Ensure DySTrack is installed and the right python environment is active
# - Ensure you are in the `DySTrack\run` folder, where this file is located
# - Start DySTrack by running `python run_lateral_line.py <target_dir> [args]`

if __name__ == "__main__":
    import sys
    run_via_cmdline(
        sys.argv,
        image_analysis_func,
        analysis_kwargs,
        analysis_cache,
        manager_kwargs
    )


### ALTERNATIVELY, DySTrack can be run from other python code (e.g. jupyter nb)

# - An example can be found in `notebooks/Run DySTrack from Jupyter.ipynb`
# - Ensure this file is available in your python path, as these config files 
#   are user-facing and *not* installed along with the DySTrack package;
#   e.g. `sys.path.insert(0, r"<<path_to_run_dir>>")`
# - You can then load the configurations specified here using e.g.
#   `import run.run_lateral_line as run_ll`
# - To run DySTrack, import `dystrack.manager.manager.run_dystrack_manager` and
#   call it with the appropriate arguments (see its doc string)
