# -*- coding: utf-8 -*-
"""
Created on Tue Feb 6 17:59:38 2024

@authors:   Zimeng Wu @ Wong group (UCL)
            Jonas Hartmann @ Mayor lab (UCL)

@descript:  ZEN Blue IronPython macro to interface Zeiss LSM980 with MATE.

@usage:     TODO!
"""

import os
import sys
from time import sleep

from System import DateTime
from System.IO import Path

### ---------------------------------------------------------------------------
### USER INPUT
### ---------------------------------------------------------------------------

# Prescan path
prescan_name = "PRESCAN_488"  # .czexp from menu

# Job path
job_name = "MATE_JOB_cldnb"  # .czexp from menu

# Output path
output_folder = r"D:\Zimeng\20250918_test"

# Loop settings
max_iterations = 90  # Number of loops
interval_min = 2  # Interval in minutes

### ---------------------------------------------------------------------------
### END OF USER INPUT
### ---------------------------------------------------------------------------


### Start experiment

# Clear open images
Zen.Application.Documents.RemoveAll()

# Prep
interval = interval_min * 60000
coords_fpath = os.path.join(output_folder, "mate_coords.txt")
with open(coords_fpath, "r") as infile:
    lines_read = len(infile.readlines())

print(lines_read)

# Get positions
Zen.Application.Documents.RemoveAll()

experiment1 = ZenExperiment()
experiment1.Load(prescan_name)
experiment1.SetActive()

tile_positions = experiment1.GetSinglePositionInfos(0)


### Run loop

for i in range(max_iterations):

    # Timing
    time_before = DateTime.Now
    time_after = time_before.AddMilliseconds(interval)

    # Clear open images
    Zen.Application.Documents.RemoveAll()

    for pos_idx, position in enumerate(tile_positions):

        ## Acquire and save prescan

        # Prescan
        experiment2 = ZenExperiment()
        experiment2.Load(prescan_name)
        experiment2.SetActive()

        x_pos = position.X
        y_pos = position.Y
        z_pos = position.Z

        experiment2.ClearTileRegionsAndPositions(0)
        experiment2.AddSinglePosition(0, x_pos, y_pos, z_pos)

        # AutoSave
        experiment2.AutoSave.IsActivated = True
        experiment2.AutoSave.StorageFolder = output_folder
        experiment2.AutoSave.Name = "prescan_%d_pos_%d" % (i, pos_idx)
        output_experiment2 = Zen.Acquisition.Execute(experiment2)

        # Save prescan image size
        prescan_x = output_experiment2.Bounds.SizeX
        prescan_y = output_experiment2.Bounds.SizeY
        prescan_z = output_experiment2.Bounds.SizeZ

        scaling_x = output_experiment2.Scaling.X
        scaling_y = output_experiment2.Scaling.Y
        scaling_z = output_experiment2.Scaling.Z

        ## Read coords provided by MATE

        # Wait for mate_coords.txt to be updated with a new line
        while True:
            with open(coords_fpath, "r") as infile:
                lines = infile.readlines()

            if len(lines) > lines_read:
                newest_line = lines[-1]
                values = newest_line.split()

                x2_pos = float(values[2])
                y2_pos = float(values[1])
                z2_pos = float(values[0])

                lines_read = len(lines)
                break

            sleep(0.1)

        ### Convert new coordinates into the stage's Frame Of Reference (FOR)

        # Convert from corner-of-image FOR to center-of-image FOR
        relative_z = z2_pos - ((prescan_z - 1) / 2.0)

        # Scale from pixels to microns
        scaled_x = x2_pos * scaling_x
        scaled_y = y2_pos * scaling_y
        scaled_z = relative_z * scaling_z

        # Get stage coordinates
        x_coord = output_experiment2.GetPositionLeftTop().X
        y_coord = output_experiment2.GetPositionLeftTop().Y
        z_coord = z_pos

        # Convert from center-of-image FOR to the stage's FOR
        new_pos_x = x_coord + scaled_x
        new_pos_y = y_coord + scaled_y
        new_pos_z = z_coord + scaled_z

        ### Update position and run main scan

        # Update position
        position.X = new_pos_x
        position.Y = new_pos_y
        position.Z = new_pos_z

        # Reuse settings and move stage
        experiment3 = ZenExperiment()
        experiment3.Load(job_name)
        experiment3.SetActive()

        experiment3.ClearTileRegionsAndPositions(0)
        experiment3.AddSinglePosition(0, new_pos_x, new_pos_y, new_pos_z)

        # AutoSave
        experiment3.AutoSave.IsActivated = True
        experiment3.AutoSave.StorageFolder = output_folder
        experiment3.AutoSave.Name = "job_%d_pos_%d" % (i, pos_idx)

        # Acquire
        output_experiment3 = Zen.Acquisition.Execute(experiment3)

        print("Saved: position %s, timepoint %04d" % (pos_idx, i))

    ### Interval timing

    while time_after > DateTime.Now:
        sleep(0.1)
