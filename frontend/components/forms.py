# -*- coding: utf-8 -*-
"""
表单组件
Form Components

包含侧边栏配置、决策约束设置等表单组件
"""

import streamlit as st


def render_sidebar_config():
    """
    渲染侧边栏配置

    Returns:
        dict: 包含所有配置参数的字典
    """
    with st.sidebar:
        st.markdown("### ⚙️ 参数配置")

        st.markdown("""
        <div class="apple-info-box" style="margin-bottom: 24px;">
            <strong>💡 参数说明</strong><br>
            • 基础财务参数来自2025经审计财报<br>
            • 油价涨幅是外生冲击变量<br>
            • 有效燃油成本 = 基础 × (1 + 油价涨幅 × (1 - 套保比例))
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 📊 基础财务参数 (万亿₫)")
        R_base = st.slider("基础运营收入", 50.0, 80.0, 64.94, 0.01)
        V_fuel_base = st.slider("基础燃油成本", 15.0, 35.0, 24.70, 0.01)
        V_other_base = st.slider("其他变动成本", 15.0, 30.0, 22.70, 0.01)
        FC = st.slider("固定成本", 10.0, 30.0, 19.06, 0.01)

        st.markdown("#### 📈 弹性参数")
        demand_elasticity = st.slider("需求价格弹性", -1.5, -0.3, -0.8, 0.1)
        network_preserve = st.slider("网络保留权重", 0.1, 0.5, 0.25, 0.05)

        return {
            "R_base": R_base,
            "V_fuel_base": V_fuel_base,
            "V_other_base": V_other_base,
            "FC": FC,
            "demand_elasticity": demand_elasticity,
            "network_preserve": network_preserve
        }


def render_decision_constraints():
    """
    渲染决策约束设置

    Returns:
        dict: 包含 fare_cap 和 hedge_cap 的字典
    """
    with st.expander("⚙️ 决策约束设置"):
        col_con1, col_con2 = st.columns(2)
        with col_con1:
            fare_cap = st.slider("票价上调上限 (%)", 0, 30, 20, 5) / 100
        with col_con2:
            hedge_cap = st.slider("套保额度上限 (%)", 0, 100, 80, 10) / 100

    return {"fare_cap": fare_cap, "hedge_cap": hedge_cap}


def render_oil_input(default_value=40, step=5):
    """
    渲染油价涨幅输入

    Args:
        default_value: 默认值（百分比）
        step: 步长（百分比）

    Returns:
        float: 油价涨幅（小数形式）
    """
    col_input = st.columns(1)[0]
    with col_input:
        oil_increase = st.slider(
            "油价涨幅 (%)",
            min_value=0,
            max_value=100,
            value=default_value,
            step=step
        ) / 100
    return oil_increase


def render_manual_inputs(default_oil=40, default_fare=8, default_hedge=30):
    """
    渲染手动模式输入控件

    Args:
        default_oil: 默认油价涨幅（百分比）
        default_fare: 默认票价调整（百分比）
        default_hedge: 默认套保比例（百分比）

    Returns:
        dict: 包含 oil_increase, fare_adj, hedge_ratio 的字典
    """
    col1, col2, col3 = st.columns(3)
    with col1:
        oil_increase = st.slider("油价涨幅 (%)", 0, 150, default_oil) / 100
    with col2:
        fare_adj = st.slider("票价调整 (%)", -20, 50, default_fare) / 100
    with col3:
        hedge_ratio = st.slider("套保比例 (%)", 0, 100, default_hedge) / 100

    return {
        "oil_increase": oil_increase,
        "fare_adj": fare_adj,
        "hedge_ratio": hedge_ratio
    }


def render_scan_parameters():
    """
    渲染情景扫描参数

    Returns:
        dict: 包含扫描参数的字典
    """
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 扫描参数")
        oil_min = st.slider("油价涨幅最小值 (%)", 0, 100, 0) / 100
        oil_max = st.slider("油价涨幅最大值 (%)", 50, 200, 100) / 100
        oil_step = st.slider("油价涨幅步长 (%)", 5, 20, 10) / 100

    with col2:
        st.markdown("#### 策略选项")
        fare_options = st.multiselect(
            "票价调整选项 (%)",
            [0, 5, 10, 15, 20],
            default=[0, 5, 10]
        )
        hedge_options = st.multiselect(
            "套保比例选项 (%)",
            [0, 20, 30, 40, 50],
            default=[0, 30, 50]
        )

    return {
        "oil_min": oil_min,
        "oil_max": oil_max,
        "oil_step": oil_step,
        "fare_options": fare_options,
        "hedge_options": hedge_options
    }
