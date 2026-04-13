# chimerax-batch-tools
A collection of ChimeraX .cxs scripts together with Python and PowerShell utilities for automating batch visualization and analysis workflows in ChimeraX.
## Table of contents
- [Overview](#overview)
- [Features](#features)
- [Repository layout](#repository-layout)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Create a template from CHARMM-GUI output](#create-a-template-from-charmm-gui-output)
  - [Set up AF3-derived structures with or without a template file](#set-up-af3-derived-structures-with-or-without-a-template-file)
  - [Show the surface of protein complexes](#show-the-surface-of-protein-complexes)
  - [Show the electrostatic potential of protein complexes](#show-the-electrostatic-potential-of-protein-complexes)
  - [Show molecular lipophilicity potential of protein complexes](#show-molecular-lipophilicity-potential-of-protein-complexes)
- [Notes](#notes)
- [Status](#status)
## Overview
`chimerax-batch-tools` is a repository for automating repetitive ChimeraX visualization and analysis workflows on protein structures retrieved from AF3 predicitons. It combines ChimeraX command scripts with Python and PowerShell utilities to support template generation from CHARMM-GUI builds, setup and alignment of AF3-derived structures, and standardized downstream rendering.

The repository is designed for batch-style processing, where the same ChimeraX workflow is applied to multiple `.cxs` session files or structure-specific script variants. Its main goal is to make figure generation and structural comparison in ChimeraX more reproducible, faster, and easier to reuse across related projects.

## Features
- Batch execution of ChimeraX `.cxc` scripts on multiple `.cxs` session files (pending)
- Python and PowerShell helper scripts for automating recurring ChimeraX workflows
- Template generation from CHARMM-GUI-derived membrane protein builds
- Setup workflows for AF3-derived structures with or without a reference template
- Standardized visualization presets for ChimeraX sessions
    - Surface visualization workflows for prepared protein complexes
    - Electrostatic surface potential mapping using `coulombic`
    - Molecular lipophilicity potential mapping using `mlp`
- Reusable script structure for extending the repository with additional ChimeraX analysis workflows

## Repository layout
C:.
├───cxc_scripts
├───input
├───setup
└───templates
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
To set up AF3-derived structures for analysis and visualization in ChimeraX, save a `.cxs` file containing all AF3 models from a single run (for example, five models) in the `./input` folder. The setup first applies a standardized display setup, including a white background, silhouettes, soft lighting, cartoon rendering, and an orthographic camera view. It then superposes AF3 structures onto a template structure and colors the individual chains inferred from AF3 prediction.

In `setup_w_template.cxc`, specify the desired template structure and adjust the template structure model ID as needed. The default template model ID is `6`, assuming that the session contains five AF3 models. The script then superposes the AF3 models onto the template structure either with the `matchmaker` command or by using `align` to fit selected residues in the AF3 models to the corresponding residues in the template. The latter requires manual adjustment of the selected residues, but it can provide a more precise alignment when all subunits should be considered rather than only a single chain.

Run from the `setup` directory:
```bash
cd .\setup\
python .\run_cxc_on_cxs_1.3.py ..\input\0084_02*.cxs ..\cxc_scripts\setup_w_template.cxc
```
Run `setup_wo_template.cxc` if you do not want to use a template structure.

### Show the surface of protein complexes
The `surface.cxc` script prepares ChimeraX models for visualization of the molecular surface. It is intended to be run after a setup script.

The script hides all models except model `#1`, displays the surface of that model, sets the surface transparency, and resets the view for inspection.

Finally, the script clears the selection.

Run from the `surface` directory:
```bash
python .\run_cxc_on_cxs_1.3.py ..\setup\0097_01*.cxs ..\cxc_scripts\surface.cxc
```

### Show the electrostatic potential of protein complexes
The `coulombic.cxc` script prepares ChimeraX models for visualization of the electrostatic surface potential. It is intended to be run after a setup script.

The script hides all models except model `#1`, displays its molecular surface, and sets the surface transparency. All protein subunits are colored white before the electrostatic potential is mapped onto the surface using the `coulombic` command with a custom red-white-teal palette. In addition, chain `A` is shown with partial surface transparency, and its cartoon representation is colored by residue number.

Finally, the script resets the view for inspection and clears the selection.

Run from the `coulombic` directory:
```bash
python .\run_cxc_on_cxs_1.3.py ..\setup\0097_01*.cxs ..\cxc_scripts\coulombic.cxc
```

### Show molecular lipophilicity potential of protein complexes
The `mlp_<structure>.cxc` script prepares AF3-derived models in ChimeraX for visualization of the molecular lipophilicity potential (MLP). It colors chain `A` by structural region, using distinct colors for the transmembrane, extracellular, and intracellular domains, while chains `B` and `C` are colored white.

The script then calculates and displays the molecular lipophilicity potential on the protein surface using the `mlp` command. The surface is shown with a custom color gradient ranging from teal to white to orange, allowing lipophilic and less lipophilic regions to be distinguished visually.

Finally, the script hides atoms, cartoons, and surfaces for models `#2-5`, leaving only the first model visible for inspection.

Run from the `mlp` directory:
```bash
cd .\mlp\
python .\run_cxc_on_cxs_1.3.py ..\setup\0097_01*.cxs ..\cxc_scripts\mlp_HvMlo.cxc
```

## Notes

## Status
This repository is under construction.