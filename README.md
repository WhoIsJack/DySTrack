# DySTrack - Dynamic Sample Tracker

**DySTrack ("diss track")** is a simple, modular, python-based, open-source 
**automated feedback microscopy tool** for live tracking of moving samples like 
migratory cells or tissues during acquisition. It works with common commercial
microscope control software through a minimal interface.

Please see [the Documentation](https://whoisjack.github.io/DySTrack/) for more information!

_**Warning:**_ Modern microscopes are expensive machines, and automating them 
comes with an inherent risk of damage. Appropriate care must be taken when
installing, testing, and using DySTrack. The code and documentation are 
provided "as is", without warranty or liability of any kind (see LICENSE).

![DySTrack lateral line primordium animation](docs/source/images/landing_page/pllp_movie.gif)


## Quick start

It is strongly advised that first-time users consult 
[the Documentation](https://whoisjack.github.io/DySTrack/) before installing 
and using DySTrack. These Quick Start instructions are intended solely for 
experienced users.

Install from cloned GitHub repo (recommended):

```batch
git clone https://github.com/WhoIsJack/DySTrack.git
cd DySTrack
conda create -n dystrack python=3.13
conda activate dystrack
pip install -e ".[full]"
pytest
```

Install from PyPI:

```batch
conda create -n dystrack python=3.13
conda activate dystrack
pip install "dystrack[full]"
pytest
```

Start a DySTrack manager session:

```batch
conda activate dystrack
python <path-to-config-file.py> <path-to-target-dir> [optional arguments]
```


## Overview of repo structure

* `run\`: Config files
    - Specify the image analysis pipeline (and optionally other parameters) for a DySTrack run
    - Run a DySTrack session: ```python path\to\config_file.py path\to\target_dir [optional args]```

- `src\dystrack\manager\`: Core module
    - Implements "DySTrack manager" sessions and a command line app to launch them
    - A manager session scans for new (prescan) images produced by the microscope
    - Upon detection of a new target image, an image analysis pipeline is triggered
    - The pipeline returns new coordinates, which are then forwarded to the microscope

* `src\dystrack\pipelines\`: Image analysis pipelines
    - Called by the DyStrack manager when a new target image is detected
    - A pipeline reads a target image and returns new coordinates for acquisition
    - Adapting DySTrack to new use cases is mainly a matter of developing new pipelines

- `macros\`: Interfacing with the microscope
    - Macros are run within commercial microscope software
    - They control all of the microscope's actual operations
    - They interface with DySTrack only by saving image files and reading new coordinates

* `tests\`: Automated testing with pytest
    - Run `pytest` to execute the complete test suite

- `docs\`: DySTrack documentation
    - Run `make html` to build a local version of the docs

* `notebooks\`: Some potentially useful Jupyter notebooks


## Asking for help or contributing to DySTrack

We welcome Issues and Pull Requests that:

- Report or fix a bug or other problem
- Ask a question not answered in [the Documentation](https://whoisjack.github.io/DySTrack/)
- Fix or improve something in the documentation
- (Aim to) add a new image analysis pipeline
- (Aim to) add support for an unsupported microscope
- Suggest or make (backwards-compatible) improvements to features or performance

When raising an Issue or PR, please give it a clear title and description, and 
include as much relevant information as possible.

For PRs, please follow the conventions in the existing code base as closely as
possible, use `black` and `isort` for code formatting and numpy-style doc 
strings, and include/update unit tests and the documentation as necessary. 

That said, if you are unsure how to do these things, please raise an Issue or 
PR anyway and just ask for support! If we find the time, we are happy to help;
after all, most of us are scientists (not professional software developers),
and we are all always still learning!

*Disclaimer:* We currently cannot guarantee any level of support whatsoever and
retain full discretion to close Issues or reject Pull Requests for any reason.
Nevertheless, we do aspire to be helpful and responsive to the extent our 
limited resources permit.

All interactions must abide by the [Contributor Covenenat Code of Conduct](CODE_OF_CONDUCT.md).


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
development for ZEN Blue and Robert Tetley (Nikon) for NIS Elements. The chick 
node tracking experiments were developed with Octavian Voiculescu in the lab of 
Alessandro Mongera.


## Citing DySTrack

If you are using DySTrack in your research, please cite [the preprint](LINK!):

```Wu, Zimeng, ..., and Hartmann, Jonas; [citation forthcoming]```

```
# TODO: Add link and complete BibTeX reference once preprint has been posted
```