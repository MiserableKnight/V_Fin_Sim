# -*- coding: utf-8 -*-
"""
前端组件模块
Frontend Components Module

包含可复用的UI组件
"""

from .cards import (
    render_threshold_cards,
    render_metric_cards,
    render_status_badge
)
from .charts import (
    get_apple_layout,
    render_profit_heatmap,
    render_cut_ratio_heatmap,
    render_status_distribution,
    render_cm_trend,
    render_3d_surface
)
from .forms import (
    render_sidebar_config,
    render_decision_constraints
)

__all__ = [
    "render_threshold_cards",
    "render_metric_cards",
    "render_status_badge",
    "get_apple_layout",
    "render_profit_heatmap",
    "render_cut_ratio_heatmap",
    "render_status_distribution",
    "render_cm_trend",
    "render_3d_surface",
    "render_sidebar_config",
    "render_decision_constraints",
]
