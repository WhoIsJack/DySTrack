# MATE - Microscope Automation for Tracking Experiments

Automated feedback microscopy tool to track moving tissues. WIP.


## LEGACY: Notes copied over from the old implementation ("prim tracker 880" aka "pt880")

### Purpose

The [Zeiss LSM 880 with AiryScan](https://www.zeiss.com/microscopy/int/products/confocal-microscopes/lsm-880-with-airyscan-.html) allows confocal imaging of unprecedented quality and speed. However, a migrating tissue like the zebrafish lateral line primordium will move out of a single field of view relatively quickly, making prolonged live imaging difficult. This project provides an "automated feedback microscopy" (aka "smart microscopy") solution to this problem, implementing an "online tracking" system so the microscope automatically tracks and follows the moving tissue, effectively producing a registered time course.


### Implementation Overview

The smart microscopy system roughly follows the steps in this pseudo-code:

```python
for timepoint in timepoints:
    for embryo in multiposition_embryos:
        1) Acquire a low-resolution fast pre-scan in normal LSM mode
        2) External image analysis masks prim & finds new coordinates
        3) Microscope moves to new coordinates
        4) Acquire a high-resolution stack in Airy FAST mode
```

The microscope itself is controlled through the *ZEISS ZEN BLACK* software, which is used to set up all the imaging parameters for both the low-res pre-scan and the high-res Airy imaging. An example stack of each is saved so the scheduler can load the appropriate parameters during acquisition.

Scheduling and interaction with the image analysis is handled by [*MyPiC*](https://git.embl.de/politi/mypic), a VBA-based pipeline constructor macro created by Antonio Politi (Ellenberg group, EMBL Heidelberg). It is within this macro that the user specifies the number and length of timepoints and the sequence of events, i.e. the acquisition of a low-res pre-scan followed by the wait for new instructions from the image analysis pipeline and finally the acquisition of the high-res stack. Furthermore, the user can mark multiple "starting points" (i.e. multiple embryos) to be tracked at the same time.

The image analysis part is handled by the python scripts in this repo. Essentially, python monitors a given directory for pre-scan files produced by the scope. As soon as it discovers one, it launches an image analysis pipeline that uses object-count thresholding to mask the primordium, then calculates and returns new coordinates for the scope based on the position of the prim's tip (note: the new coords are chosen such that 1/5th of the image in front of the prim will be empty to allow for movement before the next pre-scan is acquired). The new coordinates are then written to the registry, where they are detected by MyPiC which in turn triggers stage movement, acquisition of the high-res stack, and then continuation to the next embryo/timepoint.

The python program handling this consists of the following scripts/modules:

- `pt880_start.py`
    - Run via a command-line interface to start the monitoring session.
    - Monitors the target directory and coordinates the other steps.
- `pt880_analyze.py`
    - Masks prims in pre-scan images by object-count thresholding.
    - Calculates new coordinates based on the mask's tip.
- `pt880_scope.py`
    - Writes the new coordinates and instructions to proceed to the registry.
    - This triggers the continuation of the process in MyPiC.


### Practical Note

- Make sure the embryos are **not too young** and **nicely mounted**!

- Best **restart ZEN** or even the computer when arriving at running/standby system!

- The **objective** is very important to get good quality!
    - Make sure you are using the **40X 1.2 W objective!** (does *not* auto-reload!)
    - Make sure the objective is configured for the **coverslip thickness!** (0.16-0.19; **0.175**)

- Don't forget to *switch off* the **piezo** thingy!

- Use the **center mode** for setting up the z-stack!

- On-line airyScan decon is not an option but batch mode can be run afterwards (click "run batch" and select imgs).