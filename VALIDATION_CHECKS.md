# GOAT Input Generator - Validation Checks

## Overview
The generator scripts now include comprehensive validation to prevent common ORCA GOAT configuration errors.

## Validation Checks Implemented

### 1. XTB Solvation Model Compatibility
**Problem**: XTB methods are incompatible with CPCM and SMD solvation models.

**Solution**:
- Detects when XTB methods are selected (XTB2, GFN2-XTB, etc.)
- Prompts user to choose compatible solvation models:
  - **ALPB** (Analytical Linearized Poisson-Boltzmann) - Recommended
  - **ddCOSMO** (Domain-decomposition COSMO)
  - **CPCMX** (Extended CPCM for XTB)
- Warns if incompatible model is selected
- Validates before file generation

**Error Prevented**:
```
WARNING: Found SMD or SMDSolvent or CPCM keyword with XTB calculation.
This is not implemented.
===> : Please use ALPB, ddCOSMO or CPCMX instead
```

### 2. GOAT-ENTROPY Worker Count Validation
**Problem**: GOAT-ENTROPY uses 4 temperature replicas, so NWORKERS must be divisible by 4.

**Solution**:
- Detects GOAT-ENTROPY variant selection
- Displays warning about 4 temperature replicas requirement
- Shows recommended values (4, 8, 12, 16, 20, 24, 28, 32, ...)
- Validates input and suggests nearest valid value if invalid
- Loops until valid value is entered

**Error Prevented**:
```
WARNING: Number of GOAT workers (25) must be a multiple of the number of temperatures (4)!
===> : Adjusting NWORKERS to 24
```

### 3. MAXCORESOPT vs NPROCS Check
**Problem**: MAXCORESOPT larger than NPROCS causes ORCA to automatically reduce it.

**Solution**:
- Compares MAXCORESOPT to NPROCS
- Issues warning if MAXCORESOPT > NPROCS
- Informs user that ORCA will automatically adjust

**Warning Issued**:
```
WARNING: The total number of processors given is larger than MAXCORESOPT for GOAT!
===> : For the first optimization step, it will be reduced to that amount (32).
```

### 4. Pre-Generation Validation Summary
**Feature**: Comprehensive validation report before file generation

**Displays**:
- ✓ Compatibility checks passed
- ✗ Configuration errors detected
- ⚠ Warnings about suboptimal settings

**Actions**:
- Blocks generation if critical errors found
- Allows override with explicit confirmation (not recommended)
- Provides clear error messages and solutions

## Usage

### Python Script
```bash
cd orca-goat-generator
python3 generate_goat_inputs.py
```

### Bash Script
```bash
cd orca-goat-generator
bash generate_goat_inputs.sh
```

Both scripts now include identical validation logic.

## Example Validation Output

```
=========================================
[INFO] === Configuration Validation ===
=========================================

[SUCCESS] Solvation model ALPB is compatible with XTB2
[SUCCESS] NWORKERS (24) is valid for GOAT-ENTROPY (divisible by 4)

[SUCCESS] Created output directory: goat_inputs
```

## Benefits

1. **Prevents Job Failures**: Catches configuration errors before submission
2. **Saves Compute Time**: Avoids wasted HPC resources on invalid jobs
3. **User-Friendly**: Clear prompts and helpful suggestions
4. **Educational**: Explains why certain combinations are invalid
5. **Flexible**: Allows override for advanced users (with warnings)

## Compatibility Notes

### XTB Methods
- XTB2, GFN2-XTB, GFN1-XTB, GFN0-XTB, GFNFF

### Compatible Solvation Models
| Method Type | Compatible Models |
|-------------|-------------------|
| XTB         | ALPB, ddCOSMO, CPCMX |
| DFT/HF      | CPCM, SMD, COSMO, ALPB, ddCOSMO |

### GOAT Variants and Worker Requirements
| Variant | Worker Constraint |
|---------|-------------------|
| GOAT-ENTROPY | Must be divisible by 4 |
| GOAT | No constraint |
| GOAT-EXPLORE | No constraint |
| GOAT-DIVERSITY | No constraint |
