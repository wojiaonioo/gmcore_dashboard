"""Chinese display names and default analyses for GMCORE test cases.

Keys are exact case directory names (the string returned by Path(case_dir).name).
"""

# ---------------------------------------------------------------------------
# Chinese display names
# ---------------------------------------------------------------------------
CASE_DISPLAY_NAMES: dict[str, str] = {
    # ── adv ──
    "adv_dc1.360x180":    "形变流场平流 DC1（360×180）",
    "adv_dc2.360x180":    "形变流场平流 DC2（360×180）",
    "adv_dc3.360x180":    "形变流场平流 DC3（360×180）",
    "adv_dc4.360x180":    "形变流场平流 DC4（360×180）",
    "adv_dc4.720x360":    "形变流场平流 DC4（720×360）",
    "adv_dc4.1440x720":   "形变流场平流 DC4（1440×720）",
    "adv_dcmip12.360x180":"DCMIP2012 Hadley 型经向环流平流（360×180）",
    "adv_mv.360x180":     "移动涡旋平流（360×180）",
    "adv_sr.360x180":     "刚体平移平流（360×180）",
    "adv_sr.720x360":     "刚体平移平流（720×360）",
    # ── aqua ──
    "aqua.360x180":       "水球理想模拟（360×180）",
    # ── bw ──
    "bw.150x75":          "斜压波（150×75）",
    "bw.180x90":          "斜压波（180×90）",
    "bw.360x180":         "斜压波（360×180）",
    "bw.720x360":         "斜压波（720×360）",
    "bw.1440x720":        "斜压波（1440×720）",
    "bw.2880x1440":       "斜压波（2880×1440）",
    # ── check ──
    "check_parallel":     "并行一致性检验",
    "check_restart":      "重启动一致性检验",
    # ── cm ──
    "cm.720x360":         "碰撞偶极子（720×360）",
    # ── dcmip ──
    "dcmip31":            "DCMIP2016 山脉 Rossby 波（测试 3.1）",
    # ── hs ──
    "hs.128x72":          "Held-Suarez 气候态（128×72）",
    "hs.360x180":         "Held-Suarez 气候态（360×180）",
    # ── ksp15 ──
    "ksp15_01":           "非静力过山重力波（KSP2015-01）",
    "ksp15_02":           "非静力过山重力波（KSP2015-02，含风切变）",
    # ── lin97 ──
    "lin97_static.100x5": "Lin1997 静态山地 PGF 测试（100×5）",
    # ── mz ──
    "mz.180x90":          "斜压地形波（180×90）",
    "mz.360x180":         "斜压地形波（360×180）",
    "mz.1440x720":        "斜压地形波（1440×720）",
    # ── nh ──
    "nh_bw.360x180":      "非静力斜压波（360×180）",
    "nh_mz.360x180":      "非静力斜压地形波（360×180）",
    # ── rh ──
    "rh.180x90":          "三维 Rossby-Haurwitz 波（180×90）",
    "rh.360x180":         "三维 Rossby-Haurwitz 波（360×180）",
    # ── sc ──
    "sc.180x90":          "超级单体分裂（180×90）",
    "sc.360x180":         "超级单体分裂（360×180）",
    "sc.720x360":         "超级单体分裂（720×360）",
    # ── ss ──
    "ss.180x90":          "斜压稳态地转流（180×90）",
    "ss.360x180":         "斜压稳态地转流（360×180）",
    "ss_pgf.360x181":     "稳态气压梯度力（360×181）",
    # ── swm ──
    "swm_cm.720x360":     "浅水-碰撞偶极子（720×360）",
    "swm_cp.360x180":     "浅水-跨极点旋转高低压（360×180）",
    "swm_jz.180x90":      "浅水-不稳定急流（Galewsky，180×90）",
    "swm_jz.360x180":     "浅水-不稳定急流（Galewsky，360×180）",
    "swm_jz.720x360":     "浅水-不稳定急流（Galewsky，720×360）",
    "swm_jz.3600x1800":   "浅水-不稳定急流（Galewsky，3600×1800）",
    "swm_mz.180x90":      "浅水-正压地形波（TC5，180×90）",
    "swm_mz.360x180":     "浅水-正压地形波（TC5，360×180）",
    "swm_mz.720x360":     "浅水-正压地形波（TC5，720×360）",
    "swm_mz.1440x720":    "浅水-正压地形波（TC5，1440×720）",
    "swm_mz.3600x1800":   "浅水-正压地形波（TC5，3600×1800）",
    "swm_rh.180x90":      "浅水-Rossby-Haurwitz 波（TC6，180×90）",
    "swm_rh.360x180":     "浅水-Rossby-Haurwitz 波（TC6，360×180）",
    "swm_rh.720x360":     "浅水-Rossby-Haurwitz 波（TC6，720×360）",
    "swm_rh.3600x1800":   "浅水-Rossby-Haurwitz 波（TC6，3600×1800）",
    "swm_sg.360x180":     "浅水-稳态非线性地转流（TC2，360×180）",
    "swm_sp.360x180":     "浅水-球面溅水（Chen 2021，360×180）",
    "swm_vr.180x90":      "浅水-平流层涡度侵蚀（180×90）",
    "swm_vr.360x180":     "浅水-平流层涡度侵蚀（360×180）",
    "swm_vr.512x256":     "浅水-平流层涡度侵蚀（512×256）",
    # ── tc ──
    "tc.360x180":         "赤道气旋（360×180）",
    "tc.720x360":         "赤道气旋（720×360）",
    "tc.1440x720":        "赤道气旋（1440×720）",
}


# ---------------------------------------------------------------------------
# Map background selection for 2-D lon/lat plots.
#
# GMCORE test cases are all idealized — none are on a real Earth map, so the
# Natural Earth coastline overlay is misleading. Each case is tagged as either
# "topography" (idealized mountain / terrain — overlay surface geopotential
# contours when available) or "none" (pure ideal grid — draw nothing).
# Any case not listed here falls back to "none".
# ---------------------------------------------------------------------------
CASE_MAP_BACKGROUND: dict[str, str] = {
    # Idealized mountain / terrain cases — overlay gzs (surface geopotential)
    # contours so the reader can see where the forcing sits.
    "swm_mz.180x90":      "topography",
    "swm_mz.360x180":     "topography",
    "swm_mz.720x360":     "topography",
    "swm_mz.1440x720":    "topography",
    "swm_mz.3600x1800":   "topography",
    "mz.180x90":          "topography",
    "mz.360x180":         "topography",
    "mz.1440x720":        "topography",
    "nh_mz.360x180":      "topography",
    "ksp15_01":           "topography",
    "ksp15_02":           "topography",
    "dcmip31":            "topography",
    "ss_pgf.360x181":     "topography",
    "lin97_static.100x5": "topography",
}


def get_map_background(case_name: str | None) -> str:
    """Return the map background mode for *case_name* (coastline / topography / none).

    Unknown cases default to ``"none"`` — every GMCORE case is idealized.
    """
    if not case_name:
        return "none"
    return CASE_MAP_BACKGROUND.get(case_name, "none")


