# -*- coding: utf-8 -*-
"""
可视化标签页
Visualization Tab

多维度图表展示
"""

import streamlit as st
import numpy as np

from ..components.charts import (
    render_profit_heatmap,
    render_cut_ratio_heatmap,
    render_status_distribution,
    render_cm_trend,
    render_3d_surface
)


def render_visualization_tab(model):
    """
    渲染可视化标签页

    Args:
        model: VietJetOilShockModel 实例
    """
    st.markdown('<h2 class="apple-section-title">可视化分析</h2>', unsafe_allow_html=True)
    st.markdown('<p class="apple-section-description">多维度图表展示，深入理解数据规律</p>', unsafe_allow_html=True)

    viz_type = st.selectbox(
        "选择图表类型",
        ["利润热力图", "航班削减热力图", "状态分布图", "边际贡献趋势图", "三维决策曲面"]
    )

    # 生成数据
    oil_range = np.arange(0.0, 1.1, 0.1)
    fare_range = [0.0, 0.05, 0.10]
    hedge_range = [0.0, 0.3, 0.5]
    df = model.scenario_sweep(oil_range, fare_range, hedge_range)

    # 获取固定成本
    config = model.get_config_summary()
    FC = config.get("固定成本(万亿₫)", 19.06)

    if viz_type == "利润热力图":
        render_profit_heatmap(df, hedge_ratio=0.3)

    elif viz_type == "航班削减热力图":
        render_cut_ratio_heatmap(df, hedge_ratio=0.3)

    elif viz_type == "状态分布图":
        render_status_distribution(df)

    elif viz_type == "边际贡献趋势图":
        render_cm_trend(df, FC, fare_range, hedge_range)

    elif viz_type == "三维决策曲面":
        render_3d_surface(df, hedge_ratio=0.3)
