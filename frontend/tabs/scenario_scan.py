# -*- coding: utf-8 -*-
"""
情景扫描标签页
Scenario Scan Tab

多情景批量扫描与分析
"""

import streamlit as st
import pandas as pd
import numpy as np

from ..components.forms import render_scan_parameters


def render_scenario_scan_tab(model):
    """
    渲染情景扫描标签页

    Args:
        model: VietJetOilShockModel 实例
    """
    st.markdown('<h2 class="apple-section-title">多情景批量扫描</h2>', unsafe_allow_html=True)
    st.markdown('<p class="apple-section-description">批量计算不同油价与策略组合，快速找到最优方案</p>', unsafe_allow_html=True)

    params = render_scan_parameters()

    if st.button("🚀 开始扫描", type="primary"):
        with st.spinner("正在计算..."):
            oil_range = np.arange(
                params["oil_min"],
                params["oil_max"] + params["oil_step"],
                params["oil_step"]
            )
            fare_range = [f/100 for f in params["fare_options"]]
            hedge_range = [h/100 for h in params["hedge_options"]]

            df = model.scenario_sweep(oil_range, fare_range, hedge_range)

            st.success(f"✅ 扫描完成！共计算 {len(df)} 种情景")

            # 数据表格
            st.markdown('<h3 style="font-size: 20px; font-weight: 600; margin: 32px 0 16px;">📋 情景分析结果</h3>', unsafe_allow_html=True)
            st.dataframe(df.round(2), use_container_width=True, height=300)

            # 下载按钮
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载CSV文件",
                data=csv,
                file_name="vietjet_oil_shock_scenarios.csv",
                mime="text/csv"
            )

            # 统计摘要
            st.markdown('<h3 style="font-size: 20px; font-weight: 600; margin: 32px 0 16px;">📈 统计摘要</h3>', unsafe_allow_html=True)

            healthy_count = (df["状态类型"] == "healthy").sum()
            warning_count = (df["状态类型"] == "warning").sum()
            critical_count = (df["状态类型"] == "critical").sum()

            st.markdown(f"""
            <div class="apple-metric-container">
                <div class="apple-metric-card">
                    <div class="apple-metric-label">情景总数</div>
                    <div class="apple-metric-value">{len(df)}</div>
                </div>
                <div class="apple-metric-card">
                    <div class="apple-metric-label">✅ 健康</div>
                    <div class="apple-metric-value" style="color: #34C759;">{healthy_count}</div>
                    <div class="apple-metric-label">{healthy_count/len(df)*100:.1f}%</div>
                </div>
                <div class="apple-metric-card">
                    <div class="apple-metric-label">⚠️ 承压</div>
                    <div class="apple-metric-value" style="color: #FF9500;">{warning_count}</div>
                    <div class="apple-metric-label">{warning_count/len(df)*100:.1f}%</div>
                </div>
                <div class="apple-metric-card">
                    <div class="apple-metric-label">🚨 危险</div>
                    <div class="apple-metric-value" style="color: #FF3B30;">{critical_count}</div>
                    <div class="apple-metric-label">{critical_count/len(df)*100:.1f}%</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
