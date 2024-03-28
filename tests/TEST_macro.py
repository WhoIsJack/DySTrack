### Prep

# Imports
from __future__ import division, print_function
import sys, os
import clr
from System.Diagnostics import Process
from System.IO import Directory, Path, File
from time import sleep, time

### Add script folder - maybe not needed

#coords_fpath = r'D:\Zimeng\20240327_MATE_test\mate_coords.txt' 
prescan_fpath = r'D:\Zimeng\_settings\MATE_prescan.czi'
job_fpath = r'D:\Zimeng\_settings\MATE_job_488.czi'
output_folder = r'D:\Zimeng\20240327_MATE_test'

### Remove all open images

Zen.Application.Documents.RemoveAll()

### Start experiment

max_iterations = 2 #How many times it loops?
interval = 100000 #in milliseconds
lines_read = 0

for i in range(max_iterations):
    #timing
    time_before = System.DateTime.Now
    time_after = time_before.AddMilliseconds(interval)

    Zen.Application.Documents.RemoveAll()

    # Load image
    image1 = Zen.Application.LoadImage(prescan_fpath, False) #add stack
    Zen.Application.Documents.Add(image1)

    # Reuse settings
    experiment1 = Zen.Acquisition.Experiments.GetByFileName(prescan_fpath) #needs to be .czexp?
    #hardwareSetting = ZenHardwareSetting()

    #acquire
    outputexperiment1 = Zen.Acquisition.Execute(experiment1) 
    
    #save prescan image
    outputexperiment1.Name = 'prescan_%d.czi'%i #save with different name
    outputexperiment1 = Zen.Application.Save(outputexperiment1, Path.Combine(output_folder, outputexperiment1.Name), False) 
    
    sleep(10) #10 second timer to wait for image analysis

##Read external coords
    
    coords_fpath = Path.Combine(output_folder, 'mate_coords.txt')

    with open(coords_fpath, 'r') as infile:
        lines = infile.readlines()

        if len(lines) > lines_read:
            newest_line = lines[-1]
            values = newest_line.split()

            x_pos = float(values[2])
            y_pos = float(values[1])
            z_pos = float(values[0])

            lines_read = len(lines)
    #with open(coords_fpath,'r') as infile: #put where the python script spits out coordinates
        #newest_line = infile.readlines()[-1]
    
    #values = newest_line.split()

    #x_pos = float(values[2])
    #y_pos = float(values[1])
    #z_pos = float(values[0])

###Calculate new position in microns from center of image
    relative_x = x_pos - (image1.Bounds.SizeX/2)
    relative_y = y_pos - (image1.Bounds.SizeY/2)
    relative_z = 

    scaled_x = relative_x * image1.Scaling.X
    scaled_y = relative_y * image1.Scaling.Y
    scaled_z = z_pos * image1.Scaling.Z
    
    new_pos_x = Zen.Devices.Stage.ActualPositionX + scaled_x
    new_pos_y = Zen.Devices.Stage.ActualPositionY + scaled_y
    new_pos_z = Zen.Devices.Focus.ActualPosition + scaled_z

    print(Zen.Devices.Focus.ActualPosition)
    print(new_pos_z)

###move to new position
    Zen.Devices.Stage.MoveTo(new_pos_x, new_pos_y)
    #Zen.Devices.Focus.MoveTo(new_pos_z)
    Zen.Acquisition.Experiments.ActiveExperiment.Save()

# Load image
    image2 = Zen.Application.LoadImage(job_fpath, False)
    Zen.Application.Documents.Add(image2)

# Reuse settings
    hardwareSetting = ZenHardwareSetting()

#acquire
    experiment2 = Zen.Acquisition.Experiments.ActiveExperiment
    outputexperiment2 = Zen.Acquisition.Execute(experiment2) 

# Save job image
    outputexperiment2.Name = 'job_%d.czi'%i #save with different name
    saved2 = Zen.Application.Save(outputexperiment2, Path.Combine(output_folder, outputexperiment2.Name), False) 
    print("Saved:", saved2)

#timing
    while (time_after > System.DateTime.Now):
        sleep(0.1)