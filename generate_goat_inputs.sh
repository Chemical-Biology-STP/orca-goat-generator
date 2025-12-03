#!/bin/bash

# Interactive ORCA GOAT Input Generator for Cyclic Peptides
# Generates .inp files and corresponding sbatch scripts for GOAT workflows

set -e

# Color codes for better readability
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to prompt user with default value
prompt_with_default() {
    local prompt="$1"
    local default="$2"
    local var_name="$3"
    
    read -p "$(echo -e ${BLUE}${prompt}${NC} [default: ${GREEN}${default}${NC}]: )" input
    eval $var_name=\"\${input:-\$default}\"
}

# Function to prompt yes/no
prompt_yes_no() {
    local prompt="$1"
    local default="$2"
    
    while true; do
        read -p "$(echo -e ${BLUE}${prompt}${NC} [y/n, default: ${GREEN}${default}${NC}]: )" yn
        yn=${yn:-$default}
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes (y) or no (n).";;
        esac
    done
}

# Function to select GOAT variant
select_goat_variant() {
    echo ""
    print_info "Select GOAT variant:"
    echo "  1) GOAT           - Find global minimum and conformational ensemble"
    echo "  2) GOAT-ENTROPY   - Maximize conformational entropy (most complete ensemble)"
    echo "  3) GOAT-EXPLORE   - Topology-free search (can break bonds)"
    echo "  4) GOAT-DIVERSITY - Maximize structural diversity (ignore energies)"
    echo ""
    
    while true; do
        read -p "$(echo -e ${BLUE}Enter choice [1-4]:${NC} )" choice
        case $choice in
            1) GOAT_TYPE="GOAT"; break;;
            2) GOAT_TYPE="GOAT-ENTROPY"; break;;
            3) GOAT_TYPE="GOAT-EXPLORE"; break;;
            4) GOAT_TYPE="GOAT-DIVERSITY"; break;;
            *) print_error "Invalid choice. Please enter 1-4.";;
        esac
    done
}

# Function to generate GOAT input file
generate_inp_file() {
    local xyz_file="$1"
    local base_name=$(basename "$xyz_file" .xyz)
    local output_dir="$2"
    local inp_file="${output_dir}/${base_name}_${GOAT_TYPE_LOWER}.inp"
    
    print_info "Generating input file: $inp_file"
    
    cat > "$inp_file" << EOF
# ORCA ${GOAT_TYPE} Input File for ${base_name}
# Generated for cyclic peptide conformational search
# Objective: Generate structurally diverse conformations without breaking topology
# Configured for ${NPROCS} CPU cores

! ${GOAT_TYPE} ${METHOD} ${SOLVENT_KEYWORD} ${EXTRA_KEYWORDS}

%pal
  nprocs ${NPROCS}
end

%goat
  NWORKERS ${NWORKERS}             # Number of parallel workers
  MAXCORESOPT ${MAXCORESOPT}       # Max cores per optimization
  MAXITER ${MAXITER}               # Maximum global iterations
  MINGLOBALITER ${MINGLOBALITER}   # Minimum global iterations
  MAXEN ${MAXEN}                   # Maximum relative energy (kcal/mol)
  KEEPWORKERDATA ${KEEPWORKERDATA} # Keep worker output files
  CONFTEMP ${CONFTEMP}             # Temperature for Boltzmann populations (K)
EOF

    # Add GOAT-ENTROPY specific parameters
    if [ "$GOAT_TYPE" == "GOAT-ENTROPY" ]; then
        cat >> "$inp_file" << EOF
  MAXENTROPY true                  # Use delta Gconf as convergence criteria
  MINDELS ${MINDELS}               # Minimum entropy difference (cal/mol/K)
  CONFDEGEN ${CONFDEGEN}           # Rotamer degeneracy handling
EOF
    fi
    
    # Add GOAT-EXPLORE specific parameters
    if [ "$GOAT_TYPE" == "GOAT-EXPLORE" ]; then
        cat >> "$inp_file" << EOF
  FREEZEBONDS ${FREEZEBONDS}       # Freeze bonds during uphill step
  FREEZEANGLES ${FREEZEANGLES}     # Freeze sp2 angles and dihedrals
EOF
    fi
    
    # Add cyclic peptide specific constraints
    if [ "$FREEZE_AMIDES" == "true" ]; then
        cat >> "$inp_file" << EOF
  FREEZEAMIDES true                # Preserve amide bond chirality (cis/trans)
EOF
    fi
    
    if [ "$FREEZE_CISTRANS" == "true" ]; then
        cat >> "$inp_file" << EOF
  FREEZECISTRANS true              # Preserve double bond stereochemistry
EOF
    fi
    
    # Add optional GFN uphill method
    if [ "$USE_GFNUPHILL" == "true" ]; then
        cat >> "$inp_file" << EOF
  GFNUPHILL ${GFNUPHILL_METHOD}    # Use faster method for uphill steps
EOF
    fi
    
    cat >> "$inp_file" << EOF
end

%geom
  MaxIter ${GEOM_MAXITER}
  TolE ${GEOM_TOLE}
  TolRMSG ${GEOM_TOLRMSG}
  TolMaxG ${GEOM_TOLMAXG}
end

* xyzfile ${CHARGE} ${MULT} ${xyz_file}

EOF

    print_success "Created: $inp_file"
}

