#!/usr/bin/env bash
# ==============================================================================
# GMCORE 环境检测与 Python 依赖安装
#
# 策略：
#   1. 编译依赖（gfortran, MPI, HDF5, NetCDF）—— 仅检测本地已有环境，
#      不自动安装（这些由系统管理员或 module load 提供）。
#   2. Python 依赖（dashboard, experiments）—— 通过 pip 安装。
#
# Usage:
#   ./setup_env.sh              # 检测编译环境 + 安装 Python 依赖
#   ./setup_env.sh --check      # 仅检测，不安装任何东西
#   ./setup_env.sh --pip-only   # 仅安装 Python 依赖（跳过编译环境检测）
#   ./setup_env.sh --build      # 检测 + 安装 + 编译 GMCORE
#
# 编译依赖检测顺序：
#   1. 当前 PATH / LD_LIBRARY_PATH 中的工具
#   2. 环境变量 NETCDF_ROOT / NETCDF / HDF5_ROOT
#   3. module 系统（如有）
#   4. conda/mamba 环境（如有）
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GMCORE_ROOT="$(cd "$SCRIPT_DIR/../.." 2>/dev/null && pwd || echo "$SCRIPT_DIR")"

# --- Color output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

info()  { echo -e "${BLUE}[INFO]${NC} $*"; }
ok()    { echo -e "${GREEN}  ✓${NC} $*"; }
warn()  { echo -e "${YELLOW}  ⚠${NC} $*"; }
miss()  { echo -e "${RED}  ✗${NC} $*"; }
hint()  { echo -e "      ${CYAN}→${NC} $*"; }

# ==============================================================================
# 编译环境检测
# ==============================================================================

