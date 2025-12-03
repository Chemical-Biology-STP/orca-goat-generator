#!/usr/bin/env python3

"""
Interactive ORCA GOAT Input Generator for Cyclic Peptides
Generates .inp files and corresponding sbatch scripts for GOAT workflows
"""

import os
import sys
from pathlib import Path
from typing import List, Optional


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def print_info(message: str) -> None:
    """Print info message in blue"""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def print_success(message: str) -> None:
    """Print success message in green"""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def print_warning(message: str) -> None:
    """Print warning message in yellow"""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def print_error(message: str) -> None:
    """Print error message in red"""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")


def prompt_with_default(prompt: str, default: str) -> str:
    """Prompt user with a default value"""
    user_input = input(f"{Colors.BLUE}{prompt}{Colors.NC} [default: {Colors.GREEN}{default}{Colors.NC}]: ").strip()
    return user_input if user_input else default


def prompt_yes_no(prompt: str, default: str = "n") -> bool:
    """Prompt user for yes/no answer"""
    while True:
        response = input(f"{Colors.BLUE}{prompt}{Colors.NC} [y/n, default: {Colors.GREEN}{default}{Colors.NC}]: ").strip().lower()
        response = response if response else default
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please answer yes (y) or no (n).")


def select_goat_variant() -> str:
    """Select GOAT variant from menu"""
    print()
    print_info("Select GOAT variant:")
    print("  1) GOAT           - Find global minimum and conformational ensemble")
    print("  2) GOAT-ENTROPY   - Maximize conformational entropy (most complete ensemble)")
    print("  3) GOAT-EXPLORE   - Topology-free search (can break bonds)")
    print("  4) GOAT-DIVERSITY - Maximize structural diversity (ignore energies)")
    print()
    
    variants = {
        '1': 'GOAT',
        '2': 'GOAT-ENTROPY',
        '3': 'GOAT-EXPLORE',
        '4': 'GOAT-DIVERSITY'
    }
    
    while True:
        choice = input(f"{Colors.BLUE}Enter choice [1-4]:{Colors.NC} ").strip()
        if choice in variants:
            return variants[choice]
        else:
            print_error("Invalid choice. Please enter 1-4.")


def generate_inp_file(xyz_file: Path, output_dir: Path, config: dict) -> None:
    """Generate ORCA GOAT input file"""
    base_name = xyz_file.stem
    goat_type_lower = config['GOAT_TYPE'].lower().replace('-', '_')
    inp_file = output_dir / f"{base_name}_{goat_type_lower}.inp"
    
    print_info(f"Generating input file: {inp_file}")
    
    with open(inp_file, 'w') as f:
        f.write(f"# ORCA {config['GOAT_TYPE']} Input File for {base_name}\n")
        f.write("# Generated for cyclic peptide conformational search\n")
        f.write("# Objective: Generate structurally diverse conformations without breaking topology\n")
        f.write(f"# Configured for {config['NPROCS']} CPU cores\n\n")
        
        f.write(f"! {config['GOAT_TYPE']} {config['METHOD']} {config['SOLVENT_KEYWORD']} {config['EXTRA_KEYWORDS']}\n\n")
        
        f.write("%pal\n")
        f.write(f"  nprocs {config['NPROCS']}\n")
        f.write("end\n\n")
        
        f.write("%goat\n")
        f.write(f"  NWORKERS {config['NWORKERS']}             # Number of parallel workers\n")
        f.write(f"  MAXCORESOPT {config['MAXCORESOPT']}       # Max cores per optimization\n")
        f.write(f"  MAXITER {config['MAXITER']}               # Maximum global iterations\n")
        f.write(f"  MINGLOBALITER {config['MINGLOBALITER']}   # Minimum global iterations\n")
        f.write(f"  MAXEN {config['MAXEN']}                   # Maximum relative energy (kcal/mol)\n")
        f.write(f"  KEEPWORKERDATA {config['KEEPWORKERDATA']} # Keep worker output files\n")
        f.write(f"  CONFTEMP {config['CONFTEMP']}             # Temperature for Boltzmann populations (K)\n")
        
        # Add GOAT-ENTROPY specific parameters
        if config['GOAT_TYPE'] == 'GOAT-ENTROPY':
            f.write("  MAXENTROPY true                  # Use delta Gconf as convergence criteria\n")
            f.write(f"  MINDELS {config['MINDELS']}               # Minimum entropy difference (cal/mol/K)\n")
            f.write(f"  CONFDEGEN {config['CONFDEGEN']}           # Rotamer degeneracy handling\n")
        
        # Add GOAT-EXPLORE specific parameters
        if config['GOAT_TYPE'] == 'GOAT-EXPLORE':
            f.write(f"  FREEZEBONDS {config['FREEZEBONDS']}       # Freeze bonds during uphill step\n")
            f.write(f"  FREEZEANGLES {config['FREEZEANGLES']}     # Freeze sp2 angles and dihedrals\n")
        
        # Add cyclic peptide specific constraints
        if config.get('FREEZE_AMIDES') == 'true':
            f.write("  FREEZEAMIDES true                # Preserve amide bond chirality (cis/trans)\n")
        
        if config.get('FREEZE_CISTRANS') == 'true':
            f.write("  FREEZECISTRANS true              # Preserve double bond stereochemistry\n")
        
        # Add optional GFN uphill method
        if config.get('USE_GFNUPHILL') == 'true':
            f.write(f"  GFNUPHILL {config['GFNUPHILL_METHOD']}    # Use faster method for uphill steps\n")
        
        f.write("end\n\n")
        
        f.write("%geom\n")
        f.write(f"  MaxIter {config['GEOM_MAXITER']}\n")
        f.write(f"  TolE {config['GEOM_TOLE']}\n")
        f.write(f"  TolRMSG {config['GEOM_TOLRMSG']}\n")
        f.write(f"  TolMaxG {config['GEOM_TOLMAXG']}\n")
        f.write("end\n\n")
        
        f.write(f"* xyzfile {config['CHARGE']} {config['MULT']} {xyz_file}\n\n")
    
    print_success(f"Created: {inp_file}")