# Function to generate sbatch script
generate_sbatch_script() {
    local xyz_file="$1"
    local base_name=$(basename "$xyz_file" .xyz)
    local output_dir="$2"
    local inp_file="${base_name}_${GOAT_TYPE_LOWER}.inp"
    local sbatch_file="${output_dir}/run_${base_name}_${GOAT_TYPE_LOWER}.sh"
    
    print_info "Generating sbatch script: $sbatch_file"
    
    cat > "$sbatch_file" << EOF
#!/bin/bash
#SBATCH --job-name=${base_name}_${GOAT_TYPE_LOWER}
#SBATCH --nodes=${NODES}
#SBATCH --ntasks=${NPROCS}
#SBATCH --time=${WALLTIME}
#SBATCH --mem=${MEMORY}
#SBATCH --output=slurm-%j.out
EOF

    # Add partition if specified
    if [ -n "$PARTITION" ]; then
        cat >> "$sbatch_file" << EOF
#SBATCH --partition=${PARTITION}
EOF
    fi
    
    cat >> "$sbatch_file" << EOF

# Load ORCA module
module purge
module load ${MODULE_LOAD}

# Set environment variables
export RSH_COMMAND="${RSH_COMMAND}"

# Print job information
echo "========================================="
echo "Job started at: \$(date)"
echo "Job ID: \$SLURM_JOB_ID"
echo "Node: \$SLURM_NODELIST"
echo "Working directory: \$PWD"
echo "========================================="
echo ""

# Run ORCA
${ORCA_PATH} ${inp_file} > ${base_name}_${GOAT_TYPE_LOWER}.out

# Print completion information
echo ""
echo "========================================="
echo "Job completed at: \$(date)"
echo "========================================="

EOF

    chmod +x "$sbatch_file"
    print_success "Created: $sbatch_file"
}

# Main script
echo ""
echo "========================================="
echo "  ORCA GOAT Input Generator"
echo "  For Cyclic Peptide Conformational Search"
echo "========================================="
echo ""

# Check if xyzs directory exists
if [ ! -d "xyzs" ]; then
    print_error "xyzs directory not found!"
    exit 1
fi

