# gmcore-dashboard

GMCORE 数值试验管理与诊断可视化平台。

提供基于 Web 的交互式仪表盘，支持数值试验的配置、提交、监控、诊断后处理及多场对比分析。

## 环境配置

### 一键安装（推荐）

本工具依赖并行 I/O 库栈（MPI-enabled HDF5、NetCDF-C/Fortran）。提供 conda 环境定义与自动化安装脚本：

```bash
# 创建并验证编译环境（含 gfortran、OpenMPI、并行 NetCDF 等）
./setup_env.sh

# 仅创建/更新 conda 环境
./setup_env.sh --env-only

# 仅校验已有环境完整性
./setup_env.sh --verify
```

所安装组件：

| 组件 | 说明 |
|------|------|
| gfortran ≥ 12 | GNU Fortran 编译器 |
| OpenMPI | 消息传递接口（MPI）运行时及编译器封装 |
| HDF5 (mpi) | 并行 HDF5 科学数据格式库 |
| NetCDF-C (mpi) | 并行 NetCDF-C 库（`nc-config --has-parallel4 = yes`）|
| NetCDF-Fortran (mpi) | NetCDF Fortran 绑定（并行模式）|
| CMake ≥ 3.16 | 构建系统生成器 |
| Python ≥ 3.10 | 仪表盘及试验管理 CLI 运行时 |

### 手动安装 Python 包

```bash
# 从 GMCORE 根目录（开发模式）
pip install -e tools/gmcore_dashboard

# 或使用 uv
uv pip install -e tools/gmcore_dashboard
```

## 使用方法

### 仪表盘 Web 界面

```bash
# 自动检测 GMCORE 源码根目录
gmcore-dashboard

# 显式指定根目录
gmcore-dashboard --gmcore-root /path/to/gmcore

# 通过环境变量指定
GMCORE_ROOT=/path/to/gmcore gmcore-dashboard

# 自定义监听地址与端口
gmcore-dashboard --host 0.0.0.0 --port 8080
```

仪表盘包含以下功能模块：

| 标签页 | 功能 |
|--------|------|
| Visualize | 单场 NetCDF 变量可视化（经纬度投影、经向/纬向剖面）|
| Experiments | 试验注册表管理、参数扫描、诊断对比 |
| Multi-view | 多试验多变量并排对比 |
| Configure | Namelist 参数在线编辑 |
| Build & Run | 编译构建与算例提交 |
| Monitor | 运行时日志监控与进程管理 |

### 试验管理 CLI

```bash
# 列出已注册试验
gmcore-experiments list

# 从注册表创建试验实例
gmcore-experiments create cdod_baseline

# 提交运行
gmcore-experiments run <experiment_id>

# 参数敏感性扫描（全因子设计）
gmcore-experiments sweep ddl_wsl_sweep --run

# 诊断后处理
gmcore-experiments diag <experiment_id> --set-name core

# 提取标量度量指标
gmcore-experiments metrics <experiment_id>

# 双试验对比分析
gmcore-experiments compare <exp_a> <exp_b>
```

## 路径配置机制

所有文件路径均相对于 `GMCORE_ROOT` 解析，解析优先级：

1. `--gmcore-root` 命令行参数
2. `GMCORE_ROOT` 环境变量
3. 沿目录树向上搜索 `CMakeLists.txt` 自动检测

### `registry.yaml` 配置

注册表中路径均为相对路径，由框架在运行时拼接 `GMCORE_ROOT`：

```yaml
defaults:
  workspace_root: tools/gmcore_dashboard/experiments/experiments
  executable: build/gmcore_driver.exe
  mpi_launcher: mpirun
  mpi_ranks: 8
```

## 作为 Git 子模块使用

当本仓库作为 GMCORE 的外部依赖时，通过子模块机制拉取：

```bash
git submodule update --init tools/gmcore_dashboard
```

或通过 `pull_libs.py` 自动管理：

```bash
./pull_libs.py --libs dashboard
```

## 依赖清单

### 编译运行依赖（Fortran/C）

- GNU Fortran ≥ 12 或 Intel ifort/ifx
- OpenMPI 或 MPICH（提供 `mpifort`、`mpiexec`）
- 并行 HDF5（MPI-enabled）
- 并行 NetCDF-C/Fortran（MPI-enabled）
- CMake ≥ 3.16

### Python 依赖

```
dash >= 2.0
dash-bootstrap-components >= 1.0
dash-ace >= 0.2
plotly >= 5.0
numpy >= 1.21
xarray >= 2023.1.0
netCDF4 >= 1.6.4
f90nml >= 1.4
pyyaml >= 6.0
diskcache
markdown
```
