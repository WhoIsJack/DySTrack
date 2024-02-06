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

### Start external script?

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

# Reuse settings
hardwaresetting1 = ZenHardwareSetting()


# Save image
if image2 is None:
    saved = Zen.Application.Save(image1, r"D:\Jonas\_automation\test_stack_2.czi", False)
    print("Saved:", saved)
    image2 = image1
