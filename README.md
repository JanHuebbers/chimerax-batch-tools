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

To create such a template, copy the corresponding `.pdb` file to the `./templates` folder, then change to that directory:
```bash
cd .\templates\
```
Run:
```bash
python curate_template_pdb.py HvMlodIDR_trimer_1710_00_step5.pdb HvMlodIDR_trimer_1710_00_step5_template.pdb
```
This removes water and ions from the structure and assigns proper chain IDs to the protein subunits.

### Set up AF3-derived structures with or without a template file
To set up AF3-derived structures for analysis and visualization in ChimeraX, save a `.cxs` file containing all AF3 models from a single run (for example, five models) in the `./input` folder.

In `setup_w_template.cxc`, specify the desired template structure and adjust the template structure model ID as needed. The default template model ID is `6`, assuming that the session contains five AF3 models. The script then superposes the AF3 models onto the template structure either with the `matchmaker` command or by using `align` to fit selected residues in the AF3 models to the corresponding residues in the template. The latter requires manual adjustment of the selected residues, but it can provide a more precise alignment when all subunits should be considered rather than only one chain.

Run from the `Setup` directory:
```bash
cd .\Setup\
python .\run_cxc_on_cxs_1.3.py ..\Input\0084_02*.cxs ..\cxc_scripts\Setup_EXO70_wCHARMM.cxc
```

## Notes

## Status
This repository is under construction.