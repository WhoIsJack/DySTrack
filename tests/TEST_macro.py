### Prep

# Imports
from __future__ import division, print_function
import sys, os
import clr
from System.Diagnostics import Process
from System.IO import Directory, Path, File
import StartExternal as stext
from time import sleep

# Check version and working dir
print(sys.version)
print(os.getcwd())


### Add script folder - maybe not needed

scriptfolder = r'Folder\With\MATE' #input folder
sys.path.append(scriptfolder)


### print known hardware changes 
componentIds = hardwareSetting.GetAllComponentIds()

for componentId in componentIds:
    print(componentId)
    
    parameterNames = hardwareSetting.GetAllParameterNames(componentId)
    
    for parameterName in parameterNames:
        print(parameterName)
        
        parameterValue = hardwareSetting.GetParameter(componentId, parameterName)
        print(parameterValue)

### Remove all open images

Zen.Application.Documents.RemoveAll()

### Start experiment

counter = 0
max_iterations = 10 #How many time it loops?
interval = 600 #in seconds

while counter < max_iterations:

    if Zen.Application.LoadImage():   
        counter = counter+1

    # Load image
    image1 = Zen.Application.LoadImage(r"prescan.czi", False) #add stack
    Zen.Application.Documents.Add(image1)

    # Reuse settings
    hardwareSetting = ZenHardwareSetting()
    hardwareSetting.Load(image1)

    #acquire
    outputexperiment1 = Zen.Acquisition.Execute(experiment1) 
    
    # save prescan
    saved = Zen.Application.Save(outputexperiment1, 'prescan%d'%counter.czi, False) #save with different name
    print("Saved:", saved)

### Append current coordinates to a file

    #output to the same as image folder (timepoint and date time?)
    imgX = ZenService.Analysis.AllParticles.ImageStageXPosition
    imgY = ZenService.Analysis.AllParticles.ImageStageYPosition
    imgZ = ZenService.HardwareActions.ReadFocusPosition()
    ZenService.Xtra.System.AppendLogLine(imgX, imgY, imgZ, str(ZenService.Experiment.CurrentTimePointIndex), ":", "1. " + str(ZenService.Environment.CurrentTimeHour).zfill(2) + ":" + str(ZenService.Environment.CurrentTimeMinute).zfill(2) + ":" + str(ZenService.Environment.CurrentTimeSecond).zfill(2) + " on " + str(ZenService.Environment.CurrentDateYear).zfill(4) + "-" + str(ZenService.Environment.CurrentDateMonth).zfill(2) + "-" + str(ZenService.Environment.CurrentDateDay).zfill(2), "LogFile")

    #ZenService.Xtra.System.AppendLogLine(str(ZenService.Experiment.CurrentTimePointIndex), "LogFile")

    sleep(10) #10 second timer to wait for image analysis

##Read external coords
    with open(r'coords.txt','r') as infile: #put where the python script spits out coordinates
        newest_line = infile.readlines()[-1]

    x_pos = int(newest_line.split('X:')[1].split(', ')[0])
    y_pos = int(newest_line.split('Y:')[1].split(', ')[0])
    z_pos = int(newest_line.split('Z:')[1])

###Calculate new position in microns
    relative_x = x_pos - img.Bounds.X/2
    relative_y = y_pos - img.Bounds.Y/2

    scaled_x = relative_x * image1.Scaling.X
    scaled_y = relative_y * image1.Scaling.Y
    scaled_z = z_pos * image1.Scaling.Z

###move to new position
    Zen.Devices.Stage.MoveTo(Zen.Devices.Stage.ActualPositionX + scaled_x)
    Zen.Devices.Stage.MoveTo(Zen.Devices.Stage.ActualPositionY + scaled_y)
    Zen.Devices.Stage.MoveTo(Zen.Devices.Stage.ActualPositionZ + scaled_z)

# Load image
    image2 = Zen.Application.LoadImage(r"stack.czi", False)
    Zen.Application.Documents.Add(image2)

# Reuse settings
    hardwareSetting = ZenHardwareSetting()
    hardwareSetting.Load(image2)

#acquire
    outputexperiment2 = Zen.Acquisition.Execute(experiment2)

# Save image
    saved2 = Zen.Application.Save(outputexperiment2, 'image%d'%counter.czi, False) #save with different name
    print("Saved:", saved)

sleep(interval)