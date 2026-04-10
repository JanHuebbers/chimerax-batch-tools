# chimerax-batch-tools
A collection of ChimeraX .cxs scripts together with Python and PowerShell utilities for automating batch visualization and analysis workflows in ChimeraX.
## Table of contents
- [Overview](#overview)
- [Features](#features)
- [Repository layout](#repository-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Notes](#notes)
- [Status](#status)
## Overview

## Features

## Repository layout

## Requirements
-[CliX](https://github.com/hanjinliu/Chimerax-clix)



## Usage
`.cxc` scripts can be run in several ways:
- Open the file directly in an active ChimeraX session
- Drag and drop the `.cxc` file into an open ChimeraX session
- Copy and paste the script contents into the ChimeraX console and press `Enter`
- Run `run_cxc_on_cxs_1.3.py` from a terminal; the runner must be located in the same directory as the target `.cxs` files, and ChimeraX must be available on `PATH`

### Create a template from CHARMM-GUI output
CHARMM-GUI-derived membrane protein builds can be used to generate template structures that help maintain a consistent orientation across the same protein, its isoforms, or structurally related models when using ChimeraX commands such as `align` or `matchmaker`.

To create such a template, open the corresponding `.gro` file in ChimeraX, then save it as a session file in the `Input` folder. Because opening `.gro` files may take some time, it is recommended to wait until the structure has fully loaded before saving the session. Before running the template script, set the `Input` folder as the working directory either through **File → Set Working Folder** or with the ChimeraX `cd` command.

Template scripts such as `template_create_for_charmm_gui_membrane_protein_builds.cxc` usually require manual adjustment before execution, for example to match the number of subunits or chain IDs in the input structure and to define the desired output file names.

## Notes

## Status
This repository is under construction.