# -*- coding: utf-8 -*-
"""
Created on Sun Jan 15 00:34:07 2017

@authors:   Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)
            Zimeng Wu @ Wong group (UCL)

@descript:  Main script to run the MATE manager. This script monitors a target
            directory (and its subdirectories) for images produced by the scope
            that fit certain criteria, then triggers an image analysis pipeline
            that determines the new coordinates to be sent to the microscope,
            or rather to the relevant macro running in the scope's software.
            
@usage:     Run from Windows command line. 
            See 'python run_mate.py -h' for help.
"""


### Imports

import sys, os
from warnings import simplefilter, warn
simplefilter('always', UserWarning)

from msvcrt import kbhit, getch
from time import sleep

from masking.lateral_line import analyze_image
from feedback import send_coords_winreg, send_coords_txt


### Main function

def main():
    """Parses command-line arguments and initializes the scheduler."""
     
    # Help
    if '-h' in sys.argv or '--help' in sys.argv:
        print("""
        run_mate TARGET_DIR [-s START] [-e END] [-c CHANNEL] [-w] [-v] [-p]

        Start up a MATE manager session.

        MATE is a tool to automatically track moving objects using adaptive
        feedback microscopy ("smart microscopy").
        
        A MATE manager session monitors a target directory (and its subdirs)
        for image files produced by the microscope (usually low-resolution
        slices or stacks produced with "pre-scan" settings). When such a file
        is detected, MATE manager triggers an image analysis workflow defined
        in a separate python script. This workflow processes the image and
        returns new coordinates that the microscope should use in order to
        track the moving object. MATE manager then forwards these coordinates
        to the microscope and triggers the next step, usually a high-resolution
        acquisition of the moving object.

        For this to work, the microscope must run a Macro that is compatible
        with MATE and handles the acquisition settings.
        
        Parameters
        ----------
        TARGET_DIR : string
            Path to the directory to be monitored.
        CHANNEL : int, optional
            Integer (starting at 0) that denotes the channel which should be 
            used for masking for multi-channel images. If no channel is given, 
            a single-channel image is assumed!
        START : string, optional
            Target files must contain this string at the start of their name.
        END : string, optional
            Target files must contain this string at the end of their name.
        -w : flag, optional
            If given, the calculated coordinates are written to the Windows
            registry instead of a txt file. This is required when using the
            MyPiC pipeline constructor macro on ZEN Black (ZEISS).
        -v : flag, optional
            If given, the program runs in verbose mode, printing more info.
        -p : flag, optional
            If given, the image analysis pipeline generates plots.
        """)
        sys.exit()
    
    # Get positional arguments
    TARGET_DIR = sys.argv[1]
    if not os.path.isdir(TARGET_DIR):
        raise IOError(TARGET_DIR + " is not valid. See run_mate -h for help.")
    
    # Get optional arguments
    # TODO: Use an automated cmdline parser to do all this much more cleanly!
    if "-c" in sys.argv:
        CHANNEL = int(sys.argv[sys.argv.index("-c")+1])
    else:
        CHANNEL = None
    if "-s" in sys.argv:
        FILESTART = sys.argv[sys.argv.index("-s")+1]
    else:
        FILESTART = ''
    if "-e" in sys.argv:
        FILEEND = sys.argv[sys.argv.index("-e")+1]
    else:
        FILEEND = ''
    if "-w" in sys.argv:
        WINREG = True
    else:
        WINREG = False
    if "-v" in sys.argv:
        VERBOSE = True
    else:
        VERBOSE = False
    if "-p" in sys.argv:
        PLOT = True
    else:
        PLOT = False
    
    # Start the scheduler
    stats = main_scheduler(
        TARGET_DIR, 
        img_params={'channel':CHANNEL, 'show':PLOT},
        fileStart=FILESTART, fileEnd=FILEEND,
        write_winreg=WINREG, verbose=VERBOSE)
    
    # Done
    return stats


### Monitoring session scheduler

