# -*- coding: utf-8 -*-
"""
Created on Tue Feb 6 17:59:38 2024

@authors:   Zimeng Wu @ Wong group (UCL)
            Jonas Hartmann @ Gilmour group (EMBL) & Mayor lab (UCL)

@descript:  TODO!
            
@usage:     TODO!
"""

### Prep

### Imports

from __future__ import division, print_function
import sys, os
from System.IO import Path
from System import DateTime
from time import sleep

### User input

# Prescan paths
prescan_buffer = "LSM512" #for ZEN3.6 and below
prescan_name = "PRESCAN_4888"  #.czexp from menu

# Job path
job_name = "MATE_JOB_cldnb_cxcr4" #.czexp from menu

# Output path
output_folder = r'D:\Zimeng\20240530_MATE'

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

    # Prep

    # Timing
    time_before = DateTime.Now
    time_after = time_before.AddMilliseconds(interval)

    
    # Clear open images
    Zen.Application.Documents.RemoveAll()

    experiment1 = ZenExperiment()
    experiment1.Load(prescan_name)
    experiment1.SetActive()

    tile_positions = experiment1.GetSinglePositionInfos(0)

    for position in tile_positions[1:]:

        # Prescan
        experiment2 = ZenExperiment()
        experiment2.Load(prescan_buffer)
        experiment2.Load(prescan_name)
        experiment2.SetActive()

        x_pos = experiment2.GetSinglePositionInfos(0)[position].X
        y_pos = experiment2.GetSinglePositionInfos(0)[position].Y
        z_pos = experiment2.GetSinglePositionInfos(0)[position].Z

        experiment2.ModifyTileRegionsWithXYZOffset(0, x_pos, y_pos, z_pos)[0]

        # AutoSave
        experiment2.AutoSave.IsActivated = True
        experiment2.AutoSave.StorageFolder = output_folder
        experiment2.AutoSave.Name = f'prescan_pos_{position}_{i:04d}'
        experiment2.Save()
        output_experiment2 = Zen.Acquisition.Execute(experiment2)
    

        # Save prescimage size
        prescan_x = output_experiment2.Bounds.SizeX
        prescan_y = output_experiment2.Bounds.SizeY
        prescan_z = output_experiment2.Bounds.SizeZ
    
        scaling_x = output_experiment2.Scaling.X
        scaling_y = output_experiment2.Scaling.Y
        scaling_z = output_experiment2.Scaling.Z
    

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
        scaled_x = relative_x * scaling_x
        scaled_y = relative_y * scaling_y
        scaled_z = relative_z * scaling_z
    
    
        # Convert from center-of-image FOR to the stage's FOR
        new_pos_x = Zen.Devices.Stage.ActualPositionX + scaled_x
        new_pos_y = Zen.Devices.Stage.ActualPositionY + scaled_y
        new_pos_z = Zen.Devices.Focus.ActualPosition  - scaled_z

        ### Update position and run main scan
    
        experiment2.ModifyTileRegionsWithXYZOffset(0, scaled_x, scaled_y, -scaled_z)[position] #negative z for inverted
        experiment2.Save()
    
        # Reuse settings and move stage
        experiment3 = ZenExperiment()
        experiment3.Load(job_name)
        experiment3.SetActive()
    
        experiment3.ModifyTileRegionsWithXYZOffset(0, scaled_x, scaled_y, -scaled_z) #negative z for inverted


        #AutoSave
        experiment3.AutoSave.IsActivated = True
        experiment3.AutoSave.StorageFolder = output_folder
        experiment3.AutoSave.Name = f'job_pos_{position}_{i:04d}'
        experiment3.Save()

        # Acquire
        output_experiment3 = Zen.Acquisition.Execute(experiment3) 

        print(f'Saved: position {position}, timepoint {i:04d} ')     

    ### Interval timing

    while (time_after > DateTime.Now):
        sleep(0.1)