check_compile_env() {
    info "检测编译环境..."
    echo ""
    echo "  ┌──────────────────────────────────────────────────┐"
    echo "  │  编译环境检测（仅检测，不安装）                  │"
    echo "  └──────────────────────────────────────────────────┘"
    echo ""

    local errors=0
    local warnings=0

    # ── gfortran ──
    if command -v gfortran &>/dev/null; then
        local gf_ver
        gf_ver=$(gfortran -dumpversion 2>/dev/null || echo "?")
        local gf_major=${gf_ver%%.*}
        if [[ "$gf_major" -ge 12 ]] 2>/dev/null; then
            ok "gfortran $gf_ver"
        else
            warn "gfortran $gf_ver （建议 ≥ 12）"
            ((warnings++))
        fi
    elif command -v ifort &>/dev/null; then
        ok "ifort $(ifort --version 2>&1 | head -1)"
    elif command -v ifx &>/dev/null; then
        ok "ifx $(ifx --version 2>&1 | head -1)"
    else
        miss "Fortran 编译器未找到"
        hint "安装: apt install gfortran / yum install gcc-gfortran / module load gcc"
        ((errors++))
    fi

    # ── MPI ──
    if command -v mpifort &>/dev/null; then
        local mpi_info
        mpi_info=$(mpifort --showme:version 2>/dev/null || mpifort --version 2>/dev/null | head -1 || echo "found")
        ok "mpifort ($mpi_info)"
    elif command -v mpiifort &>/dev/null; then
        ok "mpiifort (Intel MPI)"
    else
        miss "MPI Fortran 编译器 (mpifort/mpiifort) 未找到"
        hint "安装: apt install libopenmpi-dev / module load openmpi"
        ((errors++))
    fi

    if command -v mpiexec &>/dev/null || command -v mpirun &>/dev/null; then
        ok "MPI launcher: $(which mpiexec 2>/dev/null || which mpirun)"
    else
        miss "mpiexec/mpirun 未找到"
        ((errors++))
    fi

    # ── CMake ──
    if command -v cmake &>/dev/null; then
        ok "cmake $(cmake --version | head -1 | awk '{print $3}')"
    else
        miss "cmake 未找到"
        hint "安装: pip install cmake / apt install cmake"
        ((errors++))
    fi

    # ── NetCDF ──
    local nc_config_bin=""
    # 优先使用 NETCDF_ROOT
    if [[ -n "${NETCDF_ROOT:-}" ]] && [[ -x "${NETCDF_ROOT}/bin/nc-config" ]]; then
        nc_config_bin="${NETCDF_ROOT}/bin/nc-config"
    elif [[ -n "${NETCDF:-}" ]] && [[ -x "${NETCDF}/bin/nc-config" ]]; then
        nc_config_bin="${NETCDF}/bin/nc-config"
    elif command -v nc-config &>/dev/null; then
        nc_config_bin="$(which nc-config)"
    fi

    if [[ -n "$nc_config_bin" ]]; then
        local nc_ver
        nc_ver=$("$nc_config_bin" --version 2>/dev/null || echo "?")
        local nc_par
        nc_par=$("$nc_config_bin" --has-parallel4 2>/dev/null || echo "unknown")
        if [[ "$nc_par" == "yes" ]]; then
            ok "NetCDF-C $nc_ver (parallel4=yes)"
        else
            warn "NetCDF-C $nc_ver (parallel4=$nc_par — 建议使用并行版本)"
            hint "并行 I/O 需要 MPI-enabled HDF5 + NetCDF；串行版本可运行但输出受限"
            ((warnings++))
        fi
    else
        miss "nc-config 未找到（NetCDF-C 未安装或未设置 NETCDF_ROOT）"
        hint "设置: export NETCDF_ROOT=/path/to/netcdf"
        hint "或: module load netcdf"
        ((errors++))
    fi

    # ── NetCDF-Fortran ──
    if command -v nf-config &>/dev/null; then
        ok "NetCDF-Fortran $(nf-config --version 2>/dev/null || echo '?')"
    elif [[ -n "${NETCDF_ROOT:-}" ]] && [[ -f "${NETCDF_ROOT}/include/netcdf.mod" ]]; then
        ok "NetCDF-Fortran (found netcdf.mod in NETCDF_ROOT)"
    else
        miss "NetCDF-Fortran (nf-config) 未找到"
        hint "通常与 NetCDF-C 一起安装；检查 module avail netcdf"
        ((errors++))
    fi

    # ── HDF5 ──
    if command -v h5pcc &>/dev/null; then
        ok "HDF5 并行版 (h5pcc found)"
    elif command -v h5cc &>/dev/null; then
        local h5_par
        h5_par=$(h5cc -showconfig 2>/dev/null | grep -i "Parallel HDF5" | awk '{print $NF}' || echo "unknown")
        if [[ "$h5_par" == "yes" ]]; then
            ok "HDF5 并行版"
        else
            warn "HDF5 已安装但并行状态未确认 (Parallel=$h5_par)"
            ((warnings++))
        fi
    elif [[ -n "${HDF5_ROOT:-}" ]]; then
        ok "HDF5 (HDF5_ROOT=$HDF5_ROOT)"
    else
        warn "HDF5 未显式检测到（可能随 NetCDF 自带）"
        ((warnings++))
    fi

    echo ""
    echo "  ──────────────────────────────────────────────────"

    if [[ $errors -gt 0 ]]; then
        echo ""
        echo -e "  ${RED}$errors 项缺失${NC}，$warnings 项警告"
        echo ""
        echo "  常见解决方案："
        echo "    • HPC 集群:  module load gcc openmpi netcdf-fortran cmake"
        echo "    • Ubuntu:    sudo apt install gfortran libopenmpi-dev libnetcdf-dev libnetcdff-dev cmake"
        echo "    • CentOS:    sudo yum install gcc-gfortran openmpi-devel netcdf-fortran-devel cmake"
        echo "    • macOS:     brew install gcc open-mpi netcdf netcdf-fortran cmake"
        echo "    • conda:     conda install -c conda-forge gfortran_linux-64 openmpi hdf5=*=mpi* libnetcdf=*=mpi* netcdf-fortran=*=mpi* cmake"
        echo ""
        return 1
    fi

    if [[ $warnings -gt 0 ]]; then
        echo -e "  ${GREEN}基本可用${NC}（$warnings 项警告，非阻断性）"
    else
        echo -e "  ${GREEN}编译环境完备${NC}"
    fi
    echo ""
    return 0
}

# ==============================================================================
# Python 环境检测与安装
# ==============================================================================

