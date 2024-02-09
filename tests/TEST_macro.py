### Prep

# Imports
from __future__ import division, print_function
import sys, os
import clr
from System.Diagnostics import Process
from System.IO import Directory, Path, File
import StartExternal as stext

# Check version and working dir
print(sys.version)
print(os.getcwd())


### Add script folder

scriptfolder = r'Folder\With\MATE'
sys.path.append(scriptfolder)

### Remove all open images

Zen.Application.Documents.RemoveAll()

### Start experiment

ZenService.Actions.StartExperiment()

counter = 0

if #if what?    
    counter = counter+1

# Load image
#image1 = Zen.Application.Documents.GetByName("test_stack_2.czi") ##Add stack
#if image2 is None:
image1 = Zen.Application.LoadImage(r"S:\DBIO_WongGroup_1\Zimeng\980_vis\20240131_cldnb_stacks\516x180_LSM_50um_xyz.czi", False) #add stack
Zen.Application.Documents.Add(image1)

# Reuse settings
ZenService.HardwareActions.ExecuteHardwareSettingFromFile(image1)


# Save image
if image2 is None:
    saved = Zen.Application.Save(image1, r"D:\Zimeng\test_{counter}.czi", False)
    print("Saved:", saved)
    image2 = image1


### Append things to a file

#output to the same as image folder (timepoint and date time?)
ZenService.Xtra.System.AppendLogLine(str(ZenService.Experiment.CurrentTimePointIndex), ":", "1. " + str(ZenService.Environment.CurrentTimeHour).zfill(2) + ":" + str(ZenService.Environment.CurrentTimeMinute).zfill(2) + ":" + str(ZenService.Environment.CurrentTimeSecond).zfill(2) + " on " + str(ZenService.Environment.CurrentDateYear).zfill(4) + "-" + str(ZenService.Environment.CurrentDateMonth).zfill(2) + "-" + str(ZenService.Environment.CurrentDateDay).zfill(2), "LogFile")

#ZenService.Xtra.System.AppendLogLine(str(ZenService.Experiment.CurrentTimePointIndex), "LogFile")


### Start external script? Don't need maybe...

if (start_Simple_Plot == True):
    
    # this is easy version, where one has define the columns manually inside the data display script
    script2 = r'MyFolder\\simple_plot.py'
    # this one for the easy version --> only the filename is passed as an argument
    params2 = ' -f ' + csvfile
    # start the data display script as an external application using a tool script
    stext.StartApp(script2, params2)

# Load image
image1 = Zen.Application.Documents.GetByName("test_stack_2.czi")
if image2 is None:
    image1 = Zen.Application.LoadImage(r"D:\Jonas\_automation\test_stack.czi", False)
    Zen.Application.Documents.Add(image1)



# Save image
if image2 is None:
    saved = Zen.Application.Save(image1, r"D:\Jonas\_automation\test_stack_2.czi", False)
    print("Saved:", saved)
    image2 = image1
