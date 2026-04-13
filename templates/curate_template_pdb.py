#!/usr/bin/env python3
"""
Curate a CHARMM-GUI-derived PDB template for ChimeraX.

What this script does:
- removes water and ions
- assigns protein chain IDs A, B, C, ... from TER-separated protein subunits
- assigns membrane residues to chain M
- writes a single cleaned PDB containing both protein and membrane

Usage:
    python curate_template_pdb.py input.pdb output_template.pdb
"""

from __future__ import annotations
import sys
from pathlib import Path

# Standard and common protein residue names
PROTEIN_RESNAMES = {
    "ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
    "LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL",
    "HSD", "HSE", "HSP", "HID", "HIE", "HIP", "CYX", "ASH", "GLH", "LYN",
    "NMA", "ACE",
}

# Common water and ion residue names in CHARMM-GUI / MD outputs
REMOVE_RESNAMES = {
    "TIP", "TIP3", "TIP3P", "SOL", "HOH", "WAT",
    "CLA", "CL", "SOD", "NA", "POT", "K", "CAL", "CA", "MG", "ZN"
}

# Common membrane residue names; extend if needed
MEMBRANE_RESNAMES = {
    "POPC", "POPE", "POPG", "POPS",
    "DOPC", "DOPE", "DOPG", "DOPS",
    "DPPC", "DPPE", "DPPG", "DPPS",
    "DMPC", "DLPC", "DSPC",
    "CHL1", "CHOL", "ERG", "CER", "SAPI",
    "PLPC", "PYPC", "POPI", "POPA", "PPCS",
}

CHAIN_IDS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def parse_resname(line: str) -> str:
    return line[17:20].strip()


def set_chain_id(line: str, chain_id: str) -> str:
    # PDB chain ID is column 22 (0-based index 21)
    return line[:21] + chain_id + line[22:]


def is_atom_record(line: str) -> bool:
    return line.startswith("ATOM") or line.startswith("HETATM")


def classify_residue(resname: str) -> str:
    if resname in REMOVE_RESNAMES:
        return "remove"
    if resname in PROTEIN_RESNAMES:
        return "protein"
    if resname in MEMBRANE_RESNAMES:
        return "membrane"
    return "other"


def curate_pdb(lines: list[str]) -> list[str]:
    output = []
    protein_chain_index = 0
    last_kept_class = None

    for line in lines:
        record = line[:6].strip()

        if is_atom_record(line):
            resname = parse_resname(line)
            residue_class = classify_residue(resname)

            if residue_class == "remove":
                continue

            if residue_class == "protein":
                if protein_chain_index >= len(CHAIN_IDS):
                    raise ValueError("Too many protein subunits for simple A-Z chain assignment.")
                line = set_chain_id(line, CHAIN_IDS[protein_chain_index])

            elif residue_class == "membrane":
                line = set_chain_id(line, "M")

            else:
                # Keep unknown residues but mark them with chain X
                line = set_chain_id(line, "X")

            output.append(line)
            last_kept_class = residue_class
            continue

        if record == "TER":
            # Keep TER only after kept protein atoms, and advance protein chain
            if last_kept_class == "protein":
                output.append(line)
                protein_chain_index += 1
            last_kept_class = None
            continue

        if record in {"END", "ENDMDL"}:
            continue

        # Keep headers/remarks/etc.
        output.append(line)

    output.append("END\n")
    return output


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: python curate_template_pdb.py input.pdb output_template.pdb")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])

    lines = input_path.read_text().splitlines(keepends=True)
    curated = curate_pdb(lines)
    output_path.write_text("".join(curated))

    print(f"Wrote curated template to: {output_path}")


if __name__ == "__main__":
    main()