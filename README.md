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

**[DEV-NOTE:]** The '-e' means the installation is updated "live" as changes are 
made to the source code (either directly or through e.g. `git pull`). However,
when changes are made in `pyproject.toml` (e.g. if a new dependency is added)
the pip installation needs to be updated with `pip install -Ue ".[dev]"`!


## [DEV-NOTE:] Git/GitHub dev workflow

- "I want to work on some aspect or new feature of MATE."
- Get your main branch up to date: `git checkout main`, `git pull`
- Create and check out a new branch: `git checkout -b <feature_name>`
- "Yay, I get to write code now!"
- While working, regularly do the following:
  - `git add <changed/new files>` and `git commit -m "<message>"` every substantive change/addition that stands on its own to create regular "progress checkpoints"; don't wait to commit until the entire feature is done.
  - After having made one or more commits, `git push` them to GitHub so they are backed up and visible for collaborators (the first time pushing on a new branch, `git push --set-upstream origin <feature_branch_name>` is needed).
  - Regularly (e.g. before each commit) run the code formatters (`isort <folder/file with code>` and `black <folder/file with code>`) to have your code automatically formatted to the standard style. In the future, this may be handled automatically through pre-commit hooks, but this doesn't work yet lol (at least not on my machine...).
  - Regularly (e.g. before each commit) run pytest (`pytest` while in top-level repo directory) to check if your changes break anything. In the future (once refactoring is complete), writing new features will also need to go hand in hand with writing new tests for them.
- Once the feature is done, ensure all your changes are committed
- Get your feature branch up to date with any changes that have happened on the main branch: `git checkout main`, `git pull`, `git checkout <feature_branch_name>`, `git merge main` (+if there are merge conflicts, resolve them and commit the result)
- Ensure that `isort`, `black`, and `pytest` have been run, and that everything is clean and ready to go
- `git push` the final product
- On GitHub, create a pull request and then wait for Jonas to check it and - if everything's good - to merge it into main
- Once the merge is complete, you can delete the feature branch locally with `git branch -d <feature_branch_name>` and on GitHub with `git push -d origin <feature_branch_name>`
- "I feel a profound sense of pride and accomplishment!"












