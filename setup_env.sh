#!/usr/bin/env bash
# ==============================================================================
# GMCORE one-click environment setup
#
# Creates a conda environment "gmcore" with:
#   - GNU Fortran compiler (gfortran 12+)
#   - OpenMPI (mpifort, mpicc, mpiexec)
#   - Parallel HDF5 (MPI-enabled)
#   - Parallel NetCDF-C/Fortran (MPI-enabled, nc-config --has-parallel4 = yes)
#   - CMake
#   - Python tools (dashboard, experiments)
#
# Usage:
#   ./setup_env.sh              # Full install (conda env + build + verify)
#   ./setup_env.sh --env-only   # Only create/update conda environment
#   ./setup_env.sh --verify     # Only run verification checks
#
# Prerequisites:
#   - conda, mamba, or micromamba must be on PATH
#   - Internet access for downloading packages
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_NAME="gmcore"
ENV_FILE="$SCRIPT_DIR/environment.yml"

# --- Color output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}[OK]${NC} $*"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail()  { echo -e "${RED}[FAIL]${NC} $*"; exit 1; }

# --- Detect conda tool ---
detect_conda() {
    if command -v mamba &>/dev/null; then
        CONDA_CMD="mamba"
    elif command -v micromamba &>/dev/null; then
        CONDA_CMD="micromamba"
    elif command -v conda &>/dev/null; then
        CONDA_CMD="conda"
    else
        fail "No conda/mamba/micromamba found. Install one first:
  curl -L https://micro.mamba.pm/install.sh | bash"
    fi
    info "Using: $CONDA_CMD"
}

# --- Create or update environment ---
setup_environment() {
    info "Creating/updating conda environment '$ENV_NAME' ..."

    if $CONDA_CMD env list 2>/dev/null | grep -q "^${ENV_NAME} "; then
        info "Environment '$ENV_NAME' exists, updating..."
        $CONDA_CMD env update -n "$ENV_NAME" -f "$ENV_FILE" --prune
    else
        info "Creating new environment '$ENV_NAME'..."
        $CONDA_CMD env create -f "$ENV_FILE"
    fi

    ok "Environment '$ENV_NAME' ready"
}

