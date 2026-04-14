# chimerax-batch-tools
A collection of ChimeraX `.cxc` scripts together with Python and PowerShell utilities for automating batch visualization and analysis workflows in ChimeraX.
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
  - [Create a morph between setup and endpoint structures](#create-a-morph-between-setup-and-endpoint-structures)
  - [Take pictures from predefined views](#take-pictures-from-predefined-views)
  - [Create movies from ChimeraX sessions](#create-movies-from-chimerax-sessions)
  - [Batch-run ChimeraX workflows from PowerShell](#batch-run-chimerax-workflows-from-powershell)
- [Notes](#notes)
- [Status](#status)
## Overview
`chimerax-batch-tools` is a repository for automating repetitive ChimeraX visualization and analysis workflows for protein structures derived from AF3 predictions. It combines ChimeraX command scripts with Python and PowerShell utilities to support template generation from CHARMM-GUI membrane protein builds, setup and alignment of AF3-derived structures, and standardized downstream visualization and rendering.

The repository is designed for batch-style processing, where the same ChimeraX workflow is applied to multiple `.cxs` session files or structure-specific script variants. Its main goal is to make figure generation and structural comparison in ChimeraX more reproducible, faster, and easier to reuse across related projects.

## Features
- Python and PowerShell helper scripts for automating recurring ChimeraX workflows
- Template generation from CHARMM-GUI-derived membrane protein builds
- Setup workflows for AF3-derived structures with or without a reference template
- Standardized visualization presets for ChimeraX sessions
    - Surface visualization workflows for prepared protein complexes
    - Electrostatic surface potential mapping using `coulombic`
    - Molecular lipophilicity potential mapping using `mlp`
- Reusable script structure for extending the repository with additional ChimeraX analysis workflows
- Batch execution of ChimeraX `.cxc` scripts on multiple `.cxs` session files
## Repository layout
```text
C:.
├───coulombic
├───cxc_scripts
├───input
├───mlp
├───morph
├───movie
├───setup
├───shots
├───surface
└───templates
```
## Requirements
- ChimeraX 1.10.1 or compatible version
- Python 3.12
- PowerShell for the batch wrapper scripts on Windows
- [CliX](https://github.com/hanjinliu/Chimerax-clix)
- A valid `ChimeraX-console.exe` path configured in `run_cxc_on_cxs_1.3.py` or passed via `--chimerax`
## Installation
Clone the repository and ensure that Python, ChimeraX, and CliX are available. Update the ChimeraX executable path in `run_cxc_on_cxs_1.3.py` if your local installation differs from the default path.
## Usage
`.cxc` scripts can be run in several ways:
- Open the file directly in an active ChimeraX session
- Drag and drop the `.cxc` file into an open ChimeraX session
- Copy and paste the script contents into the ChimeraX console and press `Enter`
- Run `run_cxc_on_cxs_1.3.py` from a terminal; the current working directory determines where output files are written, and the ChimeraX-console path must be correct (default: "C:\Program Files\ChimeraX 1.10.1\bin\ChimeraX-console.exe")
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
To set up AF3-derived structures for analysis and visualization in ChimeraX, save a `.cxs` file containing all AF3 models from a single run (for example, five models) in the `./input` folder. The setup first applies a standardized display setup, including a white background, silhouettes, soft lighting, cartoon rendering, and an orthographic camera view. It then superposes AF3 structures onto a template structure and colors the individual chains inferred from the AF3 predictions.

In `setup_w_template.cxc`, specify the desired template structure and adjust the template structure model ID as needed. The default template model ID is `6`, assuming that the session contains five AF3 models. The script then superposes the AF3 models onto the template structure either with the `matchmaker` command or by using `align` to fit selected residues in the AF3 models to the corresponding residues in the template. The latter requires manual adjustment of the selected residues, but it can provide a more precise alignment when all subunits should be considered rather than only a single chain.

Run from the `setup` directory:
```bash
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
python .\run_cxc_on_cxs_1.3.py ..\setup\0097_01*.cxs ..\cxc_scripts\mlp_HvMlo.cxc
```
### Create a morph between setup and endpoint structures
The `morph.cxc` script is applied to a prepared setup `.cxs` file and generates a structural morph between the starting model and a defined endpoint structure.

The script opens a desired endpoint `<structure>.pdb` (defined in the script), applies styling, and colors chains with separate residue-number gradients. It then aligns the endpoint model to the starting model using selected `Cα` atoms from specified residues. After alignment, the script creates a morph trajectory between the starting and endpoint structures.

Run from the `morph` directory:
```bash
python .\run_cxc_on_cxs_1.3.py ..\setup\0097_01*.cxs ..\cxc_scripts\morph.cxc
```
### Take pictures from predefined views
The `shots.cxc` scripts typically apply a standardized visualization setup, define one or more fixed viewpoints, and save high-resolution `.png` images with transparent backgrounds for figures and presentations.

Because the scripts save images directly from the current session, the exact output depends on the structure, coloring, and display settings already present in the input `.cxs` file.

Example workflow:
```bash
cd .\shots\
python .\run_cxc_on_cxs_1.3.py ..\setup\0097_01*.cxs ..\cxc_scripts\shots.cxc
```
The saved view names, camera orientations, output file names, image size, and rendering options can be adjusted as needed for a given structure or figure layout.
### Create movies from ChimeraX sessions
Movie scripts can be used to generate animated visualizations from prepared ChimeraX session files, for example after surface rendering or morph generation. Here, a typical movie workflow defines one or more saved views, records a sequence of camera movements, optionally plays a morph trajectory, and then encodes the recorded frames as an animated `.png`.

`movie_<description>.cxc` scripts are applied to an existing `.cxs` session and usually carry out the following steps:
- reset and save relevant views
- define the window size and zoom level
- start movie recording
- rotate or move the camera between predefined views
- optionally play a morph trajectory
- encode the recorded frames as an animated `.png`

These animated `.png` files can then be converted to `.gif` format with `apng_to_gif.py` for easier sharing or embedding.

Example workflow from the `movie` directory:
```bash
cd .\movie\
python .\run_cxc_on_cxs_1.3.py ..\morph\0097_01_morph_to_0097_08_02_surface.cxs ..\cxc_scripts\movie_morph_bottom_and_spin.cxc
```

Convert the resulting animated `.png` to `.gif`:
```bash
python .\apng_to_gif.py ".\0097_01_00_to_08_02_morph_bottom_spin.png" -o ".\0097_01_00_to_08_02_morph_bottom_spin.gif"
```
The exact input session, camera path, morph model ID, and output file name can be adjusted depending on the structure and movie to be generated.
### Batch-run ChimeraX workflows from PowerShell
The `run_coulombic_all.ps1` script is a PowerShell batch wrapper for `run_cxc_on_cxs_1.3.py`. It iterates over a predefined set of input `.cxs` files, applies a selected `.cxc` script to each one, and checks whether the expected output session file was created. If no output is found, the script retries the run up to a configurable number of times.
Although the example script is configured for a Coulombic workflow, it can also be adapted for other ChimeraX `.cxc` scripts by changing the `$cxc` path, the directory from which it is run, and, if necessary, the expected output naming convention.
Run the script from the `./coulombic` directory:
```bash
.\run_coulombic_all.ps1
```
## Notes
- Many workflows rely on relative paths. Run commands from the directory specified in each example.
- Output `.cxs`, `.png`, and `.gif` files are typically written to the current working directory.
- The default ChimeraX executable path is hard-coded in `run_cxc_on_cxs_1.3.py` and may need to be updated for a different local installation.
- Some `.cxc` scripts require manual adjustment of model IDs, residue selections, chain IDs, or file names before execution.
- Template generation from CHARMM-GUI output assumes protein subunits can be identified and assigned consistent chain IDs.
- Large generated media and session files are usually better excluded from Git tracking.
## Status
This repository is functional and covers the core ChimeraX batch workflows currently used in the project. Additional scripts, refinements, and workflow-specific extensions may be added over time.
