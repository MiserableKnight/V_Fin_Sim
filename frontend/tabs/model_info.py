# -*- coding: utf-8 -*-
"""
模型说明标签页
Model Info Tab

展示模型参数、公式说明、使用提醒等
"""

import streamlit as st


def render_model_info_tab(model):
    """
    渲染模型说明标签页

    Args:
        model: VietJetOilShockModel 实例
    """
    st.markdown('<h2 class="apple-section-title">模型说明</h2>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 📊 当前配置参数")
        config_summary = model.get_config_summary()

        st.markdown("**收入与成本参数**")
        for k, v in config_summary.items():
            if "弹性" not in k and "机队" not in k:
                st.markdown(f"• **{k}**: {v}")

    with col2:
        st.markdown("### 📈 运营参数")
        st.markdown(f"• **机队规模**: {config_summary['机队规模(架)']} 架")
        st.markdown(f"• **需求价格弹性**: {config_summary['需求价格弹性']}")

    st.markdown("---")
    st.markdown("### 🎯 决策状态分类")

    st.markdown("""
    <div class="apple-info-box" style="margin-bottom: 16px;">
        <strong>🚨 危险</strong><br>
        边际贡献 ≤ 0，单班边际贡献为负，飞一班亏一班<br>
        <strong>建议</strong>: 战略性停飞，保留10%骨架
    </div>

    <div class="apple-info-box" style="margin-bottom: 16px; border-left-color: #FF9500;">
        <strong>⚠️ 承压</strong><br>
        0 < 边际贡献 < 固定成本，单班贡献为正但无法覆盖全部固定成本<br>
        <strong>建议</strong>: 保核心网络，压降低效边缘航班
    </div>

    <div class="apple-info-box" style="border-left-color: #34C759;">
        <strong>✅ 健康</strong><br>
        边际贡献 ≥ 固定成本，边际贡献完全覆盖固定成本<br>
        <strong>建议</strong>: 无需砍航班，可优化排班提效
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📐 关键公式")

    st.markdown("""
    <div style="background: var(--apple-bg-secondary); padding: 24px; border-radius: 12px; font-size: 15px; line-height: 1.8;">
    <strong>有效燃油成本</strong> = 基础燃油成本 × (1 + 油价涨幅 × (1 - 套保比例))<br>
    <strong>需求因子（恒定弹性模型）</strong> = (1 + 票价调整)<sup>需求弹性</sup>，弹性=-0.8<br>
    <strong>调整后收入</strong> = 基础收入 × (1 + 票价调整) × 需求因子<br>
    <strong>总边际贡献</strong> = 调整后收入 - 其他变动成本×需求因子 - 有效燃油成本<br>
    <strong>预期运营利润</strong> = 总边际贡献 - 固定成本
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ⚠️ 使用提醒")

    st.markdown("""
    <div style="background: rgba(255, 149, 0, 0.1); padding: 20px; border-radius: 12px; border-left: 3px solid #FF9500;">
        • 本模型为简化分析工具，实际决策需考虑更多因素<br>
        • 砍航班可能扩大账面亏损，但可缓解短期现金流压力<br>
        • 套保具有双刃剑效应，油价下跌时可能产生机会成本<br>
        • 国际航线受双边协定约束，需考虑合规性风险
    </div>
    """, unsafe_allow_html=True)
