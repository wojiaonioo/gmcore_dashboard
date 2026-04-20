"""Chinese display names and map backgrounds for GMCORE test cases.

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
# ---------------------------------------------------------------------------
CASE_MAP_BACKGROUND: dict[str, str] = {
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
    if not case_name:
        return "none"
    return CASE_MAP_BACKGROUND.get(case_name, "none")


# ---------------------------------------------------------------------------
# Default analyses — empty; users write their own in the Analysis panel.
# ---------------------------------------------------------------------------
CASE_DEFAULT_ANALYSES: dict[str, str] = {}