def generate_sbatch_script(xyz_file: Path, output_dir: Path, config: dict) -> None:
    """Generate sbatch submission script"""
    base_name = xyz_file.stem
    goat_type_lower = config['GOAT_TYPE'].lower().replace('-', '_')
    inp_file = f"{base_name}_{goat_type_lower}.inp"
    sbatch_file = output_dir / f"run_{base_name}_{goat_type_lower}.sh"
    
    print_info(f"Generating sbatch script: {sbatch_file}")
    
    with open(sbatch_file, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write(f"#SBATCH --job-name={base_name}_{goat_type_lower}\n")
        f.write(f"#SBATCH --nodes={config['NODES']}\n")
        f.write(f"#SBATCH --ntasks={config['NPROCS']}\n")
        f.write(f"#SBATCH --time={config['WALLTIME']}\n")
        f.write(f"#SBATCH --mem={config['MEMORY']}\n")
        f.write("#SBATCH --output=slurm-%j.out\n")
        
        # Add partition if specified
        if config.get('PARTITION'):
            f.write(f"#SBATCH --partition={config['PARTITION']}\n")
        
        f.write("\n# Load ORCA module\n")
        f.write("module purge\n")
        f.write(f"module load {config['MODULE_LOAD']}\n\n")
        
        f.write("# Set environment variables\n")
        f.write(f'export RSH_COMMAND="{config["RSH_COMMAND"]}"\n\n')
        
        f.write("# Print job information\n")
        f.write('echo "========================================="\n')
        f.write('echo "Job started at: $(date)"\n')
        f.write('echo "Job ID: $SLURM_JOB_ID"\n')
        f.write('echo "Node: $SLURM_NODELIST"\n')
        f.write('echo "Working directory: $PWD"\n')
        f.write('echo "========================================="\n')
        f.write('echo ""\n\n')
        
        f.write("# Run ORCA\n")
        f.write(f"{config['ORCA_PATH']} {inp_file} > {base_name}_{goat_type_lower}.out\n\n")
        
        f.write("# Print completion information\n")
        f.write('echo ""\n')
        f.write('echo "========================================="\n')
        f.write('echo "Job completed at: $(date)"\n')
        f.write('echo "========================================="\n\n')
    
    # Make script executable
    os.chmod(sbatch_file, 0o755)
    print_success(f"Created: {sbatch_file}")


def generate_submit_all_script(output_dir: Path, goat_type_lower: str) -> None:
    """Generate helper script to submit all jobs"""
    submit_script = output_dir / "submit_all_jobs.sh"
    
    with open(submit_script, 'w') as f:
        f.write("""#!/bin/bash

# Batch submission script for all GOAT jobs
# Generated automatically by generate_goat_inputs.py

echo "========================================="
echo "  Submitting All GOAT Jobs"
echo "========================================="
echo ""

# Find all sbatch scripts
sbatch_scripts=(run_*.sh)

if [ ${#sbatch_scripts[@]} -eq 0 ]; then
    echo "ERROR: No sbatch scripts found!"
    exit 1
fi

echo "Found ${#sbatch_scripts[@]} job(s) to submit:"
echo ""

# Submit each job
job_ids=()
for script in "${sbatch_scripts[@]}"; do
    if [ -f "$script" ] && [ -x "$script" ]; then
        echo "Submitting: $script"
        output=$(sbatch "$script" 2>&1)
        if [ $? -eq 0 ]; then
            job_id=$(echo "$output" | grep -oP 'Submitted batch job \\K\\d+')
            job_ids+=("$job_id")
            echo "  ✓ Job ID: $job_id"
        else
            echo "  ✗ Failed: $output"
        fi
    else
        echo "Skipping: $script (not executable or not found)"
    fi
    echo ""
done

echo "========================================="
echo "  Submission Summary"
echo "========================================="
echo ""
echo "Total jobs submitted: ${#job_ids[@]}"
echo "Job IDs: ${job_ids[@]}"
echo ""
echo "To monitor jobs:"
echo "  squeue -u $USER"
echo "  squeue -j $(IFS=,; echo "${job_ids[*]}")"
echo ""
echo "To cancel all jobs:"
echo "  scancel $(IFS=' '; echo "${job_ids[*]}")"
echo ""
""")
    
    os.chmod(submit_script, 0o755)
    return submit_script


def main():
    """Main script execution"""
    print()
    print("=========================================")
    print("  ORCA GOAT Input Generator")
    print("  For Cyclic Peptide Conformational Search")
    print("=========================================")
    print()
    
    # Check if xyzs directory exists
    xyzs_dir = Path("xyzs")
    if not xyzs_dir.exists():
        print_error("xyzs directory not found!")
        sys.exit(1)
    
    # List available XYZ files
    xyz_files = sorted(xyzs_dir.glob("*.xyz"))
    if not xyz_files:
        print_error("No XYZ files found in xyzs/ directory!")
        sys.exit(1)
    
    print_info("Available XYZ files in xyzs/:")
    for i, xyz_file in enumerate(xyz_files, 1):
        print(f"  {i}) {xyz_file.name}")
    print()
    
    # Select XYZ files
    print_info("Select XYZ files to process:")
    print("  Enter numbers separated by spaces (e.g., '1 2 3')")
    print("  Or enter 'all' to process all files")
    selection = input(f"{Colors.BLUE}Selection:{Colors.NC} ").strip()
    
    if selection.lower() == 'all':
        selected_files = xyz_files
    else:
        selected_files = []
        for idx_str in selection.split():
            try:
                idx = int(idx_str)
                if 1 <= idx <= len(xyz_files):
                    selected_files.append(xyz_files[idx - 1])
                else:
                    print_warning(f"Invalid index: {idx} (skipped)")
            except ValueError:
                print_warning(f"Invalid input: {idx_str} (skipped)")
    
    if not selected_files:
        print_error("No valid files selected!")
        sys.exit(1)
    
    print_success(f"Selected {len(selected_files)} file(s)")
    print()
    
    # Configuration dictionary
    config = {}
    
    # Select GOAT variant
    config['GOAT_TYPE'] = select_goat_variant()
    print_success(f"Selected: {config['GOAT_TYPE']}")
    print()
    
    # Computational method settings
    print_info("=== Computational Method Settings ===")
    config['METHOD'] = prompt_with_default("Computational method (e.g., XTB2, R2SCAN-3C, PBE)", "XTB2")
    
    # Solvent settings
    print()
    print_info("=== Solvent Settings ===")
    if prompt_yes_no("Use implicit solvation (CPCM)?", "n"):
        print()
        print("  Common solvents:")
        print("    Water, Acetone, Acetonitrile, Ammonia, Benzene, CCl4,")
        print("    CH2Cl2, CHCl3, Cyclohexane, DMF, DMSO, Ethanol, Ether,")
        print("    Hexane, Methanol, Octanol, Pyridine, THF, Toluene")
        print()
        solvent_name = prompt_with_default("Solvent name", "Water")
        config['SOLVENT_KEYWORD'] = f"CPCM({solvent_name})"
    else:
        config['SOLVENT_KEYWORD'] = ""
    
    # Optimization level settings
    print()
    print_info("=== Optimization Level ===")
    print("  Optimization levels:")
    print("    SLOPPYOPT  - Loose convergence (fastest, for diversity scans)")
    print("    NORMALOPT  - Standard convergence (recommended, default)")
    print("    TIGHTOPT   - Tight convergence (slower, for accurate energies)")
    print()
    opt_level = prompt_with_default("Optimization level", "NORMALOPT")
    
    # Additional keywords
    print()
    additional_keywords = prompt_with_default("Additional keywords (optional, e.g., GRID5, DEFGRID3)", "")
    
    # Combine all keywords
    if additional_keywords:
        config['EXTRA_KEYWORDS'] = f"{opt_level} {additional_keywords}"
    else:
        config['EXTRA_KEYWORDS'] = opt_level
    
    # Parallelization settings
    print()
    print_info("=== Parallelization Settings ===")
    config['NPROCS'] = prompt_with_default("Total number of processors", "200")
    config['NWORKERS'] = prompt_with_default("Number of workers", "25")
    config['MAXCORESOPT'] = prompt_with_default("Max cores per optimization", "32")
    
    # GOAT algorithm parameters
    print()
    print_info("=== GOAT Algorithm Parameters ===")
    config['MAXITER'] = prompt_with_default("Maximum global iterations", "256")
    config['MINGLOBALITER'] = prompt_with_default("Minimum global iterations", "5")
    config['MAXEN'] = prompt_with_default("Maximum relative energy (kcal/mol)", "12.0")
    config['CONFTEMP'] = prompt_with_default("Conformational temperature (K)", "298.15")
    
    config['KEEPWORKERDATA'] = 'true' if prompt_yes_no("Keep worker output files?", "n") else 'false'
    
    # GOAT-ENTROPY specific parameters
    if config['GOAT_TYPE'] == 'GOAT-ENTROPY':
        print()
        print_info("=== GOAT-ENTROPY Specific Parameters ===")
        config['MINDELS'] = prompt_with_default("Minimum entropy difference (cal/mol/K)", "0.1")
        config['CONFDEGEN'] = prompt_with_default("Conformer degeneracy (AUTO, AUTOMAX, or number)", "AUTO")
    
    # GOAT-EXPLORE specific parameters
    if config['GOAT_TYPE'] == 'GOAT-EXPLORE':
        print()
        print_info("=== GOAT-EXPLORE Specific Parameters ===")
        config['FREEZEBONDS'] = 'true' if prompt_yes_no("Freeze bonds during uphill step?", "y") else 'false'
        config['FREEZEANGLES'] = 'true' if prompt_yes_no("Freeze angles during uphill step?", "y") else 'false'
    
    # Cyclic peptide specific constraints
    print()
    print_info("=== Cyclic Peptide Specific Constraints ===")
    config['FREEZE_AMIDES'] = 'true' if prompt_yes_no("Freeze amide bond chirality (cis/trans)?", "y") else 'false'
    config['FREEZE_CISTRANS'] = 'true' if prompt_yes_no("Freeze double bond stereochemistry?", "y") else 'false'
    
    # GFN uphill method
    print()
    print_info("=== Uphill Step Optimization ===")
    if prompt_yes_no("Use faster GFN method for uphill steps?", "n"):
        config['USE_GFNUPHILL'] = 'true'
        print("  Available options: gfnff, gfn2xtb, gfn1xtb, gfn0xtb")
        config['GFNUPHILL_METHOD'] = prompt_with_default("GFN method for uphill", "gfn2xtb")
    else:
        config['USE_GFNUPHILL'] = 'false'
    
    # Geometry optimization parameters
    print()
    print_info("=== Geometry Optimization Parameters ===")
    config['GEOM_MAXITER'] = prompt_with_default("Max geometry iterations", "500")
    config['GEOM_TOLE'] = prompt_with_default("Energy tolerance", "5e-6")
    config['GEOM_TOLRMSG'] = prompt_with_default("RMS gradient tolerance", "1e-4")
    config['GEOM_TOLMAXG'] = prompt_with_default("Max gradient tolerance", "3e-4")
    
    # Molecular properties
    print()
    print_info("=== Molecular Properties ===")
    config['CHARGE'] = prompt_with_default("Charge", "0")
    config['MULT'] = prompt_with_default("Multiplicity", "1")
    
    # SLURM/sbatch settings
    print()
    print_info("=== SLURM Job Settings ===")
    config['NODES'] = prompt_with_default("Number of nodes", "1")
    config['WALLTIME'] = prompt_with_default("Wall time (e.g., 72:00:00)", "96:00:00")
    config['MEMORY'] = prompt_with_default("Memory (e.g., 400G)", "400G")
    config['PARTITION'] = prompt_with_default("Partition (leave empty if not needed)", "")
    config['MODULE_LOAD'] = prompt_with_default("Module load command", "OpenMPI/4.1.6-GCC-13.2.0 ORCA/6.1.0")
    config['ORCA_PATH'] = prompt_with_default("ORCA executable path", "/path/to/orca")
    config['RSH_COMMAND'] = prompt_with_default("RSH command", "sh")
    
    # Output directory
    print()
    output_dir_str = prompt_with_default("Output directory for generated files", "goat_inputs")
    output_dir = Path(output_dir_str)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    print_success(f"Created output directory: {output_dir}")
    print()
    
    # Generate files
    print_info("=== Generating Files ===")
    for xyz_file in selected_files:
        print()
        print_info(f"Processing: {xyz_file.name}")
        generate_inp_file(xyz_file, output_dir, config)
        generate_sbatch_script(xyz_file, output_dir, config)
    
    # Generate submission helper script
    goat_type_lower = config['GOAT_TYPE'].lower().replace('-', '_')
    submit_script = generate_submit_all_script(output_dir, goat_type_lower)
    
    # Summary
    print()
    print("=========================================")
    print_success("Generation Complete!")
    print("=========================================")
    print()
    print_info("Summary:")
    print(f"  GOAT variant: {config['GOAT_TYPE']}")
    print(f"  Method: {config['METHOD']}")
    print(f"  Files processed: {len(selected_files)}")
    print(f"  Output directory: {output_dir}")
    print()
    print_success(f"Created submission helper script: {submit_script}")
    print()
    print_info("=== How to Submit Jobs ===")
    print()
    print("Option 1: Submit all jobs at once (RECOMMENDED)")
    print(f"  cd {output_dir}")
    print("  ./submit_all_jobs.sh")
    print()
    print("Option 2: Submit individual jobs")
    print(f"  cd {output_dir}")
    print(f"  sbatch run_<basename>_{goat_type_lower}.sh")
    print()
    print("Option 3: Submit all jobs with a one-liner")
    print(f"  cd {output_dir} && for script in run_*.sh; do sbatch $script; done")
    print()
    print_info("=== Monitor Jobs ===")
    print("  squeue -u $USER                    # View all your jobs")
    print("  squeue -u $USER --start            # View estimated start times")
    print("  tail -f slurm-<jobid>.out          # Watch job output in real-time")
    print()
    print_warning("Remember to:")
    print("  1. Verify the ORCA path in the sbatch scripts")
    print("  2. Check module names match your cluster")
    print("  3. Adjust memory/time limits as needed")
    print("  4. Copy XYZ files to the output directory or adjust paths")
    print()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        print_warning("Script interrupted by user")
        sys.exit(1)
    except Exception as e:
        print()
        print_error(f"An error occurred: {e}")
        sys.exit(1)
