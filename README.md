# ORCA GOAT Generator

> Interactive input generator for ORCA GOAT conformational searches with automatic SLURM batch submission

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![ORCA Version](https://img.shields.io/badge/ORCA-6.0%2B-blue)](https://orcaforum.kofo.mpg.de/)
[![Shell](https://img.shields.io/badge/Shell-Bash-green)](https://www.gnu.org/software/bash/)

Generate production-ready ORCA GOAT input files and SLURM batch scripts for conformational searches of cyclic peptides and other molecules. Perfect for beginners and experienced users alike!

---

## 📋 Table of Contents

- [What is This?](#what-is-this)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Step-by-Step Tutorial](#step-by-step-tutorial)
- [Understanding GOAT Variants](#understanding-goat-variants)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)
- [Citation](#citation)
- [License](#license)

---

## 🤔 What is This?

This tool helps you create input files for **ORCA's GOAT** (Global Optimizer Algorithm for Topology) - a powerful method for finding all possible 3D shapes (conformations) that a molecule can adopt.

**Why use this tool?**
- ✅ No need to manually write complex input files
- ✅ Automatically generates job submission scripts for your HPC cluster
- ✅ Interactive prompts guide you through all options
- ✅ Optimized for cyclic peptides with proper constraints
- ✅ Batch process multiple molecules at once

**Perfect for:**
- Finding the global minimum energy structure
- Generating complete conformational ensembles
- Boltzmann-averaged property calculations
- Exploring structural diversity

---

## ✨ Features

- 🎯 **4 GOAT Variants**: GOAT, GOAT-ENTROPY, GOAT-EXPLORE, GOAT-DIVERSITY
- 🧬 **Cyclic Peptide Optimized**: Preserves topology, amide bonds, stereochemistry
- 💧 **Solvent Support**: Built-in CPCM implicit solvation
- ⚙️ **Optimization Levels**: SLOPPYOPT, NORMALOPT, TIGHTOPT
- 🚀 **Batch Submission**: Automatic helper script for submitting all jobs
- 📊 **Smart Defaults**: Sensible values for all parameters
- 🔄 **Batch Processing**: Handle multiple molecules simultaneously

---

## 📦 Prerequisites

### On Your Computer:
- Basic terminal/command line knowledge
- SSH access to your HPC cluster
- Your molecule structure files in XYZ format

### On Your HPC Cluster:
- ORCA 6.0 or later installed
- SLURM job scheduler
- Bash shell (usually default)

**Don't worry if you're new to HPC!** This guide will walk you through everything step-by-step.

---

## 🔧 Installation

### Step 1: Connect to Your HPC Cluster

Open a terminal on your computer and connect to your cluster:

```bash
ssh your_username@your_cluster.edu
```

Replace `your_username` with your actual username and `your_cluster.edu` with your cluster's address.

### Step 2: Download This Repository

Once connected to the cluster, download the tool:

```bash
# Navigate to your home directory or preferred location
cd ~

# Clone the repository
git clone https://github.com/Chemical-Biology-STP/orca-goat-generator.git

# Enter the directory
cd orca-goat-generator
```

**Don't have git?** Download manually:
```bash
wget https://github.com/Chemical-Biology-STP/orca-goat-generator/archive/main.zip
unzip main.zip
cd orca-goat-generator-main
```

### Step 3: Make the Script Executable

```bash
chmod +x generate_goat_inputs.sh
```

### Step 4: Verify Installation

```bash
ls -lh
```

You should see:
- `generate_goat_inputs.sh` (the main script)
- `xyzs/` (folder for your molecule files)
- `README.md` (this file)

---

## 🚀 Quick Start

### 1. Add Your Molecule Files

Place your XYZ coordinate files in the `xyzs/` folder:

```bash
# Copy your XYZ files to the xyzs folder
cp /path/to/your/molecule.xyz xyzs/
```

**What's an XYZ file?** It's a simple text file containing your molecule's 3D coordinates. Example:
```
20
Molecule name
C  -3.26482  -0.47497   0.33191
C  -2.16518   0.24269   0.35382
H  -4.23539  -0.01923   0.27823
...
```

### 2. Run the Generator

```bash
./generate_goat_inputs.sh
```

### 3. Answer the Prompts

The script will ask you questions. **Just press Enter to use the default values** (shown in green), or type your own value.

Example:
```
Computational method [default: XTB2]: [press Enter]
Use implicit solvation (CPCM)? [y/n, default: n]: y
Solvent name [default: Water]: [press Enter]
```

### 4. Submit Your Jobs

After the script finishes, it creates a folder with all your files:

```bash
cd goat_inputs
./submit_all_jobs.sh
```

That's it! Your jobs are now running on the cluster.

---

## 📚 Step-by-Step Tutorial

### For Complete Beginners

Let's walk through a complete example from start to finish.

#### Scenario: You have a cyclic peptide and want to find all its conformations

**Step 1: Prepare Your Molecule File**

You need an XYZ file of your molecule. You can:
- Export from molecular modeling software (Avogadro, ChemDraw, etc.)
- Use existing files from the `xyzs/` folder as examples
- Ask your supervisor for the file

**Step 2: Upload to the Cluster**

From your computer:
```bash
# Upload your file to the cluster
scp my_peptide.xyz your_username@cluster.edu:~/orca-goat-generator/xyzs/
```

Or use an SFTP client like FileZilla, WinSCP, or Cyberduck.

**Step 3: Connect to the Cluster**

```bash
ssh your_username@cluster.edu
cd ~/orca-goat-generator
```

**Step 4: Run the Generator**

```bash
./generate_goat_inputs.sh
```

**Step 5: Answer the Questions**

Here's what the script will ask and what to answer:

| Question | What to Answer | Why |
|----------|----------------|-----|
| **Select XYZ files** | Type `1` (or the number of your file) | Choose which molecule to process |
| **GOAT variant** | Type `2` (GOAT-ENTROPY) | Best for complete conformational ensemble |
| **Computational method** | Press Enter (XTB2) | Fast and accurate for initial searches |
| **Use solvent?** | Type `y` if in solution, `n` if gas phase | Matches your experimental conditions |
| **Solvent name** | Type `Water` (or your solvent) | Common solvents: Water, DMSO, Methanol |
| **Optimization level** | Press Enter (NORMALOPT) | Standard convergence |
| **Total processors** | Type `200` (or what your cluster allows) | More = faster |
| **Number of workers** | Type `25` | Parallel optimizations |
| **Wall time** | Type `96:00:00` | 4 days (adjust as needed) |
| **Memory** | Type `400G` | Adjust based on molecule size |
| **Module load** | Type your cluster's ORCA module name | Ask your cluster admin if unsure |
| **ORCA path** | Type the path to ORCA executable | Usually `/path/to/orca` or just `orca` |

**For everything else, just press Enter to use defaults!**

**Step 6: Review Generated Files**

```bash
cd goat_inputs
ls
```

You'll see:
- `my_peptide_goat_entropy.inp` - ORCA input file
- `run_my_peptide_goat_entropy.sh` - Job submission script
- `submit_all_jobs.sh` - Helper to submit all jobs

**Step 7: Submit the Job**

```bash
./submit_all_jobs.sh
```

You'll see:
```
=========================================
  Submitting All GOAT Jobs
=========================================

Found 1 job(s) to submit:

Submitting: run_my_peptide_goat_entropy.sh
  ✓ Job ID: 12345

To monitor jobs:
  squeue -u $USER
```

**Step 8: Monitor Your Job**

```bash
# Check if your job is running
squeue -u $USER

# Watch the output in real-time
tail -f slurm-12345.out
```

Press `Ctrl+C` to stop watching.

**Step 9: Wait for Results**

Depending on your molecule size:
- Small peptide (20-30 atoms): 1-6 hours
- Medium peptide (50-80 atoms): 6-24 hours  
- Large peptide (100+ atoms): 1-4 days

**Step 10: Get Your Results**

When finished, you'll have:
- `my_peptide.finalensemble.xyz` - All conformations found
- `my_peptide.globalminimum.xyz` - Lowest energy structure
- `my_peptide_goat_entropy.out` - Full output with energies

---

## 🎯 Understanding GOAT Variants

Choose the right variant for your needs:

### GOAT (Standard)
**Best for:** Finding the global minimum and major conformers  
**Speed:** ⚡ Fast (1-24 hours)  
**Completeness:** 🟢 Good (~80-90% of conformers)

```bash
# When to use:
- Quick conformational search
- Finding the most stable structure
- Preliminary studies
```

### GOAT-ENTROPY (Most Complete)
**Best for:** Complete conformational ensemble, Boltzmann averaging  
**Speed:** 🐌 Slow (2-4 days)  
**Completeness:** 🟢🟢🟢 Excellent (~95-99% of conformers)

```bash
# When to use:
- Need complete ensemble for property calculations
- Boltzmann-averaged spectra
- Entropy calculations
- Publication-quality results
```

### GOAT-EXPLORE (Topology-Free)
**Best for:** Ring puckering, large conformational changes  
**Speed:** 🐌🐌 Very slow (3-7 days)  
**Completeness:** 🟢🟢 Explores more degrees of freedom

```bash
# When to use:
- Flexible ring systems
- Large conformational changes
- Unknown topology
# ⚠️ For cyclic peptides: ALWAYS use FREEZEBONDS true!
```

### GOAT-DIVERSITY (Structural Diversity)
**Best for:** Quick diverse structures for further refinement  
**Speed:** ⚡⚡ Very fast (hours to 1 day)  
**Completeness:** 🟡 Focuses on diversity, not energy

```bash
# When to use:
- Quick initial scan
- Generating diverse starting structures
- Testing before expensive calculations
```

---

## 🔍 Troubleshooting

### Common Issues and Solutions

#### ❌ "Permission denied" when running the script
```bash
# Solution: Make the script executable
chmod +x generate_goat_inputs.sh
```

#### ❌ "No such file or directory: xyzs/"
```bash
# Solution: Create the xyzs folder
mkdir xyzs
# Then add your XYZ files
cp /path/to/your/molecule.xyz xyzs/
```

#### ❌ "sbatch: command not found"
```bash
# Solution: You're not on the cluster or SLURM isn't available
# Make sure you're connected via SSH to your HPC cluster
```

#### ❌ Job fails immediately after submission
```bash
# Check the error log
cat slurm-*.out

# Common causes:
# 1. Wrong ORCA path - check with: which orca
# 2. Wrong module name - ask your cluster admin
# 3. Not enough memory - reduce memory request
# 4. XYZ file not found - copy XYZ files to job directory
```

#### ❌ "Too many conformers found"
```bash
# Solution: Decrease MAXEN parameter
# When prompted: Maximum relative energy: 6.0
# (instead of default 12.0)
```

#### ❌ "Not enough conformers found"
```bash
# Solution: Use GOAT-ENTROPY instead of GOAT
# Or increase MAXITER when prompted
```

#### ❌ Job runs too long
```bash
# Solutions:
# 1. Use GFNUPHILL gfn2xtb for faster uphill steps
# 2. Increase NWORKERS with more cores
# 3. Use GOAT-DIVERSITY for quick scan first
```

#### ❌ Ring opened in cyclic peptide
```bash
# Solution: When using GOAT-EXPLORE, answer:
# Freeze bonds during uphill step? y
```

### Getting Help

1. **Check the output file**: `cat slurm-*.out` for error messages
2. **Check ORCA output**: `cat *.out` for ORCA-specific errors
3. **Ask your cluster admin**: For cluster-specific issues (modules, paths, resources)
4. **ORCA Forum**: https://orcaforum.kofo.mpg.de for ORCA-related questions
5. **Open an issue**: On this GitHub repository for script-related problems

---

## 📖 Examples

### Example 1: Quick Conformational Search (Beginner)

```bash
./generate_goat_inputs.sh

# Answers:
Selection: 1                    # First XYZ file
GOAT variant: 1                 # GOAT (standard)
Method: [Enter]                 # XTB2 (default)
Use solvent: n                  # Gas phase
Optimization level: [Enter]     # NORMALOPT (default)
# Press Enter for all other prompts to use defaults

cd goat_inputs
./submit_all_jobs.sh
```

### Example 2: Complete Ensemble in Water (Intermediate)

```bash
./generate_goat_inputs.sh

# Answers:
Selection: all                  # All XYZ files
GOAT variant: 2                 # GOAT-ENTROPY
Method: [Enter]                 # XTB2
Use solvent: y                  # Yes
Solvent: Water                  # Water
Optimization level: [Enter]     # NORMALOPT
Total processors: 400           # More cores = faster
Number of workers: 50           # More parallel jobs
Wall time: 168:00:00           # 1 week
Memory: 800G                    # More memory

cd goat_inputs
./submit_all_jobs.sh
```

### Example 3: DFT Refinement (Advanced)

```bash
./generate_goat_inputs.sh

# Answers:
Selection: 1
GOAT variant: 1                 # GOAT (standard)
Method: R2SCAN-3C              # DFT method
Use solvent: y
Solvent: DMSO
Optimization level: TIGHTOPT    # Tight convergence
Use GFN uphill: y              # Faster uphill steps
GFNUPHILL method: gfn2xtb      # Use XTB for uphill
Total processors: 200
Number of workers: 16           # Fewer workers for DFT
Max cores per opt: 64           # More cores per optimization
Wall time: 168:00:00           # 1 week for DFT

cd goat_inputs
./submit_all_jobs.sh
```

---

## 📊 Computational Cost Estimates

### Using XTB2 (Recommended for Initial Searches)

| Molecule Size | GOAT | GOAT-ENTROPY | GOAT-DIVERSITY |
|---------------|------|--------------|----------------|
| Small (20-30 atoms) | 1-6 hours | 6-24 hours | 1-3 hours |
| Medium (50-80 atoms) | 6-24 hours | 1-3 days | 3-6 hours |
| Large (100+ atoms) | 1-3 days | 3-7 days | 6-12 hours |

*Estimates for 200 cores*

### Using DFT (R2SCAN-3C, PBE)

| Molecule Size | GOAT | GOAT-ENTROPY |
|---------------|------|--------------|
| Small (20-30 atoms) | 1-3 days | 3-7 days |
| Medium (50-80 atoms) | 3-7 days | 1-2 weeks |
| Large (100+ atoms) | 1-2 weeks | 2-4 weeks |

*Estimates for 200 cores*

**💡 Tip:** Always start with XTB2, then refine promising conformers with DFT!

---

## 🎓 Recommended Workflow

### For Cyclic Peptides (Step-by-Step)

#### Phase 1: Initial Exploration (1 day)
```bash
# Use GOAT-DIVERSITY for quick scan
GOAT variant: 4 (GOAT-DIVERSITY)
Method: XTB2
Time: ~6-12 hours
```

#### Phase 2: Complete Ensemble (3-4 days)
```bash
# Use GOAT-ENTROPY for complete search
GOAT variant: 2 (GOAT-ENTROPY)
Method: XTB2
Time: ~2-4 days
```

#### Phase 3: DFT Refinement (1 week, optional)
```bash
# Refine top conformers with DFT
GOAT variant: 1 (GOAT)
Method: R2SCAN-3C
GFNUPHILL: gfn2xtb
Time: ~3-7 days
```

---

## 📝 Important Notes for Cyclic Peptides

When working with cyclic peptides, **always** use these settings:

✅ **Freeze amide bonds**: `y` - Prevents unphysical cis/trans flipping  
✅ **Freeze double bonds**: `y` - Preserves E/Z stereochemistry  
✅ **Freeze bonds** (for GOAT-EXPLORE): `y` - Prevents ring opening

The script will prompt you for these automatically!

---

## 🔬 Understanding the Output

After your job completes, you'll find several files:

### Main Output Files

**`molecule.finalensemble.xyz`**
- Contains all conformers found
- Each structure has its relative energy in the comment line
- Can be opened in molecular viewers (Avogadro, VMD, etc.)

**`molecule.globalminimum.xyz`**
- The lowest energy structure
- Your most stable conformation

**`molecule_goat.out`**
- Complete ORCA output
- Contains energies, convergence info, and statistics

### Understanding the Energy Table

In the output file, you'll see:
```
# Final ensemble info #
Conformer Energy Degen. % total % cumul.
         (kcal/mol)
------------------------------------------------------
    0      0.000     1    37.96    37.96
    1      0.503     1    16.25    54.20
    2      0.914     1     8.11    62.32
```

- **Energy**: Relative energy (0 = lowest)
- **% total**: Boltzmann population at 298 K
- **% cumul**: Cumulative population

**What this means:**
- Conformer 0 is the most stable (37.96% populated)
- Top 3 conformers account for 62.32% of the population
- You need all conformers for accurate Boltzmann averaging

---

## 📚 Additional Resources

### Learning More About GOAT

- **ORCA Manual**: Section 4.11 - GOAT
- **ORCA Forum**: https://orcaforum.kofo.mpg.de
- **ORCA Website**: https://orcaforum.kofo.mpg.de

### Learning HPC/SLURM Basics

- **SLURM Documentation**: https://slurm.schedmd.com/quickstart.html
- **HPC Carpentry**: https://www.hpc-carpentry.org/
- **Your Cluster Documentation**: Ask your admin for cluster-specific guides

### Molecular Visualization

- **Avogadro**: https://avogadro.cc/ (Free, easy to use)
- **VMD**: https://www.ks.uiuc.edu/Research/vmd/ (Free, powerful)
- **PyMOL**: https://pymol.org/ (Professional)

---

## 📄 Citation

If you use this tool in your research, please cite:

**ORCA:**
```
Neese, F. Software update: the ORCA program system, version 6.0
Wiley Interdiscip. Rev.: Comput. Mol. Sci., 2025, 15(2), e70019
DOI: 10.1002/wcms.70019
```

**This Tool:**
```
ORCA GOAT Generator
https://github.com/Chemical-Biology-STP/orca-goat-generator
```

---

## 🤝 Contributing

Found a bug? Have a suggestion? Contributions are welcome!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- ORCA development team for the amazing GOAT algorithm
- The computational chemistry community
- All contributors and users of this tool

---

## 💬 Support

- **Issues**: Open an issue on GitHub
- **Questions**: Use GitHub Discussions
- **Email**: [yewmun.yip@crick.ac.uk]

---

## 🎉 Quick Reference Card

```
┌─────────────────────────────────────────────────────────┐
│  GOAT Variant Selection Guide                           │
├─────────────────────────────────────────────────────────┤
│  GOAT            → Fast, good coverage                   │
│  GOAT-ENTROPY    → Slow, complete ensemble              │
│  GOAT-EXPLORE    → Very slow, topology-free             │
│  GOAT-DIVERSITY  → Very fast, structural diversity      │
├─────────────────────────────────────────────────────────┤
│  Cyclic Peptide Must-Haves:                             │
│    ✓ FREEZEAMIDES true                                  │
│    ✓ FREEZECISTRANS true                                │
│    ✓ FREEZEBONDS true (for GOAT-EXPLORE)               │
├─────────────────────────────────────────────────────────┤
│  Speed Tips:                                             │
│    • Use XTB2 for initial searches                      │
│    • Use GFNUPHILL gfn2xtb for DFT                      │
│    • Increase NWORKERS with more cores                  │
│    • Start with GOAT-DIVERSITY for quick scan           │
└─────────────────────────────────────────────────────────┘
```

---

**Happy conformational searching! 🧬**

*Last updated: December 2024*