# --- Activate and verify ---
verify_environment() {
    info "Verifying environment..."

    # Source conda activation
    CONDA_BASE=$(conda info --base 2>/dev/null || true)
    if [[ -n "$CONDA_BASE" ]]; then
        source "$CONDA_BASE/etc/profile.d/conda.sh"
        conda activate "$ENV_NAME" 2>/dev/null || true
    fi

    # If activation didn't set CONDA_PREFIX, find it manually
    if [[ -z "${CONDA_PREFIX:-}" ]] || [[ "$(basename "$CONDA_PREFIX")" != "$ENV_NAME" ]]; then
        local env_path
        env_path="$($CONDA_CMD env list 2>/dev/null | grep "^${ENV_NAME} " | awk '{print $NF}')"
        if [[ -z "$env_path" ]]; then
            # Try alternative format (active env has *)
            env_path="$($CONDA_CMD env list 2>/dev/null | grep "${ENV_NAME}" | sed 's/\*//g' | awk '{print $NF}')"
        fi
        if [[ -z "$env_path" ]]; then
            fail "Cannot find environment '$ENV_NAME'. Run: ./setup_env.sh --env-only"
        fi
        export CONDA_PREFIX="$env_path"
    fi

    export PATH="$CONDA_PREFIX/bin:$PATH"
    export NETCDF_ROOT="$CONDA_PREFIX"

    local errors=0

    echo ""
    echo "  Component checks:"
    echo "  ─────────────────────────────────────────────────"

    # gfortran
    if command -v gfortran &>/dev/null; then
        local gf_ver=$(gfortran --version | head -1)
        ok "  gfortran: $gf_ver"
    else
        echo -e "  ${RED}✗${NC} gfortran: NOT FOUND"; ((errors++))
    fi

    # MPI
    if command -v mpifort &>/dev/null; then
        local mpi_ver
        mpi_ver=$(mpifort --showme:version 2>/dev/null | head -1 || \
                  mpifort --version 2>/dev/null | head -1 || \
                  echo "found")
        ok "  mpifort:  $mpi_ver"
    else
        echo -e "  ${RED}✗${NC} mpifort: NOT FOUND"; ((errors++))
    fi

    if command -v mpiexec &>/dev/null; then
        ok "  mpiexec:  $(which mpiexec)"
    else
        echo -e "  ${RED}✗${NC} mpiexec: NOT FOUND"; ((errors++))
    fi

    # CMake
    if command -v cmake &>/dev/null; then
        ok "  cmake:    $(cmake --version | head -1)"
    else
        echo -e "  ${RED}✗${NC} cmake: NOT FOUND"; ((errors++))
    fi

    # nc-config
    if command -v nc-config &>/dev/null; then
        local nc_ver=$(nc-config --version)
        local nc_par=$(nc-config --has-parallel4)
        if [[ "$nc_par" == "yes" ]]; then
            ok "  netcdf:   $nc_ver (parallel4=yes)"
        else
            echo -e "  ${RED}✗${NC} netcdf: $nc_ver (parallel4=$nc_par — MUST be yes!)"; ((errors++))
        fi
    else
        echo -e "  ${RED}✗${NC} nc-config: NOT FOUND"; ((errors++))
    fi

    # nf-config (NetCDF-Fortran)
    if command -v nf-config &>/dev/null; then
        ok "  netcdf-f: $(nf-config --version)"
    else
        echo -e "  ${RED}✗${NC} nf-config (NetCDF-Fortran): NOT FOUND"; ((errors++))
    fi

    # HDF5 parallel check
    if command -v h5pcc &>/dev/null; then
        ok "  hdf5:     parallel (h5pcc found)"
    elif [[ -f "${CONDA_PREFIX:-}/bin/h5diff" ]]; then
        # Check if HDF5 was built with MPI
        local h5_par=$(h5cc -showconfig 2>/dev/null | grep "Parallel HDF5" || echo "")
        if echo "$h5_par" | grep -qi "yes"; then
            ok "  hdf5:     parallel"
        else
            warn "  hdf5:     found but parallel status unclear"
        fi
    else
        echo -e "  ${RED}✗${NC} hdf5: NOT FOUND"; ((errors++))
    fi

    # Python
    if command -v python &>/dev/null; then
        ok "  python:   $(python --version)"
    else
        echo -e "  ${RED}✗${NC} python: NOT FOUND"; ((errors++))
    fi

    echo "  ─────────────────────────────────────────────────"
    echo ""

    if [[ $errors -gt 0 ]]; then
        fail "$errors component(s) failed verification"
    fi

    ok "All components verified. Ready to build GMCORE."
    echo ""
    echo "  Quick start:"
    echo "    conda activate $ENV_NAME"
    echo "    mkdir build && cd build"
    echo "    cmake .."
    echo "    make -j\$(nproc)"
    echo ""
}

# --- Build GMCORE (optional) ---
build_gmcore() {
    info "Building GMCORE..."
    cd "$SCRIPT_DIR"
    mkdir -p build && cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j"$(nproc)"
    ok "Build complete: $(ls *.exe 2>/dev/null | tr '\n' ' ')"
}

# --- Main ---
main() {
    echo ""
    echo "  ╔════════════════════════════════════════��═╗"
    echo "  ║     GMCORE Environment Setup            ║"
    echo "  ╚══════════════════════════════════════════╝"
    echo ""

    detect_conda

    case "${1:-}" in
        --env-only)
            setup_environment
            ;;
        --verify)
            verify_environment
            ;;
        --build)
            verify_environment
            build_gmcore
            ;;
        *)
            setup_environment
            verify_environment
            echo ""
            info "To build GMCORE now, run: ./setup_env.sh --build"
            info "Or manually:"
            echo "    conda activate $ENV_NAME"
            echo "    mkdir build && cd build && cmake .. && make -j\$(nproc)"
            ;;
    esac
}

main "$@"