check_python() {
    local py_cmd=""
    if command -v python3 &>/dev/null; then
        py_cmd="python3"
    elif command -v python &>/dev/null; then
        py_cmd="python"
    fi

    if [[ -z "$py_cmd" ]]; then
        miss "Python 未找到"
        hint "安装: https://www.python.org/downloads/"
        hint "或使用 pyenv: curl https://pyenv.run | bash && pyenv install 3.12"
        return 1
    fi

    local py_ver
    py_ver=$($py_cmd --version 2>&1 | awk '{print $2}')
    local py_major py_minor
    py_major=$(echo "$py_ver" | cut -d. -f1)
    py_minor=$(echo "$py_ver" | cut -d. -f2)

    if [[ "$py_major" -lt 3 ]] || { [[ "$py_major" -eq 3 ]] && [[ "$py_minor" -lt 10 ]]; }; then
        miss "Python $py_ver 版本过低（需要 ≥ 3.10）"
        hint "升级: pyenv install 3.12 && pyenv global 3.12"
        return 1
    fi

    ok "Python $py_ver ($py_cmd → $(which $py_cmd))"
    echo "$py_cmd"
    return 0
}

install_python_deps() {
    info "安装 Python 依赖..."
    echo ""
    echo "  ┌──────────────────────────────────────────────────┐"
    echo "  │  Python 依赖安装（pip install）                  │"
    echo "  └──────────────────────────────────────────────────┘"
    echo ""

    local py_cmd
    py_cmd=$(check_python 2>/dev/null | tail -1)
    if [[ -z "$py_cmd" ]]; then
        check_python
        return 1
    fi

    # 确保 pip 可用
    if ! $py_cmd -m pip --version &>/dev/null; then
        miss "pip 不可用"
        hint "安装: $py_cmd -m ensurepip --upgrade"
        hint "或: curl https://bootstrap.pypa.io/get-pip.py | $py_cmd"
        return 1
    fi

    ok "pip $($py_cmd -m pip --version | awk '{print $2}')"

    # 安装当前包（开发模式）
    info "  执行: pip install -e $SCRIPT_DIR"
    echo ""
    $py_cmd -m pip install -e "$SCRIPT_DIR" --quiet --quiet 2>&1 | while read -r line; do
        echo "    $line"
    done

    if [[ ${PIPESTATUS[0]} -eq 0 ]]; then
        echo ""
        ok "Python 依赖安装完成"
        echo ""
        echo "  已注册命令："
        echo "    • gmcore-dashboard      — 启动 Web 仪表盘"
        echo "    • gmcore-experiments    — 试验管理 CLI"
        echo ""
    else
        echo ""
        miss "pip install 失败，请检查上方错误信息"
        return 1
    fi
}

# ==============================================================================
# 编译 GMCORE
# ==============================================================================

build_gmcore() {
    info "编译 GMCORE..."
    cd "$GMCORE_ROOT"
    mkdir -p build && cd build
    cmake .. -DCMAKE_BUILD_TYPE=Release
    make -j"$(nproc)"
    echo ""
    ok "编译完成: $(ls *.exe 2>/dev/null | tr '\n' ' ')"
}

# ==============================================================================
# Main
# ==============================================================================

main() {
    echo ""
    echo "  ╔══════════════════════════════════════════╗"
    echo "  ║     GMCORE 环境配置工具                  ║"
    echo "  ╚══════════════════════════════════════════╝"
    echo ""

    case "${1:-}" in
        --check)
            check_compile_env || true
            echo ""
            check_python || true
            ;;
        --pip-only)
            install_python_deps
            ;;
        --build)
            check_compile_env || fail "编译环境不完整，无法继续"
            install_python_deps
            build_gmcore
            ;;
        -h|--help)
            echo "用法: ./setup_env.sh [选项]"
            echo ""
            echo "选项:"
            echo "  (无参数)     检测编译环境 + 安装 Python 依赖"
            echo "  --check      仅检测环境，不安装"
            echo "  --pip-only   仅安装 Python 依赖（pip install -e .）"
            echo "  --build      检测 + 安装 + 编译 GMCORE"
            echo "  -h, --help   显示此帮助"
            echo ""
            echo "编译依赖检测优先级:"
            echo "  1. PATH 中的工具 (gfortran, mpifort, nc-config, cmake)"
            echo "  2. 环境变量 NETCDF_ROOT / HDF5_ROOT"
            echo "  3. module load 加载的模块"
            echo "  4. conda 环境（如已激活）"
            echo ""
            echo "Python 依赖通过 pip 安装，无需 conda。"
            ;;
        *)
            check_compile_env || true
            echo ""
            install_python_deps
            echo ""
            echo "  下一步:"
            echo "    cd $(realpath "$GMCORE_ROOT") && mkdir -p build && cd build"
            echo "    cmake .. && make -j\$(nproc)"
            echo ""
            ;;
    esac
}

main "$@"
