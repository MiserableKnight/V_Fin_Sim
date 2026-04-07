"""
越捷航空油价冲击财务决策模型 - Apple风格界面
VietJet Air Oil Shock Financial Decision Model - Apple-inspired Design

运行方式 / Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from vietjet_oil_model import VietJetOilShockModel, ModelConfig

# ============================================
# 页面配置 / Page config
# ============================================
st.set_page_config(
    page_title="VietJet Oil Shock Model",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================
# Apple Design System CSS / 苹果设计系统样式
# ============================================
APPLE_CSS = """
<style>
    /* ============================================
       APPLE DESIGN SYSTEM - 核心样式
       ============================================ */

    /* 全局字体 - SF Pro */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    :root {
        --apple-bg: #FFFFFF;
        --apple-bg-secondary: #F5F5F7;
        --apple-text: #1D1D1F;
        --apple-text-secondary: #86868B;
        --apple-accent: #0071E3;
        --apple-accent-hover: #0077ED;
        --apple-border: rgba(0, 0, 0, 0.08);
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.04);
        --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.08);
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;
    }

    /* 基础重置 */
    .main {
        background: var(--apple-bg) !important;
    }

    /* 字体系统 */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Inter", "Helvetica Neue", sans-serif !important;
        -webkit-font-smoothing: antialiased !important;
        -moz-osx-font-smoothing: grayscale !important;
    }

    /* 隐藏默认菜单 */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: visible; }

    /* 侧边栏样式 */
    .css-1d391kg {
        background: var(--apple-bg-secondary) !important;
        border-right: 1px solid var(--apple-border) !important;
    }

    /* ============================================
       HERO HEADER / 英雄标题区
       ============================================ */
    .apple-hero {
        text-align: center;
        padding: 80px 20px 60px;
        background: linear-gradient(180deg, #FFFFFF 0%, #F5F5F7 100%);
    }

    .apple-hero-title {
        font-size: clamp(48px, 8vw, 72px);
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--apple-text);
        margin-bottom: 16px;
        line-height: 1.1;
    }

    .apple-hero-subtitle {
        font-size: clamp(20px, 3vw, 24px);
        font-weight: 400;
        letter-spacing: -0.01em;
        color: var(--apple-text-secondary);
        max-width: 680px;
        margin: 0 auto 32px;
        line-height: 1.4;
    }

    .apple-hero-badge {
        display: inline-block;
        padding: 8px 16px;
        background: rgba(0, 113, 227, 0.1);
        color: var(--apple-accent);
        font-size: 14px;
        font-weight: 600;
        border-radius: 20px;
        margin-bottom: 24px;
        letter-spacing: 0.02em;
    }

    /* ============================================
       METRIC CARDS / 指标卡片
       ============================================ */
    .apple-metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 40px 0;
    }

    .apple-metric-card {
        background: var(--apple-bg);
        border: 1px solid var(--apple-border);
        border-radius: var(--radius-lg);
        padding: 28px 24px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: var(--shadow-sm);
    }

    .apple-metric-card:hover {
        transform: translateY(-4px);
        box-shadow: var(--shadow-lg);
        border-color: var(--apple-accent);
    }

    .apple-metric-label {
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--apple-text-secondary);
        margin-bottom: 12px;
    }

    .apple-metric-value {
        font-size: 36px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--apple-text);
        line-height: 1;
        margin-bottom: 8px;
    }

    .apple-metric-change {
        font-size: 14px;
        font-weight: 500;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }

    .apple-metric-change.positive {
        color: #34C759;
    }

    .apple-metric-change.negative {
        color: #FF3B30;
    }

    /* ============================================
       THRESHOLD CARDS / 阈值卡片
       ============================================ */
    .apple-threshold-container {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 24px;
        margin: 48px 0;
    }

    .apple-threshold-card {
        background: var(--apple-bg-secondary);
        border-radius: var(--radius-xl);
        padding: 32px 24px;
        text-align: center;
        transition: all 0.3s ease;
    }

    .apple-threshold-card:hover {
        background: var(--apple-bg);
        box-shadow: var(--shadow-md);
    }

    .apple-threshold-card .icon {
        font-size: 32px;
        margin-bottom: 16px;
    }

    .apple-threshold-value {
        font-size: 48px;
        font-weight: 700;
        letter-spacing: -0.03em;
        color: var(--apple-accent);
        line-height: 1;
        margin-bottom: 8px;
    }

    .apple-threshold-label {
        font-size: 14px;
        font-weight: 500;
        color: var(--apple-text-secondary);
        letter-spacing: 0.02em;
    }

    /* ============================================
       DECISION PATH / 决策路径
       ============================================ */
    .apple-decision-path {
        margin: 48px 0;
    }

    .apple-decision-step {
        display: flex;
        align-items: flex-start;
        gap: 20px;
        padding: 24px;
        background: var(--apple-bg);
        border: 1px solid var(--apple-border);
        border-radius: var(--radius-lg);
        margin-bottom: 16px;
        transition: all 0.3s ease;
    }

    .apple-decision-step:hover {
        box-shadow: var(--shadow-md);
        transform: translateX(8px);
    }

    .apple-step-indicator {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
        font-weight: 600;
    }

    .apple-step-indicator.low {
        background: rgba(52, 199, 89, 0.15);
        color: #34C759;
    }

    .apple-step-indicator.medium {
        background: rgba(255, 149, 0, 0.15);
        color: #FF9500;
    }

    .apple-step-indicator.high {
        background: rgba(255, 159, 10, 0.15);
        color: #FF9F0A;
    }

    .apple-step-indicator.critical {
        background: rgba(255, 59, 48, 0.15);
        color: #FF3B30;
    }

    .apple-step-content h4 {
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 8px 0;
        color: var(--apple-text);
        letter-spacing: -0.01em;
    }

    .apple-step-content p {
        font-size: 15px;
        color: var(--apple-text-secondary);
        margin: 4px 0 0 0;
        line-height: 1.5;
    }

    /* ============================================
       STATUS BADGE / 状态徽章
       ============================================ */
    .apple-status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 10px 20px;
        border-radius: 24px;
        font-size: 15px;
        font-weight: 500;
        letter-spacing: 0.01em;
    }

    .apple-status-healthy {
        background: rgba(52, 199, 89, 0.12);
        color: #34C759;
    }

    .apple-status-warning {
        background: rgba(255, 149, 0, 0.12);
        color: #FF9500;
    }

    .apple-status-critical {
        background: rgba(255, 59, 48, 0.12);
        color: #FF3B30;
    }

    /* ============================================
       INFO BOX / 信息框
       ============================================ */
    .apple-info-box {
        padding: 20px 24px;
        background: var(--apple-bg-secondary);
        border-left: 3px solid var(--apple-accent);
        border-radius: 0 var(--radius-md) var(--radius-md) 0;
        font-size: 15px;
        line-height: 1.6;
        color: var(--apple-text);
    }

    .apple-info-box strong {
        font-weight: 600;
        color: var(--apple-text);
    }

    /* ============================================
       SECTION STYLES / 区域样式
       ============================================ */
    .apple-section {
        padding: 60px 0;
        border-bottom: 1px solid var(--apple-border);
    }

    .apple-section-title {
        font-size: 32px;
        font-weight: 700;
        letter-spacing: -0.02em;
        color: var(--apple-text);
        margin-bottom: 12px;
    }

    .apple-section-description {
        font-size: 17px;
        color: var(--apple-text-secondary);
        line-height: 1.5;
        margin-bottom: 32px;
        max-width: 720px;
    }

    /* ============================================
       BUTTON STYLES / 按钮样式
       ============================================ */
    .stButton > button {
        background: var(--apple-accent) !important;
        color: white !important;
        border: none !important;
        border-radius: 24px !important;
        padding: 12px 28px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }

    .stButton > button:hover {
        background: var(--apple-accent-hover) !important;
        transform: scale(1.02) !important;
        box-shadow: 0 4px 16px rgba(0, 113, 227, 0.3) !important;
    }

    /* ============================================
       TAB STYLES / 标签页样式
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 12px 24px;
        font-size: 15px;
        font-weight: 500;
        color: var(--apple-text-secondary);
        border: 1px solid transparent;
        transition: all 0.2s ease;
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: var(--apple-bg-secondary);
        color: var(--apple-text);
        font-weight: 600;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--apple-bg-secondary);
    }

    /* ============================================
       SLIDER STYLES / 滑块样式
       ============================================ */
    .stSlider [data-testid="stSlider"] {
        background: transparent;
    }

    /* ============================================
       EXPANDER STYLES / 折叠面板样式
       ============================================ */
    .streamlit-expanderHeader {
        background: var(--apple-bg-secondary) !important;
        border: 1px solid var(--apple-border) !important;
        border-radius: var(--radius-md) !important;
        padding: 16px 20px !important;
        font-weight: 500 !important;
    }

    .streamlit-expanderContent {
        background: var(--apple-bg) !important;
        border: 1px solid var(--apple-border) !important;
        border-top: none !important;
        border-radius: 0 0 var(--radius-md) var(--radius-md) !important;
        padding: 20px !important;
    }

    /* ============================================
       DATAFRAME STYLES / 数据表格样式
       ============================================ */
    .stDataFrame {
        border: 1px solid var(--apple-border);
        border-radius: var(--radius-lg);
        overflow: hidden;
    }

    /* ============================================
       RESPONSIVE / 响应式设计
       ============================================ */
    @media (max-width: 768px) {
        .apple-threshold-container {
            grid-template-columns: 1fr;
        }

        .apple-hero-title {
            font-size: 40px;
        }

        .apple-metric-container {
            grid-template-columns: 1fr;
        }
    }
