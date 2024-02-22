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


#------------------------------------------------------------------------------

# MAIN FUNCTION

def main():
    """Parses command-line arguments and initializes the scheduler."""
     
    # Help
    if '-h' in sys.argv or '--help' in sys.argv:
        print("""
        run_mate TARGET_DIR [-s START] [-e END] [-c CHANNEL] [-w] [-v]
        
        Tool to be used in conjunction with LSM880 (ZEN BLACK) and the pipeline
        constructor macro to automatically track moving zebrafish posterior
        lateral line primordia across several embryos (positions) during a
        timecourse.
        
        Monitors a directory (and its subdirectories) for low-res stacks or 
        slices produced by the scope and determines the positional shift 
        required for the subsequent hi-res stack to be positioned correctly 
        with regard to the prim. 
        
        Parameters
        ----------
        TARGET_DIR : string
            Path to the directory to be monitored.
        CHANNEL : int, optional
            Integer denoting the channel that should be used for masking for
            multi-channel images. If no channel is given, a single-channel
            image is assumed!
        START : string, optional
            Target files must contain this string at the start of their name.
        END : string, optional
            Target files must contain this string at the end of their name.
        -w : flag, optional
            If given, the calculated coordinates are written to the Windows
            registry instead of a txt file. This is required when using the
            MyPiC pipeline constructor macro on ZEN Black.
        -v : flag, optional
            If given, the program runs in verbose mode, printing more info.
        """)
        sys.exit()
    
    # Get positional arguments
    TARGET_DIR = sys.argv[1]
    if not os.path.isdir(TARGET_DIR):
        raise IOError(TARGET_DIR+" is not a valid dir. See pt880_start -h for help.")
    
    # Get optional arguments
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
    
    # Start the scheduler
    stats = main_scheduler(TARGET_DIR, img_params=CHANNEL,
                           fileStart=FILESTART, fileEnd=FILEEND,
                           write_winreg=WINREG, verbose=VERBOSE)
    
    # Done
    return stats


#------------------------------------------------------------------------------

# FUNCTION FOR MONITORING AND SCHEDULING

def main_scheduler(target_dir, interval=1, fileStart='', fileEnd='',
                   img_params=None, scope_params=None,
                   write_winreg=False, verbose=False):
    """
        Checks a target directory and its subdirectores for new files using 
        os.walk. For each file found that matches a particular starting and/or 
        ending sequence, the masking & microscope-instruction pipeline is run.
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
            Default is ''.
        fileEnd : string, optional
            Only files that end with this string will trigger the pipeline.
            Default is ''.
        img_params : object or iterable, optional
            Additional parameter or parameters to be passed to the img analysis
            function when it is called. Default is None.
        scope_params : object or iterable, optional
            Additional parameter or parameters to be passed to the microscope
            communication function when it is called. Default is None.
        write_winreg : bool, optional
            If True, calculated coordinates are written to the Windows registry
            instead of a txt file. This is required when using the MyPiC
            pipeline constructor macro on ZEN Black.
            
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
    
    
    #..........................................................................
  
    # PREPARATION
    
    # Report
    print("\n\nMONITORING IN PROGRESS...")
    print("Press <Esc> to terminate.\n")   
    
    # Prep
    dirlist = [os.path.join(dir_info[0],fname) for dir_info in os.walk(target_dir) for fname in dir_info[2]]
    
    # Stats
    check_counter = 0
    new_counter = 0
    target_counter = 0
    img_success_counter = 0
    reg_success_counter = 0
    
    
    #..........................................................................
    
    # RUN MONITORING 
    
    # Enter infinite loop
    while True:
    
        # Listen for ESC keypress to exit loop
        if kbhit():
            if ord(getch()) == 27:
                break

        # Comb through dir and subdirs, create list of all files' full paths
        new_dirlist = [os.path.join(dir_info[0],fname) for dir_info in os.walk(target_dir) for fname in dir_info[2]]
        
        # If something has changed...
        if new_dirlist != dirlist:
            
            # Get all the new files
            new_files = [f for f in new_dirlist if f not in dirlist]

            # Stats
            check_counter += 1
            new_counter += len(new_files)     
            
            # For each new file...
            for f in new_files:
                
                # If the file matches the conditions...
                if os.path.split(f)[1].startswith(fileStart) and f.endswith(fileEnd):
                    
                    # Stats
                    target_counter += 1  
                    
                    
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    
                    # RUN THE IMAGE ANALYSIS PIPELINE
                    
                    # Report
                    print("\n  Target file detected:", f)
                    print("    Running image analysis...")
                    
                    # Try running it
                    try:
                        
                        # Prep
                        img_path = os.path.join(target_dir,f)
                        
                        # RUN IT!
                        z_pos,y_pos,x_pos = analyze_image(
                            img_path, channel=img_params,
                            show=False, verbose=verbose)
                        
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
                        #       even the same shift as for the last timepoint!
                        z_pos,y_pos,x_pos = (None,None,None)
                        codeM  = "nothing"  # Continues with previous position
                        errMsg = "Image analysis failed."
                    
                    
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
                    
                    # SUBMIT THE NEW COORDINATES TO THE SCOPE

                    # If something fails, try again a few times
                    attempts = 0
                    while attempts < 3:
                        attempts += 1                        
                        
                        # SUBMIT THE COORDS!
                        if write_winreg:
                            no_error = send_coords_winreg(
                                z_pos, y_pos, x_pos, 
                                codeM=codeM, errMsg=errMsg)
                        else:
                            no_error = send_coords_txt(
                                coords_path, z_pos, y_pos, x_pos, 
                                codeM=codeM)
                        
                        # Check if it worked
                        if no_error:
                            reg_success_counter += 1
                            break
                    
                    # Report
                    if no_error:
                        print("    Coords pushed.")
                        print("    Resuming monitoring...")
                    
                    # Desperately try to handle an error
                    else:      
                        
                        # Try just running it with the last position
                        if write_winreg:
                            no_error = send_coords_winreg(
                                codeM="nothing",
                                errMsg="Coordinate communication failed!")
                        else:
                            raise NotImplementedError("Retrying with the previous position is not yet implemented for send_coords_txt!")
                                                     
                        # Report if this final solution worked or not
                        if no_error:
                            warn("Coordinate communication failed! Using previous coordinates.")
                        else: 
                            warn("TERMINAL FAILURE OF SCOPE COMMUNICATION! " +
                                 "Pipeline constructor may continue with " +
                                 "previous coordinates once the waiting " +
                                 "time limit has elapsed.")
                                 
                        # Move on and hope for the best
                        print("    Resuming monitoring...")
                    
                    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

            
            # Remember the new list
            dirlist = new_dirlist
            
            # Start looking again
            continue
        
        # If nothing is found, wait for the interval to pass
        check_counter += 1
        sleep(interval)


    #..........................................................................

    # FINISH AND REPORT
    
    # Report
    print("\n\nMONITORING TERMINATED!")
    print("  Stats:")
    print("    Total checks made:", check_counter)
    print("    Total new files found:", new_counter)
    print("    Total target files found:", target_counter)
    print("      Successfully analyzed:", img_success_counter)
    print("      Coords sent to scope:", reg_success_counter)
   
    # Return information
    return [check_counter,new_counter,target_counter,img_success_counter,reg_success_counter]


#------------------------------------------------------------------------------

# RUN MAIN

if __name__ == '__main__':
    main()
    print("\n\n---PROGRAM COMPLETE---")


#------------------------------------------------------------------------------



