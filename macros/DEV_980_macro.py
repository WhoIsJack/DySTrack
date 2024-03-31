### Prep

# Imports
from __future__ import division, print_function
import sys, os
import clr
from System.Diagnostics import Process
from System.IO import Directory, Path, File
from System import DateTime
from time import sleep, time

### Add script folder - maybe not needed

prescan_fpath = r'D:\Zimeng\_settings\MATE_prescan.czexp' #.czexp file
prescan_czi =   r'D:\Zimeng\_settings\MATE_prescan.czi'

job_fpath = r'D:\Zimeng\_settings\MATE_job_488.czexp' #.czexp file
output_folder = r'D:\Zimeng\20240328_MATE_test_2'

### Remove all open images

Zen.Application.Documents.RemoveAll()

### Start experiment

max_iterations = 20 #number of loops
interval = 300000 # interval in milliseconds

lines_read = 0

for i in range(max_iterations):
    #timing
    time_before = DateTime.Now
    time_after = time_before.AddMilliseconds(interval)

    Zen.Application.Documents.RemoveAll()

    # Reuse settings
    experiment1 = Zen.Acquisition.Experiments.GetByFileName(prescan_fpath)

    #acquire
    outputexperiment1 = Zen.Acquisition.Execute(experiment1) 
    
    #save prescan image
    outputexperiment1.Name = 'prescan_%d.czi'%i 
    outputexperiment1 = Zen.Application.Save(outputexperiment1, Path.Combine(output_folder, outputexperiment1.Name), False) 

##Read external coords
    
    coords_fpath = Path.Combine(output_folder, 'mate_coords.txt')
    
    while not os.path.isfile(coords_fpath):
        print("Waiting for mate_coords.txt to be generated...")
        sleep(1)
    
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
        

###Calculate new position in microns from center of image
    image1 = Zen.Application.LoadImage(prescan_czi, False)

    relative_x = x_pos - (image1.Bounds.SizeX/2)
    relative_y = y_pos - (image1.Bounds.SizeY/2)
    relative_z = z_pos - image1.Bounds.SizeZ

    scaled_x = relative_x * image1.Scaling.X
    scaled_y = relative_y * image1.Scaling.Y
    scaled_z = relative_z * image1.Scaling.Z
    
    new_pos_x = Zen.Devices.Stage.ActualPositionX + scaled_x
    new_pos_y = Zen.Devices.Stage.ActualPositionY + scaled_y
    new_pos_z = Zen.Devices.Focus.ActualPosition - scaled_z
    

# Reuse settings and move to new position
    experiment2 = Zen.Acquisition.Experiments.GetByFileName(job_fpath)
    experiment2.ModifyTileRegionsWithXYZOffset(0, new_pos_x, new_pos_y,new_pos_z)
    Zen.Acquisition.Experiments.ActiveExperiment.Save()

#acquire
    outputexperiment2 = Zen.Acquisition.Execute(experiment2) 

# Save job image
    outputexperiment2.Name = 'job_%d.czi'%i #save with different name
    saved2 = Zen.Application.Save(outputexperiment2, Path.Combine(output_folder, outputexperiment2.Name), False) 
    print("Saved:")

#timing
    while (time_after > DateTime.Now):
        sleep(0.1)