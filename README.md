# DySTrack - Dynamic Sample Tracker

A simple automated feedback microscopy tool for live tracking of moving samples like migrating cells or tissues.


## Structure

* `run/`: Config files
    - Config files for users to specify the image analysis pipeline and other parameters

- `src/dystrack/manager/`: Core module
    - Command line application that starts a DysTrack monitoring session
    - The monitoring session scans for new prescan images produced by the microscope
    - Upon detection of a new prescan, an image analysis pipeline is triggered
    - The pipeline returns new coordinates, which are then forwarded to the microscope

* `src/dystrack/pipelines/`: Image analysis pipelines
    - An image analysis pipeline reads a prescan and returns new main scan coordinates

- `macros/`: Interfacing with the microscope
    - Macros are run within commercial microscope software
    - They control all the microscope's operations
    - They interface with DySTrack only by saving prescan files and reading new coordinates


## Installation

For users:

```pip install -e .```


For developers:

```pip install -e ".[dev]"```


To update:

```pip install -Ue ".[dev]"```