# ---------------------------------------------------------------------------
# Default analyses for cases that have been run (have .nc output).
# Shown in the Case Analysis panel until the user saves custom content.
# ---------------------------------------------------------------------------
CASE_DEFAULT_ANALYSES: dict[str, str] = {
    # ── adv ──────────────────────────────────────────────────────────────────

    "adv_dc1.360x180": r"""
## 形变流场平流测试 DC1（360×180）

**配置：** 360×180 水平网格，纯平流模式，积分 12 天，Δt = 600 s

![参考示意图：形变流场平流测试](/assets/ref_figures/ref_advection.png)

这个测试考察的是平流方案在大变形无辐散流场中的**精度与保形性**。
对应 DCMIP2012 Suite 1 Test 1：初始场为两个**余弦钟脉冲**，流场前 6 天顺向变形，
后 6 天反向恢复，12 天后标量应精确回到初始位置。

平流方程 ∂q/∂t + **v**·∇q = 0 是大气数值模式中最基本的方程之一。
在真实大气中，示踪物（水汽、气溶胶、化学物种）的输运决定了全球物质循环。
这里用的是 Nair & Lauritzen（2010）提出的可逆形变流场，该流场在前半周期
将余弦钟脉冲拉伸为狭长丝状结构，后半周期完全恢复——
这种极端变形对平流方案的**保形性**（shape-preserving）和**精度**是个严苛考验。

**初值怎么给的：**
- 流场：Nair & Lauritzen（2010）双涡旋可逆形变流场（无辐散，∇·**v** = 0）
- 标量 q₁：两个余弦钟，分别置于 (5°N, 0°) 和 (5°S, 180°)
- 理论上 t = 12 天 = t = 0（流场完全可逆）

GMCORE 采用**通量型有限体积（FFSL）**平流方案，在经纬度网格上通过
Strang-splitting 实现水平方向的算子分裂。PPM（Piecewise Parabolic Method）
子网格重构配合单调限制器保证正定性和单调性。

我预期看到的结果和诊断指标：

| 误差范数 | 参考量级（1°×1° 网格） |
|---|---|
| ℓ₁ | ≈ 0.04 |
| ℓ₂ | ≈ 0.05 |
| ℓ∞ | ≈ 0.3 |

- 质量守恒偏差应在机器精度量级（~10⁻¹⁵）
- 不应出现虚假超调/下调（Gibbs 振荡）
- 最大值不超过初始最大值（单调性约束）

### 参考文献
- [Lauritzen et al. (2012) *Geosci. Model Dev.* 5, 887–901](https://doi.org/10.5194/gmd-5-887-2012)
- [Nair & Lauritzen (2010) *J. Comput. Phys.* 229, 8868–8887](https://doi.org/10.1016/j.jcp.2010.08.014)
""",

    "adv_dc2.360x180": r"""
## 形变流场平流测试 DC2（360×180）

**配置：** 360×180，纯平流，积分 12 天，Δt = 600 s

这是 DC1 的扩展：加入了**示踪物关联约束**（φ₂ = φ₁²），
我想看看方案在输运过程中能否维持非线性示踪物之间的物理相关性。

在大气化学输运中，不同化学物种之间存在已知的函数关系（如 O₃ 与 NOₓ 的化学平衡态）。
如果平流方案破坏了这种关系（即引入"虚假混合"），将导致化学反应速率计算的系统偏差。
DC2 通过检验 φ₂ = φ₁² 的关联是否在输运后仍然成立来量化这种误差。
非线性保形方案（如 PPM + 限制器）通常优于线性方案（如 SL 不带限制器）。

**初值怎么给的：**
与 DC1 相同的余弦钟 + 双涡旋流场；携带额外关联示踪物 φ₂ = φ₁²。

除 DC1 的误差范数外，我关注的重点是**关联偏差**：

ε_corr = ‖φ₂ⁿᵘᵐ − (φ₁ⁿᵘᵐ)²‖₂ → 0

- 完美保关联方案：ε_corr = 0
- 典型一阶方案：ε_corr ≈ 0.1–0.3
- 散布图（scatter plot）中 (φ₁, φ₂) 应保持在抛物线 φ₂ = φ₁² 附近

### 参考文献
- [Lauritzen et al. (2012) *Geosci. Model Dev.* 5, 887–901](https://doi.org/10.5194/gmd-5-887-2012)
""",

    "adv_dc3.360x180": r"""
## 形变流场平流测试 DC3（360×180）

**配置：** 360×180，纯平流，积分 12 天，Δt = 600 s

这个测试用**槽函数（slotted cylinders）**替代光滑余弦钟，
我想看看方案在**不连续初值**下的保形能力：是否引入负值、过冲或虚假扩散。

真实大气中存在锐利的标量边界（如锋面附近的水汽跃变、云边界），
这些不连续特征对平流方案提出了严峻考验。过度扩散会模糊锋面结构，
而 Gibbs 振荡会引入非物理的负值。槽函数测试正是模拟这类极端情形。

**初值怎么给的：**
- 流场：同 DC1（双涡旋可逆形变流场）
- 标量：两个带矩形槽口的圆柱函数（不连续边界），分别置于 (5°N, 0°) 和 (5°S, 180°)

12 天后复原；按理负值量应为零（或满足方案声明的保形界限）。
ℓ₂ 误差通常大于 DC1（因初值不连续）。
关键指标是有没有单调性破坏、最小值是否低于初始最小值，
以及不连续边缘处有没有明显 ringing。

### 参考文献
- [Lauritzen et al. (2012) *Geosci. Model Dev.* 5, 887–901](https://doi.org/10.5194/gmd-5-887-2012)
""",

    "adv_dc4.360x180": r"""
## 形变流场平流测试 DC4（360×180）

**配置：** 360×180，动力+平流（dt_dyn=300 s，dt_adv=1800 s），积分 12 天

这个测试对应 DCMIP2012 Suite 1 Test 4：使用**大尺度非可逆纬向流**
（斜压流场在 12 天内单向演变），我关注的是平流方案在不可逆真实风场驱动下
的长时间守恒性与数值稳定性。

与 DC1–DC3 的可逆流场不同，DC4 更接近真实大气：
流场由斜压扰动驱动，12 天后不再恢复。
这使得误差评估必须依赖高分辨率参考解（如 1440×720），
重点关注长时间积分中的**质量守恒性、正定性和数值稳定性**。

**初值怎么给的：**
- 流场：纬向背景风 + 斜压扰动叠加形成的非可逆大尺度流
- 标量：余弦钟脉冲

与高分辨率参考解对比，我预期看到：
- 质量守恒（相对误差 < 10⁻¹⁰）
- 终态形状（spreading 量化，无虚假极小值）
- 与 DC4 1440×720 高分辨率版本进行收敛性比较

### 参考文献
- [Lauritzen et al. (2012) *Geosci. Model Dev.* 5, 887–901](https://doi.org/10.5194/gmd-5-887-2012)
""",

    "adv_dc4.1440x720": r"""
## 形变流场平流测试 DC4（1440×720，高分辨率）

**配置：** 1440×720（约 0.25°），积分 12 天

这个配置的用途是提供 DC4 的**高分辨率参考解**，用来量化平流方案的收敛阶数，
以及作为评估低分辨率结果准确性的基准。

相比 360×180，ℓ₂ 误差应以 ≥ 2 阶收敛；
高分辨率下可观察到更精细的标量结构，可以判断低分辨率是否出现过度扩散。

| 分辨率 | 期望 ℓ₂ 误差量级 | 收敛比 |
|---|---|---|
| 360×180 | ~0.05 | — |
| 720×360 | ~0.015 | ~3.3× |
| 1440×720 | ~0.004 | ~3.8× |

### 参考文献
- [Lauritzen et al. (2012) *Geosci. Model Dev.* 5, 887–901](https://doi.org/10.5194/gmd-5-887-2012)
""",

    "adv_dcmip12.360x180": r"""
## DCMIP2012 Hadley 型经向环流平流测试（360×180×60）

**配置：** 360×180，60 层（dcmip12 hybrid 模板），积分 1 天，Δt = 300 s

这个测试把 DCMIP2012 平流测试扩展到了**三维球坐标系**：
我想在兼含水平与垂直分量的时变流场中，验证三维平流方案的精度与质量守恒性。

真实大气输运本质上是三维过程：水汽在热带对流区的强上升运动中
被抬升至对流层顶，再通过 Brewer-Dobson 环流水平输运至极区。
三维平流测试考察数值方案在垂直坐标变换（地面跟随坐标/混合坐标）
引入额外度量因子后能否保持精度。

**初值怎么给的：**
- 流场：DCMIP2012 三维时变无辐散流（同时含 u, v, w 分量）
- 标量：球形余弦钟，初始置于中层大气（约 500 hPa）
- 1 天后流场恢复，标量应回到初始位置

我预期看到：1 天后与解析解对比，ℓ₂ 误差量级参考 2D 测试（约 0.05）；
垂直坐标变换引入的额外误差须通过网格收敛性验证；
质量守恒偏差 < 10⁻¹⁰。

### 参考文献
- [Kent et al. (2014) *Q. J. R. Meteorol. Soc.* 140, 1279–1293](https://doi.org/10.1002/qj.2208)
""",

    "adv_mv.360x180": r"""
## 移动涡旋平流测试（360×180）

**配置：** 360×180，纯平流，积分 12 天，Δt = 600 s

这是 Nair & Jablonowski（2008）**移动涡旋测试**：流场为解析旋转涡旋对，
标量场随流绕全球传播并经过极区，12 天后回到原位。
我关注的是**极区附近平流精度**及经向传播误差。

经纬度网格在极点处存在固有的几何奇异性（经线汇聚），
导致极区附近的分辨率极高而纬向 CFL 数受限。
这个测试设计的移动涡旋轨迹刻意穿越极区，
用来看平流方案是否能在极区保持各向同性的精度，
以及极区滤波/阻尼处理有没有引入额外误差。

**初值怎么给的：**
- 流场：纯刚体背景旋转 + 叠加的涡旋扰动（12 天可逆）
- 标量：光滑高斯型涡旋结构，中心初始置于赤道

12 天后标量场应回到初始分布。
若方案存在极区奇异性，涡旋经过极区时误差会显著偏大——
对比极区误差与赤道误差的比值可以评估各向同性。

### 参考文献
- [Nair & Jablonowski (2008) *Mon. Weather Rev.* 136, 699–711](https://doi.org/10.1175/2007MWR2102.1)
""",

    "adv_sr.360x180": r"""
## 刚体平移平流测试（360×180）

**配置：** 360×180，纯平流，积分 12 天，Δt = 600 s

这个测试对应 Williamson et al.（1992）**Test Case 1**：余弦钟脉冲在纯刚体旋转流中绕全球一整圈，
我想检验方案的**各向同性、相位误差及极区处理**。

刚体旋转是最简单的球面平流测试，但通过改变旋转轴与赤道的夹角 α，
可以有效检验方案在不同纬度带的精度一致性。
当 α = π/2 时，标量穿越极点，对经纬度网格上的方案构成最严苛考验。

**初值怎么给的：**
- 流场：无辐散刚体旋转，周期 T = 12 天（绕行一圈）
- 标量：余弦钟脉冲，初始中心置于 (0°, 270°)（lon₀ = 3π/2）

12 天后标量应精确回到初始位置。
ℓ₂ 误差典型量级 O(10⁻³)（1° 网格，二阶方案），不应出现数值扩散、分裂或振荡。
与 720×360 版本对比可量化收敛阶数。

### 参考文献
- [Williamson et al. (1992) *J. Comput. Phys.* 102, 211–224](https://doi.org/10.1016/S0021-9991(05)80016-6)
""",

    # ── bw ───────────────────────────────────────────────────────────────────

    "bw.180x90": r"""
## 斜压波测试（180×90）

**配置：** 180×90，30 层 hybrid（cam_l30），积分 10 天，Δt = 300 s，散度+涡度阻尼开启

![参考示意图：斜压不稳定波发展](/assets/ref_figures/ref_baroclinic_wave.png)

这个测试来自 Ullrich, Melvin, Staniforth & Jablonowski（2014）的斜压不稳定波方案：
从解析均衡初值出发施加波数 6 扰动，我想看模式对**斜压不稳定增长机制**的模拟能力。

斜压不稳定是中纬度天气系统（温带气旋）发生的主要机制。
在经向温度梯度和纬向急流的背景下，微小扰动从基本流中提取有效位能（APE），
转化为扰动动能（EKE），导致气旋–反气旋对的指数增长。
Charney（1947）和 Eady（1949）的线性理论给出了增长率的解析解。
这个测试就是验证动力核能否正确模拟这一增长过程及后续的非线性饱和阶段。

**初值怎么给的：**
- 背景：纬向对称的均衡初始场（温度、风速、地表气压由解析公式给定）
- 扰动：在 (40°N, 20°E) 叠加 exp(−r²) 型流函数扰动，触发斜压不稳定

GMCORE 采用 Arakawa C 网格上的涡度–散度形式离散，配合 IAP 变换保证总能量守恒。
涡度和散度阻尼（二阶/四阶）用于控制计算噪声，不应过度阻尼以免削弱斜压增长。

我预期在第 9–10 天看到波数 4–6 的斜压波列，
850 hPa 温度扰动振幅约 5–12 K。
与 360×180 和高分辨率参考解对比，波形相位偏差应 < 10°，振幅偏差 < 20%。

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Ullrich et al. (2014) *Q. J. R. Meteorol. Soc.* 140, 1590–1602](https://doi.org/10.1002/qj.2241)
- [Jablonowski & Williamson (2006) *Q. J. R. Meteorol. Soc.* 132, 2943–2975](https://doi.org/10.1256/qj.06.12)
""",

    "bw.360x180": r"""
## 斜压波测试（360×180）

**配置：** 360×180，30 层 hybrid（cam_l30），积分 10 天，Δt = 300 s，散度+涡度阻尼开启

这是斜压波测试的**标准分辨率**配置，主要用途是和其他全球大气动力核
（CAM-SE、DYNAMICO、ICON、FV3 等）进行 DCMIP 式互比对。

在 1° 分辨率下，斜压波的主要特征尺度（~1000 km 波长）可以被充分分辨。
这个分辨率是 DCMIP2016 互比对中多数模式的标准选择，
因此 GMCORE 在此分辨率下的结果可直接与国际主流模式对比。

**初值怎么给的：**
与 180×90 版本相同；可切换干/湿（moist=0/1）和深/浅大气（deep=0/1）选项。

第 10 天 850 hPa 温度扰动参考 DCMIP2016 图集（Fig. 9–12）：
我预期气旋中心经度偏差 < 5°，最大温度扰动振幅偏差 < 15%，锋面锐度与参考解一致。

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Jablonowski & Williamson (2006) *Q. J. R. Meteorol. Soc.* 132, 2943–2975](https://doi.org/10.1256/qj.06.12)
- [Ullrich et al. (2014) *Q. J. R. Meteorol. Soc.* 140, 1590–1602](https://doi.org/10.1002/qj.2241)
- [Ullrich et al. (2017) *Geosci. Model Dev.* 10, 4477–4509](https://doi.org/10.5194/gmd-10-4477-2017)
""",

    "bw.1440x720": r"""
## 斜压波测试（1440×720，高分辨率）

**配置：** 1440×720（约 0.25°），30 层，积分 10 天，散度+涡度阻尼开启

这个配置的作用是提供斜压波测试的**高分辨率参考解**：
一方面量化低分辨率版本（180×90、360×180）的收敛性，
另一方面验证高分辨率下细尺度结构（锋面、次级涡旋）能否自洽发展。

我预期主斜压波列结构与低分辨率一致，
但额外出现更精细的锋面和中尺度涡旋。
高分辨率波形可作为低分辨率相位偏差的判据（锁相差异 < 2°）。

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Jablonowski & Williamson (2006) *Q. J. R. Meteorol. Soc.* 132, 2943–2975](https://doi.org/10.1256/qj.06.12)
- [Ullrich et al. (2014) *Q. J. R. Meteorol. Soc.* 140, 1590–1602](https://doi.org/10.1002/qj.2241)
""",

    # ── cm ───────────────────────────────────────────────────────────────────

    "cm.720x360": r"""
## 碰撞偶极子（720×360）

**配置：** 720×360，5 层 hybrid（modon_l5），积分 100 天，Δt = 150 s，散度阻尼开启

![参考示意图：偶极子碰撞过程](/assets/ref_figures/ref_modon_collision.png)

这个测试想验证模式对**大气偶极子孤波（modon）**长时间演化的保真能力：
两个相向运动的偶极子相互碰撞，在准地转极限下考察数值方案的能量守恒与涡旋结构维持。

偶极子（modon）是准地转方程的一类非线性精确解，由一对等强度的气旋–反气旋涡旋组成，
以自身非线性传播速度沿直线运动。在大气中，偶极子结构与**阻塞高压**的维持机制密切相关。
两个偶极子碰撞是准地转湍流中涡旋相互作用的典型过程，碰撞结果
（弹性散射 vs 非弹性融合）取决于碰撞参数，对数值方案的能量和位涡守恒提出极高要求。

**初值怎么给的：**
- 两个 Larichev-Reznik 型正压偶极子，对称分布于赤道两侧
- 偶极子沿相反方向以各自的非线性传播速度平移

诊断指标：
- 100 天内总能量守恒偏差 < 0.1%
- 位涡（PV）守恒
- 碰撞后偶极子发生部分**弹性散射**（伴侣交换），继续传播
- 无数值耗散导致的明显振幅衰减
- 对称性应维持

### 参考文献
- [McWilliams (1980) *Dyn. Atmos. Oceans* 5, 43–66](https://doi.org/10.1016/0377-0265(80)90016-X)
""",

    # ── dcmip ────────────────────────────────────────────────────────────────

    "dcmip31": r"""
## DCMIP2016 测试 3.1 — 山脉诱发 Rossby 波

**配置：** 320×161，10 层 hybrid（dcmip31_l10），**非静力**，积分 1 小时，Δt = 2 s，行星缩比 X = 125

![参考示意图：缩小行星上的山脉激发波](/assets/ref_figures/ref_dcmip31.png)

这是 DCMIP2016 测试 3-1：在**缩小行星**（X = 125，地球半径缩为 1/125）上，
孤立山脉激发行星波，同时检验**非静力动力核**在压缩行星上的正确性。

行星缩小（small-planet scaling）使得 Rossby 变形半径 L_R = NH/(fX) 显著减小，
非静力效应（垂直加速度、声波–重力波耦合）在缩小行星上更加显著。
这是一种巧妙的测试策略：无需极高分辨率即可检验非静力动力核的正确性。
山脉激发的扰动同时包含**重力波**（短时间尺度）和**行星 Rossby 波**（长时间尺度），
是对模式多尺度模拟能力的综合考验。

**初值怎么给的：**
- 背景：均匀纬向风 u₀ = 20 m/s，等温大气 T = 300 K
- 山脉：高斯型孤立山（高度约 2000/X m），置于赤道
- 无扰动，仅山脉触发动力响应

非静力模式使用**垂直隐式–水平显式（HEVI）**时间积分方案，
垂直声波采用隐式求解（implicit_w_wgt）以放宽时间步长限制。

1 模拟小时（对应真实行星约 125 小时）内，按理应该出现山脉激发的行星 Rossby 波向东西两侧传播，
垂直结构与线性理论吻合，非静力效应（垂直加速度）可在结果中观测到。
参见 DCMIP2016 互比对论文 Fig. 11–14。

### 参考文献
- [Ullrich et al. (2017) *Geosci. Model Dev.* 10, 4477–4509](https://doi.org/10.5194/gmd-10-4477-2017)
""",

    # ── hs ───────────────────────────────────────────────────────────────────

    "hs.128x72": r"""
## Held-Suarez 气候态测试（128×72）

**配置：** 128×72（约 2.8°），26 层 hybrid（test_l26），长时间积分，Δt = 480 s，散度阻尼开启

![参考示意图：Held-Suarez 理想气候态](/assets/ref_figures/ref_held_suarez.png)

这是 Held & Suarez（1994）经典"简单 GCM"基准的**粗分辨率**版本：
用牛顿温度弛豫代替完整辐射、对流等物理参数化，
积分足够长时间后达到统计均衡气候态。
粗分辨率（~2.8°）主要用于快速验证大尺度环流特征和调试模式参数。

Held-Suarez 测试是大气动力核开发中最广泛使用的气候态基准。
通过移除所有复杂物理过程，仅保留牛顿冷却（弛豫至平衡温度场 T_eq）
和边界层 Rayleigh 摩擦（模拟近地面摩擦耗散），
使得不同动力核之间的差异完全源于离散方案本身。
统计均衡后应产生包括 Hadley 环流、Ferrel 环流和副热带急流在内的类地球大气环流结构。

**初值怎么给的：**
- 静止大气，全球均匀等温初始场
- 强迫：Newtonian relaxation（弛豫至平衡温度场）+ 边界层 Rayleigh 摩擦
- 小幅度随机扰动触发流动

纬向平均状态应与 Held & Suarez（1994）Fig. 2–4 吻合，我预期看到：
- 双急流结构，峰值约 ±40° 纬度，u_max ≈ 25–35 m/s
- 赤道对称的温度场
- 地表气压纬向平均约 1000 hPa，极区偏低约 5 hPa
- 粗分辨率下急流峰值可能偏弱 5–10%

### 参考文献
- [Held & Suarez (1994) *Bull. Amer. Meteor. Soc.* 75, 1825–1830](https://doi.org/10.1175/1520-0477(1994)075<1825:APFTIO>2.0.CO;2)
""",

    "hs.360x180": r"""
## Held-Suarez 气候态测试（360×180）

**配置：** 360×180，26 层 hybrid（test_l26），积分 1200 天（约 3.3 年），Δt = 300 s，散度阻尼开启

这是 Held & Suarez（1994）经典"简单 GCM"基准的**标准分辨率**版本：
1° 分辨率下可充分分辨中纬度瞬变涡旋活动，
积分 1200 天以确保达到完整的统计均衡。

在 1° 分辨率下，中纬度天气尺度涡旋（~1000 km 波长）可以被充分分辨，
涡旋热量和动量输送的统计特征应与更高分辨率的结果基本一致。
1200 天的积分时间允许丢弃前 200 天的 spin-up 过程，
使用后 1000 天的数据进行时间平均和方差分析。

**初值怎么给的：**
同 hs.128x72：静止大气 + Newtonian relaxation + Rayleigh 摩擦。

| 指标 | 参考值 |
|---|---|
| 急流峰值 | u_max ≈ 30 m/s at ±40° |
| 赤道温度 | T_eq ≈ 315 K |
| 瞬变涡旋动能（EKE） | 峰值在 45° 附近 |

### 参考文献
- [Held & Suarez (1994) *Bull. Amer. Meteor. Soc.* 75, 1825–1830](https://doi.org/10.1175/1520-0477(1994)075<1825:APFTIO>2.0.CO;2)
""",

    # ── mz ───────────────────────────────────────────────────────────────────

    "mz.180x90": r"""
## 斜压地形波测试（180×90）

**配置：** 180×90，30 层 hybrid（cam_l30），**静力**，积分 30 天，Δt = 600 s

![参考示意图：山脉激发 Rossby 波列](/assets/ref_figures/ref_mountain_wave.png)

这个测试想验证模式在解析纬向平衡背景流中被**孤立地形**强迫出
Rossby 波列的发展过程——对应 Jablonowski et al.（2008）NCAR ASP2008
测试集中的**斜压地形波（mountain-induced Rossby wave train）**算例。

当稳态斜压平衡流遭遇孤立山脉时，地表产生非零垂直速度扰动，
通过涡度方程激发向下游传播的 Rossby 波列。
初值已满足静力和地转平衡，因此任何下游出现的波列都来自地形强迫本身，
可以干净地检验数值框架对地形–动力耦合的保真度。

**初值怎么给的：**
- 背景：Jablonowski & Williamson（2006）干静力斜压稳态初值
  （纬向急流 u₀ ≈ 35 m/s，温度递减率 Γ = 0.005 K/m，满足热成风平衡）
- 地形：30°N, 90°E 处的高斯钟型山脉（h₀ = 2000 m，半宽 ~1500 km）
- 静力模式（无非静力垂直加速度项）

地形跟随坐标中的气压梯度力（PGF）采用参考态扣除法以减少截断误差。
静力模式下垂直动量方程被静力平衡关系 ∂p/∂z = −ρg 替代。

我预期看到：约第 5 天起在下游形成清晰的 Rossby 波列，
30 天内质量、能量、位涡拟能守恒偏差保持在可接受量级，
与 Jablonowski et al.（2008）给出的参考波列结构一致。

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Jablonowski & Williamson (2006) *Q. J. R. Meteorol. Soc.* 132, 2943–2975](https://doi.org/10.1256/qj.06.12)
""",

    # ── nh ───────────────────────────────────────────────────────────────────

    "nh_mz.360x180": r"""
## 非静力斜压地形波测试（360×180）

**配置：** 360×180，30 层 hybrid（cam_l30），**非静力**（pgf_scheme=ptb，implicit_w_wgt=1），
积分 5 天，Δt = 240 s，散度+涡度阻尼开启

与静力版本（`mz`）相同的 Jablonowski et al.（2008）地形强迫 Rossby 波列配置，
但这里开启了**非静力模式**，用以验证非静力动力核中垂直动量方程（dw/dt 项）
的正确实现。

非静力模式完整保留 Dw/Dt 项，使用半隐式时间积分方案
（implicit_w_wgt 控制隐式权重）来稳定处理快速垂直声波。
与静力版本对比同一算例，可以干净地暴露非静力项引入的离散误差
以及框架在大尺度 Rossby 波列背景上的数值稳定性。

**初值怎么给的：**
同 `mz.180x90`：Jablonowski & Williamson（2006）斜压稳态平衡流 +
30°N 处高斯型山脉（h₀ = 2000 m），但方程组完整保留垂直加速度项。

与静力解对比，非静力解在高频重力波区域应有可测偏差；
5 天内应无数值发散；下游 Rossby 波列相位与静力版本相近，
局地垂直速度场体现非静力修正。

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Jablonowski & Williamson (2006) *Q. J. R. Meteorol. Soc.* 132, 2943–2975](https://doi.org/10.1256/qj.06.12)
""",

    "lin97_static.100x5": r"""
## Lin (1997) 静态山地气压梯度误差测试（100×5）

**配置：** 100×5 水平网格，20 层 sigma，静力，周期边界；本仓库中将论文的二维 `x-z`
静态山地实验映射为**沿赤道的一条周期经向带**，便于直接用现有 GMCORE tools 运行和可视化。

对应论文：
[Lin (1997), *A finite-volume integration method for computing pressure gradient force in general vertical coordinates*](https://www.weather.gov/media/sti/nggps/Lin_Pressure_Gradient_Force_General_Vertical_Coordinates_QuartJRoyMetSoc_1997.pdf)

论文第一个数值实验是一个**纯静态评估**，目的不是看真实天气演变，而是隔离
terrain-following 坐标下的**伪气压梯度力（spurious PGF）**。
参数是：

- 半域宽 `Xmax = 2500 km`
- 高斯山高 `Hmax = 4 km`
- 山宽参数 `D = Xmax / 8`
- 常数直减率 `Γ = 20/3 K km^-1`
- 顶高 `ztop = 10.5 km`
- 水平分辨率 `Δx = 50 km`

论文里与这个 case 直接相关的是 **Fig.2–Fig.6**：

### Fig. 2 地形与地表压强

![Lin1997 Fig.2：地形与地表压强](/assets/ref_figures/ref_lin1997_fig2.png)

这张图给出高斯山体 `H(x)` 和由静力积分得到的地表气压。
山顶处气柱变短，所以地表压强出现对应低谷。
这张图回答的是：**初始静力平衡背景场是什么**。

### Fig. 3 位温等值线

![Lin1997 Fig.3：位温等值线](/assets/ref_figures/ref_lin1997_fig3.png)

这是常数直减率大气在 sigma 坐标下得到的位温结构。
等值线随山体一起弯折，说明虽然物理空间中是静态平衡，
但在地形跟随坐标里，离散 PGF 需要处理强烈倾斜的层面。
这张图回答的是：**误差会在哪种热力层结上暴露出来**。

### Fig. 4 误差收敛曲线

![Lin1997 Fig.4：平均绝对 PGF 误差随垂直分辨率变化](/assets/ref_figures/ref_lin1997_fig4.png)

这张图是论文最关键的定量结论：
纵轴是域平均绝对 PGF 误差，横轴是垂直层数 `N`。
圆点是 Lin 的有限体积方法，方块是 Arakawa-Suarez。
结论很直接：**有限体积 PGF 在所有分辨率上都更小，并且在低到中等垂直分辨率下优势最明显**。

### Fig. 5 Arakawa-Suarez 误差分布

![Lin1997 Fig.5：Arakawa-Suarez 误差分布](/assets/ref_figures/ref_lin1997_fig5.png)

这里展示 `N = 20` 时，传统 Arakawa-Suarez 方法算出来的伪 PGF 空间分布。
误差不仅集中在山附近，而且**在垂直方向分布较广**，
说明误差会更容易污染整层流场。

### Fig. 6 Lin97 有限体积误差分布

![Lin1997 Fig.6：Lin97 有限体积误差分布](/assets/ref_figures/ref_lin1997_fig6.png)

这是同样 `N = 20` 时有限体积方法的误差分布。
相较 Fig.5，误差显著减弱，并更集中在模型顶附近。
论文原文的核心解释是：**有限体积方法把误差压缩到了更局地、更容易识别的位置**。

### 这个 case 在 GMCORE 里怎么看

这个 case 不是拿来追求“有趣的流场”，而是拿来回答一个更硬的问题：
**地形跟随坐标下，当前 PGF 离散会不会把静态平衡场激发成假风和假垂直运动？**

对照论文图时，我建议重点看三件事：

1. 山顶上方是否快速长出非零 `u` 和 `omega`
2. 假信号是否主要集中在山附近和高层
3. 改变垂直层数后，误差是否沿 Fig.4 那样随 `N` 减小

如果后续要做更严格复现，可以继续把这个 case 扩展成论文那种
`N = 5, 10, 20, 40, 60, 80, 100` 的垂直分辨率扫描，
然后把 GMCORE 的均方或平均绝对 PGF 误差也画成收敛曲线，直接和 Fig.4 对比。

### 参考文献
- [Lin (1997) *Q. J. R. Meteorol. Soc.* 123, 1749–1762](https://www.weather.gov/media/sti/nggps/Lin_Pressure_Gradient_Force_General_Vertical_Coordinates_QuartJRoyMetSoc_1997.pdf)
""",

    # ── rh ───────────────────────────────────────────────────────────────────

    "rh.180x90": r"""
## 三维 Rossby-Haurwitz 波测试（180×90）

**配置：** 180×90，26 层 hybrid（test_l26），积分 90 天，Δt = 600 s，散度+涡度阻尼开启

![参考示意图：Rossby-Haurwitz 波数 4 结构](/assets/ref_figures/ref_rossby_haurwitz.png)

这是 Jablonowski et al.（2008）NCAR ASP2008 测试集中**三维 Rossby-Haurwitz 波**算例：
浅水 RH 波（Williamson et al. 1992 TC6）的三维扩展版。
我想看模式能否在**90 天长时间积分**中维持 RH 行波结构。
该测试对数值耗散极为敏感。

Rossby-Haurwitz 波是正压涡度方程在球面上的一类解析非线性行波解，
由 Haurwitz（1940）首先推导。注意：**浅水 RH 波向东传播，
而三维（斜压）RH 波向西传播**——这是三维扩展相对浅水版本的关键区别之一。
波数 n = 4 的解包含四个交替排列的高低压中心，以常速传播。
该行波在无耗散、无外力的条件下应无限期维持，
然而由于它不是原始方程（含非线性平流和多层耦合）的严格解，
在长时间积分中可能出现缓慢的结构演变——
这种演变的速率是评估数值方案精度的良好指标。

**初值怎么给的：**
- Jablonowski et al.（2008）三维 RH 解析初值：波数 4 扰动叠加在纬向背景流上
- 温度与气压廓线由静力与质量一致条件构造
- 这是解析给定的初始场，无需外部数据

诊断指标：
- 行波相速度：约 **0.125°/天** 向西
- 振幅守恒：衰减应 < 5% / 90 天
- 总能量和总位涡应保守
- 过多数值耗散会导致波形提前消散或相速度偏慢

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Williamson et al. (1992) *J. Comput. Phys.* 102, 211–224](https://doi.org/10.1016/S0021-9991(05)80016-6)
""",

    # ── ss ───────────────────────────────────────────────────────────────────

    "ss.180x90": r"""
## 斜压稳态地转流测试（180×90）

**配置：** 180×90，26 层 hybrid（test_l26），积分 30 天，Δt = 480 s，散度阻尼开启

![参考示意图：稳态均衡初始场](/assets/ref_figures/ref_steady_state.png)

这是 Jablonowski & Williamson（2006）稳态测试：
初始场为**解析均衡态**（u₀ = 35 m/s 纬向急流，T₀ = 288 K，Γ = 0.005 K/m），
精确满足热成风平衡。在无外强迫条件下，我预期模式在 30 天内**保持初始状态不变**。

热成风平衡是大气大尺度运动的基本约束：
f × ∂u/∂z = −(R/p) × ∂T/∂y

如果数值格式的离散化引入了对这一平衡的破坏
（例如气压梯度力的计算精度不足、或坐标变换引入的截断误差），
初始场将产生非物理的调整运动。
这种"虚假调整"的幅度直接反映了数值格式的**平衡态保持能力**。

**初值怎么给的：**
- 纬向风：由解析温度场通过热成风关系导出，峰值 ~35 m/s at σ ≈ 0.3
- 气压/温度：由 Γ = 5 K/km 递减率的解析廓线给出
- 无任何外部扰动

气压梯度力（PGF）采用参考态扣除法（ptb scheme），
这样做通过扣除等温参考大气来减少地形坐标中的截断误差，
对于此类均衡态保持测试尤为关键。

| 指标 | 判据 |
|---|---|
| 地表气压变化 | < 0.1 hPa（30 天） |
| 纬向风偏差 | < 0.1 m/s |
| 温度偏差 | < 0.1 K |

任何超出上述阈值的偏差均指示离散方案中存在非守恒项。

### 参考文献
- Jablonowski, C., P. H. Lauritzen, R. D. Nair, and M. A. Taylor (2008): Idealized test cases for the dynamical cores of Atmospheric General Circulation Models: A proposal for the NCAR ASP 2008 summer colloquium. *Tech. rep.*, University of Michigan & NCAR.
- [Jablonowski & Williamson (2006) *Q. J. R. Meteorol. Soc.* 132, 2943–2975](https://doi.org/10.1256/qj.06.12)
""",

    # ── swm ──────────────────────────────────────────────────────────────────

    "swm_sg.360x180": r"""
## 浅水方程稳态非线性地转流测试（360×180）

**配置：** 360×180，纯浅水方程，积分 12 天，Δt = 300 s

![参考示意图：浅水地转平衡](/assets/ref_figures/ref_shallow_water.png)

这是 Williamson et al.（1992）浅水方程测试集 **Test Case 2**：
初始场为精确纬向对称地转均衡态（速度场与位势场满足精确平衡），
我想看看浅水方程求解器能否在数值舍入误差范围内**维持该均衡**不变。

地转平衡 fu = −g ∂h/∂y 是旋转流体力学中的基本平衡态。
浅水方程是大气原始方程在垂直方向取深度平均后的简化形式，
保留了 Rossby 波、重力波和地转调整等关键动力过程。
这里我想看看离散格式是否引入了"离散地转失衡"
（discretization-induced geostrophic imbalance），
这种失衡会激发虚假的惯性重力波。

**初值怎么给的：**
- 纬向风：cos(θ) 型对称均匀急流
- 位势 gh：由地转平衡精确计算（无地形）

12 天内 gh 误差 ℓ₂ 应保持在 O(10⁻¹⁰) 量级（接近机器精度）。
若数值格式存在离散地转失衡，误差会随时间增长，12 天后可达 O(10⁻⁴) 量级（不良格式）。

### 参考文献
- [Williamson et al. (1992) *J. Comput. Phys.* 102, 211–224](https://doi.org/10.1016/S0021-9991(05)80016-6)
""",

    # ── tc ───────────────────────────────────────────────────────────────────

    "tc.360x180": r"""
## 赤道气旋理想模拟（360×180）

**配置：** 360×180，30 层 hybrid（cam_l30），物理参数化：simple_physics v6，
积分 10 天，散度阻尼开启

![参考示意图：赤道气旋结构](/assets/ref_figures/ref_tropical_cyclone.png)

这是 Reed & Jablonowski（2011）赤道气旋理想化基准的粗分辨率版本。
在 1° 分辨率下，我想看模式能否产生可辨识的气旋结构，
虽然眼墙和强度细节受分辨率限制。

赤道气旋（TC）是热带海洋上最强烈的天气系统，由赤道附近的弱涡旋在湿物理过程驱动下逐步增强而成。
其能量来源于海表蒸发–对流释放的潜热（WISHE 机制）。
理想化 TC 测试使用简单物理参数化（边界层方案 + 大尺度凝结 + 地表通量），
在可控条件下检验动力核对轴对称暖核涡旋发展的模拟能力。
1° 分辨率能捕捉 TC 的大尺度结构，但眼墙对流需要更高分辨率
（如 tc.720x360 或 tc.1440x720）才能充分分辨。

**初值怎么给的：**
- 背景：Jordan（1958）平均热带探空廓线（温度、湿度），静止大气
- 扰动：10°N 处轴对称旋转风场（最大风速 ≈ 8 m/s，Rankine 涡型）
- 边界条件：固定海温 SST = 29°C（302 K）

10 天后气旋应发展但强度弱于高分辨率版本，我预期：
- 近地面最大风速约 40–60 m/s（受分辨率限制）
- 中心最低气压约 950–970 hPa
- 暖核结构可辨识但偏弱

### 参考文献
- [Reed & Jablonowski (2011) *Mon. Wea. Rev.* 139, 689–710](https://doi.org/10.1175/2010MWR3488.1)
""",

    # ── swm_rh ───────────────────────────────────────────────────────────────

    "swm_rh.360x180": r"""
## 浅水方程 Rossby-Haurwitz 波测试（360×180）

**配置：** 360×180（1°×1°），单层浅水方程，积分 14 天，Δt = 300 s，位涡平流 5 阶迎风

![Rossby-Haurwitz 波数 4 结构示意图](/assets/ref_figures/ref_rossby_haurwitz.png)

---

## 一、测试概述

Williamson et al.（1992）浅水方程标准测试集 **Test Case 6**。
初始场为 Haurwitz（1940）给出的 **波数 4 Rossby-Haurwitz 行波解析解**，
在无粘、无外力条件下应以恒定角速度向东传播，波形保持不变。

这个测试是对动力核以下能力的综合评估：
- **涡度-散度形式离散**的精度
- **科里奥利力**和**气压梯度力**的平衡维持
- **长时间积分**中总能量和总位涡拟能的守恒性

值得注意的是，Thuburn & Li（2000）指出波数 4 的 Rossby-Haurwitz 波在原始方程下
并非严格稳定解——它在足够长的积分后会因非线性不稳定性而破碎。
因此，14 天积分是国际通用的对比时间节点。

---

## 二、控制方程：球面浅水方程组

GMCORE 浅水模式求解的是旋转球面上的浅水方程组，采用**涡度-散度-动能**形式——矢量不变形式。
相比原始形式，这种写法天然保证了能量和位涡的良好守恒性。

### 2.1 动量方程（涡度-动能形式）

原始动量方程为：

$$\frac{\partial \mathbf{v}}{\partial t} = -f\mathbf{k}\times\mathbf{v} - \nabla(g h) - \frac{1}{2}\nabla|\mathbf{v}|^2 + q \cdot \mathbf{k}\times(h\mathbf{v})$$

GMCORE 将其改写为矢量不变形式，在经纬度球坐标 (λ, φ) 中展开为：

**纬向动量方程：**

$$\frac{\partial u}{\partial t} = \underbrace{q \cdot F_y}_{\text{科里奥利+涡度}} - \underbrace{\frac{\partial K}{\partial x}}_{\text{动能梯度}} - \underbrace{\frac{\partial (gH)}{\partial x}}_{\text{气压梯度力}}$$

**经向动量方程：**

$$\frac{\partial v}{\partial t} = \underbrace{-q \cdot F_x}_{\text{科里奥利+涡度}} - \underbrace{\frac{\partial K}{\partial y}}_{\text{动能梯度}} - \underbrace{\frac{\partial (gH)}{\partial y}}_{\text{气压梯度力}}$$

其中各物理量定义为：

| 符号 | 含义 | 定义 |
|------|------|------|
| **q** | 位涡（Potential Vorticity） | q = (ζ + f) / h |
| **ζ** | 相对涡度 | ζ = ∂v/∂x − ∂u/∂y |
| **f** | 科里奥利参数 | f = 2Ω sinφ |
| **K** | 动能 | K = (u² + v²) / 2 |
| **gH** | 位势高度 | gz 场 |
| **Fₓ, Fy** | 质量通量 | Fₓ = h·u, Fy = h·v |

将科里奥利力和相对涡度统一为位涡通量项 q×(hv)，
使得方程天然保证总能量和总位涡拟能在适当离散下守恒。

### 2.2 连续方程（高度/质量方程）

$$\frac{\partial (gH)}{\partial t} = -g \nabla \cdot (H \mathbf{v})$$

即位势高度的变化率等于质量通量散度乘以重力加速度。
这是质量守恒的直接表达。

### 2.3 方程组总结

浅水方程组共 **3 个预报变量**（u, v, gH），**3 个方程**：

```
┌──────────────────────────────────────────────────┐
│  ∂u/∂t  =  +q·Fy  − ∂K/∂x  − ∂(gH)/∂x         │  ← 纬向动量
│  ∂v/∂t  =  −q·Fx  − ∂K/∂y  − ∂(gH)/∂y         │  ← 经向动量
│  ∂(gH)/∂t = −g·∇·(Hv)                           │  ← 连续方程
└──────────────────────────────────────────────────┘
```

---

## 三、空间离散：方程到代码的对应

GMCORE 采用 **Arakawa C 网格**（交错网格）离散：
- **u** 存储在经度半格点（i+1/2, j）
- **v** 存储在纬度半格点（i, j+1/2）
- **gH** 存储在整格点（i, j）

下面我逐项整理一下方程右端项与代码的对应关系。

### 3.1 气压梯度力（PGF）

**数学形式**：−∂(gH)/∂x 和 −∂(gH)/∂y

**代码变量 → 数学符号**：

| 代码变量 | 数学符号 | 含义 | 网格位置 |
|----------|---------|------|---------|
| `gz(i,j)` | gH | 位势高度 = 重力加速度 × 流体层厚度 | 整格点 (i,j) |
| `dudt(i,j)` | ∂u/∂t | 纬向速度的时间变化率 | 半格点 (i+½,j) |
| `dvdt(i,j)` | ∂v/∂t | 经向速度的时间变化率 | 半格点 (i,j+½) |
| `de_lon(j)` | a·cosφ·Δλ | 纬向网格间距（球面弧长），随纬度变化 | — |
| `de_lat(j)` | a·Δφ | 经向网格间距（球面弧长），各纬度相同 | — |

**代码实现**（`src/dynamics/pgf/pgf_swm_mod.F90`）：

```fortran
! ---- 纬向分量 du/dt += -∂(gz)/∂x ----
do j = ...; do i = ...
  dudt(i,j) = dudt(i,j) - (gz(i+1,j) - gz(i,j)) / de_lon(j)
end do; end do

! ---- 经向分量 dv/dt += -∂(gz)/∂y ----
do j = ...; do i = ...
  dvdt(i,j) = dvdt(i,j) - (gz(i,j+1) - gz(i,j)) / de_lat(j)
end do; end do
```

这里的实现是最简单的**二阶中心差分**。
在 C 网格上，gz 位于整格点 (i, j) 和 (i+1, j)，差分结果自然落在半格点 (i+½, j) 上——
正好是 dudt 存储的位置。这种"差分天然对齐"是交错网格的核心优势，
不需要额外的插值就能得到二阶精度的梯度。

### 3.2 动能梯度

**数学形式**：−∂K/∂x 和 −∂K/∂y

**代码变量 → 数学符号**：

| 代码变量 | 数学符号 | 含义 | 计算方式 |
|----------|---------|------|---------|
| `ke(i,j)` | K = (u²+v²)/2 | 动能 | 在整格点上由周围 u, v 插值后平方求和 |
| `dudt(i,j)` | ∂u/∂t | 纬向速度的时间变化率（累加） | — |
| `dvdt(i,j)` | ∂v/∂t | 经向速度的时间变化率（累加） | — |

**代码实现**（`src/dynamics/operators_mod.F90: calc_grad_ke`）：

```fortran
! ---- 纬向分量 du/dt += -∂K/∂x ----
do j = ...; do i = ...
  dudt(i,j) = dudt(i,j) - (ke(i+1,j) - ke(i,j)) / de_lon(j)
end do; end do

! ---- 经向分量 dv/dt += -∂K/∂y ----
do j = ...; do i = ...
  dvdt(i,j) = dvdt(i,j) - (ke(i,j+1) - ke(i,j)) / de_lat(j)
end do; end do
```

与 PGF 完全相同的差分模板。
注意 `dudt`、`dvdt` 是**累加**的——PGF 和动能梯度的贡献依次叠加到同一个变量上，
最终 dudt 包含了动量方程右端所有项的总和。

### 3.3 科里奥利力 + 涡度通量（位涡项）

**数学形式**：旋转浅水方程动量方程的矢量不变形式将科里奥利力和相对涡度合并为同一项：

$$\frac{\partial u}{\partial t}\bigg|_{\text{vor}} = +q \cdot F_y, \qquad \frac{\partial v}{\partial t}\bigg|_{\text{vor}} = -q \cdot F_x$$

其中 $q = (\zeta + f)/h$ 是绝对位涡，$F = h\mathbf{v}$ 是质量通量。
这一写法将"相对涡度 × 速度"和"科里奥利参数 × 速度"统一成一个算子，
是矢量不变形式区别于原始形式的核心。

---

#### 第一步：涡度 ζ 的计算（Stokes 定理离散）

**文件**：`src/meshes/latlon/latlon_operators_mod.F90: curl_operator`

C 网格上，u 分布在纬向边，v 分布在经向边——它们恰好构成角点（vorticity point）周围的封闭环路，
所以涡度天然定义在角点，Stokes 定理将面积分（涡度）转化为围道积分（速度环流）。

**代码实现**：

```fortran
! vor(i,j) 在角点 (i+½, j+½)
! 离散 Stokes 定理：ζ = 环流 / 面积
vor%d(i,j,k) = (
  u_lon%d(i  ,j  ,k) * de_lon(j  )   &  ! 下边 u(i+½,j) 向右 × 边长
- u_lon%d(i  ,j+1,k) * de_lon(j+1)   &  ! 上边 u(i+½,j+1) 向左 × 边长（符号反）
+ v_lat%d(i+1,j  ,k) * de_lat(j  )   &  ! 右边 v(i+1,j+½) 向上 × 边长
- v_lat%d(i  ,j  ,k) * de_lat(j  )   &  ! 左边 v(i,j+½) 向下 × 边长（符号反）
) / area_vtx(j)
```

| 代码变量 | 数学符号 | 定义 | 来源 |
|----------|---------|------|------|
| `u_lon%d(i,j,k)` | u(i+½,j) | 纬向速度（半格点） | `block%dstate%u_lon` |
| `v_lat%d(i,j,k)` | v(i,j+½) | 经向速度（半格点） | `block%dstate%v_lat` |
| `de_lon(j)` | a·cosφⱼ·Δλ | 纬向对偶边长（球面弧长） | `mesh%de_lon(j)` |
| `de_lat(j)` | a·Δφ | 经向对偶边长（常数） | `mesh%de_lat(j)` |
| `area_vtx(j)` | le_lat(j)·de_lat(j) | 角点对偶格元面积 | `mesh%area_vtx(j)` |
| `vor%d(i,j,k)` | ζ(i+½,j+½) | 相对涡度，存于角点 | `block%aux%vor` |

`de_lon` 随纬度变化是因为球面上纬向边长为 a·cosφ·Δλ，高纬度缩短。
`de_lat = a·Δφ` 是经向间距，在均匀网格上是常数。
`area_vtx(j) = le_lat(j) × de_lat(j)` = (a·cosφ_{j+½}·Δλ) × (a·Δφ) ——角点格元的实际球面面积。

---

#### 第二步：层厚 h 插值到角点（dmg_vtx）

**文件**：`src/dynamics/operators_mod.F90: calc_dmg`

在浅水模式中（无地形），层厚 h 由位势高度场诊断：

```fortran
! 浅水模式，gzs = 0（平坦地形）
dmg%d(i,j,1) = (gz%d(i,j,1) - gzs%d(i,j)) / g   ! h = (gH - gHs)/g = H
```

然后通过双线性插值得到角点处的层厚：

```fortran
dmg_vtx%d(i,j,k) = 0.25 * (dmg%d(i,j,k) + dmg%d(i+1,j,k) + dmg%d(i,j+1,k) + dmg%d(i+1,j+1,k))
```

| 代码变量 | 数学符号 | 含义 |
|----------|---------|------|
| `gz%d(i,j,1)` | gH | 位势高度 = g × 流体层顶高度 |
| `gzs%d(i,j)` | gHs = 0 | 地表位势（浅水测试中置零） |
| `dmg%d(i,j,1)` | h(i,j) | 整格点处的流体层厚 |
| `dmg_vtx%d(i,j,k)` | h(i+½,j+½) | 角点处的层厚（四邻居平均） |

需要把 h 插值到角点，是因为位涡 q = (ζ + f)/h，分子 ζ 和分母 h 必须在同一位置（角点）计算，否则除法无意义。

---

#### 第三步：位涡 q 的计算

**文件**：`src/dynamics/operators_mod.F90: calc_pv`

```fortran
! pv(i,j) 在角点 (i+½, j+½)
pv%d(i,j,k) = (vor%d(i,j,k) + mesh%f_lat(j)) / dmg_vtx%d(i,j,k)
```

| 代码变量 | 数学符号 | 定义 | 来源 |
|----------|---------|------|------|
| `vor%d(i,j,k)` | ζ(i+½,j+½) | 相对涡度（上一步计算） | `block%aux%vor` |
| `mesh%f_lat(j)` | f(j+½) = 2Ω sin(φ_{j+½}) | 半格点处的科里奥利参数 | `latlon_mesh_mod:261`：`f_lat(j) = 2*omega*half_sin_lat(j)` |
| `dmg_vtx%d(i,j,k)` | h(i+½,j+½) | 角点层厚（上一步插值） | `block%aux%dmg_vtx` |
| `pv%d(i,j,k)` | q(i+½,j+½) | 绝对位涡 = (ζ+f)/h | `block%aux%pv` |

这里用 `f_lat` 而非 `f_lon`，是因为科里奥利参数在角点处取 `f_lat(j) = 2Ω sin(φ_{j+½})`，
对应角点的半格点纬度，`f_lon(j)` 是整格点纬度处的值，两者不同。

q = (ζ + f)/h 是守恒量，是因为对理想流体，浅水位涡方程为 Dq/Dt = 0，
即沿流体粒子轨迹 q 保持不变——这是旋转浅水系统最深刻的守恒性质，
后续数值方案都要围绕它的守恒性来设计。

---

#### 第四步：位涡插值到速度格点

**文件**：`src/dynamics/operators_mod.F90: interp_pv_midpoint`（或迎风格式）

q 定义在角点 (i+½, j+½)，但动量方程的 Coriolis 项需要在速度格点上计算。
GMCORE 将 q 分别插值到 u 点和 v 点：

```fortran
! pv_lon(i,j) —— q 插值到 u 点 (i+½, j)
! 沿纬度方向平均：上下两个角点的算术平均
pv_lon%d(i,j,k) = 0.5 * (pv%d(i,j,k) + pv%d(i,j-1,k))
!                         ↑角点(i+½,j+½)  ↑角点(i+½,j-½)

! pv_lat(i,j) —— q 插值到 v 点 (i, j+½)
! 沿经度方向平均：左右两个角点的算术平均
pv_lat%d(i,j,k) = 0.5 * (pv%d(i-1,j,k) + pv%d(i,j,k))
!                         ↑角点(i-½,j+½)  ↑角点(i+½,j+½)
```

| 变量 | 位置 | 插值方向 | 物理意义 |
|------|------|---------|---------|
| `pv_lon(i,j)` | u 点 (i+½, j) | 沿纬度平均上下两角点 | u 方程所用的 q，与 mfy 耦合 |
| `pv_lat(i,j)` | v 点 (i, j+½) | 沿经度平均左右两角点 | v 方程所用的 q，与 mfx 耦合 |

这里是最简单的中点插值（迎风格式关闭时）。浅水测试开启 5 阶迎风位涡平流时，
会改用 `upwind5` 等高阶格式替代这两行，以控制数值扩散。

---

#### 第五步：质量通量 F = h·v

**文件**：`src/dynamics/operators_mod.F90: calc_mf`

```fortran
! mfx_lon(i,j) —— 纬向质量通量，在 u 点 (i+½, j)
mfx_lon%d(i,j,k) = dmg_lon%d(i,j,k) * u_lon%d(i,j,k)
!                   ↑ h 插值到 u 点     ↑ 纬向速度

! mfy_lat(i,j) —— 经向质量通量，在 v 点 (i, j+½)
mfy_lat%d(i,j,k) = dmg_lat%d(i,j,k) * v_lat%d(i,j,k)
!                   ↑ h 插值到 v 点     ↑ 经向速度
```

| 变量 | 位置 | 含义 |
|------|------|------|
| `dmg_lon(i,j)` | u 点 (i+½,j) | h 在 u 点处（东西邻格元平均） |
| `dmg_lat(i,j)` | v 点 (i,j+½) | h 在 v 点处（南北邻格元平均） |
| `mfx_lon(i,j)` | u 点 (i+½,j) | Fₓ = h·u，纬向质量通量 |
| `mfy_lat(i,j)` | v 点 (i,j+½) | Fy = h·v，经向质量通量 |

---

#### 第六步：Arakawa 守恒插值——为什么是 `(pv_lat + pv_lon) × 0.5`

**文件**：`src/dynamics/operators_mod.F90: calc_coriolis`

这是整个动力核中离散精度最微妙的地方。完整代码：

```fortran
! dvdt(i,j) 在 v 点 (i, j+½)
do j = mesh%half_jds, mesh%half_jde        ! j 是半格点纬度索引
  do i = mesh%full_ids, mesh%full_ide      ! i 是整格点经度索引
    tmp = - (
      mesh%tg_wgt_lat(1,j) * (
        mfx_lon%d(i-1, j  , k) * (pv_lat%d(i,j,k) + pv_lon%d(i-1, j  , k)) +
        mfx_lon%d(i  , j  , k) * (pv_lat%d(i,j,k) + pv_lon%d(i  , j  , k))
      ) +
      mesh%tg_wgt_lat(2,j) * (
        mfx_lon%d(i-1, j+1, k) * (pv_lat%d(i,j,k) + pv_lon%d(i-1, j+1, k)) +
        mfx_lon%d(i  , j+1, k) * (pv_lat%d(i,j,k) + pv_lon%d(i  , j+1, k))
      )
    ) * 0.5
    dvdt%d(i,j,k) = dvdt%d(i,j,k) + tmp
  end do
end do
```

**几何布局**（以 v 点 (i, j+½) 为中心）：

```
角点×(i-½,j+½)      角点×(i+½,j+½)
       │    ↑ pv_lat(i,j) = 左右两角点平均，在 v 点本身 ↑     │
  mfx(i-1,j+1)    v点(i,j+½)←dvdt在此    mfx(i,j+1)
       │                   ×                              │
                    ← tg_wgt_lat(2,j) 这一行 →
       │                                                  │
  mfx(i-1,j)                                   mfx(i,j)
       │                                                  │
                    ← tg_wgt_lat(1,j) 这一行 →
角点×(i-½,j-½)      角点×(i+½,j-½)
```

**为什么是 `(pv_lat + pv_lon)`，而非直接用一个 q**：

以 mfx_lon(i,j) 为例——它位于 u 点 (i+½, j)，周围有两个角点：

- 上方角点 (i+½, j+½)：即 `pv(i,j)`
- 下方角点 (i+½, j-½)：即 `pv(i,j-1)`

它们的平均正好是 `pv_lon(i,j) = 0.5*(pv(i,j) + pv(i,j-1))`——这是"与 mfx 相邻"的 q。

同时，v 点 (i, j+½) 左右两侧的角点平均是 `pv_lat(i,j) = 0.5*(pv(i-1,j) + pv(i,j))`——这是"与 dvdt 相邻"的 q。

展开 `(pv_lat + pv_lon) * 0.5`：

$$\frac{1}{2}\left[\underbrace{\frac{pv(i-1,j)+pv(i,j)}{2}}_{\text{与 v 点相邻}} + \underbrace{\frac{pv(i,j)+pv(i,j-1)}{2}}_{\text{与此 mfx 相邻}}\right] = \frac{1}{4}\left[pv(i-1,j) + 2\cdot pv(i,j) + pv(i,j-1)\right]$$

**共享角点 pv(i,j)（同时与 mfx 和 dvdt 相邻）的权重是 2，其余角点权重是 1。**
这种不均匀权重正是 Arakawa & Lamb (1981) 守恒方案的核心。

Arakawa（1966）证明了这个加权方式能同时满足总能量和总拟能守恒：

| 守恒量 | 条件 | 物理含义 |
|--------|------|---------|
| 总能量 E = ∫(K+gH)dA | Σ[u·(∂u/∂t)_cor + v·(∂v/∂t)_cor] = 0 | 科里奥利力不做功 |
| 总拟能 Z = ∫q²h dA | Σ q·(∂q/∂t)_advect = 0 | 非线性项不产生拟能 |

两个条件都要求特定的"望远镜求和"（telescoping sum）成立。
共享角点权重 2 使得每个角点 q 在 u 方向和 v 方向的贡献以**相反符号**出现，
对速度求和（能量）时抵消，对 q 本身求和（拟能）时同样抵消——两个守恒性质同时成立。

对比两种退化方案：只用 `pv_lon`（不加 `pv_lat`）→ 仅守恒拟能；
只用 `pv_lat`（不加 `pv_lon`）→ 仅守恒能量。Arakawa 的贡献是证明了两者的**线性组合**可以同时满足。

---

#### 第七步：tg_wgt 权重——球面几何修正

**文件**：`src/meshes/latlon/latlon_mesh_mod.F90:264-272`

```fortran
! tg_wgt_lat：用于 dvdt（v 方程），关联纬向质量通量 mfx
tg_wgt_lat(1,j) = le_lon(j  ) / de_lat(j) * 0.25   ! 下方 mfx 行的权重
tg_wgt_lat(2,j) = le_lon(j+1) / de_lat(j) * 0.25   ! 上方 mfx 行的权重

! tg_wgt_lon：用于 dudt（u 方程），关联经向质量通量 mfy
tg_wgt_lon(1,j) = le_lat(j-1) / de_lon(j) * 0.25   ! 下方 mfy 列的权重
tg_wgt_lon(2,j) = le_lat(j  ) / de_lon(j) * 0.25   ! 上方 mfy 列的权重
```

| 变量 | 定义 | 数值（地球，Δλ=1°，Δφ=1°） |
|------|------|--------------------------|
| `le_lon(j)` = a·Δφ | 经向 primal 边长（常数） | 约 111 km |
| `de_lat(j)` = a·Δφ | v 点间距（经向 dual 边，常数） | 约 111 km |
| `le_lat(j)` = a·cosφ_{j+½}·Δλ | 纬向 primal 边长（随纬度缩短） | 赤道 111 km，60°N 约 56 km |
| `de_lon(j)` = a·cosφⱼ·Δλ | u 点间距（纬向 dual 边） | 同上，随纬度变 |

`tg_wgt_lat = le_lon/de_lat * 0.25`，因为 `le_lon = de_lat = a·Δφ`（常数），
所以 `tg_wgt_lat(1,j) = tg_wgt_lat(2,j) = 0.25`，与纬度无关。

而 `tg_wgt_lon = le_lat/de_lon * 0.25`，两者都含 cosφ 但取不同纬度：
`le_lat(j-1) = a·cos(φ_{j-½})·Δλ` vs `de_lon(j) = a·cos(φⱼ)·Δλ`，
比值略偏离 1，是对球面格元非矩形性的修正。

**完整变量一览表**：

| 代码变量 | 数学符号 | 位置 | 来源/计算 |
|----------|---------|------|----------|
| `vor%d(i,j,k)` | ζ(i+½,j+½) | 角点 | `curl_operator`（Stokes 定理） |
| `mesh%f_lat(j)` | f(j+½) = 2Ω sin φ_{j+½} | 角点（半格点纬度） | `latlon_mesh_mod`，运行时由 `omega` 计算 |
| `dmg_vtx%d(i,j,k)` | h(i+½,j+½) | 角点 | `dmg` 四邻居平均 |
| `pv%d(i,j,k)` | q(i+½,j+½) | 角点 | `(vor + f_lat) / dmg_vtx` |
| `pv_lon%d(i,j,k)` | q̄(i+½,j) | u 点 | `0.5*(pv(i,j) + pv(i,j-1))` |
| `pv_lat%d(i,j,k)` | q̄(i,j+½) | v 点 | `0.5*(pv(i-1,j) + pv(i,j))` |
| `mfx_lon%d(i,j,k)` | Fₓ(i+½,j) | u 点 | `dmg_lon × u_lon` |
| `mfy_lat%d(i,j,k)` | Fy(i,j+½) | v 点 | `dmg_lat × v_lat` |
| `tg_wgt_lat(1:2,j)` | w₁,w₂ | — | `le_lon / de_lat * 0.25`，纬度无关 |
| `tg_wgt_lon(1:2,j)` | w₁,w₂ | — | `le_lat / de_lon * 0.25`，随纬度微变 |

### 3.4 连续方程

**数学形式**：∂(gH)/∂t = −g · ∇·(Hv)

**代码变量 → 数学符号**：

| 代码变量 | 数学符号 | 含义 |
|----------|---------|------|
| `dgzdt(i,j)` | ∂(gH)/∂t | 位势高度的时间变化率 |
| `dmf(i,j)` | ∇·(Hv) | 质量通量散度 = ∂(hu)/∂x + ∂(hv)/∂y |
| `g` | g = 9.80616 m/s² | 重力加速度常数 |

**代码实现**（`src/dynamics/gmcore_mod.F90: space_operators`）：

```fortran
dgzdt(i,j,k) = -dmf(i,j,k) * g
```

`dmf` 是质量通量散度 ∇·(Hv)，由 `calc_grad_mf` 计算质量通量
（Fₓ = h·u, Fy = h·v），再由 `div_operator` 求散度。
整个连续方程在代码中就是这一行乘法——因为散度计算已经被封装在前序步骤中。
质量通量的净流出（散度 > 0）导致本地位势高度下降，物理上非常直观。

---

## 四、时间积分方案

### 4.1 前推后调技术（Forward-Backward）

GMCORE 不是将所有方程同时推进，而是使用**前推后调（forward-backward）**分裂：

```
Step 1（Forward Pass）：
  用当前时刻的 u, v 计算质量通量散度
  → 更新 gH（连续方程）

Step 2（Backward Pass）：
  用刚刚更新的 gH（最新值！）计算 PGF
  → 更新 u, v（动量方程）
```

先推高度场，再用新的高度场来调整速度。
这等价于对快波（重力波）做半隐式处理，显著提高了时间步长的稳定性上限。

### 4.2 PC2 时间积分

在前推后调的基础上，GMCORE 默认采用 **PC2（Predict-Correct 2 阶）** 方案：

```
Substep 1：  state_new  = state_old + (Δt/2) × F(state_old)     ← 预测
Substep 2：  state_tmp  = state_old + (Δt/2) × F(state_new)     ← 修正
Substep 3：  state_new  = state_old +  Δt    × F(state_tmp)     ← 最终
```

**代码变量 → 数学含义**：

| 代码变量 | 含义 |
|----------|------|
| `dstate(old)` | 当前时刻的状态量 (u, v, gH)ⁿ |
| `dstate(new)` | 下一时刻的状态量 (u, v, gH)ⁿ⁺¹ |
| `dstate(3)` | 中间临时状态（用于修正步） |
| `dtend` | 时间倾向量 (∂u/∂t, ∂v/∂t, ∂gH/∂t) |
| `dt` | 时间步长 Δt（本例 300 s） |
| `space_operators` | 计算方程右端项的函数指针 → 即上面第三节所有算子 |

代码实现极为简洁（`src/dynamics/time_schemes_mod.F90`）：

```fortran
subroutine pc2(space_operators, block, old, new, dt)
  ! Substep 1: 预测 — 用 old 状态算右端，步进半步到 new
  call step(..., dstate(old), dstate(old), dstate(new), dtend, dt/2, 1)
  ! Substep 2: 修正 — 用 new 状态算右端，步进半步到 tmp(3)
  call step(..., dstate(old), dstate(new), dstate(3  ), dtend, dt/2, 2)
  ! Substep 3: 最终 — 用 tmp(3) 算右端，步进整步到 new
  call step(..., dstate(old), dstate(3  ), dstate(new), dtend, dt  , 3)
end subroutine pc2
```

PC2 具有二阶精度，且因为多次修正而具有良好的相位误差特性——
这对于 Rossby-Haurwitz 波的相速度模拟非常重要。

**`update_state` 中的实际更新**（每个 `step` 最终执行的操作）：

| 代码 | 数学含义 |
|------|---------|
| `u_new(i,j) = u_old(i,j) + dt * dudt(i,j)` | uⁿ⁺¹ = uⁿ + Δt · (∂u/∂t) |
| `v_new(i,j) = v_old(i,j) + dt * dvdt(i,j)` | vⁿ⁺¹ = vⁿ + Δt · (∂v/∂t) |
| `gz_new(i,j) = gz_old(i,j) + dt * dgzdt(i,j)` | (gH)ⁿ⁺¹ = (gH)ⁿ + Δt · ∂(gH)/∂t |

这就是 Euler 前差的基本形式，PC2 通过三次子步骤使其达到二阶精度。

---

## 五、初始条件：Rossby-Haurwitz 波解析解

Haurwitz（1940）给出的球面正压涡度方程的非线性行波解。
入口函数为 `src/tests/swm/rossby_haurwitz_wave_test_mod.F90` 中的
`rossby_haurwitz_wave_test_set_ic(block)`。

### 5.1 参数来源

| 代码符号 | 数学符号 | 值 | 来源 |
|----------|---------|-----|------|
| `R` | R | 4.0 | 模块级 `parameter`（编译期常量） |
| `omg` | ω | 7.848×10⁻⁶ s⁻¹ | 模块级 `parameter`（编译期常量） |
| `gz0` | gH₀ | `8.0d3 * g` ≈ 78449 m²/s² | 运行时计算，`g` 来自 `const_mod` |
| `omega` | Ω | 7.2921×10⁻⁵ s⁻¹ | `const_mod`，地球行星参数运行时赋值 |
| `radius` | a | 6.37122×10⁶ m | `const_mod`，地球行星参数运行时赋值 |
| `g` | g | 9.80616 m/s² | `const_mod`，地球行星参数运行时赋值 |

`omega`、`radius`、`g` 在 `const_mod.F90` 中声明为普通变量（非 parameter），
在模型初始化时由行星类型（Earth/Mars）决定其运行时值。

地形场在初值函数中被显式置零（平坦下垫面假设）：

```fortran
gzs%d = 0.0   ! block%static%gzs：地表位势，浅水测试无地形
```

### 5.2 速度场

$$u = a\omega\left(\cos\varphi + R\cos^{R-1}\varphi \sin^2\varphi \cos R\lambda - \cos^{R+1}\varphi \cos R\lambda\right)$$

$$v = -a\omega R \cos^{R-1}\varphi \sin\varphi \sin R\lambda$$

### 5.3 位势高度场

$$gH = gH_0 + a^2 \left[ A(\varphi) + B(\varphi)\cos R\lambda + C(\varphi)\cos 2R\lambda \right]$$

其中：

$$A(\varphi) = \frac{\omega}{2}(2\Omega + \omega)\cos^2\varphi + \frac{\omega^2}{4}\left[(R+1)\cos^{2R+2}\varphi + (2R^2-R-2)\cos^{2R}\varphi - 2R^2\cos^{2R-2}\varphi\right]$$

$$B(\varphi) = \frac{2(\Omega+\omega)\omega}{(R+1)(R+2)}\cos^R\varphi\left[(R^2+2R+2) - (R+1)^2\cos^2\varphi\right]$$

$$C(\varphi) = \frac{\omega^2}{4}\cos^{2R}\varphi\left[(R+1)\cos^2\varphi - (R+2)\right]$$

### 5.4 源码逐行对照

以下为 `rossby_haurwitz_wave_test_set_ic` 的实际代码，带注释说明每项来源。

**纬向风速 u**（C 网格半格点：`half_lon(i)` × `full_lat(j)`）：

```fortran
! 循环范围：j ∈ full_jds:full_jde，i ∈ half_ids:half_ide
! 经度取 half_lon（u 存储在 i+½ 位置）
lon = mesh%half_lon(i)
cos_lat = mesh%full_cos_lat(j)   ! cosφ
sin_lat = mesh%full_sin_lat(j)   ! sinφ

a = cos_lat                                             ! 第一项：cosφ
b = R * cos_lat**(R - 1) * sin_lat**2 * cos(R * lon)   ! 第二项：R cos³φ sin²φ cos4λ
c = cos_lat**(R + 1) * cos(R * lon)                    ! 第三项：cos⁵φ cos4λ
u%d(i,j,1) = radius * omg * (a + b - c)               ! u = aω(cosφ + … - …)
```

**经向风速 v**（C 网格半格点：`full_lon(i)` × `half_lat(j)`）：

```fortran
! 循环范围：j ∈ half_jds:half_jde，i ∈ full_ids:full_ide
! 经度取 full_lon，纬度取 half（v 存储在 j+½ 位置）
lon = mesh%full_lon(i)
cos_lat = mesh%half_cos_lat(j)
sin_lat = mesh%half_sin_lat(j)

! 局部变量 a 此时含义：R cos^(R-1)φ sinφ sin4λ
a = R * cos_lat**(R - 1) * sin_lat * sin(R * lon)
v%d(i,j,1) = - radius * omg * a    ! v = -aω R cos³φ sinφ sin4λ
```

注意：`a, b, c` 是局部变量，在计算 u 和 gz 时**含义不同**，均被复用。

**位势高度 gz**（整格点：`full_lon(i)` × `full_lat(j)`）：

```fortran
! 循环范围：j ∈ full_jds:full_jde（纬度方向先算 a,b,c 与 i 无关）
cos_lat = mesh%full_cos_lat(j)

! A(φ)：两项之和
a = 0.5_r8 * omg * (2 * omega + omg) * cos_lat**2 + &
    0.25_r8 * omg**2 * (                              &
      (R + 1) * cos_lat**(2 * R + 2)   +              &  ! (R+1) cos^(2R+2)φ
      (2 * R**2 - R - 2) * cos_lat**(2 * R)   -       &  ! (2R²-R-2) cos^(2R)φ
      2 * R**2 * cos_lat**(2 * R - 2)          )         ! -2R² cos^(2R-2)φ

! B(φ)
b = 2 * (omega + omg) * omg * cos_lat**R * &
    (R**2 + 2 * R + 2 - (R + 1)**2 * cos_lat**2) / (R + 1) / (R + 2)

! C(φ)
c = 0.25_r8 * omg**2 * cos_lat**(2 * R) * ((R + 1) * cos_lat**2 - R - 2)

! 内层循环赋值（a,b,c 只与 j 有关，cos(Rλ) 与 i 有关）
do i = mesh%full_ids, mesh%full_ide
  lon = mesh%full_lon(i)
  gz%d(i,j,1) = gz0 + radius**2 * (a + b * cos(R * lon) + c * cos(2 * R * lon))
end do
```

**初始化结束后的标志位**：

```fortran
init_hydrostatic_gz = .true.
```

这个全局标志告知模型：gz 场已经从初值直接给定（而非由温度场诊断），
模型跳过静力平衡诊断步骤，直接用赋值的 gz 场开始积分。

---

## 六、期望结果与诊断

### 6.1 波形演化

| 时间 | 期望表现 |
|------|---------|
| Day 0 | 波数 4 的高低压中心交替排列，位势高度极差约 600 m |
| Day 7 | 波形整体向东传播，保持结构完整 |
| Day 14 | 波形仍可辨识，但高分辨率下可能出现细微的非线性变形 |

**文献参考图：第 14 天位势高度场**（Drake, Swarztrauber & Williamson, 1997, Fig. 21）

![TC6 第 14 天位势高度参考解](/assets/ref_figures/ref_tc6_day14_drake97.png)

上图为 Cartesian 方法计算的 Rossby-Haurwitz 波在第 14 天的位势（φ = gH，单位 m²/s²）。
波数 4 结构仍然保持，但已出现明显的非对称变形——这是非线性不稳定性的表现。
GMCORE 的模拟结果应与此图在定性上一致。

**文献参考图：总质量、能量、拟能守恒**（Drake et al. 1997, Fig. 20）

![TC6 守恒量演化](/assets/ref_figures/ref_tc6_conservation_drake97.png)

上图展示了 TC6 积分过程中归一化的总质量（mass）、总能量（energy）、
总拟能（enstrophy）和总涡度（vorticity）的相对变化。
良好的数值方案应保证这些量在长时间积分中保持在 10⁻⁵ 量级以下。

### 6.2 守恒性诊断

| 物理量 | 理论值 | 判据 |
|--------|--------|------|
| 总质量 | 恒定 | 相对偏差 < 10⁻¹⁰ |
| 总能量 | 恒定 | 相对偏差 < 10⁻⁴（14 天） |
| 总位涡拟能 | 恒定 | 相对偏差 < 10⁻³（14 天） |

### 6.3 推荐查看变量

- **gz**（位势高度）：主要展示变量，绘制全球等值线图
- **vor**（相对涡度）：波结构的另一种表达，对称性更清晰
- **pv**（位涡）：涡度 + 科里奥利的综合效应
- **u, v**（风场）：可叠加矢量箭头

---

## 七、数值方法总结：从方程到程序的完整链路

```
                        ┌──────────────────────┐
     方程组              │  space_operators()   │  gmcore_mod.F90:535
                        └──────────┬───────────┘
                                   │
            ┌──────────────────────┼──────────────────────┐
            │                      │                      │
    ┌───────▼───────┐    ┌────────▼────────┐    ┌───────▼───────┐
    │ calc_coriolis │    │  calc_grad_ke   │    │  pgf_swm_run  │
    │ q × (h·v)     │    │  −∇K            │    │  −∇(gH)       │
    │ operators_mod │    │  operators_mod  │    │  pgf_swm_mod  │
    └───────┬───────┘    └────────┬────────┘    └───────┬───────┘
            │                      │                      │
            └──────────────────────┼──────────────────────┘
                                   │
                           ┌───────▼───────┐
                           │ dudt, dvdt    │  → 动量方程右端
                           └───────┬───────┘
                                   │
                        ┌──────────▼──────────┐
                        │  update_state()     │  time_schemes_mod.F90
                        │  u_new = u_old      │
                        │       + Δt × dudt   │
                        └──────────┬──────────┘
                                   │
                        ┌──────────▼──────────┐
                        │  dgzdt = -dmf × g   │  → 连续方程
                        │  gz_new = gz_old     │
                        │       + Δt × dgzdt  │
                        └─────────────────────┘
```

---

## 八、参考文献

1. Williamson, D. L., Drake, J. B., Hack, J. J., Jakob, R., & Swarztrauber, P. N. (1992). A standard test set for numerical approximations to the shallow water equations in spherical geometry. *J. Comput. Phys.*, 102(1), 211–224. [DOI:10.1016/S0021-9991(05)80016-6](https://doi.org/10.1016/S0021-9991(05)80016-6)

2. Haurwitz, B. (1940). The motion of atmospheric disturbances on the spherical earth. *J. Mar. Res.*, 3, 254–267.

3. Thuburn, J., & Li, Y. (2000). Numerical simulations of Rossby–Haurwitz waves. *Tellus A*, 52, 181–189. [DOI:10.3402/tellusa.v52i2.12258](https://doi.org/10.3402/tellusa.v52i2.12258)

4. 李东 等. GMCORE：格点模式大气动力框架. 中国科学院大气物理研究所.
""",

    "tc.720x360": r"""
## 赤道气旋理想模拟（720×360）

**配置：** 720×360，30 层 hybrid（cam_l30），物理参数化：simple_physics v6，
积分 10 天，Δt_dyn = 150 s，Δt_phys = 600 s，散度阻尼开启

这是 Reed & Jablonowski（2011）赤道气旋理想化基准的**标准分辨率**版本：
在可控的轴对称初始扰动下，我想看模式能否模拟赤道气旋**快速增强（RI）**过程。

在 0.5° 分辨率下，TC 的眼墙对流和径向入流结构可以被较好分辨。
快速增强（Rapid Intensification）是指 TC 中心最大风速在 24 小时内
增加 ≥ 30 kt（约 15 m/s），是业务预报中最具挑战性的现象之一。
在此理想化测试中，通过对比不同模式和分辨率下的 TC 增强曲线
来评估动力核的模拟能力。

**初值怎么给的：**
- 背景：Jordan（1958）平均热带探空廓线，静止大气
- 扰动：10°N 处轴对称旋转风场（最大风速 ≈ 8 m/s）
- 边界条件：固定海温 SST = 29°C（302 K）

| 指标 | 参考值（720×360）|
|---|---|
| 近地面最大风速 | 60–80 m/s |
| 中心最低气压 | ~920–950 hPa |
| 暖核偏差（对流层中层） | +8–12 K |

### 参考文献
- [Reed & Jablonowski (2011) *Mon. Wea. Rev.* 139, 689–710](https://doi.org/10.1175/2010MWR3488.1)
- [Ullrich et al. (2017) *Geosci. Model Dev.* 10, 4477–4509](https://doi.org/10.5194/gmd-10-4477-2017)
""",

}