def main_scheduler(target_dir, interval=1, fileStart='', fileEnd='',
                   img_params={}, scope_params={},
                   write_winreg=False, verbose=False):
    """Monitors a target directory and its subdirectores for new files using 
    `os.walk`. For each file found that matches a particular starting and/or 
    ending sequence, the masking and microscope instruction pipelines are run.

    Keeps going until the Esc key is pressed.
        
    Must be run from a windows console to work properly.

    Parameters
    ----------
    target_dir : path-like
        Path to the directory that is to be monitored.
    interval : float, optional
        Time (in seconds) to wait between two checks of the directory.
        Default is 1.0 second.
    fileStart : string, optional
        Only files that start with this string will trigger the pipeline.
        Default is an empty string.
    fileEnd : string, optional
        Only files that end with this string will trigger the pipeline.
        Default is an empty string.
    img_params : dict, optional
        Additional parameter or parameters to be passed to the img analysis
        function. Default is empty dict.
    scope_params : dict, optional
        Additional parameter or parameters to be passed to the microscope
        communication function. Default is empty dict.
    write_winreg : bool, optional
        If True, calculated coordinates are written to the Windows registry
        instead of a txt file. This is required when using the MyPiC
        pipeline constructor macro on ZEN Black (ZEISS).
        
    Returns
    -------
    stats : list
        A list containing the following stats about the run: number of
        checks made (checks_counter), number of times a check triggered
        (hits_counter), number of files found (files_counter).
        
    WARNING
    -------
    This function runs on WINDOWS ONLY and only works properly if called in
    a python process that was started from a Windows console.
    """

  
    ### Preparation
    
    # Report
    print("\n\n  MATE MONITORING SESSION IN PROGRESS...")
    print("  Press <Esc> to terminate.\n")   
    
    # Prep
    paths = [
        os.path.join(dir_info[0], fname) 
        for dir_info in os.walk(target_dir) 
        for fname in dir_info[2]]
    
    # Stats
    check_counter = 0
    new_counter = 0
    target_counter = 0
    img_success_counter = 0
    reg_success_counter = 0
    
    
    ### Run monitoring loop
    
    # Enter infinite loop
    while True:
    
        # Listen for ESC keypress to exit loop
        # FIXME: I think this sometimes doesn't work if other keys were pressed
        #        prior to ESC being pressed. To be investigated!
        if kbhit():
            if ord(getch()) == 27:
                break

        # Comb through dir and subdirs, create list of all files' full paths
        new_paths = [
            os.path.join(dir_info[0], fname) 
            for dir_info in os.walk(target_dir) 
            for fname in dir_info[2]]
        
        # If something has changed...
        if new_paths != paths:
            
            # Get all new files
            new_files = [f for f in new_paths if f not in paths]

            # Stats
            check_counter += 1
            new_counter += len(new_files)     
            
            # For each new file...
            # TODO: Refactor the parts of this inner loop!
            for f in new_files:
                
                # If the file matches the conditions...
                if (os.path.split(f)[1].startswith(fileStart) 
                    and f.endswith(fileEnd)
                    and os.path.split(f)[1] != 'mate_coords.txt'):
                    
                    # Stats
                    target_counter += 1  
                    
                    
                    ### Run image analysis pipeline
                    
                    # Report
                    print("\n    Target file detected:", f)
                    print("    Running image analysis...")
                    
                    # Try running it
                    try:
                        
                        # Run
                        z_pos, y_pos, x_pos = analyze_image(
                            f, verbose=verbose, **img_params)
                        
                        # Report
                        errMsg = None
                        codeM = 'focus'
                        img_success_counter += 1
                        print("    Image analysis complete.")
                        print("    Pushing coords to scope...")
                        
                    # Handle unexpected failures
                    except:
                        warn("IMAGE ANALYSIS FAILED! Using previous position...")
                        # TODO: Would be nice to have a default shift here, or
                        #       even the same shift as for the last timepoint,
                        #       or best of all a PID-calculated shift (lol...).
                        if write_winreg:
                            # Will continue with previous position in MyPiC
                            z_pos, y_pos, x_pos = (None, None, None)
                            codeM = "nothing"
                        else:
                            # Will write previous position again on new line in coords txt file
                            # FIXME: If this point is hit during the first loop, there will be a hard error 
                            #        when trying to write the coords txt file, as in that case the *_pos are
                            #        undefined. Ultimately, the cleanest way to handle this is to implement 
                            #        reuse of previous position in the macro itself!
                            codeM = "IMAGE_ANALYSIS_FAILED"
                        errMsg = "Image analysis failed."
                    
                    
                    ### Submit coordinates to the scope

                    # If something fails, retry a few times
                    attempts = 0
                    while attempts < 3:
                        attempts += 1                        
                        
                        # Submit
                        if write_winreg:
                            no_error = send_coords_winreg(
                                z_pos, y_pos, x_pos, 
                                codeM=codeM, errMsg=errMsg,
                                **scope_params)
                        else:
                            coords_path = os.path.join(
                                target_dir, 'mate_coords.txt')
                            no_error = send_coords_txt(
                                coords_path, z_pos, y_pos, x_pos, 
                                codeM=codeM, 
                                **scope_params)
                        
                        # Check if it worked
                        if no_error:
                            reg_success_counter += 1
                            break
                    
                    # Report
                    if no_error:
                        print("    Coords pushed.")
                        print("    Resuming monitoring...")
                    
                    # Try to handle error cases
                    else:      
                        
                        # Try just running it with the previous position
                        if write_winreg:
                            no_error = send_coords_winreg(
                                codeM="nothing",
                                errMsg="Coordinate communication failed!",
                                **scope_params)
                        else:
                            raise NotImplementedError("No fallback option implemented yet for failure to write coordinate text file.")  # TODO!
                                                     
                        # Report if this final attempt worked or not
                        if no_error:
                            warn("Coordinate communication failed! Using previous coordinates.")
                        else: 
                            warn("TERMINAL FAILURE OF SCOPE COMMUNICATION! " +
                                 "Pipeline constructor may continue with " +
                                 "previous coordinates once the waiting " +
                                 "time limit has elapsed.")
                                 
                        # Move on and hope for the best
                        print("    Resuming monitoring...")
            
            # Remember the new list
            paths = new_paths
            
            # Start looking again
            continue
        
        # If nothing is found, wait for the interval to pass
        check_counter += 1
        sleep(interval)


    ### Report and return
    
    # Report
    print("\n\n  MATE MONITORING SESSION TERMINATED!")
    print("\n    Stats:")
    print("      Total checks made:", check_counter)
    print("      Total new files found:", new_counter)
    print("      Total target files found:", target_counter)
    print("        Successfully analyzed:", img_success_counter)
    print("        Coords sent to scope:", reg_success_counter)
   
    # Return information
    return check_counter, new_counter, target_counter, img_success_counter, reg_success_counter


### Run main

if __name__ == '__main__':
    main()



