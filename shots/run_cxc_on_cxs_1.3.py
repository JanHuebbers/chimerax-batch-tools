#!/usr/bin/env python3
# run_cxc_on_cxs.py — Open .cxs, run .cxc, save new .cxs (output next to this script).
#
# Minimal changes vs your original:
# - Accept wildcards for input_cxs (PowerShell does not expand globs).
# - If wildcard matches multiple .cxs, run ChimeraX once per input file.
# - Fix missing variable script_dir (used by --debug).

import argparse, re, subprocess, sys, tempfile, shutil, os, glob
from pathlib import Path

# ChimeraX executable default (Windows)
CHIMERAX_EXE = r"C:\Program Files\ChimeraX 1.10.1\bin\ChimeraX-console.exe"

def sanitize(name: str) -> str:
    """Keep output stem tidy."""
    return re.sub(r'[^0-9A-Za-z_-]+', '', name)

def build_cxc(input_cxs: Path, user_cxc: Path, out_cxs: Path, log_path: Path | None) -> str:
    """
    Build a tiny ChimeraX runner script that:
      1) cd's into the directory of the user .cxc (so relative paths inside it work),
      2) opens the input .cxs session,
      3) executes the user .cxc via 'runscript',
      4) saves the resulting session to out_cxs,
      5) optionally saves the ChimeraX log,
      6) exits.
    """
    i = input_cxs.as_posix()
    s = user_cxc.as_posix()
    o = out_cxs.as_posix()
    workdir = Path.cwd().resolve().as_posix()

    lines = [
        f'cd "{workdir}"',      # <— NOW images go to the shell's current wd (e.g. .\Setup\)
        f'open "{i}"',
        f'runscript "{s}"',
        f'save "{o}"',
    ]

    if log_path:
        lines.append(f'log save "{log_path.as_posix()}"')
    lines.append('exit')
    return "\n".join(lines) + "\n"

def extract_run_job(stem: str) -> str | None:
    """
    From an input stem like:
      0011_03_1710_0ions_3hvmlo
      0015_20_0ions3hvmlo
      0062_03_1706_0ions_3hvmlo_MLOsetup_MLOalign
    return "0011_03", "0015_20", "0062_03", etc.
    """
    m = re.match(r'^(\d{4})_(\d{2,3})(?:_|$)', stem)
    if m:
        return f"{m.group(1)}_{m.group(2)}"
    return None

def choose_executable(user_arg: str | None) -> list[str]:
    """
    Find a ChimeraX executable.
    Hardcoded default for your Windows install, with optional override via --chimerax.
    """
    if user_arg:
        p = Path(str(user_arg))
        if p.exists():
            return [str(p)]
        return []

    p = Path(CHIMERAX_EXE)
    if p.exists():
        return [str(p)]

    return []


def build_cmd_base(exe_path: str) -> list[str]:
    """
    Construct the executable + stable flags:
      - Windows: DO NOT add --offscreen (causes OpenGL context None on some systems).
                 Only add --nogui if we ended up with the GUI build.
      - Linux/macOS: --offscreen is generally safe and avoids window creation.
                     Add --nogui for GUI builds to suppress UI.
    """
    base = [exe_path]
    name = os.path.basename(exe_path).lower()
    is_windows = (os.name == "nt")

    if is_windows:
        if "console" in name:
            # ChimeraX-console.exe: already headless enough
            return base
        else:
            # ChimeraX.exe (GUI): avoid offscreen, just request no GUI
            return base + ["--nogui"]
    else:
        # Non-Windows: offscreen is reliable
        if "console" in name or "chimerax-console" in name:
            return base + ["--offscreen"]
        else:
            return base + ["--nogui", "--offscreen"]

def main():
    ap = argparse.ArgumentParser(description="Run a ChimeraX .cxc on a .cxs and save output .cxs.")
    ap.add_argument("input_cxs", type=Path)
    ap.add_argument("script_cxc", type=Path)
    ap.add_argument("--chimerax", type=Path, help="Path to ChimeraX(-console) executable")
    ap.add_argument("--log", action="store_true", help="Also write a ChimeraX log next to the output .cxs")
    ap.add_argument("--debug", action="store_true", help="Keep the generated runner .cxc next to this script")
    args = ap.parse_args()

    # FIX: script_dir was referenced but never defined in your original
    script_dir = Path(__file__).resolve().parent

    # Resolve the script path normally (no wildcard expected here in your use-case)
    script_cxc = args.script_cxc.resolve()
    if not script_cxc.is_file():
        sys.exit(f"[ERR] Script file not found: {script_cxc}")

    # MINIMAL CHANGE: expand wildcards for input_cxs ourselves (PowerShell won't)
    raw_input = str(args.input_cxs)
    if any(ch in raw_input for ch in "*?[]"):
        matches = sorted(glob.glob(raw_input))
        input_list = [Path(m).resolve() for m in matches]
    else:
        input_list = [args.input_cxs.resolve()]

    if not input_list:
        sys.exit(f"[ERR] Input session not found: {args.input_cxs}")

    # Locate ChimeraX
    exe = choose_executable(str(args.chimerax) if args.chimerax else None)
    if not exe:
        sys.exit('[ERR] Could not find ChimeraX. Pass --chimerax "C:\\Program Files\\ChimeraX\\bin\\ChimeraX-console.exe"')

    # OS-aware base flags to avoid OpenGL context issues on Windows
    cmd_base = build_cmd_base(exe[0])

    # On Windows, suppress extra console window popups for the launched process
    creationflags = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW

    # Run once per input file
    for input_cxs in input_list:
        if not input_cxs.is_file():
            print(f"[WARN] Skipping (not a file): {input_cxs}")
            continue

        # Outputs live in the CURRENT working directory (where you run the script)
        out_dir = Path.cwd().resolve()
        in_stem = input_cxs.stem
        run_job = extract_run_job(in_stem) or in_stem
        script_stem = sanitize(script_cxc.stem)
        out_name = f"{run_job}_{script_stem}.cxs"

        out_cxs = out_dir / out_name
        log_path = (out_dir / (out_cxs.stem + "_chimerax.log")) if args.log else None

        # Build the tiny runner script content
        runner_text = build_cxc(input_cxs, script_cxc, out_cxs, log_path)

        # Write the runner script to a temp file unless --debug is set
        if args.debug:
            runner_path = script_dir / "runner_debug.cxc"
            runner_path.write_text(runner_text, encoding="utf-8")
            td = None
        else:
            td = tempfile.TemporaryDirectory()
            runner_path = Path(td.name) / "runner.cxc"
            runner_path.write_text(runner_text, encoding="utf-8")

        # Use --script runner.cxc everywhere (more stable than long --cmd chains on Windows)
        full_cmd = cmd_base + ["--script", str(runner_path)]

        print("[INFO] Input  :", input_cxs)
        print("[INFO] Running:", " ".join(full_cmd))
        try:
            subprocess.run(full_cmd, check=True, creationflags=creationflags)
        except subprocess.CalledProcessError as e:
            print(f"[ERR] ChimeraX failed (exit code {e.returncode}).{' See log: '+str(log_path) if log_path else ''}")
            # continue to next input instead of killing the whole batch
            continue
        finally:
            if td is not None:
                td.cleanup()

        if out_cxs.exists():
            print(f"[OK] Saved: {out_cxs}")
            if log_path:
                print(f"[LOG] Wrote: {log_path}")
        else:
            print(f"[ERR] Output not created.{(' Check log: '+str(log_path)) if log_path else ''}")

if __name__ == "__main__":
    main()