# List available XYZ files
print_info "Available XYZ files in xyzs/:"
xyz_files=(xyzs/*.xyz)
for i in "${!xyz_files[@]}"; do
    echo "  $((i+1))) $(basename ${xyz_files[$i]})"
done
echo ""

# Select XYZ files
print_info "Select XYZ files to process:"
echo "  Enter numbers separated by spaces (e.g., '1 2 3')"
echo "  Or enter 'all' to process all files"
read -p "$(echo -e ${BLUE}Selection:${NC} )" selection

if [ "$selection" == "all" ]; then
    selected_files=("${xyz_files[@]}")
else
    selected_files=()
    for idx in $selection; do
        if [ $idx -ge 1 ] && [ $idx -le ${#xyz_files[@]} ]; then
            selected_files+=("${xyz_files[$((idx-1))]}")
        else
            print_warning "Invalid index: $idx (skipped)"
        fi
    done
fi

if [ ${#selected_files[@]} -eq 0 ]; then
    print_error "No valid files selected!"
    exit 1
fi

print_success "Selected ${#selected_files[@]} file(s)"
echo ""

# Select GOAT variant
select_goat_variant
GOAT_TYPE_LOWER=$(echo "$GOAT_TYPE" | tr '[:upper:]' '[:lower:]' | tr '-' '_')
print_success "Selected: $GOAT_TYPE"
echo ""

# Computational method settings
print_info "=== Computational Method Settings ==="
prompt_with_default "Computational method (e.g., XTB2, R2SCAN-3C, PBE)" "XTB2" METHOD

# Solvent settings
echo ""
print_info "=== Solvent Settings ==="
if prompt_yes_no "Use implicit solvation (CPCM)?" "n"; then
    USE_SOLVENT="true"
    echo ""
    echo "  Common solvents:"
    echo "    Water, Acetone, Acetonitrile, Ammonia, Benzene, CCl4,"
    echo "    CH2Cl2, CHCl3, Cyclohexane, DMF, DMSO, Ethanol, Ether,"
    echo "    Hexane, Methanol, Octanol, Pyridine, THF, Toluene"
    echo ""
    prompt_with_default "Solvent name" "Water" SOLVENT_NAME
    SOLVENT_KEYWORD="CPCM(${SOLVENT_NAME})"
else
    USE_SOLVENT="false"
    SOLVENT_KEYWORD=""
fi

# Optimization level settings
echo ""
print_info "=== Optimization Level ==="
echo "  Optimization levels:"
echo "    SLOPPYOPT  - Loose convergence (fastest, for diversity scans)"
echo "    NORMALOPT  - Standard convergence (recommended, default)"
echo "    TIGHTOPT   - Tight convergence (slower, for accurate energies)"
echo ""
prompt_with_default "Optimization level" "NORMALOPT" OPT_LEVEL

# Additional keywords
echo ""
prompt_with_default "Additional keywords (optional, e.g., GRID5, DEFGRID3)" "" ADDITIONAL_KEYWORDS

# Combine all keywords
if [ -n "$ADDITIONAL_KEYWORDS" ]; then
    EXTRA_KEYWORDS="${OPT_LEVEL} ${ADDITIONAL_KEYWORDS}"
else
    EXTRA_KEYWORDS="${OPT_LEVEL}"
fi

# Parallelization settings
echo ""
print_info "=== Parallelization Settings ==="
prompt_with_default "Total number of processors" "200" NPROCS
prompt_with_default "Number of workers" "25" NWORKERS
prompt_with_default "Max cores per optimization" "32" MAXCORESOPT

# GOAT algorithm parameters
echo ""
print_info "=== GOAT Algorithm Parameters ==="
prompt_with_default "Maximum global iterations" "256" MAXITER
prompt_with_default "Minimum global iterations" "5" MINGLOBALITER
prompt_with_default "Maximum relative energy (kcal/mol)" "12.0" MAXEN
prompt_with_default "Conformational temperature (K)" "298.15" CONFTEMP

if prompt_yes_no "Keep worker output files?" "n"; then
    KEEPWORKERDATA="true"
else
    KEEPWORKERDATA="false"
fi

# GOAT-ENTROPY specific parameters
if [ "$GOAT_TYPE" == "GOAT-ENTROPY" ]; then
    echo ""
    print_info "=== GOAT-ENTROPY Specific Parameters ==="
    prompt_with_default "Minimum entropy difference (cal/mol/K)" "0.1" MINDELS
    prompt_with_default "Conformer degeneracy (AUTO, AUTOMAX, or number)" "AUTO" CONFDEGEN
fi

# GOAT-EXPLORE specific parameters
if [ "$GOAT_TYPE" == "GOAT-EXPLORE" ]; then
    echo ""
    print_info "=== GOAT-EXPLORE Specific Parameters ==="
    if prompt_yes_no "Freeze bonds during uphill step?" "y"; then
        FREEZEBONDS="true"
    else
        FREEZEBONDS="false"
    fi
    if prompt_yes_no "Freeze angles during uphill step?" "y"; then
        FREEZEANGLES="true"
    else
        FREEZEANGLES="false"
    fi
fi

# Cyclic peptide specific constraints
echo ""
print_info "=== Cyclic Peptide Specific Constraints ==="
if prompt_yes_no "Freeze amide bond chirality (cis/trans)?" "y"; then
    FREEZE_AMIDES="true"
else
    FREEZE_AMIDES="false"
fi

if prompt_yes_no "Freeze double bond stereochemistry?" "y"; then
    FREEZE_CISTRANS="true"
else
    FREEZE_CISTRANS="false"
fi

# GFN uphill method
echo ""
print_info "=== Uphill Step Optimization ==="
if prompt_yes_no "Use faster GFN method for uphill steps?" "n"; then
    USE_GFNUPHILL="true"
    echo "  Available options: gfnff, gfn2xtb, gfn1xtb, gfn0xtb"
    prompt_with_default "GFN method for uphill" "gfn2xtb" GFNUPHILL_METHOD
else
    USE_GFNUPHILL="false"
fi

# Geometry optimization parameters
echo ""
print_info "=== Geometry Optimization Parameters ==="
prompt_with_default "Max geometry iterations" "500" GEOM_MAXITER
prompt_with_default "Energy tolerance" "5e-6" GEOM_TOLE
prompt_with_default "RMS gradient tolerance" "1e-4" GEOM_TOLRMSG
prompt_with_default "Max gradient tolerance" "3e-4" GEOM_TOLMAXG

# Molecular properties
echo ""
print_info "=== Molecular Properties ==="
prompt_with_default "Charge" "0" CHARGE
prompt_with_default "Multiplicity" "1" MULT

# SLURM/sbatch settings
echo ""
print_info "=== SLURM Job Settings ==="
prompt_with_default "Number of nodes" "1" NODES
prompt_with_default "Wall time (e.g., 72:00:00)" "96:00:00" WALLTIME
prompt_with_default "Memory (e.g., 400G)" "400G" MEMORY
prompt_with_default "Partition (leave empty if not needed)" "" PARTITION
prompt_with_default "Module load command" "OpenMPI/4.1.6-GCC-13.2.0 ORCA/6.1.0" MODULE_LOAD
prompt_with_default "ORCA executable path" "/path/to/orca" ORCA_PATH
prompt_with_default "RSH command" "sh" RSH_COMMAND

# Output directory
echo ""
prompt_with_default "Output directory for generated files" "goat_inputs" OUTPUT_DIR

# Create output directory
mkdir -p "$OUTPUT_DIR"
print_success "Created output directory: $OUTPUT_DIR"
echo ""

# Generate files
print_info "=== Generating Files ==="
for xyz_file in "${selected_files[@]}"; do
    echo ""
    print_info "Processing: $(basename $xyz_file)"
    generate_inp_file "$xyz_file" "$OUTPUT_DIR"
    generate_sbatch_script "$xyz_file" "$OUTPUT_DIR"
done

# Generate submission helper script
SUBMIT_SCRIPT="${OUTPUT_DIR}/submit_all_jobs.sh"
cat > "$SUBMIT_SCRIPT" << 'SUBMIT_EOF'
#!/bin/bash

# Batch submission script for all GOAT jobs
# Generated automatically by generate_goat_inputs.sh

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
            job_id=$(echo "$output" | grep -oP 'Submitted batch job \K\d+')
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
echo "  squeue -u \$USER"
echo "  squeue -j $(IFS=,; echo "${job_ids[*]}")"
echo ""
echo "To cancel all jobs:"
echo "  scancel $(IFS=' '; echo "${job_ids[*]}")"
echo ""

SUBMIT_EOF
chmod +x "$SUBMIT_SCRIPT"

# Summary
echo ""
echo "========================================="
print_success "Generation Complete!"
echo "========================================="
echo ""
print_info "Summary:"
echo "  GOAT variant: $GOAT_TYPE"
echo "  Method: $METHOD"
echo "  Files processed: ${#selected_files[@]}"
echo "  Output directory: $OUTPUT_DIR"
echo ""
print_success "Created submission helper script: $SUBMIT_SCRIPT"
echo ""
print_info "=== How to Submit Jobs ==="
echo ""
echo "Option 1: Submit all jobs at once (RECOMMENDED)"
echo "  cd $OUTPUT_DIR"
echo "  ./submit_all_jobs.sh"
echo ""
echo "Option 2: Submit individual jobs"
echo "  cd $OUTPUT_DIR"
echo "  sbatch run_<basename>_${GOAT_TYPE_LOWER}.sh"
echo ""
echo "Option 3: Submit all jobs with a one-liner"
echo "  cd $OUTPUT_DIR && for script in run_*.sh; do sbatch \$script; done"
echo ""
print_info "=== Monitor Jobs ==="
echo "  squeue -u \$USER                    # View all your jobs"
echo "  squeue -u \$USER --start            # View estimated start times"
echo "  tail -f slurm-<jobid>.out          # Watch job output in real-time"
echo ""
print_warning "Remember to:"
echo "  1. Verify the ORCA path in the sbatch scripts"
echo "  2. Check module names match your cluster"
echo "  3. Adjust memory/time limits as needed"
echo "  4. Copy XYZ files to the output directory or adjust paths"
echo ""
