# DySTrack - Dynamic Sample Tracker

**DySTrack ("diss track")** is a simple, modular, python-based, open-source 
**automated feedback microscopy tool** for live tracking of moving samples like 
migratory cells or tissues during acquisition. It works with common commercial
microscope control software through a minimal interface.

Please see [the Documentation](LINK!) for more information!

_**Warning:**_ Modern microscopes are expensive machines, and automating them 
comes with an inherent risk of damage. Appropriate care must be taken when
installing, testing, and using DySTrack. The code and documentation are 
provided "as is", without warranty or liability of any kind (see LICENSE).

![DySTrack lateral line primordium animation](docs/source/images/landing_page/pllp_movie.gif)

```
# TODO: Add link to documentation once it is live
```


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

```
# TODO: 
#  - Remove the dev specs
#  - Swap local install for pip install (for users)
#  - Refer to documentation for more installation instructions
```

For users:

```pip install -e .```


For developers:

```pip install -e ".[dev]"```


To update:

```pip install -Ue ".[dev]"```


## Citing DySTrack

```
# TODO: Add link and complete reference once preprint has been posted
```

If you are using DySTrack in your research, please cite [the preprint](LINK!):

```Wu, Zimeng, ..., and Hartmann, Jonas; [citation forthcoming]```


## Acknowledgements

The earliest prototype of DySTrack was created by Jonas Hartmann in the group
of Darren Gilmour at EMBL Heidelberg, with support by the Advanced Light 
Microscopy Facility (ALMF) and especially Christian Tischer, Antonio Politi, 
and Aliaksandr Halavatyi, and with Elisa Gallo and Mie Wong providing user
feedback.

The prototype was then modernized and further developed by Zimeng Wu and Jonas 
Hartmann at UCL, in the groups of Mie Wong and Roberto Mayor, respectively, 
with support by the Centre for Cell & Molecular Dynamics (CCMD), especially 
Virginia Silio, Mike Redd, and Alan Greig. Nicolas Sergent (Zeiss) supported 
development for ZEN Black and Robert Tetley (Nikon) for NIS Elements. The chick 
node tracking experiments were developed with Octavian Voiculescu in the lab of 
Alessandro Mongera.