</style>
"""

st.markdown(APPLE_CSS, unsafe_allow_html=True)

# ============================================
# HERO SECTION / 英雄区域
# ============================================
st.markdown("""
<div class="apple-hero">
    <div class="apple-hero-badge">Financial Decision Model</div>
    <h1 class="apple-hero-title">VietJet Oil Shock</h1>
    <p class="apple-hero-subtitle">
        基于财报校准的智能决策系统，助力油价冲击下的运营优化
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# SIDEBAR / 侧边栏配置
# ============================================
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

# ============================================
# MODEL INITIALIZATION / 模型初始化
# ============================================
config = ModelConfig(
    R_base=R_base,
    V_fuel_base=V_fuel_base,
    V_other_base=V_other_base,
    FC=FC,
    demand_elasticity=demand_elasticity,
    network_preserve=network_preserve
)
model = VietJetOilShockModel(config)

# ============================================
# TABS / 标签页
# ============================================
tab1, tab2, tab3, tab4 = st.tabs([
    " 📊  智能决策",
    " 📈  情景扫描",
    " 🎨  可视化",
    " ⚙️  模型说明"
])

# ==================== TAB 1: 智能决策 ====================
with tab1:
    st.markdown('<h2 class="apple-section-title">智能决策分析</h2>', unsafe_allow_html=True)
    st.markdown('<p class="apple-section-description">输入油价涨幅，系统自动计算最优响应策略</p>', unsafe_allow_html=True)

    col_mode, col_display = st.columns([3, 1])
    with col_mode:
        auto_mode = st.checkbox("🤖 启用智能决策模式", value=True)
    with col_display:
        show_details = st.checkbox("显示详情", value=False)

    # 油价输入
    col_input = st.columns(1)[0]
    with col_input:
        oil_increase_input = st.slider(
            "油价涨幅 (%)",
            min_value=0,
            max_value=100,
            value=40,
            step=5
        ) / 100

    if auto_mode:
        with st.expander("⚙️ 决策约束设置"):
            col_con1, col_con2 = st.columns(2)
            with col_con1:
                fare_cap = st.slider("票价上调上限 (%)", 0, 30, 20, 5) / 100
            with col_con2:
                hedge_cap = st.slider("套保额度上限 (%)", 0, 100, 80, 10) / 100

        try:
            threshold_result = model.get_thresholds(
                oil_increase=oil_increase_input,
                fare_cap=fare_cap,
                hedge_cap=hedge_cap,
                verbose=show_details
            )

            # 当前状态
            urgency_info = model.threshold_config.get_urgency_info(threshold_result.current_stage)
            stage_name = model.threshold_config.get_stage_name(threshold_result.current_stage)

            status_class = f"apple-status-{urgency_info['level']}" if urgency_info['level'] in ['healthy', 'warning', 'critical'] else 'apple-status-warning'

            st.markdown(f"""
            <div class="apple-info-box" style="text-align: center; margin: 32px 0;">
                <span class="apple-status-badge {status_class}">
                    {urgency_info['icon']} 当前状态: 阶段 {threshold_result.current_stage} — {stage_name}
                </span>
            </div>
            """, unsafe_allow_html=True)

            # 三阈值卡片
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

            # 决策路径
            st.markdown('<h3 style="font-size: 24px; font-weight: 600; margin: 48px 0 24px;">📈 决策响应路径</h3>', unsafe_allow_html=True)

            for step in threshold_result.decision_path:
                urgency_level = step.get("urgency_level", "低")
                urgency_map = {
                    "低": "low",
                    "中": "medium",
                    "高": "high",
                    "紧急": "critical"
                }
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

            # 推荐动作
            if threshold_result.decision_path:
                recommended = threshold_result.decision_path[0]
                preview_result = model.evaluate(
                    oil_increase_input,
                    recommended['recommended_fare'],
                    recommended['recommended_hedge']
                )

                st.markdown('<h3 style="font-size: 24px; font-weight: 600; margin: 48px 0 24px;">🎬 推荐动作预览</h3>', unsafe_allow_html=True)

                st.markdown(f"""
                <div class="apple-metric-container">
                    <div class="apple-metric-card">
                        <div class="apple-metric-label">推荐票价调整</div>
                        <div class="apple-metric-value">+{recommended['recommended_fare']*100:.1f}%</div>
                    </div>
                    <div class="apple-metric-card">
                        <div class="apple-metric-label">推荐套保比例</div>
                        <div class="apple-metric-value">{recommended['recommended_hedge']*100:.1f}%</div>
                    </div>
                    <div class="apple-metric-card">
                        <div class="apple-metric-label">预期边际贡献</div>
                        <div class="apple-metric-value">{preview_result.total_cm:,.1f}</div>
                        <div class="apple-metric-label">万亿₫</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # 预警信息
            if threshold_result.warnings:
                st.markdown('<h3 style="font-size: 20px; font-weight: 600; margin: 32px 0 16px;">⚠️ 预警信息</h3>', unsafe_allow_html=True)
                for warning in threshold_result.warnings:
                    st.warning(warning)

            if show_details:
                with st.expander("🔍 详细计算过程"):
                    st.json({
                        "输入参数": {
                            "油价涨幅": f"{oil_increase_input*100:.1f}%",
                            "票价上限": f"{fare_cap*100:.1f}%",
                            "套保上限": f"{hedge_cap*100:.1f}%"
                        },
                        "计算结果": {
                            "票价盈亏平衡": f"{threshold_result.fare_breakeven*100:.2f}%",
                            "油价容忍度": f"{threshold_result.oil_tolerance*100:.2f}%",
                            "套保触发线": f"{threshold_result.hedge_trigger*100:.2f}%"
                        },
                        "决策路径": threshold_result.decision_path
                    })

        except ValueError as e:
            st.error(f"❌ 参数错误: {str(e)}")
        except Exception as e:
            st.error(f"❌ 计算失败: {str(e)}")

    else:
        st.info("👆 关闭智能推荐以使用手动模式")

        col1, col2, col3 = st.columns(3)
        with col1:
            oil_increase = st.slider("油价涨幅 (%)", 0, 150, 40) / 100
        with col2:
            fare_adj = st.slider("票价调整 (%)", -20, 50, 8) / 100
        with col3:
            hedge_ratio = st.slider("套保比例 (%)", 0, 100, 30) / 100

        result = model.evaluate(
            oil_increase=oil_increase,
            fare_adj=fare_adj,
            hedge_ratio=hedge_ratio
        )

        # 结果展示
        status_badge_class = f"apple-status-{result.status_type}" if result.status_type in ['healthy', 'warning', 'critical'] else 'apple-status-warning'

        st.markdown(f"""
        <div style="text-align: center; margin: 40px 0;">
            <span class="apple-status-badge {status_badge_class}" style="font-size: 18px; padding: 14px 28px;">
                {result.status}
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="apple-metric-container">
            <div class="apple-metric-card">
                <div class="apple-metric-label">有效燃油成本</div>
                <div class="apple-metric-value">{result.eff_fuel:.2f}</div>
                <div class="apple-metric-change {"positive" if result.eff_fuel < V_fuel_base else "negative"}">
                    {"/" if result.eff_fuel == V_fuel_base else ("▼" if result.eff_fuel < V_fuel_base else "▲")}
                    {(result.eff_fuel/V_fuel_base - 1)*100:+.1f}%
                </div>
            </div>
            <div class="apple-metric-card">
                <div class="apple-metric-label">调整后收入</div>
                <div class="apple-metric-value">{result.adj_revenue:.2f}</div>
                <div class="apple-metric-change {"positive" if result.adj_revenue > R_base else "negative"}">
                    {"/" if result.adj_revenue == R_base else ("▲" if result.adj_revenue > R_base else "▼")}
                    {(result.adj_revenue/R_base - 1)*100:+.1f}%
                </div>
            </div>
            <div class="apple-metric-card">
                <div class="apple-metric-label">总边际贡献</div>
                <div class="apple-metric-value">{result.total_cm:.2f}</div>
                <div class="apple-metric-label">万亿₫</div>
            </div>
            <div class="apple-metric-card">
                <div class="apple-metric-label">预期运营利润</div>
                <div class="apple-metric-value" style="color: {"#34C759" if result.expected_pnl >= 0 else "#FF3B30"};">
                    {result.expected_pnl:+.2f}
                </div>
                <div class="apple-metric-label">万亿₫</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="apple-info-box" style="margin-top: 32px;">
            <strong>✂️ 航班调整建议</strong><br>
            建议航班削减比例: <strong>{result.cut_ratio*100:.1f}%</strong><br>
            预计保留航班数量: <strong>{121 * (1 - result.cut_ratio):.0f}</strong> 架次
        </div>
        """, unsafe_allow_html=True)

# ==================== TAB 2: 情景扫描 ====================
with tab2:
    st.markdown('<h2 class="apple-section-title">多情景批量扫描</h2>', unsafe_allow_html=True)
    st.markdown('<p class="apple-section-description">批量计算不同油价与策略组合，快速找到最优方案</p>', unsafe_allow_html=True)

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

    if st.button("🚀 开始扫描", type="primary"):
        with st.spinner("正在计算..."):
            oil_range = np.arange(oil_min, oil_max + oil_step, oil_step)
            fare_range = [f/100 for f in fare_options]
            hedge_range = [h/100 for h in hedge_options]

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

# ==================== TAB 3: 可视化 ====================
with tab3:
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

    # Apple风格图表配置
    apple_layout = {
        'font': {'family': '-apple-system, SF Pro Display, sans-serif'},
        'paper_bgcolor': 'rgba(0,0,0,0)',
        'plot_bgcolor': 'rgba(0,0,0,0)',
        'margin': dict(l=20, r=20, t=40, b=20),
        'xaxis': {'gridcolor': 'rgba(0,0,0,0.05)'},
        'yaxis': {'gridcolor': 'rgba(0,0,0,0.05)'}
    }

    if viz_type == "利润热力图":
        pivot_df = df[df["套保比例"] == 0.3].pivot(
            index="油价涨幅",
            columns="票价调整",
            values="预期利润"
        )

        fig = px.imshow(
            pivot_df,
            labels=dict(x="票价调整", y="油价涨幅", color="预期利润(万亿₫)"),
            x=[f"{f*100:.0f}%" for f in pivot_df.columns],
            y=[f"{o*100:.0f}%" for o in pivot_df.index],
            color_continuous_scale=["#FF3B30", "#FF9500", "#FFCC00", "#34C759"],
            aspect="auto"
        )
        fig.update_layout(height=500, **apple_layout)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "航班削减热力图":
        pivot_df = df[df["套保比例"] == 0.3].pivot(
            index="油价涨幅",
            columns="票价调整",
            values="航班削减比例"
        )

        fig = px.imshow(
            pivot_df * 100,
            labels=dict(x="票价调整", y="油价涨幅", color="削减比例(%)"),
            x=[f"{f*100:.0f}%" for f in pivot_df.columns],
            y=[f"{o*100:.0f}%" for o in pivot_df.index],
            color_continuous_scale=["#34C759", "#FFCC00", "#FF9500", "#FF3B30"],
            aspect="auto"
        )
        fig.update_layout(height=500, **apple_layout)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "状态分布图":
        status_count = df["状态类型"].value_counts().reset_index()
        status_count.columns = ["状态类型", "数量"]

        status_map = {"healthy": "✅ 健康", "warning": "⚠️ 承压", "critical": "🚨 危险"}
        status_count["状态名称"] = status_count["状态类型"].map(status_map)

        color_map = {"healthy": "#34C759", "warning": "#FF9500", "critical": "#FF3B30"}

        fig = px.bar(
            status_count,
            x="状态名称",
            y="数量",
            color="状态类型",
            color_discrete_map=color_map
        )
        fig.update_layout(showlegend=False, xaxis_title="", height=400, **apple_layout)
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "边际贡献趋势图":
        fig = go.Figure()

        colors = ["#0071E3", "#34C759", "#FF9500", "#FF3B30"]
        color_idx = 0

        for fare in fare_range:
            for hedge in hedge_range:
                df_filtered = df[
                    (df["票价调整"] == fare) &
                    (df["套保比例"] == hedge)
                ]

                label = f"票价+{fare*100:.0f}%, 套保{hedge*100:.0f}%"
                fig.add_trace(go.Scatter(
                    x=df_filtered["油价涨幅"] * 100,
                    y=df_filtered["总边际贡献"],
                    mode="lines+markers",
                    name=label,
                    line=dict(width=2.5, color=colors[color_idx % len(colors)]),
                    marker=dict(size=6)
                ))
                color_idx += 1

        fig.add_hline(
            y=FC,
            line_dash="dash",
            line_color="#FF3B30",
            annotation_text="固定成本线"
        )
        fig.add_hline(
            y=0,
            line_dash="dash",
            line_color="#86868B",
            annotation_text="盈亏平衡线"
        )

        fig.update_layout(
            xaxis_title="油价涨幅 (%)",
            yaxis_title="总边际贡献 (万亿₫)",
            height=500,
            hovermode="x unified",
            legend=dict(orientation="h", y=1.02),
            **apple_layout
        )
        st.plotly_chart(fig, use_container_width=True)

    elif viz_type == "三维决策曲面":
        df_filtered = df[df["套保比例"] == 0.3]

        fig = go.Figure(data=[go.Surface(
            x=df_filtered["票价调整"].unique() * 100,
            y=df_filtered["油价涨幅"].unique() * 100,
            z=df_filtered["预期利润"].values.reshape(
                len(df_filtered["票价调整"].unique()),
                len(df_filtered["油价涨幅"].unique())
            ).T,
            colorscale=[
                [0, "#FF3B30"],
                [0.25, "#FF9500"],
                [0.5, "#FFCC00"],
                [0.75, "#34C759"],
                [1, "#30D158"]
            ],
            colorbar=dict(title="预期利润(万亿₫)")
        )])

        fig.update_layout(
            scene=dict(
                xaxis_title="票价调整 (%)",
                yaxis_title="油价涨幅 (%)",
                zaxis_title="预期利润(万亿₫)",
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2))
            ),
            height=600,
            **apple_layout
        )
        st.plotly_chart(fig, use_container_width=True)

# ==================== TAB 4: 模型说明 ====================
with tab4:
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
    <strong>需求因子</strong> = 1 + 票价调整 × 需求弹性（弹性=-0.8）<br>
    <strong>调整后收入</strong> = 基础收入 × (1 + 票价调整) × 需求因子<br>
    <strong>总边际贡献</strong> = 调整后收入 - 其他变动成本 - 有效燃油成本<br>
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

# ============================================
# FOOTER / 页脚
# ============================================
st.markdown("""
---
<div style="text-align: center; padding: 40px 20px; color: var(--apple-text-secondary); font-size: 14px;">
    <p>VietJet Air Oil Shock Financial Decision Model v1.0</p>
    <p style="margin-top: 8px;">基于2025经审计财报数据 · Apple Design Style</p>
</div>
""", unsafe_allow_html=True)
