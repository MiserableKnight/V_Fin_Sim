# -*- coding: utf-8 -*-
"""
卡片组件
Card Components

包含阈值卡片、指标卡片、状态徽章等组件
"""

import streamlit as st


def render_threshold_cards(threshold_result):
    """
    渲染三个阈值卡片

    Args:
        threshold_result: ThresholdResult 对象
    """
    st.markdown("""
    <div class="apple-threshold-container">
        <div class="apple-threshold-card">
            <div class="icon">💰</div>
            <div class="apple-threshold-value">+{:.1f}%</div>
            <div class="apple-threshold-label">票价盈亏平衡点</div>
        </div>
        <div class="apple-threshold-card">
            <div class="icon">🛢️</div>
            <div class="apple-threshold-value">+{:.1f}%</div>
            <div class="apple-threshold-label">油价容忍上限</div>
        </div>
        <div class="apple-threshold-card">
            <div class="icon">🛡️</div>
            <div class="apple-threshold-value">{:.1f}%</div>
            <div class="apple-threshold-label">削班触发套保线</div>
        </div>
    </div>
    """.format(
        threshold_result.fare_breakeven * 100,
        threshold_result.oil_tolerance * 100,
        threshold_result.hedge_trigger * 100
    ), unsafe_allow_html=True)


def render_metric_card(label, value, unit="", change=None, change_type=None):
    """
    渲染单个指标卡片

    Args:
        label: 标签
        value: 值
        unit: 单位
        change: 变化百分比（可选）
        change_type: "positive" 或 "negative"
    """
    change_html = ""
    if change is not None and change_type:
        arrow = "▲" if change_type == "positive" else "▼"
        change_html = f"""
        <div class="apple-metric-change {change_type}">
            {arrow} {change:+.1f}%
        </div>
        """

    st.markdown(f"""
    <div class="apple-metric-card">
        <div class="apple-metric-label">{label}</div>
        <div class="apple-metric-value">{value}</div>
        {change_html}
        <div class="apple-metric-label">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


def render_metric_cards(metrics):
    """
    渲染多个指标卡片

    Args:
        metrics: 字典列表，每个字典包含 label, value, unit
    """
    cards_html = '<div class="apple-metric-container">'
    for metric in metrics:
        label = metric.get("label", "")
        value = metric.get("value", "")
        unit = metric.get("unit", "")
        change = metric.get("change")
        change_type = metric.get("change_type")

        change_html = ""
        if change is not None and change_type:
            arrow = "▲" if change_type == "positive" else "▼"
            if change != 0:
                change_html = f"""
                <div class="apple-metric-change {change_type}">
                    {arrow} {change:+.1f}%
                </div>
                """

        cards_html += f"""
        <div class="apple-metric-card">
            <div class="apple-metric-label">{label}</div>
            <div class="apple-metric-value">{value}</div>
            {change_html}
            <div class="apple-metric-label">{unit}</div>
        </div>
        """
    cards_html += "</div>"

    st.markdown(cards_html, unsafe_allow_html=True)


def render_status_badge(text, status_type="healthy"):
    """
    渲染状态徽章

    Args:
        text: 徽章文本
        status_type: "healthy", "warning", "critical"
    """
    status_class = f"apple-status-{status_type}" if status_type in ['healthy', 'warning', 'critical'] else 'apple-status-warning'

    st.markdown(f"""
    <div style="text-align: center; margin: 40px 0;">
        <span class="apple-status-badge {status_class}" style="font-size: 18px; padding: 14px 28px;">
            {text}
        </span>
    </div>
    """, unsafe_allow_html=True)


def render_decision_path(decision_path):
    """
    渲染决策路径步骤

    Args:
        decision_path: 决策路径列表
    """
    urgency_map = {
        "低": "low",
        "中": "medium",
        "高": "high",
        "紧急": "critical"
    }

    for step in decision_path:
        urgency_level = step.get("urgency_level", "低")
        indicator_class = urgency_map.get(urgency_level, "low")

        st.markdown(f"""
        <div class="apple-decision-step">
            <div class="apple-step-indicator {indicator_class}">
                {step['stage']}
            </div>
            <div class="apple-step-content">
                <h4>{step['action']}</h4>
                <p><strong>📍 触发条件:</strong> {step['trigger_value']}</p>
                <p><strong>💡 说明:</strong> {step['desc']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
