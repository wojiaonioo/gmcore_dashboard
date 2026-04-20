"""Internationalization support for GMCORE Dashboard.

Default language: Chinese (zh). Switch via set_locale('en') or the UI toggle.
"""

from __future__ import annotations

_STRINGS: dict[str, dict[str, str]] = {
    # === App shell / Navbar ===
    "brand_sub": {"zh": "仪表盘", "en": "Dashboard"},
    "brand_tagline": {"zh": "大气动力学框架", "en": "Scientific dynamical core"},
    "status_online": {"zh": "在线", "en": "Online"},

    # === Tab labels ===
    "tab_visualize": {"zh": "可视化", "en": "Visualize"},
    "tab_experiments": {"zh": "数值试验", "en": "Experiments"},
    "tab_multi_view": {"zh": "多场对比", "en": "Multi-view"},
    "tab_configure": {"zh": "参数配置", "en": "Configure"},
    "tab_build_run": {"zh": "编译与运行", "en": "Build & Run"},
    "tab_monitor": {"zh": "运行监控", "en": "Monitor"},

    # === Visualize tab ===
    "viz_unavailable_title": {"zh": "可视化不可用", "en": "Visualization unavailable"},
    "viz_unavailable_msg": {
        "zh": "未找到 GMCORE 测试集目录，无法发现算例及 NetCDF 输出。",
        "en": "The dashboard could not locate the GMCORE testbed root needed to discover cases and NetCDF outputs.",
    },
    "viz_case_select": {"zh": "选择算例", "en": "Select case"},
    "viz_variable": {"zh": "变量", "en": "Variable"},
    "viz_level": {"zh": "层次", "en": "Level"},
    "viz_time_step": {"zh": "时间步", "en": "Time step"},
    "viz_colormap": {"zh": "色标", "en": "Colormap"},
    "viz_view_mode": {"zh": "视图模式", "en": "View mode"},
    "viz_map_projection": {"zh": "经纬度投影", "en": "Map projection"},
    "viz_lon_cross": {"zh": "经向剖面", "en": "Lon cross-section"},
    "viz_lat_cross": {"zh": "纬向剖面", "en": "Lat cross-section"},
    "viz_color_range": {"zh": "色标范围", "en": "Color range"},
    "viz_auto": {"zh": "自动", "en": "Auto"},
    "viz_global": {"zh": "全局", "en": "Global"},
    "viz_manual": {"zh": "手动", "en": "Manual"},
    "viz_symmetric": {"zh": "对称", "en": "Symmetric"},

    # === Experiments tab ===
    "exp_no_experiments": {"zh": "暂无试验", "en": "No experiments yet"},
    "exp_create_first": {
        "zh": "创建首个试验以开始调整参数。",
        "en": "Create your first experiment to start tuning parameters.",
    },
    "exp_detail": {"zh": "详情", "en": "Detail"},
    "exp_compare": {"zh": "对比分析", "en": "Compare"},
    "exp_sweep": {"zh": "参数扫描", "en": "Sweep"},
    "exp_no_selected": {"zh": "未选择试验", "en": "No experiment selected"},
    "exp_select_hint": {"zh": "从列表中选择一个试验", "en": "Select an experiment from the table"},
    "exp_no_metadata": {"zh": "无可用元数据", "en": "No metadata available."},
    "exp_record_unavailable": {"zh": "记录不可用", "en": "Record unavailable"},
    "exp_status": {"zh": "试验状态", "en": "Experiment status"},
    "exp_no_tags": {"zh": "无标签", "en": "No tags"},
    "exp_missing_image": {"zh": "图片缺失", "en": "Missing image"},
    "exp_missing_diag": {"zh": "诊断缺失", "en": "Missing diagnostic"},
    "exp_template_preview": {"zh": "模板预览", "en": "Template Preview"},
    "exp_persistent": {"zh": "跨会话持久化", "en": "Persistent across sessions"},
    "exp_custom_root": {"zh": "自定义试验目录", "en": "Custom experiment root"},
    "exp_selected_status": {"zh": "已选试验状态", "en": "Selected experiment status"},

    # === Configure tab ===
    "cfg_unavailable_title": {"zh": "参数编辑器不可用", "en": "Configuration editor unavailable"},
    "cfg_unavailable_msg": {
        "zh": "未找到 GMCORE 测试集目录，无法发现算例 namelist 文件。",
        "en": "The dashboard could not locate the GMCORE testbed root needed to discover case namelists.",
    },
    "cfg_case_selector": {"zh": "算例与文件选择", "en": "Case & File Selector"},
    "cfg_namelist_info": {"zh": "当前 Namelist 信息", "en": "Current Namelist Info"},
    "cfg_clone_template": {"zh": "克隆模板", "en": "Clone Template"},
    "cfg_select_hint": {"zh": "选择算例以查看其 namelist", "en": "Select a case to inspect its namelist."},
    "cfg_file": {"zh": "文件", "en": "File"},

    # === Build & Run tab ===
    "br_build_config": {"zh": "编译配置", "en": "Build Configuration"},
    "br_run_config": {"zh": "运行配置", "en": "Run Configuration"},
    "br_quick_actions": {"zh": "快捷操作", "en": "Quick Actions"},
    "br_job_status": {"zh": "作业状态", "en": "Job Status"},
    "br_log_viewer": {"zh": "日志查看器", "en": "Log Viewer"},
    "br_build_type": {"zh": "构建类型", "en": "Build type"},
    "br_cmake_args": {"zh": "附加 CMake 参数", "en": "Extra CMake args"},
    "br_case_name": {"zh": "算例名称", "en": "Case name"},
    "br_nprocs": {"zh": "MPI 进程数", "en": "MPI processes"},
    "br_work_dir": {"zh": "工作目录", "en": "Work directory"},
    "br_configure": {"zh": "配置", "en": "Configure"},
    "br_build": {"zh": "编译", "en": "Build"},
    "br_run": {"zh": "运行", "en": "Run"},
    "br_clean_rebuild": {"zh": "清理重建", "en": "Clean & Rebuild"},
    "br_stop": {"zh": "终止", "en": "Stop"},

    # === Monitor tab ===
    "mon_running_jobs": {"zh": "运行中作业", "en": "Running Jobs"},
    "mon_no_jobs": {"zh": "当前无活跃作业", "en": "No active jobs"},
    "mon_elapsed": {"zh": "已用时间", "en": "Elapsed"},
    "mon_pid": {"zh": "进程号", "en": "PID"},

    # === Multi-view tab ===
    "mv_add_panel": {"zh": "添加面板", "en": "Add panel"},
    "mv_remove_panel": {"zh": "移除面板", "en": "Remove panel"},
    "mv_source": {"zh": "数据来源", "en": "Source"},
    "mv_testbed": {"zh": "测试集", "en": "Testbed"},
    "mv_experiment": {"zh": "数值试验", "en": "Experiment"},

    # === Common ===
    "testbed_not_found_title": {"zh": "测试集目录未找到", "en": "GMCORE testbed directory not found."},
    "testbed_not_found_msg": {"zh": "预期路径：", "en": "Expected path:"},
    "loading": {"zh": "加载中...", "en": "Loading..."},
    "error": {"zh": "错误", "en": "Error"},
    "success": {"zh": "成功", "en": "Success"},
    "cancel": {"zh": "取消", "en": "Cancel"},
    "confirm": {"zh": "确认", "en": "Confirm"},
    "save": {"zh": "保存", "en": "Save"},
    "delete": {"zh": "删除", "en": "Delete"},
    "refresh": {"zh": "刷新", "en": "Refresh"},
    "download": {"zh": "下载", "en": "Download"},
    "parameter": {"zh": "参数", "en": "Parameter"},
    "value": {"zh": "值", "en": "Value"},
    "status": {"zh": "状态", "en": "Status"},
    "name": {"zh": "名称", "en": "Name"},
    "description": {"zh": "描述", "en": "Description"},
    "created_at": {"zh": "创建时间", "en": "Created at"},
    "updated_at": {"zh": "更新时间", "en": "Updated at"},

    # === Status values ===
    "status_created": {"zh": "已创建", "en": "Created"},
    "status_queued": {"zh": "排队中", "en": "Queued"},
    "status_running": {"zh": "运行中", "en": "Running"},
    "status_completed": {"zh": "已完成", "en": "Completed"},
    "status_failed": {"zh": "失败", "en": "Failed"},
    "status_timeout": {"zh": "超时", "en": "Timeout"},
    "status_cancelled": {"zh": "已取消", "en": "Cancelled"},

    # === Language switch ===
    "lang_switch": {"zh": "English", "en": "中文"},
}

_current_locale: str = "zh"


def set_locale(locale: str) -> None:
    global _current_locale
    if locale not in ("zh", "en"):
        raise ValueError(f"Unsupported locale: {locale!r}. Use 'zh' or 'en'.")
    _current_locale = locale


def get_locale() -> str:
    return _current_locale


def t(key: str, locale: str | None = None) -> str:
    """Translate a key to the current (or specified) locale."""
    loc = locale or _current_locale
    entry = _STRINGS.get(key)
    if entry is None:
        return key
    return entry.get(loc, entry.get("en", key))
