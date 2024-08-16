# MATE - Microscope Automation for Tracking Experiments

A simple automated feedback microscopy tool for tracking of moving tissues. WIP.


## Structure

- `src/mate/manager/`: Monitors images produced, triggers image analysis pipelines, and sends coordinates to the microscope
- `src/mate/pipelines/`: Image analysis pipelines that start with an previous image and return new imaging coordinates
- `macros/`: Macros running within commercial microscope software to interface with MATE


## Installation

For users:

```pip install -e .```

For developers:

```pip install -e ".[dev]"```

[DEV-NOTE:] The '-e' means the installation is updated "live" as changes are 
made to the source code (either directly or through e.g. `git pull`). However,
when changes are made in `pyproject.toml` (e.g. if a new dependency is added)
the pip installation needs to be updated with `pip install -Ue ".[dev]"`!