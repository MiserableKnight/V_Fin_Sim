# -*- coding: utf-8 -*-
"""
标签页模块
Tabs Module

包含各个标签页的渲染函数
"""

from .smart_decision import render_smart_decision_tab
from .scenario_scan import render_scenario_scan_tab
from .visualization import render_visualization_tab
from .model_info import render_model_info_tab

__all__ = [
    "render_smart_decision_tab",
    "render_scenario_scan_tab",
    "render_visualization_tab",
    "render_model_info_tab",
]
