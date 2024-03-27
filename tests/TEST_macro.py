### Prep

# Imports
#from __future__ import division, print_function
import sys, os
import clr
from System.Diagnostics import Process
from System.IO import Directory, Path, File
from time import sleep

### Add script folder - maybe not needed

coords_fpath = r'D:\Zimeng\20240327_MATE_test\mate_coords.txt' 
prescan_fpath = r'D:\Zimeng\_settings\MATE_prescan.czi'
job_fpath = r'D:\Zimeng\_settings\MATE_job_488.czi'
output_folder = r'D:\Zimeng\20240327_MATE_test'

### Remove all open images

Zen.Application.Documents.RemoveAll()

### Start experiment

counter = 0
max_iterations = 2 #How many times it loops?
interval = 100 #in seconds


while counter < max_iterations:

    if Zen.Application.Documents.RemoveAll():   
        counter = counter+1

    Zen.Application.Documents.RemoveAll()

    # Load image
    image1 = Zen.Application.LoadImage(prescan_fpath, False) #add stack
    Zen.Application.Documents.Add(image1)

    # Reuse settings
    hardwareSetting = ZenHardwareSetting()

    #acquire
    experiment1 = Zen.Acquisition.Experiments.ActiveExperiment
    outputexperiment1 = Zen.Acquisition.Execute(experiment1) 
    
    #save prescan image
    outputexperiment1.Name = 'prescan_%d.czi'%counter #save with different name
    outputexperiment1 = Zen.Application.Save(outputexperiment1, Path.Combine(output_folder, outputexperiment1.Name), False) 
    
    sleep(10) #10 second timer to wait for image analysis

##Read external coords
    with open(coords_fpath,'r') as infile: #put where the python script spits out coordinates
        newest_line = infile.readlines()[-1]
    
    values = newest_line.split()

    x_pos = float(values[0])
    y_pos = float(values[1])
    z_pos = float(values[2])

###Calculate new position in microns from center of image
    relative_x = x_pos - (image1.Bounds.SizeX/2)
    relative_y = y_pos - (image1.Bounds.SizeY/2)

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

# Load image
    image2 = Zen.Application.LoadImage(job_fpath, False)
    Zen.Application.Documents.Add(image2)

# Reuse settings
    hardwareSetting = ZenHardwareSetting()
        #hardwareSetting.Load(image2)

#acquire
    experiment2 = Zen.Acquisition.Experiments.ActiveExperiment
    outputexperiment2 = Zen.Acquisition.Execute(experiment2) 

# Save job image
    outputexperiment2.Name = 'job_%d.czi'%counter #save with different name
    saved2 = Zen.Application.Save(outputexperiment2, Path.Combine(output_folder, outputexperiment2.Name), False) 
    print("Saved:", saved2)

    sleep(interval)