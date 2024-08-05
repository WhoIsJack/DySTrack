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
