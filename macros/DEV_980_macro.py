# -*- coding: utf-8 -*-
"""
Created on Tue Feb 6 17:59:38 2024

@authors:   Zimeng Wu @ Wong group (UCL)
            Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)

@descript:  TODO!
            
@usage:     TODO!
"""

### Prep

# Imports

from __future__ import division, print_function
import sys, os
from System.IO import Path
from System import DateTime
from time import sleep


# User input

# Prescan paths
#prescan_fpath = r'D:\Zimeng\_settings\PRESCAN_488.czexp'  #.czexp file
prescan_czi =   r'D:\Zimeng\_settings\PRESCAN_488.czi'

# Job path
#job_fpath = r'D:\Zimeng\_settings\JOB_488_561.czexp'  #.czexp file
job_czi = r'D:\Zimeng\_settings\JOB_488.czi'
# JH: Almost certainly irrelevant, but the .czexp was "JOB_488_561", whereas job_czi is just "JOB_488"

# Output path
output_folder = r'D:\Zimeng\20240402_KTR_MATE'

# Loop settings
max_iterations = 90  # Number of loops
interval_min   =  2  # Interval in minutes  


### Start experiment

# Clear open images
Zen.Application.Documents.RemoveAll()

# Prep
interval = interval_min * 60000
lines_read = 0
coords_fpath = os.path.join(output_folder, 'mate_coords.txt')

# Start the loop
for i in range(max_iterations):


    ### Prep

    # Timing
    time_before = DateTime.Now
    time_after = time_before.AddMilliseconds(interval)

    # Clear open images
    Zen.Application.Documents.RemoveAll()

    
    ### Prescan

    # Reuse prescan settings
    experiment1 = ZenExperiment()
    experiment1.LoadFromImage(Zen.Application.LoadImage(prescan_czi))
    experiment1.SetActive()

    # AutoSave
    experiment1.AutoSave.Name = 'prescan_%d.czi' % i
    # JH: Check if .Name is the only thing to set; what about .StorageFolder?
    #     See e.g. here for all properties (also includes "ConvertTo8Bit"; maybe relevant?): https://shorturl.at/qBw82
    experiment1.Save()
    # JH: What exactly is this for? Does this save a ZenExperiment? If so, where and as what file does it get saved? When is it reused?
    #     (Note to self: this wouldn't save into 'prescan_%d.czi', as that presumably says where ZenImages acquired under this ZenExperiment
    #      will be stored, not where the ZenExperiment will be stored, which should presumably be a .czexp file.)

    # Acquire prescan
    output_experiment1 = Zen.Acquisition.Execute(experiment1)
    # JH: It would make sense to use variable names that indicate whether it is a ZenExperiment object or a ZenImage.
    #     I'd propose renaming `experiment1` into `prescan_exp` and `output_experiment1` into `prescan_img`
    
    # Get prescan image size for later calculations
    prescan_x = outputexperiment1.Bounds.SizeX
    prescan_y = outputexperiment1.Bounds.SizeY
    prescan_z = outputexperiment1.Bounds.SizeZ
    
    ## Save prescan image
    #output_experiment1.Name = 'prescan_%d.czi'%i 
    #output_experiment1.Save(os.path.join(output_folder, 'prescan_%d.czi'%i))
    
    
    ### Read coords from mate_manager
        
    # During first loop, wait for mate_coords.txt to be generated
    if i==0:   
        while not os.path.isfile(coords_fpath):
            print("Waiting for mate_coords.txt to be generated...")
            sleep(1)
    
    # Wait for mate_coords.txt to be updated with a new line
    while True:
        with open(coords_fpath, 'r') as infile:
            lines = infile.readlines()

            if len(lines) > lines_read:
                newest_line = lines[-1]
                values = newest_line.split()

                x_pos = float(values[2])
                y_pos = float(values[1])
                z_pos = float(values[0])

                lines_read = len(lines)
                break 
        sleep(0.1)
        

    ### Convert new coordinates into the stage's Frame Of Reference (FOR)

    # Convert from corner-of-image FOR to center-of-image FOR
    relative_x = x_pos - (prescan_x/2)
    relative_y = y_pos - (prescan_y/2)
    relative_z = z_pos - ((prescan_z-1)/2)

    # Scale from pixels to microns
    # JH: Where does `image1` come from? It doesn't seem to be defined anywhere!
    #     Should that be `output_experiment1`? Strange that this doesn't raise
    #     an Exception; could be a possible source of issues?!
    scaled_x = relative_x * image1.Scaling.X
    scaled_y = relative_y * image1.Scaling.Y
    scaled_z = relative_z * image1.Scaling.Z
    
    # Convert from center-of-image FOR to the stage's FOR
    new_pos_x = Zen.Devices.Stage.ActualPositionX + scaled_x
    new_pos_y = Zen.Devices.Stage.ActualPositionY + scaled_y
    new_pos_z = Zen.Devices.Focus.ActualPosition  + scaled_z
    
    
    ### Update position and run main scan

    # Reuse settings
    # JH: Proposing to rename experiment2 into mainscan_exp
    experiment2 = ZenExperiment()
    experiment2.LoadFromImage(Zen.Application.LoadImage(job_czi))
    experiment2.SetActive()
    
    # Move the stage
    #experiment2.ModifyTileRegionsWithXYZOffset(0, scaled_x, scaled_y, scaled_z)
    #experiment1.ModifyTileRegionsWithXYZOffset(0, scaled_x, scaled_y, scaled_z)
    Zen.Devices.Stage.MoveTo(new_pos_x, new_pos_y)
    Zen.Devices.Focus.MoveTo(new_pos_z)
    
    # JH: What does this do?
    Zen.Acquisition.Experiments.ActiveExperiment.Save()

    #AutoSave        
    experiment2.AutoSave.Name = 'job_%d.czi' % i
    experiment2.Save()  # JH: Also here, unclear what this does.

    # Acquire
    # JH: Proposing to rename `output_experiment2` into `mainscan_img`
    output_experiment2 = Zen.Acquisition.Execute(experiment2) 

    ## Save image
    #output_experiment2.Name = 'job_%d.czi' % i  # Output file name
    #output_experiment2.Save(os.path.join(output_folder, 'job_%d.czi' % i))
    #print("Saved: timepoint %d" % i)     
    
    print("Completed: timepoint %d" % i)     
    

    ### Interval timing

    while (time_after > DateTime.Now):
        sleep(0.1)



